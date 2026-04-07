# Databricks notebook source
# MAGIC %md
# MAGIC # Optimize And Benchmark
# MAGIC
# MAGIC This notebook benchmarks two representative queries before and after `OPTIMIZE ... ZORDER BY`.
# MAGIC
# MAGIC ## Run Inputs
# MAGIC - `catalog`: optional override for the active catalog
# MAGIC - `schema`: schema that contains the fact tables and report outputs
# MAGIC
# MAGIC ## Source Tables
# MAGIC - `fact_order_items`
# MAGIC - `fact_orders`
# MAGIC
# MAGIC ## Output Tables
# MAGIC - `report_optimize_timings`
# MAGIC - `report_optimize_summary`
# MAGIC
# MAGIC ## Workflow
# MAGIC 1. Define the benchmark queries.
# MAGIC 2. Time each query before optimization.
# MAGIC 3. Compute table statistics, run `OPTIMIZE`, and apply `ZORDER BY`.
# MAGIC 4. Time the same queries again and persist the comparison tables.

# COMMAND ----------
# MAGIC %md
# MAGIC ## Capture Runtime Inputs
# MAGIC
# MAGIC This benchmark is intentionally small and readable. Its goal is to document whether optimization helps the current sample, not to produce a production performance study.

# COMMAND ----------
import time

from pyspark.sql import functions as F

dbutils.widgets.text("catalog", "")
dbutils.widgets.text("schema", "retailpulse")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Resolve Context And Define Benchmark Queries
# MAGIC
# MAGIC The queries represent two common access patterns: grouped item distribution and user-level basket aggregation.

# COMMAND ----------
catalog = dbutils.widgets.get("catalog") or spark.sql("SELECT current_catalog()").first()[0]
schema = dbutils.widgets.get("schema") or spark.sql("SELECT current_schema()").first()[0]


def qname(name: str) -> str:
    return f"`{catalog}`.`{schema}`.`{name}`"


queries = {
    "department_hour_distribution": f"""
        SELECT department_id, order_hour_of_day, COUNT(*) AS items_seen
        FROM {qname("fact_order_items")}
        WHERE department_id IS NOT NULL
        GROUP BY department_id, order_hour_of_day
    """,
    "user_basket_summary": f"""
        SELECT user_id, AVG(basket_size) AS avg_basket_size
        FROM {qname("fact_orders")}
        GROUP BY user_id
    """,
}


# Collect the full result set so the timing measures execution work instead of only planning.
def time_query(sql_text: str) -> float:
    started = time.perf_counter()
    spark.sql(sql_text).collect()
    finished = time.perf_counter()
    return finished - started

# COMMAND ----------
# MAGIC %md
# MAGIC ## Time The Queries Before Optimization
# MAGIC
# MAGIC Store every timing row so the final comparison table can be derived rather than hard-coded.

# COMMAND ----------
timings = []
for query_name, query_sql in queries.items():
    timings.append((query_name, "before_optimize", time_query(query_sql)))

# COMMAND ----------
# MAGIC %md
# MAGIC ## Analyze And Optimize The Fact Tables
# MAGIC
# MAGIC Statistics and layout changes are applied only after the baseline timings are collected.

# COMMAND ----------
spark.sql(f"ANALYZE TABLE {qname('fact_order_items')} COMPUTE STATISTICS")
spark.sql(f"ANALYZE TABLE {qname('fact_orders')} COMPUTE STATISTICS")
spark.sql(f"OPTIMIZE {qname('fact_order_items')} ZORDER BY (product_id, department_id)")
spark.sql(f"OPTIMIZE {qname('fact_orders')} ZORDER BY (user_id)")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Time The Queries After Optimization
# MAGIC
# MAGIC Running the same SQL after optimization keeps the comparison apples-to-apples.

# COMMAND ----------
for query_name, query_sql in queries.items():
    timings.append((query_name, "after_optimize", time_query(query_sql)))

timings_df = spark.createDataFrame(timings, ["query_name", "run_stage", "seconds"])

optimize_summary = (
    timings_df.groupBy("query_name")
    .pivot("run_stage", ["before_optimize", "after_optimize"])
    .agg(F.first("seconds"))
    .withColumn("seconds_saved", F.col("before_optimize") - F.col("after_optimize"))
    .withColumn(
        "speedup_ratio",
        F.when(F.col("after_optimize") > 0, F.col("before_optimize") / F.col("after_optimize"))
        .otherwise(F.lit(None)),
    )
)

# COMMAND ----------
# MAGIC %md
# MAGIC ## Persist And Review Benchmark Outputs
# MAGIC
# MAGIC These report tables are reused by the dashboard and the report pack rather than recalculating the timings elsewhere.

# COMMAND ----------
(
    timings_df.write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(qname("report_optimize_timings"))
)

(
    optimize_summary.write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(qname("report_optimize_summary"))
)

display(timings_df)
display(optimize_summary)

# COMMAND ----------
# MAGIC %md
# MAGIC ## Interpretation Note
# MAGIC
# MAGIC Inspect the Databricks query profile for the benchmark queries above if you need richer evidence. Serverless notebooks do not expose the Spark UI directly, so this timing table is the canonical repo-tracked comparison.
