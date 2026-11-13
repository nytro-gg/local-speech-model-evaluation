# Model Evaluation Protocol

## First smoke test (required)

- Use one 30–120 second recording with clear speech.
- Use one speaker, no sensitive or private recording unless you have permission to process it.
- Start with Faster-Whisper Small, CPU, INT8, automatic language detection, beam size 5, VAD off.
- The PowerShell helper and CLI default enforce the 120-second ceiling. Do not raise it for the first run.
- Inspect the transcript manually. Confirm metadata shows the expected model commit and a non-zero segment count.

## Accuracy and robustness set

Use independent human-checked references for each clip:

1. Clean English speech (30–120 seconds).
2. Indian English speech with natural accent and pace (1–3 minutes).
3. Realistic background noise (1–3 minutes).
4. Verified silence/room tone (30–60 seconds) with an intentionally empty reference.
5. Longer recordings, gradually increasing from 5 to 15 to 30 minutes after memory behaviour is understood.

Do not treat one speaker or one accent as representative of all Indian English. Use consented audio. Do not record conversations without permission.

## Small versus Medium

For each spoken clip, use identical settings and exactly the same source audio/reference for both models. Run three speed/resource repeats where practical. Compare median run times and sampled peak RSS. Keep the initial model download/cache time separate from warm-cache model load and transcription time.

## Metrics

- WER and CER: lower is better, but both are normalized edit-distance metrics, not semantic correctness. Punctuation and capitalization are excluded by this normalization.
- Substitutions/insertions/deletions: one minimum-edit alignment; ties can change the breakdown, not the total error count.
- RTF: transcription seconds divided by audio duration; below 1 is faster than real time.
- Sampled RSS/CPU: process measurements at 250 ms intervals; short peaks can be missed.
- Silence false-positive count: interpret only when the audio is confirmed to contain no speech and the reference is intentionally empty.

## Reporting

For every run preserve `metadata.json`, transcript, segments CSV, audio/reference hashes, model repository and resolved commit, hardware, Python/package versions, language and decoding settings. Compare results only when the input and settings are matched.
