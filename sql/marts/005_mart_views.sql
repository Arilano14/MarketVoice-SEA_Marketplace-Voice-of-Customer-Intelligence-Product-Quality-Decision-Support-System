-- ==============================================================================
-- MARKETVOICE SEA — DEL-11 BASELINE BUSINESS INTELLIGENCE MARTS
-- Script: 005_mart_views.sql
-- Description: Core analytical summary marts (PostgreSQL Views) for Baseline BI.
-- Schema: marketvoice_warehouse
-- Target Phase: Phase 7 (Baseline Business Intelligence)
-- Deliverable: DEL-11
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- VIEW 1: mv_source_summary
-- Grain: One row per registered source
-- Scope: FR-003, UC-001, Integration Contract 1
-- Limitation: This output reflects review text and ratings as provided by the
-- source. It does not imply temporal trend, seller performance, product quality,
-- or decision priority. Source A and Source B are analyzed independently.
-- ------------------------------------------------------------------------------
CREATE OR REPLACE VIEW marketvoice_warehouse.mv_source_summary AS
SELECT
    ds.source_id,
    ds.source_display_name,
    COUNT(fr.review_sk)::integer AS review_count,
    ROUND(AVG(fr.rating_value)::numeric, 2) AS avg_rating,
    COUNT(fr.review_sk) FILTER (WHERE fr.rating_value = 1)::integer AS rating_1_count,
    COUNT(fr.review_sk) FILTER (WHERE fr.rating_value = 2)::integer AS rating_2_count,
    COUNT(fr.review_sk) FILTER (WHERE fr.rating_value = 3)::integer AS rating_3_count,
    COUNT(fr.review_sk) FILTER (WHERE fr.rating_value = 4)::integer AS rating_4_count,
    COUNT(fr.review_sk) FILTER (WHERE fr.rating_value = 5)::integer AS rating_5_count,
    ROUND(
        (COUNT(fr.review_sk) FILTER (WHERE fr.rating_value <= 2)::numeric / NULLIF(COUNT(fr.review_sk), 0)::numeric) * 100.0,
        2
    ) AS negative_pct,
    ROUND(
        (COUNT(fr.review_sk) FILTER (WHERE fr.rating_value = 3)::numeric / NULLIF(COUNT(fr.review_sk), 0)::numeric) * 100.0,
        2
    ) AS neutral_pct,
    ROUND(
        (COUNT(fr.review_sk) FILTER (WHERE fr.rating_value >= 4)::numeric / NULLIF(COUNT(fr.review_sk), 0)::numeric) * 100.0,
        2
    ) AS positive_pct,
    ROUND(AVG(fr.review_text_len_chars)::numeric, 0)::integer AS avg_review_text_len,
    COUNT(DISTINCT fr.category_sk)::integer AS category_count
FROM marketvoice_warehouse.dim_source ds
JOIN marketvoice_warehouse.fact_review fr ON ds.source_sk = fr.source_sk
WHERE fr.is_synthetic = FALSE
GROUP BY ds.source_sk, ds.source_id, ds.source_display_name;


-- ------------------------------------------------------------------------------
-- VIEW 2: mv_category_summary
-- Grain: One row per source and category
-- Scope: FR-003, UC-001, Integration Contract 1
-- Limitation: Results distinguish sources and do not produce temporal analyses.
-- Categories are source-native and not cross-source reconciled.
-- ------------------------------------------------------------------------------
CREATE OR REPLACE VIEW marketvoice_warehouse.mv_category_summary AS
SELECT
    ds.source_id,
    dc.source_native_category AS category,
    COUNT(fr.review_sk)::integer AS review_count,
    ROUND(AVG(fr.rating_value)::numeric, 2) AS avg_rating,
    COUNT(fr.review_sk) FILTER (WHERE fr.rating_value = 1)::integer AS rating_1_count,
    COUNT(fr.review_sk) FILTER (WHERE fr.rating_value = 2)::integer AS rating_2_count,
    COUNT(fr.review_sk) FILTER (WHERE fr.rating_value = 3)::integer AS rating_3_count,
    COUNT(fr.review_sk) FILTER (WHERE fr.rating_value = 4)::integer AS rating_4_count,
    COUNT(fr.review_sk) FILTER (WHERE fr.rating_value = 5)::integer AS rating_5_count,
    ROUND(
        (COUNT(fr.review_sk) FILTER (WHERE fr.rating_value <= 2)::numeric / NULLIF(COUNT(fr.review_sk), 0)::numeric) * 100.0,
        2
    ) AS negative_pct,
    ROUND(
        (COUNT(fr.review_sk) FILTER (WHERE fr.rating_value = 3)::numeric / NULLIF(COUNT(fr.review_sk), 0)::numeric) * 100.0,
        2
    ) AS neutral_pct,
    ROUND(
        (COUNT(fr.review_sk) FILTER (WHERE fr.rating_value >= 4)::numeric / NULLIF(COUNT(fr.review_sk), 0)::numeric) * 100.0,
        2
    ) AS positive_pct,
    ROUND(AVG(fr.review_text_len_chars)::numeric, 0)::integer AS avg_review_text_len
