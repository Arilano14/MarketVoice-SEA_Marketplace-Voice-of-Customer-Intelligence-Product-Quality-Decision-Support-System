-- DEL-08 Physical DDL (Phase 6 v1.1)
-- 003_constraints.sql
-- FK + CHECK + UNIQUE + seed dim_source (2 rows) + seed dim_rating (5 rows)
-- NO hardcoded source_sk CHECK(source_sk IN (1,2)) removed per §14 mandate.
-- Source identity resolved ONLY by source_id canonical lookup.

SET search_path TO marketvoice_warehouse;

-- ====================================================================
-- 1. pipeline_run CHECK constraints
-- ====================================================================
ALTER TABLE pipeline_run
    ADD CONSTRAINT chk_pipeline_run_status
    CHECK (status IN ('STARTED','SUCCESS','FAILED','ROLLBACK_ATTEMPTED'));

-- ====================================================================
-- 2. rejected_record_log FK + CHECK + UNIQUE
-- ====================================================================
ALTER TABLE rejected_record_log
    ADD CONSTRAINT fk_rejected_pipeline_run
    FOREIGN KEY (pipeline_run_id) REFERENCES pipeline_run(pipeline_run_id);

ALTER TABLE rejected_record_log
    ADD CONSTRAINT chk_rejected_stage
    CHECK (stage IN ('INPUT','TRANSFORM','PRE_COMMIT','FK_LOOKUP'));

ALTER TABLE rejected_record_log
    ADD CONSTRAINT chk_rejected_severity
    CHECK (severity IN ('CRITICAL','MAJOR','MINOR','INFO'));

ALTER TABLE rejected_record_log
    ADD CONSTRAINT uq_rejected_forensic_unique
    UNIQUE (pipeline_run_id, source_id, source_row_number, dq_check_id);

-- ====================================================================
-- 3. data_quality_result FK + CHECK (§25 grain already PK)
-- ====================================================================
ALTER TABLE data_quality_result
    ADD CONSTRAINT fk_dq_result_pipeline_run
    FOREIGN KEY (pipeline_run_id) REFERENCES pipeline_run(pipeline_run_id);

ALTER TABLE data_quality_result
    ADD CONSTRAINT chk_dq_severity
    CHECK (severity IN ('CRITICAL','MAJOR','MINOR','INFO'));

-- ====================================================================
-- 4. dim_category FK + UNIQUE natural key
-- ====================================================================
ALTER TABLE dim_category
    ADD CONSTRAINT fk_dim_category_source
    FOREIGN KEY (source_sk) REFERENCES dim_source(source_sk);

ALTER TABLE dim_category
    ADD CONSTRAINT uq_dim_category_natural_key
    UNIQUE (source_sk, source_native_category);

-- ====================================================================
-- 5. dim_product FK + UNIQUE natural key
-- ====================================================================
ALTER TABLE dim_product
    ADD CONSTRAINT fk_dim_product_source
    FOREIGN KEY (source_sk) REFERENCES dim_source(source_sk);

ALTER TABLE dim_product
    ADD CONSTRAINT uq_dim_product_natural_key
    UNIQUE (source_sk, source_native_product_id);

ALTER TABLE dim_product
    ADD CONSTRAINT chk_product_name_variant_count_nonneg
    CHECK (product_name_variant_count >= 1);

-- ====================================================================
-- 6. dim_shop FK + UNIQUE natural key
-- ====================================================================
ALTER TABLE dim_shop
    ADD CONSTRAINT fk_dim_shop_source
    FOREIGN KEY (source_sk) REFERENCES dim_source(source_sk);

ALTER TABLE dim_shop
    ADD CONSTRAINT uq_dim_shop_natural_key
    UNIQUE (source_sk, source_native_shop_id);

ALTER TABLE dim_shop
    ADD CONSTRAINT chk_shop_observation_count_nonneg
    CHECK (shop_observation_count >= 0);

-- ====================================================================
-- 7. dim_rating CHECK (5 rows 1..5)
-- ====================================================================
ALTER TABLE dim_rating
    ADD CONSTRAINT chk_rating_value_range
    CHECK (rating_value BETWEEN 1 AND 5);

ALTER TABLE dim_rating
    ADD CONSTRAINT chk_rating_bucket_enum
    CHECK (rating_bucket IN ('Negative','Neutral','Positive'));

