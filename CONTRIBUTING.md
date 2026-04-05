# Contributing to RetailPulse

Thank you for your interest in improving RetailPulse.

## Before You Start

1. Read [README.md](README.md) for project scope and current release truth.
2. Read [HOW_TO_USE_README.md](HOW_TO_USE_README.md) for setup and rerun guidance.
3. Check [Docs/release-checklist.md](Docs/release-checklist.md) before proposing release-facing changes.

## Contribution Scope

Contributions are welcome for:
- Documentation quality and clarity
- Test coverage improvements in `tests/`
- Pipeline robustness in `notebooks/` and `scripts/`
- Dashboard SQL quality in `sql/`

Please keep scope aligned with the current validated Instacart-first implementation.

## Local Workflow

1. Create a feature branch from `main`.
2. Make small, reviewable commits.
3. Run tests locally:
   - `pytest`
4. If your change touches SQL logic, also run smoke checks in:
   - `sql/release_smoke_checks.sql`
5. Update docs when behavior or outputs change.

## Pull Request Checklist

Use this checklist in your PR description:

- [ ] Change is scoped and easy to review
- [ ] Tests are added or updated where applicable
- [ ] Existing tests pass locally
- [ ] Documentation is updated (README/Docs)
- [ ] No secrets or credentials are committed
- [ ] Screenshots/evidence updated if dashboard-facing output changed

## Commit and PR Quality

- Prefer clear commit messages describing what changed and why.
- Include before/after evidence for analytics or dashboard changes.
- Call out any limitations or follow-up work explicitly.

## Security and Data

- Never commit secrets, tokens, or private credentials.
- Treat source data as potentially sensitive and avoid uploading private datasets to public remotes.
- See [SECURITY.md](SECURITY.md) for disclosure guidance.

## Questions

If something is unclear, open an issue describing:
- The current behavior
- The expected behavior
- Repro steps or sample inputs
