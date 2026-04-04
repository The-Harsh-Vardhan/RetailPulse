# RetailPulse Databricks Dashboard Spec

This file is the repo-tracked specification for the Databricks visualization layer.

## Goal
Build one polished AI/BI dashboard for the live demo and keep `12_report_pack.py` as the notebook fallback if the dashboard is unavailable or a panel needs drill-down.

## Delivery Surface
- Primary: AI/BI dashboard named `RetailPulse Demo Dashboard`
- Fallback: notebook dashboard built from `12_report_pack.py`
- SQL source file: `sql/retailpulse_dashboard_queries.sql`

## Authoring Rules
- Use AI/BI dashboards, not legacy SQL dashboards.
- Use manual dashboard authoring in the Databricks UI for v1.
- Set the current catalog and schema to the RetailPulse target before saving the canonical queries.
- Use only existing RetailPulse tables and marts. Do not create dashboard-specific ETL tables.

## Exact ML Disclaimer Text
Classifier and regression results are exploratory and useful for demo discussion, but not final predictive proof. Methodology tightening is still pending.

Use this exact text:
- as a text widget above the exploratory metrics table in the AI/BI dashboard
- in the notebook fallback intro inside `12_report_pack.py`

## AI/BI Dashboard Layout

### Page 1: Business Overview
| Widget title | Query | Visualization |
| --- | --- | --- |
| KPI Counters | `dashboard_kpi_summary` | 4 counter widgets |
| Department Demand | `dashboard_department_totals` | Horizontal bar chart |
| Order Timing Pattern | `dashboard_hourly_order_pattern` | Line chart |
| Basket Size By Daypart | `dashboard_daypart_basket` | Grouped bar chart |
| Top Recommendation Rules | `dashboard_top_rules` | Sortable table |
| Customer Segments | `dashboard_cluster_profiles` | Table |

### Page 2: Execution And Evidence
| Widget title | Query | Visualization |
| --- | --- | --- |
| Streaming Quality | `dashboard_stream_health` | 2 counter widgets |
| Streaming Validation Detail | `dashboard_stream_validation_detail` | Table |
| Optimize Comparison | `dashboard_optimize_comparison` | Grouped bar chart |
| Exploratory Model Metrics | `dashboard_exploratory_metrics` | Table |
| Exploratory Metrics Disclaimer | text widget | Text |

## Notebook Dashboard Fallback
Use `12_report_pack.py` as the only notebook dashboard source.

If the AI/BI dashboard is unavailable, build the notebook dashboard in this order:
1. table counts
2. OLAP cube output
3. OLAP rollup output
4. OLAP basket output
5. top rules table
6. cluster profiles table
7. stream validation table
8. optimize summary table
9. classifier metrics table
10. regression metrics table

## Manual Build Steps In Databricks
1. Open Databricks SQL and select the RetailPulse SQL warehouse.
2. Set the current catalog and schema to the RetailPulse target.
3. Create and save the ten canonical queries from `sql/retailpulse_dashboard_queries.sql`.
4. Create a new AI/BI dashboard named `RetailPulse Demo Dashboard`.
5. Add two pages named `Business Overview` and `Execution And Evidence`.
6. Add widgets in the exact order described above.
7. Add the exact ML disclaimer text above the exploratory metrics table.
8. Validate that every widget loads and that no legacy dashboard feature is used.
9. If AI/BI dashboard authoring is unavailable in the workspace, open `12_report_pack.py` and build the notebook dashboard from the same output order.

## Screenshot Capture Checklist
Tie the final dashboard or notebook captures to these repo files:
- `assets/screenshots/01_run_success.png`
- `assets/screenshots/02_report_pack_counts.png`
- `assets/screenshots/03_olap_outputs.png`
- `assets/screenshots/04_association_rules.png`
- `assets/screenshots/05_cluster_profiles.png`
- `assets/screenshots/06_classifier_metrics.png`
- `assets/screenshots/07_regression_metrics.png`
- `assets/screenshots/08_stream_validation.png`
- `assets/screenshots/09_optimize_summary.png`

## Acceptance Check
- All ten canonical queries save successfully.
- Every AI/BI widget loads on the selected SQL warehouse.
- The ML disclaimer appears on both dashboard paths.
- The fallback notebook still reads cleanly as a single evidence hub.
- Placeholder screenshots are replaced with real captures before final submission.
