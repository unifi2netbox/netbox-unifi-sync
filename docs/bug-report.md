# Bug Report Guide

Use this guide when reporting defects in `netbox_unifi_sync`.

## Required Information

Include:

- NetBox version
- Plugin version (`pip show netbox-unifi-sync` or `netbox_unifi_sync/version.py`)
- Deployment mode (`venv` or `netbox-docker`)
- Python version in NetBox + worker runtime
- Exact failing action (UI run, scheduler run, CLI run, release workflow, etc.)
- Sanitized error text from:
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
docker run --rm -v "$PWD":/work -w /work python:3.12 bash -lc "python -m pip install --upgrade pip && pip install -r requirements.txt -e . ruff bandit pip-audit && ruff check netbox_unifi_sync/ && bandit -r netbox_unifi_sync/ -ll && pip-audit -r requirements.txt"
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

## Details for v0.3.26 Regressions

For prefixes, include `sync_prefixes`, VRF/site scope and whether independent
workers overlapped. For naming/type matching, include sanitized incoming model,
resolved serial strategy, existing device site/tenant and device-type part
number/slug. For hidden power ports, compare actual component rows with cached
counts and say whether the device predates the upgrade.

For publication failures, link the workflow run and failing step. Container
startup output is not the actual PyPI error; include the sanitized HTTP/error
response near the end of the publish step. Never paste OIDC tokens or credentials.

A successful unit suite or dry-run does not establish live NetBox/UniFi behavior.
State which staging checks were actually performed; use the
[QA checklist](qa-checklist.md).
