# RetailPulse: Grocery Order Analytics & Recommendation on Databricks

RetailPulse is a submission-safe Databricks Free Edition project built around grocery order behavior, not raw revenue. The repository contains local data-prep utilities, Databricks notebook source files, architecture assets, and corrected project documentation that match the limits of the Instacart dataset and Databricks Free Edition serverless compute.

## What This Project Builds
- A bronze, silver, and gold Delta pipeline over a deterministic 10% Instacart user sample.
- A star schema centered on `fact_order_items` and `fact_orders`.
- OLAP analysis with `CUBE` and `ROLLUP`.
- Market basket recommendations using FP-growth.
- Customer segmentation with KMeans.
- One supervised classifier and one regression model.
- A file-based streaming replay demo that works with `Trigger.AvailableNow`.

## Important Dataset And Platform Corrections
- Instacart does not include product prices, revenue, or absolute order dates.
- The project therefore analyzes item counts, basket size, reorder behavior, day of week, hour of day, and days since prior order.
- Databricks Free Edition is serverless-only and quota-limited, so this repo does not rely on RDD APIs, `cache`, `persist`, Spark UI, or long-running streaming triggers.
- The streaming notebook uses a held-out replay slice and `Trigger.AvailableNow`, which is compatible with current serverless limitations.

Official references:
- Databricks Free Edition limitations: https://docs.databricks.com/aws/en/getting-started/free-edition-limitations
- Databricks serverless limitations: https://docs.databricks.com/en/compute/serverless/limitations.html

## Repository Layout
- `notebooks/`: Databricks source notebooks in execution order.
- `scripts/`: Local utilities for sampling raw Instacart CSVs and creating replay batches.
- `tests/`: Lightweight unit tests for the local Python utilities.
- `assets/`: Mermaid source files for the medallion flow and star schema.
- `Docs/`: Project writeups, implementation notes, and corrected submission-facing documents.

## Notebook Order
1. `notebooks/00_setup.py`
2. `notebooks/01_sample_and_upload.py`
3. `notebooks/02_bronze_ingest.py`
4. `notebooks/03_silver_transform.py`
5. `notebooks/04_gold_model.py`
6. `notebooks/05_olap.py`
7. `notebooks/06_association_rules.py`
8. `notebooks/07_clustering.py`
9. `notebooks/08_classifier.py`
10. `notebooks/09_regression.py`
11. `notebooks/10_streaming_replay.py`
12. `notebooks/11_optimize.py`
13. `notebooks/12_report_pack.py`

## Local Workflow
1. Download the raw Instacart CSV files manually to a local folder.
2. Build the 10% deterministic user sample:

```powershell
python scripts/sample_instacart.py `
  --input-dir C:\path\to\instacart_raw `
  --output-dir C:\path\to\retailpulse_sample
```

3. Optionally create extra replay batches from a CSV file:

```powershell
python scripts/split_stream_replay_batches.py `
  --input-file C:\path\to\orders_for_replay.csv `
  --output-dir C:\path\to\replay_batches `
  --batches 4
```

4. Upload the sampled CSV files to a Unity Catalog volume in Databricks Free Edition.
5. Import the `notebooks/*.py` files into Databricks and run them in order.

## Expected Raw Files
- `orders.csv`
- `order_products__prior.csv`
- `order_products__train.csv`
- `products.csv`
- `aisles.csv`
- `departments.csv`

## Core Table Contracts
### `fact_order_items`
- `order_id`
- `user_id`
- `product_id`
- `aisle_id`
- `department_id`
- `eval_set`
- `order_number`
- `order_dow`
- `order_hour_of_day`
- `days_since_prior_order`
- `add_to_cart_order`
- `reordered`
- `item_qty`

### `fact_orders`
- `order_id`
- `user_id`
- `eval_set`
- `order_number`
- `order_dow`
- `order_hour_of_day`
- `days_since_prior_order`
- `basket_size`
- `reordered_item_count`
- `distinct_department_count`

## Validation Targets
- Bronze counts match uploaded CSV counts.
- `fact_order_items` has no null identifiers and `reordered` stays within `0/1`.
- `fact_orders.basket_size` matches grouped line counts from `fact_order_items`.
- FP-growth produces non-trivial rules and the recommendation cell returns at least three suggestions for a seed basket.
- KMeans returns centroid summaries for `k in {3,4,5}` and keeps the best silhouette score.
- The classifier beats the majority baseline.
- The regression beats the mean-basket baseline or is documented as exploratory.
- The replay stream output matches the equivalent batch aggregate.

## Scope Boundaries
- No synthetic pricing is enabled by default.
- No Kafka, DLT, or external orchestration is required.
- No notebook depends on hidden temp views from prior sessions.
- Local scripts use only the Python standard library.
