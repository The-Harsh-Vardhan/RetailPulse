# Databricks notebook source
# MAGIC %md
# MAGIC # Report Pack
# MAGIC
# MAGIC This notebook assembles the final evidence tables used in the written report and demo.

# COMMAND ----------
from pyspark.sql import functions as F

dbutils.widgets.text("catalog", "")
dbutils.widgets.text("schema", "retailpulse")

# COMMAND ----------
catalog = dbutils.widgets.get("catalog") or spark.sql("SELECT current_catalog()").first()[0]
schema = dbutils.widgets.get("schema") or spark.sql("SELECT current_schema()").first()[0]


def qname(name: str) -> str:
    return f"`{catalog}`.`{schema}`.`{name}`"


table_counts = [
    ("bronze_orders", spark.table(qname("bronze_orders")).count()),
    ("silver_order_items", spark.table(qname("silver_order_items")).count()),
    ("fact_order_items", spark.table(qname("fact_order_items")).count()),
    ("fact_orders", spark.table(qname("fact_orders")).count()),
    ("mart_association_rules", spark.table(qname("mart_association_rules")).count()),
    ("stream_order_slot_metrics", spark.table(qname("stream_order_slot_metrics")).count()),
]

display(spark.createDataFrame(table_counts, ["table_name", "row_count"]))

# COMMAND ----------
display(spark.table(qname("report_classifier_metrics")))
display(spark.table(qname("report_regression_metrics")))
display(spark.table(qname("report_cluster_profiles")))
display(
    spark.table(qname("mart_association_rules"))
    .orderBy(F.desc("lift"), F.desc("confidence"))
    .limit(10)
)

# COMMAND ----------
report_outline = [
    ("1", "Problem statement and dataset caveats"),
    ("2", "Medallion architecture and star schema"),
    ("3", "Bronze, silver, and gold row-count validation"),
    ("4", "OLAP findings with CUBE and ROLLUP"),
    ("5", "Top association rules and recommendation example"),
    ("6", "Cluster profiles and business interpretation"),
    ("7", "Classifier and regression metrics versus baselines"),
    ("8", "Streaming replay validation and serverless limitations"),
    ("9", "Optimization timings before and after ZORDER"),
]

display(spark.createDataFrame(report_outline, ["section", "what_to_capture"]))
