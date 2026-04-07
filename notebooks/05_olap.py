# Databricks notebook source
# MAGIC %md
# MAGIC # OLAP Analysis
# MAGIC
# MAGIC This notebook runs submission-safe `CUBE` and `ROLLUP` queries over the gold facts and persists the resulting report tables.
# MAGIC
# MAGIC ## Run Inputs
# MAGIC - `catalog`: optional override for the active catalog
# MAGIC - `schema`: schema that contains the gold facts and report tables
# MAGIC
# MAGIC ## Source Tables
# MAGIC - `fact_order_items`
# MAGIC - `fact_orders`
# MAGIC - `dim_order_slot`
# MAGIC
# MAGIC ## Output Tables
# MAGIC - `report_olap_cube`
# MAGIC - `report_olap_rollup`
# MAGIC - `report_olap_basket`
# MAGIC - `report_olap_validation`
# MAGIC
# MAGIC ## Workflow
# MAGIC 1. Resolve the active catalog and schema.
# MAGIC 2. Define the OLAP queries at cube, rollup, and basket-analysis grain.
# MAGIC 3. Cross-check the cube result against a direct aggregation.
# MAGIC 4. Persist the report tables used by the dashboard and report pack.

# COMMAND ----------
# MAGIC %md
# MAGIC ## Capture Runtime Inputs
# MAGIC
# MAGIC This notebook is where the descriptive analytics layer becomes durable. Later dashboard and evidence notebooks should read these report tables instead of recalculating the logic.

# COMMAND ----------
from pyspark.sql import functions as F

dbutils.widgets.text("catalog", "")
dbutils.widgets.text("schema", "retailpulse")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Resolve Catalog Context
# MAGIC
# MAGIC Setting the catalog and schema explicitly keeps the generated SQL readable in query history and avoids ambiguity during reruns.

# COMMAND ----------
catalog = dbutils.widgets.get("catalog") or spark.sql("SELECT current_catalog()").first()[0]
schema = dbutils.widgets.get("schema") or spark.sql("SELECT current_schema()").first()[0]


def qname(name: str) -> str:
    return f"`{catalog}`.`{schema}`.`{name}`"


spark.sql(f"USE CATALOG `{catalog}`")
spark.sql(f"USE SCHEMA `{schema}`")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Define OLAP Queries
# MAGIC
# MAGIC Keep the SQL strings readable so the grouping grain is obvious both in the notebook and in the saved query history.

# COMMAND ----------
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

# COMMAND ----------
# MAGIC %md
# MAGIC ## Execute Queries And Validate The Cube
# MAGIC
# MAGIC The validation frame proves that the base-grain cube rows match a direct fact-table aggregation before the results are reused elsewhere.

# COMMAND ----------
cube_df = spark.sql(cube_query)
rollup_df = spark.sql(rollup_query)
basket_df = spark.sql(basket_query)
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

# COMMAND ----------
# MAGIC %md
# MAGIC ## Persist Report Tables
# MAGIC
# MAGIC These tables are the descriptive analytics contract used by the dashboard, the report pack, and the new prescriptive notebook.

# COMMAND ----------
for table_name, frame in {
    "report_olap_cube": cube_df,
    "report_olap_rollup": rollup_df,
    "report_olap_basket": basket_df,
    "report_olap_validation": comparison,
}.items():
    (
        frame.write.format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(qname(table_name))
    )

# COMMAND ----------
# MAGIC %md
# MAGIC ## Review OLAP Outputs
# MAGIC
# MAGIC Use these displays to confirm both analytical usefulness and validation integrity before moving on to recommendations and segmentation.

# COMMAND ----------
display(cube_df)
display(rollup_df)
display(basket_df)
display(comparison)

# COMMAND ----------
# MAGIC %md
# MAGIC ## Interpretation Note
# MAGIC
# MAGIC `report_olap_cube` and `report_olap_rollup` are reusable descriptive outputs.
# MAGIC
# MAGIC `report_olap_validation` is the quality guardrail: if `matches` is false for any row, the descriptive layer should be treated as suspect until the gold facts are rechecked.
