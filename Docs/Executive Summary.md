# Executive Summary

RetailPulse is an end-to-end Databricks Free Edition project for grocery order analytics and recommendation. It is intentionally scoped to be submission-safe: the implementation uses the real strengths of the Instacart dataset and avoids unsupported claims about revenue or calendar-time forecasting. The repo now contains a notebook-first scaffold, local sampling utilities, test coverage for those utilities, and corrected documentation that matches current Databricks serverless behavior.

## Final Scope
- Deterministic 10% user sample from Instacart
- Bronze, silver, and gold Delta pipeline
- Star schema with order-line and order-grain facts
- OLAP using `CUBE` and `ROLLUP`
- FP-growth recommendations
- KMeans customer segmentation
- Decision-tree classification
- Linear-regression prediction of basket size
- File-based streaming replay with `Trigger.AvailableNow`
- `OPTIMIZE` and `ZORDER BY` benchmarking

## Key Corrections
- No price fields exist in Instacart, so the project focuses on order behavior instead of sales amount.
- No absolute dates exist in Instacart, so the time dimension is based on day-of-week and hour-of-day slots.
- Databricks Free Edition is serverless-only and quota-limited, so the implementation avoids RDD APIs, cache-based tuning, and continuous streaming assumptions.

## Repo Deliverables
- `notebooks/00_setup.py` through `notebooks/12_report_pack.py`
- `scripts/sample_instacart.py`
- `scripts/split_stream_replay_batches.py`
- `tests/test_sample_instacart.py`
- `tests/test_split_stream_replay_batches.py`
- Mermaid architecture assets and corrected markdown reports

## References
- Databricks Free Edition limitations: https://docs.databricks.com/aws/en/getting-started/free-edition-limitations
- Databricks serverless compute limitations: https://docs.databricks.com/en/compute/serverless/limitations.html
- Instacart Open Data overview: https://www.instacart.com/datasets/grocery-shopping-2017
