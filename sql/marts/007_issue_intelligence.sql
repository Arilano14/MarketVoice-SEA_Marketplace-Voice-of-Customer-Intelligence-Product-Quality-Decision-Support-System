-- ============================================================
-- Phase 9: Issue Intelligence Schema
-- MarketVoice SEA — Product Quality & Issue Intelligence
--
-- Purpose: Store issue taxonomy, issue classifications, severity
--          assignments, and analytical views for issue intelligence.
--
-- Governance:
--   - ADDITIVE only — does NOT modify any Phase 6/7/8 tables.
--   - All issue assignments link to fact_review via review_sk.
--   - Source isolation preserved via source_sk.
--   - Taxonomy versioned via taxonomy_version.
--
-- Limitation:
--   - No temporal data exists; trend views use rating-segment
--     proxies, not time-based analysis.
--   - Severity is ANALYTICAL_PROTOTYPE (rule-based from rating).
-- ============================================================

SET search_path TO marketvoice_warehouse;

-- -----------------------------------------------------------
-- dim_issue — Issue taxonomy dimension
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_issue (
    issue_id            SMALLINT PRIMARY KEY,
    issue_name          VARCHAR(100) NOT NULL,
    issue_definition    TEXT NOT NULL,
    evidence_keywords   TEXT NOT NULL,
    in_scope            TEXT,
    non_examples        TEXT,
    ambiguity_rule      TEXT,
    taxonomy_version    VARCHAR(10) NOT NULL DEFAULT '1.0',
    created_phase       VARCHAR(20) NOT NULL DEFAULT 'Phase 9',
    status              VARCHAR(30) NOT NULL DEFAULT 'ACTIVE',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE dim_issue IS
    'Phase 9: Issue taxonomy dimension. Each row defines one validated '
    'issue category with evidence keywords and disambiguation rules. '
    'Taxonomy version is frozen at 1.0.';

-- -----------------------------------------------------------
-- dim_severity — Severity level dimension
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_severity (
    severity_id         SMALLINT PRIMARY KEY,
    severity_name       VARCHAR(20) NOT NULL,
    severity_definition TEXT NOT NULL,
    rating_range        VARCHAR(20) NOT NULL,
    status_note         VARCHAR(50) NOT NULL DEFAULT 'ANALYTICAL_PROTOTYPE',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE dim_severity IS
    'Phase 9: Severity level dimension. Severity is mapped from '
    'star rating: CRITICAL (1), HIGH (2), MODERATE (3), LOW (4-5). '
    'Status = ANALYTICAL_PROTOTYPE (rule-based, not independently validated).';

-- -----------------------------------------------------------
-- fact_review_issue — Multi-label issue assignment fact table
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS fact_review_issue (
    assignment_sk       SERIAL PRIMARY KEY,
    review_sk           INTEGER NOT NULL REFERENCES fact_review(review_sk),
    source_sk           INTEGER NOT NULL REFERENCES dim_source(source_sk),
    issue_id            SMALLINT NOT NULL REFERENCES dim_issue(issue_id),
    severity_id         SMALLINT NOT NULL REFERENCES dim_severity(severity_id),
    matched_keywords    TEXT,
    keyword_count       SMALLINT NOT NULL DEFAULT 0,
    confidence          NUMERIC(5,4) NOT NULL DEFAULT 0,
    model_version       VARCHAR(50) NOT NULL,
    classification_method VARCHAR(30) NOT NULL DEFAULT 'keyword_match',
    taxonomy_version    VARCHAR(10) NOT NULL DEFAULT '1.0',
    pipeline_run_id     VARCHAR(100),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE fact_review_issue IS
    'Phase 9: Multi-label issue assignment fact table. Each row links '
    'one review (review_sk) to one issue category (issue_id) with '
    'severity, confidence, and traceability metadata. A review may '
    'have multiple issue assignments (multi-label).';

CREATE INDEX IF NOT EXISTS idx_fri_review_sk ON fact_review_issue(review_sk);
CREATE INDEX IF NOT EXISTS idx_fri_issue_id ON fact_review_issue(issue_id);
CREATE INDEX IF NOT EXISTS idx_fri_severity_id ON fact_review_issue(severity_id);
CREATE INDEX IF NOT EXISTS idx_fri_source_sk ON fact_review_issue(source_sk);

-- -----------------------------------------------------------
-- Seed dim_severity (4 levels)
-- -----------------------------------------------------------
INSERT INTO dim_severity (severity_id, severity_name, severity_definition, rating_range, status_note)
VALUES
    (1, 'CRITICAL', 'Rating 1 + issue detected. Strongest negative signal.', '1', 'ANALYTICAL_PROTOTYPE'),
    (2, 'HIGH', 'Rating 2 + issue detected. Significant dissatisfaction.', '2', 'ANALYTICAL_PROTOTYPE'),
    (3, 'MODERATE', 'Rating 3 + issue detected. Mixed experience.', '3', 'ANALYTICAL_PROTOTYPE'),
    (4, 'LOW', 'Rating 4-5 + issue detected. Positive review mentioning issue.', '4-5', 'ANALYTICAL_PROTOTYPE')
ON CONFLICT (severity_id) DO NOTHING;

-- -----------------------------------------------------------
-- Analytical Views
-- -----------------------------------------------------------

-- mv_issue_summary: One row per (source, issue) with frequency/rate metrics
CREATE OR REPLACE VIEW mv_issue_summary AS
SELECT
    ds.source_id,
    di.issue_id,
    di.issue_name,
    COUNT(DISTINCT fri.review_sk) AS issue_volume,
    ROUND(100.0 * COUNT(DISTINCT fri.review_sk) /
        NULLIF((SELECT COUNT(*) FROM fact_review fr2 WHERE fr2.source_sk = fri.source_sk), 0), 4)
        AS issue_rate_pct,
    COUNT(DISTINCT CASE WHEN fr.rating_value <= 2 THEN fri.review_sk END) AS negative_volume,
    COUNT(DISTINCT CASE WHEN dsev.severity_name = 'CRITICAL' THEN fri.review_sk END) AS critical_volume,
    COUNT(DISTINCT CASE WHEN dsev.severity_name = 'HIGH' THEN fri.review_sk END) AS high_volume,
    ROUND(AVG(fri.confidence), 4) AS mean_confidence,
    fri.taxonomy_version
FROM fact_review_issue fri
JOIN fact_review fr ON fr.review_sk = fri.review_sk
JOIN dim_source ds ON ds.source_sk = fri.source_sk
JOIN dim_issue di ON di.issue_id = fri.issue_id
JOIN dim_severity dsev ON dsev.severity_id = fri.severity_id
GROUP BY ds.source_id, di.issue_id, di.issue_name, fri.source_sk, fri.taxonomy_version
ORDER BY ds.source_id, issue_volume DESC;

COMMENT ON VIEW mv_issue_summary IS
    'Phase 9: Issue frequency and rate summary per source and issue category. '
    'Denominator = total reviews for that source. '
    'Limitation: No temporal trend — snapshot aggregate only.';

-- mv_issue_by_category: One row per (source, category, issue)
CREATE OR REPLACE VIEW mv_issue_by_category AS
SELECT
    ds.source_id,
    dc.category_sk,
    dc.source_native_category AS category_name,
    di.issue_id,
    di.issue_name,
    COUNT(DISTINCT fri.review_sk) AS issue_volume,
    (SELECT COUNT(*) FROM fact_review fr2
     WHERE fr2.source_sk = fri.source_sk AND fr2.category_sk = dc.category_sk) AS category_review_count,
    ROUND(100.0 * COUNT(DISTINCT fri.review_sk) /
        NULLIF((SELECT COUNT(*) FROM fact_review fr2
                WHERE fr2.source_sk = fri.source_sk AND fr2.category_sk = dc.category_sk), 0), 4)
        AS category_issue_rate_pct,
    COUNT(DISTINCT CASE WHEN fr.rating_value <= 2 THEN fri.review_sk END) AS negative_volume
FROM fact_review_issue fri
JOIN fact_review fr ON fr.review_sk = fri.review_sk
JOIN dim_source ds ON ds.source_sk = fri.source_sk
JOIN dim_category dc ON dc.category_sk = fr.category_sk
JOIN dim_issue di ON di.issue_id = fri.issue_id
GROUP BY ds.source_id, dc.category_sk, dc.source_native_category, di.issue_id, di.issue_name, fri.source_sk
ORDER BY ds.source_id, dc.source_native_category, issue_volume DESC;

COMMENT ON VIEW mv_issue_by_category IS
    'Phase 9: Issue distribution per category. Category-level issue rate = '
    'issue_volume / category_review_count. '
    'Available for both Source A (29 categories) and Source B (5 categories).';

-- mv_issue_by_product: One row per (product, issue) — Source B only
CREATE OR REPLACE VIEW mv_issue_by_product AS
SELECT
    dp.product_sk,
    dp.source_native_product_name AS product_name,
    di.issue_id,
    di.issue_name,
    COUNT(DISTINCT fri.review_sk) AS issue_volume,
    (SELECT COUNT(*) FROM fact_review fr2 WHERE fr2.product_sk = dp.product_sk) AS product_review_count,
    ROUND(100.0 * COUNT(DISTINCT fri.review_sk) /
        NULLIF((SELECT COUNT(*) FROM fact_review fr2 WHERE fr2.product_sk = dp.product_sk), 0), 4)
        AS product_issue_rate_pct,
    COUNT(DISTINCT CASE WHEN fr.rating_value <= 2 THEN fri.review_sk END) AS negative_volume,
    ROUND(AVG(fr.rating_value)::numeric, 2) AS product_avg_rating
FROM fact_review_issue fri
JOIN fact_review fr ON fr.review_sk = fri.review_sk
JOIN dim_product dp ON dp.product_sk = fr.product_sk
JOIN dim_issue di ON di.issue_id = fri.issue_id
WHERE fr.product_sk IS NOT NULL AND fr.product_sk != 0
GROUP BY dp.product_sk, dp.source_native_product_name, di.issue_id, di.issue_name
ORDER BY issue_volume DESC;

COMMENT ON VIEW mv_issue_by_product IS
    'Phase 9: Product-level issue intelligence. Source B only. '
    'Source A has no product_sk and is excluded. '
    'Limitation: Product identity is Source B native ID only.';

-- mv_issue_low_rating_overrepresentation: Statistical overrepresentation analysis
-- NOTE: This view computes segment-based overrepresentation in low-rating reviews (<= 2 stars).
-- FORMAL NOMENCLATURE: Customer Dissatisfaction Driver Analysis (NOT a temporal trend).
-- TEMPORAL_EMERGING_ISSUE_ANALYSIS = DEFERRED_TO_FUTURE_DATASET_VERSION (NO_TEMPORAL_DATA).
CREATE OR REPLACE VIEW mv_issue_low_rating_overrepresentation AS
WITH issue_stats AS (
    SELECT
        fri.source_sk,
        ds.source_id,
        fri.issue_id,
        di.issue_name,
        COUNT(DISTINCT fri.review_sk) AS total_issue_count,
        COUNT(DISTINCT CASE WHEN fr.rating_value <= 2 THEN fri.review_sk END) AS neg_issue_count,
        (SELECT COUNT(*) FROM fact_review fr2 WHERE fr2.source_sk = fri.source_sk) AS total_reviews,
        (SELECT COUNT(*) FROM fact_review fr2
         WHERE fr2.source_sk = fri.source_sk AND fr2.rating_value <= 2) AS total_neg_reviews
    FROM fact_review_issue fri
    JOIN fact_review fr ON fr.review_sk = fri.review_sk
    JOIN dim_source ds ON ds.source_sk = fri.source_sk
    JOIN dim_issue di ON di.issue_id = fri.issue_id
    GROUP BY fri.source_sk, ds.source_id, fri.issue_id, di.issue_name
)
SELECT
    source_id,
    issue_id,
    issue_name,
    'rating_le_2' AS segment,
    neg_issue_count AS low_rating_issue_count,
    total_neg_reviews AS low_rating_total_reviews,
    ROUND(neg_issue_count::numeric / NULLIF(total_neg_reviews, 0), 6) AS low_rating_issue_rate,
    total_issue_count AS baseline_issue_count,
    total_reviews AS baseline_total_reviews,
    ROUND(total_issue_count::numeric / NULLIF(total_reviews, 0), 6) AS baseline_issue_rate,
    CASE WHEN total_issue_count > 0
         THEN ROUND((neg_issue_count::numeric / NULLIF(total_neg_reviews, 0)) /
                     (total_issue_count::numeric / NULLIF(total_reviews, 0)), 4)
         ELSE 0 END AS dissatisfaction_rate_ratio,
    neg_issue_count >= 30 AS min_support_met,
    'LOW_RATING_OVERREPRESENTATION' AS analysis_type,
    'TEMPORAL_EMERGING_ISSUE_ANALYSIS = DEFERRED (NO_TEMPORAL_DATA)' AS data_limitation
FROM issue_stats
ORDER BY source_id, neg_issue_count DESC;

COMMENT ON VIEW mv_issue_low_rating_overrepresentation IS
    'Phase 9 Remediation: Low-rating issue overrepresentation analysis (Dissatisfaction Driver). '
    'CRITICAL METHODOLOGICAL DISTINCTION: No temporal data exists. This view measures '
    'statistical concentration in low-rating reviews (<= 2 stars) relative to baseline corpus. '
    'TEMPORAL_EMERGING_ISSUE_ANALYSIS is formally DEFERRED.';

-- Backwards compatibility alias view for legacy references
CREATE OR REPLACE VIEW mv_issue_emerging AS
SELECT * FROM mv_issue_low_rating_overrepresentation;

COMMENT ON VIEW mv_issue_emerging IS
    'DEPRECATED ALIAS: Use mv_issue_low_rating_overrepresentation directly.';
