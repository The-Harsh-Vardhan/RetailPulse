# Databricks notebook source
# MAGIC %md
# MAGIC # Predictive Analysis Deep Dive
# MAGIC
# MAGIC This notebook packages the current predictive lane into one readable review surface. It does not retrain models or change the reported metrics.
# MAGIC
# MAGIC ## Run Inputs
# MAGIC - `catalog`: optional override for the active catalog
# MAGIC - `schema`: schema that contains the mart and predictive report tables
# MAGIC
# MAGIC ## Source Tables
# MAGIC - `mart_user_features`
# MAGIC - `report_classifier_metrics`
# MAGIC - `report_classifier_feature_importance`
# MAGIC - `report_regression_metrics`
# MAGIC
# MAGIC ## Outputs
# MAGIC - Read-only summaries of the current feature set
# MAGIC - Combined predictive metric review tables
# MAGIC - Feature-importance review for the classifier
# MAGIC
# MAGIC ## Scope Note
# MAGIC Classifier and regression results are exploratory and useful for demo discussion, but not final predictive proof. Methodology tightening is still pending.
# MAGIC
# MAGIC ## Workflow
# MAGIC 1. Load the persisted predictive report tables.
# MAGIC 2. Summarize the feature mart that feeds the exploratory models.
# MAGIC 3. Explain the feature set and baseline metrics in plain language.
# MAGIC 4. Present the combined predictive evidence without rerunning training.

# COMMAND ----------
# MAGIC %md
# MAGIC ## Capture Runtime Inputs
# MAGIC
# MAGIC This notebook is presentation-first. It reads persisted outputs from `08_classifier.py` and `09_regression.py` instead of recalculating them.

# COMMAND ----------
from pyspark.sql import functions as F

dbutils.widgets.text("catalog", "")
dbutils.widgets.text("schema", "retailpulse")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Resolve Context And Load Predictive Tables
# MAGIC
# MAGIC The notebook stays read-only so it can be added safely after the report pack in the standard rebuild job.

# COMMAND ----------
catalog = dbutils.widgets.get("catalog") or spark.sql("SELECT current_catalog()").first()[0]
schema = dbutils.widgets.get("schema") or spark.sql("SELECT current_schema()").first()[0]


def qname(name: str) -> str:
    return f"`{catalog}`.`{schema}`.`{name}`"


user_features = spark.table(qname("mart_user_features"))
classifier_metrics = spark.table(qname("report_classifier_metrics"))
classifier_feature_importance = spark.table(qname("report_classifier_feature_importance"))
regression_metrics = spark.table(qname("report_regression_metrics"))

# COMMAND ----------
# MAGIC %md
# MAGIC ## Summarize The Feature Mart
# MAGIC
# MAGIC This context block reminds reviewers what kind of user-level information the exploratory models are built on.

# COMMAND ----------
feature_snapshot = user_features.agg(
    F.countDistinct("user_id").alias("users_profiled"),
    F.avg("total_orders").alias("avg_total_orders"),
    F.avg("avg_basket_size").alias("avg_basket_size"),
    F.avg("avg_reordered_item_rate").alias("avg_reordered_item_rate"),
    F.avg("active_days").alias("avg_active_days"),
).first()

feature_summary_rows = [
    ("users_profiled", int(feature_snapshot["users_profiled"])),
    ("avg_total_orders", float(feature_snapshot["avg_total_orders"] or 0.0)),
    ("avg_basket_size", float(feature_snapshot["avg_basket_size"] or 0.0)),
    ("avg_reordered_item_rate", float(feature_snapshot["avg_reordered_item_rate"] or 0.0)),
    ("avg_active_days", float(feature_snapshot["avg_active_days"] or 0.0)),
]
feature_summary_df = spark.createDataFrame(feature_summary_rows, ["summary_item", "value"])

display(feature_summary_df)

# COMMAND ----------
# MAGIC %md
# MAGIC ## Explain The Feature Set
# MAGIC
# MAGIC The feature dictionary below maps the persisted mart columns to their role in the exploratory classifier and regression notebooks.

