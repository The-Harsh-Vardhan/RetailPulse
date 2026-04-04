# Rebuild RetailPulse From Scratch

This guide is the end-to-end rebuild path for a new machine, a new Databricks workspace, or a new contributor. It covers local setup, sampling, notebook export, Databricks authentication, first workspace bootstrap, data upload, bundle deployment, job execution, and GitHub Actions.

## Goal
By the end of this guide you should have:
- The repository cloned locally
- A deterministic 10% Instacart sample created locally
- `.ipynb` mirrors regenerated from the canonical Databricks source notebooks
- A Databricks Free Edition workspace authenticated through the Databricks CLI
- The `retailpulse_full_rebuild` bundle job deployed
- The full notebook sequence executed in Databricks after raw sample upload

## 1. Prerequisites

### Local tools
- Git
- Python 3.11 or newer
- Databricks CLI 0.205 or newer

### Platform
- A Databricks Free Edition workspace
- Permission to create a schema and Unity Catalog volumes in that workspace

### Dataset
Download these CSV files from the Instacart dataset source you are authorized to use:
- `orders.csv`
- `order_products__prior.csv`
- `order_products__train.csv`
- `products.csv`
- `aisles.csv`
- `departments.csv`

## 2. Install Databricks CLI

Preferred Windows install:
```powershell
winget search databricks
winget install Databricks.DatabricksCLI
databricks version
```

Preferred Linux or macOS install:
```bash
brew tap databricks/tap
brew install databricks
databricks version
```

If `databricks version` does not report `0.205.x` or newer, update the CLI before continuing.

## 3. Clone The Repository
```powershell
git clone https://github.com/The-Harsh-Vardhan/RetailPulse.git
cd RetailPulse
```

## 4. Understand The Notebook Format Rule
RetailPulse keeps Databricks source notebooks in `notebooks/*.py` as the editable source of truth.

Generated mirrors live in `notebooks_ipynb/*.ipynb`.

The maintenance rule is:
- Edit only `notebooks/*.py`
- Regenerate `.ipynb` mirrors after notebook changes
- Commit both formats when notebooks change

## 5. Run Local Validation Before Touching Databricks
```powershell
python -m unittest -q tests.test_sample_instacart tests.test_split_stream_replay_batches tests.test_export_databricks_source_to_ipynb
python -m py_compile notebooks\*.py scripts\*.py tests\*.py
python scripts/export_databricks_source_to_ipynb.py --check
```

If the exporter check fails, regenerate notebooks and rerun it:
```powershell
python scripts/export_databricks_source_to_ipynb.py
python scripts/export_databricks_source_to_ipynb.py --check
```

## 6. Build The Deterministic 10% Sample Locally
Run the local sampler against your raw Instacart download:

```powershell
python scripts/sample_instacart.py `
  --input-dir C:\path\to\instacart_raw `
  --output-dir C:\path\to\retailpulse_sample
```

Expected outputs in the sample directory:
- Sampled `orders.csv`
- Filtered `order_products__prior.csv`
- Filtered `order_products__train.csv`
- Copied `products.csv`
- Copied `aisles.csv`
- Copied `departments.csv`
- `sample_manifest.json`

## 7. Regenerate The `.ipynb` Mirrors
```powershell
python scripts/export_databricks_source_to_ipynb.py
```

This produces one mirror notebook per source notebook under `notebooks_ipynb/`.

## 8. Authenticate Databricks CLI

### Local development
Preferred local authentication is OAuth user-to-machine:
```powershell
databricks auth login --host https://<your-workspace-host>
```

The CLI opens a browser flow and stores a profile for later use.

Useful verification commands:
```powershell
databricks auth profiles
databricks current-user me
```

### GitHub Actions
The manual GitHub Actions workflow currently expects:
- `DATABRICKS_HOST`
- `DATABRICKS_TOKEN`

That keeps unattended automation simple. Locally, prefer OAuth over long-lived tokens.

## 9. Review The Bundle Structure
Important files:
- `databricks.yml`
- `resources/retailpulse_job_resource.yml`
- `.github/workflows/ci.yml`
- `.github/workflows/run-databricks-bundle.yml`

Shared bundle variables:
- `catalog`
- `schema`
- `raw_volume`
- `replay_volume`
- `checkpoint_volume`
- `batch_count`
- `replay_order_limit`

Default target:
- `dev`

Default workspace sync path:
```text
/Workspace/Users/<your-user>/.bundle/retailpulse/dev
```

## 10. Validate And Deploy The Bundle
```powershell
databricks bundle validate -t dev
databricks bundle deploy -t dev
```

What this does:
- Validates bundle syntax and notebook paths
- Syncs the repo files needed by the bundle to the workspace
- Creates or updates the `retailpulse_full_rebuild` job

## 11. Bootstrap The Workspace Once Before The Full Run
This project has one intentional manual checkpoint: raw data upload.

