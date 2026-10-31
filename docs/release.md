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

4. `release.yml` runs on a user-pushed tag, gates on lint/security, dependency audit, Python 3.11/3.12 tests, build and matching versions, and creates the GitHub Release. The manual tag workflow calls it directly.
5. A standalone `publish-python-package.yml` run publishes to PyPI after verifying the completed release workflow. The manual tag workflow dispatches publication explicitly; manual publication is also available for retry.

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

Keep versions aligned in all three files:

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
  - calls the reusable `release.yml` workflow after creating the tag
  - dispatches the standalone publish workflow after the release succeeds
- `release.yml`:
  - runs on push of tags matching `v*`, or as a reusable workflow
  - runs lint/security, dependency audit, Python 3.11/3.12 tests and package build
  - requires all three version files to match the release tag
  - creates GitHub Release
  - completion starts standalone publication through `workflow_run`
- `publish-python-package.yml`:
  - runs as a top-level workflow on release completion (`workflow_run`)
  - verifies that the release job passed and the tag matches the validated commit
  - requires a published GitHub Release before uploading
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
   - `version`: the next unpublished version (for example `0.3.27` or `v0.3.27`)
   - `ref`: `main` (or a specific commit SHA)
   - `verify_version_files`: `true` (recommended)
4. The workflow creates/pushes `vX.Y.Z`, then calls `release.yml`.
5. `release.yml` runs its quality gates and creates the GitHub Release from the matching changelog section.
6. The manual tag workflow dispatches `publish-python-package.yml`, which publishes to PyPI.

The manual tag workflow calls the release checks explicitly because a tag pushed
with `GITHUB_TOKEN` does not start another workflow. Publication runs as its own
workflow so both the OIDC identity and artifact attestation name
`publish-python-package.yml`, matching the configured PyPI Trusted Publisher.
Calling it as a reusable workflow can give the attestation the caller's
`release.yml` identity instead, causing PyPI to reject the upload.

A tag-push release starts publication through `workflow_run`, including recovery
of an older run whose release job passed but whose nested publisher failed.
The resolver checks the successful release job, repository, triggering event,
published release and tag commit before permitting deployment. A failed test or
release build does not authorize publication. The manual tag workflow uses an
explicit `workflow_dispatch`, which is permitted with `GITHUB_TOKEN`.

Manual publication remains available to retry a failed upload with the same tag.

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

## Recovering a Failed Publication

GitHub Release creation and PyPI publication are independent results. Inspect
**Publish Python Package**, including its `resolve` and `deploy` jobs, rather
than relying on the presence of a release page. Container startup lines are not
the upload error; inspect the final HTTP response in the publish step.

1. Fix the reported workflow/configuration error on `main` and pass CI.
2. For an existing published GitHub Release, run **Publish Python Package** on
   `main` using its exact tag. Manual retry supports `skip_existing` for artifacts
   that were already uploaded successfully.
3. For the older nested-publisher failure, rerunning the failed release workflow
   jobs can trigger standalone recovery. The resolver accepts a successful
   quality-gated release job and matching tag commit; a failed build alone does
   not authorize upload. The historical run may remain red while standalone
   publication succeeds.
4. Confirm both wheel and sdist on the exact PyPI version page, then install the
   published package in a clean environment and run `pip check`.

If an attestation names `release.yml` while PyPI expects
`publish-python-package.yml`, use the standalone workflow so its identity
matches the Trusted Publisher. Keep OIDC and attestations enabled. A filename
already used for different or deleted artifacts requires a new package version;
do not move the old tag or rebuild different content under the same version.

## Verified v0.3.26 Publication

- [GitHub Release](https://github.com/unifi2netbox/netbox-unifi-sync/releases/tag/v0.3.26)
- [PyPI version and files](https://pypi.org/project/netbox-unifi-sync/0.3.26/)
- [Successful standalone publication](https://github.com/unifi2netbox/netbox-unifi-sync/actions/runs/41222067811)

Both wheel and sdist were published, and installation/import of the published
package was verified. [PR #28](https://github.com/unifi2netbox/netbox-unifi-sync/pull/28)
contains the runtime fixes; [PR #29](https://github.com/unifi2netbox/netbox-unifi-sync/pull/29)
fixes publication identity. See [upgrade](upgrade.md) for deployment steps.
