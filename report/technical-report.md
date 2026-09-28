# Local Speech-to-Text Model Evaluation

## 1. Abstract

This project investigates the practical challenges of running modern speech-to-text models locally on consumer hardware. The experiments involved Parakeet and Faster-Whisper, with a focus on memory requirements, audio processing, local inference, language detection, and practical deployment limitations.

## 2. Objective

The objective was to understand how capable speech-to-text models behave when deployed directly on a personal computer rather than through a remote server or cloud API.

The experiment specifically examined:

* Memory and computational requirements
* Local inference
* Audio processing
* Language detection
* Voice Activity Detection (VAD)
* Input and processing limitations
* Differences between local and server-based deployment

## 3. Models Explored

### Parakeet

Multiple Parakeet configurations were explored during the experiment.

The first configuration successfully loaded the model but failed during audio processing because the system could not allocate the required CPU buffer. The observed allocation request was approximately 22.8 GB.

A later Parakeet configuration was successfully tested and produced very strong results, but the workflow introduced constraints around how recordings had to be processed.

### Faster-Whisper

Faster-Whisper was explored as a practical local speech-to-text alternative.

The experiments included different model sizes, CPU inference, INT8 computation, language detection, beam search, and Voice Activity Detection.

## 4. Experimental Environment

The experiments were performed locally on consumer hardware using Windows, Python, terminal-based workflows, and locally downloaded models.

The Faster-Whisper implementation used CPU inference with INT8 computation.

## 5. Observations

### Memory Requirements

One of the most important observations was that a model's published size does not represent its total runtime memory requirement.

During the Parakeet experiment, the model loaded successfully, but processing the audio triggered an attempted CPU buffer allocation of approximately 22.8 GB.

This demonstrated the difference between model size and actual runtime memory requirements.

### Audio Processing

Long recordings introduced additional practical constraints. Different models and implementations handle long-form audio differently, and some approaches required audio to be processed in smaller sections.

This became an important consideration when evaluating local deployment.

### Faster-Whisper

Faster-Whisper successfully processed recorded audio locally.

The experiments also demonstrated automatic language detection. One test detected English with a reported probability of 1.00.

## 6. Engineering Lessons

The experiments showed that selecting an ML model for local deployment requires more than looking at its accuracy or model size.

Hardware requirements, memory usage, input handling, inference configuration, and processing strategy all affect whether a model is practically usable.

A model that performs well on server infrastructure may behave very differently on a consumer computer with limited memory and compute resources.

## 7. Conclusion

The main conclusion from the experiments is that local ML deployment involves significant engineering trade-offs.

Powerful models can require substantial memory and computational resources. When resource requirements are reduced through different approaches, other constraints may appear, such as input-size or audio-processing limitations.

The experience emphasized the importance of researching a model's deployment requirements before attempting to host it locally.

## 8. Future Work

Future experiments could compare additional speech-to-text models under the same hardware conditions and measure:

* Peak RAM usage
* Processing time
* Real-time factor
* Transcription quality
* Long-form audio performance
* CPU versus GPU inference
* Different quantization levels
