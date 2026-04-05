# Executive Summary

RetailPulse is an end-to-end Databricks Free Edition project for grocery order analytics and recommendation. The implementation is intentionally structured for GitHub: canonical Databricks source notebooks in `.py`, generated `.ipynb` mirrors, local data-prep tooling, Databricks Asset Bundles for reproducible deployment, and GitHub Actions for validation plus manual-dispatch Databricks execution.

Current operating posture: controlled internal pilot on the current Databricks Free Edition workspace, not a customer-scale SLA deployment.

## Implemented Scope
- Deterministic 10% user sample from Instacart
- Bronze, silver, and gold Delta pipeline
- Star schema with `fact_order_items` and `fact_orders`
- OLAP using `CUBE` and `ROLLUP`
- Serverless-safe pairwise association rules for product recommendation
- KMeans user segmentation
- `Experimental Insights` lane for decision-tree classification and linear-regression basket-size prediction
- Replay-style streaming with `Trigger.AvailableNow`
- `OPTIMIZE` and `ZORDER BY` benchmarking
- Published AI/BI dashboard plus `12_report_pack.py` fallback

## Important Corrections
- Instacart has no price fields, so the current implementation does not claim true sales analytics.
- Instacart has no absolute transaction dates, so the time dimension is a slot-based dimension built from day-of-week and hour-of-day.
- Databricks Free Edition is serverless-only and quota-limited, so the project avoids unsupported RDD workflows.
- The recommendation stage uses pairwise association-rule mining instead of FP-growth because that was the stable submission-safe path on the target Spark Connect serverless workspace.

## Validated Run Snapshot
- Successful end-to-end Databricks run completed on April 5, 2026.
- Latest successful run id: `432431661287387`
- Published AI/BI dashboard: `RetailPulse Demo Dashboard`
- Sample size:
  - `341,974` sampled orders
  - `3,267,191` sampled prior rows
  - `137,847` sampled train rows
- Streaming replay validation: `158` checked order-slot aggregates with `0` mismatches
- Optimization benchmark completed, but the measured queries were slower after `OPTIMIZE` on the small sample; this is documented honestly as a result, not presented as an improvement

## Experimental Insights
Classifier and regression outputs remain visible in the dashboard and report pack for discussion, but they are not operational release gates in this internal pilot.

No business recommendation, automation, or production decision depends on classifier or regression output in this release.

## GitHub-Ready Packaging
- `notebooks/*.py` are the source of truth
- `notebooks_ipynb/*.ipynb` are generated convenience copies
- Databricks Asset Bundles define the full sequential rebuild job
- GitHub Actions validate the repo and support manual Databricks execution
- Showcase documentation includes a results summary, a demo script, a packaged evidence checklist, a production runbook, and a boss-facing release brief

## Future Works
The following items were part of the broader original vision and are intentionally preserved as future work rather than being implied as complete:
- MLflow experiment tracking
- Dashboard-as-code export, richer filters, and screenshot refresh discipline
- Synthetic `product_price_map` and `estimated_sales_amount`
- A second supervised model such as RandomForest
- Richer streaming via Kafka, Auto Loader, or paid-tier continuous streaming
- An RDD-style Hadoop demo on non-serverless compute
- Migration to a paid Databricks workspace with stronger release isolation and operational controls
