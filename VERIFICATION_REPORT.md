# Safety Verification Report — Package 1.2.0

## Independent package audit

The source ZIP was inspected without running model inference or downloading model weights.

- Python source compiled successfully with `py_compile`.
- CLI `--help` smoke test passed.
- Automated test suite independently rerun during audit: **28 passed**.
- No API-key-like strings, passwords, private-key headers, bearer tokens, or absolute Windows user paths were found in the packaged text files.
- PowerShell setup and runner scripts were statically reviewed; they were not executed in the audit environment.
- The original `SHA256SUMS.txt` did not match the submitted archive as packaged: the archive omitted several entries listed in the manifest, and the packaged `scripts/setup.ps1` hash differed. A corrected manifest is included with the repository publication; it hashes the listed source files and does not claim to hash the ZIP archive.

## Windows laptop verification

The user’s Windows 11 x64 environment used CPython 3.12.10.

- `pip check`: no broken requirements found.
- Core native imports: passed.
- User-run automated suite: 28 passed.
- Faster-Whisper Small and Medium both completed CPU INT8 transcription on the same 731.743-second M4A recording with VAD off and automatic language detection.

| Metric | Small | Medium |
|---|---:|---:|
| Transcription time | 145.798 s | 302.089 s |
| Real-time factor | 0.19925 | 0.41283 |
| Peak sampled process RSS | 1,064.01 MiB | 2,644.46 MiB |
| Segments | 63 | 147 |

These are single-run results. Medium took approximately 2.07 times as long and used approximately 2.49 times the peak sampled process RSS. The user judged the Small transcript subjectively very good compared with other tools previously tried. Some lecture-specific phrases were visible in the Medium transcript, but no formal accuracy winner is claimed.

## VAD finding

A separate default whole-file VAD experiment retained only approximately 3.84 seconds (0.52%) of the 731.74-second recording. Its runtime is not a comparable full-recording benchmark because most input audio was excluded. Do not use the current default VAD setting for this recording until the behavior is understood.

## Code-level risks addressed in package 1.2.0

1. **High RAM risk in WER/CER:** the previous full Python O(N×M) edit-distance matrix was replaced with RapidFuzz's optimized Levenshtein edit operations.
2. **Unpinned CTranslate2:** the baseline pins version 4.8.5 for repeatability rather than silently accepting the newer 4.9.0 release.
3. **Unbounded first-run input:** the quick-run helper and CLI default enforce a 120-second ceiling.
4. **Unsupported GPU path:** the verified package exposes CPU only until the actual NVIDIA driver, CUDA/cuDNN runtime, and CTranslate2 compatibility are separately established.
5. **Architecture/runtime mismatch:** setup checks for 64-bit Python 3.11/3.12 and performs native import checks before model download.
6. **Invalid numeric duration values:** non-finite limits such as NaN and infinity are rejected; unknown input duration causes a fail-closed stop when a duration cap is active.
7. **Model cache ambiguity:** the evaluator checks that the resolved snapshot contains the expected CTranslate2 `config.json` and `model.bin`.
8. **Input reproducibility:** audio and optional reference transcript SHA-256 hashes are stored in local run metadata.

## Verification boundaries and remaining limitations

- The build-time verification described in the original package was performed separately from the user’s Windows laptop run. The PowerShell scripts were statically reviewed during this audit, not executed in the Linux audit environment.
- The model run metrics in this repository came from one run per model; repeated runs and median comparisons remain future work.
- No human-verified reference transcript was supplied. WER/CER are unavailable, and subjective impressions must not be presented as formal accuracy scores.
- The audio contained faint/distorted speech and background noise in sections, based on the user's listening. The original recording was intentionally left unchanged.
- GPU benchmarking, Large-v3 evaluation, and broader multilingual/noise/diarization testing are outside the current verified scope.
