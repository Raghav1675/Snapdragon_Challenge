from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any

import requests

from .config import settings


@dataclass
class LLMResult:
    text: str
    elapsed: float
    ok: bool
    error: str = ""


class OllamaClient:
    def __init__(self, base_url: str | None = None, model: str | None = None):
        self.base_url = (base_url or settings.ollama_url).rstrip("/")
        self.model = model or settings.ollama_model

    def status(self) -> tuple[bool, str]:
        try:
            r = requests.get(f"{self.base_url}/api/tags", timeout=3)
            if not r.ok:
                return False, f"HTTP {r.status_code}"
            data = r.json()
            models = [m.get("name", "") for m in data.get("models", [])]
            if self.model not in models and not any(m.startswith(self.model + ":") for m in models):
                return True, f"Ollama is running; model {self.model!r} is not installed."
            return True, f"Ollama is running with {self.model}."
        except Exception as exc:
            return False, str(exc)

    def generate(self, prompt: str, system: str = "", temperature: float = 0.2) -> LLMResult:
        started = time.perf_counter()
        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature},
        }
        if system:
            payload["system"] = system
        try:
            response = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=180)
            response.raise_for_status()
            data = response.json()
            text = str(data.get("response", "")).strip()
            return LLMResult(text, time.perf_counter() - started, bool(text), "")
        except requests.RequestException as exc:
            return LLMResult("", time.perf_counter() - started, False, str(exc))
        except (ValueError, json.JSONDecodeError) as exc:
            return LLMResult("", time.perf_counter() - started, False, f"Invalid Ollama response: {exc}")
