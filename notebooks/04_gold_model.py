# Databricks notebook source
# MAGIC %md
# MAGIC # Gold Model
# MAGIC
# MAGIC This notebook builds the star schema and the reusable user-feature mart that later analytics notebooks consume.
# MAGIC
# MAGIC ## Run Inputs
# MAGIC - `catalog`: optional override for the active catalog
# MAGIC - `schema`: schema that contains silver and gold tables
# MAGIC
# MAGIC ## Source Tables
# MAGIC - `silver_orders`
# MAGIC - `silver_order_items`
# MAGIC - `silver_products_enriched`
# MAGIC - `silver_user_history`
# MAGIC
# MAGIC ## Output Tables
# MAGIC - `dim_user`
# MAGIC - `dim_product`
# MAGIC - `dim_aisle`
# MAGIC - `dim_department`
# MAGIC - `dim_order_slot`
# MAGIC - `fact_order_items`
# MAGIC - `fact_orders`
# MAGIC - `mart_user_features`
# MAGIC
# MAGIC ## Workflow
# MAGIC 1. Load the silver tables.
# MAGIC 2. Build warehouse-style dimensions and facts.
# MAGIC 3. Derive the reusable user-feature mart for clustering and exploratory ML.
# MAGIC 4. Persist the gold tables and run basic contract checks.

# COMMAND ----------
# MAGIC %md
# MAGIC ## Capture Runtime Inputs
# MAGIC
# MAGIC Gold is the stable analytical handoff layer, so every downstream notebook expects these tables to exist with the same names.

# COMMAND ----------
from pyspark.sql import functions as F

dbutils.widgets.text("catalog", "")
dbutils.widgets.text("schema", "retailpulse")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Resolve Catalog Context And Load Silver Tables
# MAGIC
# MAGIC The helper keeps all writes fully qualified so the bundle job can target alternate catalogs without editing notebook logic.

# COMMAND ----------
catalog = dbutils.widgets.get("catalog") or spark.sql("SELECT current_catalog()").first()[0]
schema = dbutils.widgets.get("schema") or spark.sql("SELECT current_schema()").first()[0]


def qname(name: str) -> str:
    return f"`{catalog}`.`{schema}`.`{name}`"


silver_orders = spark.table(qname("silver_orders"))
silver_order_items = spark.table(qname("silver_order_items"))
silver_products_enriched = spark.table(qname("silver_products_enriched"))
silver_user_history = spark.table(qname("silver_user_history"))

# COMMAND ----------
# MAGIC %md
# MAGIC ## Build Dimensions
# MAGIC
# MAGIC The dimensions keep descriptive attributes separated from the two fact tables and add a reusable daypart lookup.

# COMMAND ----------
dim_user = silver_user_history.select(
    "user_id",
    "total_orders",
    "avg_basket_size",
    "avg_days_since_prior_order",
    "avg_reordered_item_rate",
    "avg_distinct_department_count",
    "avg_order_hour_of_day",
    "active_days",
)

dim_product = silver_products_enriched.select(
    "product_id",
    "product_name",
    "aisle_id",
    "department_id",
).dropDuplicates(["product_id"])

dim_aisle = silver_products_enriched.select("aisle_id", "aisle").dropDuplicates(["aisle_id"])
dim_department = silver_products_enriched.select(
    "department_id", "department"
).dropDuplicates(["department_id"])

# Keep the daypart mapping explicit so dashboard-facing timing logic is easy to review.
dim_order_slot = (
    silver_orders.select("order_dow", "order_hour_of_day")
    .dropDuplicates()
    .withColumn(
        "daypart",
        F.when(F.col("order_hour_of_day") < 6, F.lit("overnight"))
        .when(F.col("order_hour_of_day") < 12, F.lit("morning"))
        .when(F.col("order_hour_of_day") < 17, F.lit("afternoon"))
        .when(F.col("order_hour_of_day") < 21, F.lit("evening"))
        .otherwise(F.lit("late_evening")),
    )
)

# COMMAND ----------
# MAGIC %md
# MAGIC ## Build Facts
# MAGIC
# MAGIC `fact_order_items` preserves the item grain, while `fact_orders` summarizes each order for later basket and timing analysis.

# COMMAND ----------
fact_order_items = silver_order_items.select(
    "order_id",
    "user_id",
    "product_id",
    "aisle_id",
    "department_id",
    "eval_set",
    "order_number",
    "order_dow",
    "order_hour_of_day",
    "days_since_prior_order",
    "add_to_cart_order",
    "reordered",
    "item_qty",
)

