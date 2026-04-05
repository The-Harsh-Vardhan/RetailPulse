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
| Draft update time | `2026-04-05T08:36:56.576Z` |
| Published revision | `2026-04-05T08:40:02.619Z` |
| Query source file | `sql/retailpulse_dashboard_queries.sql` |
| Fallback evidence hub | `notebooks/12_report_pack.py` |

## Published Dashboard V2 Layout
- `Executive Overview`
- `Order Behavior`
- `Recommendations And Segments`
- `Execution And Data Quality`
- `Experimental Insights And Performance`

## Canonical Dataset Count
- `21` inline dashboard datasets are currently encoded in the live Lakeview artifact.

## Canonical Saved Queries
- `dashboard_table_counts`
- `dashboard_kpi_summary`
- `dashboard_orders_by_day`
- `dashboard_department_totals`
- `dashboard_hourly_order_pattern`
- `dashboard_avg_basket_by_hour`
- `dashboard_daypart_basket`
- `dashboard_top_products`
- `dashboard_top_rules`
- `dashboard_available_seed_products`
- `dashboard_seed_recommendations`
- `dashboard_cluster_profiles`
- `dashboard_segment_sizes`
- `dashboard_cluster_k_scores`
- `dashboard_stream_health`
- `dashboard_stream_validation_detail`
- `dashboard_olap_validation_summary`
- `dashboard_optimize_comparison`
- `dashboard_optimize_raw_timings`
- `dashboard_exploratory_metrics`
- `dashboard_classifier_feature_importance`

## Interactive Controls
- Documented target control: `seed_product_name` parameter with default `Organic Raspberries`
- Current live API-authored dashboard behavior: the seed recommendation panel is pinned to `Organic Raspberries`
- Page-level `department` and `daypart` filters remain recommended UI enhancements if you want more interactivity later

## Screenshot Source Of Truth
- Preferred source: published AI/BI dashboard
- Current fallback/source-assisted evidence: `12_report_pack.py`, source notebooks, and live warehouse-backed renders
- Repo evidence location: `assets/screenshots/`
- Dashboard V2 screenshot set: `01_run_success.png` through `15_olap_validation.png`

## Operational Notes
- The dashboard is part of the current boss-ready release surface.
- The dashboard and the report pack tell the same five-section story because they are backed by the same report tables.
- The classifier and regression panel remains an `Experimental Insights` section, not an operational KPI block.
- If the live dashboard is republished again after layout changes, update the draft-update and published-revision timestamps here.
