# Databricks notebook source
# MAGIC %md
# MAGIC # Gold Model
# MAGIC
# MAGIC This notebook builds the star schema tables and the reusable user feature mart used by the analytics notebooks.

# COMMAND ----------
from pyspark.sql import Window, functions as F

dbutils.widgets.text("catalog", "")
dbutils.widgets.text("schema", "retailpulse")

# COMMAND ----------
catalog = dbutils.widgets.get("catalog") or spark.sql("SELECT current_catalog()").first()[0]
schema = dbutils.widgets.get("schema") or spark.sql("SELECT current_schema()").first()[0]


def qname(name: str) -> str:
    return f"`{catalog}`.`{schema}`.`{name}`"


silver_orders = spark.table(qname("silver_orders"))
silver_order_items = spark.table(qname("silver_order_items"))
silver_products_enriched = spark.table(qname("silver_products_enriched"))
silver_user_history = spark.table(qname("silver_user_history"))

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
