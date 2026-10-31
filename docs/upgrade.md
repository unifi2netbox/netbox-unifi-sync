# Upgrade to v0.3.26

Version **0.3.26**, released on **2026-10-31**, is available as a
[GitHub Release](https://github.com/unifi2netbox/netbox-unifi-sync/releases/tag/v0.3.26)
and on [PyPI](https://pypi.org/project/netbox-unifi-sync/0.3.26/).
The package supports NetBox 4.2–4.x and Python 3.11+; CI checks Python 3.11 and
3.12. Use the Python version required by your NetBox deployment.

## Before upgrading

1. Record the installed NetBox/plugin versions, current image or package pin,
   settings and controller/site mappings. Back up the NetBox database.
2. Pause automatic sync and allow running jobs to finish. Avoid overlapping
   manual, scheduled and management-command runs in separate worker processes.
3. Test the upgrade against staging. Local tests do not replace validation of
   your NetBox/PostgreSQL, Redis/RQ and UniFi versions.
4. Check dependency compatibility: this release requires patched urllib3 2.8.x.
   Install into the same environments used by the web service and every worker.

## NetBox virtual environment

Using the usual `/opt/netbox` layout:

```bash
/opt/netbox/venv/bin/python -m pip install --upgrade netbox-unifi-sync==0.3.26
/opt/netbox/venv/bin/python -m pip check
/opt/netbox/venv/bin/python /opt/netbox/netbox/manage.py migrate
/opt/netbox/venv/bin/python /opt/netbox/netbox/manage.py check
```

Restart both web and worker services using your deployment's service manager.
Confirm the version in each runtime:

```bash
/opt/netbox/venv/bin/python -c 'from netbox_unifi_sync.version import __version__; print(__version__)'
```

Version 0.3.26 adds no schema migration. Still apply pending migrations from
older versions. Migration `0009_unique_global_site_mapping` rejects duplicate
global mappings instead of deleting them; reconcile the reported rows before
retrying migration if upgrading from before that change.

## netbox-docker

Set the package requirement to `netbox-unifi-sync==0.3.26` in the custom image's
`local_requirements.txt`, replacing an older pin. Build and deploy the same
image for `netbox` and `netbox-worker`; adding the file without a custom image
build does not install the plugin. See the [Docker guide](../deploy/netbox-docker/README.md).

After rebuilding/recreating both services:

```bash
docker compose exec netbox /opt/netbox/venv/bin/python -m pip check
docker compose exec netbox /opt/netbox/netbox/manage.py migrate
docker compose exec netbox /opt/netbox/netbox/manage.py check
docker compose exec netbox /opt/netbox/venv/bin/python -c 'from netbox_unifi_sync.version import __version__; print(__version__)'
docker compose exec netbox-worker /opt/netbox/venv/bin/python -c 'from netbox_unifi_sync.version import __version__; print(__version__)'
```

Editable development mounts use the checkout's version and need restarts of
both services. Keep that development setup separate from an image-based rollout.

## Changed behavior to verify

| Area | v0.3.26 behavior | Staging check |
| --- | --- | --- |
| Prefix toggle (#26) | Disabling `sync_prefixes` covers network-config and inferred subnet creation. Existing parents determine IP masks; otherwise a host mask is used. | Sync an address without a parent, then repeat. Verify no new prefix with the toggle off. |
| Device names (#17) | Different hardware can share a display name. Create/rename collisions use a stable serial suffix; missing/ambiguous identifiers are skipped. | Sync two serials with one display name, rename and repeat; verify identity and device count. |
| Power ports (#16) | Subsequent saves preserve component counters updated by NetBox signals. | Create a device from a type with power ports; inspect actual ports and the tab counter after another save. |
| Library types (#15) | Normal sync prefers normalized SKU/library matches and preserves curated specs. | Check the selected type and device count for model/SKU spelling variants. |
| Controllers | Different effective site mappings run separately even with shared credentials. | Give two controllers different mappings for the same UniFi site name. |
| Cleanup | Cleanup is skipped when multiple execution groups are required. | Inspect requested/effective cleanup and logs; normal sync should continue. |
| Permissions | Job enqueue enforces sync permission; cleanup additionally requires `run_cleanup`. | Verify an authorized user and a user without queue/cleanup permissions. |
| Preflight | Failed NetBox database/model access fails dry-run. | Check configuration and reachability, then inspect run details. |
| Change log | Request context reaches worker threads; snapshots precede changes. | Check representative object creates and updates. |
| Login/clients | Fresh login clears old cookie state; legacy connected-client listing uses `stat/sta`. | Repeat a session-auth run; check clients when client IP sync is enabled. |

`SYNC_LIVE_READINGS=false` can reduce per-poll metadata writes. It is a worker
process environment option, not a Settings field; see [configuration](configuration.md#advanced-live-readings).

## Run after upgrade

```bash
python manage.py netbox_unifi_sync_run --dry-run --json
python manage.py netbox_unifi_sync_run --json
```

Run these in the configured NetBox runtime. Dry-run is a connectivity/configuration
preflight, not an object diff or cleanup preview. It does not synchronize network
objects, but run/audit history and controller session state may be recorded.
Keep cleanup off for the first full run. Review devices, prefixes, types,
component counters and change logs, then repeat to check idempotency before
resuming the schedule.

## Existing data and concurrency limits

The upgrade does not automatically merge duplicate prefixes/device types or
bulk-repair component counters already incorrect from older releases. Inspect
relationships and use supported NetBox repair/reconciliation procedures on
staging before changing existing data.

Prefix creation and runtime-override locks are process-local. They prevent the
covered thread races; they do not provide a global lock across independent RQ
workers or separate management commands. Keep jobs from overlapping across
processes.

Cleanup's grace period covers stale devices only and is not a safe deletion
preview. Read the [cleanup guide](cleanup.md) before enabling it.

## Rollback and verification record

Keep the previous image/package pin and database backup. Pause sync before
rollback, review migrations applied during the upgrade and restore the matching
database snapshot if required. Reverting a package does not undo NetBox object
writes or cleanup deletions. Do not move an existing release tag or reuse PyPI
filenames for changed artifacts.

The [release review](reviews/2026-10-31-release-review.md) records local and
remote validation. The publication follow-up passed in
[run 41222067811](https://github.com/unifi2netbox/netbox-unifi-sync/actions/runs/41222067811),
and installation of the published package was verified. Live integration checks
remain deployment-specific; use the [QA checklist](qa-checklist.md).
