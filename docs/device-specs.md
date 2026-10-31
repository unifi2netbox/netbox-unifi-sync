# Device Type Specs

Device type enrichment combines two sources at runtime:

1. `UNIFI_MODEL_SPECS` in `netbox_unifi_sync/services/unifi/model_specs.py`
2. The packaged `netbox_unifi_sync/services/data/ubiquiti_device_specs.json`
   community bundle, indexed by model (`by_model`) and part number (`by_part`).

The source checkout also keeps `data/ubiquiti_device_specs.json`. Runtime checks
the packaged location before the checkout copy; refresh both when updating a
release bundle. Model counts change as the bundle is refreshed.

Optional startup refresh (env-controlled) can rebuild the bundle from:
- `netbox-community/devicetype-library` (same upstream data used by Device-Type-Library-Import)
- UniFi Store technical specs (`UNIFI_SPECS_INCLUDE_STORE=true`)

## Bundled Snapshot: 2026-10-31

The checked-in copies contain 201 part-number entries and 499 model-name/alias
entries. They incorporate all 198 Ubiquiti definitions from
[Device Type Library commit f3a04d6](https://github.com/netbox-community/devicetype-library/commit/f3a04d6520b678b920438ad441cfa9b03e5bdaf2).
Seventeen upstream part numbers were added relative to the previous packaged
bundle, including U7-LR, UDR7, UX7, UNVR-G2-Pro and USW-Pro-XG-Aggregation.

The refresh preserves complete current library fields and adds the normalized
`console_ports`/`power_ports` fields consumed by the engine. Existing model
aliases, PoE budgets and three legacy/store-only part entries are retained.
Previously available Store enrichment was preserved, not fetched again in this
snapshot. The source and packaged JSON copies are byte-identical.

Preserving library metadata such as module bays, device bays, images and power
outlets does not add synchronization support for those components. The engine
continues to synchronize only its supported template types listed below.

## Merge Strategy

`_resolve_device_specs(model)`:

1. Load hardcoded spec by model key (if present)
2. Try community lookup by:
   - hardcoded `part_number`
   - model string as fallback part number
   - model lookup in `by_model`
3. Merge with precedence:
   - community fields as base
   - hardcoded fields override

This keeps curated overrides intact while inheriting rich template data from community specs.

## Upstream Refresh Options

### Runtime (automatic)

Set in plugin `Settings` (or bootstrap via `PLUGINS_CONFIG`):

```text
specs_auto_refresh = true
specs_include_store = false
```

This refreshes the in-memory bundle at startup before sync begins.

### Manual bundle refresh (recommended for repository updates)

```bash
python3 tools/refresh_unifi_specs.py
cp data/ubiquiti_device_specs.json netbox_unifi_sync/services/data/ubiquiti_device_specs.json
```

With UniFi Store enrichment disabled:

```bash
python3 tools/refresh_unifi_specs.py --skip-store
cp data/ubiquiti_device_specs.json netbox_unifi_sync/services/data/ubiquiti_device_specs.json
```

## Synced Template Types

`_sync_templates()` in `netbox_unifi_sync/services/sync_engine.py` handles:

- interface templates (`dcim.interface_templates`)
- console port templates (`dcim.console_port_templates`)
- power port templates (`dcim.power_port_templates`)

For plugin-managed types, a differing expected template set can replace existing
templates. Normal device sync skips enrichment for a curated type selected by
its SKU/library identity. The cleanup type-refresh pass is separate and can
refresh matching specs or delete unused types; review it before enabling cleanup.

## Runtime Port Metadata

Device type templates describe what a model can have. Runtime UniFi port data
describes what each live port is currently doing. During interface sync, the
plugin stores native NetBox interface fields when available:

- interface type
- enabled state
- speed
- PoE mode
- primary MAC address

Additional UniFi-only operational details are added to the NetBox interface
description so they are visible without requiring custom fields:

- uplink marker
- UniFi port profile name
- native VLAN
- tagged VLAN list
- current PoE draw
- reported max link speed

## Runtime Client Metadata

When `sync_client_ips` is enabled, UniFi client IP addresses are tagged
`unifi-client`. The IP description starts with a stable
`unifi-client:<MAC>` marker used for cleanup, followed by optional context when
UniFi reports it:

- hostname/display name
- IP address
- connection source fields from either Legacy API or Integration API
- SSID
- AP name
- signal
- connected timestamp
- last seen timestamp

If NetBox has an interface with the same MAC address, the IP is assigned to that
interface. Both physical `dcim.Interface` records and virtual
`virtualization.VMInterface` records are supported.

## Runtime AP Radio Metadata

For UniFi access points, radio interfaces are synced as NetBox wireless
interfaces. When UniFi reports operational radio data, the interface description
is enriched with:

- band
- channel
- channel width
- transmit power
- channel utilization
- noise floor
- state/enabled status

## Device Type Selection and Creation

Before creating a type, normal device sync looks for:

1. A part-number match for the model's known SKU or reported model, ignoring case
   and separators. A product-named library type is preferred over a code-named one.
2. A community-library slug or product-model match.
3. An exact reported-model match under the selected manufacturer.

The manufacturer lookup prefers `ubiquiti` and accepts legacy `ubiquity`.
An imported type can therefore retain a product name while matching UniFi model
codes and variants such as `USW 48 POE` and `USW-48-POE`. Curated types retain
specs/templates during normal device sync. New types use community metadata
where available; otherwise a basic type is created without enriched templates.

## Live Readings and Component Counters

`SYNC_LIVE_READINGS=false` omits supported rapidly changing metadata such as
PoE draw, radio utilization, uptime and client signal/AP/timestamps. Set it in
the worker environment; it has no Settings UI field. Stable metadata remains.

Power ports created from device-type templates rely on NetBox counter caches.
Version 0.3.26 refreshes signal-updated counters before subsequent saves. This
prevents newly created ports from becoming hidden by a stale zero count; it is
not a bulk repair of counters already incorrect from an older release. See
[troubleshooting](troubleshooting.md#power-ports-exist-but-the-device-tab-shows-zero).
