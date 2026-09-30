from __future__ import annotations

import re
from collections import Counter

from .config import settings
from .llm import OllamaClient
from .retrieval import Hit, LocalRetriever


def _context(hits: list[Hit]) -> str:
    blocks = []
    for hit in hits:
        blocks.append(f"[Source: {hit.source}; relevance={hit.score:.2f}]\n{hit.text}")
    return "\n\n".join(blocks)[: settings.max_context_chars]


def _keywords(text: str, count: int = 10) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z0-9'-]{3,}", text.lower())
    stop = {"this", "that", "with", "from", "have", "which", "their", "there", "about", "using", "into", "will", "your", "they", "been", "were", "what", "when", "where", "then", "than", "these", "those"}
    freqs = Counter(w for w in words if w not in stop)
    return [w for w, _ in freqs.most_common(count)]


def extractive_summary(text: str, limit: int = 6) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    if len(sentences) <= limit:
        return "\n\n".join(sentences)
    keys = set(_keywords(text, 16))
    scored = []
    for i, s in enumerate(sentences):
        score = sum(1 for w in re.findall(r"[A-Za-z][A-Za-z0-9'-]+", s.lower()) if w in keys)
        score += 0.4 if i == 0 else 0
        scored.append((score, i, s))
    selected = sorted(scored, reverse=True)[:limit]
    selected.sort(key=lambda x: x[1])
    return "\n\n".join(s for _, _, s in selected)


def fallback_answer(question: str, hits: list[Hit]) -> str:
    if not hits:
        return "I could not find a relevant passage in the active document. Try a more specific question."
    best = hits[0].text
    summary = extractive_summary(best, 3)
    return f"Based on the most relevant passage:\n\n{summary}"


def answer_question(question: str, hits: list[Hit], client: OllamaClient, level: str, language: str, style: str):
    context = _context(hits)
    system = (
        "You are AURA, a local-first document understanding assistant. "
        "Answer only from the supplied source context when making document claims. "
        "If the context is insufficient, say so. Do not invent page numbers or facts. "
        f"Audience level: {level}. Output language: {language}. Style: {style}."
    )
    prompt = (
        "Answer the user's question using the context below. Keep the response useful and structured. "
        "End with a 'Sources' section listing the source names exactly as supplied.\n\n"
        f"QUESTION:\n{question}\n\nCONTEXT:\n{context}"
    )
    result = client.generate(prompt, system=system)
    if result.ok:
        return result
    class R:
        pass
    fallback = R()
    fallback.text = fallback_answer(question, hits)
    fallback.elapsed = result.elapsed
    fallback.ok = False
    fallback.error = result.error
    return fallback


def explain_document(text: str, client: OllamaClient, level: str, language: str, style: str):
    context = text[: settings.max_context_chars]
    system = (
        "You are AURA, a careful explanation assistant. Preserve the meaning of the source. "
        f"Target audience: {level}. Language: {language}. Style: {style}. "
        "Avoid unsupported claims and clearly separate examples from source facts."
    )
    prompt = f"Explain the following source material. Start with a 2-3 sentence overview, then key ideas, then one practical example if appropriate.\n\nSOURCE:\n{context}"
    result = client.generate(prompt, system=system)
    if result.ok:
        return result
    class R:
        pass
    fallback = R()
    fallback.text = extractive_summary(text, 7)
    fallback.elapsed = result.elapsed
    fallback.ok = False
    fallback.error = result.error
    return fallback


def make_quiz(text: str, client: OllamaClient, level: str, language: str, count: int, difficulty: str):
    context = text[: settings.max_context_chars]
    system = (
        "You create factual study questions from supplied material. "
        f"Audience: {level}. Language: {language}. Difficulty: {difficulty}."
    )
    prompt = (
        f"Create exactly {count} questions from the source. Use a mix of recall and understanding. "
        "For every question, provide the answer immediately underneath it. Do not use facts absent from the source.\n\nSOURCE:\n"
        + context
    )
    return client.generate(prompt, system=system, temperature=0.35)