# COMMAND ----------
feature_dictionary = spark.createDataFrame(
    [
        ("avg_basket_size", "mart_user_features", "Average items per order for a user", "Classifier and regression input"),
        ("avg_days_since_prior_order", "mart_user_features", "Average gap between a user's orders", "Classifier and regression input"),
        ("avg_reordered_item_rate", "mart_user_features", "Average reorder rate inside user baskets", "Classifier and regression input"),
        ("avg_distinct_department_count", "mart_user_features", "Average number of departments touched per order", "Classifier and regression input"),
        ("avg_order_hour_of_day", "mart_user_features", "Typical ordering hour for the user", "Classifier input"),
        ("active_days", "mart_user_features", "Number of distinct days of week in a user's history", "Classifier input"),
        ("cluster_id", "mart_user_features from 07_clustering", "Assigned customer segment id", "Classifier and regression input"),
        ("order_number", "fact_orders joined in 09_regression", "Order sequence index within a user history", "Regression input"),
        ("order_dow", "fact_orders", "Day of week for the order", "Regression input"),
        ("order_hour_of_day", "fact_orders", "Hour of day for the order", "Regression input"),
        ("days_since_prior_order", "fact_orders", "Gap since the prior order", "Regression input"),
        ("power_user", "Derived inside 08_classifier", "1 when total_orders is at or above the top quartile threshold", "Classifier target"),
        ("basket_size", "fact_orders", "Number of items in the order", "Regression target"),
    ],
    ["feature_or_target", "source", "meaning", "used_for"],
)

display(feature_dictionary)

# COMMAND ----------
# MAGIC %md
# MAGIC ## Review Persisted Metrics And Baselines
# MAGIC
# MAGIC These are the metrics already written by the exploratory notebooks. This notebook only repackages them for easier review.

# COMMAND ----------
predictive_metrics = classifier_metrics.withColumn("analysis_lane", F.lit("classifier")).unionByName(
    regression_metrics.withColumn("analysis_lane", F.lit("regression"))
)

metric_glossary = spark.createDataFrame(
    [
        ("decision_tree_accuracy", "classifier", "Share of test predictions that matched the exploratory power-user label."),
        ("decision_tree_auc", "classifier", "Ranking quality of the classifier across decision thresholds."),
        ("majority_baseline_accuracy", "classifier", "Accuracy from always predicting the dominant class."),
        ("power_user_threshold_total_orders", "classifier", "Observed total-order threshold used to define the positive class."),
        ("linear_regression_rmse", "regression", "Typical prediction error in basket-size units."),
        ("linear_regression_r2", "regression", "Share of variance explained by the linear model on the sampled split."),
        ("mean_baseline_rmse", "regression", "Error from always predicting the training-set mean basket size."),
    ],
    ["metric_name", "analysis_lane", "interpretation"],
)

metric_review = predictive_metrics.join(metric_glossary, ["metric_name", "analysis_lane"], "left")

display(metric_review.orderBy("analysis_lane", "metric_name"))

# COMMAND ----------
# MAGIC %md
# MAGIC ## Review Classifier Feature Importance
# MAGIC
# MAGIC Feature importance is the most interpretable artifact in the current predictive lane because it shows which persisted user signals the tree relied on most heavily.

# COMMAND ----------
feature_importance_review = classifier_feature_importance.join(
    feature_dictionary.select(
        F.col("feature_or_target").alias("feature_name"),
        "meaning",
        "used_for",
    ),
    "feature_name",
    "left",
)

display(feature_importance_review.orderBy(F.desc("importance")))

# COMMAND ----------
# MAGIC %md
# MAGIC ## Interpretation Note
# MAGIC
# MAGIC Use this notebook to discuss the exploratory predictive lane honestly:
# MAGIC - the models did produce persisted metrics and an interpretable feature-importance table
# MAGIC - the outputs are useful for discussion and future-work planning
# MAGIC - the current methodology is still not strong enough to claim final predictive proof
