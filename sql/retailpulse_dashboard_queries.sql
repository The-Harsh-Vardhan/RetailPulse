-- RetailPulse Demo Dashboard canonical queries
-- Assumption: In Databricks SQL or AI/BI dashboard authoring, set the current catalog and schema
-- to the RetailPulse target before saving these queries. The SQL below intentionally uses only
-- the existing RetailPulse tables and marts.

-- dashboard_table_counts
SELECT 'bronze_orders' AS table_name, COUNT(*) AS row_count FROM bronze_orders
UNION ALL
SELECT 'silver_order_items' AS table_name, COUNT(*) AS row_count FROM silver_order_items
UNION ALL
SELECT 'fact_order_items' AS table_name, COUNT(*) AS row_count FROM fact_order_items
UNION ALL
SELECT 'fact_orders' AS table_name, COUNT(*) AS row_count FROM fact_orders
UNION ALL
SELECT 'mart_association_rules' AS table_name, COUNT(*) AS row_count FROM mart_association_rules
UNION ALL
SELECT 'report_cluster_profiles' AS table_name, COUNT(*) AS row_count FROM report_cluster_profiles
UNION ALL
SELECT 'report_cluster_k_scores' AS table_name, COUNT(*) AS row_count FROM report_cluster_k_scores
UNION ALL
SELECT 'report_classifier_feature_importance' AS table_name, COUNT(*) AS row_count FROM report_classifier_feature_importance
UNION ALL
SELECT 'report_stream_validation' AS table_name, COUNT(*) AS row_count FROM report_stream_validation
UNION ALL
SELECT 'report_optimize_summary' AS table_name, COUNT(*) AS row_count FROM report_optimize_summary
ORDER BY table_name
;

-- dashboard_kpi_summary
SELECT
  (SELECT COUNT(*) FROM fact_orders) AS total_orders,
  (SELECT COUNT(*) FROM fact_order_items) AS total_items,
  (SELECT COUNT(*) FROM mart_association_rules) AS recommendation_rules,
  (SELECT COUNT(*) FROM report_stream_validation) AS validated_stream_groups
;

-- dashboard_orders_by_day
SELECT
  CASE r.order_dow
    WHEN 0 THEN 'Sun'
    WHEN 1 THEN 'Mon'
    WHEN 2 THEN 'Tue'
    WHEN 3 THEN 'Wed'
    WHEN 4 THEN 'Thu'
    WHEN 5 THEN 'Fri'
    WHEN 6 THEN 'Sat'
  END AS order_day,
  r.order_dow,
  r.order_count,
  r.avg_basket_size
FROM report_olap_rollup r
WHERE r.order_dow IS NOT NULL
  AND r.order_hour_of_day IS NULL
ORDER BY r.order_dow
;

-- dashboard_department_totals
SELECT
  COALESCE(d.department, 'Unknown') AS department,
  c.total_items,
  c.distinct_orders
FROM report_olap_cube c
LEFT JOIN dim_department d
  ON c.department_id = d.department_id
WHERE c.department_id IS NOT NULL
  AND c.order_dow IS NULL
ORDER BY c.total_items DESC
LIMIT 10
;

-- dashboard_hourly_order_pattern
SELECT
  CASE r.order_dow
    WHEN 0 THEN 'Sun'
    WHEN 1 THEN 'Mon'
    WHEN 2 THEN 'Tue'
    WHEN 3 THEN 'Wed'
    WHEN 4 THEN 'Thu'
    WHEN 5 THEN 'Fri'
    WHEN 6 THEN 'Sat'
  END AS order_day,
  r.order_dow,
  r.order_hour_of_day,
  r.order_count,
  r.avg_basket_size
FROM report_olap_rollup r
WHERE r.order_dow IS NOT NULL
  AND r.order_hour_of_day IS NOT NULL
ORDER BY r.order_dow, r.order_hour_of_day
;

-- dashboard_avg_basket_by_hour
SELECT
  order_hour_of_day,
  COUNT(*) AS order_count,
  AVG(basket_size) AS avg_basket_size
FROM fact_orders
GROUP BY order_hour_of_day
ORDER BY order_hour_of_day
;

-- dashboard_daypart_basket
WITH top_departments AS (
  SELECT department_id
  FROM report_olap_basket
  GROUP BY department_id
  ORDER BY SUM(orders_seen) DESC
  LIMIT 8
)
SELECT
  COALESCE(d.department, 'Unknown') AS department,
  b.daypart,
  b.orders_seen,
  b.avg_basket_size
FROM report_olap_basket b
LEFT JOIN dim_department d
  ON b.department_id = d.department_id
INNER JOIN top_departments t
  ON b.department_id = t.department_id
ORDER BY department, b.daypart
;

-- dashboard_top_products
SELECT
  p.product_name,
  COUNT(*) AS items_seen,
  COUNT(DISTINCT foi.order_id) AS distinct_orders
FROM fact_order_items foi
LEFT JOIN dim_product p
  ON foi.product_id = p.product_id
GROUP BY p.product_name
ORDER BY items_seen DESC, distinct_orders DESC, p.product_name
LIMIT 15
;

