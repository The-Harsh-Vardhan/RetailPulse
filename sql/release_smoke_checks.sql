-- RetailPulse release smoke checks
-- Target release surface: current internal pilot on Databricks Free Edition
-- Expected catalog/schema for the current workspace: workspace.retailpulse

USE CATALOG workspace;
USE SCHEMA retailpulse;

-- 1. Required report tables exist.
-- Pass condition: all expected table names are returned.
SELECT table_name
FROM information_schema.tables
WHERE table_catalog = current_catalog()
  AND table_schema = current_schema()
  AND table_name IN (
    'report_olap_cube',
    'report_olap_rollup',
    'report_olap_basket',
    'report_olap_validation',
    'report_classifier_metrics',
    'report_regression_metrics',
    'report_cluster_profiles',
    'report_cluster_k_scores',
    'report_classifier_feature_importance',
    'report_stream_validation',
    'report_optimize_summary',
    'report_optimize_timings'
  )
ORDER BY table_name;

-- 2. Required report tables are readable and non-empty.
-- Pass condition: every row_count is greater than zero.
SELECT 'report_classifier_feature_importance' AS table_name, COUNT(*) AS row_count FROM report_classifier_feature_importance
UNION ALL
SELECT 'report_classifier_metrics' AS table_name, COUNT(*) AS row_count FROM report_classifier_metrics
UNION ALL
SELECT 'report_cluster_k_scores' AS table_name, COUNT(*) AS row_count FROM report_cluster_k_scores
UNION ALL
SELECT 'report_cluster_profiles' AS table_name, COUNT(*) AS row_count FROM report_cluster_profiles
UNION ALL
SELECT 'report_olap_basket' AS table_name, COUNT(*) AS row_count FROM report_olap_basket
UNION ALL
SELECT 'report_olap_cube' AS table_name, COUNT(*) AS row_count FROM report_olap_cube
UNION ALL
SELECT 'report_olap_rollup' AS table_name, COUNT(*) AS row_count FROM report_olap_rollup
UNION ALL
SELECT 'report_olap_validation' AS table_name, COUNT(*) AS row_count FROM report_olap_validation
UNION ALL
SELECT 'report_optimize_summary' AS table_name, COUNT(*) AS row_count FROM report_optimize_summary
UNION ALL
SELECT 'report_optimize_timings' AS table_name, COUNT(*) AS row_count FROM report_optimize_timings
UNION ALL
SELECT 'report_regression_metrics' AS table_name, COUNT(*) AS row_count FROM report_regression_metrics
UNION ALL
SELECT 'report_stream_validation' AS table_name, COUNT(*) AS row_count FROM report_stream_validation
ORDER BY table_name;

-- 3. Association rules are present.
-- Pass condition: rule_count is greater than zero.
SELECT
  COUNT(*) AS rule_count,
  ROUND(MAX(lift), 4) AS max_lift,
  ROUND(MAX(confidence), 4) AS max_confidence
FROM mart_association_rules;

-- 4. Streaming validation is clean.
-- Pass condition: mismatch_groups = 0.
SELECT
  COUNT(*) AS checked_groups,
  SUM(CASE WHEN count_matches AND avg_basket_matches AND reordered_matches THEN 0 ELSE 1 END) AS mismatch_groups
FROM report_stream_validation;

-- 5. OLAP validation is clean.
-- Pass condition: mismatched_groups = 0 and max_item_gap = 0.
SELECT
  COUNT(*) AS checked_groups,
  SUM(CASE WHEN matches THEN 0 ELSE 1 END) AS mismatched_groups,
  MAX(ABS(total_items - manual_total_items)) AS max_item_gap
FROM report_olap_validation;

-- 6. Report-pack backing tables can be read directly.
-- Pass condition: each query returns rows without error.
SELECT * FROM report_classifier_metrics ORDER BY metric_name;
SELECT * FROM report_regression_metrics ORDER BY metric_name;
SELECT * FROM report_classifier_feature_importance ORDER BY importance DESC, feature_name;
SELECT * FROM report_cluster_profiles ORDER BY avg_total_orders DESC;
SELECT * FROM report_cluster_k_scores ORDER BY cluster_k;
SELECT * FROM report_optimize_summary ORDER BY query_name;
