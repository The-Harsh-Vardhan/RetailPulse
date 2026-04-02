# Databricks notebook source
# MAGIC %md
# MAGIC # Silver Transform
# MAGIC
# MAGIC This notebook standardizes types, enriches products with aisle and department metadata, and creates reusable user history aggregates.

# COMMAND ----------
from pyspark.sql import Window, functions as F

dbutils.widgets.text("catalog", "")
dbutils.widgets.text("schema", "retailpulse")

# COMMAND ----------
catalog = dbutils.widgets.get("catalog") or spark.sql("SELECT current_catalog()").first()[0]
schema = dbutils.widgets.get("schema") or spark.sql("SELECT current_schema()").first()[0]


def qname(name: str) -> str:
    return f"`{catalog}`.`{schema}`.`{name}`"


orders = spark.table(qname("bronze_orders"))
prior = spark.table(qname("bronze_order_products_prior"))
train = spark.table(qname("bronze_order_products_train"))
products = spark.table(qname("bronze_products"))
aisles = spark.table(qname("bronze_aisles"))
departments = spark.table(qname("bronze_departments"))

silver_orders = (
    orders.select(
        F.col("order_id").cast("int"),
        F.col("user_id").cast("int"),
        F.trim("eval_set").alias("eval_set"),
        F.col("order_number").cast("int"),
        F.col("order_dow").cast("int"),
        F.col("order_hour_of_day").cast("int"),
        F.col("days_since_prior_order").cast("double"),
    )
    .filter(F.col("order_id").isNotNull() & F.col("user_id").isNotNull())
    .dropDuplicates(["order_id"])
)

silver_products_enriched = (
    products.join(aisles, "aisle_id", "left")
    .join(departments, "department_id", "left")
    .select("product_id", "product_name", "aisle_id", "aisle", "department_id", "department")
    .dropDuplicates(["product_id"])
)

order_items_union = prior.withColumn("source_split", F.lit("prior")).unionByName(
    train.withColumn("source_split", F.lit("train"))
)

silver_order_items = (
    order_items_union.join(silver_orders, "order_id", "inner")
    .join(silver_products_enriched, "product_id", "left")
    .select(
        "order_id",
        "user_id",
        "product_id",
        "product_name",
        "aisle_id",
        "aisle",
        "department_id",
        "department",
        "eval_set",
        "order_number",
        "order_dow",
        "order_hour_of_day",
        "days_since_prior_order",
        "add_to_cart_order",
        F.coalesce(F.col("reordered"), F.lit(0)).cast("int").alias("reordered"),
        F.lit(1).alias("item_qty"),
    )
    .filter(
        F.col("order_id").isNotNull()
        & F.col("user_id").isNotNull()
        & F.col("product_id").isNotNull()
    )
)

order_level_history = (
    silver_order_items.groupBy("order_id", "user_id")
    .agg(
        F.count("*").alias("basket_size"),
        F.avg(F.col("reordered").cast("double")).alias("reordered_item_rate"),
        F.countDistinct("department_id").alias("distinct_department_count"),
    )
)

silver_user_history = (
    silver_orders.join(order_level_history, ["order_id", "user_id"], "left")
    .groupBy("user_id")
    .agg(
        F.max("order_number").alias("total_orders"),
        F.avg("basket_size").alias("avg_basket_size"),
        F.avg("days_since_prior_order").alias("avg_days_since_prior_order"),
        F.avg("reordered_item_rate").alias("avg_reordered_item_rate"),
        F.avg("distinct_department_count").alias("avg_distinct_department_count"),
        F.avg("order_hour_of_day").alias("avg_order_hour_of_day"),
        F.countDistinct("order_dow").alias("active_days"),
    )
)

for table_name, frame in {
    "silver_orders": silver_orders,
    "silver_order_items": silver_order_items,
    "silver_products_enriched": silver_products_enriched,
    "silver_user_history": silver_user_history,
}.items():
    (
        frame.write.format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(qname(table_name))
    )

# COMMAND ----------
validations = [
    ("silver_orders", silver_orders.count()),
    ("silver_order_items", silver_order_items.count()),
    ("silver_products_enriched", silver_products_enriched.count()),
    ("silver_user_history", silver_user_history.count()),
    (
        "silver_order_items_null_keys",
        silver_order_items.filter(
            F.col("order_id").isNull()
            | F.col("user_id").isNull()
            | F.col("product_id").isNull()
        ).count(),
    ),
]

display(spark.createDataFrame(validations, ["check_name", "value"]))

