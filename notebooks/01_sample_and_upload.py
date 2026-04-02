# Databricks notebook source
# MAGIC %md
# MAGIC # Sample And Upload Validation
# MAGIC
# MAGIC Sampling happens locally. This notebook validates that the sampled CSV files were uploaded to the raw Unity Catalog volume before bronze ingestion starts.

# COMMAND ----------
from pyspark.sql import functions as F

dbutils.widgets.text("catalog", "")
dbutils.widgets.text("schema", "retailpulse")
dbutils.widgets.text("raw_volume", "retailpulse_raw")

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

uploaded = {item.name.rstrip("/") for item in dbutils.fs.ls(raw_root)}
status_rows = [(name, name in uploaded, f"{raw_root}/{name}") for name in required_files]
display(spark.createDataFrame(status_rows, ["file_name", "present", "path"]))

missing = [name for name in required_files if name not in uploaded]
assert not missing, f"Missing uploaded files: {', '.join(missing)}"

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
# MAGIC ```powershell
# MAGIC python scripts/sample_instacart.py `
# MAGIC   --input-dir C:\path\to\instacart_raw `
# MAGIC   --output-dir C:\path\to\retailpulse_sample
# MAGIC ```

