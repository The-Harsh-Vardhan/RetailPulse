# RetailPulse: Grocery Order Analytics & Recommendation on Databricks

RetailPulse is a GitHub-ready Databricks Free Edition project for grocery order analytics and recommendation. It uses the Instacart dataset to build a bronze, silver, and gold Delta pipeline, a star-schema analytics layer, association rules, clustering, supervised models, and a serverless-safe streaming replay.

The repo is organized so the project can be reviewed in Git, rebuilt from scratch, deployed with Databricks Asset Bundles, and run manually from GitHub Actions without wasting Free Edition quota.

## Project Snapshot
- Dataset: Instacart order history, sampled deterministically at 10% of users
- Platform target: Databricks Free Edition, serverless-only
- Core outputs: Delta tables, OLAP queries, recommendation rules, user segments, classifier/regression metrics, replay-stream validation
- Canonical notebook format: Databricks source notebooks in `.py`
- Convenience notebook format: generated `.ipynb` copies in `notebooks_ipynb/`

## What The Project Builds
- A bronze, silver, and gold Delta pipeline over sampled grocery-order data
- A star schema centered on `fact_order_items` and `fact_orders`
- OLAP analysis with `CUBE` and `ROLLUP`
- Market basket recommendations using FP-growth
- Customer segmentation using KMeans
- A decision-tree classifier for power-user prediction
- A linear-regression model for basket-size prediction
- A file-based replay stream using `Trigger.AvailableNow`
- Optimize and benchmark evidence using `OPTIMIZE` and `ZORDER BY`

## Why This Project Does Not Use Raw Sales
- Instacart does not include product prices or revenue
- Instacart does not include absolute calendar dates
- The analytics layer therefore focuses on item counts, basket size, reorder behavior, `order_dow`, `order_hour_of_day`, and `days_since_prior_order`

This keeps the submission honest and aligned with the real dataset instead of inventing unsupported facts.

## Architecture Summary
```text
Local sample builder -> Raw CSV upload -> Bronze Delta tables
Bronze -> Silver cleansed/enriched tables
Silver -> Gold dimensions, facts, and marts
Gold -> OLAP, FP-growth, KMeans, classifier, regression
Gold held-out slice -> Replay batches -> AvailableNow streaming aggregate
```

Assets:
- [retailpulse_medallion.mmd](c:\D Drive\Projects\6th Sem\RetailPulse\assets\retailpulse_medallion.mmd)
- [retailpulse_star_schema.mmd](c:\D Drive\Projects\6th Sem\RetailPulse\assets\retailpulse_star_schema.mmd)

## Repository Layout
- `notebooks/`: canonical Databricks source notebooks
- `notebooks_ipynb/`: generated `.ipynb` mirrors for convenience and sharing
- `scripts/`: local helper scripts and notebook export tooling
- `tests/`: local unit tests for Python utilities
- `resources/`: Databricks Asset Bundle resource definitions
- `Docs/`: report-facing and rebuild documentation
- `.github/workflows/`: CI and manual Databricks automation

## Notebook Format Policy
The canonical notebook source lives in `notebooks/*.py`.

Why `.py` instead of `.ipynb`:
- Databricks officially supports source notebooks and Jupyter notebooks for import/export
- `.py` source notebooks diff cleanly in Git
- code review is substantially easier in plain text
- bundle-based deployment works naturally with source notebooks
- deterministic generation of `.ipynb` is easier than deterministic maintenance of hand-edited notebook JSON

The rule for this repo is:
- edit only `notebooks/*.py`
- regenerate `notebooks_ipynb/*.ipynb` after notebook changes
- commit both formats
- treat `.ipynb` as a convenience mirror, not the source of truth

## Quick Start
### 1. Clone the repo
```powershell
git clone https://github.com/The-Harsh-Vardhan/RetailPulse.git
cd RetailPulse
```

### 2. Download the raw Instacart CSV files
Expected raw files:
- `orders.csv`
- `order_products__prior.csv`
- `order_products__train.csv`
- `products.csv`
- `aisles.csv`
- `departments.csv`

### 3. Build the deterministic 10% sample locally
```powershell
python scripts/sample_instacart.py `
  --input-dir C:\path\to\instacart_raw `
  --output-dir C:\path\to\retailpulse_sample
```

### 4. Generate `.ipynb` mirrors from the canonical `.py` notebooks
```powershell
python scripts/export_databricks_source_to_ipynb.py
```

### 5. Authenticate Databricks CLI locally
Preferred:
```powershell
databricks auth login --host https://<your-workspace-host>
```

Fallback if you use a PAT:
```powershell
databricks configure --host https://<your-workspace-host>
```

### 6. Deploy the Databricks bundle
```powershell
databricks bundle validate -t dev
databricks bundle deploy -t dev
```

### 7. Run the full Databricks workflow
```powershell
databricks bundle run retailpulse_full_rebuild -t dev
```

