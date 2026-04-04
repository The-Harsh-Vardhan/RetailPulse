# RetailPulse Evidence Pack

This document defines the fixed demo/submission evidence set for RetailPulse.

## Current Status
- The screenshot slots now exist under `assets/screenshots/`.
- The files currently use labeled placeholder images so the repo has a stable artifact shape.
- Before final submission, replace each placeholder with a real screenshot from the AI/BI dashboard or the notebook fallback after the latest full rerun.

## Preferred Capture Order
1. Capture the two AI/BI dashboard pages first.
2. Use `12_report_pack.py` and the source notebooks only for drill-down or fallback captures.
3. Keep the supervised-model screenshots, but present them as exploratory and retain the same disclaimer text used in the dashboard.

## Screenshot Set
| File | What it should show | Preferred source | Fallback source |
| --- | --- | --- | --- |
| `assets/screenshots/01_run_success.png` | Successful Databricks job run page | Databricks run page | same |
| `assets/screenshots/02_report_pack_counts.png` | KPI/table-count evidence | AI/BI dashboard counters | `12_report_pack.py` |
| `assets/screenshots/03_olap_outputs.png` | Department demand and timing visuals | AI/BI dashboard `Business Overview` | `05_olap.py` |
| `assets/screenshots/04_association_rules.png` | Top rules and recommendation example | AI/BI dashboard rules widget | `06_association_rules.py` |
| `assets/screenshots/05_cluster_profiles.png` | Customer segments | AI/BI dashboard segment widget | `07_clustering.py` |
| `assets/screenshots/06_classifier_metrics.png` | Exploratory classifier metrics | AI/BI dashboard metrics table | `08_classifier.py` |
| `assets/screenshots/07_regression_metrics.png` | Exploratory regression metrics | AI/BI dashboard metrics table | `09_regression.py` |
| `assets/screenshots/08_stream_validation.png` | Streaming quality and validation detail | AI/BI dashboard `Execution And Evidence` | `10_streaming_replay.py` |
| `assets/screenshots/09_optimize_summary.png` | Optimize comparison | AI/BI dashboard optimize widget | `11_optimize.py` |

## Report Tables
These report tables are expected after the full notebook sequence is rerun with the latest notebook source:

- `report_olap_cube`
- `report_olap_rollup`
- `report_olap_basket`
- `report_olap_validation`
- `report_classifier_metrics`
- `report_regression_metrics`
- `report_cluster_profiles`
- `report_stream_validation`
- `report_optimize_timings`
- `report_optimize_summary`

## Exact ML Disclaimer
Classifier and regression results are exploratory and useful for demo discussion, but not final predictive proof. Methodology tightening is still pending.

## Submission Rule
- Use the dashboard screenshots for the demo package wherever possible.
- Use the report tables plus `12_report_pack.py` for the written report and fallback evidence flow.
- Do not claim a screenshot exists unless the placeholder has been replaced with a real captured artifact.
