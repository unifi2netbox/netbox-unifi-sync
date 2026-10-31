# Configuration

Runtime configuration is managed in the NetBox UI:

- `Plugins -> UniFi Sync -> Settings`
- `Plugins -> UniFi Sync -> Controllers`
- `Plugins -> UniFi Sync -> Site mappings`

## Minimum required

1. Create global settings with:
   - `tenant_name`
   - `netbox_roles`
2. Add at least one enabled controller.
3. Add site mappings where UniFi site name differs from NetBox site name.

## Credentials

Set credentials in `Controllers` UI fields (`api_key_ref`, `username_ref`, `password_ref`, `mfa_secret_ref`).
Do not store credentials in `PLUGINS_CONFIG`.

Supported formats for credential fields:

- `env:VAR_NAME` — read from environment variable
- `file:/absolute/path/to/secret` — read from file
- plain value — pasted directly

## Sync controls

Settings lets you choose which UniFi domains are synced:

- devices, interfaces, AP radios, gateway interfaces, primary IPs
- device status and UniFi custom metadata
- VLANs, prefixes, WLANs, cables, DHCP ranges
- client IPs (`sync_client_ips`)
- stale cleanup and scheduled sync

Client IP sync creates NetBox IP addresses tagged `unifi-client`, writes a
description containing the client MAC/name/timestamps when UniFi reports them,
and assigns the IP to a matching DCIM or VM interface by MAC address.

## Change Log

NetBox Change Log is available for Settings, Controllers, and Site mappings.
Sync runs and audit events are runtime history and are viewed from the plugin
dashboard/run detail pages.

## Optional bootstrap in PLUGINS_CONFIG

You can pre-seed defaults via `PLUGINS_CONFIG["netbox_unifi_sync"]`, but UI models are the authoritative runtime state.

Reference: [docs/configuration.md](https://github.com/unifi2netbox/netbox-unifi-sync/blob/main/docs/configuration.md)

## Prefixes, identity and controller isolation

With `sync_prefixes=false`, normal sync creates neither configured nor inferred
prefixes. Existing prefixes are retained; primary IPs use a parent mask or a host
mask when none exists. DHCP-range sync has its own toggle.

Controller-specific site mappings override global mappings. Controllers with
different effective mappings execute separately even when credentials match;
cleanup is skipped across separate execution groups.

Devices match by site and resolved serial. Name collisions use a stable serial
suffix; missing/ambiguous identifiers are logged and skipped. Canonical role
keys are `WIRELESS`, `LAN`, `GATEWAY`, `ROUTER`, `UNKNOWN` and take precedence over
legacy aliases.

## Live readings and process limits

`SYNC_LIVE_READINGS=false` in the worker environment omits supported per-poll
readings such as uptime, PoE draw, utilization and client signal/timestamps. It
has no Settings UI field. Restart workers after changing their environment.
Runtime/prefix locks are process-local; avoid overlapping independent jobs.

See [Upgrade](Upgrade) and the
[full configuration reference](https://github.com/unifi2netbox/netbox-unifi-sync/blob/main/docs/configuration.md).
