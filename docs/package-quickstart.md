# Local Speech Model Evaluation — Package Quickstart (1.2.0)

Continuation of `nytro-gg/local-speech-model-evaluation`. This package is a CPU-first, Windows x64 evaluation harness for Faster-Whisper. The package has been exercised on a Windows 11 x64 laptop with Python 3.12.10: setup dependencies were installed and checked, the 28-test suite passed, and both Small and Medium CPU INT8 inference runs completed on the same 731.74-second recording. The measured runs are summarized in [the research results](../results/results.md). No human-verified reference transcript was supplied, so no formal WER/CER accuracy result is available.

## Safety and verification changes in 1.2.0

- Replaced the full Python edit-distance matrix with RapidFuzz's native Levenshtein edit script. The previous approach could allocate a huge O(reference × hypothesis) Python object matrix for long transcripts.
- Pinned the core runtime stack, including CTranslate2 4.8.5. CTranslate2 4.9.0 was released on 10 November 2026; we avoid silently taking that just-released runtime in this baseline.
- Limited this verified runner to CPU/INT8 or CPU/float32. CUDA is deliberately unavailable until its NVIDIA driver, CUDA/cuDNN runtime, and CTranslate2 compatibility can be checked on the actual laptop.
- Setup now checks 64-bit Python 3.11/3.12, verifies native package imports, then runs the test suite before model download.
- The quick-run PowerShell script and the CLI default both reject audio longer than 120 seconds. This prevents accidentally launching a long recording during the first smoke test. Raise `--max-audio-seconds` explicitly when you are ready for longer recordings.
- The evaluator verifies the downloaded snapshot contains `config.json` and `model.bin` before attempting model load.
- Records SHA-256 hashes for input audio and reference transcript so benchmark inputs can be identified exactly.
- Keeps model revision and resolved Hugging Face commit SHA in metadata.

## Recommended first run

1. Extract this ZIP into a normal folder, e.g. `C:\AI\local-speech-model-evaluation-verification-1.2.0`.
2. Open PowerShell in that folder.
3. Run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\setup.ps1
```

The setup script uses an existing 64-bit Python 3.11 or 3.12 via `py.exe`. It does not uninstall or globally modify other Python installations. If an existing project `.venv` is incompatible, the script stops and tells you to remove only that project's `.venv` folder. It runs `pip check` and imports the native packages (including Tokenizers and ONNX Runtime) before downloading a speech model. If a native import fails with a missing DLL, install the latest Microsoft Visual C++ v14 x64 Redistributable from [Microsoft's official page](https://aka.ms/vc14/vc_redist.x64.exe), restart PowerShell, and rerun setup.

4. Put one human-speech clip of 30–120 seconds in `audio` (WAV or MP3 is recommended for the first test).
5. Run:

```powershell
.\scripts\run-small.ps1 -Audio .\audio\sample.wav
```

The first run downloads Faster-Whisper Small from the official Systran model repository. The model weights are not included in this ZIP. Model files are multi-hundred-MB assets and are downloaded into the local Hugging Face cache only when the user runs the evaluator.

## Measure accuracy (WER/CER)

Create `audio\sample.txt`, encoded as UTF-8, containing a human-checked verbatim transcript of the same audio. Then run:

```powershell
.\scripts\run-small.ps1 -Audio .\audio\sample.wav -Reference .\audio\sample.txt
```

WER and CER are calculated after Unicode case-folding, punctuation removal, and whitespace normalization. This means punctuation/capitalization are not scored. Empty references produce undefined WER/CER; on verified digital silence, the evaluator also reports the number of generated words as potential false positives. The reference must be checked against the actual recording.

The accuracy backend uses RapidFuzz Levenshtein edit operations to avoid a quadratic Python object matrix. Error operation counts are one valid minimum-edit alignment; ambiguous edit sequences can have more than one equally optimal S/I/D breakdown, while the total edit count remains the Levenshtein distance.

## Compare Small and Medium

After Small works, run Medium against the exact same audio and reference:

```powershell
.\.venv\Scripts\python.exe -m src.evaluate --audio .\audio\sample.wav --model medium --device cpu --compute-type int8 --reference .\audio\sample.txt --max-audio-seconds 120
```

Do not compare models using different audio, language constraints, beam sizes, VAD settings, or reference transcripts. For a quality-only comparison, keep every decoding setting identical. For speed/resource comparison, run three repeats and compare medians.

## Models

| Name | Official CTranslate2 repository |
|---|---|
| tiny | `Systran/faster-whisper-tiny` |
| base | `Systran/faster-whisper-base` |
| small | `Systran/faster-whisper-small` |
| medium | `Systran/faster-whisper-medium` |
| large-v3 | `Systran/faster-whisper-large-v3` |

The model commit SHA is captured per run. Use `--model-revision <40-character-commit>` to repeat against a specific snapshot later. Do not assume `main` will always point to the same model revision.

## What is measured

- Model snapshot download/cache resolution time.
- Model constructor/load time.
- Full transcription time, including consuming the lazy segment generator.
- Real-time factor (transcription seconds divided by audio seconds; download and load excluded).
- Sampled process RSS and CPU, plus system RAM available at start/end. Resource sampling runs every 250 ms and may miss brief peaks.
- Detected language and probability, when supplied by the runtime. Audio-duration source is recorded: PyAV metadata first, then Faster-Whisper's reported duration, and only as a last resort the final segment end is labelled as an estimate.
- Optional WER/CER and edit counts against a human reference.
- Environment versions (including the complete installed Python distribution list), model repo/revision/commit, input file sizes and SHA-256 hashes.

## Scope and limitations

- CPU only in this verified build. CUDA and GPU memory measurement are deliberately deferred.
- Parakeet is not included because the original repository does not preserve the exact successful model ID, artifact commit, conversion, and runtime needed to reproduce it safely. The historical Parakeet failure attempted about 22.8 GB of CPU buffer allocation. We will not guess which model you previously used.
- WER/CER do not measure meaning, speaker attribution, punctuation, diarization, or factual correctness. A small speech set cannot establish general performance for all Indian English accents or noisy environments.
- The current local Small and Medium run measurements are documented in the repository results. They are single-run observations, not repeated-run medians or general accuracy claims.
- The package pins direct runtime dependencies. Pip may resolve compatible transitive dependencies; preserve the generated environment report and model commit SHA for each benchmark.

See [the test protocol](../TEST_PROTOCOL.md) and [the verification report](../VERIFICATION_REPORT.md).


## Current benchmark note

The 12-minute Small and Medium comparisons were run with CPU INT8, automatic language detection, beam size 5, and VAD off. Small was faster and used less sampled process memory in the measured runs. Because no manually verified reference transcript is available, the project does not claim that either model is more accurate. The original audio was not denoised or otherwise modified.
