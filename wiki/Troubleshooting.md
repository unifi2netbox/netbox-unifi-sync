# Troubleshooting

## Plugin not visible in menu

Check:

- `PLUGINS = ["netbox_unifi_sync"]`
- Migrations applied:

```bash
python manage.py showmigrations netbox_unifi_sync
```

## Sync runs but devices are skipped

Most common cause: missing site mapping.

Validate UniFi site names vs NetBox site names and add mapping rows.

## Dry-run fails with NetBox API URL

In containerized setups, run sync from worker context and ensure internal URL resolves (typically `http://netbox:8080`).

## PyPI publish fails with trusted publisher

Check exact publisher tuple in PyPI:

- owner/repo/workflow/environment must match GitHub claims exactly.

## PyPI publish fails with filename reuse

Bump version and publish new artifacts.

Reference: [docs/troubleshooting.md](https://github.com/unifi2netbox/netbox-unifi-sync/blob/main/docs/troubleshooting.md)
