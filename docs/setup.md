# Setup

Requires Git, Python 3.11 or newer, the Databricks CLI 0.205.x or newer, and the six raw Instacart CSVs (`orders`, `order_products__prior`, `order_products__train`, `products`, `aisles`, `departments`).

```bash
git clone https://github.com/The-Harsh-Vardhan/RetailPulse.git
cd RetailPulse
python scripts/sample_instacart.py --input-dir /path/to/instacart_raw --output-dir /path/to/retailpulse_sample
python -m unittest -q tests.test_sample_instacart tests.test_split_stream_replay_batches tests.test_export_databricks_source_to_ipynb
databricks auth login --host https://<your-workspace-host>
databricks bundle validate -t dev
databricks bundle deploy -t dev
```

Upload the sampled CSVs to `/Volumes/<catalog>/<schema>/<raw_volume>/` (a manual step), then run:

```bash
databricks bundle run retailpulse_full_rebuild -t dev
```

Review `RetailPulse Demo Dashboard` first, then `notebooks/12_report_pack.py` as a fallback. The full guide, including adapting to a new dataset, is in `HOW TO USE.md` in the repository.
