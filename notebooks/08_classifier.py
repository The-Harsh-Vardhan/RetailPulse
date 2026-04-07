# Databricks notebook source
# MAGIC %md
# MAGIC # Power User Classifier
# MAGIC
# MAGIC This notebook trains a `DecisionTreeClassifier` to predict whether a user falls in the top quartile of `total_orders`.
# MAGIC
# MAGIC ## Run Inputs
# MAGIC - `catalog`: optional override for the active catalog
# MAGIC - `schema`: schema that contains the feature mart and report tables
# MAGIC
# MAGIC ## Source Table
# MAGIC - `mart_user_features`
# MAGIC
# MAGIC ## Output Tables
# MAGIC - `report_classifier_metrics`
# MAGIC - `report_classifier_feature_importance`
# MAGIC
# MAGIC ## Scope Note
# MAGIC Classifier and regression results are exploratory and useful for demo discussion, but not final predictive proof. Methodology tightening is still pending.
# MAGIC
# MAGIC ## Workflow
# MAGIC 1. Load the user feature mart and define the `power_user` label.
# MAGIC 2. Assemble model features and split into train and test sets.
# MAGIC 3. Train the decision tree and compare it against a majority baseline.
# MAGIC 4. Persist metrics and feature-importance outputs for later review.

# COMMAND ----------
# MAGIC %md
# MAGIC ## Capture Runtime Inputs
# MAGIC
# MAGIC The notebook keeps the current exploratory setup stable so later presentation notebooks can read consistent report tables.

# COMMAND ----------
from pyspark.ml.classification import DecisionTreeClassifier
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml.feature import VectorAssembler
from pyspark.sql import functions as F

dbutils.widgets.text("catalog", "")
dbutils.widgets.text("schema", "retailpulse")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Resolve Context And Load Features
# MAGIC
# MAGIC The feature list matches the current release baseline. This notebook documents that baseline; it does not redesign it.

# COMMAND ----------
catalog = dbutils.widgets.get("catalog") or spark.sql("SELECT current_catalog()").first()[0]
schema = dbutils.widgets.get("schema") or spark.sql("SELECT current_schema()").first()[0]


def qname(name: str) -> str:
    return f"`{catalog}`.`{schema}`.`{name}`"


feature_columns = [
    "avg_basket_size",
    "avg_days_since_prior_order",
    "avg_reordered_item_rate",
    "avg_distinct_department_count",
    "avg_order_hour_of_day",
    "active_days",
    "cluster_id",
]

user_features = (
    spark.table(qname("mart_user_features"))
    .fillna(0.0, subset=feature_columns)
)

# Use the observed upper quartile as the release's current power-user threshold.
threshold = user_features.approxQuantile("total_orders", [0.75], 0.0)[0]
classified = user_features.withColumn(
    "power_user",
    F.when(F.col("total_orders") >= F.lit(threshold), F.lit(1)).otherwise(F.lit(0)),
)

# COMMAND ----------
# MAGIC %md
# MAGIC ## Assemble Model Inputs
# MAGIC
# MAGIC The classifier predicts a binary label from user-level behavior features and the currently assigned segment id.

# COMMAND ----------
assembler = VectorAssembler(inputCols=feature_columns, outputCol="features")
model_input = assembler.transform(classified).select("user_id", "features", "power_user")
train_df, test_df = model_input.randomSplit([0.8, 0.2], seed=42)

# COMMAND ----------
# MAGIC %md
# MAGIC ## Train And Evaluate The Decision Tree
# MAGIC
# MAGIC Compare the tree against a majority baseline so the metric table retains a simple point of reference.

# COMMAND ----------
decision_tree = DecisionTreeClassifier(
    labelCol="power_user",
    featuresCol="features",
    predictionCol="prediction",
    probabilityCol="probability",
    rawPredictionCol="rawPrediction",
    maxDepth=5,
    seed=42,
)
model = decision_tree.fit(train_df)
predictions = model.transform(test_df)

total_predictions = max(predictions.count(), 1)
binary_evaluator = BinaryClassificationEvaluator(
    labelCol="power_user",
    rawPredictionCol="rawPrediction",
)
auc = binary_evaluator.evaluate(predictions)
accuracy = predictions.filter(F.col("prediction") == F.col("power_user")).count() / total_predictions
label_mean = classified.agg(F.avg("power_user").alias("label_mean")).first()["label_mean"]
majority_baseline = max(label_mean, 1 - label_mean)

metrics = spark.createDataFrame(
    [
        ("decision_tree_accuracy", float(accuracy)),
        ("decision_tree_auc", float(auc)),
        ("majority_baseline_accuracy", float(majority_baseline)),
        ("power_user_threshold_total_orders", float(threshold)),
    ],
    ["metric_name", "metric_value"],
)

feature_importance_rows = list(zip(feature_columns, model.featureImportances.toArray().tolist()))
feature_importance_df = spark.createDataFrame(feature_importance_rows, ["feature_name", "importance"]).orderBy(
    F.desc("importance")
)

# COMMAND ----------
# MAGIC %md
# MAGIC ## Persist Classifier Outputs
# MAGIC
# MAGIC These report tables are consumed by the dashboard, the report pack, and the new predictive analysis notebook.

# COMMAND ----------
(
    metrics.write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(qname("report_classifier_metrics"))
)

(
    feature_importance_df.write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(qname("report_classifier_feature_importance"))
)

# COMMAND ----------
# MAGIC %md
# MAGIC ## Review Classifier Evidence
# MAGIC
# MAGIC Read these outputs as exploratory evidence only. Attractive metrics do not remove the methodology limitations documented elsewhere in the repo.

# COMMAND ----------
display(metrics)
display(feature_importance_df)
