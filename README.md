# Local Speech-to-Text Model Evaluation

An experimental study of locally hosted speech-to-text models on consumer hardware.

## Overview

This project explores the practical challenges of running modern speech recognition models locally rather than relying entirely on cloud-based inference.

The experiments focused on Parakeet and Faster-Whisper, with particular attention to memory requirements, audio processing, model limitations, and the trade-offs involved in local deployment.

## Objectives

* Evaluate modern speech-to-text models on consumer hardware
* Understand the memory and computational requirements of local inference
* Compare different approaches to processing recorded audio
* Identify practical limitations when deploying models locally
* Document failures, successful experiments, and lessons learned

## Models Explored

* Parakeet
* Faster-Whisper

## Key Areas Investigated

* RAM and computational requirements
* Local model inference
* Audio chunking
* Voice Activity Detection (VAD)
* Transcription behaviour
* Processing limitations
* Local hardware vs. server-based inference

## Status

Experimental project — documentation and results are being compiled.

## Experimental Evidence

The project includes selected screenshots documenting the actual experiments and development process.

### Faster-Whisper

- [Successful transcription](evidence/01_faster_whisper_success.png)
- [Automatic language detection](evidence/02_language_detection_en.png)
- [Python implementation](evidence/03_transcribe_py.png)

### Parakeet

- [Memory allocation failure](evidence/04_parakeet_memory_failure.png)
- [Audio processing details](evidence/05_audio_processing_details.png)
- [Parakeet CLI/model setup](evidence/06_parakeet_cli.png)
