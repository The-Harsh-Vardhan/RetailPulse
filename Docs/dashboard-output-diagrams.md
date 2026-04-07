# Dashboard Output Diagrams

This file explains the current Dashboard V2 outputs and their matching screenshot artifacts.

Use it alongside:
- `Docs/databricks-dashboard-spec.md` for the canonical widget and query layout
- `Docs/evidence-pack.md` for screenshot-pack policy and capture order
- `notebooks/12_report_pack.py` for the notebook fallback that mirrors the same five-section story

## How To Read This File
- `Primary source` names the dashboard query when the page is rendered in AI/BI dashboards.
- `Fallback source` names the notebook or persisted table that shows the same evidence if the dashboard is unavailable.
- `Screenshot artifact` points to the repo-tracked visual that best represents the widget or page output today.

## Page 1: Executive Overview
Goal: prove that the pipeline produced populated tables and that overall order behavior is readable at a glance.

| Widget or diagram | Screenshot artifact | Primary source | Fallback source | Explanation |
| --- | --- | --- | --- | --- |
| KPI Counters | `assets/screenshots/02_report_pack_counts.png` | `dashboard_kpi_summary` | `12_report_pack.py` table-count display | Summarizes the main row counts used to show that the bronze, silver, gold, and report layers are populated. |
| Orders By Day | `assets/screenshots/10_orders_by_day.png` | `dashboard_orders_by_day` | `report_olap_rollup` via `12_report_pack.py` | Shows order volume and average basket size by day-of-week rollup. Use it to see which days carry the heaviest order activity. |
| Department Demand | `assets/screenshots/03_olap_outputs.png` | `dashboard_department_totals` | `report_olap_cube` | Highlights which departments dominate item demand. This is the quickest category-level view of assortment concentration. |
| Order Timing Pattern | `assets/screenshots/03_olap_outputs.png` | `dashboard_hourly_order_pattern` | `report_olap_rollup` | Shows when orders cluster through the day. It is useful for staffing, placement, and timing interpretation. |
| Core Table Counts | `assets/screenshots/02_report_pack_counts.png` | `dashboard_table_counts` | `12_report_pack.py` table-count display | Acts as a quality gate by showing whether the expected report and mart tables exist with non-zero rows. |

## Page 2: Order Behavior
Goal: show how basket size and product demand vary by time and department.

| Widget or diagram | Screenshot artifact | Primary source | Fallback source | Explanation |
| --- | --- | --- | --- | --- |
| Basket Size By Daypart | `assets/screenshots/11_top_products.png` | `dashboard_daypart_basket` | `report_olap_basket` | Compares average basket size across dayparts and departments. Use it to spot when larger shopping missions happen. |
| Average Basket Size By Day | `assets/screenshots/10_orders_by_day.png` | `dashboard_orders_by_day` | `report_olap_rollup` | Reuses the day rollup to show how shopping missions vary by day rather than only raw order count. |
| Average Basket Size By Hour | `assets/screenshots/11_top_products.png` | `dashboard_avg_basket_by_hour` | `fact_orders` aggregation in `12_report_pack.py` | Shows whether baskets get larger at certain hours, which is useful for timing promotions or featured placements. |
| Top Products | `assets/screenshots/11_top_products.png` | `dashboard_top_products` | `fact_order_items` aggregation in `12_report_pack.py` | Lists the most frequently seen products. This is the simplest demand-ranking view in the package. |

## Page 3: Recommendations And Segments
Goal: show the most actionable current outputs: cross-sell rules, seed recommendations, and customer segments.

