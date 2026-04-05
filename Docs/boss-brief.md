# RetailPulse Boss Brief

## What Is Live
- A full bronze, silver, and gold Databricks pipeline over the sampled Instacart dataset
- Persisted report tables for OLAP, recommendations, clustering, streaming validation, optimization, and the `Experimental Insights` models
- A published AI/BI dashboard: `RetailPulse Demo Dashboard`
- A notebook fallback evidence hub: `12_report_pack.py`
- A packaged screenshot set under `assets/screenshots/`

## What Is Validated
- Latest successful rebuild run: `432431661287387`
- Job id: `61936309152043`
- Streaming replay validation: `0` mismatches across `158` checked groups
- Association rules: `49` non-trivial rules
- Dashboard is published and backed by the same report tables used by the fallback notebook

## What Is Experimental
- The classifier and regression remain in the release as `Experimental Insights`
- They are useful for technical discussion and boss review
- They are not production-grade predictive proof yet
- No business recommendation, automation, or operational decision depends on them in this release

## Known Constraints
- Databricks Free Edition is serverless-only and quota-limited
- Instacart has no raw price fields and no absolute calendar dates
- Recommendation logic is pairwise association rules, not full FP-growth
- `OPTIMIZE` completed correctly, but the benchmark was slower on this sample size

## Recommended Boss Walkthrough
1. Business Overview page in the AI/BI dashboard
2. Execution And Evidence page in the AI/BI dashboard
3. `12_report_pack.py` as the fallback and evidence hub
4. Known constraints, Experimental Insights boundary, and next milestone

## Next Milestone
- Keep this release stable as an internal pilot
- Redesign classifier and regression with leakage-safe methodology before making stronger predictive claims
- Migrate to a paid Databricks workspace if this needs true production isolation, stronger operational controls, or customer-facing reliability
