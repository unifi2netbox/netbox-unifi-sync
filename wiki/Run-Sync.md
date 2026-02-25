# Run Sync

## From NetBox UI

- Open `Plugins -> UniFi Sync -> Sync Dashboard`
- Use **Run now** for manual sync
- Use dry-run first when validating a new controller

## From CLI

Dry-run:

```bash
python manage.py netbox_unifi_sync_run --dry-run --json
```

Full sync:

```bash
python manage.py netbox_unifi_sync_run --json
```

Cleanup run:

```bash
python manage.py netbox_unifi_sync_run --cleanup
```

## What to verify after run

- Sync run status = success
- Expected devices created/updated
- VLANs/prefixes/IP ranges present
- No site mapping misses in logs
