# AURA — Adaptive Understanding & Retrieval Assistant

**Understand any information in the way you learn best.**

AURA is a local-first AI application for turning documents, images and notes into grounded explanations, answers, quizzes and privacy-safe outputs. The application adapts responses to an audience level, language and response style while keeping the core document workflow on the user's machine.

## What AURA does

- **Understand** — ask grounded questions and generate adaptive explanations from uploaded sources.
- **Protect** — detect common sensitive-data patterns locally and create redacted text or searchable-PDF copies.
- **Practice** — generate revision questions from the active source.
- **Work locally** — use a local Ollama model for generative inference; no cloud AI API is included in the default build.
- **Retrieve evidence** — select relevant passages locally before asking the model to respond.
- **Handle common source types** — PDF, DOCX, TXT, Markdown, CSV and images.

## Why the project matters

People often have access to information but struggle to understand it because of language, jargon, educational level or information overload. AURA adapts the presentation of the same source to the person using it rather than forcing the person to adapt to the source.

## Architecture

```text
                     AURA
                       |
          +------------+------------+
          |            |            |
       Document      Image        Voice*
          |            |            |
      extraction      OCR          STT*
          +------------+------------+
                       |
                Privacy engine
                       |
                 Local retrieval
                       |
                  Local LLM
                       |
          +------------+------------+
          |            |            |
        Answer      Explain       Quiz
                       |
             Translate / Redact / Export
```

`*` Speech input is an optional extension point; the base build does not require a cloud speech service.

## Technology

- Python
- Streamlit
- PyMuPDF
- python-docx
- Pillow
- Tesseract OCR (optional)
- scikit-learn TF-IDF retrieval
- Ollama local inference
- psutil for runtime information

## Quick start on Windows

### 1. Create a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Start AURA

```powershell
python -m streamlit run app.py
```

Open the local address printed by Streamlit, normally:

```text
http://localhost:8501
```

## Local generative AI

Install Ollama and then pull the configured development model:

```powershell
ollama pull gemma3:1b
```

AURA uses the local Ollama endpoint:

```text
http://127.0.0.1:11434
```

You can change the model or endpoint with environment variables:

```text
AURA_OLLAMA_URL=http://127.0.0.1:11434
AURA_OLLAMA_MODEL=gemma3:1b
AURA_MAX_CONTEXT_CHARS=12000
AURA_TOP_K=5
```

## Demo workflow

1. Upload a document.
2. Open **Ask** and ask a source-grounded question.
3. Open **Explain** and change the audience level or response style.
4. Open **Privacy** to inspect and redact common sensitive information.
5. Open **Quiz** to create revision questions.
6. Open **System** to inspect the runtime and benchmark the local model.

## Recorded development measurements

The current build has a recorded local development baseline from 30 September 2026:

| Measurement | Result |
|---|---:|
| 3-run benchmark average | **2.79 s** |
| 3-run benchmark minimum | **1.61 s** |
| 3-run benchmark maximum | **4.79 s** |
| Example document Q&A | **6.03 s** |
| Example quiz generation | **10.55 s** |
| Automated tests | **4/4 passed** |

These are measurements from the development run, not universal performance guarantees. Re-run the benchmark after changing the model, runtime or deployment environment.

## Privacy model

The default project contains no analytics SDK, no telemetry and no hosted AI API. The application extracts and indexes source material locally. Generative requests are sent to the local Ollama service on the same machine.

A privacy scan is pattern-based and intentionally conservative. A clean scan is not proof that a file contains no sensitive information.

## Repository structure

```text
AURA/
├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── LICENSE
├── aura/
│   ├── assistant.py
│   ├── benchmark.py
│   ├── config.py
│   ├── document.py
│   ├── hardware.py
│   ├── llm.py
│   ├── privacy.py
│   ├── retrieval.py
│   └── utils.py
├── data/
├── docs/
│   ├── ARCHITECTURE.md
│   ├── BENCHMARK.md
│   ├── SNAPDRAGON_DEPLOYMENT.md
│   └── SUBMISSION_DESCRIPTION.md
├── scripts/
│   ├── benchmark.py
│   └── run_windows.ps1
└── tests/
```

## Testing

Run:

```powershell
python -m pytest
```

The current test suite covers document normalization/chunking, privacy scanning/redaction and local retrieval.

## Deployment positioning

AURA's model layer is separated from the application layer so a local inference backend optimized for the target Snapdragon environment can be integrated without changing the document, privacy, retrieval or UI flow. Before making hardware-specific performance claims in a competition submission, run the included benchmark on the actual deployment environment and use the measured results.
