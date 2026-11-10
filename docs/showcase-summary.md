# RetailPulse Showcase Summary

This document is the fastest way to present the finished project. It captures the validated run, the measurable outputs, and the talking points that match the actual Databricks implementation.

## GitHub Reviewer Path
If someone opens this repository cold, the fastest clean path is:
1. `README.md`
2. this summary
3. `assets/screenshots/` with Dashboard V2 hero images first
4. `Docs/RetailPulse Handbook.md`
5. `Docs/demo-script.md`

If the review is more operational than academic, then add:
6. `Docs/current-production-state.md`
7. `Docs/release-checklist.md`
8. `Docs/Next Step Priority Plan.md`

## Dashboard V2 Page Map
- `Executive Overview`: KPI counters, orders by day, department demand, timing pattern, and core table counts
- `Order Behavior`: daypart basket patterns, average basket by day, average basket by hour, and top products
- `Recommendations And Segments`: top rules, seed recommendations, segment profiles, segment sizes, and cluster k-selection
- `Execution And Data Quality`: stream validation, OLAP validation, and release-signoff evidence
- `Experimental Insights And Performance`: exploratory metrics, classifier feature importance, and optimize timings

## Validated Run
- Validation date: April 5, 2026
- Databricks target: Free Edition serverless
- Final job status: `SUCCESS`
- Authenticated run URL: `https://dbc-27b50dca-30e0.cloud.databricks.com/?o=7474658274233226#job/61936309152043/run/631388168060027`

## Data Scope
RetailPulse uses the Instacart public order-history dataset with a deterministic 10% user sample:

| Sample output | Rows |
| --- | ---: |
| `orders.csv` | 341,974 |
| `order_products__prior.csv` | 3,267,191 |
| `order_products__train.csv` | 137,847 |

The project deliberately avoids raw sales or date claims because Instacart does not include prices or absolute calendar dates.

## Final Tables Produced
| Table | Rows |
| --- | ---: |
| `bronze_orders` | 341,974 |
| `silver_order_items` | 3,405,038 |
| `fact_order_items` | 3,405,038 |
| `fact_orders` | 334,438 |
| `mart_association_rules` | 49 |
| `report_cluster_profiles` | 3 |
| `report_stream_validation` | 158 |
| `report_optimize_summary` | 2 |

Dashboard V2 also uses:
- `report_cluster_k_scores`
- `report_classifier_feature_importance`

## Executive Overview Highlights
Top departments by item count:

| Department | Item count | Average basket size |
| --- | ---: | ---: |
| Produce | 989,427 | 15.6053 |
| Dairy eggs | 564,570 | 15.7091 |
| Snacks | 307,015 | 16.4833 |
| Beverages | 286,615 | 14.4986 |
| Frozen | 235,565 | 16.3924 |

These outputs come from the gold fact model using `CUBE`, `ROLLUP`, and grouped basket-size analysis.

The April 5 validated release persists these as report tables and exposes them in both the AI/BI dashboard and the `12_report_pack.py` fallback flow.

## Recommendation Results
The final workspace implementation uses serverless-safe pairwise association-rule mining instead of FP-growth. It still writes a reusable `mart_association_rules` table with support, confidence, and lift.

Top named rules from the validated run:

| Antecedent | Consequent | Support | Confidence | Lift |
| --- | --- | ---: | ---: | ---: |
| Organic Garlic | Organic Yellow Onion | 0.0073 | 0.2018 | 5.4620 |
| Organic Cilantro | Limes | 0.0057 | 0.2402 | 5.3970 |
| Organic Lemon | Organic Hass Avocado | 0.0067 | 0.2379 | 3.5011 |
| Organic Cucumber | Organic Hass Avocado | 0.0059 | 0.2199 | 3.2355 |
| Organic Blueberries | Organic Strawberries | 0.0079 | 0.2386 | 2.8072 |
| Organic Raspberries | Organic Strawberries | 0.0107 | 0.2384 | 2.8052 |