Why:
- The project does not pull Kaggle data from notebooks
- `01_sample_and_upload.py` is a validator, not a downloader
- The raw Unity Catalog volume must exist before you can upload sampled CSVs

### First bootstrap sequence
1. Deploy the bundle.
2. Open the synced `00_setup.py` notebook in Databricks.
3. Run `00_setup.py` once to create the schema and volumes.
4. Note the raw volume path shown by the notebook output.
5. Upload the sampled CSV files from your local `retailpulse_sample` directory into that raw volume.

The raw upload path format is:
```text
/Volumes/<catalog>/<schema>/<raw_volume>/
```

If you leave `catalog` blank, the notebook falls back to the workspace current catalog.

## 12. Upload The Sampled CSV Files
Upload these sampled files into the raw volume:
- `orders.csv`
- `order_products__prior.csv`
- `order_products__train.csv`
- `products.csv`
- `aisles.csv`
- `departments.csv`

Important:
- Use the sampled files for `orders` and the two `order_products` files
- Use the lookup files as-is
- Do not rename the files

## 13. Run The Full Databricks Workflow
After the upload is complete:
```powershell
databricks bundle run retailpulse_full_rebuild -t dev
```

The job runs these notebooks in order:
1. `00_setup.py`
2. `01_sample_and_upload.py`
3. `02_bronze_ingest.py`
4. `03_silver_transform.py`
5. `04_gold_model.py`
6. `05_olap.py`
7. `06_association_rules.py`
8. `07_clustering.py`
9. `08_classifier.py`
10. `09_regression.py`
11. `10_streaming_replay.py`
12. `11_optimize.py`
13. `12_report_pack.py`

## 14. What To Expect From Each Stage

### Bronze
- Raw CSVs land in Delta tables with explicit schemas
- Row-count checks should align with uploaded files

### Silver
- Prior and train order items are unified
- Products are enriched with aisle and department attributes
- User history features are materialized

### Gold
- Dimensions and fact tables are created
- User mart and association-rule mart are created
- Replay-stream metrics table is written after the streaming notebook

### Analytics And ML
- OLAP outputs should show `CUBE` and `ROLLUP` totals
- Association-rule mining should produce non-trivial rules
- KMeans should evaluate `k = 3, 4, 5`
- Classifier should beat the majority baseline
- Regression should beat the mean baseline or be treated as exploratory

## 15. Collect Final Artifacts
After a successful run, capture:
- Screenshots of OLAP outputs
- Top association rules
- Cluster summaries
- Classifier metrics
- Regression metrics
- Replay-stream versus batch validation
- Optimize timing evidence

Use `12_report_pack.py` to assemble the final report-facing outputs.

For the finished demo package, also use:
- `Docs/showcase-summary.md`
- `Docs/demo-script.md`

## 16. Run Through GitHub Actions Instead Of The Local CLI
If you want GitHub to trigger the deploy-and-run flow after setup:

1. Push this repository to GitHub.
2. Open repository settings.
3. Add secrets:
   - `DATABRICKS_HOST`
   - `DATABRICKS_TOKEN`
4. Go to the Actions tab.
5. Run `Run Databricks Bundle`.
6. Keep the `dev` target unless you define more targets later.

Behavior:
- `CI` runs on push and pull request
- `Run Databricks Bundle` is manual only
- The manual workflow validates, deploys, and runs the Databricks bundle job

## 17. Common Failure Modes

### `databricks bundle validate -t dev` fails
- Verify the CLI version
- Verify authentication
- Verify that you are running the command from the repo root

### `01_sample_and_upload.py` fails
- One or more required CSV files are missing from the raw volume
- A file was uploaded under the wrong name
- The files were uploaded to the wrong catalog, schema, or volume

### Streaming replay fails
- The replay or checkpoint volume paths are wrong
- The workspace does not allow the target path
- You changed the notebook away from `Trigger.AvailableNow`

### `.ipynb` files drift from `.py`
- Rerun `python scripts/export_databricks_source_to_ipynb.py`
- Rerun `python scripts/export_databricks_source_to_ipynb.py --check`
- Commit the regenerated mirrors

## 18. Rebuild Checklist
- Clone the repo
- Install the Databricks CLI
- Run local tests
- Create the local sample
- Regenerate `.ipynb`
- Authenticate Databricks CLI
- Validate and deploy the bundle
- Run `00_setup.py` once
- Upload sampled CSVs
- Run `retailpulse_full_rebuild`
- Collect outputs from `12_report_pack.py`

## 19. Future Extensions
Not yet implemented in the current submission-safe scope:
- MLflow experiment tracking
- Databricks SQL or AI/BI dashboard
- Synthetic `product_price_map` with `estimated_sales_amount`
- Second supervised model such as RandomForest
- Richer streaming via Kafka, Auto Loader, or paid-tier continuous streaming
- RDD-style Hadoop demo on non-serverless compute
