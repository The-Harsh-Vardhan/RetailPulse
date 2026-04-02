# Databricks notebook source
# MAGIC %md
# MAGIC # Basket Size Regression
# MAGIC
# MAGIC This notebook trains a `LinearRegression` model to predict `basket_size` from order context and prior user behavior.

# COMMAND ----------
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression
from pyspark.sql import functions as F

dbutils.widgets.text("catalog", "")
dbutils.widgets.text("schema", "retailpulse")

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
    .fillna(0.0, subset=[col for col in feature_columns if col != "order_number" and col != "order_dow" and col != "order_hour_of_day"])
    .fillna(0, subset=["order_number", "order_dow", "order_hour_of_day"])
)

assembler = VectorAssembler(inputCols=feature_columns, outputCol="features")
model_input = assembler.transform(regression_input).select("features", "basket_size")
train_df, test_df = model_input.randomSplit([0.8, 0.2], seed=42)

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

(
    metrics.write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(qname("report_regression_metrics"))
)

display(metrics)
display(predictions.select("basket_size", "prediction").limit(50))

