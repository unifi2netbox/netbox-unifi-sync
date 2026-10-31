# Server Installation Guide

Install the plugin in the same Python environment as NetBox and every worker.
Current release: [v0.3.26](https://pypi.org/project/netbox-unifi-sync/0.3.26/).
For an existing installation, use the [upgrade guide](upgrade.md).

## Prerequisites

- NetBox 4.2–4.x and its supported Python version (plugin minimum: Python 3.11).
- Access to the NetBox virtual environment or custom container image build.
- Network access from web/worker processes to the configured UniFi controller.
- A configured import tenant name, role mappings and corresponding NetBox sites.
- Compatible package dependencies, including urllib3 2.8.x.

## NetBox in a virtual environment

For the usual `/opt/netbox` layout:

```bash
/opt/netbox/venv/bin/python -m pip install netbox-unifi-sync==0.3.26
/opt/netbox/venv/bin/python -m pip check
```

Enable the plugin in `/opt/netbox/netbox/netbox/configuration.py`:

```python
PLUGINS = ["netbox_unifi_sync"]
PLUGINS_CONFIG = {"netbox_unifi_sync": {}}
```

If other plugins are enabled, retain them in `PLUGINS`. Apply migrations:

```bash
/opt/netbox/venv/bin/python /opt/netbox/netbox/manage.py migrate
/opt/netbox/venv/bin/python /opt/netbox/netbox/manage.py check
```

Restart web and worker services using the names/service manager of your
installation. Check that `Plugins -> UniFi Sync` appears in NetBox.

For editable development installation instead:

```bash
git clone https://github.com/unifi2netbox/netbox-unifi-sync.git
/opt/netbox/venv/bin/python -m pip install -e /path/to/netbox-unifi-sync
```

## netbox-docker

Use the [complete Docker setup](../deploy/netbox-docker/README.md) to build a
custom image or use the supplied development mount. A bare
`local_requirements.txt` is not consumed by the stock image. Both `netbox` and
`netbox-worker` must run an image/environment containing the plugin.

After deployment:

```bash
docker compose exec netbox /opt/netbox/netbox/manage.py migrate
docker compose exec netbox /opt/netbox/netbox/manage.py check
```

## Runtime setup

In `Plugins -> UniFi Sync`:

1. **Settings**: configure `tenant_name`, role mappings and desired sync scope.
   Canonical role keys are `WIRELESS`, `LAN`, `GATEWAY`, `ROUTER`, `UNKNOWN`.
2. **Controllers**: add an enabled controller, local Integration API key or
   login credentials, and TLS verification settings. Use `api_key_ref`,
   `username_ref`, `password_ref`, `mfa_secret_ref` as appropriate.
3. **Site mappings**: add global or controller-specific rows where names differ.
   Controller-specific mappings take precedence.
4. Grant users dashboard/queue permissions; cleanup has its own permission.
   See [plugin mode](netbox-plugin.md#permissions).

UI models are the runtime source of truth. `PLUGINS_CONFIG` is optional bootstrap
input; keep credentials in controller fields using secret references or direct
values, not in version-controlled configuration. See [configuration](configuration.md).

## First run

Test the controller, then run in the NetBox runtime:

```bash
python manage.py netbox_unifi_sync_run --dry-run --json
python manage.py netbox_unifi_sync_run --json
```

Dry-run verifies configuration and connectivity, not proposed object changes.
Run/audit history may still be written. For the first full sync, keep cleanup
and DHCP writeback off unless deliberately required. Inspect expected devices,
types, ports and IPs; prefixes appear only if enabled and subnet data is present.
Repeat the run to check identity stability, then configure the schedule to avoid
overlapping processes. Use [troubleshooting](troubleshooting.md) for failures and
[upgrade](upgrade.md) for updates/rollback.
