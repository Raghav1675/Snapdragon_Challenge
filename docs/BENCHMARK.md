# AURA Benchmark Report

**Recorded:** 30 September 2026

## Development benchmark

The included benchmark script was run three times using the configured local model.

| Metric | Result |
|---|---:|
| Model | `gemma3:1b` |
| Benchmark runs | 3 |
| Average generation time | **2.79 s** |
| Minimum generation time | **1.61 s** |
| Maximum generation time | **4.79 s** |

## Application interaction examples

| Workflow | Observed time |
|---|---:|
| Document Q&A | **6.03 s** |
| Quiz generation | **10.55 s** |

These are representative observations from the working development session, not statistical guarantees.

## Automated validation

The project test suite completed:

```text
4 passed in 2.79s
```

The tests cover:

- document normalization and chunking,
- privacy detection and redaction,
- local retrieval ranking.

## How to reproduce

From the project root with the virtual environment active:

```powershell
python scripts\benchmark.py
python -m pytest
```

## Interpreting the results

The benchmark measures local text-generation time for a fixed short prompt. It does not measure end-to-end document ingestion, OCR, UI rendering or a complete RAG workflow. The 6.03 s and 10.55 s values above are application-level observations from the development session and should be labeled as such in presentations.

If the model, runtime, machine or deployment configuration changes, rerun the benchmark and update this report before publishing a new performance claim.
