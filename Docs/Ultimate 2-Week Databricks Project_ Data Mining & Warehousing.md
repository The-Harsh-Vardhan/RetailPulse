# Ultimate 2-Week Databricks Project: Data Mining & Warehousing

## Project Positioning
RetailPulse is a Databricks Free Edition lakehouse project designed for a data mining and warehousing course. It covers ETL, star schema design, OLAP, clustering, association rules, classification, regression, streaming, and basic optimization while staying realistic about the actual Instacart dataset and Databricks Free Edition constraints.

## Implemented Architecture
### Raw And Bronze
- upload sampled CSV files to a Unity Catalog raw volume
- load each file with an explicit schema
- persist six bronze Delta tables

### Silver
- standardize order columns and enforce non-null IDs
- union prior and train order-product rows
- enrich products with aisle and department metadata
- derive reusable user history aggregates

### Gold
- build `dim_user`, `dim_product`, `dim_aisle`, `dim_department`, and `dim_order_slot`
- build `fact_order_items` and `fact_orders`
- build `mart_user_features`
- persist report metric tables

## Notebook Packaging Decision
This repo keeps Databricks source notebooks in `.py` as the editable, reviewable source of truth. Generated `.ipynb` copies are committed separately for portability and familiarity, but they are derived artifacts. This keeps Git diffs readable while still supporting notebook consumers who expect Jupyter format.

## Automation Decision
RetailPulse uses Databricks Asset Bundles and GitHub Actions:
- push and PR workflows run local validation only
- Databricks deploy-and-run is manual-dispatch only
- this is intentional because Free Edition is quota-limited and should not rebuild automatically on every push

## Future Works
The original broader roadmap included the following items, which remain intentionally out of the current scope:
- MLflow experiment tracking
- Databricks SQL or AI/BI dashboard
- synthetic `product_price_map` plus `estimated_sales_amount`
- second supervised model such as RandomForest
- richer streaming via Kafka, Auto Loader, or paid-tier continuous streaming
- RDD-style Hadoop demo on non-serverless compute

