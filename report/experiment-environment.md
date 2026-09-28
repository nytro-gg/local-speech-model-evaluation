# Experiment Environment

## Local Environment

The experiments were performed locally on a Windows-based consumer computer using terminal-based workflows.

## Software

- Python
- Faster-Whisper
- Parakeet
- FFmpeg
- PowerShell
- Visual Studio build tools
- llama.cpp / Parakeet GGUF tooling

## Faster-Whisper Configuration

One documented transcription run used:

- Model: Faster-Whisper Medium
- Device: CPU
- Compute type: INT8

A separate test used the Faster-Whisper Small model for language detection.

## Parakeet Configuration

The Parakeet experiments involved locally running a GGUF-based Parakeet model through Parakeet/llama.cpp tooling.

The experiment also involved converting recorded audio into WAV format before processing.

## Input Audio

One documented Parakeet test used an audio recording approximately 57 minutes long.

The audio was converted to a 16 kHz mono WAV file before processing.

## Important Note

The exact hardware specifications and model versions will be documented separately once verified from the original experiment logs and screenshots.
