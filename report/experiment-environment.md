# Experiment Environment

## Verified November 2026 environment

| Item | Value |
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
| System RAM reported by evaluator | 23,960.07 MB (~23.96 GB) |

The exact CPU product name was not preserved in the run metadata. The project therefore reports the recorded system facts without inferring a CPU model. The November Faster-Whisper comparison used CPU inference; no GPU/CUDA inference was performed.

## Faster-Whisper configuration

- Same 731.743-second M4A input for Small and Medium.
- CPU, requested INT8 (runtime-reported `int8_float32`).
- Automatic language detection, beam size 5, VAD off.
- Maximum audio duration 900 seconds.
- Model repository and resolved commit recorded in each run's metadata.
- Resource samples every 250 ms; brief peaks may be missed.

See [benchmark methodology](../docs/benchmark-methodology.md) for the exact matched results and metric definitions.

## Earlier Parakeet environment

The earlier Parakeet experiments used a GGUF-based local workflow and audio conversion to 16 kHz mono WAV. A ~57-minute recording was used in one historical setup. The exact successful model artifact and revision were not preserved sufficiently for a reproducible re-run. A separate attempt requested about 22.8 GB of CPU buffer memory and failed on the tested system.
