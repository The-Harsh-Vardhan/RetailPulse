# RetailPulse Demo Script

This script is designed for a 6 to 8 minute live demo. It keeps the presentation aligned with the actual finished implementation and avoids overclaiming features the project does not have.

## Before You Start
Open these tabs in advance:
- The GitHub repository README
- The successful Databricks job run page
- `05_olap.py`
- `06_association_rules.py`
- `07_clustering.py`
- `08_classifier.py`
- `09_regression.py`
- `10_streaming_replay.py`
- `11_optimize.py`
- `12_report_pack.py`

Keep `Docs/showcase-summary.md` open as your backup source for numbers.

## Demo Goal
Explain that RetailPulse is a Databricks Free Edition grocery-order analytics project built on Instacart. The project focuses on order behavior, recommendations, segmentation, and predictive analytics rather than raw sales because the dataset has no prices and no absolute dates.

## Suggested Flow

### 1. Open with the problem and scope
Talk track:
- RetailPulse analyzes grocery ordering behavior on Databricks Free Edition.
- The project uses a deterministic 10% sample so it stays reproducible and lightweight enough for serverless execution.
- The stack includes bronze, silver, and gold Delta tables, OLAP, recommendations, clustering, classification, regression, and a replay-style streaming demo.

Proof to show:
- README overview
- Architecture diagram links

### 2. Show the successful end-to-end Databricks run
Talk track:
- The project is not just notebook fragments; it runs as a full sequential Databricks job.
- The validated run completed successfully on April 3, 2026.

Proof to show:
- Databricks run page
- Point out the successful status for the full notebook chain

### 3. Show the medallion pipeline and star schema outcome
Talk track:
- Bronze ingests the uploaded sampled CSVs with schema checks.
- Silver unifies order items and enriches products with aisle and department metadata.
- Gold creates dimensions, facts, and marts used by analytics and ML notebooks.

Proof to show:
- `12_report_pack.py` table-count output
- Mention `fact_order_items` and `fact_orders`

### 4. Show the OLAP analysis
Talk track:
- The OLAP notebook uses `CUBE` and `ROLLUP` to produce subtotal and total views.
- Produce, dairy eggs, and snacks dominate the item counts in the sample.

Proof to show:
- `05_olap.py`
- Mention representative results such as Produce with `989,427` items

### 5. Show the recommendation engine
Talk track:
- The original plan called for FP-growth, but the final Free Edition serverless implementation uses pairwise association-rule mining because that was the stable Spark Connect path in the target workspace.
- The output is still a reusable `mart_association_rules` table with support, confidence, and lift.

Proof to show:
- `06_association_rules.py`
- Example rule: `Organic Garlic -> Organic Yellow Onion`
- Example recommendation for `Organic Raspberries`: `Bag of Organic Bananas` and `Organic Strawberries`

### 6. Show the customer segments
Talk track:
- KMeans evaluated `k = 3, 4, 5` and the retained result gives three interpretable shopper segments.
- These segments map cleanly to business language: loyal frequent shoppers, light occasional shoppers, and large-basket stock-up shoppers.

Proof to show:
- `07_clustering.py`
- Point at the three segment profiles and their average orders, basket size, and reorder rate

### 7. Show the predictive models
Talk track:
- The classifier predicts whether a user is a `power_user`, defined from the top quartile of `total_orders`.
- The regression predicts basket size from order context and user history.
- Present both supervised notebooks as exploratory modeling deliverables, not as rigorous final predictive proof.
- If challenged on the metrics, say the current feature construction is useful for demonstration but still needs a stricter leakage-safe redesign before submission-grade claims.

Proof to show:
- `08_classifier.py`
- `09_regression.py`
- Mention the current exploratory metrics:
  - classifier accuracy `0.9136` vs baseline `0.7445`
  - classifier AUC `0.8813`
  - regression RMSE `5.0945` vs baseline `7.6627`

### 8. Show the streaming validation
Talk track:
- Free Edition serverless only supports `Trigger.AvailableNow`, so the project uses a replay-style stream rather than a continuously running stream.
- The important point is correctness: the stream output matches the equivalent batch aggregate.

Proof to show:
- `10_streaming_replay.py`
- State that `158` order-slot groups were checked with `0` mismatches

### 9. Close with optimization and project realism
Talk track:
- The project also benchmarks `OPTIMIZE` and `ZORDER BY`.
- On this small sample the benchmark queries were slower after optimization, and the project records that honestly instead of forcing a success narrative.

Proof to show:
- `11_optimize.py`
- `12_report_pack.py`

## Closing Line
RetailPulse is showcaseable because it is reproducible, it runs end to end on Databricks Free Edition, and its key results are backed by validated tables plus a packaged evidence set instead of hand-waved notebook claims.

## Likely Questions And Short Answers

### Why not call it sales analytics?
Because Instacart does not provide prices. The project intentionally avoids inventing revenue numbers.

### Why no calendar dates?
Because the dataset only has day-of-week, hour-of-day, and days-since-prior-order.

### Why not use FP-growth?
Because the final target workspace was Databricks Free Edition serverless on Spark Connect, and pairwise association-rule mining was the stable submission-safe implementation path there.

### Why is the streaming demo file-based?
Because Free Edition serverless supports `Trigger.AvailableNow`, so the project uses replay batches to stay within platform limits.

### Why did optimize not improve the benchmark?
Because the sample is relatively small. The benchmark still demonstrates the optimization workflow and records the real measured result.

### Are the classifier and regression metrics final?
No. They are useful exploratory results for the demo, but they should not be presented as rigorous final predictive evidence until the feature design is tightened to avoid leakage.
