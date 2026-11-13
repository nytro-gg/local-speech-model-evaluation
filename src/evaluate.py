from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata
import json
import math
import platform
import re
import sys
import threading
import time
import unicodedata
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Iterable, Sequence

SUPPORTED_MODELS = ("tiny", "base", "small", "medium", "large-v3")
SUPPORTED_DEVICES = ("cpu",)
SUPPORTED_COMPUTE_TYPES = ("int8", "float32")
MODEL_REPOSITORIES = {
    "tiny": "Systran/faster-whisper-tiny",
    "base": "Systran/faster-whisper-base",
    "small": "Systran/faster-whisper-small",
    "medium": "Systran/faster-whisper-medium",
    "large-v3": "Systran/faster-whisper-large-v3",
}


@dataclass
class SegmentRecord:
    start: float
    end: float
    text: str
    avg_logprob: float | None = None
    no_speech_prob: float | None = None


def positive_seconds(value: str) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a number of seconds") from exc
    if not math.isfinite(parsed) or parsed <= 0:
        raise argparse.ArgumentTypeError("must be a finite number greater than zero")
    return parsed


def nonnegative_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a whole number") from exc
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be zero or greater")
    return parsed


def positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a whole number") from exc
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Benchmark a local Faster-Whisper model and optionally score it against a reference transcript."
    )
    parser.add_argument("--audio", required=True, type=Path, help="Path to the audio file")
    parser.add_argument("--model", choices=SUPPORTED_MODELS, default="small")
    parser.add_argument("--device", choices=SUPPORTED_DEVICES, default="cpu",
                        help="CPU-only in this verified package; CUDA is intentionally deferred")
    parser.add_argument("--compute-type", choices=SUPPORTED_COMPUTE_TYPES, default="int8")
    parser.add_argument("--language", default=None, help="Optional language code, e.g. en; omit for auto-detection")
    parser.add_argument("--beam-size", type=positive_int, default=5)
    parser.add_argument("--threads", type=nonnegative_int, default=0,
                        help="CPU threads (0 lets CTranslate2 choose its default)")
    parser.add_argument("--vad", action="store_true", help="Enable voice activity detection")
    parser.add_argument("--reference", type=Path, default=None,
                        help="UTF-8 reference transcript used to calculate WER/CER")
    parser.add_argument("--max-audio-seconds", type=positive_seconds, default=120.0,
                        help="Abort if audio duration exceeds this value (default: 120s); fails closed if duration cannot be read")
    parser.add_argument("--output-dir", type=Path, default=Path("results"))
    parser.add_argument("--model-cache-dir", type=Path, default=Path("models/hf-cache"),
                        help="Hugging Face model cache directory")
    parser.add_argument("--model-revision", default="main",
                        help="Hugging Face branch, tag, or commit SHA; resolved commit is recorded in metadata")
    parser.add_argument("--local-files-only", action="store_true",
                        help="Do not access the network; use a model already present in the cache")
    return parser


def get_audio_duration(path: Path) -> float | None:
    """Inspect container metadata without decoding the full audio into memory."""
    try:
        import av
    except ImportError as exc:
        raise RuntimeError("PyAV is unavailable. Reinstall dependencies with scripts/setup.ps1.") from exc

    try:
        with av.open(str(path)) as container:
            audio_streams = [stream for stream in container.streams if stream.type == "audio"]
            if not audio_streams:
                raise ValueError(f"No audio stream found in: {path}")

            stream_durations = []
            for stream in audio_streams:
                if stream.duration is not None and stream.time_base is not None:
                    duration = float(stream.duration * stream.time_base)
                    if math.isfinite(duration) and duration > 0:
                        stream_durations.append(duration)
            if stream_durations:
                return max(stream_durations)

            # AV_TIME_BASE is 1,000,000 ticks per second for container.duration.
            if container.duration is not None:
                duration = float(container.duration) / float(av.time_base)
                if math.isfinite(duration) and duration > 0:
                    return duration
            return None
    except ValueError:
        raise
    except Exception as exc:
        raise RuntimeError(f"Could not inspect audio metadata for {path}: {exc}") from exc


