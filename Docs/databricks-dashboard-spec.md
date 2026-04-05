# RetailPulse Databricks Dashboard Spec

This file is the repo-tracked specification for the Dashboard V2 visualization layer.

## Goal
Build one rich AI/BI dashboard for the live demo and GitHub showcase, and keep `12_report_pack.py` as the notebook fallback if the dashboard is unavailable or a panel needs drill-down.

## Delivery Surface
- Primary: AI/BI dashboard named `RetailPulse Demo Dashboard`
- Fallback: notebook dashboard built from `12_report_pack.py`
- SQL source file: `sql/retailpulse_dashboard_queries.sql`

## Authoring Rules
- Use AI/BI dashboards, not legacy SQL dashboards.
- Reuse the existing published dashboard instead of creating a second one.
- Set the current catalog and schema to the RetailPulse target before saving the canonical queries.
- Use only existing RetailPulse tables and marts, plus the two added evidence tables:
  - `report_cluster_k_scores`
  - `report_classifier_feature_importance`
- Keep the exploratory-ML disclaimer text unchanged.

## Exact ML Disclaimer Text
Classifier and regression results are exploratory and useful for demo discussion, but not final predictive proof. Methodology tightening is still pending.

Use this exact text:
- as a text widget above the exploratory metrics table in the AI/BI dashboard
- in the notebook fallback intro inside `12_report_pack.py`

## AI/BI Dashboard Layout

### Page 1: Executive Overview
| Widget title | Query | Visualization |
| --- | --- | --- |
| KPI Counters | `dashboard_kpi_summary` | 4 counter widgets |
| Orders By Day | `dashboard_orders_by_day` | Bar chart |
| Department Demand | `dashboard_department_totals` | Horizontal bar chart |
| Order Timing Pattern | `dashboard_hourly_order_pattern` | Multi-line chart |
| Core Table Counts | `dashboard_table_counts` | Compact table |

### Page 2: Order Behavior
| Widget title | Query | Visualization |
| --- | --- | --- |
| Basket Size By Daypart | `dashboard_daypart_basket` | Grouped bar chart |
| Average Basket Size By Day | `dashboard_orders_by_day` | Line chart |
| Average Basket Size By Hour | `dashboard_avg_basket_by_hour` | Line chart |
| Top Products | `dashboard_top_products` | Horizontal bar chart |

Page filters where supported:
- `department`
- `daypart`

### Page 3: Recommendations And Segments
| Widget title | Query | Visualization |
| --- | --- | --- |
| Top Recommendation Rules | `dashboard_top_rules` | Sortable table |
| Seed Recommendations | `dashboard_seed_recommendations` | Table |
| Customer Segment Profiles | `dashboard_cluster_profiles` | Table |
| Segment Sizes | `dashboard_segment_sizes` | Bar chart |
| Cluster Model Selection | `dashboard_cluster_k_scores` | Bar chart |

Dashboard parameter:
- name: `seed_product_name`
- source query: `dashboard_available_seed_products`
- default value: `Organic Raspberries`

### Page 4: Execution And Data Quality
| Widget title | Query | Visualization |
| --- | --- | --- |
| Streaming Quality | `dashboard_stream_health` | 3 counter widgets |
| Streaming Validation Detail | `dashboard_stream_validation_detail` | Table |
| OLAP Validation Summary | `dashboard_olap_validation_summary` | Compact summary table or counters |

Add a text widget stating:
- release signoff fails if stream mismatches are non-zero or report tables are unreadable

### Page 5: Experimental Insights And Performance
| Widget title | Query | Visualization |
| --- | --- | --- |
| Exploratory Metrics Disclaimer | text widget | Text |
| Exploratory Model Metrics | `dashboard_exploratory_metrics` | Table |
| Classifier Feature Importance | `dashboard_classifier_feature_importance` | Horizontal bar chart |
| Optimize Comparison | `dashboard_optimize_comparison` | Grouped bar chart |
| Raw Optimize Timings | `dashboard_optimize_raw_timings` | Table or grouped bar chart |

Keep this page visually separate from release-safe KPI pages.

## Canonical Saved Queries
### Existing queries retained
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

### New queries for Dashboard V2
- `dashboard_table_counts`
- `dashboard_orders_by_day`
- `dashboard_avg_basket_by_hour`
- `dashboard_top_products`
- `dashboard_available_seed_products`
- `dashboard_seed_recommendations`
- `dashboard_segment_sizes`
- `dashboard_cluster_k_scores`
- `dashboard_olap_validation_summary`
- `dashboard_classifier_feature_importance`
- `dashboard_optimize_raw_timings`

## Notebook Dashboard Fallback
Use `12_report_pack.py` as the only notebook dashboard source.

If the AI/BI dashboard is unavailable, the notebook fallback should mirror the same five sections:
1. Executive Overview
2. Order Behavior
3. Recommendations And Segments
4. Execution And Data Quality
5. Experimental Insights And Performance

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
- `assets/screenshots/10_orders_by_day.png`
- `assets/screenshots/11_top_products.png`
- `assets/screenshots/12_seed_recommendations.png`
- `assets/screenshots/13_cluster_k_scores.png`
- `assets/screenshots/14_classifier_feature_importance.png`
- `assets/screenshots/15_olap_validation.png`

## Acceptance Check
- All canonical queries save successfully.
- Every AI/BI widget loads on the selected SQL warehouse.
- The `seed_product_name` parameter resolves and defaults to `Organic Raspberries`.
- The exploratory-ML disclaimer appears only on the exploratory page and stays unchanged.
- The fallback notebook reads cleanly as the same five-section evidence hub.
- The screenshot set is updated to reflect Dashboard V2.