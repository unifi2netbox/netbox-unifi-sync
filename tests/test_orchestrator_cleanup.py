"""Tests for sync orchestration validation logic.

Imports from netbox_unifi_sync.services._validation — a pure-Python module
with no Django dependency, so no stubs or mocks are required.
"""
import pytest
from unittest.mock import MagicMock

from netbox_unifi_sync.services._validation import (
    SyncConfigurationError,
    validate_runtime_config,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _make_settings(tenant="Default", roles=None):
    s = MagicMock()
    s.tenant_name = tenant
    s.netbox_roles = roles if roles is not None else {"WIRELESS": "Wireless AP"}
    return s


def _groups(n):
    """Return a dict with n distinct credential-group keys."""
    return {(f"sig-{i}",): [{}] for i in range(n)}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
class TestValidateRuntimeConfig:
    def test_raises_when_tenant_empty(self):
        with pytest.raises(SyncConfigurationError, match="tenant_name"):
            validate_runtime_config(_make_settings(tenant="  "), _groups(1), False)

    def test_raises_when_roles_empty(self):
        with pytest.raises(SyncConfigurationError, match="netbox_roles"):
            validate_runtime_config(_make_settings(roles={}), _groups(1), False)

    def test_cleanup_single_group_allowed(self):
        result = validate_runtime_config(_make_settings(), _groups(1), cleanup_requested=True)
        assert result is True

    def test_no_cleanup_single_group(self):
        result = validate_runtime_config(_make_settings(), _groups(1), cleanup_requested=False)
        assert result is False

    def test_cleanup_disabled_gracefully_with_mixed_credentials(self):
        """Mixed credentials must warn and return False — NOT raise."""
        result = validate_runtime_config(_make_settings(), _groups(2), cleanup_requested=True)
        assert result is False

    def test_no_cleanup_with_mixed_credentials_still_ok(self):
        """Sync without cleanup must always succeed regardless of groups."""
        result = validate_runtime_config(_make_settings(), _groups(3), cleanup_requested=False)
        assert result is False

    def test_mixed_credentials_does_not_raise(self):
        """Must never raise SyncConfigurationError for mixed credentials."""
        try:
            validate_runtime_config(_make_settings(), _groups(5), cleanup_requested=True)
        except SyncConfigurationError:
            pytest.fail("validate_runtime_config raised SyncConfigurationError for mixed credentials")
