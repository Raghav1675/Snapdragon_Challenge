# AURA — Target Deployment Guide

## Deployment objective

AURA is designed as a local-first AI application for deployment on Snapdragon-powered HP PCs. The application separates user experience, document processing, retrieval and privacy logic from the model runtime so the inference layer can be replaced or optimized for the target Qualcomm environment.

## What is already local

- PDF and DOCX extraction
- Text and CSV processing
- Image OCR when Tesseract is installed
- Privacy-pattern detection
- Redaction logic
- Local TF-IDF retrieval
- Prompt construction
- Streamlit user interface
- Benchmarking and runtime inspection

## Current development inference path

The default build uses Ollama through:

```text
http://127.0.0.1:11434
```

The development model is:

```text
 gemma3:1b
```

This keeps the reference application easy to reproduce and test locally.

## Target Snapdragon optimization path

For the final target deployment:

1. Install the supported local inference/runtime stack for the specific Snapdragon environment.
2. Select a Qualcomm AI Hub or other supported open-source model that matches the target hardware and runtime.
3. Keep the existing `OllamaClient` contract at the application boundary or provide a second client implementing the same generate/status interface.
4. Run the benchmark script on the deployment machine.
5. Record model name, average latency, min/max latency and any relevant runtime metrics.
6. Use only those measured values in the final submission materials.

## Evidence to capture for the presentation

Capture the following during the target deployment:

- AURA home screen
- source upload
- grounded answer with evidence
- adaptive explanation
- privacy findings and redaction
- quiz generation
- runtime/model information
- benchmark results

## Current recorded development baseline

From the 30 September 2026 development run:

| Measurement | Result |
|---|---:|
| Benchmark runs | 3 |
| Model | gemma3:1b |
| Average | 2.79 s |
| Minimum | 1.61 s |
| Maximum | 4.79 s |
| Example document Q&A | 6.03 s |
| Example quiz generation | 10.55 s |
| Automated tests | 4/4 passed |

These values document the working development build. They must not be treated as universal hardware-performance guarantees. Re-run the benchmark if the model, runtime or target machine changes.

## Deployment principles

### Privacy first

AURA should not require a hosted AI endpoint for its core document workflow.

### Grounding first

Questions should be answered from retrieved source material when the user asks about an uploaded source. When the context is insufficient, the model should say so rather than inventing a fact.

### Measured claims only

The final competition materials should distinguish clearly between:

- implemented features,
- target deployment capabilities, and
- measured performance.

Do not present a target capability as an already-measured result.