| Widget or diagram | Screenshot artifact | Primary source | Fallback source | Explanation |
| --- | --- | --- | --- | --- |
| Top Recommendation Rules | `assets/screenshots/04_association_rules.png` | `dashboard_top_rules` | `mart_association_rules` via `06_association_rules.py` | Shows the strongest product-to-product rules using support, confidence, and lift together. These are the main recommendation-proof outputs. |
| Seed Recommendations | `assets/screenshots/12_seed_recommendations.png` | `dashboard_seed_recommendations` | `12_report_pack.py` or `14_prescriptive_analysis.py` | Turns the rule table into a next-best-product view for one chosen seed product, currently `Organic Raspberries` by default. |
| Customer Segment Profiles | `assets/screenshots/05_cluster_profiles.png` | `dashboard_cluster_profiles` | `report_cluster_profiles` | Summarizes average order frequency, basket size, and reorder behavior by cluster so the segments are interpretable. |
| Segment Sizes | `assets/screenshots/05_cluster_profiles.png` | `dashboard_segment_sizes` | `report_cluster_profiles` via `12_report_pack.py` | Shows how large each segment is, which matters when choosing which audience deserves attention first. |
| Cluster Model Selection | `assets/screenshots/13_cluster_k_scores.png` | `dashboard_cluster_k_scores` | `report_cluster_k_scores` | Documents why the chosen cluster count is reasonable by exposing the silhouette score for each tested `k`. |

## Page 4: Execution And Data Quality
Goal: prove that the replay stream and OLAP validation outputs are trustworthy enough for review.

| Widget or diagram | Screenshot artifact | Primary source | Fallback source | Explanation |
| --- | --- | --- | --- | --- |
| Streaming Quality | `assets/screenshots/08_stream_validation.png` | `dashboard_stream_health` | `report_stream_validation` | Reduces the replay validation into a quick quality signal. This is the fastest way to see whether stream and batch aggregates agree. |
| Streaming Validation Detail | `assets/screenshots/08_stream_validation.png` | `dashboard_stream_validation_detail` | `10_streaming_replay.py` or `12_report_pack.py` | Shows row-level agreement for count, basket average, and reordered-item totals at order-slot grain. |
| OLAP Validation Summary | `assets/screenshots/15_olap_validation.png` | `dashboard_olap_validation_summary` | `report_olap_validation` and summary aggregation in `12_report_pack.py` | Confirms that the cube output matches a direct aggregation at the base grouping grain. Any mismatch should be treated as a correctness issue. |

## Page 5: Experimental Insights And Performance
Goal: package the exploratory predictive outputs and optimization evidence without presenting them as release-safe business proof.

Exact disclaimer text:

> Classifier and regression results are exploratory and useful for demo discussion, but not final predictive proof. Methodology tightening is still pending.

| Widget or diagram | Screenshot artifact | Primary source | Fallback source | Explanation |
| --- | --- | --- | --- | --- |
| Exploratory Model Metrics | `assets/screenshots/06_classifier_metrics.png`, `assets/screenshots/07_regression_metrics.png` | `dashboard_exploratory_metrics` | `report_classifier_metrics` and `report_regression_metrics` | Shows the current classifier and regression metrics together. These are useful for discussion, but they remain explicitly exploratory. |
| Classifier Feature Importance | `assets/screenshots/14_classifier_feature_importance.png` | `dashboard_classifier_feature_importance` | `report_classifier_feature_importance` | Makes the classifier lane more interpretable by showing which persisted user features the decision tree weighted most heavily. |
| Optimize Comparison | `assets/screenshots/09_optimize_summary.png` | `dashboard_optimize_comparison` | `report_optimize_summary` | Compares before and after optimization timings for the benchmark queries. It documents whether `OPTIMIZE` helped on the current sample. |
| Raw Optimize Timings | `assets/screenshots/09_optimize_summary.png` | `dashboard_optimize_raw_timings` | `report_optimize_timings` | Shows the timing rows that feed the summarized performance comparison. Use it when you need the raw seconds rather than the derived speedup columns. |

## Related Deep-Dive Notebooks
- `notebooks/13_predictive_analysis.py` packages the exploratory predictive lane without retraining or reframing it as rigorous proof.
- `notebooks/14_prescriptive_analysis.py` packages the action-oriented recommendation, segmentation, and timing outputs into one plain-language review surface.
