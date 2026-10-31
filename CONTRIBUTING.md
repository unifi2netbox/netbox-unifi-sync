# Contributing to netbox-unifi-sync

Thanks for helping improve the project.

This repository is maintained in spare time, but the goal is to make it easy for new contributors to get started without requiring manual setup from the maintainer for each contribution.

## AI and helper contribution rules

These rules apply to AI-assisted work, contributors, and any helper or automation used in the repository.

1. Keep changes focused.
   - Avoid large refactors or unrelated cleanup.
   - One issue or feature should usually become one small, reviewable change.
   - If a change is outside scope, leave it out.

2. Understand the problem before changing code.
   - Read the relevant code, tests, and documentation before editing behavior.
   - Do not assume how NetBox or UniFi should behave without checking.
   - If something is unclear, state the uncertainty instead of guessing.

3. Use AI as a support tool, not an authority.
   - AI may help draft code, tests, documentation, or fixes.
   - A human must review all final changes before merging.
   - No change should be accepted solely because an AI generated it.

4. Be transparent about uncertainty.
   - If a solution is not fully validated, say so clearly.
   - Prefer "I am not certain about this part" over making a risky assumption.
   - Any NetBox- or UniFi-specific behavior should be checked before merge.

5. Run the relevant validation.
   - Run the smallest relevant lint and test commands for the changed behavior.
   - Do not rely only on code review or intuition.
   - If the change affects plugin logic or integration behavior, prefer local validation when possible.

6. Respect the project scope and architecture.
   - This project is a NetBox plugin for UniFi synchronization.
   - Changes must stay aligned with the existing architecture and NetBox compatibility.
   - Avoid unnecessary dependencies and unrelated complexity.

7. Do not introduce secrets or sensitive data.
   - Never include credentials, tokens, API keys, local environment details, or sensitive logs.
   - Use example values only in docs and tests.

8. Update documentation when behavior changes.
   - If a change affects users, configuration, or workflows, update the relevant docs.
   - Documentation is part of the contribution, not an optional extra.

9. Be careful with NetBox and UniFi integration changes.
   - NetBox should be treated as the source of truth.
   - Sync behavior must be predictable, safe, and reviewable.
   - Avoid changes that could silently alter live data without clear justification.

10. Keep pull requests readable.
    - PR descriptions should explain:
      - the problem
      - the change
      - why it was needed
      - how it was validated
    - Good PRs should be easy to review.

11. Do not let helpers take over the work.
    - Helpers should assist, not replace the human contributor.
    - AI should support debugging, drafting, testing, and documentation—not bypass understanding.
    - New contributors should still be able to follow the workflow without constant hand-holding.

12. Respect maintenance constraints.
    - This is a hobby project maintained in spare time.
    - Contributions should be clear, small, and easy to validate.
    - The project should be approachable for contributors without requiring long manual onboarding.

13. Explain complex solutions.
    - If a fix is non-trivial, the reasoning should be clear.
    - "It works" is not enough; the context and intent should be understandable.

14. Link issues and PRs where relevant.
    - If a change addresses an issue, reference it.
    - For larger work, open or reference an issue or discussion before starting.

15. No hidden or unexplained work.
    - AI-generated or assistant-assisted changes must remain understandable and reviewable.
    - No magic fixes, no hidden assumptions, and no unexplained large edits.

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
