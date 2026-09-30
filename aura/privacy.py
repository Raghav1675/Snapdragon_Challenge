from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class Finding:
    kind: str
    value: str
    start: int
    end: int
    severity: str
    masked: str


PATTERNS = [
    ("email", re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I), "medium"),
    ("phone", re.compile(r"(?<!\d)(?:\+?91[- .]?)?[6-9]\d{9}(?!\d)"), "medium"),
    ("aadhaar_like", re.compile(r"(?<!\d)(?:\d{4}[ -]?){2}\d{4}(?!\d)"), "high"),
    ("pan_like", re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b", re.I), "high"),
    ("ipv4", re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"), "medium"),
    ("url", re.compile(r"\bhttps?://[^\s<>]+", re.I), "low"),
    ("credit_card_like", re.compile(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)"), "high"),
]


def _mask(kind: str, value: str) -> str:
    if kind == "email":
        user, domain = value.split("@", 1)
        return (user[:1] + "***@" + domain) if user else "***@" + domain
    if kind == "url":
        return "[REDACTED_URL]"
    digits = re.sub(r"\D", "", value)
    if len(digits) <= 4:
        return "*" * len(digits)
    return "*" * (len(digits) - 4) + digits[-4:]


def scan_text(text: str) -> list[Finding]:
    findings: list[Finding] = []
    seen: set[tuple[int, int, str]] = set()
    for kind, pattern, severity in PATTERNS:
        for match in pattern.finditer(text):
            value = match.group(0)
            if kind == "ipv4":
                parts = value.split(".")
                if any(int(p) > 255 for p in parts):
                    continue
            key = (match.start(), match.end(), kind)
            if key in seen:
                continue
            seen.add(key)
            findings.append(Finding(kind, value, match.start(), match.end(), severity, _mask(kind, value)))
    return sorted(findings, key=lambda x: x.start)


def redact_text(text: str, findings: list[Finding] | None = None) -> str:
    findings = findings if findings is not None else scan_text(text)
    out = text
    for f in sorted(findings, key=lambda x: x.start, reverse=True):
        out = out[: f.start] + f"[{f.kind.upper()} REDACTED]" + out[f.end :]
    return out


def severity_score(findings: list[Finding]) -> int:
    weights = {"low": 1, "medium": 3, "high": 6}
    return min(100, sum(weights.get(f.severity, 1) for f in findings))
