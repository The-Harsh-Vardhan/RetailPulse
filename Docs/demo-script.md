# RetailPulse Demo Script

This script is designed for a 6 to 8 minute live demo or boss walkthrough. It keeps the presentation aligned with the actual finished implementation and avoids overclaiming features the project does not have.

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

Release-state anchor:
- Successful run id: `631388168060027`
- Published dashboard revision: `2026-04-05T08:40:02.619Z`
- Keep both values ready if the walkthrough turns into a release-readiness discussion.

## Demo Goal
Explain that RetailPulse is a Databricks Free Edition grocery-order analytics project built on Instacart. The project focuses on order behavior, recommendations, segmentation, and exploratory predictive analytics rather than raw sales because the dataset has no prices and no absolute dates.

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
- The validated run completed successfully on April 5, 2026.

Proof to show:
- Databricks run page
- Point out the successful status for the full notebook chain

### 3. Executive Overview
Talk track:
- Open the `Executive Overview` page first.
- This page gives the fast business summary: KPI counters, orders by day, department demand, timing patterns, and core table counts.
- It turns the medallion and OLAP work into a business-readable first impression.

Proof to show:
- KPI counters
- Orders-by-day chart
- Department-demand chart
- Core table-count widget

### 4. Order Behavior
Talk track:
- Move to the `Order Behavior` page to show how basket behavior changes across dayparts and hours.
- Use top-products evidence to make the dataset feel concrete instead of abstract.

Proof to show:
- Basket-size-by-daypart chart
- Average-basket-size-by-day chart
- Average-basket-size-by-hour chart
- Top-products chart

### 5. Recommendations And Segments
Talk track:
- The original plan called for FP-growth, but the final Free Edition serverless implementation uses pairwise association-rule mining because that was the stable Spark Connect path in the target workspace.
- The output is still a reusable `mart_association_rules` table with support, confidence, and lift.
- KMeans was evaluated across `k = 3, 4, 5`, and the retained result gives three interpretable shopper segments.

Proof to show:
- Top recommendation rules table
- Seed recommendations for `Organic Raspberries`
- Segment profiles table
- Segment-size chart
- Cluster k-selection chart

### 6. Execution And Data Quality
Talk track:
- This page is about correctness, not cosmetics.
- The streaming panel proves the replay output matches the equivalent batch aggregate.
- The OLAP validation panel proves the persisted rollups match the direct grouped totals.
- This is where you show that the project is not only visual but also checked.

Proof to show:
- Streaming quality counters
- Streaming validation detail table
- OLAP validation summary
- Release-signoff text widget

### 7. Experimental Insights And Performance
Talk track:
- The classifier predicts whether a user is a `power_user`, defined from the top quartile of `total_orders`.
- The regression predicts basket size from order context and user history.
- Present both supervised notebooks as `Experimental Insights`, not as rigorous final predictive proof or operational decision logic.
- State clearly that no business recommendation or automation depends on these outputs in the current release.
- If challenged on the metrics, say the current feature construction is useful for demonstration but still needs a stricter leakage-safe redesign before submission-grade claims.

Proof to show:
- Exploratory-metrics table
- Classifier feature-importance chart
- Optimize comparison chart
- Raw optimize timings

### 8. Close with project realism
Talk track:
- RetailPulse is showcaseable because it is reproducible, it runs end to end on Databricks Free Edition, and it has a rich dashboard plus notebook fallback.
- The project is also honest about what is exploratory, what is validated, and what still needs tightening before final submission.

Proof to show:
- Dashboard pages recap
- `12_report_pack.py` fallback

## Closing Line
RetailPulse is boss-review ready because it is reproducible, it runs end to end on Databricks Free Edition, and its key results are backed by validated tables plus a packaged evidence set instead of hand-waved notebook claims.

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
No. They remain `Experimental Insights` for this release, and they should not be presented as rigorous final predictive evidence until the feature design is tightened to avoid leakage.