-- dashboard_top_rules
SELECT
  ap.product_name AS antecedent_product_name,
  cp.product_name AS consequent_product_name,
  r.pair_order_count,
  r.support,
  r.confidence,
  r.lift
FROM mart_association_rules r
LEFT JOIN dim_product ap
  ON r.antecedent_product_id = ap.product_id
LEFT JOIN dim_product cp
  ON r.consequent_product_id = cp.product_id
ORDER BY r.lift DESC, r.confidence DESC
LIMIT 15
;

-- dashboard_available_seed_products
SELECT
  ap.product_name AS seed_product_name,
  COUNT(*) AS available_rule_count
FROM mart_association_rules r
LEFT JOIN dim_product ap
  ON r.antecedent_product_id = ap.product_id
GROUP BY ap.product_name
ORDER BY available_rule_count DESC, seed_product_name
LIMIT 50
;

-- dashboard_seed_recommendations
SELECT
  ap.product_name AS seed_product_name,
  cp.product_name AS recommended_product_name,
  r.pair_order_count,
  r.support,
  r.confidence,
  r.lift
FROM mart_association_rules r
LEFT JOIN dim_product ap
  ON r.antecedent_product_id = ap.product_id
LEFT JOIN dim_product cp
  ON r.consequent_product_id = cp.product_id
WHERE ap.product_name = :seed_product_name
ORDER BY r.lift DESC, r.confidence DESC
LIMIT 10
;

-- dashboard_cluster_profiles
SELECT
  cluster_id,
  CASE
    WHEN avg_total_orders >= 20 AND avg_reordered_item_rate >= 0.55 THEN 'Frequent loyal shoppers'
    WHEN avg_basket_size >= 14 THEN 'Large-basket stock-up shoppers'
    ELSE 'Light occasional shoppers'
  END AS segment_name,
  users_in_cluster,
  avg_total_orders,
  avg_basket_size,
  avg_reordered_item_rate,
  avg_days_since_prior_order
FROM report_cluster_profiles
ORDER BY avg_total_orders DESC
;

-- dashboard_segment_sizes
SELECT
  cluster_id,
  CASE
    WHEN avg_total_orders >= 20 AND avg_reordered_item_rate >= 0.55 THEN 'Frequent loyal shoppers'
    WHEN avg_basket_size >= 14 THEN 'Large-basket stock-up shoppers'
    ELSE 'Light occasional shoppers'
  END AS segment_name,
  users_in_cluster
FROM report_cluster_profiles
ORDER BY users_in_cluster DESC, cluster_id
;

-- dashboard_cluster_k_scores
SELECT
  cluster_k,
  silhouette_score
FROM report_cluster_k_scores
ORDER BY cluster_k
;

-- dashboard_stream_health
SELECT
  COUNT(*) AS checked_groups,
  SUM(CASE WHEN count_matches AND avg_basket_matches AND reordered_matches THEN 1 ELSE 0 END) AS matched_groups,
  SUM(CASE WHEN count_matches AND avg_basket_matches AND reordered_matches THEN 0 ELSE 1 END) AS mismatch_groups
FROM report_stream_validation
;

-- dashboard_stream_validation_detail
SELECT
  order_dow,
  order_hour_of_day,
  batch_order_count,
  stream_order_count,
  batch_avg_basket_size,
  stream_avg_basket_size,
  batch_reordered_items,
  stream_reordered_items,
  CASE
    WHEN count_matches AND avg_basket_matches AND reordered_matches THEN true
    ELSE false
  END AS all_checks_passed
FROM report_stream_validation
ORDER BY order_dow, order_hour_of_day
;

-- dashboard_olap_validation_summary
SELECT
  COUNT(*) AS checked_groups,
  SUM(CASE WHEN matches THEN 1 ELSE 0 END) AS matched_groups,
  SUM(CASE WHEN matches THEN 0 ELSE 1 END) AS mismatched_groups,
  MAX(ABS(total_items - manual_total_items)) AS max_item_gap
FROM report_olap_validation
;

-- dashboard_optimize_comparison
SELECT
  query_name,
  before_optimize,
  after_optimize,
  seconds_saved,
  speedup_ratio,
  CASE
    WHEN seconds_saved >= 0 THEN 'faster_or_equal'
    ELSE 'slower_on_sample'
  END AS performance_outcome
FROM report_optimize_summary
ORDER BY query_name
;

-- dashboard_optimize_raw_timings
SELECT
  query_name,
  run_stage,
  seconds
FROM report_optimize_timings
ORDER BY query_name,
  CASE run_stage
    WHEN 'before_optimize' THEN 1
    WHEN 'after_optimize' THEN 2
    ELSE 3
  END
;

-- dashboard_exploratory_metrics
SELECT
  'classifier' AS metric_group,
  metric_name,
  metric_value,
  1 AS metric_group_order
FROM report_classifier_metrics
UNION ALL
SELECT
  'regression' AS metric_group,
  metric_name,
  metric_value,
  2 AS metric_group_order
FROM report_regression_metrics
ORDER BY metric_group_order, metric_name
;

-- dashboard_classifier_feature_importance
SELECT
  feature_name,
  importance
FROM report_classifier_feature_importance
ORDER BY importance DESC, feature_name
;
