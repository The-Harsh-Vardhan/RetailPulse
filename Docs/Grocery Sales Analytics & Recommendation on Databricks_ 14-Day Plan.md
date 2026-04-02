# Grocery Order Analytics & Recommendation on Databricks: 14-Day Solo Plan

## Executive Summary
RetailPulse is a two-week Databricks Free Edition capstone built on the Instacart dataset. The project focuses on grocery order behavior rather than raw sales because Instacart does not provide prices or absolute order dates. The final solution uses a deterministic 10% user sample, a bronze/silver/gold Delta pipeline, a star schema, OLAP queries, FP-growth recommendations, KMeans clustering, a decision-tree classifier, a linear-regression model, and an `AvailableNow` replay-style streaming demo that fits current serverless limitations.

## Dataset Caveats That Shape The Design
- Instacart contains `order_dow`, `order_hour_of_day`, and `days_since_prior_order`, but not a calendar date.
- Instacart does not include product prices, revenue, or store-level sales totals.
- The project therefore measures item counts, basket size, reorder behavior, department mix, and slot-based demand patterns.
- If your evaluator insists on “sales”, use an explicitly labeled synthetic pricing extension after the core submission is complete.

## Day-By-Day Implementation
| Day | Primary Goal | Concrete Deliverable |
| --- | --- | --- |
| 1 | Set up Databricks Free Edition schema and volumes; run local sampling utility | `00_setup` complete, 10% sample prepared locally |
| 2 | Upload sampled CSVs and ingest bronze tables with explicit schemas | Bronze Delta tables plus row-count validation |
| 3 | Build silver orders, enriched order-items, and user history | `silver_orders`, `silver_order_items`, `silver_products_enriched`, `silver_user_history` |
| 4 | Build dimensions, facts, and base user feature mart | `dim_*`, `fact_order_items`, `fact_orders`, `mart_user_features` |
| 5 | Run OLAP with `CUBE` and `ROLLUP` | Department/day and slot rollups with screenshots |
| 6 | Train FP-growth and save association rules | `mart_association_rules` and one recommendation example |
| 7 | Evaluate KMeans for `k = 3, 4, 5` and keep best silhouette | Clustered `mart_user_features` and cluster profiles |
| 8 | Train a `DecisionTreeClassifier` for power-user prediction | Accuracy, AUC, baseline comparison, feature importance |
| 9 | Train a `LinearRegression` basket-size model | RMSE, R², baseline comparison |
| 10 | Create held-out replay files and run `Trigger.AvailableNow` streaming | `stream_order_slot_metrics` and batch-vs-stream validation |
| 11 | Run `OPTIMIZE ... ZORDER BY` and benchmark repeat queries | Before/after timing evidence |
| 12 | Assemble charts, diagrams, and evidence tables | Final architecture and results visuals |
| 13 | Write report, README polish, and demo story | Submission-ready documentation |
| 14 | Rehearse and rerun critical notebooks | Final verification pass |

## Core Deliverables
- Databricks notebook source files from `00_setup` through `12_report_pack`
- Local utilities to sample Instacart and split replay batches
- Bronze, silver, and gold Delta tables
- Association rules, cluster profiles, classifier metrics, regression metrics, and replay validation
- README, corrected project docs, and architecture assets

## Validation Checklist
- Bronze counts match uploaded CSV counts.
- `fact_order_items` has no null IDs and only `0/1` for `reordered`.
- `fact_orders.basket_size` matches grouped item counts.
- OLAP subtotals and grand totals are sensible and manually spot-checked.
- FP-growth produces non-trivial rules and at least three recommendations for a seed basket.
- KMeans returns interpretable segments and a saved silhouette-driven choice of `k`.
- The classifier beats the majority baseline.
- The regression beats the mean-basket baseline or is documented as exploratory.
- Replay-stream output matches the equivalent batch aggregation.

