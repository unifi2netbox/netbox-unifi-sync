# Frequently Asked Questions

## General

### Does plugin sync write back to UniFi?

Primarily no. Normal direction is **UniFi -> NetBox**.  
Writeback can happen in DHCP-to-static flow when a device is detected with a DHCP IP inside known DHCP ranges.
`dhcp_writeback_enabled` controls that writeback path. Keep it disabled when the sync must be read-only toward UniFi.

### Which UniFi API mode should I use?

Use `api_key` mode when possible (Integration API v1).  
Use `login` mode only when Integration API is not available.

### Can I use `unifi.ui.com` cloud API keys?

Not as a direct replacement for local Integration API keys.

### Can I use multiple controllers?

Yes. Add multiple enabled controllers in `Plugins -> UniFi Sync -> Controllers`.

### Can I run sync manually from UI?

Yes. Open `Plugins -> UniFi Sync -> Sync Dashboard` and use `Run now`.
The user needs `view` on `netbox_unifi_sync.SyncRun` to open the dashboard and
`add` on `netbox_unifi_sync.SyncRun` to queue a manual sync.

## Data and Mapping

### What if UniFi site names differ from NetBox site names?

Use `Site mappings` in plugin UI. Controller-specific rows override global rows.
Controllers with different effective mappings execute separately, including when
they share credentials. Cleanup is skipped across separate execution groups.

### Are prefixes created automatically?

Yes. Prefix sync is enabled by default (same strategy as VLAN sync).  
If a UniFi subnet is missing in NetBox, a prefix can be created when
`sync_prefixes=true`. With it disabled, no new prefixes are created; primary IPs
reuse an existing parent's mask or use a host mask if none exists. Existing
prefixes are retained.

### Are DHCP scopes visible in NetBox IP Ranges?

Yes. UniFi DHCP pools are synced as NetBox IP Ranges under matching prefixes.

### What happens to device status?

- On create: default status is `planned` (unless overridden)
- On update: status is not force-reset to `planned`

### What happens to offline devices?

If `sync_stale_cleanup` is enabled, stale devices can be marked offline.  
If `cleanup_enabled` is enabled, stale devices can be deleted after `cleanup_grace_days`.

## Security and Credentials

### Where should I place credentials?

Set credentials only in `Plugins -> UniFi Sync -> Controllers`.
Accepted values in controller credential fields:

- `env:VAR_NAME`
- `file:/absolute/path/to/secret`
- direct pasted credential value

Do not store UniFi credentials in `PLUGINS_CONFIG`.

### Is SSL verification enabled by default?

Yes. SSL verification defaults to `true`.

## Operations

### How do I run a dry-run?

- UI: enable dry-run on dashboard action form
- CLI: `python manage.py netbox_unifi_sync_run --dry-run --json`

### How do I run cleanup?

- UI: request cleanup from dashboard action form
- CLI: `python manage.py netbox_unifi_sync_run --cleanup`

### How do I troubleshoot missing data?

1. Test controller connection in `Controllers`.
2. Validate `tenant_name` and `netbox_roles` in `Settings`.
3. Validate `Site mappings`.
4. Inspect latest run details and worker logs.

### Does dry-run show the changes that a full sync would make?

No. It checks configuration, NetBox access and controller authentication/site
access. It does not calculate a device-by-device diff or a cleanup deletion
preview. Run/audit history and controller session state may be recorded.

### What if two devices have the same name?

Hardware is matched using the configured serial strategy. Name collisions use a
stable serial suffix, including on rename. Ambiguous or missing identifiers are
logged and skipped. See [identity settings](configuration.md#vrf-and-serial-strategy).

### Will imported device types be overwritten?

Normal device sync prefers matching library types by normalized part number and
leaves curated specs alone. Cleanup has a separate type-refresh/delete pass; see
[device specs](device-specs.md) and [cleanup](cleanup.md).

### How do I reduce change-log noise?

Set the worker environment option `SYNC_LIVE_READINGS=false` to omit supported
per-poll readings. See [configuration](configuration.md#advanced-live-readings).

### How do I upgrade?

Follow the [v0.3.26 upgrade guide](upgrade.md). Upgrade the same package in web
and worker runtimes, apply pending migrations, and restart both services.
