# Executive Summary

RetailPulse is an end-to-end Databricks Free Edition project for grocery order analytics and recommendation. The implementation is intentionally structured for GitHub: canonical Databricks source notebooks in `.py`, generated `.ipynb` mirrors, local data-prep tooling, Databricks Asset Bundles for reproducible deployment, and GitHub Actions for validation plus manual-dispatch Databricks execution.

## Implemented Scope
- deterministic 10% user sample from Instacart
- bronze, silver, and gold Delta pipeline
- star schema with `fact_order_items` and `fact_orders`
- OLAP using `CUBE` and `ROLLUP`
- FP-growth association rules
- KMeans user segmentation
- decision-tree classification
- linear-regression basket-size prediction
- replay-style streaming with `Trigger.AvailableNow`
- `OPTIMIZE` and `ZORDER BY` benchmarking

## Important Corrections
- Instacart has no price fields, so the current implementation does not claim true sales analytics.
- Instacart has no absolute transaction dates, so the time dimension is a slot-based dimension built from day-of-week and hour-of-day.
- Databricks Free Edition is serverless-only and quota-limited, so the project avoids unsupported RDD workflows and avoids automatic Databricks runs on every Git push.

## GitHub-Ready Packaging
- `notebooks/*.py` are the source of truth
- `notebooks_ipynb/*.ipynb` are generated convenience copies
- Databricks Asset Bundles define the full sequential rebuild job
- GitHub Actions validate the repo and support manual Databricks execution

## Future Works
The following items were part of the broader original vision and are intentionally preserved as future work rather than being implied as complete:
- MLflow experiment tracking
- Databricks SQL or AI/BI dashboard
- synthetic `product_price_map` and `estimated_sales_amount`
- a second supervised model such as RandomForest
- richer streaming via Kafka, Auto Loader, or paid-tier continuous streaming
- an RDD-style Hadoop demo on non-serverless compute

