from netbox_unifi_sync.services.audit import redact_audit_details, sanitize_error


def test_sanitize_error_masks_token_and_password():
    text = "Authorization: Bearer supersecret password=admin123"
    cleaned = sanitize_error(text)
    assert "supersecret" not in cleaned
    assert "admin123" not in cleaned


def test_record_event_redacts_nested_audit_details():
    details = {
        "request": {"Authorization": "Bearer supersecret"},
        "errors": ["password=admin123"],
    }
    stored = redact_audit_details(details)
    assert "supersecret" not in str(stored)
    assert "admin123" not in str(stored)
    assert "[REDACTED]" in str(stored)
