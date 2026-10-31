# Agent Instructions

These instructions apply to the whole repository. Read [CONTRIBUTING.md](CONTRIBUTING.md)
before changing code. Keep agent-assisted work understandable, focused and ready
for human review. Explicit maintainer instructions define the task's scope and
authorization; existing authorization need not be requested repeatedly.

## Start with the repository

- Inspect `git status` and the existing diff. Preserve unrelated and uncommitted work.
- Read the affected implementation, its callers and relevant tests before editing.
- Use the existing modules and test framework. Fix the root cause with a small,
  reviewable change; avoid broad refactors, dependency churn and cosmetic rewrites.
- Reference an existing issue when applicable. Align larger architectural changes
  with the maintainer before implementation.
- Distinguish confirmed behavior from assumptions. Record unavailable runtime
  checks instead of presenting them as passed.

## Project and code map

This is a Python NetBox plugin synchronizing UniFi into NetBox DCIM, IPAM and
wireless models. Python minimum and dependencies are in [pyproject.toml](pyproject.toml).
NetBox compatibility is declared in [netbox-plugin.yaml](netbox-plugin.yaml)
and [netbox_unifi_sync/__init__.py](netbox_unifi_sync/__init__.py).
CI tests Python 3.11 and 3.12. Preserve supported NetBox 4.x behavior.

| Area | Responsibility |
| --- | --- |
| `netbox_unifi_sync/models.py`, `forms.py`, `views.py`, `templates/`, `api/`, `urls.py` | Plugin configuration, UI and authenticated endpoints |
| `netbox_unifi_sync/jobs.py`, `management/commands/` | NetBox jobs, scheduling and administrative command entry point |
| `services/orchestrator.py`, `runtime.py`, `_validation.py` | Controller grouping, effective configuration and cleanup eligibility |
| `services/sync_service.py`, `configuration.py` | Execution/preflight boundary and runtime environment translation |
| `services/sync_engine.py` | Device/site/controller synchronization and cleanup pipeline |
| `services/sync/netbox_orm.py` | Django ORM adapter exposing the engine's endpoint-style interface |
| `services/sync/ipam.py`, `vrf.py`, `runtime_config.py` | IPAM, VRF and runtime parsing helpers |
| `services/unifi/` | Integration/legacy API clients, resources, authentication and specs refresh |
| `services/permissions.py`, `audit.py`, `sync/log_sanitizer.py` | Shared authorization and secret-safe audit/log handling |
| `netbox_unifi_sync/migrations/` | Versioned Django schema/data migrations |
| `tests/`, `tests/integration/` | pytest regressions and live-integration coverage/limitations |
| `docs/`, `wiki/`, `deploy/netbox-docker/` | User/maintainer guides, Wiki source and local deployment setup |
| `.github/workflows/` | CI, tag creation, release and standalone PyPI publication |

Paths beginning with `services/` in the table are relative to `netbox_unifi_sync/`.
See [architecture](docs/architecture.md) for the execution flow.

## Integration behavior to preserve

- NetBox is treated as the source of truth. Normal synchronization is UniFi to
  NetBox; DHCP-to-static writeback requires explicit `dhcp_writeback_enabled`.
  Do not introduce additional UniFi writes without a deliberate requirement.
- UI models are authoritative runtime configuration. `PLUGINS_CONFIG` is optional
  bootstrap input. Follow existing translation/validation rather than inventing
  a parallel configuration path. A new setting may require model, form, migration,
  mapping, environment and documentation changes; inspect the full path.
- NetBox access uses the Django ORM adapter. Preserve its endpoint contract and
  avoid adding HTTP self-calls or restoring a pynetbox dependency.
- Device identity uses the mapped site and resolved serial, not display name
  alone. Preserve deterministic, bounded name suffixes for collisions and warnings
  for missing/ambiguous identifiers. Repeated sync must not duplicate hardware.
- Prefer normalized library part-number/type matches and preserve curated specs
  during normal device sync. Cleanup's type-refresh pass is a separate behavior.
- `sync_prefixes=false` must prevent configured and inferred prefix creation.
  Existing parents remain usable for IP masks; absent parents use host masks.
  Existing duplicate data must not be deleted or merged incidentally.
- Support both Integration API and legacy API payloads where the affected feature
  already does. Keep pagination, TLS verification, timeouts and retries intact.

## ORM, concurrency and cleanup

- Preserve snapshots before mutation, concrete foreign-key writes through their
  column attributes, and signal-updated component counter caches.
- Contain recoverable database constraint failures in savepoints so retry logic
  does not leave an outer transaction unusable. Keep original exception causes.
- Submit thread-pool tasks with copied context so NetBox change logging retains
  its request/actor context across controller, site and device workers.
