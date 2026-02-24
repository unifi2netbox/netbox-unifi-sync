from netbox_unifi_sync.services import sync_service


def test_execute_sync_with_overrides_does_not_load_plugins_config(monkeypatch):
    def _forbid_plugins_config(*args, **kwargs):
        raise AssertionError("get_plugin_settings must not be called when config_overrides is provided")

    monkeypatch.setattr(sync_service, "get_plugin_settings", _forbid_plugins_config)
    monkeypatch.setattr(
        sync_service,
        "run_sync_once",
        lambda clear_state=True: {"controllers": 1, "sites": 2, "devices": 3},
    )
    monkeypatch.setattr(
        sync_service,
        "format_result_summary",
        lambda result, dry_run=False: {**result, "mode": "sync", "dry_run": dry_run},
    )

    result = sync_service.execute_sync(
        dry_run=False,
        config_overrides={
            "unifi_url": "https://unifi.local",
            "auth_mode": "api_key",
            "api_key": "abc123",
            "netbox_import_tenant": "Default",
            "netbox_roles": {"WIRELESS": "Wireless AP"},
            "netbox_url": "http://netbox:8080",
            "netbox_token": "token",
        },
    )

    assert result["mode"] == "sync"
    assert result["dry_run"] is False
    assert result["controllers"] == 1
    assert result["sites"] == 2
    assert result["devices"] == 3
