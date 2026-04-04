# RetailPulse Demo Script

This script is designed for a 6 to 8 minute live demo. It keeps the presentation aligned with the actual finished implementation and avoids overclaiming features the project does not have.

## Before You Start
Open these tabs in advance:
- The GitHub repository README
- The successful Databricks job run page
- The AI/BI dashboard: `RetailPulse Demo Dashboard`
- `12_report_pack.py` as the notebook fallback
- `05_olap.py`
- `06_association_rules.py`
- `07_clustering.py`
- `08_classifier.py`
- `09_regression.py`
- `10_streaming_replay.py`
- `11_optimize.py`

Keep `Docs/showcase-summary.md` open as your backup source for numbers.

## Demo Goal
Explain that RetailPulse is a Databricks Free Edition grocery-order analytics project built on Instacart. The project focuses on order behavior, recommendations, segmentation, and predictive analytics rather than raw sales because the dataset has no prices and no absolute dates.

## Suggested Flow

### 1. Open with the dashboard first
Talk track:
- Start from the AI/BI dashboard so the audience sees one polished business surface instead of a notebook stack.
- Use the dashboard to prove that RetailPulse is not just a code exercise; it has a presentable analytics layer on top of the Databricks pipeline.
- If the dashboard fails or a panel needs drill-down, switch to `12_report_pack.py` as the fallback evidence hub.

Proof to show:
- `RetailPulse Demo Dashboard`
- `12_report_pack.py` fallback note

### 2. Show the successful end-to-end Databricks run
Talk track:
- The project is not just dashboard screenshots; it runs as a full sequential Databricks job.
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
- Dashboard KPI counters or `12_report_pack.py` table-count output
- Mention `fact_order_items` and `fact_orders`

### 4. Show the business overview page
Talk track:
- The dashboard leads with KPI counters, department demand, timing patterns, and basket-size behavior by daypart.
- This turns the OLAP work into a business-readable story instead of making the audience parse raw SQL.

Proof to show:
- `Business Overview` page in the AI/BI dashboard
- Fallback: `05_olap.py`

### 5. Show the recommendation engine
Talk track:
- The original plan called for FP-growth, but the final Free Edition serverless implementation uses pairwise association-rule mining because that was the stable Spark Connect path in the target workspace.
- The output is still a reusable `mart_association_rules` table with support, confidence, and lift.

Proof to show:
- Dashboard top-rules table or `06_association_rules.py`
- Example rule: `Organic Garlic -> Organic Yellow Onion`
- Example recommendation for `Organic Raspberries`: `Bag of Organic Bananas` and `Organic Strawberries`

### 6. Show the customer segments
Talk track:
- KMeans evaluated `k = 3, 4, 5` and the retained result gives three interpretable shopper segments.
- These segments map cleanly to business language: loyal frequent shoppers, light occasional shoppers, and large-basket stock-up shoppers.

Proof to show:
- Dashboard customer-segments widget or `07_clustering.py`
- Point at the three segment profiles and their average orders, basket size, and reorder rate

### 7. Show execution and evidence
Talk track:
- The second dashboard page is about correctness, not cosmetics.
- The streaming panel proves the replay output matches the equivalent batch aggregate.
- The optimize panel records a real benchmark result, including the fact that optimization was slower on this sample.

Proof to show:
- `Execution And Evidence` page in the AI/BI dashboard
- Fallback: `10_streaming_replay.py` and `11_optimize.py`

### 8. Show the predictive models carefully
Talk track:
- The classifier predicts whether a user is a `power_user`, defined from the top quartile of `total_orders`.
- The regression predicts basket size from order context and user history.
- Present both supervised notebooks as exploratory modeling deliverables, not as rigorous final predictive proof.
- If challenged on the metrics, say the current feature construction is useful for demonstration but still needs a stricter leakage-safe redesign before submission-grade claims.

Proof to show:
- Dashboard exploratory-metrics table or `08_classifier.py` and `09_regression.py`
- Mention the current exploratory metrics:
  - classifier accuracy `0.9136` vs baseline `0.7445`
  - classifier AUC `0.8813`
  - regression RMSE `5.0945` vs baseline `7.6627`

### 9. Close with project realism
Talk track:
- RetailPulse is showcaseable because it is reproducible, it runs end to end on Databricks Free Edition, and it has a presentable dashboard plus notebook fallback.
- The project is also honest about what is exploratory, what is validated, and what still needs tightening before final submission.

Proof to show:
- Dashboard pages recap
- `12_report_pack.py` fallback

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
