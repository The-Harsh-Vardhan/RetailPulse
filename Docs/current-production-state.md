# RetailPulse Current Production State

## Release Posture
- Controlled internal pilot on the current Databricks Free Edition workspace
- Manual release path only
- Classifier and regression outputs remain in an `Experimental Insights` lane and are not operational decision drivers in this release

## Authoritative Release Record
| Item | Value |
| --- | --- |
| GitHub repo | `https://github.com/The-Harsh-Vardhan/RetailPulse` |
| Workspace host | `https://dbc-27b50dca-30e0.cloud.databricks.com/` |
| Bundle job name | `retailpulse_full_rebuild` |
| Job id | `61936309152043` |
| Latest successful run id | `432431661287387` |
| Latest successful run date | April 5, 2026 |
| Latest successful run URL | `https://dbc-27b50dca-30e0.cloud.databricks.com/?o=7474658274233226#job/61936309152043/run/432431661287387` |
| Dashboard name | `RetailPulse Demo Dashboard` |
| Dashboard id | `01f1305e8f1a115e8fb2b378bd4d8f99` |
| Dashboard workspace path | `/Users/bt23csd041@iiitn.ac.in/RetailPulse Demo Dashboard.lvdash.json` |
| Warehouse id | `2300565af9f2288c` |
| Dashboard published revision | `2026-04-05T05:08:33.719Z` |
| Report pack fallback | `notebooks/12_report_pack.py` |
| Screenshot source of truth | `assets/screenshots/` |

## Current Release Rules
- Release stays manual because Free Edition quota makes unattended rebuilds a bad production habit.
- Use the bundle job as the only release path.
- Run local validation, deploy, full rebuild, and smoke checks in that order.
- If classifier or regression output looks attractive, keep the language disciplined anyway. They remain `Experimental Insights`.
- No business recommendation, automation, or operational decision depends on classifier or regression output in this release.

## Current Next Milestone
- Boss-ready internal pilot freeze
- Immediate focus: release hardening, dashboard polish, and walkthrough stability
- Deferred until later: any new supervised-model training cycle

## Primary Demo Entry Points
- Boss brief: [boss-brief.md](boss-brief.md)
- Production runbook: [production-runbook.md](production-runbook.md)
- Release checklist: [release-checklist.md](release-checklist.md)
- Next-step roadmap: [Next Step Priority Plan.md](Next%20Step%20Priority%20Plan.md)
- Release smoke checks: [../sql/release_smoke_checks.sql](../sql/release_smoke_checks.sql)
- Latest successful Databricks run: the run URL above
- Dashboard access: open `RetailPulse Demo Dashboard` from Databricks AI/BI Dashboards or use the workspace path above
