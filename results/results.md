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

## Faster-Whisper Medium — pending

The 1.53 GB Medium model download completed and the process began loading the model on CPU INT8. The completed transcription output and metadata have not yet been captured. No Medium performance or quality result is claimed here.

## Accuracy measurement limitation

No human-verified reference transcript has yet been supplied for the 12-minute recording. Consequently, WER and CER are not available for the Small runs. Subjective comparisons are useful observations, but formal model accuracy comparisons require a verbatim, manually checked reference.

## Overall Observation

Model performance alone does not determine whether a model is practical for local deployment. Memory requirements, processing method, input length, audio quality, and available hardware can significantly affect usability.

See [the chronological experiment log](../experiments/experiment-log.md) for setup failures, error resolutions, detailed VAD diagnostics, environment details, and cleanup policy.


## Faster-Whisper Medium — run completed, metrics pending

A Medium-model evaluation was completed on 13 November 2026 using the same 731.74-second M4A input as the Small runs. Configuration: CPU INT8, automatic language detection, VAD off, 900-second maximum. Model: Systran/faster-whisper-medium, resolved commit 08e178d48790749d25932bbc082711ddcfdfbc4f. The 1.53 GB model download completed, and the evaluator created result directory test12_medium_20261113_165725_692132.

The console emitted non-fatal Hugging Face warnings: hf_xet was unavailable (regular HTTP fallback used) and Windows symlink support was unavailable (less space-efficient cache fallback used).

The Medium run's metadata and transcript have not yet been inspected, so no performance or quality result is claimed. See the chronological experiment log for details and next steps.
