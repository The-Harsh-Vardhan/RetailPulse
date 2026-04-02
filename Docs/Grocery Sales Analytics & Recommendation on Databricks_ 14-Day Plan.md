# Grocery Order Analytics & Recommendation on Databricks: 14-Day Solo Plan

## Executive Summary
RetailPulse is a two-week Databricks Free Edition capstone built on the Instacart dataset. It focuses on grocery order behavior rather than raw sales because Instacart does not provide prices or absolute dates. The implemented project uses a deterministic 10% user sample, a bronze/silver/gold Delta pipeline, a star schema, OLAP queries, FP-growth recommendations, KMeans clustering, a decision-tree classifier, a linear-regression model, and an `AvailableNow` replay-style streaming demo.

## Implemented Schedule
| Day | Primary Goal | Concrete Deliverable |
| --- | --- | --- |
| 1 | Set up Databricks schema and volumes; run local sample builder | `00_setup` plus local 10% sample |
| 2 | Upload sampled CSVs and ingest bronze tables | Bronze Delta tables and row-count checks |
| 3 | Build silver tables | `silver_orders`, `silver_order_items`, `silver_products_enriched`, `silver_user_history` |
| 4 | Build gold model | dimensions, facts, and user feature mart |
| 5 | Run OLAP analysis | CUBE and ROLLUP evidence |
| 6 | Run FP-growth | `mart_association_rules` and recommendation example |
| 7 | Run KMeans | best-k clustering and cluster profiles |
| 8 | Train classifier | accuracy, AUC, baseline, feature importance |
| 9 | Train regression model | RMSE, R², baseline comparison |
| 10 | Run replay streaming | `stream_order_slot_metrics` and validation |
| 11 | Optimize and benchmark | before/after timing evidence |
| 12 | Assemble report tables and visuals | `12_report_pack` outputs |
| 13 | Finalize README and project docs | GitHub-ready documentation |
| 14 | Rehearse and rerun critical steps | final validation |

## Validation Checklist
- Bronze counts match uploaded CSV counts
- `fact_order_items` has no null IDs and valid `reordered` values
- `fact_orders.basket_size` matches grouped item counts
- FP-growth returns non-trivial rules
- KMeans returns interpretable segments
- classifier beats majority baseline
- regression beats mean-basket baseline or is documented as exploratory
- replay-stream output matches equivalent batch aggregate

## Future Works
Features from the original broader plan that are not implemented in the current repo:
- MLflow experiment tracking
- Databricks SQL or AI/BI dashboard
- synthetic `product_price_map` plus `estimated_sales_amount`
- second supervised model such as RandomForest
- richer streaming via Kafka, Auto Loader, or paid-tier continuous streaming
- RDD-style Hadoop demo on non-serverless compute

