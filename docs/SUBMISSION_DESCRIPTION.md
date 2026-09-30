# Competition Submission Description

## Project title

**AURA — Adaptive Understanding & Retrieval Assistant**

## Final short description

AURA is a local-first AI assistant that turns documents, images and notes into grounded answers, adaptive explanations, quizzes and privacy-safe outputs. It combines local extraction, retrieval and sensitive-data scanning with on-device language generation so the same information can be adapted to different knowledge levels, languages and response styles without requiring a cloud AI API for the core workflow. The application is designed for deployment on Snapdragon-powered HP PCs.

## Problem

People often have access to information but cannot easily understand it because of language barriers, technical jargon, educational level or information overload. Sensitive documents also create a privacy challenge when they are routinely uploaded to hosted AI services.

## Solution

AURA provides one local workflow for:

- understanding documents,
- asking grounded questions,
- adapting explanations to the user,
- generating study questions,
- scanning for common sensitive information,
- exporting redacted content.

## What is technically implemented

- PDF, DOCX, TXT, Markdown, CSV and image ingestion
- OCR support when Tesseract is installed
- local TF-IDF retrieval
- Ollama-based local language-model inference
- adaptive audience/language/style prompting
- privacy-pattern detection and severity scoring
- text and searchable-PDF redaction
- benchmark and runtime inspection
- automated tests

## Demonstrated development results

The working development build records:

- 3-run local generation benchmark average: **2.79 s**
- minimum: **1.61 s**
- maximum: **4.79 s**
- example document Q&A: **6.03 s**
- example quiz generation: **10.55 s**
- automated tests: **4/4 passed**

These are measured development results and are not presented as universal performance guarantees.

## Snapdragon deployment story

The application is structured so the local model runtime can be optimized for the target Snapdragon environment without rewriting the ingestion, retrieval, privacy or user-interface layers. Qualcomm AI Hub/QNN-compatible inference can therefore be integrated at the model boundary for the final target deployment and benchmarked on the actual device.

## Intellectual-property hygiene

The repository should contain no private credentials, confidential client information, trade secrets or real personal-identification data. Demonstration data should be synthetic.
