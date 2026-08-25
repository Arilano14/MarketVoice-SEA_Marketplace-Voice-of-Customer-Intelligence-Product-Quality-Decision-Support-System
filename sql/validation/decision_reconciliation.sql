-- ============================================================
-- Phase 10: Decision Support SQL Reconciliation Suite
-- MarketVoice SEA — Priority Scoring & Queue Reconciliation
-- ============================================================

SET search_path TO marketvoice_warehouse;

-- 1. Fact review total count unchanged (MUST BE 46,007)
SELECT
    'fact_review_count' AS check_name,
    COUNT(*) AS actual_count,
    46007 AS expected_count,
    CASE WHEN COUNT(*) = 46007 THEN 'PASS' ELSE 'FAIL' END AS status
FROM fact_review;

-- 2. Fact review issue total count unchanged (MUST BE 18,863)
SELECT
    'fact_review_issue_count' AS check_name,
    COUNT(*) AS actual_count,
    18863 AS expected_count,
    CASE WHEN COUNT(*) = 18863 THEN 'PASS' ELSE 'FAIL' END AS status
FROM fact_review_issue;

-- 3. dim_priority_tier count (MUST BE 4)
SELECT
    'priority_tier_count' AS check_name,
    COUNT(*) AS actual_count,
    4 AS expected_count,
    CASE WHEN COUNT(*) = 4 THEN 'PASS' ELSE 'FAIL' END AS status
FROM dim_priority_tier;

-- 4. dim_reason_code count (MUST BE >= 6)
SELECT
    'reason_code_count' AS check_name,
    COUNT(*) AS actual_count,
    7 AS expected_count,
    CASE WHEN COUNT(*) >= 6 THEN 'PASS' ELSE 'FAIL' END AS status
FROM dim_reason_code;

-- 5. Zero orphan product_sk in fact_decision_queue
SELECT
    'orphan_decision_product_sk' AS check_name,
    COUNT(*) AS actual_count,
    0 AS expected_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM fact_decision_queue fdq
LEFT JOIN dim_product dp ON dp.product_sk = fdq.product_sk
WHERE fdq.product_sk IS NOT NULL AND dp.product_sk IS NULL;

-- 6. Zero orphan category_sk in fact_decision_queue
SELECT
    'orphan_decision_category_sk' AS check_name,
    COUNT(*) AS actual_count,
    0 AS expected_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM fact_decision_queue fdq
LEFT JOIN dim_category dc ON dc.category_sk = fdq.category_sk
WHERE fdq.category_sk IS NOT NULL AND dc.category_sk IS NULL;

-- 7. Zero orphan issue_id in fact_decision_queue
SELECT
    'orphan_decision_issue_id' AS check_name,
    COUNT(*) AS actual_count,
    0 AS expected_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM fact_decision_queue fdq
LEFT JOIN dim_issue di ON di.issue_id = fdq.issue_id
WHERE di.issue_id IS NULL;

-- 8. Score bounds check (ALL SCORES BETWEEN 0 AND 100)
SELECT
    'score_out_of_bounds_count' AS check_name,
    COUNT(*) AS actual_count,
    0 AS expected_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM fact_decision_queue
WHERE priority_score < 0.0 OR priority_score > 100.0;

-- 9. Reason codes populated for all P1 and P2 cases
SELECT
    'missing_reason_codes_p1_p2' AS check_name,
    COUNT(*) AS actual_count,
    0 AS expected_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM fact_decision_queue
WHERE tier_id IN (1, 2) AND (reason_codes IS NULL OR cardinality(reason_codes) = 0);

-- 10. Source isolation: Product grain has 0 Source A records
SELECT
    'product_grain_source_a_violations' AS check_name,
    COUNT(*) AS actual_count,
    0 AS expected_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM fact_decision_queue fdq
JOIN dim_source ds ON ds.source_sk = fdq.source_sk
WHERE fdq.grain_type = 'PRODUCT_X_ISSUE' AND ds.source_id != 'SRC_TOKOPEDIA_REVIEWS_2019';
