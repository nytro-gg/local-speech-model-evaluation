import argparse
import json
from pathlib import Path

import pytest

from src.evaluate import (
    SegmentRecord,
    build_parser,
    calculate_accuracy_metrics,
    edit_counts,
    get_audio_duration,
    positive_int,
    positive_seconds,
    write_outputs,
)


def test_positive_seconds_accepts_positive_values():
    assert positive_seconds("12.5") == 12.5


@pytest.mark.parametrize("value", ["0", "-1", "abc", "nan", "inf", "-inf"])
def test_positive_seconds_rejects_invalid_values(value):
    with pytest.raises(argparse.ArgumentTypeError):
        positive_seconds(value)


@pytest.mark.parametrize("value", ["0", "-2", "1.5", "abc"])
def test_positive_int_rejects_invalid_values(value):
    with pytest.raises(argparse.ArgumentTypeError):
        positive_int(value)


def test_parser_defaults_to_safe_cpu_int8_and_records_reference_support(tmp_path):
    args = build_parser().parse_args(["--audio", str(tmp_path / "sample.wav")])
    assert args.device == "cpu"
    assert args.compute_type == "int8"
    assert args.model == "small"
    assert args.model_revision == "main"
    assert args.reference is None
    assert args.threads == 0
    assert args.max_audio_seconds == 120.0


def test_wer_cer_known_case_and_normalization():
    metrics = calculate_accuracy_metrics("The cat sat.", "the cat sit!")
    assert metrics["wer"] == pytest.approx(1 / 3)
    assert metrics["word_errors"] == {
        "substitutions": 1, "insertions": 0, "deletions": 0, "errors": 1
    }
    assert metrics["cer"] is not None


def test_unicode_composed_and_decomposed_text_normalize_identically():
    metrics = calculate_accuracy_metrics("café", "cafe\u0301")
    assert metrics["wer"] == 0.0
    assert metrics["cer"] == 0.0


def test_edit_counts_reports_insertions_deletions_and_substitutions():
    assert edit_counts(["a", "b"], ["a", "b", "c"])["insertions"] == 1
    assert edit_counts(["a", "b"], ["a"])["deletions"] == 1
    assert edit_counts(["a", "b"], ["a", "x"])["substitutions"] == 1


def test_large_transcript_scoring_uses_optimized_distance_backend():
    # This size would make the previous Python O(N*M) matrix dangerously large.
    reference = "speech " * 12000
    hypothesis = "speech " * 11999 + "spoken"
    metrics = calculate_accuracy_metrics(reference, hypothesis)
    assert metrics["wer"] == pytest.approx(1 / 12000)
    assert metrics["word_errors"]["errors"] == 1


def test_empty_reference_is_explicitly_undefined_not_division_by_zero():
    metrics = calculate_accuracy_metrics("!!!", "some words")
    assert metrics["wer"] is None
    assert metrics["cer"] is None
    assert metrics["undefined_reason"]


def test_write_outputs_creates_transcript_csv_and_metadata(tmp_path):
    rows = [SegmentRecord(0.0, 1.2, " Hello world ", -0.2, 0.01)]
    metadata = {"model": "small", "accuracy_metrics": {"wer": 0.0}}
    write_outputs(tmp_path, rows, metadata)
    assert (tmp_path / "transcript.txt").read_text(encoding="utf-8").strip() == "Hello world"
    assert "start,end,text" in (tmp_path / "segments.csv").read_text(encoding="utf-8-sig")
    assert json.loads((tmp_path / "metadata.json").read_text(encoding="utf-8")) == metadata


def test_duration_fails_cleanly_if_pyav_not_installed(monkeypatch, tmp_path):
    import sys
    monkeypatch.setitem(sys.modules, "av", None)
    with pytest.raises(RuntimeError, match="PyAV is unavailable"):
        get_audio_duration(tmp_path / "fake.wav")


def test_duration_limit_fails_closed_when_duration_is_unknown(tmp_path, monkeypatch):
    import src.evaluate as evaluator

    audio = tmp_path / "clip.wav"
    audio.write_bytes(b"placeholder")
    monkeypatch.setattr(evaluator, "get_audio_duration", lambda _path: None)
    args = build_parser().parse_args([
        "--audio", str(audio), "--max-audio-seconds", "60",
        "--output-dir", str(tmp_path / "results"),
    ])
    with pytest.raises(RuntimeError, match="cannot be enforced"):
        evaluator.run_evaluation(args)


def test_duration_limit_rejects_file_over_limit(tmp_path, monkeypatch):
    import src.evaluate as evaluator

    audio = tmp_path / "clip.wav"
    audio.write_bytes(b"placeholder")
    monkeypatch.setattr(evaluator, "get_audio_duration", lambda _path: 120.0)
    args = build_parser().parse_args([
        "--audio", str(audio), "--max-audio-seconds", "60",
        "--output-dir", str(tmp_path / "results"),
    ])
    with pytest.raises(ValueError, match="exceeds"):
        evaluator.run_evaluation(args)


