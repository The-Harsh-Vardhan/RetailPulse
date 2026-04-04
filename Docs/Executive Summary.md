# Executive Summary

RetailPulse is an end-to-end Databricks Free Edition project for grocery order analytics and recommendation. The implementation is intentionally structured for GitHub: canonical Databricks source notebooks in `.py`, generated `.ipynb` mirrors, local data-prep tooling, Databricks Asset Bundles for reproducible deployment, and GitHub Actions for validation plus manual-dispatch Databricks execution.

## Implemented Scope
- Deterministic 10% user sample from Instacart
- Bronze, silver, and gold Delta pipeline
- Star schema with `fact_order_items` and `fact_orders`
- OLAP using `CUBE` and `ROLLUP`
- Serverless-safe pairwise association rules for product recommendation
- KMeans user segmentation
- Exploratory decision-tree classification
- Exploratory linear-regression basket-size prediction
- Replay-style streaming with `Trigger.AvailableNow`
- `OPTIMIZE` and `ZORDER BY` benchmarking

## Important Corrections
- Instacart has no price fields, so the current implementation does not claim true sales analytics.
- Instacart has no absolute transaction dates, so the time dimension is a slot-based dimension built from day-of-week and hour-of-day.
- Databricks Free Edition is serverless-only and quota-limited, so the project avoids unsupported RDD workflows.
- The recommendation stage uses pairwise association-rule mining instead of FP-growth because that was the stable submission-safe path on the target Spark Connect serverless workspace.

## Validated Run Snapshot
- Successful end-to-end Databricks run completed on April 3, 2026.
- Sample size:
  - `341,974` sampled orders
  - `3,267,191` sampled prior rows
  - `137,847` sampled train rows
- Exploratory classifier: `0.9136` accuracy, `0.8813` AUC, `0.7445` majority baseline accuracy
- Exploratory regression: `0.5580` R², `5.0945` RMSE, `7.6627` mean-baseline RMSE
- Streaming replay validation: `158` checked order-slot aggregates with `0` mismatches
- Optimization benchmark completed, but the measured queries were slower after `OPTIMIZE` on the small sample; this is documented honestly as a result, not presented as an improvement

These supervised metrics are still useful for demonstration, but they should be described as exploratory until the feature construction is reworked into a stricter leakage-safe evaluation.

## GitHub-Ready Packaging
- `notebooks/*.py` are the source of truth
- `notebooks_ipynb/*.ipynb` are generated convenience copies
- Databricks Asset Bundles define the full sequential rebuild job
- GitHub Actions validate the repo and support manual Databricks execution
- Showcase documentation includes a results summary, a demo script, and a packaged evidence checklist for presentation use

## Future Works
The following items were part of the broader original vision and are intentionally preserved as future work rather than being implied as complete:
- MLflow experiment tracking
- Databricks SQL or AI/BI dashboard
- Synthetic `product_price_map` and `estimated_sales_amount`
- A second supervised model such as RandomForest
- Richer streaming via Kafka, Auto Loader, or paid-tier continuous streaming
- An RDD-style Hadoop demo on non-serverless compute
