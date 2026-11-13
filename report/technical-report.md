# Local Speech Recognition Benchmark — Technical Report

## 1. Abstract

This project evaluates the practical challenges of running speech-to-text models locally on consumer Windows hardware. It combines an executable CPU-first Faster-Whisper evaluation harness with documented Parakeet experiments, installation troubleshooting, VAD diagnostics, performance measurements and resource observations.

The main matched benchmark compared Faster-Whisper Small and Medium on the same 731.743-second recording using CPU INT8, automatic language detection, beam size 5 and VAD disabled. Small completed transcription in 145.798 seconds with 1,064.01 MB peak sampled process RSS; Medium completed in 302.089 seconds with 2,644.46 MB. Both were faster than real time. No verified reference transcript was supplied, so WER/CER and a formal accuracy ranking are unavailable.

## 2. Objectives

- Run open-source speech-recognition models locally.
- Measure transcription time, real-time factor, process memory and CPU usage.
- Record model revisions, runtime configuration and environment details.
- Investigate long-form audio and Voice Activity Detection behavior.
- Document installation failures, successful fixes and hardware limitations.
- Keep private recordings and generated transcripts out of the public repository.

## 3. Models and scope

### Faster-Whisper

The reproducible package implements Faster-Whisper using CTranslate2. The verified configuration is CPU-first and supports INT8 or float32 compute types. The November comparison tested Small and Medium. CUDA/GPU inference was not enabled or benchmarked.

### Parakeet

Parakeet was explored in earlier experiments using a GGUF-based local workflow. One attempt encountered an attempted CPU buffer allocation of 22,837,892,192 bytes (~22.8 GB) and could not continue on the tested system. A separate configuration was documented as successful with smaller audio chunks, but its exact model artifact, revision, conversion and runtime were not preserved sufficiently to reproduce it. Parakeet is therefore a historical exploratory result, not part of the current runnable evaluation harness.

## 4. Experimental environment

| Item | Recorded value |
|---|---|
| Operating system | Windows 11 x64 |
| Shell | Windows PowerShell 5.1 |
| Python | CPython 3.12.10, 64-bit |
| Faster-Whisper | 1.2.1 |
| CTranslate2 | 4.8.5 |
| PyAV | 17.1.0 |
| Hugging Face Hub | 0.36.0 |
| Tokenizers | 0.23.3 |
| ONNX Runtime | 1.31.1 |
| RapidFuzz | 3.14.6 |
| psutil | 7.2.2 |
| pytest | 8.4.2 |
| System RAM reported | approximately 23.96 GiB |
| Inference device | CPU |

The exact CPU product name was not preserved in the benchmark metadata, so this report does not infer one. GPU inference and GPU memory were not measured.

## 5. Matched November 2026 benchmark

### Protocol

A 731.743-second (12 min 11.74 sec) M4A file was used for both model runs. The source recording remained unchanged. Both runs used CPU INT8, automatic language detection, beam size 5, VAD off and a 900-second duration ceiling. Model download/cache, model load and transcription times were recorded separately. The RTF uses transcription time only.

### Results

| Metric | Faster-Whisper Small | Faster-Whisper Medium |
|---|---:|---:|
| Model commit | `536b0662742c02347bc0e980a01041f333bce120` | `08e178d48790749d25932bbc082711ddcfdfbc4f` |
| Download/cache | 30.420 s | 66.484 s |
| Model load | 10.558 s | 3.518 s |
| Transcription | 145.798 s | 302.089 s |
| Total download + load + transcription | 186.776 s | 372.092 s |
| RTF | 0.19925 | 0.41283 |
| Peak sampled process RSS | 1,064.01 MB | 2,644.46 MB |
| Average sampled process CPU | 358.43% | 385.76% |
| Peak sampled process CPU | 425% | 425% |
| Segments | 63 | 147 |
| Detected language | English | English |
| Language probability | 0.29498 | 0.35788 |

Small was approximately 2.07 times faster and used approximately 2.49 times less peak sampled process RSS in the measured runs. Both RTF values were below 1. These are single-run measurements, not repeated-run medians. RSS and CPU were sampled every 250 ms, so brief peaks may not be captured.

### Accuracy limitation

No human-verified reference transcript was supplied. WER/CER were not computed. The user considered the Small transcript subjectively very good compared with other tools they had tried; the Medium transcript contained some recognizable lecture-specific wording but also fragmented sections. These are qualitative observations only and do not prove that one model is more accurate.

## 6. VAD investigation

A separate whole-file default VAD run retained only about 3.84 seconds (0.52%) of the 731.74-second recording. The two emitted segments do not represent a valid full-recording benchmark. Timestamp-only VAD sweeps varied considerably with chunk size and threshold; for example, 30-second chunks at threshold 0.5 retained 19.83%, while 300-second chunks retained 1.95%. These retention figures do not prove that the retained regions are speech. The default VAD configuration is not recommended for this recording without further diagnosis.

## 7. Historical experiments (not directly comparable)

An earlier Faster-Whisper run documented 3,466.26 seconds of audio processed in 26.64 seconds. This is a separate historical run with different context and is not part of the matched November Small/Medium comparison.

A separate Small run explicitly forced English and reported language probability 1.0. Since the language was supplied to the decoder, this value is not an independent automatic language-detection confidence measurement. The matched comparison used automatic detection and reported 0.29498 for Small and 0.35788 for Medium.

## 8. Installation and engineering lessons

Setup issues included Python runtime discovery, interrupted CTranslate2 wheel transfers, and non-fatal Hugging Face warnings about missing `hf_xet` and unavailable Windows symlinks. The Python discovery logic was replaced, the CTranslate2 installation succeeded after pip retry/resume options, and Hugging Face completed downloads using its fallback modes. Full details are in [Installation and Troubleshooting](../docs/installation-and-troubleshooting.md) and the [chronological experiment log](../experiments/experiment-log.md).

The verified package pins the direct runtime dependencies, records model revisions and input hashes, consumes the lazy segment generator before stopping the timer, samples resource usage, validates input duration, checks model cache files, and uses RapidFuzz edit operations for optional WER/CER to avoid a large quadratic Python object matrix.

## 9. Conclusion

The experiments show that model size alone does not determine local practicality. In this matched run, Small offered lower transcription time and lower process-memory usage than Medium. VAD behavior was unexpectedly sensitive to processing-window choices on this difficult recording. Parakeet demonstrated a significant memory-allocation constraint in one configuration, while another earlier chunked workflow was not preserved sufficiently for reproducibility.

The strongest supported conclusion is about measured speed and resource trade-offs—not formal transcription accuracy. Human-verified references, repeated runs, a broader consented dataset and GPU compatibility checks would be required for stronger claims.

## 10. Future work

- Run at least three warm-cache repeats and report medians and spread.
- Create a consented, human-verified reference set across speech conditions and speakers.
- Diagnose VAD retention against manually reviewed speech regions.
- Preserve exact model artifacts and revisions for any future Parakeet reproduction.
- Treat GPU benchmarking as a separate compatibility and measurement task.
