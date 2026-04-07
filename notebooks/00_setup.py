# Databricks notebook source
# MAGIC %md
# MAGIC # RetailPulse Setup
# MAGIC
# MAGIC This notebook provisions the Databricks schema and Unity Catalog volumes that the rest of the RetailPulse workflow expects.
# MAGIC
# MAGIC ## Run Inputs
# MAGIC - `catalog`: optional override for the active catalog
# MAGIC - `schema`: schema that will store RetailPulse tables
# MAGIC - `raw_volume`: volume used for sampled CSV uploads
# MAGIC - `replay_volume`: volume used for replay-batch files
# MAGIC - `checkpoint_volume`: volume used for streaming checkpoints
# MAGIC
# MAGIC ## Outputs
# MAGIC - The target schema in the selected catalog
# MAGIC - Three Unity Catalog volumes for raw uploads, replay batches, and checkpoints
# MAGIC - A path summary table that the operator can use in the next notebook
# MAGIC
# MAGIC ## Workflow
# MAGIC 1. Capture the runtime widgets.
# MAGIC 2. Resolve the active catalog and schema.
# MAGIC 3. Create the schema and required volumes idempotently.
# MAGIC 4. Display the provisioned paths for the upload and replay steps.

# COMMAND ----------
# MAGIC %md
# MAGIC ## Capture Runtime Inputs
# MAGIC
# MAGIC These widgets keep the notebook reusable across different workspace defaults without editing the source file.

# COMMAND ----------
dbutils.widgets.text("catalog", "")
dbutils.widgets.text("schema", "retailpulse")
dbutils.widgets.text("raw_volume", "retailpulse_raw")
dbutils.widgets.text("replay_volume", "retailpulse_replay")
dbutils.widgets.text("checkpoint_volume", "retailpulse_checkpoints")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Resolve Catalog Context
# MAGIC
# MAGIC The helper functions centralize identifier quoting and volume-path construction so later notebooks can follow the same pattern safely.

# COMMAND ----------
catalog = dbutils.widgets.get("catalog") or spark.sql("SELECT current_catalog()").first()[0]
schema = dbutils.widgets.get("schema") or spark.sql("SELECT current_schema()").first()[0]
raw_volume = dbutils.widgets.get("raw_volume")
replay_volume = dbutils.widgets.get("replay_volume")
checkpoint_volume = dbutils.widgets.get("checkpoint_volume")


# Keep identifier quoting centralized so custom catalog or schema names remain safe in SQL.
def qname(*parts: str) -> str:
    return ".".join(f"`{part}`" for part in parts)


def volume_path(volume: str, *parts: str) -> str:
    suffix = "/".join(parts)
    base = f"/Volumes/{catalog}/{schema}/{volume}"
    return f"{base}/{suffix}" if suffix else base


assert catalog, "A catalog is required."
assert schema, "A schema is required."

# COMMAND ----------
# MAGIC %md
# MAGIC ## Create Schema And Volumes
# MAGIC
# MAGIC This cell is safe to rerun. It creates the target schema first and then provisions each volume only if it does not already exist.

# COMMAND ----------
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {qname(catalog, schema)}")
spark.sql(f"USE CATALOG {qname(catalog)}")
spark.sql(f"USE SCHEMA {qname(schema)}")

for volume in (raw_volume, replay_volume, checkpoint_volume):
    spark.sql(f"CREATE VOLUME IF NOT EXISTS {qname(catalog, schema, volume)}")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Review Provisioned Paths
# MAGIC
# MAGIC Use the displayed volume paths when you upload sampled CSV files or troubleshoot the replay-stream setup later in the workflow.

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
# MAGIC 1. Run `scripts/sample_instacart.py` locally to prepare the deterministic sample.
# MAGIC 2. Upload the sampled CSV files to the raw volume path shown above.
# MAGIC 3. Continue with `01_sample_and_upload` to validate the uploaded files before bronze ingestion.
