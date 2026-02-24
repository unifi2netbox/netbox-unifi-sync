# netbox_unifi_sync

`netbox_unifi_sync` is a NetBox 4.2+ plugin that runs UniFi -> NetBox sync jobs inside NetBox workers.

## Features

- Device sync (devices, interfaces, VLANs, prefixes, WLANs, uplink relations, IP assignments)
- DHCP scope sync to NetBox IP Ranges
- UniFi auth via API key or legacy login (username/password + optional MFA)
- Manual and scheduled sync jobs
- Runtime settings stored in plugin models (`Settings`, `Controllers`, `Site mappings`)

## Quick Start

### 1. Install

```bash
pip install netbox-unifi-sync
```

### 2. Enable plugin in NetBox

```python
PLUGINS = ["netbox_unifi_sync"]

PLUGINS_CONFIG = {
    "netbox_unifi_sync": {}
}
```

### 3. Apply migrations

```bash
python manage.py migrate
```

### 4. Configure in UI

Go to `Plugins -> UniFi Sync` and configure:

1. `Settings` (`tenant_name`, `netbox_roles`, defaults)
2. `Controllers` (URL, auth mode, credentials)
3. `Site mappings` (if UniFi/NetBox site names differ)

### 5. Run first sync

- UI: `Plugins -> UniFi Sync -> Sync Dashboard -> Run now`
- CLI:

```bash
python manage.py netbox_unifi_sync_run --dry-run --json
python manage.py netbox_unifi_sync_run --cleanup
```

## Credentials

Use secret references, not plaintext:

- `env:VAR_NAME`
- `file:/absolute/path/to/secret`

## Documentation

- [Server install guide](docs/server-install.md)
- [NetBox plugin mode](docs/netbox-plugin.md)
- [Configuration reference](docs/configuration.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Release and PyPI publish](docs/release.md)
- [netbox-docker setup](deploy/netbox-docker/README.md)

## Security Notes

- SSL verification defaults to `true`
- Secrets are redacted in run history and audit logs
- Timeouts/retries/backoff are configurable

## Maintainer: Release to PyPI

1. Bump version in:
   - `pyproject.toml` (`[project].version`)
   - `netbox_unifi_sync/version.py` (`__version__`)
2. Push to `main` (auto-tag reads version from `pyproject.toml`).
3. Ensure repository secret `PYPI_API_TOKEN` is set.
4. Tag workflow triggers release workflow, which builds and publishes to PyPI.
