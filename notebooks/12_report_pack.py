# Databricks notebook source
# MAGIC %md
# MAGIC # Report Pack
# MAGIC
# MAGIC This notebook is the notebook fallback for Dashboard V2 and the main evidence hub for the repo-tracked outputs.
# MAGIC
# MAGIC ## Run Inputs
# MAGIC - `catalog`: optional override for the active catalog
# MAGIC - `schema`: schema that contains the RetailPulse report tables
# MAGIC
# MAGIC ## Source Tables
# MAGIC - `dim_product`
# MAGIC - `fact_orders`
# MAGIC - `fact_order_items`
# MAGIC - `mart_association_rules`
# MAGIC - `report_cluster_profiles`
# MAGIC - `report_cluster_k_scores`
# MAGIC - `report_olap_cube`
# MAGIC - `report_olap_rollup`
# MAGIC - `report_olap_basket`
# MAGIC - `report_olap_validation`
# MAGIC - `report_stream_validation`
# MAGIC - `report_classifier_metrics`
# MAGIC - `report_regression_metrics`
# MAGIC - `report_classifier_feature_importance`
# MAGIC - `report_optimize_summary`
# MAGIC - `report_optimize_timings`
# MAGIC
# MAGIC ## Outputs
# MAGIC - A five-section notebook view that mirrors Dashboard V2
# MAGIC - Readable fallback displays for the review package and screenshot workflow
# MAGIC
# MAGIC ## Workflow
# MAGIC 1. Resolve the active catalog and schema.
# MAGIC 2. Build shared display DataFrames used across the five sections.
# MAGIC 3. Render the same five-section story as Dashboard V2.
# MAGIC 4. Keep the exploratory-model disclaimer visible only in the experimental section.

# COMMAND ----------
# MAGIC %md
# MAGIC ## Dashboard V2 Notebook Fallback
# MAGIC
# MAGIC Use the AI/BI dashboard as the primary live-demo surface.
# MAGIC
# MAGIC If the dashboard is unavailable or a panel needs drill-down, use this notebook in the same five-section story:
# MAGIC 1. Executive Overview
# MAGIC 2. Order Behavior
# MAGIC 3. Recommendations And Segments
# MAGIC 4. Execution And Data Quality
# MAGIC 5. Experimental Insights And Performance
# MAGIC
# MAGIC Classifier and regression results are exploratory and useful for demo discussion, but not final predictive proof. Methodology tightening is still pending.

# COMMAND ----------
# MAGIC %md
# MAGIC ## Capture Runtime Inputs
# MAGIC
# MAGIC This notebook is intentionally read-heavy. It packages already-persisted report tables instead of creating new warehouse state.

# COMMAND ----------
from pyspark.sql import functions as F

dbutils.widgets.text("catalog", "")
dbutils.widgets.text("schema", "retailpulse")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Resolve Context And Load Shared Inputs
# MAGIC
# MAGIC The helper and shared lookup tables are reused across multiple dashboard-style sections below.

# COMMAND ----------
catalog = dbutils.widgets.get("catalog") or spark.sql("SELECT current_catalog()").first()[0]
schema = dbutils.widgets.get("schema") or spark.sql("SELECT current_schema()").first()[0]


def qname(name: str) -> str:
    return f"`{catalog}`.`{schema}`.`{name}`"


dim_product = spark.table(qname("dim_product"))

# Keep the day-of-week label mapping explicit so the display order stays interpretable in screenshots.
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
# MAGIC ## Assemble Shared Display DataFrames
# MAGIC
# MAGIC These DataFrames mirror the dashboard widgets closely so the fallback notebook tells the same story without recomputing the underlying marts.

# COMMAND ----------
table_counts = spark.createDataFrame(
    [
        ("bronze_orders", spark.table(qname("bronze_orders")).count()),
        ("silver_order_items", spark.table(qname("silver_order_items")).count()),
        ("fact_order_items", spark.table(qname("fact_order_items")).count()),
        ("fact_orders", spark.table(qname("fact_orders")).count()),
        ("mart_association_rules", spark.table(qname("mart_association_rules")).count()),
        ("report_cluster_profiles", spark.table(qname("report_cluster_profiles")).count()),
        ("report_cluster_k_scores", spark.table(qname("report_cluster_k_scores")).count()),
        ("report_classifier_feature_importance", spark.table(qname("report_classifier_feature_importance")).count()),
        ("report_stream_validation", spark.table(qname("report_stream_validation")).count()),
        ("report_optimize_summary", spark.table(qname("report_optimize_summary")).count()),
    ],
    ["table_name", "row_count"],
)

orders_by_day = (
    spark.table(qname("report_olap_rollup"))
    .filter(F.col("order_dow").isNotNull() & F.col("order_hour_of_day").isNull())
    .withColumn("order_day", day_name)
    .select("order_day", "order_dow", "order_count", "avg_basket_size")
    .orderBy("order_dow")
)

avg_basket_by_hour = (
    spark.table(qname("fact_orders"))
    .groupBy("order_hour_of_day")
    .agg(
        F.count("*").alias("order_count"),
        F.avg("basket_size").alias("avg_basket_size"),
    )
    .orderBy("order_hour_of_day")
)

