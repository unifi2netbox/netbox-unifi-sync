# NetBox Docker Test Setup (unifi2netbox plugin)

This folder contains a reproducible `netbox-docker` test setup that mounts this plugin locally, installs it in the running containers, and enables it through NetBox `PLUGINS_CONFIG`.

## 1) Clone repositories

```bash
git clone https://github.com/patricklind/unifi2netbox.git
cd unifi2netbox
git clone -b release https://github.com/netbox-community/netbox-docker.git .netbox-docker
```

## 2) Copy override + plugin config

```bash
cp deploy/netbox-docker/docker-compose.override.yml .netbox-docker/docker-compose.override.yml
cp deploy/netbox-docker/configuration/plugins.py .netbox-docker/configuration/plugins.py
```

`netbox-docker` loads `.netbox-docker/configuration/plugins.py` from
`/opt/netbox/netbox/netbox/configuration.py` at runtime.
So your `PLUGINS` and `PLUGINS_CONFIG` are effectively configured via:

- host: `.netbox-docker/configuration/plugins.py`
- container: `/etc/netbox/config/plugins.py` (imported by `/opt/netbox/netbox/netbox/configuration.py`)

## 3) Configure environment variables

Use `deploy/netbox-docker/env.netbox-plugin.example` as baseline.

```bash
cp deploy/netbox-docker/env.netbox-plugin.example .netbox-docker/.env.plugin
```

Set at least:
- `UNIFI2NETBOX_PLUGIN_PATH` (absolute path to this repo)
- `UNIFI_AUTH_MODE` (`api_key` or `login`)
- `UNIFI_API_KEY` for API key auth, or `UNIFI_USERNAME` + `UNIFI_PASSWORD` for login auth

Then export:

```bash
set -a
source .netbox-docker/.env.plugin
set +a
```

Also append variables to `.netbox-docker/env/netbox.env` so NetBox containers can read them at runtime:

```bash
cat .netbox-docker/.env.plugin >> .netbox-docker/env/netbox.env
```

## 4) Start stack

```bash
cd .netbox-docker
docker compose pull
docker compose up -d
```

Check health:

```bash
docker compose ps
docker compose logs -f netbox
```

## 5) Create superuser

```bash
docker compose exec netbox /opt/netbox/netbox/manage.py createsuperuser
```

`unifi2netbox` can resolve an internal NetBox API token automatically at runtime.
Manual `NETBOX_TOKEN` is optional (only needed if you want explicit token control).

## 6) Prepare tenant required by sync

```bash
docker compose exec netbox /opt/netbox/netbox/manage.py shell -c "from tenancy.models import Tenant; Tenant.objects.get_or_create(name='Default', slug='default')"
```

## 7) Test plugin from UI

1. Open `http://localhost:8000`
2. Login with superuser
3. Go to `Plugins -> UniFi2NetBox -> Status`
4. Trigger `Dry run` first
5. Review run output under `Sync Runs`

## 8) Optional CLI smoke test inside NetBox (management command)

```bash
docker compose exec netbox /opt/netbox/netbox/manage.py unifi2netbox_sync --dry-run
```

## Notes

- `auth_mode=api_key` uses header-based Integration API auth.
- `auth_mode=login` uses UniFi session login flow.
- If `auth_mode` is `login`, `api_key` is ignored.
- If `auth_mode` is `api_key`, `username/password` are ignored.
