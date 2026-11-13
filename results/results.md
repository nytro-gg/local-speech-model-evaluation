# Experimental Results

## Summary

The experiments revealed that local speech-to-text deployment involves important trade-offs between model capability, memory usage, input size, and hardware limitations.

## Parakeet — Experiment 1

The first Parakeet model could not be practically executed on the available local hardware because its memory requirements were too high.

**Result:** Not practical for the tested system.

## Parakeet — Experiment 2

The second Parakeet model successfully ran locally and produced very strong transcription results.

However, the model required recordings to be processed in smaller chunks rather than treating a long recording as a single continuous input.

**Result:** Successful inference, but with an important input-processing limitation.

## Faster-Whisper — Earlier experiments

Faster-Whisper was successfully explored as a local speech-to-text solution. Earlier work documented a successful CPU INT8 run processing 3,466.26 seconds of audio in 26.64 seconds. That result belongs to the earlier experiment and should not be conflated with the separate 12-minute test recorded below.

## Faster-Whisper — 12-minute recording (13 November 2026)

A 731.74-second M4A recording was evaluated locally using Faster-Whisper Small on CPU with INT8. The original audio was kept unchanged.

### Small, automatic language, VAD off

| Metric | Result |
|---|---:|
| Model revision | 536b0662742c02347bc0e980a01041f333bce120 |
| Transcription time | 145.80 s |
| Real-time factor | 0.19925 |
| Segments | 63 |
| Peak sampled process RSS | 1,064 MiB |
| Average sampled process CPU | 358.43% |
| Language detected | English |
| Language probability | 0.295 |

The user judged this first transcript subjectively very good compared with other transcription tools they had tried. This is a qualitative listening assessment, not a formal accuracy score.

### Small, forced English, VAD off

| Metric | Result |
|---|---:|
| Transcription time | 138.58 s |
| Real-time factor | 0.18938 |
| Segments | 85 |
| Peak sampled process RSS | 1,065 MiB |
| Average sampled process CPU | 388.81% |

Forcing English did not visibly resolve the repeated phrases observed toward the end of the transcript. The language probability of 1.0 is not an independent detection-confidence measurement because English was explicitly supplied.

### Small, forced English, VAD on

The default whole-file VAD run emitted only two segments, retaining approximately 3.84 seconds (0.52%) of the 731.74-second input. Its 3.78-second runtime and reported real-time factor are not comparable to the VAD-off runs because almost all of the input was discarded.

### VAD diagnostics

The diagnostic sweeps were not Whisper transcription benchmarks. They measured how much audio Silero VAD marked as speech.

| Processing window | Threshold | Regions | Retained audio | Retention |
|---:|---:|---:|---:|---:|
| Entire recording | 0.50 | 1 | 3.84 s | 0.52% |
| Entire recording | 0.20 | 4 | 9.84 s | 1.34% |
| 30 s | 0.50 | 37 | 145.09 s | 19.83% |
| 60 s | 0.50 | 20 | 92.06 s | 12.58% |
| 120 s | 0.50 | 12 | 65.07 s | 8.89% |
| 300 s | 0.50 | 4 | 14.29 s | 1.95% |
| 30 s | 0.20 | 57 | 319.50 s | 43.66% |

These findings show that VAD retention depends strongly on processing-window length and threshold for this particular recording. Retained audio is not necessarily correctly detected speech. The user reported periods of silence, faint/distorted speech, and substantial background noise when listening to excerpts.

**Current VAD conclusion:** Do not use the present default VAD configuration for this recording. Investigate VAD windowing, state handling, and retained-duration reporting before recommending VAD for long-form recordings.

## Faster-Whisper Medium — same 12-minute recording

Configuration: CPU INT8, automatic language detection, VAD off. Model revision: 08e178d48790749d25932bbc082711ddcfdfbc4f.

| Metric | Medium result |
|---|---:|
| Transcription time | 302.09 s |
| Real-time factor | 0.41283 |
| Peak sampled process RSS | 2,644.46 MiB |
| Average sampled process CPU | 385.76% |
| Segments | 147 |
| Language detected | English |
| Language probability | 0.35788 |
| Model download/cache | 66.48 s |
| Model loading | 3.52 s |

The Medium transcript contains recognizable lecture-specific concepts in inspected sections, including traffic flow, checkpoints, variables, eigenvalues, and eigenvectors. Its opening also contains isolated dots and fragmented phrases. The user has not yet provided a human-verified reference transcript, so WER/CER are unavailable and no formal accuracy winner is declared.

### Small vs Medium

| Metric | Small | Medium |
|---|---:|---:|
| Transcription time | 145.80 s | 302.09 s |
| Real-time factor | 0.19925 | 0.41283 |
| Peak sampled process RSS | 1,064.01 MiB | 2,644.46 MiB |
| Average sampled process CPU | 358.43% | 385.76% |
| Segments | 63 | 147 |
| Language probability | 0.29498 | 0.35788 |

Both runs used the same 731.74-second source recording, CPU INT8, automatic language detection, beam size 5, and VAD off. Medium took approximately 2.07 times as long and used approximately 2.49 times the peak sampled process RSS. Small is the faster and more memory-efficient option. Both were faster than real time: about 5.02x for Small and 2.42x for Medium.

The user previously judged the Small baseline subjectively very good compared with other transcription tools. Medium has promising qualitative wording in some inspected sections, but its accuracy advantage remains unproven without an aligned, human-verified reference transcript.



## Accuracy measurement limitation

No human-verified reference transcript has yet been supplied for the 12-minute recording. Consequently, WER and CER are not available for the Small runs. Subjective comparisons are useful observations, but formal model accuracy comparisons require a verbatim, manually checked reference.

## Overall Observation

Model performance alone does not determine whether a model is practical for local deployment. Memory requirements, processing method, input length, audio quality, and available hardware can significantly affect usability.

See [the chronological experiment log](../experiments/experiment-log.md) for setup failures, error resolutions, detailed VAD diagnostics, environment details, and cleanup policy.

