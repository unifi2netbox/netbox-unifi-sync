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

- `--dry-run`: configuration/database/controller preflight; no DCIM/IPAM/wireless sync. Run/audit history and session state may still be recorded.
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
- VLANs/prefixes/IP ranges match their enabled sync options
- Client IPs present when `sync_client_ips` is enabled, tagged `unifi-client`,
  and assigned to matching interfaces when MAC data exists in NetBox
- No site mapping misses in logs

## v0.3.26 behavior

Dry-run does not show a proposed-object or cleanup deletion diff. Test staging
before a first full sync. Cleanup queueing requires a sync permission plus
`netbox_unifi_sync.run_cleanup`; it is skipped when controller credentials or
effective site mappings require separate execution groups.

Repeat full sync to check stable identities, serial-suffixed duplicate names,
curated device types and power-port counters. With `sync_prefixes=false`, no
new prefix is created and management IPs use existing parent masks or host masks.
Avoid overlapping jobs across independent processes. See [Upgrade](Upgrade).
