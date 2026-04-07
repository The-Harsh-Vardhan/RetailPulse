# Databricks notebook source
# MAGIC %md
# MAGIC # Streaming Replay
# MAGIC
# MAGIC Databricks Free Edition serverless only supports `Trigger.AvailableNow`, so this notebook creates a held-out replay slice, writes multiple CSV files, streams them into `stream_order_slot_metrics`, and validates the result.
# MAGIC
# MAGIC ## Run Inputs
# MAGIC - `catalog`: optional override for the active catalog
# MAGIC - `schema`: schema that contains the fact tables and stream outputs
# MAGIC - `replay_volume`: volume used for generated replay CSV files
# MAGIC - `checkpoint_volume`: volume used for streaming checkpoints
# MAGIC - `batch_count`: number of replay files to create
# MAGIC - `replay_order_limit`: maximum number of held-out orders used for replay
# MAGIC
# MAGIC ## Source Table
# MAGIC - `fact_orders`
# MAGIC
# MAGIC ## Output Tables
# MAGIC - `stream_order_slot_metrics`
# MAGIC - `report_stream_validation`
# MAGIC
# MAGIC ## Workflow
# MAGIC 1. Resolve the replay and checkpoint paths.
# MAGIC 2. Build a deterministic held-out replay slice from `fact_orders`.
# MAGIC 3. Write the slice as multiple CSV batches.
# MAGIC 4. Run an `AvailableNow` stream into a Delta table.
# MAGIC 5. Validate the streamed aggregates against the batch aggregates.

# COMMAND ----------
# MAGIC %md
# MAGIC ## Capture Runtime Inputs
# MAGIC
# MAGIC This notebook intentionally owns and resets its replay state on each run so the validation compares one clean replay slice at a time.

# COMMAND ----------
from pyspark.sql import Window, functions as F

dbutils.widgets.text("catalog", "")
dbutils.widgets.text("schema", "retailpulse")
dbutils.widgets.text("replay_volume", "retailpulse_replay")
dbutils.widgets.text("checkpoint_volume", "retailpulse_checkpoints")
dbutils.widgets.text("batch_count", "4")
dbutils.widgets.text("replay_order_limit", "4000")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Resolve Context And Replay Paths
# MAGIC
# MAGIC The helper keeps the two managed volume paths deterministic so reruns clear only the state owned by this notebook.

# COMMAND ----------
catalog = dbutils.widgets.get("catalog") or spark.sql("SELECT current_catalog()").first()[0]
schema = dbutils.widgets.get("schema") or spark.sql("SELECT current_schema()").first()[0]
replay_volume = dbutils.widgets.get("replay_volume")
checkpoint_volume = dbutils.widgets.get("checkpoint_volume")
batch_count = int(dbutils.widgets.get("batch_count"))
replay_order_limit = int(dbutils.widgets.get("replay_order_limit"))


def qname(name: str) -> str:
    return f"`{catalog}`.`{schema}`.`{name}`"


def volume_path(volume: str, *parts: str) -> str:
    suffix = "/".join(parts)
    base = f"/Volumes/{catalog}/{schema}/{volume}"
    return f"{base}/{suffix}" if suffix else base


fact_orders = spark.table(qname("fact_orders"))
replay_root = volume_path(replay_volume, "stream_input")
checkpoint_root = volume_path(checkpoint_volume, "stream_order_slot_metrics")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Reset Replay State
# MAGIC
# MAGIC Reruns must clear the previous replay files, checkpoint state, and target tables so the comparison stays one-to-one with the newly generated slice.

# COMMAND ----------
dbutils.fs.rm(replay_root, True)
dbutils.fs.rm(checkpoint_root, True)
spark.sql(f"DROP TABLE IF EXISTS {qname('stream_order_slot_metrics')}")
spark.sql(f"DROP TABLE IF EXISTS {qname('report_stream_validation')}")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Build And Write The Held-Out Replay Slice
# MAGIC
# MAGIC The replay slice is deterministic because it is ordered by `order_id` before batch assignment.

