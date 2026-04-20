# Release and PyPI

Package:

- Name: `netbox-unifi-sync`
- Install: `pip install netbox-unifi-sync`

## Trusted Publisher (PyPI + GitHub OIDC)

PyPI publisher must match exactly:

- PyPI Project Name: `netbox-unifi-sync`
- Owner: `unifi2netbox`
- Repository: `netbox-unifi-sync`
- Workflow: `publish-python-package.yml`
- Environment: `pypi`

## Maintainer: Release to PyPI

1. Bump version in:
   - `pyproject.toml` (`[project].version`)
   - `netbox_unifi_sync/version.py` (`__version__`)
   - `netbox-plugin.yaml` (`compatibility[].release`)
2. Configure PyPI Trusted Publisher (OIDC) for this repository/workflow.
3. Create tag `vX.Y.Z` either:
   - via GitHub Actions `Create Release Tag (manual)` (recommended), or
   - manually with git:

```bash
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z
```

4. `release.yml` runs on the tag push, gates on lint/tests, and creates the GitHub Release.
5. `publish-python-package.yml` runs on `release: published` and publishes to PyPI (can also be run manually for retry).

## Release flow

1. Bump version in:
   - `pyproject.toml`
   - `netbox_unifi_sync/version.py`
   - `netbox-plugin.yaml` (`compatibility[].release`)
2. Commit + push `main`
3. Create tag `vX.Y.Z`:
   - recommended: run Actions workflow `Create Release Tag (manual)`
   - alternative: create and push tag manually with git
4. `release.yml` runs on tag push, gates on lint/tests, and creates GitHub release
5. `publish-python-package.yml` publishes to PyPI on `release: published`

Note:
- If publish does not start automatically from the release event, run `Publish Python Package` manually (`workflow_dispatch`) with the same release tag.
- This can happen when the GitHub Release was created by `release.yml` using the repository `GITHUB_TOKEN`; the manual workflow dispatch is the supported retry path.

## Common failure

If upload says filename already used/deleted, publish a new version (e.g. `0.1.2` -> `0.1.3`).

Reference: [docs/release.md](https://github.com/unifi2netbox/netbox-unifi-sync/blob/main/docs/release.md)
