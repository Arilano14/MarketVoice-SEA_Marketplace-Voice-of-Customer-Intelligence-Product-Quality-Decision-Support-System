-- DEL-08 Physical DDL (Phase 6 v1.1)
-- 004_indexes.sql
-- FK support indexes + composite query aid.
-- No Phase 7 BI mart indexes; no DEL-11 summary view indexes.

SET search_path TO marketvoice_warehouse;

-- audit / lineage
CREATE INDEX IF NOT EXISTS idx_rejected_pipeline_run_id
    ON rejected_record_log (pipeline_run_id);
CREATE INDEX IF NOT EXISTS idx_rejected_source_row
    ON rejected_record_log (source_id, source_row_number);
CREATE INDEX IF NOT EXISTS idx_dq_result_pipeline_run_id
    ON data_quality_result (pipeline_run_id);
CREATE INDEX IF NOT EXISTS idx_pipeline_run_status_started
    ON pipeline_run (status, started_at DESC);

-- dim source-local lookups (needed during fact SK map)
CREATE INDEX IF NOT EXISTS idx_dim_category_natkey_lookup
    ON dim_category (source_sk, source_native_category);
CREATE INDEX IF NOT EXISTS idx_dim_product_natkey_lookup
    ON dim_product (source_sk, source_native_product_id);
CREATE INDEX IF NOT EXISTS idx_dim_shop_natkey_lookup
    ON dim_shop (source_sk, source_native_shop_id);

-- fact_review FK indexes
CREATE INDEX IF NOT EXISTS idx_fact_source_sk
    ON fact_review (source_sk);
CREATE INDEX IF NOT EXISTS idx_fact_rating_sk
    ON fact_review (rating_sk);
CREATE INDEX IF NOT EXISTS idx_fact_category_sk
    ON fact_review (category_sk);
CREATE INDEX IF NOT EXISTS idx_fact_product_sk
    ON fact_review (product_sk);
CREATE INDEX IF NOT EXISTS idx_fact_shop_sk
    ON fact_review (shop_sk);
CREATE INDEX IF NOT EXISTS idx_fact_pipeline_run_id
    ON fact_review (pipeline_run_id);

-- composite query aid (Phase 7 BI will rely on this)
CREATE INDEX IF NOT EXISTS idx_fact_source_rating_value
    ON fact_review (source_sk, rating_value);
