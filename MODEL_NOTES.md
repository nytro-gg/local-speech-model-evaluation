# Model verification notes — Package 1.2.0

## Model artifacts

The runner uses the official Systran Faster-Whisper CTranslate2 repositories:

- `Systran/faster-whisper-tiny`
- `Systran/faster-whisper-base`
- `Systran/faster-whisper-small`
- `Systran/faster-whisper-medium`
- `Systran/faster-whisper-large-v3`

The first baseline is `small` on CPU with INT8. The resolved model commit and complete installed Python package set are captured in each run metadata file. A snapshot is downloaded from Hugging Face on the first run, and the resolved 40-character commit SHA is recorded. The evaluator refuses a snapshot missing the expected `config.json` or `model.bin`. Model weights are not embedded in the source package. The user downloaded and ran the Small and Medium checkpoints locally; the completed results are documented in [results/results.md](results/results.md).

## Pinned runtime baseline

- faster-whisper 1.2.1
- CTranslate2 4.8.5
- huggingface-hub 0.36.0
- PyAV 17.1.0
- tokenizers 0.23.3
- ONNX Runtime 1.31.1
- RapidFuzz 3.14.6
- psutil 7.2.2
- pytest 8.4.2

CTranslate2 4.8.5 was selected as a recent pre-4.9.0 baseline rather than silently taking CTranslate2 4.9.0, which was released shortly before this package build. The runner is deliberately CPU-only; CUDA will be introduced after the exact NVIDIA driver, CUDA/cuDNN runtime, and CTranslate2 compatibility have been verified on the target machine.

## Runtime and measurements

- Faster-Whisper returns a lazy segment generator. Timing ends only after every segment has been consumed.
- Model snapshot resolution/download, model construction, input hashing, and transcription durations are recorded separately.
- The real-time factor uses the audio duration from PyAV metadata where available. If that is missing, it uses the duration reported by Faster-Whisper; as a last resort the final segment end is labelled as an estimate.
- Process RSS and CPU are sampled during model load and inference. CPU averaging excludes the priming sample. A 250 ms sample interval can still miss very brief peaks.
- Audio and reference file SHA-256 hashes are stored in metadata.
- WER/CER uses Unicode NFC normalization, case-folding, punctuation removal, and whitespace collapsing before scoring. RapidFuzz edit operations avoid a quadratic Python object matrix.

## Historical Parakeet caveat

The original repository documented one Parakeet attempt requesting approximately 22.8 GB of CPU buffer memory, and a different successful route with chunking constraints. It does not preserve the exact successful repository ID, artifact revision, conversion, runtime version, and checksum needed for a reproducible re-run. This package intentionally does not guess that artifact.

## What model-quality verification remains

Real model accuracy cannot be inferred from a model card, installation success, or unit tests. It requires locally transcribed test recordings paired with human-checked reference transcripts. A broader set is needed for Indian English accents, background noise, silence false positives, and long-form audio. No real-world accuracy claim is made until the local measurements exist.
