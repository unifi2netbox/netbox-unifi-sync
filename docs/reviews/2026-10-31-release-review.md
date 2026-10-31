# Release review: 0.3.26 (2026-10-31)

## Executive summary

This Python/Django NetBox plugin synchronizes UniFi controllers into NetBox
DCIM, IPAM and wireless models. The review addressed issues #26, #17, #16 and
#15, incorporated the latest main-branch fixes, and inspected the relevant
configuration, authorization, orchestration, ORM, UI, API, migration, packaging
and release boundaries. Changes remain targeted; the UI keeps NetBox's existing
templates and styling.

**Assessment: ready with documented limitations.** The available automated
checks pass. Live NetBox/PostgreSQL, Redis/RQ, controller, and browser workflows
were not available locally; this is not a claim of full production validation.

## Project and architecture

- Python >=3.11, Django/NetBox >=4.2, requests, PyYAML, pyotp and python-slugify.
- NetBox UI and management command enqueue/execute the orchestration service.
- Controllers are grouped by credentials and effective site mappings. The
  sync engine uses nested controller/site/device thread pools and a Django ORM
  adapter, carrying NetBox's request context into worker threads.
- Settings come from plugin models; runtime environment overrides translate
  them for the sync engine. The overrides must not overlap in one process.
- `python -m build` creates a wheel and source distribution. GitHub workflows
  run checks, create a release, and call PyPI publication with OIDC.
- Tests use pytest, with framework dependencies isolated where NetBox is absent.

## Findings and fixes

