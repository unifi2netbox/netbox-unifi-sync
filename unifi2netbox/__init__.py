"""
Compatibility plugin entrypoint.

Allows NetBox `PLUGINS = ["unifi2netbox"]` while the implementation
lives in `netbox_unifi_sync`.
"""

from netbox_unifi_sync import NetBoxUnifiSyncConfig, config

__all__ = ["NetBoxUnifiSyncConfig", "config"]
