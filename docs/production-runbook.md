# RetailPulse Production Runbook

## Purpose
Use this runbook for a controlled internal release on the current Databricks Free Edition workspace.

This is not a customer-grade SLA deployment. It is a boss-reviewed internal pilot with manual release control.

## Release Inputs
- Repo root checked out locally
- Databricks CLI authenticated
- Current production state reviewed in [current-production-state.md](current-production-state.md)
- Boss brief reviewed in [boss-brief.md](boss-brief.md)
- Release checklist open in [release-checklist.md](release-checklist.md)

## Release Steps
### 1. Run local gates
```powershell
python -m unittest -q tests.test_sample_instacart tests.test_split_stream_replay_batches tests.test_export_databricks_source_to_ipynb
$files = @((Get-ChildItem notebooks -Filter *.py).FullName) + @((Get-ChildItem scripts -Filter *.py).FullName) + @((Get-ChildItem tests -Filter *.py).FullName)
python -m py_compile $files
python scripts/export_databricks_source_to_ipynb.py --check
```

### 2. Validate and deploy the bundle
```powershell
databricks bundle validate -t dev
databricks bundle deploy -t dev
```

### 3. Run the full rebuild
```powershell
databricks bundle run retailpulse_full_rebuild -t dev
```

### 4. Record the new run
- Open the Databricks run page.
- Confirm the run terminated `SUCCESS`.
- Update [current-production-state.md](current-production-state.md) only if the new run becomes the latest release record.

### 5. Run workspace smoke checks
- Open the SQL warehouse `2300565af9f2288c`.
- Run [../sql/release_smoke_checks.sql](../sql/release_smoke_checks.sql) in order.
- Do not sign off the release unless:
  - required report tables are present
  - required report tables are readable
  - `mart_association_rules` is non-empty
  - `mismatch_groups = 0`

### 6. Confirm dashboard and evidence
- Confirm `RetailPulse Demo Dashboard` is still published.
- Confirm `assets/screenshots/` still matches the current live story.
- Keep `12_report_pack.py` available as the fallback evidence hub.
- Spot-check dashboard polish before boss review:
  - business labels are clear
  - `Experimental Insights` are visibly separated
  - any useful filters still work
  - no panel depends on notebook context to make sense

### 7. Rehearse the boss walkthrough
Use this order:
1. `Executive Overview`
2. `Order Behavior`
3. `Recommendations And Segments`
4. `Execution And Data Quality`
5. `Experimental Insights And Performance`
6. `12_report_pack.py` fallback
7. known constraints and next milestone

## Rollback
### Trigger rollback if any of these happen
- bundle validation fails
- full rebuild run fails
- smoke checks fail
- dashboard is unavailable and the report-pack fallback is also broken
- docs or screenshots contradict the live workspace state

### Rollback steps
1. Stop claiming a new release candidate.
2. Keep the previously validated run and published dashboard as the active boss-facing baseline.
3. Revert the repo to the last validated commit on the release branch.
4. Redeploy the reverted bundle.
5. Rerun `retailpulse_full_rebuild`.
6. Re-run the smoke checks.
7. Update the boss brief so it reflects the reverted truth, not the failed attempt.

## Non-Operational ML Rule
- Classifier and regression remain in the product surface for technical discussion.
- No business recommendation, automation, or production decision depends on them in this release.
- If a boss asks whether they are production-grade, the correct answer is no.

## Current Priority Rule
- Do not start a new modeling cycle until release quality, visualization polish, and walkthrough stability are in place.
- If a next-phase decision is needed, use `Docs/Next Step Priority Plan.md`.
