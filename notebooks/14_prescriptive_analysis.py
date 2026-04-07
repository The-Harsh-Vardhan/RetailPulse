# Databricks notebook source
# MAGIC %md
# MAGIC # Prescriptive Analysis Deep Dive
# MAGIC
# MAGIC This notebook packages the current action-oriented outputs into one review surface using persisted recommendations, segment profiles, and timing/category patterns.
# MAGIC
# MAGIC ## Run Inputs
# MAGIC - `catalog`: optional override for the active catalog
# MAGIC - `schema`: schema that contains the recommendation, segmentation, and OLAP report tables
# MAGIC - `seed_product_name`: example product name used for the recommendation walkthrough
# MAGIC
# MAGIC ## Source Tables
# MAGIC - `mart_association_rules`
# MAGIC - `dim_product`
# MAGIC - `dim_department`
# MAGIC - `report_cluster_profiles`
# MAGIC - `report_cluster_k_scores`
# MAGIC - `report_olap_basket`
# MAGIC - `report_olap_rollup`
# MAGIC
# MAGIC ## Outputs
# MAGIC - Read-only recommendation evidence with named products
# MAGIC - Segment-aware action playbooks
# MAGIC - Timing and department opportunity tables
# MAGIC
# MAGIC ## Workflow
# MAGIC 1. Load the persisted recommendation, segmentation, and OLAP tables.
# MAGIC 2. Reformat the rule mart into named recommendation views.
# MAGIC 3. Translate cluster profiles into plain-language action suggestions.
# MAGIC 4. Highlight daypart and timing opportunities from the descriptive report tables.

# COMMAND ----------
# MAGIC %md
# MAGIC ## Capture Runtime Inputs
# MAGIC
# MAGIC This notebook stays read-only. It turns existing report tables into plain-language actions instead of introducing new persisted outputs.

# COMMAND ----------
from pyspark.sql import functions as F

dbutils.widgets.text("catalog", "")
dbutils.widgets.text("schema", "retailpulse")
dbutils.widgets.text("seed_product_name", "Organic Raspberries")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Resolve Context And Load Prescriptive Inputs
# MAGIC
# MAGIC The same named-product joins used in the report pack are reused here so recommendation outputs are readable without raw product ids.

# COMMAND ----------
catalog = dbutils.widgets.get("catalog") or spark.sql("SELECT current_catalog()").first()[0]
schema = dbutils.widgets.get("schema") or spark.sql("SELECT current_schema()").first()[0]
seed_product_name = dbutils.widgets.get("seed_product_name")


def qname(name: str) -> str:
    return f"`{catalog}`.`{schema}`.`{name}`"


dim_product = spark.table(qname("dim_product"))
dim_department = spark.table(qname("dim_department"))
association_rules = spark.table(qname("mart_association_rules"))
cluster_profiles = spark.table(qname("report_cluster_profiles"))
cluster_k_scores = spark.table(qname("report_cluster_k_scores"))
olap_basket = spark.table(qname("report_olap_basket"))
olap_rollup = spark.table(qname("report_olap_rollup"))

day_name = (
    F.when(F.col("order_dow") == 0, "Sun")
    .when(F.col("order_dow") == 1, "Mon")
    .when(F.col("order_dow") == 2, "Tue")
    .when(F.col("order_dow") == 3, "Wed")
    .when(F.col("order_dow") == 4, "Thu")
    .when(F.col("order_dow") == 5, "Fri")
    .when(F.col("order_dow") == 6, "Sat")
)

# COMMAND ----------
# MAGIC %md
# MAGIC ## Review Top Cross-Sell Rules
# MAGIC
# MAGIC These rows show the strongest pairwise recommendation evidence with named products and the three key rule metrics together.

# COMMAND ----------
top_rules = (
    association_rules
    .join(
        dim_product.select(
            F.col("product_id").alias("antecedent_product_id"),
            F.col("product_name").alias("antecedent_product_name"),
        ),
        "antecedent_product_id",
        "left",
    )
    .join(
        dim_product.select(
            F.col("product_id").alias("consequent_product_id"),
            F.col("product_name").alias("recommended_product_name"),
        ),
        "consequent_product_id",
        "left",
    )
    .select(
        "antecedent_product_name",
        "recommended_product_name",
        "pair_order_count",
        "support",
        "confidence",
        "lift",
    )
    .orderBy(F.desc("lift"), F.desc("confidence"))
    .limit(15)
)

display(top_rules)

# COMMAND ----------
# MAGIC %md
# MAGIC ## Review Seed-Product Recommendations
# MAGIC
# MAGIC This is the nearest thing to a current next-best-action surface in RetailPulse: start from one known product and inspect the strongest companion products.

