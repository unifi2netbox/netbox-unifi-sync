import os

from netbox_unifi_sync.configuration import (
    get_plugin_settings,
    normalize_plugin_settings,
    plugin_settings_to_env,
    resolve_secret_value,
    validate_plugin_settings,
)


def test_resolve_secret_from_env(monkeypatch):
    monkeypatch.setenv("UNIFI_TEST_KEY", "secret-value")
    assert resolve_secret_value("env:UNIFI_TEST_KEY") == "secret-value"


def test_plugin_settings_to_env_maps_core_values(monkeypatch):
    monkeypatch.setenv("NB_TEST_TOKEN", "nb-token")
    settings = {
        "unifi_url": "https://unifi.example.com/integration/v1",
        "auth_mode": "api_key",
        "api_key": "abc123",
        "netbox_url": "https://netbox.example.com",
        "netbox_token": "env:NB_TEST_TOKEN",
        "netbox_import_tenant": "Example Tenant",
        "netbox_roles": {"WIRELESS": "Wireless AP"},
        "unifi_site_mappings": {"Default": "HQ"},
        "sync_devices": False,
        "sync_interfaces": True,
        "sync_radio_interfaces": False,
        "sync_gateway_interfaces": False,
        "sync_primary_ips": False,
        "sync_device_status": True,
        "sync_device_custom_fields": False,
        "dhcp_writeback_enabled": True,
    }

    env = plugin_settings_to_env(settings)
    assert env["UNIFI_URLS"] == '["https://unifi.example.com/integration/v1"]'
    assert env["UNIFI_AUTH_MODE"] == "api_key"
    assert env["UNIFI_API_KEY"] == "abc123"
    assert env["NETBOX_URL"] == "https://netbox.example.com"
    assert env["NETBOX_TOKEN"] == "nb-token"
    assert env["NETBOX_ROLES"] == '{"WIRELESS": "Wireless AP"}'
    assert env["UNIFI_SITE_MAPPINGS"] == '{"Default": "HQ"}'
    assert env["SYNC_DEVICES"] == "false"
    assert env["SYNC_INTERVAL"] == "0"
    assert env["SYNC_INTERFACES"] == "true"
    assert env["SYNC_RADIO_INTERFACES"] == "false"
    assert env["SYNC_GATEWAY_INTERFACES"] == "false"
    assert env["SYNC_PRIMARY_IPS"] == "false"
    assert env["SYNC_DEVICE_STATUS"] == "true"
    assert env["SYNC_DEVICE_CUSTOM_FIELDS"] == "false"
    assert env["DHCP_WRITEBACK_ENABLED"] == "true"
    assert "UNIFI_USERNAME" not in env
    assert "UNIFI_PASSWORD" not in env


def test_validate_plugin_settings_reports_missing_values():
    errors = validate_plugin_settings({})
    assert any("unifi_url" in msg for msg in errors)
    assert any("netbox_roles" in msg for msg in errors)


def test_validate_plugin_settings_login_mode_requires_user_password():
    errors = validate_plugin_settings(
        {
            "unifi_url": "https://unifi.local",
            "auth_mode": "login",
            "netbox_url": "https://netbox.local",
            "netbox_token": "token",
            "netbox_import_tenant": "Tenant",
            "netbox_roles": {"WIRELESS": "Wireless AP"},
        }
    )
    assert any("auth_mode=login" in msg for msg in errors)


def test_validate_plugin_settings_api_key_mode_requires_api_key():
    errors = validate_plugin_settings(
        {
            "unifi_url": "https://unifi.local",
            "auth_mode": "api_key",
            "netbox_url": "https://netbox.local",
            "netbox_token": "token",
            "netbox_import_tenant": "Tenant",
            "netbox_roles": {"WIRELESS": "Wireless AP"},
        }
    )
    assert any("auth_mode=api_key" in msg for msg in errors)


def test_validate_plugin_settings_allows_missing_netbox_url_and_token():
    errors = validate_plugin_settings(
        {
            "unifi_url": "https://unifi.local",
            "auth_mode": "api_key",
            "api_key": "abc123",
            "netbox_import_tenant": "Tenant",
            "netbox_roles": {"WIRELESS": "Wireless AP"},
        }
    )
    assert not any("netbox_url" in msg for msg in errors)
    assert not any("netbox_token" in msg for msg in errors)


def test_plugin_settings_to_env_login_mode_ignores_api_key():
    settings = {
        "unifi_url": "https://unifi.local",
        "auth_mode": "login",
        "username": "admin",
        "password": "secret",
        "api_key": "should-not-be-exported",
        "netbox_url": "https://netbox.local",
        "netbox_token": "token",
        "netbox_import_tenant": "Tenant",
        "netbox_roles": {"WIRELESS": "Wireless AP"},
    }
    env = plugin_settings_to_env(settings)
    assert env["UNIFI_AUTH_MODE"] == "login"
    assert env["UNIFI_USERNAME"] == "admin"
    assert env["UNIFI_PASSWORD"] == "secret"
    assert "UNIFI_API_KEY" not in env


def test_get_plugin_settings_alias_overrides_for_verify_ssl_and_dry_run():
    merged = get_plugin_settings(
        {
            "verify_ssl": False,
            "dry_run": True,
            "default_site": "HQ",
        }
    )
    assert merged["verify_ssl"] is False
    assert merged["unifi_verify_ssl"] is False
    assert merged["dry_run"] is True
    assert merged["dry_run_default"] is True
    assert merged["default_site"] == "HQ"
    assert merged["default_site_name"] == "HQ"


def test_normalize_plugin_settings_can_apply_defaults_without_plugins_config_merge():
    normalized = normalize_plugin_settings(
        {
            "unifi_url": "https://unifi.local",
            "auth_mode": "api_key",
            "api_key": "abc123",
        },
        include_defaults=True,
    )
    assert normalized["unifi_url"] == "https://unifi.local"
    assert normalized["unifi_api_key"] == "abc123"
    assert normalized["verify_ssl"] is True
    assert normalized["dry_run"] is False
