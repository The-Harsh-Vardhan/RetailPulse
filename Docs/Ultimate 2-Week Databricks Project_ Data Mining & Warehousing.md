# Ultimate 2-Week Databricks Project: Data Mining & Warehousing

## Project Positioning
RetailPulse is a Databricks Free Edition lakehouse project designed for a data mining and warehousing course. It keeps the assignment ambitious enough to cover ETL, star schema design, OLAP, clustering, association rules, classification, regression, and streaming, while staying realistic about the actual Instacart dataset and the limits of serverless notebooks.

## Syllabus Mapping
| Topic | RetailPulse Implementation |
| --- | --- |
| Data warehouse design | Star schema with `fact_order_items`, `fact_orders`, and five dimensions |
| ETL | Bronze, silver, and gold Delta pipeline |
| OLAP | `GROUP BY CUBE` and `GROUP BY ROLLUP` on item and order facts |
| Association rules | Spark MLlib `FPGrowth` over order baskets |
| Clustering | KMeans over user-level behavior features |
| Decision trees | `DecisionTreeClassifier` for top-quartile power-user prediction |
| Predictive analytics | `LinearRegression` for basket size prediction |
| Streaming analytics | File-based replay plus `Trigger.AvailableNow` aggregation |
| Performance optimization | `ANALYZE TABLE`, `OPTIMIZE`, and `ZORDER BY` benchmarks |

## Architecture
### Raw And Bronze
- Upload sampled CSV files to a Unity Catalog raw volume.
- Read each file with an explicit schema.
- Persist six bronze Delta tables.

### Silver
- Standardize order columns and enforce non-null IDs.
- Union prior and train order-product rows.
- Enrich products with aisle and department metadata.
- Derive reusable user history aggregates.

### Gold
- Build `dim_user`, `dim_product`, `dim_aisle`, `dim_department`, and `dim_order_slot`.
- Build `fact_order_items` at the order-line grain.
- Build `fact_orders` at the order grain.
- Build `mart_user_features` for clustering and supervised learning.

## Why The Time Dimension Is `dim_order_slot`
Instacart exposes only:
- day of week
- hour of day
- days since prior order

It does not expose:
- transaction date
- month
- year
- season
- price

Any report that uses real months, years, or sales amounts without a synthetic extension would be inventing unsupported facts. RetailPulse avoids that mistake.

## Notebook Map
- `00_setup`: schema and volume setup
- `01_sample_and_upload`: upload validation
- `02_bronze_ingest`: raw CSV to Delta
- `03_silver_transform`: clean and enrich
- `04_gold_model`: star schema and marts
- `05_olap`: CUBE and ROLLUP queries
- `06_association_rules`: FP-growth plus recommendations
- `07_clustering`: KMeans model selection and cluster profiles
- `08_classifier`: power-user classifier
- `09_regression`: basket-size regression
- `10_streaming_replay`: replay batches and streaming aggregation
- `11_optimize`: ZORDER and timing comparison
- `12_report_pack`: final evidence tables

## Submission Narrative
Frame the project as a grocery behavior analytics lakehouse:
- “What combinations do customers buy together?”
- “Which shopper segments appear in the dataset?”
- “Can we predict larger baskets from prior behavior and order context?”
- “Can we replay held-out orders through a serverless-safe streaming pattern?”

This is stronger than pretending to do revenue forecasting with data that does not include revenue.

## Delivery Guidance
- Keep each notebook runnable top-to-bottom.
- Avoid hidden temp views or notebook interdependence.
- Show validation after every ETL stage.
- Take screenshots of OLAP outputs, top rules, cluster profiles, model metrics, replay validation, and optimize timings.

