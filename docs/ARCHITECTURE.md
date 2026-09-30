# AURA Architecture

## Design principle

AURA separates application logic from the local model runtime. This keeps the user experience stable while allowing the inference engine to change from Ollama to another local runtime, including a Qualcomm AI Hub/QNN-backed model for a Snapdragon deployment.

## Data flow

```text
Input file/image
      |
      v
Local extraction (PyMuPDF / python-docx / OCR)
      |
      +----------------------+
      |                      |
      v                      v
Privacy scan            Text normalization
      |                      |
      |                      v
      |                 Chunking
      |                      |
      |                      v
      |                TF-IDF retrieval
      |                      |
      +-----------> Local LLM prompt
                             |
                             v
                   Adaptive response
                             |
                   +---------+---------+
                   |         |         |
                   v         v         v
                Answer    Explanation  Quiz
```

## Why local-first

Documents are often the very data that users do not want to upload. The repository therefore contains no telemetry, no analytics SDK and no cloud AI integration. The only AI network call supported by the default build is to the Ollama HTTP API on the same machine.

## Retrieval strategy

The current implementation uses TF-IDF + cosine similarity. This is deliberately lightweight and deterministic, which makes the first deployment easy to inspect and benchmark. It can be replaced with local embeddings later without changing the UI or document ingestion layer.

## Model strategy

The default local model is `gemma3:1b` because it is small enough for local prototyping. For a Snapdragon competition submission, the model should be benchmarked on the actual device. A Qualcomm AI Hub model can be introduced at the `aura.llm` interface boundary when the exact target hardware and supported runtime are known.