top_products = (
    spark.table(qname("fact_order_items"))
    .join(dim_product.select("product_id", "product_name"), "product_id", "left")
    .groupBy("product_name")
    .agg(
        F.count("*").alias("items_seen"),
        F.countDistinct("order_id").alias("distinct_orders"),
    )
    .orderBy(F.desc("items_seen"), F.desc("distinct_orders"), "product_name")
    .limit(15)
)

top_rules = (
    spark.table(qname("mart_association_rules"))
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
            F.col("product_name").alias("consequent_product_name"),
        ),
        "consequent_product_id",
        "left",
    )
    .select(
        "antecedent_product_name",
        "consequent_product_name",
        "pair_order_count",
        "support",
        "confidence",
        "lift",
    )
    .orderBy(F.desc("lift"), F.desc("confidence"))
    .limit(15)
)

seed_product_name = "Organic Raspberries"
seed_recommendations = (
    spark.table(qname("mart_association_rules"))
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

cluster_profiles = (
    spark.table(qname("report_cluster_profiles"))
    .withColumn(
        "segment_name",
        F.when((F.col("avg_total_orders") >= 20) & (F.col("avg_reordered_item_rate") >= 0.55), "Frequent loyal shoppers")
        .when(F.col("avg_basket_size") >= 14, "Large-basket stock-up shoppers")
        .otherwise("Light occasional shoppers"),
    )
    .orderBy(F.desc("avg_total_orders"))
)

segment_sizes = cluster_profiles.select("cluster_id", "segment_name", "users_in_cluster").orderBy(
    F.desc("users_in_cluster"), "cluster_id"
)

olap_validation_summary = (
    spark.table(qname("report_olap_validation"))
    .agg(
        F.count("*").alias("checked_groups"),
        F.sum(F.when(F.col("matches"), F.lit(1)).otherwise(F.lit(0))).alias("matched_groups"),
        F.sum(F.when(F.col("matches"), F.lit(0)).otherwise(F.lit(1))).alias("mismatched_groups"),
        F.max(F.abs(F.col("total_items") - F.col("manual_total_items"))).alias("max_item_gap"),
    )
)

# COMMAND ----------
# MAGIC %md
# MAGIC ## 1. Executive Overview
# MAGIC
# MAGIC Start with coverage and confidence: table counts, order-day pattern, and the persisted OLAP views.

# COMMAND ----------
display(table_counts)
display(orders_by_day)
display(spark.table(qname("report_olap_cube")).orderBy("department_id", "order_dow"))
display(spark.table(qname("report_olap_rollup")).orderBy("order_dow", "order_hour_of_day"))

# COMMAND ----------
# MAGIC %md
# MAGIC ## 2. Order Behavior
# MAGIC
# MAGIC This section focuses on shopping-pattern shape: basket size by daypart and hour, plus the most frequently seen products.

# COMMAND ----------
display(spark.table(qname("report_olap_basket")).orderBy("daypart", "department_id"))
display(avg_basket_by_hour)
display(top_products)

# COMMAND ----------
# MAGIC %md
# MAGIC ## 3. Recommendations And Segments
# MAGIC
# MAGIC Keep recommendation proof and customer segmentation together because they are the strongest action-oriented outputs in the current release.

# COMMAND ----------
display(top_rules)
display(seed_recommendations)
display(cluster_profiles)
display(segment_sizes)
display(spark.table(qname("report_cluster_k_scores")).orderBy("cluster_k"))

# COMMAND ----------
# MAGIC %md
# MAGIC ## 4. Execution And Data Quality
# MAGIC
# MAGIC This section shows whether the descriptive and streaming layers are trustworthy enough for a live review.

# COMMAND ----------
display(olap_validation_summary)
display(spark.table(qname("report_olap_validation")).orderBy("department_id", "order_dow"))
display(spark.table(qname("report_stream_validation")).orderBy("order_dow", "order_hour_of_day"))

# COMMAND ----------
# MAGIC %md
# MAGIC ## 5. Experimental Insights And Performance
# MAGIC
# MAGIC Classifier and regression results are exploratory and useful for demo discussion, but not final predictive proof. Methodology tightening is still pending.

# COMMAND ----------
display(spark.table(qname("report_classifier_metrics")))
display(spark.table(qname("report_regression_metrics")))
display(spark.table(qname("report_classifier_feature_importance")).orderBy(F.desc("importance")))
display(spark.table(qname("report_optimize_summary")).orderBy("query_name"))
display(spark.table(qname("report_optimize_timings")).orderBy("query_name", "run_stage"))

# COMMAND ----------
# MAGIC %md
# MAGIC ## Capture Checklist
# MAGIC
# MAGIC Use this closing table when you are collecting screenshots or walking an evaluator through the fallback notebook.

# COMMAND ----------
report_outline = [
    ("1", "Executive Overview: KPI counts, orders by day, and OLAP overview"),
    ("2", "Order Behavior: daypart basket patterns, hourly basket size, and top products"),
    ("3", "Recommendations And Segments: rules, seed recommendations, segment profiles, and k-selection"),
    ("4", "Execution And Data Quality: OLAP validation and stream validation"),
    ("5", "Experimental Insights And Performance: model metrics, feature importance, and optimize timings"),
]

display(spark.createDataFrame(report_outline, ["section", "what_to_capture"]))