Recommendation example for the seed product `Organic Raspberries`:
- `Bag of Organic Bananas` with confidence `0.3005` and lift `2.4723`
- `Organic Strawberries` with confidence `0.2384` and lift `2.8052`

## Clustering Results
KMeans produced three interpretable shopper segments:

| Segment | Users | Avg total orders | Avg basket size | Reorder rate | Avg days since prior order | Interpretation |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Cluster 0 | 6,440 | 33.2807 | 9.1985 | 0.6521 | 9.4935 | Frequent loyal shoppers |
| Cluster 1 | 9,050 | 7.5448 | 6.6317 | 0.3594 | 18.5083 | Light occasional shoppers |
| Cluster 2 | 5,130 | 10.1033 | 17.1178 | 0.4402 | 16.9798 | Large-basket stock-up shoppers |

Dashboard V2 also surfaces the model-selection evidence for `k = 3, 4, 5` through `report_cluster_k_scores`.

## Execution And Data Quality
The streaming notebook uses `Trigger.AvailableNow` because Databricks Free Edition serverless does not support the broader continuous streaming options.

Validated replay result:
- `158` order-slot groups checked
- `0` mismatches between stream output and equivalent batch aggregation

The OLAP notebook also persists a validation table that compares grouped totals from the cube output against direct grouped totals from the fact table.

This gives a correctness story for both streaming and OLAP instead of relying on visuals alone.

## Experimental Insights And Performance
| Model | Metric | Value |
| --- | --- | ---: |
| Decision tree | Accuracy | 0.9136 |
| Decision tree | AUC | 0.8813 |
| Majority baseline | Accuracy | 0.7445 |
| Linear regression | R² | 0.5580 |
| Linear regression | RMSE | 5.0945 |
| Mean baseline | RMSE | 7.6627 |

Interpretation:
- In the current experimental evaluation, both models beat simple baselines.
- These metrics are useful for boss review and technical discussion, but they are not release gates and do not drive automated decisions in the current internal pilot.
- The feature construction still needs a stricter leakage-safe redesign before these models can be presented as rigorous final predictive evidence.
- Dashboard V2 adds classifier feature-importance evidence so the exploratory page is more interpretable than a plain metric table.

## Optimization Benchmark
The optimization notebook ran `OPTIMIZE` and `ZORDER BY` on the gold facts and persisted the benchmark summary.

| Query | Before optimize | After optimize | Seconds saved | Speedup ratio |
| --- | ---: | ---: | ---: | ---: |
| `department_hour_distribution` | 0.6994 | 0.8350 | -0.1356 | 0.8376 |
| `user_basket_summary` | 0.6828 | 0.9789 | -0.2961 | 0.6975 |

This is an important honesty point for the demo: the optimization step completed correctly, but on this small sample it did not improve the two benchmark queries.

## What Makes The Project Showcaseable
- It runs end to end on Databricks Free Edition serverless.
- The live AI/BI dashboard is published, and the repo plus workspace now share the same richer five-page Dashboard V2 story.
- The dashboard is backed by the same report tables used by the notebook fallback.
- It is GitHub-ready with clean notebook sources, generated `.ipynb` mirrors, bundle automation, CI, rebuild documentation, and a richer screenshot evidence set.
- The project is explicit about dataset constraints and platform limitations instead of overclaiming.

## Recommended Demo Assets
- Databricks run page showing overall success
- Dashboard V2 `Executive Overview`
- Dashboard V2 `Recommendations And Segments`
- Dashboard V2 `Execution And Data Quality`
- `12_report_pack.py` as the closing evidence notebook
- `assets/screenshots/` for the packaged demo evidence set

## Recommended GitHub Highlights
- Lead with the successful Databricks run screenshot and Dashboard V2 `Executive Overview`.
- Show recommendation proof, top products, cluster k-selection, and streaming validation before you show any exploratory model metrics.
- Keep classifier and regression evidence in the repo, but do not make them the hero assets.
- Link reviewers to `Docs/RetailPulse Handbook.md` if they want the full operating model instead of just the outcome snapshot.
