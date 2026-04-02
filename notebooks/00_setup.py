# Databricks notebook source
# MAGIC %md
# MAGIC # RetailPulse Setup
# MAGIC
# MAGIC This notebook prepares the Databricks Free Edition workspace for the rest of the project. It creates the schema and the Unity Catalog volumes used for raw uploads, replay batches, and checkpoints.

# COMMAND ----------
dbutils.widgets.text("catalog", "")
dbutils.widgets.text("schema", "retailpulse")
dbutils.widgets.text("raw_volume", "retailpulse_raw")
dbutils.widgets.text("replay_volume", "retailpulse_replay")
dbutils.widgets.text("checkpoint_volume", "retailpulse_checkpoints")

# COMMAND ----------
catalog = dbutils.widgets.get("catalog") or spark.sql("SELECT current_catalog()").first()[0]
schema = dbutils.widgets.get("schema") or spark.sql("SELECT current_schema()").first()[0]
raw_volume = dbutils.widgets.get("raw_volume")
replay_volume = dbutils.widgets.get("replay_volume")
checkpoint_volume = dbutils.widgets.get("checkpoint_volume")


def qname(*parts: str) -> str:
    return ".".join(f"`{part}`" for part in parts)


def volume_path(volume: str, *parts: str) -> str:
    suffix = "/".join(parts)
    base = f"/Volumes/{catalog}/{schema}/{volume}"
    return f"{base}/{suffix}" if suffix else base


assert catalog, "A catalog is required."
assert schema, "A schema is required."

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {qname(catalog, schema)}")
spark.sql(f"USE CATALOG {qname(catalog)}")
spark.sql(f"USE SCHEMA {qname(schema)}")

for volume in (raw_volume, replay_volume, checkpoint_volume):
    spark.sql(f"CREATE VOLUME IF NOT EXISTS {qname(catalog, schema, volume)}")

# COMMAND ----------
paths = [
    ("catalog", catalog),
    ("schema", schema),
    ("raw_volume_path", volume_path(raw_volume)),
    ("replay_volume_path", volume_path(replay_volume)),
    ("checkpoint_volume_path", volume_path(checkpoint_volume)),
]

display(spark.createDataFrame(paths, ["item", "value"]))

# COMMAND ----------
# MAGIC %md
# MAGIC ## Next Step
# MAGIC
# MAGIC 1. Run `scripts/sample_instacart.py` locally.
# MAGIC 2. Upload the sampled CSV files to the raw volume shown above.
# MAGIC 3. Continue with `01_sample_and_upload`.