- Keep credentials and effective site mappings isolated between execution groups.
  Preserve serialization of process-wide environment overrides and restore them
  after failures. Existing Python locks are process-local; do not claim they
  coordinate independent RQ workers or management commands.
- Preserve cleanup's skip behavior when multiple credential/mapping execution
  groups are needed. Cleanup is destructive and has site/tenant/manufacturer
  scopes; the stale-device grace period does not protect all cleanup categories.
- Dry-run is configuration/database/controller preflight, not an object diff or
  deletion preview. It avoids network-object synchronization, but run/audit
  history and controller session state may still be recorded.
- Do not run live cleanup, bulk repair, migrations or writeback against a user's
  deployment merely to validate a code change. Use an authorized staging setup.
- Add new migrations for schema changes. Do not rewrite applied migrations or
  silently discard conflicting existing data.

## Authorization and secrets

- Reuse `services/permissions.py` at UI and enqueue boundaries. Sync requires
  `run_sync` or `add_syncrun`; cleanup additionally requires `run_cleanup`.
  Preserve the controller-test permission compatibility path.
- Enforce access control server-side. Retain POST/CSRF protections for UI actions;
  hiding a control is not an authorization check.
- Never commit credentials, tokens, MFA seeds, session cookies, secret files,
  private environment details or sensitive log output. Use example values only.
- Controller credential fields support secret references and direct values;
  do not move secrets into `PLUGINS_CONFIG` or source-controlled examples.
- Use existing snapshot/audit/log redaction and test it for new sensitive fields.
  Redaction does not encrypt stored controller credentials.
- Keep TLS verification enabled by default and session-file protections intact.
  Do not disable tests, security scans or attestations to obtain a passing result.

## Setup and validation

Use an existing suitable virtual environment, or create one in the repository:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt -e .
python -m pip install pytest ruff bandit pip-audit build twine
```

Run focused tests first, then the relevant quality gates. These match the CI
commands; choose checks according to the change rather than repeating them
without a reason:

```bash
ruff check netbox_unifi_sync/
pytest -q
bandit -r netbox_unifi_sync/ -ll
pip-audit -r requirements.txt
python -m build
twine check dist/*
git diff --check
```

- Add meaningful pytest regressions for behavior changes, including failure,
  repeated-sync and concurrency cases when relevant. Follow existing fixtures
  and framework-isolation patterns in `tests/`.
- `tests/conftest.py` retains a legacy `main` import alias for the sync engine;
  prefer direct package imports in new tests.
- The normal test suite runs without a live NetBox/UniFi stack. A skipped live
  smoke placeholder is not successful integration coverage. Do not invent test
  results, suppress failures or hardcode a historical expected test count.
- For workflow changes, run `actionlint` if available and exercise changed shell
  authorization/validation paths as in `tests/test_release_workflows.py`.
- For documentation-only edits, check links, anchors, fenced examples and
  `git diff --check`. New implementation tests are unnecessary.
- Use [Docker setup](deploy/netbox-docker/README.md) and the
  [QA checklist](docs/qa-checklist.md) for live staging validation. Both web and
  worker runtimes need the plugin; the stock image does not automatically install
  a newly added `local_requirements.txt`.
- When changing dependencies, keep `requirements.txt` and `pyproject.toml`
  compatible. Resolve, audit and test the resulting dependencies; avoid unrelated
  upgrades or loosening a security minimum to hide a conflict.

## Documentation, review and releases

- Update user-facing docs with behavior/configuration changes. Keep README,
  `docs/`, deployment instructions and `wiki/` summaries consistent; link to
  canonical guides instead of duplicating whole procedures.
- Wiki files are source pages for a separate repository. Do not claim live Wiki
  publication from a source commit alone. Follow [wiki/README.md](wiki/README.md).
- Keep source and packaged device-spec bundles consistent when refreshing them;
  see [device specs](docs/device-specs.md) before running refresh tools.
- Use a focused branch/PR. Explain the problem, correction, reason, validation
  and remaining limitations using [.github/pull_request_template.md](.github/pull_request_template.md).
  Human review is required by CONTRIBUTING; do not merge or publish without
  maintainer authorization for that action. Preserve unrelated Git history.
- Do not bump versions, tag or publish for an ordinary fix/doc task unless
  release work is authorized. For a release, align `pyproject.toml`,
  `netbox_unifi_sync/version.py`, `netbox-plugin.yaml` and the changelog/tag.
- Follow [release](docs/release.md). Tag checks gate GitHub Release creation;
  PyPI publication runs as a standalone `publish-python-package.yml` workflow
  matching its Trusted Publisher and `pypi` environment. Preserve source/tag
  verification, OIDC and artifact attestations.
- A GitHub Release is not proof of PyPI upload. Verify the publication workflow
  and exact PyPI version. Never move published tags or reuse filenames for changed
  artifacts. Report what ran, what passed and what remains unverified.
