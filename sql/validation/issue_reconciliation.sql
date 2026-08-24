-- ============================================================
-- Phase 9: Issue Intelligence SQL Reconciliation Suite
-- MarketVoice SEA — Quality & Traceability Checks
-- ============================================================

SET search_path TO marketvoice_warehouse;

-- 1. Fact review total count unchanged (MUST BE 46,007)
SELECT
    'fact_review_count' AS check_name,
    COUNT(*) AS actual_count,
    46007 AS expected_count,
    CASE WHEN COUNT(*) = 46007 THEN 'PASS' ELSE 'FAIL' END AS status
FROM fact_review;

-- 2. Orphan check in fact_review_issue (MUST BE 0)
SELECT
    'orphan_review_sk' AS check_name,
    COUNT(*) AS actual_count,
    0 AS expected_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM fact_review_issue fri
LEFT JOIN fact_review fr ON fr.review_sk = fri.review_sk
WHERE fr.review_sk IS NULL;

-- 3. dim_issue active count (MUST BE 5)
SELECT
    'active_issue_categories' AS check_name,
    COUNT(*) AS actual_count,
    5 AS expected_count,
    CASE WHEN COUNT(*) = 5 THEN 'PASS' ELSE 'FAIL' END AS status
FROM dim_issue
WHERE status = 'ACTIVE';

-- 4. dim_severity level count (MUST BE 4)
SELECT
    'severity_level_count' AS check_name,
    COUNT(*) AS actual_count,
    4 AS expected_count,
    CASE WHEN COUNT(*) = 4 THEN 'PASS' ELSE 'FAIL' END AS status
FROM dim_severity;

-- 5. Cross-source isolation check (MUST BE 0)
SELECT
    'cross_source_violations' AS check_name,
    COUNT(*) AS actual_count,
    0 AS expected_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM fact_review_issue fri
JOIN fact_review fr ON fr.review_sk = fri.review_sk
WHERE fri.source_sk != fr.source_sk;

-- 6. Issue summary view reconciliation
SELECT
    'mv_issue_summary_rows' AS check_name,
    COUNT(*) AS actual_count,
    10 AS expected_count,
    CASE WHEN COUNT(*) = 10 THEN 'PASS' ELSE 'FAIL' END AS status
FROM mv_issue_summary;

-- 7. Product issue intelligence (Source B only check)
SELECT
    'product_issues_source_b_only' AS check_name,
    COUNT(DISTINCT fr.source_sk) AS source_count,
    1 AS expected_count,
    CASE WHEN COUNT(DISTINCT fr.source_sk) = 1 THEN 'PASS' ELSE 'FAIL' END AS status
FROM mv_issue_by_product mip
JOIN fact_review fr ON fr.product_sk = mip.product_sk;
