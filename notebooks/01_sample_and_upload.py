# Databricks notebook source
# MAGIC %md
# MAGIC # Sample And Upload Validation
# MAGIC
# MAGIC Sampling happens locally. This notebook verifies that the expected sampled CSV files were uploaded to the raw Unity Catalog volume before bronze ingestion begins.
# MAGIC
# MAGIC ## Run Inputs
# MAGIC - `catalog`: optional override for the active catalog
# MAGIC - `schema`: schema that holds the RetailPulse volumes
# MAGIC - `raw_volume`: volume that should contain the sampled CSV files
# MAGIC
# MAGIC ## Source Inputs
# MAGIC - Uploaded sample files in `/Volumes/<catalog>/<schema>/<raw_volume>/`
# MAGIC - Required filenames:
# MAGIC   - `orders.csv`
# MAGIC   - `order_products__prior.csv`
# MAGIC   - `order_products__train.csv`
# MAGIC   - `products.csv`
# MAGIC   - `aisles.csv`
# MAGIC   - `departments.csv`
# MAGIC
# MAGIC ## Outputs
# MAGIC - A presence-check table for every required file
# MAGIC - A lightweight row-count preview for each CSV
# MAGIC - A hard failure if any required upload is missing
# MAGIC
# MAGIC ## Workflow
# MAGIC 1. Resolve the raw volume path from widgets.
# MAGIC 2. Confirm every required file is present.
# MAGIC 3. Preview row counts so operators can catch empty uploads early.

# COMMAND ----------
# MAGIC %md
# MAGIC ## Capture Runtime Inputs
# MAGIC
# MAGIC The notebook stays read-only. Its purpose is to gate the bronze step, not to mutate the uploaded files.

# COMMAND ----------
dbutils.widgets.text("catalog", "")
dbutils.widgets.text("schema", "retailpulse")
dbutils.widgets.text("raw_volume", "retailpulse_raw")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Resolve The Raw Volume Path
# MAGIC
# MAGIC This path becomes the single source of truth for the upload checkpoint used by the bronze ingest notebook.

# COMMAND ----------
catalog = dbutils.widgets.get("catalog") or spark.sql("SELECT current_catalog()").first()[0]
schema = dbutils.widgets.get("schema") or spark.sql("SELECT current_schema()").first()[0]
raw_volume = dbutils.widgets.get("raw_volume")
raw_root = f"/Volumes/{catalog}/{schema}/{raw_volume}"

required_files = [
    "orders.csv",
    "order_products__prior.csv",
    "order_products__train.csv",
    "products.csv",
    "aisles.csv",
    "departments.csv",
]

# COMMAND ----------
# MAGIC %md
# MAGIC ## Validate Required Uploads
# MAGIC
# MAGIC Treat the volume listing as the gate before reading any CSV content. This fails fast when a file is missing or uploaded under the wrong name.

# COMMAND ----------
uploaded = {item.name.rstrip("/") for item in dbutils.fs.ls(raw_root)}
status_rows = [(name, name in uploaded, f"{raw_root}/{name}") for name in required_files]
display(spark.createDataFrame(status_rows, ["file_name", "present", "path"]))

missing = [name for name in required_files if name not in uploaded]
assert not missing, f"Missing uploaded files: {', '.join(missing)}"

# COMMAND ----------
# MAGIC %md
# MAGIC ## Preview Row Counts
# MAGIC
# MAGIC These counts are not a full contract test, but they are enough to catch empty or obviously wrong uploads before bronze tables are overwritten.

# COMMAND ----------
preview_counts = []
for name in required_files:
    count = (
        spark.read.option("header", True)
        .csv(f"{raw_root}/{name}")
        .count()
    )
    preview_counts.append((name, count))

display(spark.createDataFrame(preview_counts, ["file_name", "row_count"]))

# COMMAND ----------
# MAGIC %md
# MAGIC ## Local Sampling Command
# MAGIC
# MAGIC If you need to rebuild the sampled files locally, use the deterministic sampler before re-uploading:
# MAGIC
# MAGIC ```powershell
# MAGIC python scripts/sample_instacart.py `
# MAGIC   --input-dir C:\path\to\instacart_raw `
# MAGIC   --output-dir C:\path\to\retailpulse_sample
# MAGIC ```
# MAGIC
# MAGIC Once the required files are present and non-empty, continue with `02_bronze_ingest`.