FROM marketvoice_warehouse.dim_category dc
JOIN marketvoice_warehouse.dim_source ds ON dc.source_sk = ds.source_sk
JOIN marketvoice_warehouse.fact_review fr ON dc.category_sk = fr.category_sk
WHERE fr.is_synthetic = FALSE
GROUP BY ds.source_id, dc.category_sk, dc.source_native_category;


-- ------------------------------------------------------------------------------
-- VIEW 3: mv_product_summary
-- Grain: One row per Source B product listing
-- Scope: FR-005, UC-002, Integration Contract 2
-- Limitation: This output describes review signals for identified Source B
-- products. It does not imply causation, seller responsibility, product defect
-- confirmation, or enforcement action. Source A products are not included.
-- No temporal trend or market-wide comparison is supported.
-- ------------------------------------------------------------------------------
CREATE OR REPLACE VIEW marketvoice_warehouse.mv_product_summary AS
SELECT
    ds.source_id,
    dp.source_native_product_id AS product_id,
    dp.source_native_product_name AS product_name,
    dp.product_name_variant_count,
    MAX(dc.source_native_category) AS category,
    COUNT(fr.review_sk)::integer AS review_count,
    ROUND(AVG(fr.rating_value)::numeric, 2) AS avg_rating,
    COUNT(fr.review_sk) FILTER (WHERE fr.rating_value <= 2)::integer AS low_rating_count,
    ROUND(
        (COUNT(fr.review_sk) FILTER (WHERE fr.rating_value <= 2)::numeric / NULLIF(COUNT(fr.review_sk), 0)::numeric) * 100.0,
        2
    ) AS low_rating_pct,
    COUNT(fr.review_sk) FILTER (WHERE fr.rating_value >= 4)::integer AS high_rating_count,
    ROUND(AVG(fr.review_text_len_chars)::numeric, 0)::integer AS avg_review_text_len
FROM marketvoice_warehouse.dim_product dp
JOIN marketvoice_warehouse.dim_source ds ON dp.source_sk = ds.source_sk
JOIN marketvoice_warehouse.fact_review fr ON dp.product_sk = fr.product_sk
LEFT JOIN marketvoice_warehouse.dim_category dc ON fr.category_sk = dc.category_sk
WHERE ds.source_id = 'SRC_TOKOPEDIA_REVIEWS_2019'
  AND fr.is_synthetic = FALSE
GROUP BY ds.source_id, dp.product_sk, dp.source_native_product_id, dp.source_native_product_name, dp.product_name_variant_count;


-- ------------------------------------------------------------------------------
-- VIEW 4: mv_shop_summary
-- Grain: One row per Source B shop
-- Scope: FR-006, UC-003, Integration Contract 3
-- Limitation: This output describes review experience indicators for identified
-- Source B shops based on customer-provided reviews. It does not characterize seller
-- performance, seller capability, enforcement status, or seller reputation.
-- It is review-supplied-rating feedback only. No time trend, seller behavior
-- assessment, or automated seller action is implied or supported. It is Source B only.
-- ------------------------------------------------------------------------------
CREATE OR REPLACE VIEW marketvoice_warehouse.mv_shop_summary AS
SELECT
    ds.source_id,
    dsh.source_native_shop_id AS shop_id,
    COUNT(fr.review_sk)::integer AS review_count,
    ROUND(AVG(fr.rating_value)::numeric, 2) AS avg_rating,
    ROUND(
        (COUNT(fr.review_sk) FILTER (WHERE fr.rating_value <= 2)::numeric / NULLIF(COUNT(fr.review_sk), 0)::numeric) * 100.0,
        2
    ) AS low_rating_pct,
    COUNT(DISTINCT fr.product_sk)::integer AS product_count,
    ROUND(AVG(fr.review_text_len_chars)::numeric, 0)::integer AS avg_review_text_len
