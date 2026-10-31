# NetBox Docker Setup

Use a disposable staging stack for live validation of the plugin. Current
package: `netbox-unifi-sync==0.3.26`. Stock netbox-docker images do not install a
repository-local requirements file automatically; build a custom image or use
the separate editable development option below.

## Clone repositories

```bash
git clone https://github.com/unifi2netbox/netbox-unifi-sync.git
cd netbox-unifi-sync
git clone -b release https://github.com/netbox-community/netbox-docker.git .netbox-docker
cp deploy/netbox-docker/configuration/plugins.py .netbox-docker/configuration/plugins.py
```

Keep other enabled plugins if adapting an existing installation.

## Option A: custom image with the published package

From the plugin repository root, create or update
`.netbox-docker/local_requirements.txt` with this requirement, preserving other
required plugins:

```text
netbox-unifi-sync==0.3.26
```

Create `.netbox-docker/Dockerfile-Plugins`:

```dockerfile
ARG NETBOX_IMAGE=docker.io/netboxcommunity/netbox:v4.7-5.1.1
FROM ${NETBOX_IMAGE}
USER root
COPY local_requirements.txt /opt/netbox/local_requirements.txt
RUN /usr/local/bin/uv pip install --python /opt/netbox/venv/bin/python \
    -r /opt/netbox/local_requirements.txt
```

Choose a base-image tag matching your supported NetBox deployment; the default
above is an example from netbox-docker's release configuration, not an instruction
to upgrade an existing NetBox installation.

Create `.netbox-docker/docker-compose.override.yml`:

```yaml
services:
  netbox:
    image: netbox-unifi-sync:0.3.26
    pull_policy: never
    build:
      context: .
      dockerfile: Dockerfile-Plugins
    ports:
      - "127.0.0.1:8000:8080"
  netbox-worker:
    image: netbox-unifi-sync:0.3.26
    pull_policy: never
```

The image is built once and shared by web/worker services. Configure the upstream
stack's database/cache credentials as described by netbox-docker, then:

```bash
cd .netbox-docker
docker compose config
docker compose build netbox
docker compose up -d
docker compose ps
```

## Option B: editable development mount

Use this instead of Option A to test checkout changes. From the plugin repository
root:

```bash
cp deploy/netbox-docker/docker-compose.override.yml .netbox-docker/docker-compose.override.yml
cp deploy/netbox-docker/env.netbox-plugin.example .netbox-docker/.env.plugin
```

Set `UNIFI2NETBOX_PLUGIN_PATH` in `.netbox-docker/.env.plugin` to the absolute
checkout path, then launch with that file as Compose interpolation input:

```bash
cd .netbox-docker
docker compose --env-file .env.plugin config
docker compose --env-file .env.plugin up -d
docker compose --env-file .env.plugin ps
```

The supplied override runs editable installation at startup for both services
and uses root for that development setup. Its port mapping exposes port 8000;
adapt it to bind localhost on shared hosts. The mount path is host configuration,
not a UniFi credential, and does not need appending to `env/netbox.env`.
Use explicit `--env-file .env.plugin` for subsequent Compose commands in this mode.

## Migrate and validate

For Option A (add `--env-file .env.plugin` for Option B):

```bash
docker compose exec netbox /opt/netbox/netbox/manage.py migrate
docker compose exec netbox /opt/netbox/netbox/manage.py check
docker compose exec netbox /opt/netbox/netbox/manage.py createsuperuser
docker compose exec netbox /opt/netbox/venv/bin/python -m pip check
docker compose exec netbox /opt/netbox/venv/bin/python -c 'from netbox_unifi_sync.version import __version__; print(__version__)'
docker compose exec netbox-worker /opt/netbox/venv/bin/python -c 'from netbox_unifi_sync.version import __version__; print(__version__)'
```

Open `http://localhost:8000`, configure plugin Settings, Controllers and Mappings,
then test the controller. Run preflight before full sync:

```bash
docker compose exec netbox /opt/netbox/netbox/manage.py netbox_unifi_sync_run --dry-run --json
docker compose exec netbox /opt/netbox/netbox/manage.py netbox_unifi_sync_run --json
```

Dry-run checks configuration/database/controller access; it is not an object
change or cleanup preview. Follow [upgrade checks](../../docs/upgrade.md) and the
[QA checklist](../../docs/qa-checklist.md). These setup examples are documentation,
not evidence that the full live stack has been tested for your deployment.

## Updating

For Option A, replace the package pin, rebuild the image, recreate both services,
apply pending migrations and verify versions. For Option B, update the checkout
and restart both services with the same Compose interpolation file. Avoid
separate sync processes overlapping; Python locks are process-local. See
[upgrade and rollback](../../docs/upgrade.md).
