from os import getenv

# Imported by NetBox runtime configuration.py in netbox-docker.
# Do not edit /opt/netbox/netbox/netbox/configuration.py directly in container.
PLUGINS = ["unifi2netbox"]

PLUGINS_CONFIG = {
    "unifi2netbox": {
        "unifi_url": getenv("UNIFI_URL", "https://unifi.local"),
        "auth_mode": getenv("UNIFI_AUTH_MODE", "api_key"),  # api_key | login
        "api_key": "env:UNIFI_API_KEY",
        "username": "env:UNIFI_USERNAME",
        "password": "env:UNIFI_PASSWORD",
        "verify_ssl": getenv("UNIFI_VERIFY_SSL", "true").lower() == "true",
        "default_site": getenv("UNIFI_DEFAULT_SITE", ""),
        "dry_run": getenv("UNIFI_DRY_RUN", "false").lower() == "true",
        # Optional override. If omitted, plugin resolves internal NetBox API context at runtime.
        # "netbox_url": getenv("NETBOX_API_URL", "http://netbox:8080"),
        # "netbox_token": "env:NETBOX_TOKEN",
        "netbox_import_tenant": getenv("NETBOX_TENANT", "Default"),
        "netbox_roles": {
            "WIRELESS": "Wireless AP",
            "ROUTER": "Router",
            "SWITCH": "Switch",
            "SECURITY": "Security Appliance",
            "PHONE": "VoIP Phone",
            "OTHER": "Network Device",
        },
        "unifi_site_mappings": {},
        "tag_strategy": "append",
        "default_tags": ["unifi-sync"],
        "rate_limit_per_second": 0,
    }
}
