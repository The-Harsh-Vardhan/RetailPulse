# RetailPulse Databricks Dashboard UI Guide

This is the operator guide for building the live Databricks dashboard from the repo-tracked spec and canonical SQL queries.

Use this together with:
- [Dashboard Spec](databricks-dashboard-spec.md)
- [Canonical Dashboard Queries](../sql/retailpulse_dashboard_queries.sql)
- [Evidence Pack](evidence-pack.md)

## Goal
Upgrade the existing AI/BI dashboard `RetailPulse Demo Dashboard` to Dashboard V2 with five pages:
- `Executive Overview`
- `Order Behavior`
- `Recommendations And Segments`
- `Execution And Data Quality`
- `Experimental Insights And Performance`

If AI/BI dashboard authoring is unavailable in the workspace, fall back to the notebook dashboard built from `12_report_pack.py`.

## Before You Start
Confirm these prerequisites first:
- the full RetailPulse notebook flow has been rerun successfully
- the RetailPulse catalog and schema contain the latest report tables
- a usable Databricks SQL warehouse is running
- `sql/retailpulse_dashboard_queries.sql` is available locally for copy-paste

Recommended tables to spot-check before dashboard work:
- `report_olap_cube`
- `report_olap_rollup`
- `report_olap_basket`
- `report_olap_validation`
- `mart_association_rules`
- `report_cluster_profiles`
- `report_cluster_k_scores`
- `report_stream_validation`
- `report_optimize_summary`
- `report_optimize_timings`
- `report_classifier_metrics`
- `report_classifier_feature_importance`
- `report_regression_metrics`

## Exact ML Disclaimer
Use this exact text in the dashboard text widget and keep it unchanged:

> Classifier and regression results are exploratory and useful for demo discussion, but not final predictive proof. Methodology tightening is still pending.

## Part 1: Save The Canonical Queries
1. Open Databricks SQL.
2. Select the SQL warehouse you will use for the demo.
3. Set the current catalog and schema to the RetailPulse target.
4. Open a new SQL query tab.
5. Copy one query at a time from `sql/retailpulse_dashboard_queries.sql`.
6. Run it and confirm it returns data.
7. Save it with the exact query name shown in the SQL file.

Save the queries in this order:
1. `dashboard_table_counts`
2. `dashboard_kpi_summary`
3. `dashboard_orders_by_day`
4. `dashboard_department_totals`
5. `dashboard_hourly_order_pattern`
6. `dashboard_avg_basket_by_hour`
7. `dashboard_daypart_basket`
8. `dashboard_top_products`
9. `dashboard_top_rules`
10. `dashboard_available_seed_products`
11. `dashboard_seed_recommendations`
12. `dashboard_cluster_profiles`
13. `dashboard_segment_sizes`
14. `dashboard_cluster_k_scores`
15. `dashboard_stream_health`
16. `dashboard_stream_validation_detail`
17. `dashboard_olap_validation_summary`
18. `dashboard_optimize_comparison`
19. `dashboard_optimize_raw_timings`
20. `dashboard_exploratory_metrics`
21. `dashboard_classifier_feature_importance`

## Part 2: Upgrade The AI/BI Dashboard
1. Open the AI/BI dashboards area in Databricks SQL.
2. Open the existing dashboard `RetailPulse Demo Dashboard`.
3. Rename or reorder the current pages so the dashboard ends up with exactly five pages:
   - `Executive Overview`
   - `Order Behavior`
   - `Recommendations And Segments`
   - `Execution And Data Quality`
   - `Experimental Insights And Performance`
4. Remove stale widgets that only fit the old 2-page layout.
5. Keep the layout dense but readable. This is a reviewer-facing dashboard, not a minimal executive KPI board.

## Part 3: Add Dashboard Parameters And Filters
### Seed recommendation parameter
1. Create a parameter named `seed_product_name`.
2. Back it with the query `dashboard_available_seed_products`.
3. Use `seed_product_name` as the available field.
4. Set the default value to `Organic Raspberries`.
5. Confirm `dashboard_seed_recommendations` refreshes when the parameter changes.

### Page filters
Where AI/BI dashboards support them cleanly, add:
- `department` filter on pages that use department-level queries
- `daypart` filter on the `Order Behavior` page

Do not add filters that create empty or confusing widgets.

## Part 4: Build Page 1 - Executive Overview
Add these widgets in this order.

### 1. KPI Counters
- Source query: `dashboard_kpi_summary`
- Visual: 4 counter widgets
- Suggested labels:
  - `Total Orders`
  - `Total Items`
  - `Recommendation Rules`
  - `Validated Stream Groups`

### 2. Orders By Day
- Source query: `dashboard_orders_by_day`
- Visual: bar chart
- X-axis: `order_day`
- Y-axis: `order_count`
- Sort by `order_dow`

### 3. Department Demand
- Source query: `dashboard_department_totals`
- Visual: horizontal bar chart
- X-axis: `total_items`
- Y-axis: `department`
- Sort descending by `total_items`

### 4. Order Timing Pattern
- Source query: `dashboard_hourly_order_pattern`
- Visual: multi-line chart
- X-axis: `order_hour_of_day`
- Y-axis: `order_count`
- Series/grouping: `order_day`

### 5. Core Table Counts
- Source query: `dashboard_table_counts`
- Visual: compact table

