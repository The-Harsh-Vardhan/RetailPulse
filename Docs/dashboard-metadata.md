# RetailPulse Dashboard Metadata

## Published Dashboard
| Field | Value |
| --- | --- |
| Dashboard name | `RetailPulse Demo Dashboard` |
| Dashboard id | `01f1305e8f1a115e8fb2b378bd4d8f99` |
| Lifecycle state | `ACTIVE` |
| Published status | `Published` |
| Dashboard workspace path | `/Users/bt23csd041@iiitn.ac.in/RetailPulse Demo Dashboard.lvdash.json` |
| Parent path | `/Users/bt23csd041@iiitn.ac.in` |
| Warehouse id | `2300565af9f2288c` |
| Draft create time | `2026-04-04T19:43:31.147Z` |
| Draft update time | `2026-04-05T05:06:08.680Z` |
| Published revision | `2026-04-05T05:08:33.719Z` |
| Query source file | `sql/retailpulse_dashboard_queries.sql` |
| Fallback evidence hub | `notebooks/12_report_pack.py` |

## Pages
- `Business Overview`
- `Execution And Evidence`

## Canonical Saved Queries
- `dashboard_kpi_summary`
- `dashboard_department_totals`
- `dashboard_hourly_order_pattern`
- `dashboard_daypart_basket`
- `dashboard_top_rules`
- `dashboard_cluster_profiles`
- `dashboard_stream_health`
- `dashboard_stream_validation_detail`
- `dashboard_optimize_comparison`
- `dashboard_exploratory_metrics`

## Screenshot Source Of Truth
- Preferred source: published AI/BI dashboard
- Fallback source: `12_report_pack.py` and the source notebooks
- Repo evidence location: `assets/screenshots/`

## Operational Notes
- The dashboard is part of the current boss-ready release surface.
- The dashboard and the report pack must tell the same story because they are backed by the same report tables.
- The classifier and regression panel remains an `Experimental Insights` section, not an operational KPI block.
