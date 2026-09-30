from __future__ import annotations

from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class Hit:
    rank: int
    score: float
    text: str
    source: str


class LocalRetriever:
    def __init__(self, chunks: list[tuple[str, str]]):
        self.chunks = chunks
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=15000)
        corpus = [c[0] for c in chunks]
        self.matrix = self.vectorizer.fit_transform(corpus) if corpus else None

    def search(self, query: str, top_k: int = 5) -> list[Hit]:
        if not self.chunks or self.matrix is None or not query.strip():
            return []
        q = self.vectorizer.transform([query])
        scores = cosine_similarity(q, self.matrix).ravel()
        indices = scores.argsort()[::-1][:top_k]
        hits: list[Hit] = []
        for rank, idx in enumerate(indices, 1):
            score = float(scores[idx])
            if score <= 0:
                continue
            text, source = self.chunks[idx]
            hits.append(Hit(rank, score, text, source))
        return hits
