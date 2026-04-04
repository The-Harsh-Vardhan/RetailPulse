# RetailPulse Databricks Dashboard UI Guide

This is the operator guide for building the live Databricks dashboard from the repo-tracked spec and canonical SQL queries.

Use this together with:
- [Dashboard Spec](databricks-dashboard-spec.md)
- [Canonical Dashboard Queries](../sql/retailpulse_dashboard_queries.sql)
- [Evidence Pack](evidence-pack.md)

## Goal
Create one AI/BI dashboard named `RetailPulse Demo Dashboard` with two pages:
- `Business Overview`
- `Execution And Evidence`

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
- `mart_association_rules`
- `report_cluster_profiles`
- `report_stream_validation`
- `report_optimize_summary`
- `report_classifier_metrics`
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

Save these ten queries exactly:
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

## Part 2: Create The AI/BI Dashboard
1. Open the AI/BI dashboards area in Databricks SQL.
2. Create a new dashboard.
3. Name it `RetailPulse Demo Dashboard`.
4. Add two pages:
   - `Business Overview`
   - `Execution And Evidence`
5. Keep the layout simple and readable. This is a project demo, not a design contest.

## Part 3: Build Page 1 - Business Overview
Add these widgets in this order.

### 1. KPI Counters
- Source query: `dashboard_kpi_summary`
- Visual: 4 counter widgets
- Suggested labels:
  - `Total Orders`
  - `Total Items`
  - `Recommendation Rules`
  - `Validated Stream Groups`

### 2. Department Demand
- Source query: `dashboard_department_totals`
- Visual: horizontal bar chart
- X-axis: `total_items`
- Y-axis: `department`
- Sort: descending by `total_items`

### 3. Order Timing Pattern
- Source query: `dashboard_hourly_order_pattern`
- Visual: line chart
- X-axis: `order_hour_of_day`
- Y-axis: `order_count`
- Series/grouping: `order_day`

### 4. Basket Size By Daypart
- Source query: `dashboard_daypart_basket`
- Visual: grouped bar chart
- Category axis: `department`
- Series: `daypart`
- Measure: `avg_basket_size`

### 5. Top Recommendation Rules
- Source query: `dashboard_top_rules`
- Visual: table
- Visible columns:
  - `antecedent_product_name`
  - `consequent_product_name`
  - `pair_order_count`
  - `support`
  - `confidence`
  - `lift`
- Default sort: `lift` descending, then `confidence` descending

### 6. Customer Segments
- Source query: `dashboard_cluster_profiles`
- Visual: table
- Visible columns:
  - `cluster_id`
  - `segment_name`
  - `users_in_cluster`
  - `avg_total_orders`
  - `avg_basket_size`
  - `avg_reordered_item_rate`
  - `avg_days_since_prior_order`

## Part 4: Build Page 2 - Execution And Evidence
Add these widgets in this order.

### 1. Streaming Quality
- Source query: `dashboard_stream_health`
- Visual: 2 counter widgets
- Show:
  - `checked_groups`
  - `mismatch_groups`
- Goal: `mismatch_groups = 0`

### 2. Streaming Validation Detail
- Source query: `dashboard_stream_validation_detail`
- Visual: table
- Keep the pass/fail column visible so reviewers can see the validation logic

### 3. Optimize Comparison
- Source query: `dashboard_optimize_comparison`
- Visual: grouped bar chart
- Category axis: `query_name`
- Measures:
  - `before_optimize`
  - `after_optimize`

### 4. Exploratory Metrics Disclaimer
- Add a text widget directly above the metrics table
- Paste the exact disclaimer text from the section above

### 5. Exploratory Model Metrics
- Source query: `dashboard_exploratory_metrics`
- Visual: table only
- Keep both classifier and regression rows visible
- Do not present this as final predictive proof

## Part 5: Build The Notebook Dashboard Fallback
If AI/BI dashboards are unavailable in the workspace:
1. Open `12_report_pack.py` in Databricks.
2. Run the notebook.
3. Create a notebook dashboard from cell outputs.
4. Add outputs in this order:
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
5. Keep the markdown intro and the exploratory ML disclaimer visible at the top.

## Part 6: Screenshot Capture
After the dashboard loads correctly, replace the placeholder images in `assets/screenshots/` with real captures in this order:
- `01_run_success.png`
- `02_report_pack_counts.png`
- `03_olap_outputs.png`
- `04_association_rules.png`
- `05_cluster_profiles.png`
- `06_classifier_metrics.png`
- `07_regression_metrics.png`
- `08_stream_validation.png`
- `09_optimize_summary.png`

Use the AI/BI dashboard as the preferred source. Use the notebook fallback only if a dashboard panel fails or a drill-down is clearer in notebook form.

## Final Readiness Check
Before the demo, confirm:
- all ten canonical queries run on the chosen SQL warehouse
- both dashboard pages load without broken widgets
- the exploratory ML disclaimer is visible
- `report_stream_validation` shows zero mismatches
- the optimize comparison reflects the real benchmark result
- placeholder screenshots have been replaced with real captures