# COMMAND ----------
seed_recommendations = (
    association_rules
    .join(
        dim_product.select(
            F.col("product_id").alias("antecedent_product_id"),
            F.col("product_name").alias("seed_product_name"),
        ),
        "antecedent_product_id",
        "left",
    )
    .join(
        dim_product.select(
            F.col("product_id").alias("consequent_product_id"),
            F.col("product_name").alias("recommended_product_name"),
        ),
        "consequent_product_id",
        "left",
    )
    .filter(F.col("seed_product_name") == F.lit(seed_product_name))
    .select(
        "seed_product_name",
        "recommended_product_name",
        "pair_order_count",
        "support",
        "confidence",
        "lift",
    )
    .orderBy(F.desc("lift"), F.desc("confidence"))
    .limit(10)
)

display(seed_recommendations)

# COMMAND ----------
# MAGIC %md
# MAGIC ## Translate Segment Profiles Into Actions
# MAGIC
# MAGIC The heuristics below keep the current segment labels aligned with the report pack while adding plain-language action guidance.

# COMMAND ----------
segment_actions = (
    cluster_profiles
    .withColumn(
        "segment_name",
        F.when((F.col("avg_total_orders") >= 20) & (F.col("avg_reordered_item_rate") >= 0.55), "Frequent loyal shoppers")
        .when(F.col("avg_basket_size") >= 14, "Large-basket stock-up shoppers")
        .otherwise("Light occasional shoppers"),
    )
    .withColumn(
        "recommended_action",
        F.when(
            F.col("segment_name") == "Frequent loyal shoppers",
            F.lit("Prioritize replenishment reminders and loyalty bundles."),
        )
        .when(
            F.col("segment_name") == "Large-basket stock-up shoppers",
            F.lit("Promote family-size bundles and pantry stock-up offers."),
        )
        .otherwise(F.lit("Use lightweight reactivation prompts and simpler starter bundles.")),
    )
    .withColumn(
        "why_it_fits",
        F.when(
            F.col("segment_name") == "Frequent loyal shoppers",
            F.lit("High order frequency and strong reorder behavior suggest repeat-need items."),
        )
        .when(
            F.col("segment_name") == "Large-basket stock-up shoppers",
            F.lit("Large baskets suggest bulk or planned shopping missions."),
        )
        .otherwise(F.lit("Lower activity suggests gentle prompts are safer than aggressive cross-sell tactics.")),
    )
    .orderBy(F.desc("users_in_cluster"), "cluster_id")
)

display(segment_actions)
display(cluster_k_scores.orderBy("cluster_k"))

# COMMAND ----------
# MAGIC %md
# MAGIC ## Highlight Department And Daypart Opportunities
# MAGIC
# MAGIC These rows turn descriptive OLAP patterns into candidate campaign or merchandising suggestions.

# COMMAND ----------
daypart_opportunities = (
    olap_basket.join(dim_department, "department_id", "left")
    .withColumn(
        "recommended_action",
        F.concat(
            F.lit("Feature "),
            F.coalesce(F.col("department"), F.lit("this department")),
            F.lit(" during "),
            F.col("daypart"),
            F.lit(" because it combines volume with stronger basket size."),
        ),
    )
    .select(
        "daypart",
        "department_id",
        "department",
        "orders_seen",
        "avg_basket_size",
        "recommended_action",
    )
    .orderBy(F.desc("orders_seen"), F.desc("avg_basket_size"))
    .limit(12)
)

display(daypart_opportunities)

# COMMAND ----------
# MAGIC %md
# MAGIC ## Highlight Peak Order Windows
# MAGIC
# MAGIC Timing actions are useful operationally even without prices or promotions because they suggest when to staff, place hero items, or time communications.

# COMMAND ----------
peak_order_windows = (
    olap_rollup.filter(F.col("order_dow").isNotNull() & F.col("order_hour_of_day").isNotNull())
    .withColumn("order_day", day_name)
    .withColumn(
        "recommended_action",
        F.concat(
            F.lit("Prioritize staffing and featured placements on "),
            F.col("order_day"),
            F.lit(" around hour "),
            F.format_string("%02d", F.col("order_hour_of_day")),
            F.lit("."),
        ),
    )
    .select(
        "order_day",
        "order_dow",
        "order_hour_of_day",
        "order_count",
        "avg_basket_size",
        "recommended_action",
    )
    .orderBy(F.desc("order_count"), F.desc("avg_basket_size"))
    .limit(10)
)

display(peak_order_windows)

# COMMAND ----------
# MAGIC %md
# MAGIC ## Interpretation Note
# MAGIC
# MAGIC These are candidate actions, not automated policies. The current release is strongest when you use recommendation rules, segment profiles, and timing patterns as human-reviewed decision support.
