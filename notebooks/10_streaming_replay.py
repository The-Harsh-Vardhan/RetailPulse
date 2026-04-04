# Databricks notebook source
# MAGIC %md
# MAGIC # Streaming Replay
# MAGIC
# MAGIC Databricks Free Edition serverless only supports `Trigger.AvailableNow`, so this notebook creates a held-out replay slice, writes multiple CSV files, and streams them into `stream_order_slot_metrics`.

# COMMAND ----------
from pyspark.sql import Window, functions as F

dbutils.widgets.text("catalog", "")
dbutils.widgets.text("schema", "retailpulse")
dbutils.widgets.text("replay_volume", "retailpulse_replay")
dbutils.widgets.text("checkpoint_volume", "retailpulse_checkpoints")
dbutils.widgets.text("batch_count", "4")
dbutils.widgets.text("replay_order_limit", "4000")

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

dbutils.fs.rm(replay_root, True)
dbutils.fs.rm(checkpoint_root, True)
spark.sql(f"DROP TABLE IF EXISTS {qname('stream_order_slot_metrics')}")
spark.sql(f"DROP TABLE IF EXISTS {qname('report_stream_validation')}")

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
