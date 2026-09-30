from __future__ import annotations

import time

from .llm import OllamaClient


def run_benchmark(client: OllamaClient, runs: int = 3) -> dict:
    samples = []
    for i in range(runs):
        prompt = "In two sentences, explain why keeping sensitive information on-device can reduce data exposure."
        result = client.generate(prompt, temperature=0.0)
        samples.append({"run": i + 1, "seconds": result.elapsed, "ok": result.ok, "error": result.error})
        if not result.ok:
            break
    successful = [x["seconds"] for x in samples if x["ok"]]
    return {
        "model": client.model,
        "runs": samples,
        "average_seconds": sum(successful) / len(successful) if successful else None,
        "min_seconds": min(successful) if successful else None,
        "max_seconds": max(successful) if successful else None,
    }
