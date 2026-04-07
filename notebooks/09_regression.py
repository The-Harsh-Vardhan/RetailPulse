# Databricks notebook source
# MAGIC %md
# MAGIC # Basket Size Regression
# MAGIC
# MAGIC This notebook trains a `LinearRegression` model to predict `basket_size` from order context and prior user behavior.
# MAGIC
# MAGIC ## Run Inputs
# MAGIC - `catalog`: optional override for the active catalog
# MAGIC - `schema`: schema that contains the fact tables and feature mart
# MAGIC
# MAGIC ## Source Tables
# MAGIC - `fact_orders`
# MAGIC - `mart_user_features`
# MAGIC
# MAGIC ## Output Tables And Artifacts
# MAGIC - `report_regression_metrics`
# MAGIC - A prediction preview table for quick inspection
# MAGIC
# MAGIC ## Scope Note
# MAGIC Classifier and regression results are exploratory and useful for demo discussion, but not final predictive proof. Methodology tightening is still pending.
# MAGIC
# MAGIC ## Workflow
# MAGIC 1. Join order-level context with the reusable user feature mart.
# MAGIC 2. Assemble the regression feature vector.
# MAGIC 3. Train the linear model and compare it against a mean baseline.
# MAGIC 4. Persist the evaluation metrics for later review.

# COMMAND ----------
# MAGIC %md
# MAGIC ## Capture Runtime Inputs
# MAGIC
# MAGIC This notebook documents the current exploratory predictive lane. It is intentionally not a leakage-safe redesign in this release.

# COMMAND ----------
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression
from pyspark.sql import functions as F

dbutils.widgets.text("catalog", "")
dbutils.widgets.text("schema", "retailpulse")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Resolve Context And Load Inputs
# MAGIC
# MAGIC The feature list combines order context with reusable user aggregates so the resulting report table stays aligned with the rest of the release package.

# COMMAND ----------
catalog = dbutils.widgets.get("catalog") or spark.sql("SELECT current_catalog()").first()[0]
schema = dbutils.widgets.get("schema") or spark.sql("SELECT current_schema()").first()[0]


def qname(name: str) -> str:
    return f"`{catalog}`.`{schema}`.`{name}`"


feature_columns = [
    "order_number",
    "order_dow",
    "order_hour_of_day",
    "days_since_prior_order",
    "total_orders",
    "avg_basket_size",
    "avg_days_since_prior_order",
    "avg_reordered_item_rate",
    "avg_distinct_department_count",
    "cluster_id",
]

fact_orders = spark.table(qname("fact_orders"))
user_features = spark.table(qname("mart_user_features"))

regression_input = (
    fact_orders.join(user_features.select("user_id", *[col for col in feature_columns if col in user_features.columns]), "user_id", "left")
    .fillna(0.0, subset=[col for col in feature_columns if col not in {"order_number", "order_dow", "order_hour_of_day"}])
    .fillna(0, subset=["order_number", "order_dow", "order_hour_of_day"])
)

# COMMAND ----------
# MAGIC %md
# MAGIC ## Assemble The Regression Dataset
# MAGIC
# MAGIC The target is `basket_size`, while the feature vector mixes current-order context with user-level history features.

# COMMAND ----------
assembler = VectorAssembler(inputCols=feature_columns, outputCol="features")
model_input = assembler.transform(regression_input).select("features", "basket_size")
train_df, test_df = model_input.randomSplit([0.8, 0.2], seed=42)

# COMMAND ----------
# MAGIC %md
# MAGIC ## Train And Evaluate The Linear Model
# MAGIC
# MAGIC The mean-basket baseline is included so the regression table keeps a simple benchmark alongside RMSE and R-squared.

# COMMAND ----------
linear_regression = LinearRegression(
    labelCol="basket_size",
    featuresCol="features",
    predictionCol="prediction",
    maxIter=50,
    regParam=0.05,
    elasticNetParam=0.0,
)
model = linear_regression.fit(train_df)
predictions = model.transform(test_df)

rmse_evaluator = RegressionEvaluator(
    labelCol="basket_size",
    predictionCol="prediction",
    metricName="rmse",
)
r2_evaluator = RegressionEvaluator(
    labelCol="basket_size",
    predictionCol="prediction",
    metricName="r2",
)
rmse = rmse_evaluator.evaluate(predictions)
r2 = r2_evaluator.evaluate(predictions)

mean_basket_size = train_df.agg(F.avg("basket_size").alias("mean_basket_size")).first()["mean_basket_size"]
baseline_predictions = test_df.withColumn("prediction", F.lit(mean_basket_size))
baseline_rmse = rmse_evaluator.evaluate(baseline_predictions)

metrics = spark.createDataFrame(
    [
        ("linear_regression_rmse", float(rmse)),
        ("linear_regression_r2", float(r2)),
        ("mean_baseline_rmse", float(baseline_rmse)),
    ],
    ["metric_name", "metric_value"],
)

# COMMAND ----------
# MAGIC %md
# MAGIC ## Persist Regression Metrics
# MAGIC
# MAGIC The metric table is reused by the dashboard, the report pack, and the predictive analysis deep-dive notebook.

# COMMAND ----------
(
    metrics.write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(qname("report_regression_metrics"))
)

# COMMAND ----------
# MAGIC %md
# MAGIC ## Review Regression Evidence
# MAGIC
# MAGIC Use the metric table for summary review and the prediction preview only for sanity-checking that the fitted values are in a plausible range.

# COMMAND ----------
display(metrics)
display(predictions.select("basket_size", "prediction").limit(50))
