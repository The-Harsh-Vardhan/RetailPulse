# Grocery Order Analytics & Recommendation on Databricks: 14-Day Solo Plan

## Executive Summary
RetailPulse is a two-week Databricks Free Edition capstone built on the Instacart dataset. It focuses on grocery order behavior rather than raw sales because Instacart does not provide prices or absolute dates. The implemented project uses a deterministic 10% user sample, a bronze/silver/gold Delta pipeline, a star schema, OLAP queries, serverless-safe association rules, KMeans clustering, a decision-tree classifier, a linear-regression model, and an `AvailableNow` replay-style streaming demo.

## Implementation Note
The original plan called for FP-growth on basket data. The final Databricks Free Edition implementation uses pairwise association-rule mining instead because that was the stable submission-safe path on the target Spark Connect serverless workspace.

## Implemented Schedule
| Day | Primary Goal | Concrete Deliverable |
| --- | --- | --- |
| 1 | Set up Databricks schema and volumes; run local sample builder | `00_setup` plus local 10% sample |
| 2 | Upload sampled CSVs and ingest bronze tables | Bronze Delta tables and row-count checks |
| 3 | Build silver tables | `silver_orders`, `silver_order_items`, `silver_products_enriched`, `silver_user_history` |
| 4 | Build gold model | Dimensions, facts, and user feature mart |
| 5 | Run OLAP analysis | CUBE and ROLLUP evidence |
| 6 | Build association rules | `mart_association_rules` and recommendation example |
| 7 | Run KMeans | Best-k clustering and cluster profiles |
| 8 | Train exploratory classifier | Accuracy, AUC, baseline, feature importance |
| 9 | Train exploratory regression model | RMSE, R², baseline comparison |
| 10 | Run replay streaming | `stream_order_slot_metrics` and validation |
| 11 | Optimize and benchmark | Before/after timing evidence |
| 12 | Assemble report tables and visuals | `12_report_pack` outputs |
| 13 | Finalize README and project docs | GitHub-ready documentation |
| 14 | Rehearse and rerun critical steps | Final validation |

## Validated Outcomes
- Bronze counts matched the uploaded sampled files.
- `fact_order_items` and `fact_orders` were validated in the notebook flow.
- `mart_association_rules` produced `49` non-trivial rules with usable confidence and lift.
- KMeans produced three interpretable user segments.
- The current exploratory classifier evaluation beat the majority baseline.
- The current exploratory regression evaluation beat the mean-basket baseline.
- Replay-stream output matched the equivalent batch aggregate with `0` mismatches across `158` order-slot groups.
- Optimization benchmarks were recorded honestly, including the fact that the two measured queries were slower after `OPTIMIZE` on the small sample.

The supervised results are still presentation-useful, but they should be framed as exploratory until the feature design is tightened to remove leakage risk.

## Validation Checklist
- Bronze counts match uploaded CSV counts
- `fact_order_items` has no null IDs and valid `reordered` values
- `fact_orders.basket_size` matches grouped item counts
- Association-rule mining returns non-trivial rules
- KMeans returns interpretable segments
- Current exploratory classifier evaluation beats majority baseline
- Current exploratory regression evaluation beats mean-basket baseline and is documented as exploratory
- Replay-stream output matches equivalent batch aggregate

## Future Works
Features from the original broader plan that are not implemented in the current repo:
- MLflow experiment tracking
- Databricks SQL or AI/BI dashboard
- Synthetic `product_price_map` plus `estimated_sales_amount`
- Second supervised model such as RandomForest
- Richer streaming via Kafka, Auto Loader, or paid-tier continuous streaming
- RDD-style Hadoop demo on non-serverless compute
