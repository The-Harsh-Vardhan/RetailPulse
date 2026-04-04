# RetailPulse Solo Free-Edition Blueprint

## Summary
- Build a submission-safe Databricks project around grocery order behavior, not raw revenue.
- Keep core scope to: sampled Instacart data, bronze/silver/gold Delta pipeline, star schema, OLAP, association-rule recommendations, KMeans user segments, one classifier, one regression model, and a simple streaming replay demo.
- Correct the current docs before implementation: Instacart does not include product prices or absolute calendar dates, and Databricks Free Edition is serverless-only. Replace `sales_amount` and month/year analysis with item-count, basket-size, reorder-rate, `order_dow`, `order_hour_of_day`, and `days_since_prior_order`. Add synthetic pricing only if your evaluator explicitly requires “sales”.

## Final Implementation Note
The original blueprint targeted FP-growth for the recommendation stage. The final Databricks Free Edition implementation uses pairwise association-rule mining instead because that was the stable submission-safe path on the target Spark Connect serverless workspace.

## Interfaces And Artifacts
- Use a deterministic 10% user sample as the working dataset: keep rows where `pmod(user_id, 10) = 0` in `orders`, then filter order-product files to those `order_id`s. Download locally and upload to Databricks; do not fetch Kaggle from notebooks.
- Bronze tables: `bronze_orders`, `bronze_order_products_prior`, `bronze_order_products_train`, `bronze_products`, `bronze_aisles`, `bronze_departments`.
- Silver tables: `silver_orders`, `silver_order_items`, `silver_products_enriched`, `silver_user_history`.
- Gold tables: `dim_user`, `dim_product`, `dim_aisle`, `dim_department`, `dim_order_slot`, `fact_order_items`, `fact_orders`, `mart_user_features`, `mart_association_rules`, `stream_order_slot_metrics`.
- `fact_order_items` contract: `order_id`, `user_id`, `product_id`, `aisle_id`, `department_id`, `eval_set`, `order_number`, `order_dow`, `order_hour_of_day`, `days_since_prior_order`, `add_to_cart_order`, `reordered`, `item_qty`.
- `fact_orders` contract: `order_id`, `user_id`, `eval_set`, `order_number`, `order_dow`, `order_hour_of_day`, `days_since_prior_order`, `basket_size`, `reordered_item_count`, `distinct_department_count`.
- Notebook entrypoints: `00_setup`, `01_sample_and_upload`, `02_bronze_ingest`, `03_silver_transform`, `04_gold_model`, `05_olap`, `06_association_rules`, `07_clustering`, `08_classifier`, `09_regression`, `10_streaming_replay`, `11_optimize`, `12_report_pack`.

## Implementation
1. Day 1: Create the Databricks Free Edition workspace, default catalog/schema, and one raw volume; add notebook widgets for catalog/schema/path names; locally download Instacart and build the 10% user sample.
2. Day 2: Upload sampled raw files plus full lookup tables; ingest to bronze Delta tables with explicit schemas and row-count validation.
3. Day 3: Build silver tables by unioning prior/train order-items, enriching products with aisles/departments, and validating null/duplicate behavior.
4. Day 4: Build `dim_*`, `fact_order_items`, and `fact_orders`; use `dim_order_slot` instead of `dim_date`; keep measures to item count, basket size, and reorder metrics.
5. Day 5: Implement OLAP queries with `CUBE(department_id, order_dow)`, `ROLLUP(order_dow, order_hour_of_day)`, and basket-size analysis by department/day-part; capture charts/screenshots.
6. Day 6: Build association rules on per-order product baskets, persist `mart_association_rules`, and add a notebook cell that returns top consequent products for a seed basket.
7. Day 7: Create `mart_user_features` and cluster users with KMeans; restrict `k` search to `3`, `4`, `5`; keep the best silhouette plus interpretable segments.
8. Day 8: Train a `DecisionTreeClassifier` on user-level features with `power_user` defined as top-quartile `total_orders`; compare against majority baseline and save feature importance.
9. Day 9: Train a `LinearRegression` model to predict `basket_size` from order context and prior-user behavior; use this as the predictive analytics deliverable.
10. Day 10: Split a held-out slice into 3-5 small batch files; run Structured Streaming with `Trigger.AvailableNow` and write aggregates to `stream_order_slot_metrics`.
11. Day 11: Run `OPTIMIZE` on gold facts and benchmark the same OLAP queries before/after using query profile; do not use `cache`, `persist`, or Spark UI workflows.
12. Day 12: Produce final visuals, architecture diagram, ER diagram, and medallion diagram; export evidence tables/charts for the report.
13. Day 13: Write the README/report from completed notebooks: problem statement, dataset caveats, architecture, analytics, model metrics, streaming demo, limitations, and future work.
14. Day 14: Rehearse the demo end-to-end, rerun critical notebooks, fix broken cells, and export the final submission set.
- Stretch only after the core passes: synthetic `product_price_map` plus `estimated_sales_amount`, SQL dashboard on the small warehouse, and a second supervised model such as RandomForest.

## Test Plan
- Bronze row counts match uploaded files minus header; silver row counts are explainable after union/filter steps.
- `fact_order_items` has no null `order_id`, `user_id`, `product_id`, or `department_id`; `reordered` is only `0/1`.
- `fact_orders.basket_size` matches grouped line counts from `fact_order_items` on a sampled order set.
- OLAP output includes subtotal and grand-total rows for both `CUBE` and `ROLLUP`, and manual spot checks match fact aggregates.
- Association-rule mining produces at least 10 non-trivial rules with sensible confidence and lift; the recommendation cell returns suggestions for a sample basket.
- KMeans output includes centroid values and one short business interpretation per segment.
- The decision tree beats majority-class baseline; the regression beats mean-basket baseline or is explicitly documented as exploratory if it does not.
- Streaming replay output matches an equivalent batch aggregate over the same held-out files.
- Final notebooks run top-to-bottom with only widget/path edits and no hidden temp-view dependency between notebooks.

## Assumptions
- Default project title becomes `RetailPulse: Grocery Order Analytics & Recommendation on Databricks`; only use “sales” wording if you intentionally add synthetic pricing and label it estimated.
- `dim_order_slot` is the time dimension. Do not invent month/year facts from this dataset.
- Keep notebook logic linear and bounded: one responsibility per notebook, small transformations, explicit validation after each stage, minimal UDFs, and no hidden state.
- As of March 27, 2026, Databricks documents Free Edition as serverless-only and quota-limited, and as of January 24, 2026, Databricks documents that serverless does not support RDD APIs, has limited DBFS access, and only supports `Trigger.AvailableNow` for Structured Streaming.
