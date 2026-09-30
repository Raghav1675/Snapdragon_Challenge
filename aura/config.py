from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    ollama_url: str = os.getenv("AURA_OLLAMA_URL", "http://127.0.0.1:11434")
    ollama_model: str = os.getenv("AURA_OLLAMA_MODEL", "gemma3:1b")
    max_context_chars: int = int(os.getenv("AURA_MAX_CONTEXT_CHARS", "12000"))
    top_k: int = int(os.getenv("AURA_TOP_K", "5"))


settings = Settings()
