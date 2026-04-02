# Databricks notebook source
# MAGIC %md
# MAGIC # Bronze Ingest
# MAGIC
# MAGIC This notebook loads the uploaded CSV files into explicit-schema Delta tables.

# COMMAND ----------
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType, IntegerType, StringType, StructField, StructType

dbutils.widgets.text("catalog", "")
dbutils.widgets.text("schema", "retailpulse")
dbutils.widgets.text("raw_volume", "retailpulse_raw")

# COMMAND ----------
catalog = dbutils.widgets.get("catalog") or spark.sql("SELECT current_catalog()").first()[0]
schema = dbutils.widgets.get("schema") or spark.sql("SELECT current_schema()").first()[0]
raw_volume = dbutils.widgets.get("raw_volume")
raw_root = f"/Volumes/{catalog}/{schema}/{raw_volume}"


def qname(name: str) -> str:
    return f"`{catalog}`.`{schema}`.`{name}`"


def read_csv(file_name: str, schema_def: StructType):
    return (
        spark.read.option("header", True)
        .schema(schema_def)
        .csv(f"{raw_root}/{file_name}")
    )


orders_schema = StructType(
    [
        StructField("order_id", IntegerType(), False),
        StructField("user_id", IntegerType(), False),
        StructField("eval_set", StringType(), False),
        StructField("order_number", IntegerType(), False),
        StructField("order_dow", IntegerType(), True),
        StructField("order_hour_of_day", IntegerType(), True),
        StructField("days_since_prior_order", DoubleType(), True),
    ]
)
order_products_schema = StructType(
    [
        StructField("order_id", IntegerType(), False),
        StructField("product_id", IntegerType(), False),
        StructField("add_to_cart_order", IntegerType(), True),
        StructField("reordered", IntegerType(), True),
    ]
)
products_schema = StructType(
    [
        StructField("product_id", IntegerType(), False),
        StructField("product_name", StringType(), True),
        StructField("aisle_id", IntegerType(), True),
        StructField("department_id", IntegerType(), True),
    ]
)
aisles_schema = StructType(
    [
        StructField("aisle_id", IntegerType(), False),
        StructField("aisle", StringType(), True),
    ]
)
departments_schema = StructType(
    [
        StructField("department_id", IntegerType(), False),
        StructField("department", StringType(), True),
    ]
)

bronze_frames = {
    "bronze_orders": read_csv("orders.csv", orders_schema),
    "bronze_order_products_prior": read_csv("order_products__prior.csv", order_products_schema),
    "bronze_order_products_train": read_csv("order_products__train.csv", order_products_schema),
    "bronze_products": read_csv("products.csv", products_schema),
    "bronze_aisles": read_csv("aisles.csv", aisles_schema),
    "bronze_departments": read_csv("departments.csv", departments_schema),
}

for table_name, frame in bronze_frames.items():
    assert frame.count() > 0, f"{table_name} is empty."
    (
        frame.write.format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(qname(table_name))
    )

# COMMAND ----------
counts = [(name, spark.table(qname(name)).count()) for name in bronze_frames]
display(spark.createDataFrame(counts, ["table_name", "row_count"]))

