# RetailPulse Evidence Pack

This document defines the fixed demo/submission evidence set for RetailPulse Dashboard V2.

## Current Status
- The screenshot slots live under `assets/screenshots/`.
- Files `01` through `09` already exist from the latest validated Databricks run and live SQL result sets.
- Dashboard V2 adds six more screenshot slots for richer GitHub and review coverage.
- Files 10 through 15 now exist as warehouse-backed renders generated from the latest live dashboard data refresh.
- If you later capture cleaner UI-native screenshots from the AI/BI dashboard, keep the same filenames and replace the current warehouse-backed renders in place.

## Preferred Capture Order
1. Capture the AI/BI dashboard pages first.
2. Use `12_report_pack.py` and the source notebooks only for drill-down or fallback captures.
3. Keep the supervised-model screenshots, but present them as exploratory and retain the same disclaimer text used in the dashboard.
4. Lead GitHub and boss-facing packaging with business overview, recommendation proof, and data-quality proof before exploratory model visuals.

## Screenshot Set
| File | What it should show | Preferred source | Fallback source |
| --- | --- | --- | --- |
| `assets/screenshots/01_run_success.png` | Successful Databricks job run page | Databricks run page | same |
| `assets/screenshots/02_report_pack_counts.png` | KPI/table-count evidence | Dashboard V2 `Executive Overview` | `12_report_pack.py` |
| `assets/screenshots/03_olap_outputs.png` | Department demand and timing visuals | Dashboard V2 `Executive Overview` | `05_olap.py` |
| `assets/screenshots/04_association_rules.png` | Top rules and recommendation example | Dashboard V2 `Recommendations And Segments` | `06_association_rules.py` |
| `assets/screenshots/05_cluster_profiles.png` | Customer segments | Dashboard V2 `Recommendations And Segments` | `07_clustering.py` |
| `assets/screenshots/06_classifier_metrics.png` | Exploratory classifier metrics | Dashboard V2 `Experimental Insights And Performance` | `08_classifier.py` |
| `assets/screenshots/07_regression_metrics.png` | Exploratory regression metrics | Dashboard V2 `Experimental Insights And Performance` | `09_regression.py` |
| `assets/screenshots/08_stream_validation.png` | Streaming quality and validation detail | Dashboard V2 `Execution And Data Quality` | `10_streaming_replay.py` |
| `assets/screenshots/09_optimize_summary.png` | Optimize comparison | Dashboard V2 `Experimental Insights And Performance` | `11_optimize.py` |
| `assets/screenshots/10_orders_by_day.png` | Orders by day visual | Dashboard V2 `Executive Overview` | `12_report_pack.py` |
| `assets/screenshots/11_top_products.png` | Top products visual | Dashboard V2 `Order Behavior` | `12_report_pack.py` |
| `assets/screenshots/12_seed_recommendations.png` | Seed-product recommendations table | Dashboard V2 `Recommendations And Segments` | `12_report_pack.py` |
| `assets/screenshots/13_cluster_k_scores.png` | Cluster k-selection evidence | Dashboard V2 `Recommendations And Segments` | `07_clustering.py` |
| `assets/screenshots/14_classifier_feature_importance.png` | Classifier feature importance visual | Dashboard V2 `Experimental Insights And Performance` | `08_classifier.py` |
| `assets/screenshots/15_olap_validation.png` | OLAP validation summary or detail | Dashboard V2 `Execution And Data Quality` | `05_olap.py` |

## Report Tables
These report tables are expected after the full notebook sequence is rerun with the latest notebook source:

- `report_olap_cube`
- `report_olap_rollup`
- `report_olap_basket`
- `report_olap_validation`
- `report_classifier_metrics`
- `report_classifier_feature_importance`
- `report_regression_metrics`
- `report_cluster_profiles`
- `report_cluster_k_scores`
- `report_stream_validation`
- `report_optimize_timings`
- `report_optimize_summary`

## Exact ML Disclaimer
Classifier and regression results are exploratory and useful for demo discussion, but not final predictive proof. Methodology tightening is still pending.

## GitHub Showcase Rule
- Lead with business overview, recommendation proof, and data-quality proof.
- Keep experimental-model visuals in the repo, but do not make them the hero assets.
- Use the dashboard screenshots for the demo package wherever possible.
- Use the report tables plus `12_report_pack.py` for the written report and fallback evidence flow.
- Do not claim an artifact exists unless the file has been replaced with a real data-backed capture or render from the latest validated run.
