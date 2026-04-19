# Device Type Specs

Device type enrichment combines two sources at runtime:

1. `UNIFI_MODEL_SPECS` in `netbox_unifi_sync/services/unifi/model_specs.py` (**46 hardcoded models**)
2. `data/ubiquiti_device_specs.json` (community bundle):
   - **173** entries indexed by model (`by_model`)
   - **166** entries indexed by part number (`by_part`)

Optional startup refresh (env-controlled) can rebuild the bundle from:
- `netbox-community/devicetype-library` (same upstream data used by Device-Type-Library-Import)
- UniFi Store technical specs (`UNIFI_SPECS_INCLUDE_STORE=true`)

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
```

With UniFi Store enrichment disabled:

```bash
python3 tools/refresh_unifi_specs.py --skip-store
```

## Synced Template Types

`_sync_templates()` in `netbox_unifi_sync/services/sync_engine.py` handles:

- interface templates (`dcim.interface_templates`)
- console port templates (`dcim.console_port_templates`)
- power port templates (`dcim.power_port_templates`)

If expected template set differs from existing templates, current templates are replaced for that device type.

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
- SSID
- AP name
- signal
- last seen timestamp

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

## Auto-Create Device Types

When UniFi reports an unknown model:

1. `_resolve_device_specs(model)` is called
2. If specs exist, a NetBox device type is created
3. `ensure_device_type_specs()` applies template sync and metadata fields

If no spec is found, devices still sync, but without enriched template definitions.