def test_resolve_model_snapshot_records_hash_from_snapshot_path(tmp_path, monkeypatch):
    import sys
    from types import SimpleNamespace
    import src.evaluate as evaluator

    commit = "a" * 40
    snapshot = tmp_path / "models" / "snapshots" / commit
    snapshot.mkdir(parents=True)
    called = {}

    def fake_snapshot_download(**kwargs):
        called.update(kwargs)
        return str(snapshot)

    monkeypatch.setitem(sys.modules, "huggingface_hub", SimpleNamespace(snapshot_download=fake_snapshot_download))
    path, resolved = evaluator.resolve_model_snapshot("small", "main", tmp_path / "cache", False)
    assert path == snapshot.resolve()
    assert resolved == commit
    assert called["repo_id"] == "Systran/faster-whisper-small"
    assert called["revision"] == "main"


def test_mocked_end_to_end_run_writes_accuracy_provenance_and_resource_metrics(tmp_path, monkeypatch):
    import sys
    from types import SimpleNamespace
    import src.evaluate as evaluator

    audio = tmp_path / "spoken.wav"
    reference = tmp_path / "spoken.txt"
    audio.write_bytes(b"mock audio payload")
    reference.write_text("Hello world", encoding="utf-8")
    snapshot = tmp_path / "snapshot" / ("b" * 40)
    snapshot.mkdir(parents=True)
    (snapshot / "config.json").write_text("{}", encoding="utf-8")
    (snapshot / "model.bin").write_bytes(b"mock model")
    monkeypatch.setattr(evaluator, "get_audio_duration", lambda _path: 2.0)
    monkeypatch.setattr(evaluator, "resolve_model_snapshot", lambda *args: (snapshot, "b" * 40))

    class FakeSegment:
        start = 0.0
        end = 1.8
        text = " Hello world."
        avg_logprob = -0.1
        no_speech_prob = 0.0

    class FakeModel:
        def __init__(self, model_path, **kwargs):
            assert Path(model_path) == snapshot
            assert kwargs["device"] == "cpu"
            assert kwargs["compute_type"] == "int8"

        def transcribe(self, _audio, **_kwargs):
            return iter([FakeSegment()]), SimpleNamespace(language="en", language_probability=0.99)

    monkeypatch.setitem(sys.modules, "faster_whisper", SimpleNamespace(WhisperModel=FakeModel))
    args = build_parser().parse_args([
        "--audio", str(audio), "--reference", str(reference),
        "--output-dir", str(tmp_path / "results"),
    ])
    output = evaluator.run_evaluation(args)
    metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
    assert metadata["model_repository"] == "Systran/faster-whisper-small"
    assert metadata["model_resolved_commit"] == "b" * 40
    assert len(metadata["audio_sha256"]) == 64
    assert len(metadata["reference_sha256"]) == 64
    assert metadata["audio_duration_source"] == "pyav_stream_or_container_metadata"
    assert "rapidfuzz" in metadata["environment"]["package_versions"]
    assert metadata["environment"]["package_versions"]["all_installed_distributions"]
    assert metadata["accuracy_metrics"]["wer"] == 0.0
    assert metadata["timing"]["transcription_seconds_including_generator_consumption"] >= 0
    assert "process_rss_peak_sampled_mb" in metadata["resources"]
    assert (output / "transcript.txt").read_text(encoding="utf-8").strip() == "Hello world."


def test_silence_reference_reports_potential_false_positives():
    metrics = calculate_accuracy_metrics("", "thank you for watching")
    assert metrics["wer"] is None
    assert metrics["potential_false_positive_word_count_for_silence_test"] == 4
    assert metrics["reference_is_empty_after_normalization"] is True


def test_audio_duration_reads_audio_stream_metadata(tmp_path, monkeypatch):
    import sys
    from types import SimpleNamespace
    import src.evaluate as evaluator

    class FakeContainer:
        streams = [SimpleNamespace(type="audio", duration=48000, time_base=1 / 16000)]
        duration = None
        def __enter__(self):
            return self
        def __exit__(self, *_args):
            return False

    fake_av = SimpleNamespace(open=lambda _path: FakeContainer(), time_base=1_000_000)
    monkeypatch.setitem(sys.modules, "av", fake_av)
    assert evaluator.get_audio_duration(tmp_path / "sample.wav") == pytest.approx(3.0)


def test_sha256_file_streams_content_and_returns_expected_digest(tmp_path):
    import hashlib
    from src.evaluate import sha256_file

    target = tmp_path / "input.bin"
    target.write_bytes(b"verified input")
    assert sha256_file(target) == hashlib.sha256(b"verified input").hexdigest()


def test_verified_build_is_cpu_only():
    from src.evaluate import SUPPORTED_DEVICES, SUPPORTED_COMPUTE_TYPES
    assert SUPPORTED_DEVICES == ("cpu",)
    assert set(SUPPORTED_COMPUTE_TYPES) == {"int8", "float32"}


def test_registered_models_use_official_systran_repositories():
    from src.evaluate import MODEL_REPOSITORIES
    assert MODEL_REPOSITORIES["small"] == "Systran/faster-whisper-small"
    assert MODEL_REPOSITORIES["medium"] == "Systran/faster-whisper-medium"
    assert MODEL_REPOSITORIES["large-v3"] == "Systran/faster-whisper-large-v3"
