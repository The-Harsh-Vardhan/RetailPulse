# Databricks notebook source
# MAGIC %md
# MAGIC # Power User Classifier
# MAGIC
# MAGIC This notebook trains a `DecisionTreeClassifier` to predict whether a user falls in the top quartile of `total_orders`.

# COMMAND ----------
from pyspark.ml.classification import DecisionTreeClassifier
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml.feature import VectorAssembler
from pyspark.sql import functions as F

dbutils.widgets.text("catalog", "")
dbutils.widgets.text("schema", "retailpulse")

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
threshold = user_features.approxQuantile("total_orders", [0.75], 0.0)[0]
classified = user_features.withColumn(
    "power_user",
    F.when(F.col("total_orders") >= F.lit(threshold), F.lit(1)).otherwise(F.lit(0)),
)

assembler = VectorAssembler(inputCols=feature_columns, outputCol="features")
model_input = assembler.transform(classified).select("user_id", "features", "power_user")
train_df, test_df = model_input.randomSplit([0.8, 0.2], seed=42)

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

binary_evaluator = BinaryClassificationEvaluator(
    labelCol="power_user",
    rawPredictionCol="rawPrediction",
)
auc = binary_evaluator.evaluate(predictions)
accuracy = predictions.filter(F.col("prediction") == F.col("power_user")).count() / max(predictions.count(), 1)
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

(
    metrics.write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(qname("report_classifier_metrics"))
)

display(metrics)

feature_importance_rows = list(zip(feature_columns, model.featureImportances.toArray().tolist()))
display(spark.createDataFrame(feature_importance_rows, ["feature_name", "importance"]).orderBy(F.desc("importance")))
