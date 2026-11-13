# Installation and Troubleshooting

This page summarizes the setup problems observed while preparing the local Windows evaluation environment. The detailed chronological record is in [the experiment log](../experiments/experiment-log.md).

| Issue | Observed behavior | Resolution / interpretation |
|---|---|---|
| Python runtime discovery | Initial setup script stopped with `No suitable Python runtime found`. | Reworked setup to enumerate installed interpreters with `py -0p`, select 64-bit Python 3.12 (or 3.11), and verify interpreter architecture before creating `.venv`. |
| Setup script file copy | First copy attempt failed because the replacement script was not yet in the expected Downloads path. | Downloaded the replacement script and copied it into the project `scripts/` directory. |
| CTranslate2 wheel download | pip disconnected repeatedly while downloading the approximately 20.4 MB wheel, failing near 19 MB after multiple attempts. | Retried with `python -m pip install --resume-retries 15 --timeout 120 -r requirements.txt`; installation completed. |
| `hf_xet` missing | Hugging Face warned that Xet storage was enabled but `hf_xet` was not installed. | Non-fatal; regular HTTP download fallback was used. No installation was required for the benchmark. |
| Windows symlink capability | Hugging Face warned that Windows symlinks were unavailable for its cache. | Non-fatal; cache operated in a less space-efficient fallback mode. |
| Parakeet memory allocation | An earlier Parakeet attempt requested a CPU buffer of 22,837,892,192 bytes (~22.8 GB). | The tested system could not satisfy that allocation. This was recorded as a hardware/resource limitation, not a Faster-Whisper failure. |

## Verified environment checks

The Windows setup completed on 64-bit CPython 3.12.10. The following checks passed:

- `python -m pip check` — no broken requirements found.
- Core imports for Faster-Whisper, CTranslate2, PyAV, ONNX Runtime, RapidFuzz and psutil.
- `python -m pytest -q` — 28 tests passed (2.76 seconds in the initial setup check; 0.35 seconds in the later clean-clone run).
- Both Faster-Whisper Small and Medium completed CPU INT8 inference on the same 731.74-second recording with VAD off.

## Re-run setup

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\setup.ps1
```

The setup script checks the installed Python Launcher runtime list and does not modify or uninstall system-wide Python installations. It creates dependencies inside the project `.venv`.

## Warnings versus failures

The `hf_xet` and symlink messages were warnings with successful fallback behavior. They should not be described as failed model downloads. The CTranslate2 transfer interruptions were genuine installation failures that were resolved through pip retry/resume options.
