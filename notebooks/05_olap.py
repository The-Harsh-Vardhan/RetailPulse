# Databricks notebook source
# MAGIC %md
# MAGIC # OLAP Analysis
# MAGIC
# MAGIC This notebook runs submission-safe CUBE and ROLLUP queries over the gold facts.

# COMMAND ----------
from pyspark.sql import functions as F

dbutils.widgets.text("catalog", "")
dbutils.widgets.text("schema", "retailpulse")

# COMMAND ----------
catalog = dbutils.widgets.get("catalog") or spark.sql("SELECT current_catalog()").first()[0]
schema = dbutils.widgets.get("schema") or spark.sql("SELECT current_schema()").first()[0]


def qname(name: str) -> str:
    return f"`{catalog}`.`{schema}`.`{name}`"


spark.sql(f"USE CATALOG `{catalog}`")
spark.sql(f"USE SCHEMA `{schema}`")

cube_query = f"""
SELECT
  department_id,
  order_dow,
  SUM(item_qty) AS total_items,
  COUNT(DISTINCT order_id) AS distinct_orders
FROM {qname("fact_order_items")}
GROUP BY CUBE(department_id, order_dow)
ORDER BY department_id, order_dow
"""

rollup_query = f"""
SELECT
  order_dow,
  order_hour_of_day,
  COUNT(*) AS order_count,
  AVG(basket_size) AS avg_basket_size
FROM {qname("fact_orders")}
GROUP BY ROLLUP(order_dow, order_hour_of_day)
ORDER BY order_dow, order_hour_of_day
"""

basket_query = f"""
SELECT
  dos.daypart,
  foi.department_id,
  COUNT(DISTINCT foi.order_id) AS orders_seen,
  AVG(fo.basket_size) AS avg_basket_size
FROM {qname("fact_order_items")} foi
JOIN {qname("fact_orders")} fo
  ON foi.order_id = fo.order_id
JOIN {qname("dim_order_slot")} dos
  ON foi.order_dow = dos.order_dow
 AND foi.order_hour_of_day = dos.order_hour_of_day
GROUP BY dos.daypart, foi.department_id
ORDER BY dos.daypart, avg_basket_size DESC
"""

cube_df = spark.sql(cube_query)
rollup_df = spark.sql(rollup_query)
basket_df = spark.sql(basket_query)

display(cube_df)
display(rollup_df)
display(basket_df)

# COMMAND ----------
manual_check = (
    spark.table(qname("fact_order_items"))
    .groupBy("department_id", "order_dow")
    .agg(F.sum("item_qty").alias("manual_total_items"))
)

comparison = (
    cube_df.filter(F.col("department_id").isNotNull() & F.col("order_dow").isNotNull())
    .join(manual_check, ["department_id", "order_dow"], "inner")
    .withColumn("matches", F.col("total_items") == F.col("manual_total_items"))
)

display(comparison)

