-- ============================================================
-- Phase 11: Operational Workflow & Audit Schema
-- MarketVoice SEA — Operational Automation & Decision Triage
--
-- Governance:
--   - ADDITIVE only — zero modification to Phase 6-10 tables.
--   - Tracks operational events, n8n executions, and HITL cases.
-- ============================================================

SET search_path TO marketvoice_warehouse;

-- -----------------------------------------------------------
-- 1. operational_event_log — Raw Ingested Event Ledger
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS operational_event_log (
    event_sk                BIGSERIAL PRIMARY KEY,
    idempotency_key         VARCHAR(64) NOT NULL UNIQUE,
    request_id              VARCHAR(64) NOT NULL,
    source_id               VARCHAR(50) NOT NULL,
    source_review_id        VARCHAR(100) NOT NULL,
    payload_hash            VARCHAR(64) NOT NULL,
    rating_value            SMALLINT NOT NULL CHECK (rating_value BETWEEN 1 AND 5),
    detected_issues_count   SMALLINT NOT NULL,
    priority_score          NUMERIC(5,2) NOT NULL,
    tier_code               VARCHAR(30) NOT NULL,
    routing_destination     VARCHAR(50) NOT NULL,
    is_duplicate            BOOLEAN NOT NULL DEFAULT FALSE,
    raw_payload             JSONB NOT NULL,
    api_response            JSONB NOT NULL,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_operational_event_source
    ON operational_event_log (source_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_operational_event_routing
    ON operational_event_log (routing_destination, tier_code);

COMMENT ON TABLE operational_event_log IS
    'Phase 11: Operational audit log of all ingested review events with SHA-256 idempotency protection.';


-- -----------------------------------------------------------
-- 2. workflow_execution — n8n Orchestration Run Metrics
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS workflow_execution (
    execution_sk            BIGSERIAL PRIMARY KEY,
    workflow_id             VARCHAR(100) NOT NULL DEFAULT 'marketvoice_review_triage',
    execution_id            VARCHAR(100) NOT NULL UNIQUE,
    idempotency_key         VARCHAR(64) NOT NULL REFERENCES operational_event_log(idempotency_key),
    execution_status        VARCHAR(30) NOT NULL, -- SUCCESS, FAILED, RETRIED
    retry_count             SMALLINT NOT NULL DEFAULT 0,
    api_latency_ms          INTEGER NOT NULL,
    total_execution_ms      INTEGER NOT NULL,
    error_details           JSONB,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_workflow_exec_status
    ON workflow_execution (execution_status, created_at DESC);

COMMENT ON TABLE workflow_execution IS
    'Phase 11: n8n workflow execution performance metrics, latencies, and error logs.';


-- -----------------------------------------------------------
-- 3. human_review_case — Human-in-the-Loop Decision Triage Queue
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS human_review_case (
    case_sk                 BIGSERIAL PRIMARY KEY,
    case_id                 VARCHAR(64) NOT NULL UNIQUE,
    idempotency_key         VARCHAR(64) NOT NULL REFERENCES operational_event_log(idempotency_key),
    source_id               VARCHAR(50) NOT NULL,
    product_id              VARCHAR(100),
    category_id             VARCHAR(100),
    issue_name              VARCHAR(100) NOT NULL,
    priority_score          NUMERIC(5,2) NOT NULL,
    tier_code               VARCHAR(30) NOT NULL,
    reason_codes            TEXT[] NOT NULL,
    review_status           VARCHAR(30) NOT NULL DEFAULT 'PENDING_HUMAN_REVIEW', -- PENDING_HUMAN_REVIEW, IN_REVIEW, RESOLVED
    assigned_reviewer       VARCHAR(100),
    resolution_notes        TEXT,
    resolution_action       VARCHAR(50),
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at             TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_human_review_status
    ON human_review_case (review_status, priority_score DESC);

COMMENT ON TABLE human_review_case IS
    'Phase 11: Human-in-the-loop triage queue for P1 and P2 high-priority decision cases.';


-- -----------------------------------------------------------
-- 4. human_review_outcome — Resolution Ledger
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS human_review_outcome (
    outcome_sk              BIGSERIAL PRIMARY KEY,
    case_sk                 BIGINT REFERENCES human_review_case(case_sk),
    idempotency_key         VARCHAR(64) NOT NULL,
    action_type             VARCHAR(50) NOT NULL, -- QUALITY_AUDIT_INITIATED, VENDOR_INQUIRY, LOGISTICS_REVIEW, DISMISSED_FALSE_POSITIVE
    action_notes            TEXT NOT NULL,
    performed_by            VARCHAR(100) NOT NULL,
    action_timestamp        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE human_review_outcome IS
    'Phase 11: Audit trail of human decisions and operational actions taken.';
