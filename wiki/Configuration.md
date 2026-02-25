# Configuration

Runtime-konfiguration håndteres primært i NetBox UI:

- `Plugins -> UniFi Sync -> Settings`
- `Plugins -> UniFi Sync -> Controllers`
- `Plugins -> UniFi Sync -> Site mappings`

## Minimum required

1. Opret global settings med:
   - `tenant_name`
   - `netbox_roles`
2. Opret mindst én aktiv controller.
3. Opret site mappings hvor UniFi site-navn != NetBox site-navn.

## Credentials

Brug references i stedet for plaintext:

- `env:VAR_NAME`
- `file:/absolute/path/to/secret`

## Optional bootstrap in PLUGINS_CONFIG

Du kan stadig pre-seede defaults via `PLUGINS_CONFIG["netbox_unifi_sync"]`, men UI-modeller er autoritativ runtime state.

Reference: [docs/configuration.md](https://github.com/unifi2netbox/netbox-unifi-sync/blob/main/docs/configuration.md)
