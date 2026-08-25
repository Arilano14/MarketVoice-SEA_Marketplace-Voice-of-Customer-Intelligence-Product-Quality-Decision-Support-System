-- ============================================================
-- Phase 10: Decision Support System (DSS) Schema
-- MarketVoice SEA — Priority Case Scoring & Decision Support
--
-- Governance:
--   - ADDITIVE only — zero modification to Phase 6-9 tables.
--   - Decision queue links to dim_source, dim_product, dim_category, dim_issue.
--   - Grains are explicitly isolated:
--       * PRODUCT_X_ISSUE (Source B only)
--       * CATEGORY_X_ISSUE (Source A & B)
--       * SOURCE_X_ISSUE (Global portfolio)
--   - Traceable to underlying issue and review facts.
-- ============================================================

SET search_path TO marketvoice_warehouse;

-- -----------------------------------------------------------
-- 1. dim_priority_tier — Decision priority classification
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_priority_tier (
    tier_id             SMALLINT PRIMARY KEY,
    tier_code           VARCHAR(30) NOT NULL UNIQUE,
    tier_name           VARCHAR(80) NOT NULL,
    score_min           NUMERIC(5,2) NOT NULL,
    score_max           NUMERIC(5,2) NOT NULL,
    guidance_recommendation TEXT NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE dim_priority_tier IS
    'Phase 10: Priority tiers for decision support queue. '
    'P1 (Immediate Review), P2 (Near-Term Review), P3 (Monitoring), P4 (Informational). '
    'Guidance is analytical recommendation only, not operational SLA.';

INSERT INTO dim_priority_tier
    (tier_id, tier_code, tier_name, score_min, score_max, guidance_recommendation)
VALUES
    (1, 'P1_CRITICAL', 'Immediate Human Review Recommendation', 70.00, 100.00,
     'High-severity, chronic customer defect; prioritize for root-cause analysis.'),
    (2, 'P2_HIGH_PRIORITY', 'Near-Term Review Recommendation', 50.00, 69.99,
     'Substantial dissatisfaction or recurring issue; investigate quality drivers.'),
    (3, 'P3_MONITORING', 'Quality Monitoring Recommendation', 30.00, 49.99,
     'Moderate risk; monitor for recurrence or low-rating escalation.'),
    (4, 'P4_INFORMATIONAL', 'Informational Logging', 0.00, 29.99,
     'Low severity or baseline incidental feedback; standard automated logging.')
ON CONFLICT (tier_id) DO UPDATE SET
    tier_code = EXCLUDED.tier_code,
    tier_name = EXCLUDED.tier_name,
    score_min = EXCLUDED.score_min,
    score_max = EXCLUDED.score_max,
    guidance_recommendation = EXCLUDED.guidance_recommendation;


-- -----------------------------------------------------------
-- 2. dim_reason_code — Standardized explanation catalog
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_reason_code (
    reason_code         VARCHAR(50) PRIMARY KEY,
    reason_title        VARCHAR(100) NOT NULL,
    trigger_condition   TEXT NOT NULL,
    dimension_category  VARCHAR(50) NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE dim_reason_code IS
    'Phase 10: Standardized reason code registry for decision explainability.';

INSERT INTO dim_reason_code
    (reason_code, reason_title, trigger_condition, dimension_category)
VALUES
    ('RC_CRITICAL_SEVERITY_DOMINANCE', 'Critical Severity Dominance',
     'Critical/High severity proxy ratio >= 0.50', 'Severity Impact'),
    ('RC_HIGH_DISSATISFACTION_DRIVER', 'High Dissatisfaction Driver',
     'Dissatisfaction rate ratio >= 2.0x or z-score >= 2.0', 'Dissatisfaction Overrepresentation'),
    ('RC_CHRONIC_EVENT_RECURRENCE', 'Chronic Review-Event Recurrence',
     'Distinct review event recurrence count >= 5', 'Recurrence Intensity'),
    ('RC_BROAD_EVIDENCE_SUPPORT', 'Broad Evidence Support',
     'Total issue facts >= 50 reviews', 'Evidence Volume'),
    ('RC_HIGH_CONFIDENCE_SIGNAL', 'High Classification Confidence',
     'Mean NLP classification confidence >= 0.70', 'Classification Quality'),
    ('RC_SMALL_SAMPLE_CAUTION', 'Small Sample Caution Flag',
     'Total issue facts < 5 reviews', 'Sample Caution'),
    ('RC_BASELINE_MONITORING', 'Baseline Monitoring',
     'Standard baseline distribution without critical escalation', 'Baseline')
ON CONFLICT (reason_code) DO UPDATE SET
    reason_title = EXCLUDED.reason_title,
    trigger_condition = EXCLUDED.trigger_condition,
    dimension_category = EXCLUDED.dimension_category;


-- -----------------------------------------------------------
-- 3. fact_decision_queue — Primary Decision Support Table
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS fact_decision_queue (
    decision_sk             SERIAL PRIMARY KEY,
    source_sk               INTEGER NOT NULL REFERENCES dim_source(source_sk),
    grain_type              VARCHAR(30) NOT NULL,
    product_sk              INTEGER REFERENCES dim_product(product_sk),
    category_sk             INTEGER REFERENCES dim_category(category_sk),
    issue_id                SMALLINT NOT NULL REFERENCES dim_issue(issue_id),
    priority_score          NUMERIC(5,2) NOT NULL CHECK (priority_score BETWEEN 0 AND 100),
    tier_id                 SMALLINT NOT NULL REFERENCES dim_priority_tier(tier_id),
    severity_impact_score   NUMERIC(5,2) NOT NULL,
    dissatisfaction_score   NUMERIC(5,2) NOT NULL,
    recurrence_score        NUMERIC(5,2) NOT NULL,
    volume_score            NUMERIC(5,2) NOT NULL,
    confidence_score        NUMERIC(5,2) NOT NULL,
    evidence_support        INTEGER NOT NULL,
    distinct_review_events  INTEGER NOT NULL,
    critical_severity_count INTEGER NOT NULL,
    reason_codes            TEXT[] NOT NULL,
    calculation_version     VARCHAR(20) NOT NULL DEFAULT '1.0',
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_decision_grain_tier
    ON fact_decision_queue (grain_type, tier_id, priority_score DESC);

CREATE INDEX IF NOT EXISTS idx_decision_product
    ON fact_decision_queue (product_sk, issue_id) WHERE product_sk IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_decision_category
    ON fact_decision_queue (category_sk, issue_id) WHERE category_sk IS NOT NULL;

COMMENT ON TABLE fact_decision_queue IS
    'Phase 10: Decision support action queue across isolated grains. '
    'Contains explainable priority scores, sub-scores, and deterministic reason codes.';


-- -----------------------------------------------------------
-- 4. Analytical Mart Views
-- -----------------------------------------------------------

-- View: mv_priority_product_queue (Grain A: Product x Issue, Source B)
CREATE OR REPLACE VIEW mv_priority_product_queue AS
SELECT
    fdq.decision_sk,
    dp.product_sk,
    dp.source_native_product_id AS product_id,
    dp.source_native_product_name AS product_name,
    di.issue_id,
    di.issue_name,
    fdq.priority_score,
    dpt.tier_code AS priority_tier,
    dpt.guidance_recommendation,
    fdq.severity_impact_score,
    fdq.dissatisfaction_score,
    fdq.recurrence_score,
    fdq.volume_score,
    fdq.confidence_score,
    fdq.evidence_support,
    fdq.distinct_review_events,
    fdq.critical_severity_count,
    fdq.reason_codes,
    fdq.created_at
FROM fact_decision_queue fdq
JOIN dim_product dp ON dp.product_sk = fdq.product_sk
JOIN dim_issue di ON di.issue_id = fdq.issue_id
JOIN dim_priority_tier dpt ON dpt.tier_id = fdq.tier_id
WHERE fdq.grain_type = 'PRODUCT_X_ISSUE'
ORDER BY fdq.priority_score DESC;

COMMENT ON VIEW mv_priority_product_queue IS
    'Phase 10: Ranked operational decision queue for Source B products.';


-- View: mv_priority_category_queue (Grain B: Source x Category x Issue)
CREATE OR REPLACE VIEW mv_priority_category_queue AS
SELECT
    fdq.decision_sk,
    ds.source_id,
    dc.category_sk,
    dc.source_native_category AS category_name,
    di.issue_id,
    di.issue_name,
    fdq.priority_score,
    dpt.tier_code AS priority_tier,
    dpt.guidance_recommendation,
    fdq.severity_impact_score,
    fdq.dissatisfaction_score,
    fdq.recurrence_score,
    fdq.volume_score,
    fdq.confidence_score,
    fdq.evidence_support,
    fdq.distinct_review_events,
    fdq.reason_codes,
    fdq.created_at
FROM fact_decision_queue fdq
JOIN dim_source ds ON ds.source_sk = fdq.source_sk
JOIN dim_category dc ON dc.category_sk = fdq.category_sk
JOIN dim_issue di ON di.issue_id = fdq.issue_id
JOIN dim_priority_tier dpt ON dpt.tier_id = fdq.tier_id
WHERE fdq.grain_type = 'CATEGORY_X_ISSUE'
ORDER BY ds.source_id, fdq.priority_score DESC;

COMMENT ON VIEW mv_priority_category_queue IS
    'Phase 10: Source-aware ranked queue for category issues across Source A and B.';


-- View: mv_product_risk_index (Rollup at Product Level, Source B)
CREATE OR REPLACE VIEW mv_product_risk_index AS
SELECT
    dp.product_sk,
    dp.source_native_product_id AS product_id,
    dp.source_native_product_name AS product_name,
    COUNT(fdq.decision_sk) AS total_issue_types,
    ROUND(MAX(fdq.priority_score), 2) AS max_priority_score,
    ROUND(AVG(fdq.priority_score)::numeric, 2) AS avg_priority_score,
    SUM(fdq.evidence_support) AS total_issue_volume,
    SUM(fdq.critical_severity_count) AS total_critical_volume,
    COUNT(CASE WHEN fdq.tier_id = 1 THEN 1 END) AS p1_critical_issues_count,
    COUNT(CASE WHEN fdq.tier_id = 2 THEN 1 END) AS p2_high_issues_count
FROM fact_decision_queue fdq
JOIN dim_product dp ON dp.product_sk = fdq.product_sk
WHERE fdq.grain_type = 'PRODUCT_X_ISSUE'
GROUP BY dp.product_sk, dp.source_native_product_id, dp.source_native_product_name
ORDER BY max_priority_score DESC, total_issue_volume DESC;

COMMENT ON VIEW mv_product_risk_index IS
    'Phase 10: Product-level multi-issue risk rollup for Source B catalog.';
