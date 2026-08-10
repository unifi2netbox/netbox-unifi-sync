from __future__ import annotations

import re
from typing import Any

from netbox_unifi_sync.services.sync.log_sanitizer import redact_text

_SENSITIVE_DETAIL_KEY = re.compile(
    r"(?:^|_)(?:authorization|api_?key|password|passwd|secret|token|credential)s?$",
    re.IGNORECASE,
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
                if _SENSITIVE_DETAIL_KEY.search(normalized_key)
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