fact_orders = (
    fact_order_items.groupBy(
        "order_id",
        "user_id",
        "eval_set",
        "order_number",
        "order_dow",
        "order_hour_of_day",
        "days_since_prior_order",
    )
    .agg(
        F.count("*").alias("basket_size"),
        F.sum("reordered").alias("reordered_item_count"),
        F.countDistinct("department_id").alias("distinct_department_count"),
    )
)

# COMMAND ----------
# MAGIC %md
# MAGIC ## Build The Reusable User Feature Mart
# MAGIC
# MAGIC This mart mirrors the user-level signals that later clustering and exploratory predictive notebooks expect. It intentionally keeps the current methodology stable for this release.

# COMMAND ----------
base_user_features = (
    fact_orders.groupBy("user_id")
    .agg(
        F.max("order_number").alias("total_orders"),
        F.avg("basket_size").alias("avg_basket_size"),
        F.avg("days_since_prior_order").alias("avg_days_since_prior_order"),
        F.avg(
            F.when(F.col("basket_size") > 0, F.col("reordered_item_count") / F.col("basket_size"))
            .otherwise(F.lit(0.0))
        ).alias("avg_reordered_item_rate"),
        F.avg("distinct_department_count").alias("avg_distinct_department_count"),
        F.avg("order_hour_of_day").alias("avg_order_hour_of_day"),
        F.countDistinct("order_dow").alias("active_days"),
    )
)

# Merge the fact-derived features with the silver history snapshot so downstream notebooks always find a complete user row.
mart_user_features = (
    base_user_features.join(
        dim_user.select(
            F.col("user_id"),
            F.col("total_orders").alias("history_total_orders"),
            F.col("avg_basket_size").alias("history_avg_basket_size"),
            F.col("avg_days_since_prior_order").alias("history_avg_days_since_prior_order"),
            F.col("avg_reordered_item_rate").alias("history_avg_reordered_item_rate"),
            F.col("avg_distinct_department_count").alias("history_avg_distinct_department_count"),
            F.col("avg_order_hour_of_day").alias("history_avg_order_hour_of_day"),
            F.col("active_days").alias("history_active_days"),
        ),
        "user_id",
        "full",
    )
    .select(
        "user_id",
        F.coalesce(F.col("total_orders"), F.col("history_total_orders")).alias("total_orders"),
        F.coalesce(F.col("avg_basket_size"), F.col("history_avg_basket_size")).alias("avg_basket_size"),
        F.coalesce(
            F.col("avg_days_since_prior_order"),
            F.col("history_avg_days_since_prior_order"),
        ).alias("avg_days_since_prior_order"),
        F.coalesce(
            F.col("avg_reordered_item_rate"),
            F.col("history_avg_reordered_item_rate"),
        ).alias("avg_reordered_item_rate"),
        F.coalesce(
            F.col("avg_distinct_department_count"),
            F.col("history_avg_distinct_department_count"),
        ).alias("avg_distinct_department_count"),
        F.coalesce(
            F.col("avg_order_hour_of_day"),
            F.col("history_avg_order_hour_of_day"),
        ).alias("avg_order_hour_of_day"),
        F.coalesce(F.col("active_days"), F.col("history_active_days")).alias("active_days"),
    )
)

# COMMAND ----------
# MAGIC %md
# MAGIC ## Persist Gold Tables
# MAGIC
# MAGIC These tables form the durable analytical contract for OLAP, recommendation, clustering, streaming validation, and the two supplementary deep-dive notebooks.

# COMMAND ----------
for table_name, frame in {
    "dim_user": dim_user,
    "dim_product": dim_product,
    "dim_aisle": dim_aisle,
    "dim_department": dim_department,
    "dim_order_slot": dim_order_slot,
    "fact_order_items": fact_order_items,
    "fact_orders": fact_orders,
    "mart_user_features": mart_user_features,
}.items():
    (
        frame.write.format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(qname(table_name))
    )

# COMMAND ----------
# MAGIC %md
# MAGIC ## Validate Gold Outputs
# MAGIC
# MAGIC These checks focus on row presence and core key integrity. Richer business validation is deferred to the later report tables.

# COMMAND ----------
checks = [
    ("fact_order_items", fact_order_items.count()),
    ("fact_orders", fact_orders.count()),
    (
        "fact_order_items_null_keys",
        fact_order_items.filter(
            F.col("order_id").isNull()
            | F.col("user_id").isNull()
            | F.col("product_id").isNull()
            | F.col("department_id").isNull()
        ).count(),
    ),
    (
        "fact_order_items_bad_reordered",
        fact_order_items.filter(~F.col("reordered").isin(0, 1)).count(),
    ),
]

display(spark.createDataFrame(checks, ["check_name", "value"]))