-- ====================================================================
-- 8. fact_review FK + CHECK + defensive UNIQUE (§17 defensive only)
-- ====================================================================
ALTER TABLE fact_review
    ADD CONSTRAINT fk_fact_source
    FOREIGN KEY (source_sk) REFERENCES dim_source(source_sk);

ALTER TABLE fact_review
    ADD CONSTRAINT fk_fact_rating
    FOREIGN KEY (rating_sk) REFERENCES dim_rating(rating_sk);

ALTER TABLE fact_review
    ADD CONSTRAINT fk_fact_category
    FOREIGN KEY (category_sk) REFERENCES dim_category(category_sk);

ALTER TABLE fact_review
    ADD CONSTRAINT fk_fact_product
    FOREIGN KEY (product_sk) REFERENCES dim_product(product_sk);

ALTER TABLE fact_review
    ADD CONSTRAINT fk_fact_shop
    FOREIGN KEY (shop_sk) REFERENCES dim_shop(shop_sk);

ALTER TABLE fact_review
    ADD CONSTRAINT fk_fact_pipeline_run
    FOREIGN KEY (pipeline_run_id) REFERENCES pipeline_run(pipeline_run_id);

ALTER TABLE fact_review
    ADD CONSTRAINT chk_fact_rating_value_range
    CHECK (rating_value BETWEEN 1 AND 5);

ALTER TABLE fact_review
    ADD CONSTRAINT chk_fact_sentiment_enum
    CHECK (source_gold_sentiment_label IN ('Positive','Negative') OR source_gold_sentiment_label IS NULL);

ALTER TABLE fact_review
    ADD CONSTRAINT chk_fact_emotion_enum
    CHECK (source_gold_emotion_label IN ('Happy','Sadness','Fear','Love','Anger') OR source_gold_emotion_label IS NULL);

-- Defensive natural key uniqueness (§17 idempotency defensive; NOT a second strategy)
ALTER TABLE fact_review
    ADD CONSTRAINT uq_fact_natural_key_defensive
    UNIQUE (source_sk, source_native_row_hash);

-- Timestamp ordering TECHNICAL_METADATA only (§6 §21)
ALTER TABLE fact_review
    ADD CONSTRAINT chk_fact_timestamp_ordering
    CHECK (ingested_at <= processed_at AND processed_at <= loaded_at);

-- ====================================================================
-- 9. SEED dim_source — 2 manifest-registered sources (idempotent)
--    source_id = canonical authority. source_sk assigned internally; never hardcode 1/2.
--    Resolve at runtime: SELECT source_sk FROM dim_source WHERE source_id = %s
-- ====================================================================
INSERT INTO dim_source (
    source_id,
    source_display_name,
    source_license,
    source_doi_or_ref,
    source_data_url,
    source_file_sha256,
    source_row_count_manifest,
    source_column_count,
    source_locale
) VALUES (
    'SRC_PRDECT_ID_V1',
    'Source A - PRDECT-ID Indonesian Reviews V1',
    'CC BY 4.0',
    'https://doi.org/10.17632/574v66hf2v.1',
    NULL,
    '1dfdde6bb169ad57aab4211ecf45a75a4111b774ab43932f6d39c349bfd92bde',
    5400,
    11,
    'id-ID'
), (
    'SRC_TOKOPEDIA_REVIEWS_2019',
    'Source B - Tokopedia Reviews 2019',
    'Apache-2.0',
    'https://huggingface.co/datasets/farhamu/tokopedia-product-reviews-2019',
    NULL,
    'dbffc29078db1894e60884c526fe4d0ccbc592f33fe95d2e5ac2d8f96336b7ed',
    40607,
    8,
    'id-ID'
) ON CONFLICT (source_id) DO NOTHING;

-- ====================================================================
-- 10. SEED dim_rating — 5 rows (idempotent, ON CONFLICT DO NOTHING)
-- ====================================================================
INSERT INTO dim_rating (rating_value, rating_label, rating_bucket) VALUES
    (1, '1 - Very Negative', 'Negative'),
    (2, '2 - Negative',      'Negative'),
    (3, '3 - Neutral',       'Neutral'),
    (4, '4 - Positive',      'Positive'),
    (5, '5 - Very Positive', 'Positive')
ON CONFLICT (rating_value) DO NOTHING;
