# Maintenance Backlog

Status recorded for **v0.3.26**, published 2026-10-31. This is a maintenance
snapshot, not an assertion that live NetBox/UniFi integration has been validated.
See the [release review](docs/reviews/2026-10-31-release-review.md) and
[QA checklist](docs/qa-checklist.md).

## Completed in the release and publication follow-up

- Issues #26, #17, #16 and #15: prefix toggle/thread safety, deterministic device
  names, component counters and library device-type reuse.
- Runtime credential isolation, controller-scoped mapping separation, enqueue
  permissions, secret snapshot redaction and failed preflight handling.
- Canonical role precedence and failed-controller test timestamps.
- urllib3 2.8.x security update and dependency auditing in CI/release checks.
- Explicit release checks and standalone PyPI publication with matching
  Trusted Publisher identity and attestations.
- Baseline after publication follow-up: 249 passed, one pre-existing live-NetBox
  placeholder skipped; CI/build/audit/publication checks passed.

## Priorities

1. **Live integration coverage**: replace the skipped smoke placeholder with
   repeatable NetBox/PostgreSQL, Redis/RQ and UniFi staging tests. Cover upgrade,
   repeated sync, component signals, permissions and API variants.
2. **Cross-process coordination**: runtime and prefix locks are process-local.
   Validate independent RQ workers/management commands and design explicit
   overlap prevention before promising global duplicate protection.
3. **Cleanup scope**: cleanup currently requires one credential/mapping execution
   group. Explore safe aggregation across groups without deleting another
   group's hardware. Preserve the existing skip behavior until validated.
4. **Existing-data repair**: document and test supported reconciliation of old
   duplicate prefixes/types and stale component counters. Avoid automatic
   destructive repair or new uniqueness constraints without a migration plan.
5. **Scheduler robustness**: test concurrent ticks, long runs and worker crashes.
   `mark_scheduler_tick()` runs before sync; a failure can still advance the
   schedule timestamp. Check status reconciliation against real RQ state.
6. **Error handling and module boundaries**: audit broad exception guards where
   failures can obscure partial sync; extract domains incrementally only where
   tests and maintenance benefit. Do not target arbitrary line/catch counts.
7. **Scanner noise**: remove obsolete Bandit suppression comments only after
   checking which findings they suppress, keeping real checks enabled.
8. **Configuration clarity**: keep UI models authoritative and document bootstrap
   compatibility keys without implying unsupported UI options.

## Validation commands

Install developer tools as described in [CONTRIBUTING](CONTRIBUTING.md), then:

```bash
ruff check netbox_unifi_sync/
pytest -q
bandit -r netbox_unifi_sync/ -ll
pip-audit -r requirements.txt
python -m build
twine check dist/*
```

Use `actionlint` for workflow changes. Follow [release](docs/release.md) for all
three version files and publication identity, and [upgrade](docs/upgrade.md) for
deployment/rollback. Test counts are historical observations, not hardcoded
requirements for future changes.
