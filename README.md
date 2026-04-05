# RetailPulse: Grocery Order Analytics & Recommendation on Databricks

RetailPulse is a GitHub-ready Databricks Free Edition project for grocery order analytics and recommendation. It uses the Instacart dataset to build a bronze, silver, and gold Delta pipeline, a star-schema analytics layer, serverless-safe association rules, clustering, Experimental Insights models, and a replay-style streaming demo.

The repo is organized so the project can be reviewed in Git, rebuilt from scratch, deployed with Databricks Asset Bundles, and run manually from GitHub Actions without wasting Free Edition quota.

## Release Posture
- Controlled internal production pilot on the current Databricks Free Edition workspace
- Manual release path only
- Classifier and regression outputs remain in an `Experimental Insights` lane and are not operational decision drivers in this release

## Validated Run Snapshot
- Latest validated end-to-end Databricks run: April 5, 2026
- Workspace target: Databricks Free Edition serverless
- End-to-end status: `SUCCESS`
- Authenticated run URL: `https://dbc-27b50dca-30e0.cloud.databricks.com/?o=7474658274233226#job/61936309152043/run/631388168060027`
- Published AI/BI dashboard: `RetailPulse Demo Dashboard`
- Deterministic sample size:
  - `341,974` sampled orders
  - `3,267,191` sampled prior order rows
  - `137,847` sampled train order rows

## Review This Repo In 5 Minutes
1. Read [Showcase Summary](Docs/showcase-summary.md) for the finished project story and validated results.
2. Read [RetailPulse Handbook](Docs/RetailPulse%20Handbook.md) if you want the full explanation of what the project does and how to run it.
3. Use [Boss Brief](Docs/boss-brief.md) and [Demo Script](Docs/demo-script.md) for the live walkthrough order.
4. Inspect the screenshot evidence pack through [Evidence Pack](Docs/evidence-pack.md) and `assets/screenshots/`.
5. Read [Next Step Priority Plan](Docs/Next%20Step%20Priority%20Plan.md) if you want the recommended path after the current release freeze.

## Project Snapshot
- Dataset: Instacart order history, sampled deterministically at 10% of users
- Platform target: Databricks Free Edition, serverless-only
- Core outputs: Delta tables, persisted OLAP report tables, association rules, user segments, Experimental Insights metrics, replay-stream validation, and a published AI/BI dashboard
- Canonical notebook format: Databricks source notebooks in `.py`
- Convenience notebook format: generated `.ipynb` copies in `notebooks_ipynb/`

