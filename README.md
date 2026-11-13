# Local Speech-to-Text Model Evaluation

An experimental study of locally hosted speech-to-text models on consumer hardware.

## Overview

This project explores the practical challenges of running modern speech recognition models locally rather than relying entirely on cloud-based inference.

The experiments focus on Parakeet and Faster-Whisper, with particular attention to memory requirements, audio processing, model limitations, long-form recordings, and the trade-offs involved in local deployment.

## Objectives

* Evaluate modern speech-to-text models on consumer hardware
* Understand the memory and computational requirements of local inference
* Compare different approaches to processing recorded audio
* Identify practical limitations when deploying models locally
* Document failures, successful experiments, and lessons learned
* Keep a reproducible chronological lab notebook

## Models Explored

* Parakeet
* Faster-Whisper Small and Medium

## Key Areas Investigated

* RAM and computational requirements
* Local model inference
* Audio chunking
* Voice Activity Detection (VAD)
* Transcription behaviour and repetition
* Long-form audio processing
* Processing limitations
* Local hardware vs. server-based inference

## Current Research Snapshot — 13 November 2026

A 731.74-second M4A recording was used for matched Faster-Whisper Small and Medium CPU INT8 runs. Both used automatic language detection, beam size 5, and VAD off. The original audio was kept unchanged.

- Small completed transcription in 145.80 seconds (RTF 0.19925; peak sampled process RSS 1,064 MiB; 63 segments).
- Medium completed transcription in 302.09 seconds (RTF 0.41283; peak sampled process RSS 2,644 MiB; 147 segments).
- Small was approximately 2.07 times faster and used approximately 2.49 times less peak sampled process memory.
- The user judged the first Small transcript subjectively very good compared with other tools previously tried. Medium contains some promising lecture-specific wording, but no formal accuracy winner can be declared.
- No human-verified reference transcript was provided, so WER/CER are unavailable.
- A separate default whole-file VAD run retained only about 3.84 seconds of the input. VAD is not recommended for this recording with the current settings.

These are single-run results, with sampled resource measurements; they are not repeated-run medians or broad model-accuracy claims.

See the [experimental results](results/results.md) for the concise summary and the [experiment log](experiments/experiment-log.md) for setup errors, commands, metrics, VAD diagnostics, decisions, and cleanup policy.

## Runnable Source Package

The repository now includes the CPU-first Faster-Whisper evaluation harness, PowerShell setup and runner scripts, pinned direct dependencies, and automated tests.

- [Package quickstart and usage](docs/package-quickstart.md)
- [Model verification notes](MODEL_NOTES.md)
- [Test protocol](TEST_PROTOCOL.md)
- [Verification report](VERIFICATION_REPORT.md)
- [Changelog](CHANGELOG.md)
- [Python evaluator](src/evaluate.py)
- [Automated tests](tests/test_evaluate.py)

The first smoke test intentionally defaults to a maximum audio duration of 120 seconds. Longer recordings require an explicit `--max-audio-seconds` override.

## Earlier Findings

- Local ML deployment can have substantially higher runtime memory requirements than the model size alone suggests.
- One Parakeet experiment attempted to allocate approximately 22.8 GB of CPU buffer memory during audio processing.
- An earlier Faster-Whisper experiment processed 3,466.26 seconds of audio in 26.64 seconds using CPU INT8 inference. This is a separate historical run, not the November 2026 12-minute benchmark.

## Project Documentation

- [Technical Report](report/technical-report.md)
- [Experiment Environment](report/experiment-environment.md)
- [Experimental Results](results/results.md)
- [Model Comparison](results/model-comparison.md)
- [Chronological Experiment Log / Lab Notebook](experiments/experiment-log.md)
- [Experimental Evidence](evidence/README.md)

## Repository Hygiene

The repository intentionally excludes private/local audio, transcripts, temporary audio excerpts, downloaded model weights, virtual environments, caches, and generated per-run result folders. The local cleanup plan retains system-wide Git and Python installations for other coursework and development.

## Status

The Small and Medium CPU benchmark runs are complete for the current 12-minute sample. Research remains preliminary: formal WER/CER comparisons require manually verified reference transcripts, and broader robustness testing would require a properly consented and labelled test set.

## Experimental Evidence

The project includes selected screenshots documenting earlier experiments and the development process.

### Faster-Whisper

- [Successful transcription](evidence/01_faster_whisper_success.png)
- [Automatic language detection](evidence/02_language_detection_en.png)
- [Python implementation](evidence/03_transcribe_py.png)

### Parakeet

- [Memory allocation failure](evidence/04_parakeet_memory_failure.png)
- [Audio processing details](evidence/05_audio_processing_details.png)
- [Parakeet CLI/model setup](evidence/06_parakeet_cli.png)
