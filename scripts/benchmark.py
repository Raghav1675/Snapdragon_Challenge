from __future__ import annotations

import json

from aura.benchmark import run_benchmark
from aura.hardware import get_hardware_info
from aura.llm import OllamaClient


if __name__ == "__main__":
    client = OllamaClient()
    report = {"timestamp": __import__("datetime").datetime.now().isoformat(), "hardware": get_hardware_info(), "benchmark": run_benchmark(client, 3)}
    print(json.dumps(report, indent=2))
