# Changelog

## 1.2.0 — 2026-11-13

- Replaced quadratic-memory Python WER/CER DP matrix with RapidFuzz edit operations.
- Pinned CTranslate2 4.8.5 and the core dependency stack for a repeatable CPU baseline.
- Made this verified build CPU-only; removed unverified CUDA modes.
- Limited setup to 64-bit Python 3.11/3.12 and added native import smoke check.
- Added a 120-second default audio cap to the CLI and first-run PowerShell helper.
- Added setup-time `pip check` and native import checks for Tokenizers and ONNX Runtime.
- Added CTranslate2 checkpoint preflight and input SHA-256 metadata.
- Expanded tests for large transcripts, hashes, and supported runtime modes.

## 1.1.0

- Added WER/CER, model revision capture, sampled process resources, and safer audio duration checks.
