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

## Faster-Whisper

Faster-Whisper was successfully explored as a local speech-to-text solution.

The experiment also involved techniques such as Voice Activity Detection (VAD), timestamps, and inference configuration.

**Result:** Practical for the local workflow and suitable for further experimentation.

## Overall Observation

The experiments showed that model performance alone does not determine whether a model is practical for local deployment.

Memory requirements, processing method, input length, and available hardware can significantly affect usability.

A model that works efficiently on a server may require substantially different resources when executed directly on a consumer computer.