## Databricks Automation
This repo is set up for two automation levels:

### Local automation
- use Databricks CLI for authentication
- validate and deploy with Databricks Asset Bundles
- run the end-to-end job locally when you want a full rebuild

### GitHub automation
- CI workflow runs local validation on push and pull request
- Databricks workflow is `workflow_dispatch` only
- manual dispatch validates, deploys, and runs the full job
- GitHub secrets required:
  - `DATABRICKS_HOST`
  - `DATABRICKS_TOKEN`

This is deliberate. Databricks Free Edition is quota-limited and should not auto-run on every push.

## Core Commands
### Local validation
```powershell
python -m unittest -q tests.test_sample_instacart tests.test_split_stream_replay_batches
python -m py_compile scripts\sample_instacart.py scripts\split_stream_replay_batches.py scripts\export_databricks_source_to_ipynb.py
python scripts/export_databricks_source_to_ipynb.py --check
databricks bundle validate -t dev
```

### Regenerate `.ipynb`
```powershell
python scripts/export_databricks_source_to_ipynb.py
```

### Run the full job from GitHub
- Open the `Run Databricks Bundle` workflow
- Click `Run workflow`
- Provide the target if requested

## Notebook Execution Order
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

## Validation Targets
- Bronze counts match uploaded CSV counts
- `fact_order_items` has no null identifiers and `reordered` stays within `0/1`
- `fact_orders.basket_size` matches grouped line counts from `fact_order_items`
- FP-growth produces non-trivial rules and at least three recommendations for a seed basket
- KMeans returns centroid summaries for `k in {3,4,5}`
- The classifier beats the majority baseline
- The regression beats the mean-basket baseline or is documented as exploratory
- Replay stream output matches the equivalent batch aggregate
- Bundle validation passes without manual notebook path edits

## Screenshots And Report Artifacts
Use these in the GitHub repo and final report:
- architecture diagram
- star schema diagram
- OLAP query outputs
- top association rules
- cluster profiles
- classifier metrics
- regression metrics
- replay-stream validation
- optimize timing comparison

You can later add screenshots to a folder such as `assets/screenshots/` and link them from this README.

## Detailed Documentation
- [Executive Summary](c:\D Drive\Projects\6th Sem\RetailPulse\Docs\Executive%20Summary.md)
- [14-Day Plan](c:\D Drive\Projects\6th Sem\RetailPulse\Docs\Grocery%20Sales%20Analytics%20%26%20Recommendation%20on%20Databricks_%2014-Day%20Plan.md)
- [Ultimate 2-Week Guide](c:\D Drive\Projects\6th Sem\RetailPulse\Docs\Ultimate%202-Week%20Databricks%20Project_%20Data%20Mining%20%26%20Warehousing.md)
- [Rebuild From Scratch](c:\D Drive\Projects\6th Sem\RetailPulse\Docs\rebuild-from-scratch.md)
- [Original Blueprint](c:\D Drive\Projects\6th Sem\RetailPulse\Docs\RetailPulse%20PLAN.md)

## Troubleshooting
### Why are the notebooks in `.py` instead of `.ipynb`?
Because `.py` is the reviewable source of truth in Git. The repo still provides generated `.ipynb` copies for people who prefer Jupyter-format files.

### Can I run everything automatically in Databricks?
Yes. The Databricks Asset Bundle defines a single sequential multi-task job, and GitHub Actions can validate, deploy, and run it manually through `workflow_dispatch`.

### Will GitHub automatically run Databricks on every push?
No. The Databricks run workflow is manual by design to avoid Free Edition quota waste.

### Can I use MLflow or dashboards later?
Yes. They are listed under future work because the current repo focuses on the core submission-safe scope.

## Future Works
The following items were in the broader original vision but are not part of the current implemented scope:
- MLflow experiment tracking for models and artifacts
- Databricks SQL or AI/BI dashboard for presentation-ready visuals
- Synthetic `product_price_map` plus `estimated_sales_amount`
- A second supervised model such as RandomForest
- Richer streaming via Kafka, Auto Loader, or paid-tier continuous streaming
- An RDD-style Hadoop demo on non-serverless compute

## References
- Databricks notebook import/export formats: https://docs.databricks.com/gcp/en/notebooks/notebook-export-import
- Databricks CLI workspace commands: https://docs.databricks.com/gcp/en/dev-tools/cli/reference/workspace-commands
- Databricks bundle commands: https://docs.databricks.com/aws/en/dev-tools/cli/bundle-commands
- Databricks Asset Bundles: https://docs.databricks.com/aws/en/dev-tools/bundles/
- Databricks GitHub CI/CD guidance: https://docs.databricks.com/gcp/en/dev-tools/ci-cd/github
- Databricks Free Edition limitations: https://docs.databricks.com/aws/en/getting-started/free-edition-limitations
