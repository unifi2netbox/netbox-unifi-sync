# netbox-unifi-sync Wiki

`netbox-unifi-sync` er et NetBox plugin til UniFi -> NetBox sync.

## Diagrammer

![Overview](https://raw.githubusercontent.com/unifi2netbox/netbox-unifi-sync/main/docs/assets/netbox-unifi-sync-overview.svg)

```mermaid
flowchart LR
    U["UniFi"] --> P["Plugin Jobs"]
    P --> N["NetBox"]
    UI["Plugin UI"] --> P
```

## Aktuel release

[v0.3.26](https://github.com/unifi2netbox/netbox-unifi-sync/releases/tag/v0.3.26)
er publiceret på [PyPI](https://pypi.org/project/netbox-unifi-sync/0.3.26/).
Se [Upgrade](Upgrade) for udrulning, ændret sync-adfærd og staging-checks.

## Quick links

- [Installation](Installation)
- [Upgrade](Upgrade)
- [Configuration](Configuration)
- [Run Sync](Run-Sync)
- [Release and PyPI](Release-and-PyPI)
- [Troubleshooting](Troubleshooting)

## Source docs in repository

- [README](https://github.com/unifi2netbox/netbox-unifi-sync/blob/main/README.md)
- [Server install](https://github.com/unifi2netbox/netbox-unifi-sync/blob/main/docs/server-install.md)
- [Configuration](https://github.com/unifi2netbox/netbox-unifi-sync/blob/main/docs/configuration.md)
- [Troubleshooting](https://github.com/unifi2netbox/netbox-unifi-sync/blob/main/docs/troubleshooting.md)
- [Release](https://github.com/unifi2netbox/netbox-unifi-sync/blob/main/docs/release.md)
