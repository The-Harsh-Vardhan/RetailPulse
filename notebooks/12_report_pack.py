# Databricks notebook source
# MAGIC %md
# MAGIC # Report Pack
# MAGIC
# MAGIC This notebook assembles the final evidence tables used in the written report and demo.

# COMMAND ----------
# MAGIC %md
# MAGIC ## Notebook Dashboard Fallback
# MAGIC
# MAGIC Use the AI/BI dashboard as the primary live-demo surface.
# MAGIC
# MAGIC If the dashboard is unavailable or a panel needs drill-down, use this notebook as the fallback dashboard in this order:
# MAGIC 1. table counts
# MAGIC 2. OLAP cube
# MAGIC 3. OLAP rollup
# MAGIC 4. OLAP basket analysis
# MAGIC 5. recommendation rules
# MAGIC 6. cluster profiles
# MAGIC 7. stream validation
# MAGIC 8. optimize summary
# MAGIC 9. classifier metrics
# MAGIC 10. regression metrics
# MAGIC
# MAGIC Classifier and regression results are exploratory and useful for demo discussion, but not final predictive proof. Methodology tightening is still pending.

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
display(spark.table(qname("report_olap_cube")).orderBy("department_id", "order_dow"))
display(spark.table(qname("report_olap_rollup")).orderBy("order_dow", "order_hour_of_day"))
display(spark.table(qname("report_olap_basket")).orderBy("daypart", "department_id"))
display(spark.table(qname("report_olap_validation")).orderBy("department_id", "order_dow"))

# COMMAND ----------
dim_product = spark.table(qname("dim_product"))
top_rules = (
    spark.table(qname("mart_association_rules"))
    .join(
        dim_product.select(
            F.col("product_id").alias("antecedent_product_id"),
            F.col("product_name").alias("antecedent_product_name"),
        ),
        "antecedent_product_id",
        "left",
    )
    .join(
        dim_product.select(
            F.col("product_id").alias("consequent_product_id"),
            F.col("product_name").alias("consequent_product_name"),
        ),
        "consequent_product_id",
        "left",
    )
    .orderBy(F.desc("lift"), F.desc("confidence"))
    .limit(10)
)

display(spark.table(qname("report_classifier_metrics")))
display(spark.table(qname("report_regression_metrics")))
display(spark.table(qname("report_cluster_profiles")))
display(spark.table(qname("report_stream_validation")).orderBy("order_dow", "order_hour_of_day"))
display(spark.table(qname("report_optimize_summary")).orderBy("query_name"))
display(top_rules)

# COMMAND ----------
report_outline = [
    ("1", "Problem statement and dataset caveats"),
    ("2", "Medallion architecture and star schema"),
    ("3", "Bronze, silver, and gold row-count validation"),
    ("4", "OLAP findings with CUBE and ROLLUP plus persisted report tables"),
    ("5", "Top association rules and recommendation example"),
    ("6", "Cluster profiles and business interpretation"),
    ("7", "Classifier and regression metrics versus baselines"),
    ("8", "Streaming replay validation and serverless limitations"),
    ("9", "Optimization timings before and after ZORDER"),
]

display(spark.createDataFrame(report_outline, ["section", "what_to_capture"]))
