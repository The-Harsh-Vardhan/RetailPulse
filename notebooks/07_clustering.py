# Databricks notebook source
# MAGIC %md
# MAGIC # Customer Clustering
# MAGIC
# MAGIC This notebook evaluates KMeans for `k = 3, 4, 5`, keeps the best silhouette score, and writes the chosen cluster labels back to `mart_user_features`.

# COMMAND ----------
from pyspark.ml.clustering import KMeans
from pyspark.ml.evaluation import ClusteringEvaluator
from pyspark.ml.feature import StandardScaler, VectorAssembler
from pyspark.sql import functions as F

dbutils.widgets.text("catalog", "")
dbutils.widgets.text("schema", "retailpulse")

# COMMAND ----------
catalog = dbutils.widgets.get("catalog") or spark.sql("SELECT current_catalog()").first()[0]
schema = dbutils.widgets.get("schema") or spark.sql("SELECT current_schema()").first()[0]


def qname(name: str) -> str:
    return f"`{catalog}`.`{schema}`.`{name}`"


feature_columns = [
    "total_orders",
    "avg_basket_size",
    "avg_days_since_prior_order",
    "avg_reordered_item_rate",
    "avg_distinct_department_count",
    "avg_order_hour_of_day",
    "active_days",
]

user_features = spark.table(qname("mart_user_features"))
for stale_column in ("cluster_id", "chosen_k"):
    if stale_column in user_features.columns:
        user_features = user_features.drop(stale_column)

user_features = user_features.fillna(0.0, subset=feature_columns)

assembler = VectorAssembler(inputCols=feature_columns, outputCol="feature_vector")
assembled = assembler.transform(user_features)
scaler = StandardScaler(
    inputCol="feature_vector",
    outputCol="features",
    withStd=True,
    withMean=True,
)
scaled = scaler.fit(assembled).transform(assembled)

results = []
predictions_by_k = {}

for k_value in (3, 4, 5):
    prediction_col = f"cluster_id_{k_value}"
    evaluator = ClusteringEvaluator(featuresCol="features", predictionCol=prediction_col)
    model = KMeans(
        featuresCol="features",
        predictionCol=prediction_col,
        k=k_value,
        seed=42,
        maxIter=30,
    ).fit(scaled)
    predicted = model.transform(scaled)
    silhouette = evaluator.evaluate(predicted)
    results.append((k_value, silhouette))
    predictions_by_k[k_value] = predicted

scores_df = spark.createDataFrame(results, ["k", "silhouette_score"]).orderBy(F.desc("silhouette_score"))
display(scores_df)

best_k = scores_df.first()["k"]
best_predictions = predictions_by_k[best_k]
best_prediction_col = f"cluster_id_{best_k}"

clustered_user_features = (
    best_predictions.drop("feature_vector", "features")
    .withColumnRenamed(best_prediction_col, "cluster_id")
    .withColumn("chosen_k", F.lit(int(best_k)))
)

(
    clustered_user_features.write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(qname("mart_user_features"))
)

cluster_profiles = (
    clustered_user_features.groupBy("cluster_id")
    .agg(
        F.count("*").alias("users_in_cluster"),
        F.avg("total_orders").alias("avg_total_orders"),
        F.avg("avg_basket_size").alias("avg_basket_size"),
        F.avg("avg_reordered_item_rate").alias("avg_reordered_item_rate"),
        F.avg("avg_days_since_prior_order").alias("avg_days_since_prior_order"),
    )
    .orderBy("cluster_id")
)

(
    cluster_profiles.write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(qname("report_cluster_profiles"))
)

display(cluster_profiles)
