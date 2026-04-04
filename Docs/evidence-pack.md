# RetailPulse Evidence Pack

This document defines the fixed demo/submission evidence set for RetailPulse.

## Current Status
- The screenshot slots now exist under `assets/screenshots/`.
- The files currently use labeled placeholder images so the repo has a stable artifact shape.
- Before final submission, replace each placeholder with a real screenshot from the validated Databricks run or the final rerun that includes the OLAP report tables.

## Screenshot Set
| File | What it should show | Source |
| --- | --- | --- |
| `assets/screenshots/01_run_success.png` | Successful Databricks job run page | Databricks job run URL from README |
| `assets/screenshots/02_report_pack_counts.png` | Table-count output | `12_report_pack.py` |
| `assets/screenshots/03_olap_outputs.png` | OLAP outputs | `05_olap.py` |
| `assets/screenshots/04_association_rules.png` | Top rules and recommendation example | `06_association_rules.py` |
| `assets/screenshots/05_cluster_profiles.png` | Cluster profile table | `07_clustering.py` |
| `assets/screenshots/06_classifier_metrics.png` | Classifier metrics | `08_classifier.py` |
| `assets/screenshots/07_regression_metrics.png` | Regression metrics | `09_regression.py` |
| `assets/screenshots/08_stream_validation.png` | Stream-vs-batch validation | `10_streaming_replay.py` |
| `assets/screenshots/09_optimize_summary.png` | Optimize timing summary | `11_optimize.py` |

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

## Submission Rule
- Use the screenshot set for the demo package.
- Use the report tables plus `12_report_pack.py` for the written report.
- Do not claim a screenshot exists unless the placeholder has been replaced with a real captured artifact.
