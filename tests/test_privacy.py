from aura.privacy import redact_text, scan_text, severity_score


def test_privacy_scan_and_redaction():
    text = "Email raghav@example.com, phone 9876543210, PAN ABCDE1234F."
    findings = scan_text(text)
    assert {f.kind for f in findings} >= {"email", "phone", "pan_like"}
    assert severity_score(findings) > 0
    redacted = redact_text(text, findings)
    assert "raghav@example.com" not in redacted
    assert "9876543210" not in redacted
    assert "ABCDE1234F" not in redacted
