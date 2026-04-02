# Databricks notebook source
# MAGIC %md
# MAGIC # Optimize And Benchmark
# MAGIC
# MAGIC This notebook benchmarks two representative queries before and after `OPTIMIZE ... ZORDER BY`.

# COMMAND ----------
import time

from pyspark.sql import functions as F

dbutils.widgets.text("catalog", "")
dbutils.widgets.text("schema", "retailpulse")

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


def time_query(sql_text: str) -> float:
    started = time.perf_counter()
    spark.sql(sql_text).collect()
    finished = time.perf_counter()
    return finished - started


timings = []
for query_name, query_sql in queries.items():
    timings.append((query_name, "before_optimize", time_query(query_sql)))

spark.sql(f"ANALYZE TABLE {qname('fact_order_items')} COMPUTE STATISTICS")
spark.sql(f"ANALYZE TABLE {qname('fact_orders')} COMPUTE STATISTICS")
spark.sql(f"OPTIMIZE {qname('fact_order_items')} ZORDER BY (product_id, department_id)")
spark.sql(f"OPTIMIZE {qname('fact_orders')} ZORDER BY (user_id)")

for query_name, query_sql in queries.items():
    timings.append((query_name, "after_optimize", time_query(query_sql)))

display(spark.createDataFrame(timings, ["query_name", "run_stage", "seconds"]))

# COMMAND ----------
# MAGIC %md
# MAGIC Inspect the Databricks query profile for the two benchmark queries above to capture submission evidence. Serverless notebooks do not expose the Spark UI.

