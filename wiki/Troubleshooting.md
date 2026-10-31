# Troubleshooting

Start with **Runs -> Run detail**, the controller test and worker logs. Confirm
that web and worker runtimes report the same plugin version.

## Plugin missing or startup errors

Check `PLUGINS`, package installation in both runtimes, pending migrations and
`manage.py check`. In Docker, the stock image needs a custom plugin image or
editable mount; adding a requirements file alone is insufficient.

## Missing or unexpected sync data

- Check controller authentication, import tenant/roles and site mappings.
- Prefixes require `sync_prefixes`; disabling it also blocks inferred prefixes.
- Distinct hardware sharing a name should receive stable serial suffixes in
  v0.3.26. Inspect the resolved serial and mapped site for skipped devices.
- Imported types match normalized SKUs under `ubiquiti` or legacy `ubiquity`.
- New power ports should retain their counters after saves; old incorrect counts
  may need a supported NetBox repair procedure.
- Repeated session login clears old cookie/CSRF state before authentication.
- Cleanup may be skipped for separate credential/mapping execution groups.

Dry-run is a preflight, not an object-change or deletion preview. Avoid overlap
between independent worker processes and use [Upgrade](Upgrade) for staging checks.

## Permissions

Dashboard access needs `view_syncrun`; queueing needs `add_syncrun` or `run_sync`.
Cleanup additionally needs `run_cleanup`. Controller testing accepts the
controller change permission or the custom test permission.

## Release or PyPI failure

GitHub Release existence does not prove PyPI upload succeeded. Inspect the
standalone publisher. A Build Config URI mismatch requires the expected
`publish-python-package.yml` identity and `pypi` environment. Retry publication
on `main` for the existing release tag; keep OIDC and attestations enabled.
Changed/deleted filenames on PyPI require a new version. See [Release and PyPI](Release-and-PyPI).

The old `netbox:8080`/localhost self-call errors came from 0.1.x; current versions
use the Django ORM. Follow [Installation](Installation) or [Upgrade](Upgrade).

Full diagnostics and issue-report details:
[troubleshooting guide](https://github.com/unifi2netbox/netbox-unifi-sync/blob/main/docs/troubleshooting.md).
Share sanitized errors only; exclude keys, tokens, cookies, passwords and MFA seeds.