def normalize_text(text: str) -> str:
    """Unicode-normalize, case-fold, remove punctuation, and collapse whitespace."""
    normalized = unicodedata.normalize("NFC", text.casefold())
    cleaned = []
    for char in normalized:
        if unicodedata.category(char).startswith("P"):
            cleaned.append(" ")
        else:
            cleaned.append(char)
    return " ".join("".join(cleaned).split())


def edit_counts(reference: Sequence[str], hypothesis: Sequence[str]) -> dict[str, int]:
    """Return Levenshtein edit counts without allocating an O(N*M) Python matrix.

    RapidFuzz computes the edit script in optimized native code. This matters for
    long-form transcripts: a full Python DP matrix can require gigabytes of RAM.
    """
    try:
        from rapidfuzz.distance import Levenshtein
    except ImportError as exc:
        raise RuntimeError("rapidfuzz is unavailable. Reinstall dependencies with scripts/setup.ps1.") from exc

    operations = Levenshtein.editops(reference, hypothesis)
    substitutions = sum(operation.tag == "replace" for operation in operations)
    insertions = sum(operation.tag == "insert" for operation in operations)
    deletions = sum(operation.tag == "delete" for operation in operations)
    return {
        "substitutions": substitutions,
        "insertions": insertions,
        "deletions": deletions,
        "errors": len(operations),
    }


def calculate_accuracy_metrics(reference: str, hypothesis: str) -> dict[str, Any]:
    """Calculate normalized WER/CER. Empty references are explicitly marked undefined."""
    ref = normalize_text(reference)
    hyp = normalize_text(hypothesis)
    ref_words = ref.split() if ref else []
    hyp_words = hyp.split() if hyp else []
    word_counts = edit_counts(ref_words, hyp_words)
    char_counts = edit_counts(list(ref), list(hyp))

    return {
        "normalization": "Unicode casefold; punctuation removed; whitespace collapsed",
        "reference_word_count": len(ref_words),
        "hypothesis_word_count": len(hyp_words),
        "reference_character_count": len(ref),
        "hypothesis_character_count": len(hyp),
        "wer": (word_counts["errors"] / len(ref_words)) if ref_words else None,
        "cer": (char_counts["errors"] / len(ref)) if ref else None,
        "word_errors": word_counts,
        "character_errors": char_counts,
        "reference_is_empty_after_normalization": not bool(ref),
        "potential_false_positive_word_count_for_silence_test": len(hyp_words) if not ref else None,
        "undefined_reason": "Reference contains no normalized words/characters" if not ref else None,
    }


def safe_float(value: Any) -> float | None:
    try:
        parsed = float(value) if value is not None else None
        return parsed if parsed is not None and math.isfinite(parsed) else None
    except (TypeError, ValueError):
        return None


def package_version(name: str) -> str | None:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def installed_distribution_versions() -> dict[str, str]:
    """Capture the complete installed Python distribution set for run reproducibility."""
    versions: dict[str, str] = {}
    for distribution in importlib.metadata.distributions():
        name = distribution.metadata.get("Name")
        if name:
            versions[name.lower().replace("_", "-")] = distribution.version
    return dict(sorted(versions.items()))


def resolve_model_snapshot(model_name: str, revision: str, cache_dir: Path, local_files_only: bool) -> tuple[Path, str | None]:
    """Download/cache an official Systran CTranslate2 checkpoint and return its resolved commit."""
    try:
        from huggingface_hub import snapshot_download
    except ImportError as exc:
        raise RuntimeError("huggingface_hub is unavailable. Run scripts/setup.ps1 again.") from exc

    repo_id = MODEL_REPOSITORIES[model_name]
    snapshot_path = Path(snapshot_download(
        repo_id=repo_id,
        revision=revision,
        cache_dir=str(cache_dir.expanduser().resolve()),
        local_files_only=local_files_only,
    )).resolve()
    resolved_commit = snapshot_path.name if re.fullmatch(r"[0-9a-f]{40}", snapshot_path.name) else None
    return snapshot_path, resolved_commit


