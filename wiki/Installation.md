# Installation

Current release: [v0.3.27](https://pypi.org/project/netbox-unifi-sync/0.3.27/).
Install into the Python environment used by NetBox and every worker. The plugin
supports NetBox 4.2–4.x and Python 3.11+; respect NetBox's own Python requirements.

```bash
python -m pip install netbox-unifi-sync==0.3.27
python -m pip check
```

Enable the plugin in NetBox configuration, retaining any other enabled plugins:

```python
PLUGINS = ["netbox_unifi_sync"]
PLUGINS_CONFIG = {"netbox_unifi_sync": {}}
```

Apply migrations and restart web/worker services:

```bash
python manage.py migrate
python manage.py check
```

Configure credentials in **Controllers**, Settings and site mappings in the UI.
Run a controller test, then preflight and a first full sync without cleanup.
See [Configuration](Configuration) and [Run Sync](Run-Sync).

For netbox-docker, use a custom image containing the pinned package for both
services or the separate editable development mount. The stock image does not
consume a new `local_requirements.txt` without a custom build. Follow the
[complete Docker guide](https://github.com/unifi2netbox/netbox-unifi-sync/blob/main/deploy/netbox-docker/README.md).

Existing installations should follow [Upgrade](Upgrade). Full paths, migrations
and deployment details are in the
[server guide](https://github.com/unifi2netbox/netbox-unifi-sync/blob/main/docs/server-install.md).
