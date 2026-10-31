# Contributing to netbox-unifi-sync

Thanks for helping improve the project.

This repository is maintained in spare time, but the goal is to make it easy for new contributors to get started without requiring manual setup from the maintainer for each contribution.

## Quick start

1. Fork the repository and create a branch.
2. Clone it locally:

```bash
git clone https://github.com/<your-user>/netbox-unifi-sync.git
cd netbox-unifi-sync
```

3. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

4. Run the checks before opening a PR:

```bash
ruff check netbox_unifi_sync/
pytest -q
```

Optional security lint:

```bash
pip install bandit
bandit -r netbox_unifi_sync/ -ll
```

## Local validation setup

For plugin validation against a running NetBox stack, use the included Docker setup:

```bash
cp deploy/netbox-docker/configuration/plugins.py .netbox-docker/configuration/plugins.py
# or follow the full instructions in deploy/netbox-docker/README.md
```

The full local test setup is documented in:

- `deploy/netbox-docker/README.md`
- `docs/troubleshooting.md`

## Good contribution workflow

- For bug fixes, open or reference an issue first when practical.
- Keep PRs focused on one change or one bug.
- Prefer small, readable patches over broad refactors.
- Add or update tests when behavior changes.
- Keep documentation in sync with user-facing changes.

## Project structure

- `netbox_unifi_sync/` — plugin code
- `tests/` — unit/integration tests
- `docs/` — user and maintainer documentation
- `deploy/netbox-docker/` — local NetBox verification stack
- `wiki/` — GitHub Wiki source pages

## Coding expectations

- Python 3.11+
- Keep changes compatible with the project's existing style
- Prefer explicit, maintainable logic over clever shortcuts
- Validate any setting, API contract, or NetBox compatibility changes carefully

## Pull request checklist

Before opening a PR, confirm:

- [ ] The change is scoped and easy to review
- [ ] Tests pass locally
- [ ] Relevant documentation is updated
- [ ] No secrets or credentials were added
- [ ] The PR description explains the why, not just the what

## Need help?

Use the repository's issue tracker or discussions for questions. For architectural or larger changes, open an issue first so the work can be aligned before a large PR is created.

This project is a hobby project maintained in spare time, so response times may vary. However, the repository should be straightforward enough for contributors to work independently with the guidance above.
