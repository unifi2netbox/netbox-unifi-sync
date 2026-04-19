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

## Sync shows `1 controller, 1 site, 0 devices`

Check in order:

1. Controller test connection passes.
2. `tenant_name` + `netbox_roles` are configured.
3. Site mappings are correct.
4. Run detail does not contain skipped site mapping warnings.
5. Worker logs show site device fetch count (`Found N devices for site ...`).
   - If `N=0`, UniFi returned no devices for that site.
6. Verify UniFi credentials scope:
   - `api_key` mode must have read access to devices for that site.
   - Use a local controller Integration API key (`unifi.ui.com` cloud tokens are not a drop-in replacement).
   - If uncertain, test with a known full-access local key or temporary `login` mode.
7. Confirm the site has adopted/managed UniFi devices (not only client endpoints).

Dry-run check:

```bash
python manage.py netbox_unifi_sync_run --dry-run --json
```

If dry-run still reports `devices: 0`, collect run detail + worker logs before opening an issue.

## Connection error to `netbox:8080` or `http://localhost`

This only occurs with plugin version 0.1.x which used HTTP self-calls to NetBox. Since v0.2.0 the plugin uses the Django ORM directly — no internal HTTP call is needed. Upgrade to the latest version:

```bash
pip install --upgrade netbox-unifi-sync
python manage.py migrate
# restart netbox + netbox-worker
```

## PyPI publish fails with trusted publisher

Check exact publisher tuple in PyPI:

- owner/repo/workflow/environment must match GitHub claims exactly.

## PyPI publish fails with filename reuse

Bump version and publish new artifacts.

Reference: [docs/troubleshooting.md](https://github.com/unifi2netbox/netbox-unifi-sync/blob/main/docs/troubleshooting.md)
