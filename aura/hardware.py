from __future__ import annotations

import platform
import subprocess

import psutil


def _powershell(command: str) -> str:
    try:
        result = subprocess.run(["powershell", "-NoProfile", "-Command", command], capture_output=True, text=True, timeout=5)
        return result.stdout.strip()
    except Exception:
        return ""


def get_hardware_info() -> dict[str, str]:
    cpu = platform.processor() or platform.uname().processor or "Unknown"
    system = f"{platform.system()} {platform.release()}"
    memory_gb = f"{psutil.virtual_memory().total / (1024**3):.1f} GB"
    model = _powershell("(Get-CimInstance Win32_ComputerSystem).Model") if platform.system() == "Windows" else ""
    vendor = _powershell("(Get-CimInstance Win32_ComputerSystemProduct).Vendor") if platform.system() == "Windows" else ""
    return {"CPU": cpu, "System": system, "Memory": memory_gb, "Device": model or "Unknown", "Vendor": vendor or "Unknown"}
