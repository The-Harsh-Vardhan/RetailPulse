# Databricks notebook source
# MAGIC %md
# MAGIC # Association Rules
# MAGIC
# MAGIC This notebook derives serverless-safe pairwise association rules from order baskets and persists them to `mart_association_rules`.
# MAGIC
# MAGIC ## Run Inputs
# MAGIC - `catalog`: optional override for the active catalog
# MAGIC - `schema`: schema that contains the gold marts
# MAGIC - `min_support`: minimum support threshold for a rule to survive
# MAGIC - `min_confidence`: minimum confidence threshold for a rule to survive
# MAGIC - `seed_products`: comma-separated product ids used for a recommendation example
# MAGIC
# MAGIC ## Source Tables
# MAGIC - `fact_order_items`
# MAGIC - `dim_product`
# MAGIC
# MAGIC ## Output Tables And Artifacts
# MAGIC - `mart_association_rules`
# MAGIC - A top-rules preview
# MAGIC - A seed-product recommendation preview
# MAGIC
# MAGIC ## Workflow
# MAGIC 1. Build basket-level item sets from the fact table.
# MAGIC 2. Count pairwise co-occurrences and derive support, confidence, and lift.
# MAGIC 3. Persist the surviving rules.
# MAGIC 4. Show a recommendation example for the configured seed products.

# COMMAND ----------
# MAGIC %md
# MAGIC ## Capture Runtime Inputs
# MAGIC
# MAGIC The thresholds stay as widgets so you can tighten or relax the recommendation evidence without editing notebook code.

# COMMAND ----------
from pyspark.sql import functions as F

dbutils.widgets.text("catalog", "")
dbutils.widgets.text("schema", "retailpulse")
dbutils.widgets.text("min_support", "0.005")
dbutils.widgets.text("min_confidence", "0.2")
dbutils.widgets.text("seed_products", "24852,13176")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Resolve Context And Load Gold Tables
# MAGIC
# MAGIC The seed product list is parsed once here so the later recommendation preview can stay purely DataFrame-based.

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

# COMMAND ----------
# MAGIC %md
# MAGIC ## Build Basket-Level Pairs
# MAGIC
# MAGIC Pairwise rules are more conservative than full FP-growth, but they are reliable on the current Databricks Free Edition serverless target.

# COMMAND ----------
baskets = (
    fact_order_items.groupBy("order_id")
    .agg(F.collect_set("product_id").alias("items"))
    .filter(F.size("items") >= 2)
)

total_baskets = baskets.count()
assert total_baskets > 0, "No baskets were found for association-rule mining."

basket_items = baskets.select(
    "order_id",
    F.explode("items").alias("product_id"),
)

antecedent_counts = basket_items.groupBy("product_id").agg(
    F.count("*").alias("antecedent_order_count")
)
consequent_counts = basket_items.groupBy("product_id").agg(
    F.count("*").alias("consequent_order_count")
)

# COMMAND ----------
# MAGIC %md
# MAGIC ## Derive Rule Metrics
# MAGIC
# MAGIC The self-join enumerates product pairs inside the same basket, then derives support, confidence, and lift from the pair counts.

# COMMAND ----------
rules = (
    basket_items.alias("left")
    .join(basket_items.alias("right"), "order_id")
    .filter(F.col("left.product_id") != F.col("right.product_id"))
    .groupBy(
        F.col("left.product_id").alias("antecedent_product_id"),
        F.col("right.product_id").alias("consequent_product_id"),
    )
    .agg(F.count("*").alias("pair_order_count"))
    .join(
        antecedent_counts,
        F.col("antecedent_product_id") == antecedent_counts["product_id"],
        "inner",
    )
    .drop(antecedent_counts["product_id"])
    .join(
        consequent_counts,
        F.col("consequent_product_id") == consequent_counts["product_id"],
        "inner",
    )
    .drop(consequent_counts["product_id"])
    .withColumn("support", F.col("pair_order_count") / F.lit(float(total_baskets)))
    .withColumn("confidence", F.col("pair_order_count") / F.col("antecedent_order_count"))
    .withColumn(
        "lift",
        F.col("confidence") / (F.col("consequent_order_count") / F.lit(float(total_baskets))),
    )
    .filter(F.col("support") >= F.lit(min_support))
    .filter(F.col("confidence") >= F.lit(min_confidence))
    .withColumn("antecedent", F.array("antecedent_product_id"))
    .withColumn("consequent", F.array("consequent_product_id"))
    .withColumn("antecedent_size", F.lit(1))
    .withColumn("consequent_size", F.lit(1))
    .select(
        "antecedent",
        "consequent",
        "antecedent_product_id",
        "consequent_product_id",
        "pair_order_count",
        "antecedent_order_count",
        "consequent_order_count",
        "support",
        "confidence",
        "lift",
        "antecedent_size",
        "consequent_size",
    )
)

# COMMAND ----------
# MAGIC %md
# MAGIC ## Persist And Review The Rule Table
# MAGIC
# MAGIC The persisted mart is the reusable recommendation surface. Later notebooks should read it instead of recalculating rules.

# COMMAND ----------
(
    rules.write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(qname("mart_association_rules"))
)

display(rules.orderBy(F.desc("lift"), F.desc("confidence")).limit(10))

# COMMAND ----------
# MAGIC %md
# MAGIC ## Seed Recommendation Example
# MAGIC
# MAGIC This is a presentation convenience: it shows how the rule table can be turned into candidate next-best products for a chosen seed basket.

# COMMAND ----------
seed_array = F.array(*[F.lit(product_id) for product_id in seed_products])
recommendations = (
    rules.filter(F.size(F.array_except(F.col("antecedent"), seed_array)) == 0)
    .withColumn("recommended_product_id", F.col("consequent_product_id"))
    .filter(~F.col("consequent_product_id").isin(seed_products))
    .groupBy("recommended_product_id")
    .agg(
        F.max("confidence").alias("best_confidence"),
        F.max("lift").alias("best_lift"),
        F.count("*").alias("matched_rule_count"),
    )
    .join(
        dim_product.select(
            F.col("product_id").alias("recommended_product_id"),
            "product_name",
        ),
        "recommended_product_id",
        "left",
    )
    .orderBy(F.desc("matched_rule_count"), F.desc("best_lift"), F.desc("best_confidence"))
    .limit(3)
)

display(recommendations)

# COMMAND ----------
# MAGIC %md
# MAGIC ## Interpretation Note
# MAGIC
# MAGIC The strongest rules are useful prescriptive evidence because they combine co-occurrence frequency with directional strength. Treat support, confidence, and lift together rather than relying on any single metric.