# COMMAND ----------
window_spec = Window.orderBy("order_id")
held_out_orders = (
    fact_orders.withColumn("row_num", F.row_number().over(window_spec))
    .filter(F.col("row_num") <= replay_order_limit)
    .withColumn("batch_id", (F.pmod(F.col("row_num") - 1, F.lit(batch_count)) + 1).cast("int"))
)

assert held_out_orders.count() > 0, "No held-out orders were available for the replay stream."

for batch_id in range(1, batch_count + 1):
    (
        held_out_orders.filter(F.col("batch_id") == batch_id)
        .drop("row_num", "batch_id")
        .coalesce(1)
        .write.mode("append")
        .option("header", True)
        .csv(replay_root)
    )

# COMMAND ----------
# MAGIC %md
# MAGIC ## Run The `AvailableNow` Stream
# MAGIC
# MAGIC `collect` is not needed here because the streaming writer materializes the state once `awaitTermination()` completes.

# COMMAND ----------
replay_schema = held_out_orders.drop("row_num", "batch_id").schema
stream_input = (
    spark.readStream.schema(replay_schema)
    .option("header", True)
    .option("maxFilesPerTrigger", 1)
    .csv(replay_root)
)

stream_metrics = (
    stream_input.groupBy("order_dow", "order_hour_of_day")
    .agg(
        F.count("*").alias("stream_order_count"),
        F.avg("basket_size").alias("stream_avg_basket_size"),
        F.sum("reordered_item_count").alias("stream_reordered_items"),
    )
)

query = (
    stream_metrics.writeStream.format("delta")
    .outputMode("complete")
    .option("checkpointLocation", checkpoint_root)
    .trigger(availableNow=True)
    .toTable(qname("stream_order_slot_metrics"))
)
query.awaitTermination()

# COMMAND ----------
# MAGIC %md
# MAGIC ## Validate Stream Output Against Batch Output
# MAGIC
# MAGIC The replay only counts as valid if counts, average basket size, and reordered-item totals all match exactly at order-slot grain.

# COMMAND ----------
batch_validation = (
    held_out_orders.groupBy("order_dow", "order_hour_of_day")
    .agg(
        F.count("*").alias("batch_order_count"),
        F.avg("basket_size").alias("batch_avg_basket_size"),
        F.sum("reordered_item_count").alias("batch_reordered_items"),
    )
)

stream_validation = spark.table(qname("stream_order_slot_metrics"))
comparison = (
    batch_validation.join(stream_validation, ["order_dow", "order_hour_of_day"], "full")
    .na.fill(
        {
            "batch_order_count": 0,
            "stream_order_count": 0,
            "batch_avg_basket_size": 0.0,
            "stream_avg_basket_size": 0.0,
            "batch_reordered_items": 0,
            "stream_reordered_items": 0,
        }
    )
    .withColumn("count_matches", F.col("batch_order_count") == F.col("stream_order_count"))
    .withColumn(
        "avg_basket_matches",
        F.abs(F.col("batch_avg_basket_size") - F.col("stream_avg_basket_size")) < F.lit(1e-9),
    )
    .withColumn(
        "reordered_matches",
        F.col("batch_reordered_items") == F.col("stream_reordered_items"),
    )
)

(
    comparison.write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(qname("report_stream_validation"))
)

mismatches = comparison.filter(
    ~F.col("count_matches") | ~F.col("avg_basket_matches") | ~F.col("reordered_matches")
).count()
assert mismatches == 0, f"Streaming replay validation found {mismatches} mismatched order-slot aggregates."

display(comparison.orderBy("order_dow", "order_hour_of_day"))

# COMMAND ----------
# MAGIC %md
# MAGIC ## Interpretation Note
# MAGIC
# MAGIC A zero-mismatch validation table is the release-safe outcome. Any mismatch should be treated as a data-quality failure, not as an acceptable approximation.
