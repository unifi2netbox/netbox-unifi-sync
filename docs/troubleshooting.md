# Troubleshooting

## Quick Triage

1. Check `Plugins -> UniFi Sync -> Runs` for the latest run status/error.
2. Check worker logs:
   - Docker: `docker compose logs -f netbox-worker`
3. Validate plugin setup:
   - `Settings` has `tenant_name` and `netbox_roles`
   - At least one enabled controller has valid auth config
   - Site mappings exist where names differ

## Common Issues

### `HTTPConnectionPool(host='netbox', port=8080)` error

This error indicates an outdated plugin version (0.1.3 or earlier) that used a hardcoded Docker-only fallback URL. It does not work on standard server installs.

Upgrade to fix:

```bash
pip install --upgrade netbox-unifi-sync
python manage.py migrate
# restart netbox + netbox-worker
```

### `could not be found` for `http://localhost/api/...`

This error only appeared in plugin versions 0.1.x which used internal HTTP self-calls to the NetBox REST API. Since **v0.2.0** the plugin accesses NetBox directly via the Django ORM — no HTTP self-call is made, so there is no URL to configure.

Upgrade to the latest version to resolve this:

```bash
pip install --upgrade netbox-unifi-sync
python manage.py migrate
# restart netbox + netbox-worker
```

### Connection timeout / connection refused

Check:

- controller URL in `Controllers`
- network reachability from NetBox worker container/host
- TLS/SSL settings (`verify_ssl`)
- `request_timeout` value

### Authentication failed (`401`/`403`)

For `api_key` mode:

- verify `api_key_ref` in the controller row contains a valid local UniFi Integration API key
- verify header (`api_key_header`)
- do not place UniFi credentials in `PLUGINS_CONFIG`

For `login` mode:

- verify `username_ref` and `password_ref`
- verify optional `mfa_secret_ref` when required
- UniFi OS consoles such as UDM Pro are detected automatically: the plugin tries
  `/api/auth/login` with the UniFi OS payload first and uses the
  `/proxy/network` API prefix after authentication
- standalone/legacy controllers fall back to `/api/login`; no separate `udm`
  authentication mode is required

### Plugin page errors / namespace errors

Check:

- plugin enabled in NetBox config:
  - `PLUGINS = ["netbox_unifi_sync"]`
- plugin package installed in both `netbox` and `netbox-worker`
- migrations applied

Useful checks:

```bash
python manage.py showmigrations netbox_unifi_sync
python manage.py check
```

### `Missing permission` on the sync dashboard

The dashboard requires `view` permission on `netbox_unifi_sync.SyncRun`.
Queueing a manual sync requires `add` permission on `netbox_unifi_sync.SyncRun`.

The plugin still accepts the legacy custom permission
`netbox_unifi_sync.run_sync`, but normal NetBox object permissions should use
`netbox_unifi_sync.add_syncrun` for manual queueing.

### `Missing permission` when testing a controller

Testing controller connectivity requires `change` permission on
`netbox_unifi_sync.UnifiController`. The legacy custom permission
`netbox_unifi_sync.test_controller` is still accepted for compatibility.

### No devices created

Check in order:

1. Controller test connection passes
2. `tenant_name` + `netbox_roles` are configured
3. Site mappings are correct
4. Run detail does not contain skipped site mapping warnings

### WLAN has no VLAN or radio interfaces

- confirm `sync_wlans`, `sync_vlans`, `sync_interfaces`, and
  `sync_radio_interfaces` are enabled
- confirm the UniFi WLAN has an explicit VLAN network and broadcasting access
  points; WLAN-to-interface linkage requires the Integration API's
  `broadcastingDeviceIds` data
- WLAN relationships are synchronized after device radio interfaces, so the
  first full sync can populate both the WLAN and its interface assignments

### Prefix exists but DHCP range missing

Check:

- DHCP is enabled on UniFi network
- `dhcp_auto_discover` enabled
- `sync_dhcp_ranges` enabled in plugin settings

### Expected prefixes not created

Check:

- `sync_prefixes` enabled in plugin settings
- network has valid subnet/CIDR in UniFi data
- run detail for per-site errors

### Worker not processing jobs

Check:

- `netbox-worker` container/service is running
- RQ queues active (`high`, `default`, `low`)
- no startup install failure for plugin package

