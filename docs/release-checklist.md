# RetailPulse Release Checklist

## Pre-Release
- [ ] `README.md` reflects the April 5 validated run and the published dashboard
- [ ] `Docs/Executive Summary.md` reflects the current internal-pilot posture
- [ ] Classifier and regression are described as `Experimental Insights`, not operational KPIs
- [ ] [current-production-state.md](current-production-state.md) matches the live workspace
- [ ] [dashboard-metadata.md](dashboard-metadata.md) matches the live dashboard
- [ ] Boss brief is current and internally consistent

## Local Gates
- [ ] `python -m unittest -q tests.test_sample_instacart tests.test_split_stream_replay_batches tests.test_export_databricks_source_to_ipynb`
- [ ] PowerShell-safe compile pass completed for `notebooks/`, `scripts/`, and `tests/`
- [ ] `python scripts/export_databricks_source_to_ipynb.py --check`

## Release Execution
- [ ] `databricks bundle validate -t dev`
- [ ] `databricks bundle deploy -t dev`
- [ ] `databricks bundle run retailpulse_full_rebuild -t dev`
- [ ] Latest run terminated `SUCCESS`

## Smoke Checks
- [ ] [../sql/release_smoke_checks.sql](../sql/release_smoke_checks.sql) executed on warehouse `2300565af9f2288c`
- [ ] Required report tables are present
- [ ] Required report tables are readable and non-empty
- [ ] `mart_association_rules` is non-empty
- [ ] `report_stream_validation` returns `mismatch_groups = 0`
- [ ] Published dashboard metadata resolves cleanly

## Evidence And Walkthrough
- [ ] `assets/screenshots/` matches the current live workspace story
- [ ] `RetailPulse Demo Dashboard` loads for the walkthrough
- [ ] `12_report_pack.py` is open as the fallback evidence hub
- [ ] Boss walkthrough has been rehearsed in the fixed order

## Dashboard Polish Gates
- [ ] Business-facing widgets use clear labels instead of notebook-style phrasing
- [ ] Table-heavy panels have been reduced where a chart or counter is clearer
- [ ] Non-obvious charts include short interpretation text
- [ ] `Experimental Insights` are visually separate from release-safe KPIs
- [ ] Any useful page-level filters are present and working

## GitHub Showcase Pass
- [ ] `README.md` opens with a fast reviewer path and visible proof assets
- [ ] Featured screenshots in the README match the live workspace story
- [ ] `Docs/showcase-summary.md` matches the README and current production state
- [ ] `Docs/RetailPulse Handbook.md` is linked and up to date
- [ ] `Docs/Next Step Priority Plan.md` reflects the current milestone and does not imply a premature ML cycle

## Final Signoff Rule
- [ ] No document, screenshot, or spoken claim contradicts the live workspace
- [ ] No business recommendation, automation, or production decision depends on classifier or regression output