class ResourceMonitor:
    """Sample this process' RSS and CPU while model loading/inference run."""
    def __init__(self, interval_seconds: float = 0.25):
        self.interval_seconds = interval_seconds
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._samples: list[dict[str, float | None]] = []
        self._process = None
        self._started_at: float | None = None
        self._system_memory_total_mb: float | None = None
        self._system_memory_available_start_mb: float | None = None

    def _sample(self, include_cpu: bool = True) -> None:
        try:
            memory = self._process.memory_info().rss / (1024 * 1024)
            cpu = float(self._process.cpu_percent(interval=None)) if include_cpu else None
            self._samples.append({"rss_mb": memory, "cpu_percent": cpu})
        except Exception:
            # Sampling should not crash a transcription run; failures are disclosed in metadata.
            return

    def _worker(self) -> None:
        while not self._stop_event.wait(self.interval_seconds):
            self._sample()

    def start(self) -> None:
        try:
            import psutil
        except ImportError as exc:
            raise RuntimeError("psutil is unavailable. Run scripts/setup.ps1 again.") from exc
        self._process = psutil.Process()
        self._process.cpu_percent(interval=None)  # Prime the non-blocking CPU sampler.
        system_memory = psutil.virtual_memory()
        self._system_memory_total_mb = system_memory.total / (1024 * 1024)
        self._system_memory_available_start_mb = system_memory.available / (1024 * 1024)
        self._started_at = time.perf_counter()
        self._sample(include_cpu=False)  # Initial memory baseline; do not bias CPU average with a zero-length sample.
        self._thread = threading.Thread(target=self._worker, name="resource-monitor", daemon=True)
        self._thread.start()

    def stop(self) -> dict[str, Any]:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=max(1.0, self.interval_seconds * 4))
        if self._process is not None:
            self._sample(include_cpu=False)
        samples = self._samples
        try:
            import psutil
            available_end = psutil.virtual_memory().available / (1024 * 1024)
        except Exception:
            available_end = None
        rss_values = [sample["rss_mb"] for sample in samples]
        cpu_values = [sample["cpu_percent"] for sample in samples if sample["cpu_percent"] is not None]
        return {
            "sampling_interval_seconds": self.interval_seconds,
            "sample_count": len(samples),
            "process_rss_start_mb": rss_values[0] if rss_values else None,
            "process_rss_end_mb": rss_values[-1] if rss_values else None,
            "process_rss_peak_sampled_mb": max(rss_values) if rss_values else None,
            "process_cpu_average_sampled_percent": mean(cpu_values) if cpu_values else None,
            "process_cpu_peak_sampled_percent": max(cpu_values) if cpu_values else None,
            "system_ram_total_mb": self._system_memory_total_mb,
            "system_ram_available_start_mb": self._system_memory_available_start_mb,
            "system_ram_available_end_mb": available_end,
            "measurement_note": "Process RSS/CPU are sampled; brief peaks between samples may be missed. CPU percent can exceed 100% on multi-core systems.",
        }


def prepare_output_dir(root: Path, audio_path: Path, model_name: str) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    out = root.expanduser().resolve() / f"{audio_path.stem}_{model_name}_{stamp}"
    out.mkdir(parents=True, exist_ok=False)
    return out


