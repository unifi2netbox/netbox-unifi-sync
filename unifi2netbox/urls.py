"""
URL shim for NetBox plugin discovery.

NetBox registers plugin URL patterns by importing `<plugin_path>.urls`.
This package is configured as `PLUGINS = ["unifi2netbox"]`, while the
implementation lives in `netbox_unifi_sync`.
"""

from netbox_unifi_sync.urls import urlpatterns

app_name = "netbox_unifi_sync"
