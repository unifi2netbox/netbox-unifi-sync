# Upgrade to v0.3.27

[v0.3.27](https://github.com/unifi2netbox/netbox-unifi-sync/releases/tag/v0.3.27)
is available on [PyPI](https://pypi.org/project/netbox-unifi-sync/0.3.27/).

1. Back up NetBox and pause sync scheduling while upgrading.
2. Install `netbox-unifi-sync==0.3.27` in web and every worker environment, or
   rebuild their shared custom image. Check dependency compatibility with `pip check`.
3. Apply pending migrations, run `manage.py check`, and restart both services.
4. Run controller tests and dry-run, then full sync without cleanup on staging.
   Dry-run is connectivity/configuration preflight, not a proposed-change diff.
5. Repeat and verify the four issue reproductions: disabled prefix sync,
   duplicate device names, power-port visibility and imported device-type reuse.
6. Resume the schedule after reviewing results and avoiding overlapping processes.

The release requires patched urllib3 2.8.x and improves controller mapping and
credential isolation. Cleanup is skipped when separate execution groups are
needed. Prefix/runtime locks are process-local. Existing duplicate data and
incorrect counters are not bulk-repaired automatically.

Use the [full upgrade and rollback guide](https://github.com/unifi2netbox/netbox-unifi-sync/blob/main/docs/upgrade.md)
for exact virtualenv/Docker commands, changed behavior and verification limits.
The [release review](https://github.com/unifi2netbox/netbox-unifi-sync/blob/main/docs/reviews/2026-10-31-release-review.md)
records the checks performed; live deployment validation remains required.