## Part 5: Build Page 2 - Order Behavior
Add these widgets in this order.

### 1. Basket Size By Daypart
- Source query: `dashboard_daypart_basket`
- Visual: grouped bar chart
- Category axis: `department`
- Series: `daypart`
- Measure: `avg_basket_size`

### 2. Average Basket Size By Day
- Source query: `dashboard_orders_by_day`
- Visual: line chart
- X-axis: `order_day`
- Y-axis: `avg_basket_size`
- Sort by `order_dow`

### 3. Average Basket Size By Hour
- Source query: `dashboard_avg_basket_by_hour`
- Visual: line chart
- X-axis: `order_hour_of_day`
- Y-axis: `avg_basket_size`

### 4. Top Products
- Source query: `dashboard_top_products`
- Visual: horizontal bar chart
- X-axis: `items_seen`
- Y-axis: `product_name`
- Sort descending by `items_seen`

## Part 6: Build Page 3 - Recommendations And Segments
Add these widgets in this order.

### 1. Top Recommendation Rules
- Source query: `dashboard_top_rules`
- Visual: sortable table
- Default sort: `lift` descending, then `confidence` descending

### 2. Seed Recommendations
- Source query: `dashboard_seed_recommendations`
- Visual: table
- Ensure this query is bound to `seed_product_name`

### 3. Customer Segment Profiles
- Source query: `dashboard_cluster_profiles`
- Visual: table

### 4. Segment Sizes
- Source query: `dashboard_segment_sizes`
- Visual: bar chart
- X-axis: `users_in_cluster`
- Y-axis: `segment_name`

### 5. Cluster Model Selection
- Source query: `dashboard_cluster_k_scores`
- Visual: bar chart
- X-axis: `cluster_k`
- Y-axis: `silhouette_score`

## Part 7: Build Page 4 - Execution And Data Quality
Add these widgets in this order.

### 1. Streaming Quality
- Source query: `dashboard_stream_health`
- Visual: 3 counter widgets
- Show:
  - `checked_groups`
  - `matched_groups`
  - `mismatch_groups`
- Goal: `mismatch_groups = 0`

### 2. Streaming Validation Detail
- Source query: `dashboard_stream_validation_detail`
- Visual: table
- Keep the pass/fail column visible

### 3. OLAP Validation Summary
- Source query: `dashboard_olap_validation_summary`
- Visual: counters or compact summary table
- Keep `mismatched_groups` and `max_item_gap` visible

### 4. Release Signoff Rule
- Add a text widget stating that release signoff fails if stream mismatches are non-zero or report tables are unreadable.

## Part 8: Build Page 5 - Experimental Insights And Performance
Add these widgets in this order.

### 1. Exploratory Metrics Disclaimer
- Add a text widget at the top of the page
- Paste the exact disclaimer text from the section above

### 2. Exploratory Model Metrics
- Source query: `dashboard_exploratory_metrics`
- Visual: table only
- Keep both classifier and regression rows visible

### 3. Classifier Feature Importance
- Source query: `dashboard_classifier_feature_importance`
- Visual: horizontal bar chart
- X-axis: `importance`
- Y-axis: `feature_name`

### 4. Optimize Comparison
- Source query: `dashboard_optimize_comparison`
- Visual: grouped bar chart
- Category axis: `query_name`
- Measures:
  - `before_optimize`
  - `after_optimize`

### 5. Raw Optimize Timings
- Source query: `dashboard_optimize_raw_timings`
- Visual: table or grouped bar chart

## Part 9: Build The Notebook Dashboard Fallback
If AI/BI dashboards are unavailable in the workspace:
1. Open `12_report_pack.py` in Databricks.
2. Run the notebook.
3. Create a notebook dashboard from cell outputs.
4. Add outputs in this order:
   1. Executive Overview
   2. Order Behavior
   3. Recommendations And Segments
   4. Execution And Data Quality
   5. Experimental Insights And Performance
5. Keep the markdown intro and the exploratory ML disclaimer visible at the top.

## Part 10: Screenshot Capture
After the upgraded dashboard loads correctly, refresh the screenshot pack in this order:
- `01_run_success.png`
- `02_report_pack_counts.png`
- `03_olap_outputs.png`
- `04_association_rules.png`
- `05_cluster_profiles.png`
- `06_classifier_metrics.png`
- `07_regression_metrics.png`
- `08_stream_validation.png`
- `09_optimize_summary.png`
- `10_orders_by_day.png`
- `11_top_products.png`
- `12_seed_recommendations.png`
- `13_cluster_k_scores.png`
- `14_classifier_feature_importance.png`
- `15_olap_validation.png`

Use the AI/BI dashboard as the preferred source. Use the notebook fallback only if a dashboard panel fails or a drill-down is clearer in notebook form.

## Final Readiness Check
Before the demo, confirm:
- all Dashboard V2 queries run on the chosen SQL warehouse
- all five pages load without broken widgets
- the `seed_product_name` parameter works with default `Organic Raspberries`
- any useful `department` and `daypart` filters are working
- the exploratory ML disclaimer is visible only on the exploratory page
- `report_stream_validation` shows zero mismatches
- the OLAP validation summary shows no mismatches
- the screenshot set has been refreshed for Dashboard V2