## What The Project Builds
- A bronze, silver, and gold Delta pipeline over sampled grocery-order data
- A star schema centered on `fact_order_items` and `fact_orders`
- OLAP analysis with `CUBE` and `ROLLUP`
- Serverless-safe pairwise association-rule mining for product recommendations
- Customer segmentation using KMeans
- An `Experimental Insights` lane with a decision-tree classifier for power-user prediction
- An `Experimental Insights` lane with a linear-regression model for basket-size prediction
- A file-based replay stream using `Trigger.AvailableNow`
- Optimize and benchmark evidence using `OPTIMIZE` and `ZORDER BY`
- A published AI/BI dashboard plus `12_report_pack.py` fallback for boss review and release evidence, both aligned to the five-page Dashboard V2 story

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
Gold -> OLAP, pairwise association rules, KMeans, Experimental Insights notebooks
Gold held-out slice -> Replay batches -> AvailableNow streaming aggregate
```

Assets:
- [retailpulse_medallion.mmd](assets/retailpulse_medallion.mmd)
- [retailpulse_star_schema.mmd](assets/retailpulse_star_schema.mmd)

## GitHub Showcase
| Successful run | Executive overview |
| --- | --- |
| ![Successful Databricks run](assets/screenshots/01_run_success.png) | ![Business overview and OLAP outputs](assets/screenshots/03_olap_outputs.png) |

| Recommendation proof | Execution evidence |
| --- | --- |
| ![Association rules and recommendation evidence](assets/screenshots/04_association_rules.png) | ![Streaming validation and execution evidence](assets/screenshots/08_stream_validation.png) |

Dashboard V2 is organized into five reviewer-facing pages:
1. `Executive Overview`
2. `Order Behavior`
3. `Recommendations And Segments`
4. `Execution And Data Quality`
5. `Experimental Insights And Performance`

For GitHub review, lead with business overview, recommendation proof, and execution evidence. Keep exploratory metrics visible, but not as the hero story.

More packaged evidence lives in `assets/screenshots/`, and the capture/source-of-truth rules live in [Docs/evidence-pack.md](Docs/evidence-pack.md).

## Current Results Snapshot

### Key table outputs
| Table | Rows |
| --- | ---: |
| `bronze_orders` | 341,974 |
| `silver_order_items` | 3,405,038 |
| `fact_order_items` | 3,405,038 |
| `fact_orders` | 334,438 |
| `mart_association_rules` | 49 |
| `stream_order_slot_metrics` | 158 |

### Experimental Insights metrics
| Metric | Value |
| --- | ---: |
| Decision-tree accuracy | 0.9136 |
| Decision-tree AUC | 0.8813 |
| Majority baseline accuracy | 0.7445 |
| Linear-regression R² | 0.5580 |
| Linear-regression RMSE | 5.0945 |
| Mean baseline RMSE | 7.6627 |

These Experimental Insights are retained for boss review and product discussion, but they are not operational KPIs or release gates. The current feature construction still needs a stricter leakage-safe redesign before final predictive claims or automated decisions.

### Recommendation example
- Seed product: `Organic Raspberries`
- Recommended consequent: `Bag of Organic Bananas` with confidence `0.3005` and lift `2.4723`
- Recommended consequent: `Organic Strawberries` with confidence `0.2384` and lift `2.8052`

### Segment summary
- Frequent loyal shoppers: `33.28` average orders, `9.20` average basket size, `65.21%` reorder rate
- Light occasional shoppers: `7.54` average orders, `6.63` average basket size, `35.94%` reorder rate
- Large-basket stock-up shoppers: `10.10` average orders, `17.12` average basket size, `44.02%` reorder rate

### Streaming and optimization
- Streaming replay validation checked `158` order-slot aggregates with `0` mismatches
- `OPTIMIZE` completed successfully, but the measured benchmark queries were slower on this small sample; the repo documents that outcome honestly rather than claiming an improvement

## Showcase Docs
- [Showcase Summary](Docs/showcase-summary.md)
- [Demo Script](Docs/demo-script.md)
- [RetailPulse Handbook](Docs/RetailPulse%20Handbook.md)
- [BI Integration And Visualization Strategy](Docs/BI%20Integration%20And%20Visualization%20Strategy.md)
- [Dashboard Spec](Docs/databricks-dashboard-spec.md)
- [Dashboard UI Guide](Docs/databricks-dashboard-ui-guide.md)
- [Evidence Pack](Docs/evidence-pack.md)
- [Canonical Dashboard Queries](sql/retailpulse_dashboard_queries.sql)
- [Executive Summary](Docs/Executive%20Summary.md)
- [14-Day Plan](Docs/Grocery%20Sales%20Analytics%20%26%20Recommendation%20on%20Databricks_%2014-Day%20Plan.md)
- [Ultimate 2-Week Guide](Docs/Ultimate%202-Week%20Databricks%20Project_%20Data%20Mining%20%26%20Warehousing.md)
- [Rebuild From Scratch](Docs/rebuild-from-scratch.md)
- [Original Blueprint](Docs/RetailPulse%20PLAN.md)

## Operations Docs
- [Current Production State](Docs/current-production-state.md)
- [Next Step Priority Plan](Docs/Next%20Step%20Priority%20Plan.md)
- [Production Runbook](Docs/production-runbook.md)
- [Release Checklist](Docs/release-checklist.md)
- [Boss Brief](Docs/boss-brief.md)
- [Dashboard Metadata](Docs/dashboard-metadata.md)
- [Release Smoke Checks](sql/release_smoke_checks.sql)

## Repository Layout
- `notebooks/`: canonical Databricks source notebooks
- `notebooks_ipynb/`: generated `.ipynb` mirrors for convenience and sharing
- `scripts/`: local helper scripts and notebook export tooling
- `sql/`: canonical Databricks SQL query definitions for AI/BI dashboard authoring
- `tests/`: local unit tests for Python utilities
- `resources/`: Databricks Asset Bundle resource definitions
- `Docs/`: report-facing, rebuild, and showcase documentation
- `.github/workflows/`: CI and manual Databricks automation

## Automation Files
- `databricks.yml`: bundle entrypoint and shared variables
- `resources/retailpulse_job_resource.yml`: sequential `retailpulse_full_rebuild` job definition
- `.github/workflows/ci.yml`: local validation on push and pull request
- `.github/workflows/run-databricks-bundle.yml`: manual Databricks validate, deploy, and run workflow

## Notebook Format Policy
The canonical notebook source lives in `notebooks/*.py`.

Why `.py` instead of `.ipynb`:
- Databricks officially supports source notebooks and Jupyter notebooks for import/export
- `.py` source notebooks diff cleanly in Git
- Code review is substantially easier in plain text
- Bundle-based deployment works naturally with source notebooks
- Deterministic generation of `.ipynb` is easier than deterministic maintenance of hand-edited notebook JSON

The rule for this repo is:
- Edit only `notebooks/*.py`
- Regenerate `notebooks_ipynb/*.ipynb` after notebook changes
- Commit both formats
- Treat `.ipynb` as a convenience mirror, not the source of truth

## Quick Start
### 0. Install Databricks CLI
Windows:
```powershell
winget install Databricks.DatabricksCLI
databricks version
```

If `databricks bundle` later fails with `No such command 'bundle'`, your shell is still pointing at the deprecated legacy CLI. On Windows, run `where databricks` and make sure the newer winget-installed Databricks CLI is ahead of the old Python-installed one in `PATH`.

Linux or macOS:
```bash
brew tap databricks/tap
brew install databricks
databricks version
```

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
This repo is set up for two automation levels.

### Local automation
- Use Databricks CLI for authentication
- Validate and deploy with Databricks Asset Bundles
- Run the end-to-end job locally when you want a full rebuild

### GitHub automation
- CI workflow runs local validation on push and pull request
- Databricks workflow is `workflow_dispatch` only
- Manual dispatch validates, deploys, and runs the full job
- GitHub secrets required:
  - `DATABRICKS_HOST`
  - `DATABRICKS_TOKEN`

This is deliberate. Databricks Free Edition is quota-limited and should not auto-run on every push.

## What Is Automated And What Is Still Manual
Automated:
- Workspace-authenticated bundle validation
- Bundle deployment
- Sequential notebook execution through `retailpulse_full_rebuild`
- GitHub-triggered manual Databricks runs

Still manual by design:
- Downloading the raw Instacart dataset
- Building the deterministic 10% local sample
- Uploading sampled CSV files into the raw Unity Catalog volume

The last point is intentional. The project explicitly avoids pulling Kaggle data from notebooks, and `01_sample_and_upload.py` is a validation checkpoint rather than a downloader.

## Core Commands
### Local validation
```powershell
python -m unittest -q tests.test_sample_instacart tests.test_split_stream_replay_batches tests.test_export_databricks_source_to_ipynb
python -m py_compile scripts\sample_instacart.py scripts\split_stream_replay_batches.py scripts\export_databricks_source_to_ipynb.py
python scripts/export_databricks_source_to_ipynb.py --check
databricks bundle validate -t dev
```

### Regenerate `.ipynb`
```powershell
python scripts/export_databricks_source_to_ipynb.py
```

### Run the full job from GitHub
- Open the `Run Databricks Bundle` workflow in GitHub Actions
- Click `Run workflow`
- Keep the `dev` target unless you define more bundle targets later

### Automatic Databricks execution after one-time setup
If your question is whether the repo can connect to Databricks and run all notebooks automatically, the answer is yes after two prerequisites are satisfied:
1. Databricks CLI authentication is configured locally or through GitHub secrets.
2. The sampled CSV files are already uploaded to the raw volume.

After that, either of these is enough:
```powershell
databricks bundle deploy -t dev
databricks bundle run retailpulse_full_rebuild -t dev
```

Or, from GitHub Actions:
- Run `.github/workflows/run-databricks-bundle.yml`
- Provide the `dev` target
- Let the workflow validate, deploy, and run the bundle job

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
- Association-rule mining produces non-trivial rules and at least three recommendations for a seed basket
- KMeans returns centroid summaries for `k in {3,4,5}`
- Classifier and regression outputs remain available as `Experimental Insights` and are explicitly documented as non-operational
- Replay stream output matches the equivalent batch aggregate
- Bundle validation passes without manual notebook path edits

## Screenshots And Report Artifacts
Use these in the GitHub repo and final report:
- Architecture diagram
- Star schema diagram
- Executive overview and OLAP visuals
- Order-behavior visuals such as orders by day and top products
- Recommendation proof and seed-product recommendations
- Cluster profiles and cluster-k selection evidence
- Classifier metrics and classifier feature importance
- Regression metrics
- Replay-stream validation and OLAP validation
- Optimize timing comparison

The demo evidence set now lives under `assets/screenshots/`, and the capture checklist lives in `Docs/evidence-pack.md`. Dashboard V2 expands the evidence pack through `15_olap_validation.png`. If you later capture cleaner UI-native dashboard screenshots, keep the same filenames and replace them in place.

For GitHub review, the top-priority files are:
- `assets/screenshots/01_run_success.png`
- `assets/screenshots/03_olap_outputs.png`
- `assets/screenshots/04_association_rules.png`
- `assets/screenshots/08_stream_validation.png`
- `assets/screenshots/10_orders_by_day.png`
- `assets/screenshots/12_seed_recommendations.png`
- `assets/screenshots/13_cluster_k_scores.png`
- `assets/screenshots/15_olap_validation.png`
- `Docs/showcase-summary.md`
- `Docs/RetailPulse Handbook.md`
- `Docs/databricks-dashboard-spec.md`

## Troubleshooting
### Why are the notebooks in `.py` instead of `.ipynb`?
Because `.py` is the reviewable source of truth in Git. The repo still provides generated `.ipynb` copies for people who prefer Jupyter-format files.

### Can I run everything automatically in Databricks?
Yes, once the sampled raw CSVs are uploaded. The Databricks Asset Bundle defines a single sequential multi-task job, and GitHub Actions can validate, deploy, and run it manually through `workflow_dispatch`.

### Why does `databricks bundle` say `No such command 'bundle'`?
Because the shell is usually resolving the deprecated legacy Databricks CLI instead of the newer bundle-capable CLI. Fix `PATH`, verify `where databricks` on Windows, and make sure the newer Databricks CLI is the one being executed before you try bundle commands again.

### Why does the recommendation notebook not use FP-growth?
The final Databricks Free Edition serverless implementation uses pairwise association-rule mining instead. In this workspace, Spark Connect serverless was not a reliable path for `FPGrowth`, so the recommendation step was adapted to a submission-safe implementation that still writes `mart_association_rules` and supports seed-product recommendations.

### Why did the optimize benchmark get slower?
Because the dataset sample is small. The benchmark was still run and recorded honestly, but `OPTIMIZE` plus `ZORDER BY` did not improve those two measured queries on this specific sample size.

### Can I use MLflow or extend the dashboard later?
Yes. MLflow is still future work. The AI/BI dashboard is already published in the current workspace; future work is dashboard export automation, richer filters, and cleaner UI-native screenshot refreshes.

### Can I connect RetailPulse to Power BI or Tableau?
Yes, but the current recommendation is Databricks dashboard first and Power BI Desktop second. The comparison, supported vendor paths, and CLI/MCP reality are documented in `Docs/BI Integration And Visualization Strategy.md`. There is no Power BI or Tableau MCP server configured in this environment today.

### Should I build more models right now?
No. The current priority is release hardening, dashboard polish, and boss-facing walkthrough stability. The short roadmap is documented in `Docs/Next Step Priority Plan.md`. More supervised-model work should wait unless ML rigor becomes the top evaluation criterion.

## Future Works
The following items were in the broader original vision but are not part of the current implemented scope:
- MLflow experiment tracking for models and artifacts
- Dashboard-as-code export, richer filters, and refreshed UI-native dashboard screenshots
- Synthetic `product_price_map` plus `estimated_sales_amount`
- A second supervised model such as RandomForest
- Richer streaming via Kafka, Auto Loader, or paid-tier continuous streaming
- An RDD-style Hadoop demo on non-serverless compute

## References
- Databricks notebook import/export formats: https://docs.databricks.com/gcp/en/notebooks/notebook-export-import
- Databricks CLI install: https://docs.databricks.com/aws/en/dev-tools/cli/install
- Databricks CLI authentication: https://docs.databricks.com/aws/en/dev-tools/cli/authentication
- Databricks CLI workspace commands: https://docs.databricks.com/gcp/en/dev-tools/cli/reference/workspace-commands
- Databricks bundle commands: https://docs.databricks.com/aws/en/dev-tools/cli/bundle-commands
- Databricks Asset Bundles: https://docs.databricks.com/aws/en/dev-tools/bundles/
- Databricks GitHub CI/CD guidance: https://docs.databricks.com/gcp/en/dev-tools/ci-cd/github
- Databricks Free Edition limitations: https://docs.databricks.com/aws/en/getting-started/free-edition-limitations
