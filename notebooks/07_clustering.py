# Databricks notebook source
# MAGIC %md
# MAGIC # Customer Clustering
# MAGIC
# MAGIC This notebook evaluates KMeans for `k = 3, 4, 5`, selects the best silhouette score, writes the chosen cluster labels back to `mart_user_features`, and persists segment profiles.
# MAGIC
# MAGIC ## Run Inputs
# MAGIC - `catalog`: optional override for the active catalog
# MAGIC - `schema`: schema that contains the user feature mart
# MAGIC
# MAGIC ## Source Table
# MAGIC - `mart_user_features`
# MAGIC
# MAGIC ## Output Tables
# MAGIC - `report_cluster_k_scores`
# MAGIC - Updated `mart_user_features` with `cluster_id` and `chosen_k`
# MAGIC - `report_cluster_profiles`
# MAGIC
# MAGIC ## Workflow
# MAGIC 1. Load the user feature mart.
# MAGIC 2. Assemble and scale the clustering features.
# MAGIC 3. Evaluate `k = 3, 4, 5` with silhouette score.
# MAGIC 4. Persist the winning cluster assignments and cluster profiles.

# COMMAND ----------
# MAGIC %md
# MAGIC ## Capture Runtime Inputs
# MAGIC
# MAGIC The notebook keeps the current segmentation recipe stable so the dashboard and report tables remain aligned across reruns.

# COMMAND ----------
from pyspark.ml.clustering import KMeans
from pyspark.ml.evaluation import ClusteringEvaluator
from pyspark.ml.feature import StandardScaler, VectorAssembler
from pyspark.sql import functions as F

dbutils.widgets.text("catalog", "")
dbutils.widgets.text("schema", "retailpulse")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Resolve Context And Load User Features
# MAGIC
# MAGIC Remove any stale clustering columns before feature assembly so reruns never feed yesterday's labels back into today's segmentation.

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

# COMMAND ----------
# MAGIC %md
# MAGIC ## Assemble And Scale Features
# MAGIC
# MAGIC Standardization keeps large-range metrics such as `total_orders` from dominating smaller-rate features during distance calculations.

# COMMAND ----------
assembler = VectorAssembler(inputCols=feature_columns, outputCol="feature_vector")
assembled = assembler.transform(user_features)
scaler = StandardScaler(
    inputCol="feature_vector",
    outputCol="features",
    withStd=True,
    withMean=True,
)
scaled = scaler.fit(assembled).transform(assembled)

# COMMAND ----------
# MAGIC %md
# MAGIC ## Evaluate Candidate K Values
# MAGIC
# MAGIC Store every candidate result so the chosen `k` is inspectable later instead of being hard-coded without evidence.

# COMMAND ----------
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

scores_df = spark.createDataFrame(results, ["cluster_k", "silhouette_score"]).orderBy(F.desc("silhouette_score"))

(
    scores_df.write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(qname("report_cluster_k_scores"))
)

display(scores_df)

# COMMAND ----------
# MAGIC %md
# MAGIC ## Persist Winning Cluster Assignments
# MAGIC
# MAGIC The chosen cluster ids are written back into `mart_user_features` because later notebooks expect a single reusable segmentation column.

# COMMAND ----------
best_k = int(scores_df.first()["cluster_k"])
best_predictions = predictions_by_k[best_k]
best_prediction_col = f"cluster_id_{best_k}"

clustered_user_features = (
    best_predictions.drop("feature_vector", "features")
    .withColumnRenamed(best_prediction_col, "cluster_id")
    .withColumn("chosen_k", F.lit(best_k))
)

(
    clustered_user_features.write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(qname("mart_user_features"))
)

# COMMAND ----------
# MAGIC %md
# MAGIC ## Build Cluster Profiles
# MAGIC
# MAGIC These aggregated profiles are the human-readable summary used by the dashboard, report pack, and prescriptive deep dive.

# COMMAND ----------
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

# COMMAND ----------
# MAGIC %md
# MAGIC ## Interpretation Note
# MAGIC
# MAGIC Keep the cluster profiles in the descriptive and prescriptive lane. They are useful for audience segmentation, but they are not a causal explanation of customer behavior on their own.
