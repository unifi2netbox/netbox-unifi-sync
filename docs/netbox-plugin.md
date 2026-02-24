# NetBox Plugin Mode

This project ships as a NetBox plugin package named `netbox_unifi_sync`.

## Install

From your NetBox Python environment:

```bash
pip install /path/to/unifi2netbox-plugins
```

For development (editable):

```bash
pip install -e /path/to/unifi2netbox-plugins
```

## NetBox configuration

In `configuration.py`:

```python
PLUGINS = ["netbox_unifi_sync"]

PLUGINS_CONFIG = {
    "netbox_unifi_sync": {
        "unifi_url": "https://controller.example.com/proxy/network/integration/v1",
        "auth_mode": "api_key",  # api_key | login
        "api_key": "env:UNIFI_API_KEY",
        "username": "",
        "password": "",
        "verify_ssl": True,
        "default_site": "",
        "dry_run": False,
    }
}
```

Compatibility alias is still supported:

```python
PLUGINS = ["unifi2netbox"]
```

## Run sync

- UI: `Plugins -> UniFi Sync -> Sync Dashboard -> Run now`
- CLI:

```bash
python manage.py netbox_unifi_sync_run --dry-run --json
python manage.py netbox_unifi_sync_run --cleanup
```

## Permissions

- `netbox_unifi_sync.run_sync`
- `netbox_unifi_sync.run_cleanup`
- `netbox_unifi_sync.test_controller`