| Severity | Location | Root cause, impact and correction | Verification |
| --- | --- | --- | --- |
| High | `services/sync_engine.py` (#17) | ORM device-name constraints bypassed the old message match. Recognize database constraints and wrapped errors; suffix create/rename conflicts with the incoming serial; bound long names; skip ambiguous hardware matches. | Different serials, repeat sync, rename, wrapped constraints and long/Unicode identifiers. |
| High | `configuration.py` | Concurrent runtime contexts could replace credentials and settings used by another sync. Serialize overrides and restore them even after failure. | Competing thread contexts and exception restoration. |
| High | `configuration.py` | Configuration snapshots omitted MFA seeds and legacy NetBox tokens from redaction. Add both secret fields. | Snapshot redaction regression. |
| High | `jobs.py` | Enqueue enforced cleanup permissions but relied on UI callers for general sync authorization. Enforce both at the job boundary. | Six authorized/unauthorized enqueue combinations. |
| High | dependency manifests | urllib3 2.6.3 had known proxy TLS, redirect-header and decompression advisories. Require the patched 2.8 series and add dependency auditing to CI/release gates. | Fresh dependency resolution and pip-audit: no known vulnerabilities. |
| High | `services/orchestrator.py` | Controllers sharing credentials could merge conflicting scoped mappings. Include effective mappings in the execution grouping key; disable unsafe cross-group stale cleanup. | Same/different mappings with identical credentials, including cleanup behavior. |
| Medium | `services/sync_engine.py` (#26) | Inferred subnet creation ignored the prefix toggle and raced across worker threads. Guard both creation entry points with the option and one lock. Continue primary-IP assignment using an existing parent or host mask. | Disabled toggle, eight concurrent workers, existing /24 and absent-parent /32 cases. |
| Medium | `services/sync/netbox_orm.py` (#16) | Component signals updated cached counters in the database; later saves wrote stale instance values back. Refresh counter fields after create and before save. Use savepoints so uniqueness recovery leaves outer transactions usable. | Counter regression plus real Django/SQLite create/rename/savepoint checks. |
| Medium | `services/sync_engine.py` (#15) | Matching missed SKU separator differences and library names. Combine upstream curated-type preference/manufacturer handling with normalized SKU, slug and library-model fallbacks. Preserve curated specs. | Imported-library variants, case/separator matching, manufacturer filtering and upstream lookup tests. |
| Medium | `services/sync_service.py` | Dry-run could report success after a failed NetBox preflight. Query the database and reject failed checks before controller access. | Failed-preflight regression. |
| Medium | GitHub workflows | Token-created tags/releases do not reliably trigger downstream workflows. Call reusable workflows explicitly, gate release on lint, tests, dependency audit and package build, and check all three versions against the tag. | actionlint; local build/twine; remote execution verified during publication. |
| Medium | GitHub workflows | Manual inputs were interpolated directly into shell source. Transfer them through environment variables and validate tag format. | Workflow static validation and source review. |
| Low | `views.py` | Failed controller tests did not update the attempt timestamp. Save `last_tested` consistently. | Failed-test view regression. |
| Low | `services/orchestrator.py` | A legacy role alias preceding a canonical mapping won incorrectly. Make the canonical mapping take precedence in either insertion order. | Both key orders. |
| Low | `services/sync_engine.py` | A newly merged helper split the import block and failed Ruff. Move the helper below imports. | Ruff. |

Upstream changes retained include thread request-context propagation, snapshots
before mutations, connected-client listing via `stat/sta`, cached-cookie clearing
before login, legacy switch roles, curated device types, and optional live readings.
No unrelated data was removed and no historical migration was rewritten.

## Changed files

Created:

- `tests/test_issue_regressions.py`: four original issue regressions.
- `tests/test_review_regressions.py`: authorization, configuration, concurrency,
  preflight, mapping, timestamp and identifier boundary regressions.
- This report.

Modified:

- `services/sync_engine.py`, `services/sync/netbox_orm.py`: original issue fixes.
- `configuration.py`, `jobs.py`, `views.py`, `services/orchestrator.py`,
  `services/_validation.py`, `services/sync_service.py`: review fixes.
- `pyproject.toml`, `requirements.txt`, `version.py`, `netbox-plugin.yaml`:
  patched dependency and aligned version 0.3.26.
- `.github/workflows/{ci,create-release-tag,release,publish-python-package}.yml`:
  secure input handling, explicit workflow calls and release quality gates.
- `CHANGELOG.md`, `docs/release.md`, `docs/architecture.md`: behavior and release
  documentation.

No files moved or deleted. No schema migration or visual redesign is required.
UI changes concern error-state timestamps and server-side permissions; browser
appearance, responsive behavior and accessibility were not runtime-tested.

## Verification and commands

Commands used the prepared Python 3.12 virtual environment unless noted.

| Command/check | Result |
| --- | --- |
| `pytest -q` | 237 passed, 1 skipped (pre-existing live-NetBox placeholder). |
| `ruff check netbox_unifi_sync/ tests/test_issue_regressions.py tests/test_review_regressions.py` | Passed after fixing the upstream import placement. |
| `bandit -r netbox_unifi_sync/ -ll` | Passed: no medium/high findings. Existing suppression-comment warnings remain. |
| `pip-audit -r requirements.txt` | Initially found urllib3 advisories; passed after the targeted dependency update. |
| `python -m compileall -q netbox_unifi_sync/` | Passed. |
| `actionlint` 1.7.12 | All four workflows passed. |
| `python -m build --no-isolation` | Wheel and sdist built; the initial missing setuptools backend was installed in the build environment. |
| `twine check` on both 0.3.26 artifacts | Passed. |
| `git diff --check` | Passed. |
| Isolated Django 5.2/SQLite ORM transaction exercise | Passed create and rename uniqueness recovery inside an outer transaction, plus preservation of component counters on subsequent save. |

The full suite was rerun after rebasing on the current main branch and after the
review fixes. GitHub additionally runs Python 3.11 and 3.12 checks before release.
The local artifact directory is `/workspace/artifacts/netbox-unifi-sync/0.3.26/`.

Tools used: shell/Git, GitHub connector, the cloud runtime skill and environment
status, pytest, Ruff, Bandit, pip-audit, actionlint, build, twine, and Django's
SQLite ORM. No browser session or UI runtime was available; no browser test is
claimed. Repository and release state were read through the GitHub connector;
Git transport used the managed environment's supported network permissions.

## Remaining limitations

- Live integration verification: NetBox component signals/UI counters,
  PostgreSQL constraint diagnostics, RQ scheduling, real UniFi APIs, and
  browser keyboard/mobile/accessibility flows need a staging deployment.
- Concurrency: Python locks coordinate threads and runs in one process; they
  do not prevent simultaneous prefix creation by independent worker processes.
  NetBox deliberately permits duplicate prefixes, so this release does not add
  a database uniqueness constraint. Avoid overlapping scheduled/manual workers
  until multi-process behavior has been verified in PostgreSQL.
- Dependency scans report the advisories known at scan time, not an assurance
  against all vulnerabilities. CI now repeats the scan on subsequent changes.
- Publication still depends on repository Actions permissions and the configured
  PyPI Trusted Publisher/environment. Verify remote workflow status before
  treating the package as published.

Next verification step: install 0.3.26 in staging, run each original issue's
reproduction, then repeat the sync to confirm idempotency and component visibility.