FROM marketvoice_warehouse.dim_shop dsh
JOIN marketvoice_warehouse.dim_source ds ON dsh.source_sk = ds.source_sk
JOIN marketvoice_warehouse.fact_review fr ON dsh.shop_sk = fr.shop_sk
WHERE ds.source_id = 'SRC_TOKOPEDIA_REVIEWS_2019'
  AND fr.is_synthetic = FALSE
GROUP BY ds.source_id, dsh.shop_sk, dsh.source_native_shop_id;


-- ------------------------------------------------------------------------------
-- VIEW 5: mv_source_a_label_breakdown
-- Grain: One row per (sentiment_label, emotion_label) pair
-- Scope: FR-004 baseline exploration, Integration Contract 4 prep
-- Limitation: This output presents the sentiment and emotion labels as provided
-- by Source A (PRDECT-ID dataset), the sole gold-label benchmark for these attributes
-- in MarketVoice SEA. Labels are not predictions; they are source-supplied annotations.
-- Labels and ratings describe customer-provided review text. They do not characterize
-- product quality or seller performance. Source A baseline is used for Phase 8 model
-- evaluation only; Source B reviews are not labeled with Source A labels.
-- ------------------------------------------------------------------------------
CREATE OR REPLACE VIEW marketvoice_warehouse.mv_source_a_label_breakdown AS
SELECT
    ds.source_id,
    fr.source_gold_sentiment_label AS sentiment_label,
    fr.source_gold_emotion_label AS emotion_label,
    COUNT(fr.review_sk)::integer AS review_count,
    ROUND(AVG(fr.rating_value)::numeric, 2) AS avg_rating,
    ROUND(
        (COUNT(fr.review_sk)::numeric / 5400.0) * 100.0,
        2
    ) AS pct_of_source
FROM marketvoice_warehouse.fact_review fr
JOIN marketvoice_warehouse.dim_source ds ON fr.source_sk = ds.source_sk
WHERE ds.source_id = 'SRC_PRDECT_ID_V1'
  AND fr.is_synthetic = FALSE
GROUP BY ds.source_id, fr.source_gold_sentiment_label, fr.source_gold_emotion_label;


-- ------------------------------------------------------------------------------
-- VIEW 6: mv_pipeline_health
-- Grain: One row per pipeline execution run
-- Scope: NFR-003, UC-007, Operational Audit
-- Limitation: Technical pipeline audit data only. Timestamps are system execution
-- metadata, not customer review timestamps.
-- ------------------------------------------------------------------------------
CREATE OR REPLACE VIEW marketvoice_warehouse.mv_pipeline_health AS
SELECT
    pr.pipeline_run_id,
    pr.pipeline_version,
    pr.status,
    pr.started_at,
    pr.completed_at,
    ROUND(EXTRACT(EPOCH FROM (pr.completed_at - pr.started_at))::numeric, 2) AS duration_seconds,
    pr.source_a_rows_read,
    pr.source_b_rows_read,
    pr.loaded_rows_total,
    pr.rejected_rows_total,
    pr.critical_dq_fails,
    pr.major_dq_fails,
    COALESCE(dq_stats.total_checks, 0)::integer AS dq_check_count,
    COALESCE(dq_stats.passed_checks, 0)::integer AS dq_pass_count
FROM marketvoice_warehouse.pipeline_run pr
LEFT JOIN (
    SELECT
        pipeline_run_id,
        COUNT(*)::integer AS total_checks,
        COUNT(*) FILTER (WHERE passed = TRUE)::integer AS passed_checks
    FROM marketvoice_warehouse.data_quality_result
    GROUP BY pipeline_run_id
) dq_stats ON pr.pipeline_run_id = dq_stats.pipeline_run_id;
