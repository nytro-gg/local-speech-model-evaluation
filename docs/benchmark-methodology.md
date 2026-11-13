# Benchmark Methodology and Measurement Notes

## Matched Faster-Whisper comparison

The primary comparison uses the same original M4A input for Faster-Whisper Small and Medium.

### Input and controls

| Item | Setting |
|---|---|
| Recording duration | 731.743229 seconds (12 min 11.74 sec) |
| Input | Same M4A file for both models; original left unchanged |
| Device | CPU |
| Requested compute type | INT8 |
| Runtime-reported compute type | `int8_float32` |
| Language | Automatic detection |
| Beam size | 5 |
| VAD | Off |
| Maximum audio duration | 900 seconds |
| Python | 3.12.10, 64-bit |
| OS | Windows 11 x64 |
| System RAM reported | 23,960.07 MB (~23.96 GB) |

### Model revisions and results

| Measurement | Small | Medium |
|---|---:|---:|
| Model repository | `Systran/faster-whisper-small` | `Systran/faster-whisper-medium` |
| Resolved commit | `536b0662742c02347bc0e980a01041f333bce120` | `08e178d48790749d25932bbc082711ddcfdfbc4f` |
| Download/cache time | 30.420 s | 66.484 s |
| Model load time | 10.558 s | 3.518 s |
| Transcription time | 145.798 s | 302.089 s |
| Download + load + transcription | 186.776 s | 372.092 s |
| RTF | 0.19925 | 0.41283 |
| Segments | 63 | 147 |
| Detected language | English | English |
| Language probability | 0.29498 | 0.35788 |
| Peak sampled process RSS | 1,064.01 MB | 2,644.46 MB |
| Average sampled process CPU | 358.43% | 385.76% |
| Peak sampled process CPU | 425% | 425% |

### Metric definitions

- **Transcription time** is measured through consumption of the lazy segment generator. Model snapshot resolution/download and model construction are reported separately.
- **Real-time factor (RTF)** = transcription seconds ÷ audio duration seconds. Lower is faster; below 1 means transcription completed faster than playback time.
- **Peak sampled process RSS** is the largest resident-set-size sample recorded by the process monitor. Sampling interval was 250 ms, so brief peaks may be missed. It is not a measurement of total system RAM consumed by the model alone.
- **Average process CPU** can exceed 100% because usage is measured across multiple logical processors.
- **Segments** are output segment count, not a transcript accuracy score.
- **Language probability** is the value returned by the runtime for automatic language detection in these two runs; it does not measure transcription correctness.

### Interpretation

Small completed the measured transcription in 145.798 seconds compared with 302.089 seconds for Medium. Medium took about 2.07× as long. Medium's peak sampled process RSS was about 2.49× Small's. Both RTF values were below 1.

These are single-run observations. The model order, cache state and normal process variation can affect timings. Three or more repeated warm-cache runs and medians would be preferable for a formal performance study. The current project does not present the measurements as repeated-run results.

## Accuracy and transcript review

No human-verified reference transcript was supplied for the recording. WER/CER are therefore unavailable. The user's listening impression of the Small transcript and the observed wording in Medium are qualitative notes only. They must not be converted into a formal claim that one model is more accurate.

The source recording contained silence, faint/distorted speech and background noise in sections, as reported after listening to two excerpts. The original file was not denoised, normalized, trimmed or otherwise modified.

## VAD investigation

A separate default whole-file VAD run retained two segments totaling approximately 3.84 seconds (0.52%) from the 731.74-second input. Its short runtime and RTF are not comparable with the VAD-off full-input runs.

Separate timestamp-only sweeps—not Whisper transcription benchmarks—showed:

| Windowing | Threshold | Regions | Retained | Retention |
|---|---:|---:|---:|---:|
| Whole file | 0.50 | 1 | 3.84 s | 0.52% |
| Whole file | 0.20 | 4 | 9.84 s | 1.34% |
| 30-second chunks | 0.50 | 37 | 145.09 s | 19.83% |
| 60-second chunks | 0.50 | 20 | 92.06 s | 12.58% |
| 120-second chunks | 0.50 | 12 | 65.07 s | 8.89% |
| 300-second chunks | 0.50 | 4 | 14.29 s | 1.95% |
| 30-second chunks | 0.20 | 57 | 319.50 s | 43.66% |

Retention figures show how much audio the VAD timestamps retained; they do not prove that retained regions are speech or that rejected regions are silence. The current default VAD behavior is not recommended for this recording.

## Historical experiments kept separate

- An earlier documented Faster-Whisper run processed a 3,466.26-second recording in 26.64 seconds. It is a separate historical run and must not be compared directly with the November 12-minute Small/Medium runs.
- A separate Small run explicitly forced English and reported language probability 1.0. Because English was supplied, that is not an independent automatic-detection confidence result.
- Earlier Parakeet work included an attempted CPU buffer allocation of 22,837,892,192 bytes (~22.8 GB) and a different GGUF-based workflow reported as successful with chunking constraints. The exact successful artifact/revision/runtime was not preserved; Parakeet is not part of the reproducible package.

## Reproducibility checklist

To extend this benchmark responsibly:

1. Use the exact same input file and record its SHA-256.
2. Pin the model repository and 40-character resolved revision.
3. Keep language, beam size, VAD, compute type and audio-duration cap identical.
4. Record cold download/cache, model load and transcription times separately.
5. Run at least three repeats where practical and report median plus spread.
6. Use a manually verified reference transcript for WER/CER; do not infer accuracy from segment count or language probability.
7. Keep private or permission-restricted audio and transcripts out of the public repository.
