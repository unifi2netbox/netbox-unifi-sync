# Release and PyPI Publish

This plugin is published as:

- package name: `netbox-unifi-sync`
- install command: `pip install netbox-unifi-sync`
- project URL: <https://pypi.org/project/netbox-unifi-sync/>

## Maintainer: Release to PyPI

1. Bump version in:
   - `pyproject.toml` (`[project].version`)
   - `netbox_unifi_sync/version.py` (`__version__`)
   - `netbox-plugin.yaml` (`compatibility[].release`)
2. Configure **PyPI Trusted Publisher** (OIDC) for this repository/workflow if not already configured.
3. Create tag `vX.Y.Z` either:
   - via GitHub Actions **Create Release Tag (manual)** (recommended), or
   - manually with git:

```bash
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z
```

4. `release.yml` runs on the tag push, gates on lint/tests, and creates the GitHub Release.
5. `publish-python-package.yml` runs on `release: published` and publishes to PyPI (can also be run manually for retry).

## One-Time Setup

1. Create project on PyPI:
   - `netbox-unifi-sync`
2. Configure **PyPI Trusted Publisher** (GitHub OIDC) with:
   - **PyPI Project Name**: `netbox-unifi-sync`
   - **Owner**: `unifi2netbox`
   - **Repository name**: `netbox-unifi-sync`
   - **Workflow name**: `publish-python-package.yml`
   - **Environment name**: `pypi`
3. In GitHub repository settings, create environment:
   - `pypi`

Read more: GitHub Actions OpenID Connect support  
https://docs.github.com/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect

## Versioning Rules

Keep versions aligned in both files:

- `pyproject.toml` -> `[project].version`
- `netbox_unifi_sync/version.py` -> `__version__`
- `netbox-plugin.yaml` -> `compatibility[].release`

Tag must match version exactly: `vX.Y.Z`.

## Automated Publish Flow

Configured workflows:

- `create-release-tag.yml`:
  - runs only on manual dispatch
  - creates and pushes an annotated tag (`vX.Y.Z`)
  - can validate version consistency in `pyproject.toml`, `version.py`, and `netbox-plugin.yaml`
  - triggers `release.yml` automatically via tag push
- `release.yml`:
  - runs on push of tags matching `v*`
  - runs lint + tests first
  - creates GitHub Release
- `publish-python-package.yml`:
  - runs automatically on `release: published`
  - can also be run manually (`workflow_dispatch`) for retry
  - uses environment `pypi`
  - uses GitHub OIDC (`id-token: write`)
  - builds package (`sdist` + `wheel`)
  - runs `twine check`
  - publishes to PyPI without API token secret

## Manual Release from GitHub UI

1. Commit and push version/changelog updates on `main`.
2. Open Actions -> `Create Release Tag (manual)`.
3. Click `Run workflow` and set:
   - `version`: `0.3.19` (or `v0.3.19`)
   - `ref`: `main` (or a specific commit SHA)
   - `verify_version_files`: `true` (recommended)
4. The workflow creates/pushes `vX.Y.Z`, which triggers `release.yml`.
5. `release.yml` runs lint/tests and creates the GitHub Release.
6. Publishing that release triggers `publish-python-package.yml`, which publishes to PyPI.

## Recommended CLI Commands (alternative)

```bash
git add pyproject.toml netbox_unifi_sync/version.py netbox-plugin.yaml CHANGELOG.md
git commit -m "Release vX.Y.Z"
git push origin main
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z
```

If PyPI publish fails, run `Publish Python Package` manually from GitHub Actions (`workflow_dispatch`) with the same tag.

## Manual Publish (fallback)

```bash
python -m pip install --upgrade build twine
python -m build
twine check dist/*
twine upload dist/*
```

Use (only for fallback without OIDC):

- username: `__token__`
- password: `<your PyPI API token>`

## Verification

After publish:

```bash
python -m pip index versions netbox-unifi-sync
pip install netbox-unifi-sync
```
