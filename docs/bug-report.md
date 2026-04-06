# Bug Report Guide

Use this guide when reporting defects in `netbox_unifi_sync`.

## Required Information

Include:

- NetBox version
- Plugin version (`pip show netbox-unifi-sync` or `netbox_unifi_sync/version.py`)
- Deployment mode (`venv` or `netbox-docker`)
- Python version in NetBox + worker runtime
- Exact failing action (UI run, scheduler run, CLI run, release workflow, etc.)
- Full error text from:
  - `Plugins -> UniFi Sync -> Runs -> Run detail`
  - worker logs

Do not include secrets (API keys, passwords, MFA secrets, tokens, cookies).

## Reproduction Template

1. Initial state (settings/controller/site mapping values).
2. Exact command or UI action used.
3. Expected behavior.
4. Actual behavior.
5. Whether issue is deterministic or intermittent.

## Local Validation Commands (Docker)

From repository root:

```bash
docker run --rm -v "$PWD":/work -w /work python:3.12 bash -lc "python -m pip install --upgrade pip && pip install -r requirements.txt -e . ruff bandit && ruff check netbox_unifi_sync/ && bandit -r netbox_unifi_sync/ -ll"
docker run --rm -v "$PWD":/work -w /work python:3.11 bash -lc "python -m pip install --upgrade pip && pip install -r requirements.txt -e . pytest && pytest -q"
docker run --rm -v "$PWD":/work -w /work python:3.12 bash -lc "python -m pip install --upgrade pip && pip install -r requirements.txt -e . pytest && pytest -q"
```

Optional package build check:

```bash
docker run --rm -v "$PWD":/work -w /work python:3.12 bash -lc "python -m pip install --upgrade pip && pip install build twine && python -m build && twine check dist/*"
```

## NetBox Runtime Checks

```bash
python manage.py showmigrations netbox_unifi_sync
python manage.py check
python manage.py netbox_unifi_sync_run --dry-run --json
```

## Useful Attachments

- Screenshot of `Runs` error page
- Relevant worker log excerpt around failure timestamp
- Sanitized controller test result from:
  - `POST /plugins/unifi-sync/api/controllers/<pk>/test/`
