# Rebuild RetailPulse From Scratch

This guide explains how to rebuild RetailPulse from a fresh clone, from local dataset prep through a full Databricks run.

## 1. Prerequisites
### Local machine
- Python 3.11+ or equivalent recent Python
- Git
- Databricks CLI 0.205+
- A Databricks Free Edition workspace

### GitHub
- A fork or write access to the repository
- Optional GitHub Actions secrets:
  - `DATABRICKS_HOST`
  - `DATABRICKS_TOKEN`

### Dataset
Download the raw Instacart CSV files:
- `orders.csv`
- `order_products__prior.csv`
- `order_products__train.csv`
- `products.csv`
- `aisles.csv`
- `departments.csv`

## 2. Clone The Repository
```powershell
git clone https://github.com/The-Harsh-Vardhan/RetailPulse.git
cd RetailPulse
```

## 3. Run Local Validation First
```powershell
python -m unittest -q tests.test_sample_instacart tests.test_split_stream_replay_batches
python -m py_compile scripts\sample_instacart.py scripts\split_stream_replay_batches.py scripts\export_databricks_source_to_ipynb.py
```

## 4. Create The Deterministic 10% Sample
Run the local sampling tool against the raw Instacart files:

```powershell
python scripts/sample_instacart.py `
  --input-dir C:\path\to\instacart_raw `
  --output-dir C:\path\to\retailpulse_sample
```

Expected outputs:
- sampled `orders.csv`
- filtered `order_products__prior.csv`
- filtered `order_products__train.csv`
- copied lookup files
- `sample_manifest.json`

## 5. Regenerate `.ipynb` Copies
The repo treats `notebooks/*.py` as the source of truth. Generate convenience notebook copies with:

```powershell
python scripts/export_databricks_source_to_ipynb.py
```

To confirm nothing drifted:

```powershell
python scripts/export_databricks_source_to_ipynb.py --check
```

## 6. Authenticate Databricks CLI
Preferred local flow:

```powershell
databricks auth login --host https://<your-workspace-host>
```

If you are using a token:

```powershell
databricks configure --host https://<your-workspace-host>
```

Confirm the profile:

```powershell
databricks auth profiles
```

## 7. Configure Bundle Variables
RetailPulse uses these bundle variables:
- `catalog`
- `schema`
- `raw_volume`
- `replay_volume`
- `checkpoint_volume`
- `batch_count`
- `replay_order_limit`

Defaults should work for the provided Free Edition flow, but you can override them through bundle targets or `--var` flags when needed.

## 8. Validate The Bundle
```powershell
databricks bundle validate -t dev
```

This should confirm:
- notebook paths resolve
- job resources parse correctly
- variables are present

## 9. Upload The Sampled CSV Files
Use the Databricks workspace UI to upload the sampled CSV files into the raw Unity Catalog volume defined by `00_setup.py`, or use Databricks CLI workspace/volume commands if available in your setup.

The notebook sequence assumes the sampled raw files are already in the raw volume before bronze ingest begins.

## 10. Deploy The Bundle
```powershell
databricks bundle deploy -t dev
```

This creates or updates the Databricks job resources for RetailPulse.

## 11. Run The Full Workflow
```powershell
databricks bundle run retailpulse_full_rebuild -t dev
```

The bundle job should execute the notebooks sequentially:
1. `00_setup`
2. `01_sample_and_upload`
3. `02_bronze_ingest`
4. `03_silver_transform`
5. `04_gold_model`
6. `05_olap`
7. `06_association_rules`
8. `07_clustering`
9. `08_classifier`
10. `09_regression`
11. `10_streaming_replay`
12. `11_optimize`
13. `12_report_pack`

## 12. Collect Final Artifacts
After the run completes, collect:
- Delta tables
- OLAP outputs
- top association rules
- cluster profiles
- classifier metrics
- regression metrics
- replay-stream validation
- optimize timing results

Use `12_report_pack.py` as the structured summary notebook for report capture.

## 13. GitHub Actions Setup
To enable the manual-dispatch Databricks workflow in GitHub:
1. Open the repo settings in GitHub.
2. Add secrets:
   - `DATABRICKS_HOST`
   - `DATABRICKS_TOKEN`
3. Push the workflow files to `main`.
4. Open the Actions tab and run the Databricks workflow manually.

Expected behavior:
- push and PR workflows run local checks only
- Databricks deploy/run is manual via `workflow_dispatch`

## 14. Recommended Rebuild Checklist
- Pull latest changes
- Re-run tests
- Re-run notebook export
- Validate bundle
- Confirm sampled data is available
- Deploy bundle
- Run full rebuild
- Capture report outputs
- Regenerate `.ipynb` and commit if notebooks changed

## 15. Common Failure Modes
### Bundle validates but run fails
- Recheck Databricks authentication
- Recheck notebook paths in the bundle
- Recheck that uploaded CSVs exist in the raw volume

### `01_sample_and_upload` fails
- One or more sampled CSV files are missing from the Databricks raw volume

### Streaming replay fails
- Check volume write permissions
- Check checkpoint path reuse
- Keep `Trigger.AvailableNow`; do not switch to continuous triggers on Free Edition

### `.ipynb` files look stale
- Run `python scripts/export_databricks_source_to_ipynb.py`
- Commit regenerated files after notebook edits

## 16. Future Extensions
If you rebuild this repo and want to go beyond the current scope, start with:
- MLflow run tracking
- dashboard publishing
- synthetic price mapping
- a second supervised model
- richer streaming on a paid tier
- a non-serverless Hadoop/RDD demo

