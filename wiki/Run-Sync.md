# Run Sync

## From NetBox UI

- Open `Plugins -> UniFi Sync -> Sync Dashboard`
- Use **Run now** for manual sync
- Use dry-run first when validating a new controller

Required NetBox object permissions:

- `view` on `netbox_unifi_sync.SyncRun` to open the dashboard
- `add` on `netbox_unifi_sync.SyncRun` to queue a manual sync

The plugin still accepts the legacy custom permission
`netbox_unifi_sync.run_sync`, but the standard NetBox object permission for
manual queueing is `netbox_unifi_sync.add_syncrun`.

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

Flags:

- `--dry-run`: preflight only, no writes.
- `--cleanup`: requests cleanup in same run.
- `--json`: structured JSON output.

## Scheduler

- NetBox system job checks every 60 seconds if auto-sync is due.
- Requires `enabled=true` and `schedule_enabled=true` in Settings.
- Interval is controlled by `sync_interval_minutes`.

## JSON API

Mounted under `/plugins/unifi-sync/api/`:

- `GET /plugins/unifi-sync/api/status/`
- `POST /plugins/unifi-sync/api/controllers/<pk>/test/`

## What to verify after run

- Sync run status = success
- Expected devices created/updated
- VLANs/prefixes/IP ranges present
- Client IPs present when `sync_client_ips` is enabled, tagged `unifi-client`,
  and assigned to matching interfaces when MAC data exists in NetBox
- No site mapping misses in logs
