from __future__ import annotations

from typing import Any

from netbox_unifi_sync.services.sync.log_sanitizer import redact_text

_SENSITIVE_DETAIL_KEYS = frozenset(
    {
        "authorization",
        "api_key",
        "apikey",
        "access_token",
        "token",
        "password",
        "secret",
        "csrf_token",
        "x_api_key",
    }
)


def redact_audit_details(value: Any) -> Any:
    """Recursively redact strings before persisting structured audit details."""
    if isinstance(value, str):
        return redact_text(value)
    if isinstance(value, dict):
        redacted = {}
        for key, item in value.items():
            text_key = str(key)
            normalized_key = text_key.strip().lower().replace("-", "_")
            redacted[text_key] = (
                "[REDACTED]"
                if normalized_key in _SENSITIVE_DETAIL_KEYS
                else redact_audit_details(item)
            )
        return redacted
    if isinstance(value, (list, tuple)):
        return [redact_audit_details(item) for item in value]
    return value


def record_event(*, action: str, status: str, actor=None, target: str = "", message: str = "", details: dict[str, Any] | None = None):
    from ..models import PluginAuditEvent

    PluginAuditEvent.objects.create(
        action=action,
        status=status,
        actor=actor,
        target=target,
        message=redact_text(str(message or ""))[:255],
        details=redact_audit_details(details or {}),
    )


def sanitize_error(message: str) -> str:
    return redact_text(str(message or ""))
