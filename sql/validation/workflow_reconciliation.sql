-- ============================================================
-- Phase 11: Operational Workflow SQL Reconciliation Suite
-- MarketVoice SEA — Verification of Additive Workflow Objects
-- ============================================================

SET search_path TO marketvoice_warehouse;

-- 1. fact_review total count unchanged (MUST BE 46,007)
SELECT
    'fact_review_count' AS check_name,
    COUNT(*) AS actual_count,
    46007 AS expected_count,
    CASE WHEN COUNT(*) = 46007 THEN 'PASS' ELSE 'FAIL' END AS status
FROM fact_review;

-- 2. fact_review_issue total count unchanged (MUST BE 18,863)
SELECT
    'fact_review_issue_count' AS check_name,
    COUNT(*) AS actual_count,
    18863 AS expected_count,
    CASE WHEN COUNT(*) = 18863 THEN 'PASS' ELSE 'FAIL' END AS status
FROM fact_review_issue;

-- 3. fact_decision_queue count unchanged (MUST BE 5,090)
SELECT
    'fact_decision_queue_count' AS check_name,
    COUNT(*) AS actual_count,
    5090 AS expected_count,
    CASE WHEN COUNT(*) = 5090 THEN 'PASS' ELSE 'FAIL' END AS status
FROM fact_decision_queue;

-- 4. operational_event_log table exists and accessible
SELECT
    'operational_event_log_accessible' AS check_name,
    COUNT(*) AS actual_count,
    0 AS expected_count,
    'PASS' AS status
FROM operational_event_log;

-- 5. workflow_execution table exists and accessible
SELECT
    'workflow_execution_accessible' AS check_name,
    COUNT(*) AS actual_count,
    0 AS expected_count,
    'PASS' AS status
FROM workflow_execution;

-- 6. human_review_case table exists and accessible
SELECT
    'human_review_case_accessible' AS check_name,
    COUNT(*) AS actual_count,
    0 AS expected_count,
    'PASS' AS status
FROM human_review_case;

-- 7. human_review_outcome table exists and accessible
SELECT
    'human_review_outcome_accessible' AS check_name,
    COUNT(*) AS actual_count,
    0 AS expected_count,
    'PASS' AS status
FROM human_review_outcome;
