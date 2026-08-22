-- ============================================================
-- Phase 8: NLP Prediction Schema
-- MarketVoice SEA — Marketplace VoC Intelligence
--
-- Purpose: Store model predictions in the warehouse for
--          downstream BI consumption (Phase 9+).
--          These tables are ADDITIVE — they do NOT modify
--          any existing Phase 6/7 tables.
--
-- Governance:
--   - All predictions link back to fact_review via review_sk
--   - Source isolation preserved via source_sk
--   - Model provenance tracked via model_name + model_version
-- ============================================================

SET search_path TO marketvoice_warehouse;

-- -----------------------------------------------------------
-- Predicted rating classifications
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS pred_rating_classification (
    prediction_sk       SERIAL PRIMARY KEY,
    review_sk           INTEGER NOT NULL REFERENCES fact_review(review_sk),
    source_sk           INTEGER NOT NULL REFERENCES dim_source(source_sk),
    model_name          VARCHAR(200) NOT NULL,
    model_version       VARCHAR(50) NOT NULL,
    predicted_rating    SMALLINT NOT NULL CHECK (predicted_rating BETWEEN 1 AND 5),
    confidence_score    NUMERIC(6,4),
    prediction_date     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    pipeline_run_id     VARCHAR(100),
    UNIQUE (review_sk, model_name, model_version)
);

COMMENT ON TABLE pred_rating_classification IS
    'Phase 8: Predicted star-rating classifications from NLP models. '
    'Each row links to one fact_review and records the model provenance.';

-- -----------------------------------------------------------
-- Predicted sentiment labels (binary: Negative/Positive)
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS pred_sentiment (
    prediction_sk       SERIAL PRIMARY KEY,
    review_sk           INTEGER NOT NULL REFERENCES fact_review(review_sk),
    source_sk           INTEGER NOT NULL REFERENCES dim_source(source_sk),
    model_name          VARCHAR(200) NOT NULL,
    model_version       VARCHAR(50) NOT NULL,
    predicted_sentiment VARCHAR(20) NOT NULL,
    confidence_score    NUMERIC(6,4),
    prediction_date     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    pipeline_run_id     VARCHAR(100),
    UNIQUE (review_sk, model_name, model_version)
);

COMMENT ON TABLE pred_sentiment IS
    'Phase 8: Predicted binary sentiment labels (Negative/Positive). '
    'Gold labels exist only for Source A; predictions can cover all sources.';

-- -----------------------------------------------------------
-- Predicted emotion labels (5-class)
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS pred_emotion (
    prediction_sk       SERIAL PRIMARY KEY,
    review_sk           INTEGER NOT NULL REFERENCES fact_review(review_sk),
    source_sk           INTEGER NOT NULL REFERENCES dim_source(source_sk),
    model_name          VARCHAR(200) NOT NULL,
    model_version       VARCHAR(50) NOT NULL,
    predicted_emotion   VARCHAR(30) NOT NULL,
    confidence_score    NUMERIC(6,4),
    prediction_date     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    pipeline_run_id     VARCHAR(100),
    UNIQUE (review_sk, model_name, model_version)
);

COMMENT ON TABLE pred_emotion IS
    'Phase 8: Predicted emotion labels (Anger/Fear/Happy/Love/Sadness). '
    'Gold labels exist only for Source A; predictions can cover all sources.';

-- -----------------------------------------------------------
-- Candidate aspect/issue tags (unsupervised discovery)
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS pred_aspect_candidate (
    candidate_sk        SERIAL PRIMARY KEY,
    review_sk           INTEGER NOT NULL REFERENCES fact_review(review_sk),
    source_sk           INTEGER NOT NULL REFERENCES dim_source(source_sk),
    aspect_category     VARCHAR(100) NOT NULL,
    evidence_keyword    VARCHAR(200),
    discovery_method    VARCHAR(50) NOT NULL DEFAULT 'ngram_frequency',
    confidence_note     VARCHAR(200),
    created_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    pipeline_run_id     VARCHAR(100)
);

COMMENT ON TABLE pred_aspect_candidate IS
    'Phase 8: Candidate aspect/issue taxonomy tags from unsupervised discovery. '
    'Status = CANDIDATE_FOR_PHASE_9. Final taxonomy is Phase 9 scope.';

-- -----------------------------------------------------------
-- Model registry (lightweight metadata)
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS model_registry (
    registry_sk         SERIAL PRIMARY KEY,
    model_name          VARCHAR(200) NOT NULL,
    model_version       VARCHAR(50) NOT NULL,
    task                VARCHAR(100) NOT NULL,
    source_scope        VARCHAR(100) NOT NULL,
    selected_status     VARCHAR(30) NOT NULL DEFAULT 'candidate',
    macro_f1_val        NUMERIC(6,4),
    macro_f1_test       NUMERIC(6,4),
    accuracy_test       NUMERIC(6,4),
    qwk_test            NUMERIC(6,4),
    training_date       TIMESTAMPTZ,
    model_card_path     VARCHAR(500),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (model_name, model_version)
);

COMMENT ON TABLE model_registry IS
    'Phase 8: Lightweight model registry tracking all trained models, '
    'their evaluation metrics, and selection status.';
