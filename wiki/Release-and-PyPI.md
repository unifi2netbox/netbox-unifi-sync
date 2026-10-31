# Release and PyPI

The current package is
[netbox-unifi-sync 0.3.27](https://pypi.org/project/netbox-unifi-sync/0.3.27/).
The [GitHub Release](https://github.com/unifi2netbox/netbox-unifi-sync/releases/tag/v0.3.27)
and PyPI upload are separate publication results.

## Maintainer workflow

1. Set the next unpublished version in `pyproject.toml`,
   `netbox_unifi_sync/version.py` and `netbox-plugin.yaml`. Add its changelog entry.
2. Pass review and CI, then merge the versioned source.
3. Run **Create Release Tag (manual)** with version, ref and version verification
   enabled, or push the matching annotated `vX.Y.Z` tag.
4. Release checks lint/security, dependency audit, Python 3.11/3.12 tests, build
   and matching metadata before publishing the GitHub Release.
5. A tag-push release starts standalone publication through `workflow_run`.
   The manual tag workflow calls release checks directly and explicitly
   dispatches standalone publication afterward.

## Trusted Publisher

Configure this exact identity in PyPI:

- Project: `netbox-unifi-sync`
- Owner/repository: `unifi2netbox/netbox-unifi-sync`
- Workflow: `publish-python-package.yml`
- Environment: `pypi`

Publication runs as its own workflow so OIDC and artifact attestations use this
identity. A nested reusable publisher can produce a caller `release.yml` Build
Config URI that PyPI rejects. Current publication retains both OIDC and attestations.

## Retry and verification

The automatic resolver requires a successful release job, the original tag
commit, the expected repository/tag-push event and a published GitHub Release.
A failed quality gate does not authorize publication. Manual retry uses **Publish
Python Package** on `main` with the exact existing release tag; `skip_existing`
can handle an already uploaded part of the same release.

Never move a published tag or reuse PyPI filenames for different/deleted artifacts.
Use a new version for changed artifacts. Inspect the actual final HTTP error,
not just the Docker startup lines.

v0.3.26 publication succeeded in
[run 41222067811](https://github.com/unifi2netbox/netbox-unifi-sync/actions/runs/41222067811).
Verify wheel and sdist on the exact PyPI page and test installation. See the
[canonical release guide](https://github.com/unifi2netbox/netbox-unifi-sync/blob/main/docs/release.md)
for commands and recovery details.
