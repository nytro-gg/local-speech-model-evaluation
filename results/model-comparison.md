# Model Comparison

## Matched Faster-Whisper comparison — 13 November 2026

Both models processed the same 731.743-second recording with CPU INT8, automatic language detection, beam size 5 and VAD off.

| Metric | Small | Medium |
|---|---:|---:|
| Transcription time | **145.80 s** | 302.09 s |
| RTF | **0.19925** | 0.41283 |
| Peak sampled process RSS | **1,064.01 MB** | 2,644.46 MB |
| Average sampled process CPU | 358.43% | 385.76% |
| Segments | 63 | 147 |
| Language probability | 0.29498 | 0.35788 |

Small was about 2.07× faster and used about 2.49× less peak sampled process RSS in these single runs. Both completed faster than real time. RSS/CPU samples were taken every 250 ms.

**Accuracy:** No human-verified reference transcript was supplied. WER/CER are unavailable; subjective transcript observations do not establish an accuracy winner.

## Other completed experiments

| Experiment | Outcome | Interpretation |
|---|---|---|
| Small, forced English, VAD off | 138.58 s; 85 segments | Explicit language setting did not remove repeated phrases near the end. Probability 1.0 is not independent detection confidence because English was forced. |
| Small, default whole-file VAD | 3.84 s retained from 731.74 s input | Not a valid full-recording benchmark; nearly all input was discarded. |
| Parakeet allocation attempt | Attempted 22.8 GB CPU buffer allocation | Failed on the tested system due to resource requirements. |
| Earlier Parakeet chunked workflow | Successful output reported | Chunking constraints noted; exact artifact/revision/runtime not preserved for repeatability. |

## VAD-only timestamp diagnostics

These tests measured retained timestamps only—not transcription quality or speech-recognition accuracy.

| Processing window | Threshold | Regions | Retained audio | Retention |
|---:|---:|---:|---:|---:|
| Entire recording | 0.50 | 1 | 3.84 s | 0.52% |
| Entire recording | 0.20 | 4 | 9.84 s | 1.34% |
| 30 s | 0.50 | 37 | 145.09 s | 19.83% |
| 60 s | 0.50 | 20 | 92.06 s | 12.58% |
| 120 s | 0.50 | 12 | 65.07 s | 8.89% |
| 300 s | 0.50 | 4 | 14.29 s | 1.95% |
| 30 s | 0.20 | 57 | 319.50 s | 43.66% |

Retention is not proof that a region contains speech. Default VAD is not recommended for this recording until its behavior is checked against manually reviewed regions.

## Historical run kept separate

An earlier Faster-Whisper run documented a 3,466.26-second recording transcribed in 26.64 seconds. It is not comparable to the matched 12-minute November benchmark and is retained only as historical evidence.
