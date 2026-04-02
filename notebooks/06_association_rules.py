# Databricks notebook source
# MAGIC %md
# MAGIC # Association Rules
# MAGIC
# MAGIC This notebook trains an FP-growth model on order baskets and persists the resulting rules to `mart_association_rules`.

# COMMAND ----------
from pyspark.ml.fpm import FPGrowth
from pyspark.sql import functions as F

dbutils.widgets.text("catalog", "")
dbutils.widgets.text("schema", "retailpulse")
dbutils.widgets.text("min_support", "0.005")
dbutils.widgets.text("min_confidence", "0.2")
dbutils.widgets.text("seed_products", "24852,13176")

# COMMAND ----------
catalog = dbutils.widgets.get("catalog") or spark.sql("SELECT current_catalog()").first()[0]
schema = dbutils.widgets.get("schema") or spark.sql("SELECT current_schema()").first()[0]
min_support = float(dbutils.widgets.get("min_support"))
min_confidence = float(dbutils.widgets.get("min_confidence"))
seed_products = [
    int(value.strip())
    for value in dbutils.widgets.get("seed_products").split(",")
    if value.strip()
]


def qname(name: str) -> str:
    return f"`{catalog}`.`{schema}`.`{name}`"


fact_order_items = spark.table(qname("fact_order_items"))
dim_product = spark.table(qname("dim_product"))

baskets = (
    fact_order_items.groupBy("order_id")
    .agg(F.collect_set("product_id").alias("items"))
    .filter(F.size("items") >= 2)
)

fp_growth = FPGrowth(
    itemsCol="items",
    minSupport=min_support,
    minConfidence=min_confidence,
)
fp_model = fp_growth.fit(baskets)

rules = (
    fp_model.associationRules
    .withColumn("antecedent_size", F.size("antecedent"))
    .withColumn("consequent_size", F.size("consequent"))
)

(
    rules.write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(qname("mart_association_rules"))
)

display(rules.orderBy(F.desc("lift"), F.desc("confidence")).limit(10))

# COMMAND ----------
seed_array = F.array(*[F.lit(product_id) for product_id in seed_products])
recommendations = (
    rules.filter(F.size(F.array_except(F.col("antecedent"), seed_array)) == 0)
    .withColumn("recommended_product_id", F.explode("consequent"))
    .filter(~F.col("recommended_product_id").isin(seed_products))
    .groupBy("recommended_product_id")
    .agg(
        F.max("confidence").alias("best_confidence"),
        F.max("lift").alias("best_lift"),
    )
    .join(
        dim_product.select(
            F.col("product_id").alias("recommended_product_id"),
            "product_name",
        ),
        "recommended_product_id",
        "left",
    )
    .orderBy(F.desc("best_lift"), F.desc("best_confidence"))
    .limit(3)
)

display(recommendations)

