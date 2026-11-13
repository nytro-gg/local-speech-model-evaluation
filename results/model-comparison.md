# Model Comparison

| Model | Local Execution | Main Observation | Practical Limitation |
|---|---|---|---|
| Parakeet — Experiment 1 | Not practical | Very high memory requirement | Could not be practically executed on the available hardware |
| Parakeet — Experiment 2 | Successful | Very strong transcription performance | Required audio to be processed in smaller chunks |
| Faster-Whisper | Successful | Practical for local transcription experiments | Performance and output depend on inference settings and input processing |

## Key Takeaway

The experiments demonstrated that there is no single factor that determines whether an AI model is practical for local deployment.

Model capability must be considered alongside memory requirements, processing method, input length, and the hardware available to the user.
