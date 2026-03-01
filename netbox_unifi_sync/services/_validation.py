"""Pure-Python validation helpers for sync orchestration.

No Django or NetBox imports — intentionally kept dependency-free so that
this module can be loaded in unit tests without a live Django environment.
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("netbox.plugins.netbox_unifi_sync.orchestrator")


class SyncConfigurationError(ValueError):
    pass


def validate_runtime_config(
    settings,
    runtime_groups: dict[tuple[str, ...], list[dict[str, Any]]],
    cleanup_requested: bool,
) -> bool:
    """Validate sync configuration and return the effective cleanup flag.

    Returns *False* (cleanup disabled) when cleanup was requested but cannot
    run safely, instead of raising an error that would abort the entire sync.

    Raises SyncConfigurationError for hard misconfigurations (missing tenant,
    missing roles) that prevent any sync from running.
    """
    if not settings.tenant_name.strip():
        raise SyncConfigurationError("tenant_name must be configured.")
    if not settings.netbox_roles:
        raise SyncConfigurationError("netbox_roles must be configured.")

    if cleanup_requested and len(runtime_groups) > 1:
        logger.warning(
            "Cleanup skipped this run: %d controller credential groups detected. "
            "Stale cleanup requires a single shared credential set across all controllers "
            "(running cleanup per group risks deleting devices that belong to other groups). "
            "To enable cleanup: use the same credentials for all controllers, or run with "
            "a single controller selected.",
            len(runtime_groups),
        )
        return False

    return cleanup_requested
