# NetBox Plugin Mode

This project ships as a NetBox plugin package named `netbox_unifi_sync`.

## Install

From your NetBox Python environment:

```bash
pip install netbox-unifi-sync
```

For development (editable):

```bash
pip install -e /path/to/netbox-unifi-sync
```

## NetBox configuration

In `configuration.py`:

```python
PLUGINS = ["netbox_unifi_sync"]

PLUGINS_CONFIG = {
    "netbox_unifi_sync": {}
}
```

Runtime configuration is managed in NetBox UI (`Plugins -> UniFi Sync`).

## Run sync

- UI: `Plugins -> UniFi Sync -> Sync Dashboard -> Run now`
- CLI:

```bash
python manage.py netbox_unifi_sync_run --dry-run --json
python manage.py netbox_unifi_sync_run --json
python manage.py netbox_unifi_sync_run --cleanup
```

CLI flags:
- `--dry-run`: run preflight only (no NetBox writes).
- `--cleanup`: request cleanup phase in the same run.
- `--json`: output structured JSON result (default output is one-line summary).

## Scheduler behavior

- The plugin registers a NetBox system job (`UniFi Sync Scheduler`) that runs every 60 seconds.
- A real sync is triggered only when:
  - `enabled = true`
  - `schedule_enabled = true`
  - time since last automatic sync >= `sync_interval_minutes`
- Scheduled runs use `dry_run_default` and `cleanup_enabled` from Settings.

## JSON API endpoints

Mounted under `/plugins/unifi-sync/api/`:

- `GET /plugins/unifi-sync/api/status/`
  - Returns plugin status and latest run summary.
  - Permission: `netbox_unifi_sync.view_syncrun`
- `POST /plugins/unifi-sync/api/controllers/<pk>/test/`
  - Tests one controller and returns JSON status/details.
  - Permission: `netbox_unifi_sync.test_controller`

## Permissions

- `netbox_unifi_sync.run_sync`
- `netbox_unifi_sync.run_cleanup`
- `netbox_unifi_sync.test_controller`