## Debug Commands

```bash
# Dry-run from NetBox runtime
python manage.py netbox_unifi_sync_run --dry-run --json

# Cleanup run
python manage.py netbox_unifi_sync_run --cleanup

# Migration state
python manage.py showmigrations netbox_unifi_sync
```

## When opening an issue

Include:

- NetBox version
- plugin version
- deployment mode (venv or netbox-docker)
- relevant run error from `Runs` detail
- worker log excerpt

Do not include credentials, tokens, cookies, or private secrets.

### Dependabot alerts remain after a dependency update

Check both the version requirement on `main` and the dependency graph's recorded
version. The native dependency job previously submitted `pkg:pypi/urllib3`
without a version, even after the compatible requirement excluded older
releases. The scanned `requirements.txt` now pins `urllib3==2.8.0`; the published
package's `pyproject.toml` dependency still permits compatible patched 2.8.x
releases. Version 2.8.0 fixes GHSA-vxq7-64xx-v4gw and GHSA-gh4c-6fx4-qh6g.

After merging a manifest change, inspect the dependency update job/snapshot and
the alert status. A clean `pip-audit` verifies the dependencies resolved for that
scan; it does not prove that GitHub has closed an alert. Do not dismiss an alert
as a substitute for confirming the recorded dependency and fix.

## v0.3.26 Sync and Upgrade Checks

### Prefixes appear with prefix sync disabled

Upgrade web and worker runtimes to 0.3.26 and restart both. The prefix toggle now
covers inferred device subnets as well as network-config sync. It does not
remove old duplicates; inspect their VRF, scope, VLAN and relationships before
reconciling existing data. With the toggle off, primary IPs use an existing
parent mask or a host mask. Avoid overlapping independent worker processes.

### Duplicate device names or ambiguous serial warnings

The same display name can belong to different hardware. Version 0.3.26 handles
create/rename conflicts with a serial suffix. Inspect the configured
`serial_mode`, incoming identifier and mapped site when a device is skipped.
Missing or multiple existing matches are skipped with a warning; do not merge
devices merely because their names are equal.

### Power ports exist but the device tab shows zero

Version 0.3.26 prevents later ORM saves from overwriting signal-updated counts
for newly created components. It does not bulk-repair old cached counters.
Compare actual power ports with the device-type templates and follow your
NetBox version's supported counter-repair procedure on staging first. Avoid
creating placeholder ports as a permanent workaround.

### Imported device type is not reused

Check manufacturer identity (`ubiquiti`, or legacy `ubiquity`), reported model,
part number and library slug. Normal sync prefers normalized SKU matches and
preserves curated specs. Existing duplicate types are not automatically merged.
See [device specs](device-specs.md) before moving devices between types.

### Repeated login fails after a previously successful run

Version 0.3.26 clears old session cookies/CSRF state before authenticating again.
Confirm every worker has the upgraded package, then inspect the sanitized login
error. Docker-container startup lines alone do not identify an authentication
or PyPI failure; find the first error response later in the log.

### Dry-run fails NetBox preflight

Preflight now checks database access as well as model availability. Verify the
plugin and pending migrations in the same runtime as the worker. Dry-run is not
an object-change preview; run/audit history may still be written.

### Cleanup requested but skipped

Different controller credentials or effective site mappings require separate
executions. Cleanup is disabled across those groups for safety; normal sync
continues. See [cleanup](cleanup.md#authorization-execution-groups-and-limits).

### PyPI rejects the attestation Build Config URI

The expected Trusted Publisher workflow is `publish-python-package.yml` with
environment `pypi`. Calling publication as a reusable workflow can give its
attestation the caller's `release.yml` identity. Current automation runs
publication as a standalone workflow and retains OIDC and attestations. Retry
**Publish Python Package** on `main` with the already published release tag;
see [release recovery](release.md#recovering-a-failed-publication).

### Release is visible but pip cannot find the new version

GitHub Release creation and PyPI upload are separate steps. Check the standalone
publication run and the exact version page on PyPI before upgrading. For
v0.3.26, publication succeeded in
[run 41222067811](https://github.com/unifi2netbox/netbox-unifi-sync/actions/runs/41222067811).
See [upgrade](upgrade.md) for install and restart commands.
