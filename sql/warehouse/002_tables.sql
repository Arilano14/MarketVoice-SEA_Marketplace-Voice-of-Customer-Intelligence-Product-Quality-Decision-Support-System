-- DEL-08 Physical DDL (Phase 6 v1.1)
-- 002_tables.sql
-- 9 physical tables only. No views, no dim_date, no Track B, no DEL-11 marts.
-- 3 audit (historical never truncate) + 2 conformed master dims (never truncate) + 3 dynamic analytical dims (truncated each run) + 1 central fact (truncated each run)

SET search_path TO marketvoice_warehouse;

-- ================================================================
-- A1. pipeline_run (HISTORICAL AUDIT — NEVER TRUNCATED)
-- ================================================================
CREATE TABLE IF NOT EXISTS pipeline_run (
    pipeline_run_id UUID PRIMARY KEY,
    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ NULL,
    status TEXT NOT NULL,
    pipeline_version TEXT NOT NULL,
    input_rows_total INTEGER NOT NULL DEFAULT 0,
    accepted_rows_total INTEGER NOT NULL DEFAULT 0,
    rejected_rows_total INTEGER NOT NULL DEFAULT 0,
    loaded_rows_total INTEGER NOT NULL DEFAULT 0,
    source_a_file_sha256 TEXT NOT NULL,
    source_b_file_sha256 TEXT NOT NULL,
    source_a_rows_manifest INTEGER NOT NULL,
    source_b_rows_manifest INTEGER NOT NULL,
    source_a_rows_read INTEGER NOT NULL DEFAULT 0,
    source_b_rows_read INTEGER NOT NULL DEFAULT 0,
    source_a_rows_loaded INTEGER NOT NULL DEFAULT 0,
    source_b_rows_loaded INTEGER NOT NULL DEFAULT 0,
    critical_dq_fails INTEGER NOT NULL DEFAULT 0,
    major_dq_fails INTEGER NOT NULL DEFAULT 0,
    notes TEXT NULL
);

-- ================================================================
-- A2. rejected_record_log (HISTORICAL AUDIT — NEVER TRUNCATED)
-- ================================================================
CREATE TABLE IF NOT EXISTS rejected_record_log (
    rejection_id SERIAL PRIMARY KEY,
    pipeline_run_id UUID NOT NULL,
    source_id TEXT NOT NULL,
    source_row_number INTEGER NOT NULL,
    source_native_row_hash TEXT NULL,
    stage TEXT NOT NULL,
    severity TEXT NOT NULL,
    dq_check_id TEXT NOT NULL,
    reason_code TEXT NOT NULL,
    reason_text TEXT NOT NULL,
    raw_row_snippet TEXT NULL,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ================================================================
-- A3. data_quality_result (REQUIRED GRAIN §25 — NEVER TRUNCATED)
-- Grain: one pipeline_run_id x one dq_check_id
-- ================================================================
CREATE TABLE IF NOT EXISTS data_quality_result (
    pipeline_run_id UUID NOT NULL,
    dq_check_id TEXT NOT NULL,
    severity TEXT NOT NULL,
    passed BOOLEAN NOT NULL,
    actual_value TEXT NULL,
    expected_value TEXT NULL,
    evidence TEXT NULL,
    measured_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (pipeline_run_id, dq_check_id)
);

-- ================================================================
-- D1. dim_source (CONFORMED MASTER DIM — NEVER TRUNCATED)
-- Resolve source_sk via: SELECT source_sk FROM dim_source WHERE source_id = %s
-- NEVER hardcode source_sk = 1 or 2.
-- ================================================================
CREATE TABLE IF NOT EXISTS dim_source (
    source_sk SMALLSERIAL PRIMARY KEY,
    source_id TEXT NOT NULL UNIQUE,
    source_display_name TEXT NOT NULL,
    source_license TEXT NOT NULL,
    source_doi_or_ref TEXT NULL,
    source_data_url TEXT NULL,
    source_file_sha256 TEXT NOT NULL,
    source_row_count_manifest INTEGER NOT NULL,
    source_column_count INTEGER NOT NULL,
    source_locale TEXT NOT NULL,
    registered_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ================================================================
-- D2. dim_rating (CONFORMED MASTER DIM — NEVER TRUNCATED)
-- 5 rows only. 1..5 rating_value.
-- ================================================================
CREATE TABLE IF NOT EXISTS dim_rating (
    rating_sk SMALLSERIAL PRIMARY KEY,
    rating_value SMALLINT NOT NULL UNIQUE,
    rating_label TEXT NOT NULL,
    rating_bucket TEXT NOT NULL
);

-- ================================================================
-- D3. dim_category (SOURCE-LOCAL DIM — TRUNCATED each TX-B run)
-- ================================================================
CREATE TABLE IF NOT EXISTS dim_category (
    category_sk SERIAL PRIMARY KEY,
    source_sk SMALLINT NOT NULL,
    source_native_category TEXT NOT NULL,
    category_value_count_observations INTEGER NOT NULL DEFAULT 0
);

-- ================================================================
-- D4. dim_product (SOURCE-LOCAL DIM — TRUNCATED each run; B-only MVP)
-- ================================================================
CREATE TABLE IF NOT EXISTS dim_product (
    product_sk SERIAL PRIMARY KEY,
    source_sk SMALLINT NOT NULL,
    source_native_product_id TEXT NOT NULL,
    source_native_product_name TEXT NULL,
    product_name_variant_count SMALLINT NOT NULL DEFAULT 1
);

-- ================================================================
-- D5. dim_shop (SOURCE-LOCAL DIM — TRUNCATED each run; B-only MVP)
-- ================================================================
CREATE TABLE IF NOT EXISTS dim_shop (
    shop_sk SERIAL PRIMARY KEY,
    source_sk SMALLINT NOT NULL,
    source_native_shop_id TEXT NOT NULL,
    shop_observation_count INTEGER NOT NULL DEFAULT 0
);

-- ================================================================
-- F1. fact_review (CENTRAL FACT — TRUNCATED each TX-B run)
-- ONE_FACT_ONE_GRAIN. UNEXPLAINED_WAREHOUSE_FIELDS = 0 (§28).
-- ================================================================
CREATE TABLE IF NOT EXISTS fact_review (
    review_sk BIGSERIAL PRIMARY KEY,
    source_sk SMALLINT NOT NULL,
    source_native_row_hash TEXT NOT NULL,
    source_row_number INTEGER NOT NULL,
    source_file_sha256 TEXT NOT NULL,
    rating_sk SMALLINT NOT NULL,
    rating_value SMALLINT NOT NULL,
    category_sk INTEGER NOT NULL,
    product_sk INTEGER NULL,
    shop_sk INTEGER NULL,
    review_text TEXT NOT NULL,
    review_text_len_chars INTEGER NOT NULL,
    source_gold_sentiment_label TEXT NULL,
    source_gold_emotion_label TEXT NULL,
    source_a_location_text TEXT NULL,
    source_a_product_name_text TEXT NULL,
    source_a_price_text TEXT NULL,
    source_a_overall_rating_text TEXT NULL,
    source_a_number_sold_text TEXT NULL,
    source_a_total_review_text TEXT NULL,
    source_b_product_name TEXT NULL,
    source_b_sold_raw_text TEXT NULL,
    source_b_product_url TEXT NULL,
    is_synthetic BOOLEAN NOT NULL DEFAULT FALSE,
    pipeline_run_id UUID NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL,
    processed_at TIMESTAMPTZ NOT NULL,
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
