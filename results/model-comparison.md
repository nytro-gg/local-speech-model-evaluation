# Model Comparison

This file separates completed experiments from pending tests. Runs must use the same audio and equivalent settings before speed or quality comparisons are made.

| Model / experiment | Status | Configuration / observation | Practical limitation or caveat |
|---|---|---|---|
| Parakeet — Experiment 1 | Unsuccessful on tested hardware | Attempted local execution | Approximately 22.8 GB CPU buffer allocation was attempted; not practical in that setup |
| Parakeet — Experiment 2 | Successful | Local GGUF-based workflow | Required audio to be processed in smaller chunks |
| Faster-Whisper Small — 12-minute baseline | Completed | CPU INT8, VAD off, automatic language; 731.74 s audio transcribed in 145.80 s; RTF 0.19925; peak sampled process RSS 1,064 MiB | User judged transcript subjectively very good; no verified reference, so WER/CER are unavailable |
| Faster-Whisper Small — forced English | Completed | CPU INT8, VAD off; 138.58 s transcription; 85 segments | Similar-looking output, including repeated phrases near the end; no verified accuracy score |
| Faster-Whisper Small — default VAD | Completed, rejected as a valid benchmark | CPU INT8, VAD on; two segments, about 3.84 s retained from 731.74 s input | Nearly all audio discarded; reported RTF is misleading because it uses full input duration |
| Faster-Whisper Medium — 12-minute comparison | Completed; qualitative review preliminary | CPU INT8, automatic language, VAD off; 302.09 s transcription; RTF 0.41283; 2,644 MiB peak sampled RSS; 147 segments | No verified reference transcript; accuracy advantage over Small is not established |

## VAD diagnostic observations

VAD-only timestamp experiments (not Whisper transcription benchmarks) produced the following retained-audio percentages for the same 731.74-second recording:

| Processing window | Threshold | Retained audio | Retention |
|---:|---:|---:|---:|
| Entire recording | 0.50 | 3.84 s | 0.52% |
| Entire recording | 0.20 | 9.84 s | 1.34% |
| 30 s | 0.50 | 145.09 s | 19.83% |
| 60 s | 0.50 | 92.06 s | 12.58% |
| 120 s | 0.50 | 65.07 s | 8.89% |
| 300 s | 0.50 | 14.29 s | 1.95% |
| 30 s | 0.20 | 319.50 s | 43.66% |

These are detection/retention statistics only. They do not prove that the retained material is speech or that rejected portions are silence. The user reports the source recording contains silence, faint/distorted voice, and substantial background noise. VAD is not recommended for this recording until the detection behaviour is understood and verified against listening or labelled speech regions.

## Key Takeaway

There is no single factor that determines whether a speech model is practical for local deployment. Model capability must be considered alongside memory requirements, processing method, input length, audio conditions, and available hardware.

For the November 2026 Small baseline, the measured transcription speed is promising. Formal model-accuracy comparisons still require a manually verified reference transcript.


## Small vs Medium — 13 November 2026

Both runs used the same 731.74-second M4A recording, CPU INT8, automatic language detection, beam size 5, and VAD off.

| Metric | Small | Medium |
|---|---:|---:|
| Transcription time | 145.80 s | 302.09 s |
| RTF | 0.19925 | 0.41283 |
| Peak sampled process RSS | 1,064 MiB | 2,644 MiB |
| Average sampled process CPU | 358.43% | 385.76% |
| Segments | 63 | 147 |
| Language probability | 0.29498 | 0.35788 |

Small is approximately 2.07 times faster and uses approximately 2.49 times less peak sampled process memory. Both are faster than real time. Medium's transcript contains some promising lecture-specific terms in the inspected output, but includes fragmented opening text. No verified reference transcript is available; do not rank accuracy from subjective impression alone.