def write_outputs(out_dir: Path, records: Iterable[SegmentRecord], metadata: dict[str, Any]) -> None:
    rows = list(records)
    transcript = "\n".join(row.text.strip() for row in rows).strip()
    (out_dir / "transcript.txt").write_text(transcript, encoding="utf-8")
    with (out_dir / "segments.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=["start", "end", "text", "avg_logprob", "no_speech_prob"])
        writer.writeheader()
        writer.writerows(asdict(row) for row in rows)
    (out_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8"
    )


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    """Return a streaming SHA-256 digest without loading the file into memory."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_evaluation(args: argparse.Namespace) -> Path:
    audio_path: Path = args.audio.expanduser().resolve()
    if not audio_path.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    if args.device != "cpu":
        raise ValueError("This verified build is CPU-only. CUDA support will be added after a separate driver/runtime verification.")
    if args.compute_type not in ("int8", "float32"):
        raise ValueError("CPU mode supports int8 or float32 in this package")
    if args.threads < 0:
        raise ValueError("--threads cannot be negative")

    reference_text = None
    if args.reference is not None:
        reference_path = args.reference.expanduser().resolve()
        if not reference_path.is_file():
            raise FileNotFoundError(f"Reference transcript not found: {reference_path}")
        reference_text = reference_path.read_text(encoding="utf-8-sig")

    duration = get_audio_duration(audio_path)
    if args.max_audio_seconds is not None:
        if duration is None:
            raise RuntimeError(
                "Audio duration could not be read, so --max-audio-seconds cannot be enforced. "
                "The run was stopped to avoid silently bypassing the safety limit."
            )
        if duration > args.max_audio_seconds:
            raise ValueError(
                f"Audio duration {duration:.1f}s exceeds --max-audio-seconds {args.max_audio_seconds:.1f}s"
            )

    model_cache_dir = args.model_cache_dir.expanduser().resolve()
    download_started = time.perf_counter()
    snapshot_path, resolved_commit = resolve_model_snapshot(
        args.model, args.model_revision, model_cache_dir, args.local_files_only
    )
    download_seconds = time.perf_counter() - download_started
    if not snapshot_path.is_dir() or not (snapshot_path / "config.json").is_file() or not (snapshot_path / "model.bin").is_file():
        raise RuntimeError(
            f"Downloaded model snapshot is incomplete or not a Faster-Whisper CTranslate2 checkpoint: {snapshot_path}"
        )

    input_hash_started = time.perf_counter()
    audio_sha256 = sha256_file(audio_path)
    reference_sha256 = sha256_file(reference_path) if args.reference is not None else None
    input_hash_seconds = time.perf_counter() - input_hash_started

    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError("faster-whisper is not installed. Run scripts/setup.ps1 or pip install -r requirements.txt") from exc

    monitor = ResourceMonitor()
    monitor.start()
    try:
        load_started = time.perf_counter()
        model_kwargs: dict[str, Any] = {"device": args.device, "compute_type": args.compute_type}
        if args.threads:
            model_kwargs["cpu_threads"] = args.threads
        print(f"Loading {MODEL_REPOSITORIES[args.model]} ({resolved_commit or args.model_revision}) on {args.device}/{args.compute_type}...")
        model = WhisperModel(str(snapshot_path), **model_kwargs)
        model_load_seconds = time.perf_counter() - load_started

        inference_started = time.perf_counter()
        segments_iter, info = model.transcribe(
            str(audio_path),
            language=args.language,
            beam_size=args.beam_size,
            vad_filter=args.vad,
        )
        records: list[SegmentRecord] = []
        # Faster-Whisper returns a lazy generator. Consuming it is what performs inference.
        for segment in segments_iter:
            records.append(SegmentRecord(
                start=float(segment.start),
                end=float(segment.end),
                text=str(segment.text),
                avg_logprob=safe_float(getattr(segment, "avg_logprob", None)),
                no_speech_prob=safe_float(getattr(segment, "no_speech_prob", None)),
            ))
        transcription_seconds = time.perf_counter() - inference_started
        runtime_compute_type = getattr(getattr(model, "model", None), "compute_type", None)
        if runtime_compute_type is not None:
            runtime_compute_type = str(runtime_compute_type)
    finally:
        resource_metrics = monitor.stop()

    duration_source = "pyav_stream_or_container_metadata" if duration is not None else None
    if duration is None:
        runtime_duration = safe_float(getattr(info, "duration", None))
        if runtime_duration is not None and runtime_duration > 0:
            duration = runtime_duration
            duration_source = "faster_whisper_transcription_info"
        elif records:
            duration = max(row.end for row in records)
            duration_source = "estimated_from_last_transcribed_segment_end"
        else:
            duration_source = "unavailable"
    real_time_factor = (transcription_seconds / duration) if duration and duration > 0 else None
    transcript = "\n".join(row.text.strip() for row in records).strip()
    accuracy_metrics = calculate_accuracy_metrics(reference_text, transcript) if reference_text is not None else None
    if accuracy_metrics and accuracy_metrics["reference_is_empty_after_normalization"] and duration and duration > 0:
        accuracy_metrics["potential_false_positive_words_per_minute"] = (
            accuracy_metrics["potential_false_positive_word_count_for_silence_test"] / (duration / 60.0)
        )
        accuracy_metrics["silence_test_warning"] = (
            "Interpret as false positives only when the supplied reference is intentionally empty "
            "and the audio has been verified to contain no speech."
        )
    total_runtime_seconds = download_seconds + model_load_seconds + transcription_seconds

    metadata = {
        "project": "local-speech-model-evaluation-verification",
        "package_version": "1.2.0",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "audio_file": str(audio_path),
        "audio_file_size_bytes": audio_path.stat().st_size,
        "audio_sha256": audio_sha256,
        "reference_sha256": reference_sha256,
        "audio_duration_seconds": duration,
        "audio_duration_source": duration_source,
        "model": args.model,
        "model_repository": MODEL_REPOSITORIES[args.model],
        "model_revision_requested": args.model_revision,
        "model_resolved_commit": resolved_commit,
        "model_snapshot_path": str(snapshot_path),
        "model_commit_recorded": resolved_commit is not None,
        "backend": "faster-whisper / CTranslate2",
        "device": args.device,
        "compute_type_requested": args.compute_type,
        "compute_type_reported_by_runtime": runtime_compute_type,
        "cpu_threads_requested": args.threads,
        "language_requested": args.language,
        "language_detected": getattr(info, "language", None),
        "language_probability": safe_float(getattr(info, "language_probability", None)),
        "beam_size": args.beam_size,
        "vad_filter": args.vad,
        "reference_file": str(args.reference.expanduser().resolve()) if args.reference else None,
        "accuracy_metrics": accuracy_metrics,
        "timing": {
            "model_download_or_cache_seconds": download_seconds,
            "input_hashing_seconds": input_hash_seconds,
            "model_load_seconds": model_load_seconds,
            "transcription_seconds_including_generator_consumption": transcription_seconds,
            "download_plus_load_plus_transcription_seconds": total_runtime_seconds,
            "real_time_factor": real_time_factor,
            "real_time_factor_definition": "transcription_seconds / audio_duration_seconds; model download and load excluded",
        },
        "resources": resource_metrics,
        "segment_count": len(records),
        "environment": {
            "python_version": sys.version,
            "platform": platform.platform(),
            "processor": platform.processor() or None,
            "package_versions": {
                "faster-whisper": package_version("faster-whisper"),
                "ctranslate2": package_version("ctranslate2"),
                "av": package_version("av"),
                "huggingface-hub": package_version("huggingface-hub"),
                "tokenizers": package_version("tokenizers"),
                "onnxruntime": package_version("onnxruntime"),
                "rapidfuzz": package_version("rapidfuzz"),
                "tqdm": package_version("tqdm"),
                "psutil": package_version("psutil"),
                "pytest": package_version("pytest"),
                "all_installed_distributions": installed_distribution_versions(),
            },
        },
    }
    out_dir = prepare_output_dir(args.output_dir, audio_path, args.model)
    write_outputs(out_dir, records, metadata)
    return out_dir


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        out_dir = run_evaluation(args)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"\nCompleted. Results: {out_dir}")
    print("See metadata.json for model commit, timing, WER/CER (when --reference is supplied), and sampled RAM/CPU.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
