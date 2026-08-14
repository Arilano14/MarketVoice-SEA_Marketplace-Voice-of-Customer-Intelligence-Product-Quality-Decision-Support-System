# MARKETVOICE SEA — PHASE 6 IMPLEMENTATION PLAN

**Phase:** 6 — ETL & Data Warehouse

**Document Version:** 1.1 (Revised Execution — MANDATORY REVISIONS applied per 2026-08-14 execution authorization)

**Date Revised:** 2026-08-14

**Status:**
```
PHASE_6_PLAN_STATUS = APPROVED_WITH_MANDATORY_REVISIONS
PHASE_6_PLAN_VERSION = 1.1
PHASE_6_EXECUTION_STATUS = IN_PROGRESS
PHASE_6_EXECUTION_AUTHORIZED = TRUE
PHASE_7_IMPLEMENTATION = FORBIDDEN
```

**Authority:** Phase 5 gate PASS recorded in `docs/governance/phase_gates.md` v4.3 (2026-08-14). Phase 5 logical architecture (29/29 design checks PASS via `reports/validation/phase_05_architecture_validation.md` v1.1). Execution authorization issued with 36 MANDATORY REVISIONS (§1-§36 of execution brief). All revisions in this v1.1 plan are traceable to those mandates.

**Revision Change Summary v1.0 → v1.1:**
| # | Mandate § | Revision Applied |
|---|---|---|
| R1 | §7 | DEL-08 scope CLARIFIED: business analytical marts / BI summary views (mv_*) are Phase 7 DEL-11; REMOVED from Phase 6 DEL-08. |
| R2 | §8 | Staging: Python IN-MEMORY dict-list only; NO DB staging tables; NO Pandas added. |
| R3 | §9 | Removed ALL Track B loader, ENABLE_TRACK_B branch, synthetic fixture pipeline. is_synthetic = FALSE for every row; any TRUE → CRITICAL BLOCK_LOAD. |
| R4 | §10 | Removed 099_future_phases_reserved.sql from SQL tree. |
| R5 | §11 | Replaced single-transaction model with THREE-TRANSACTION AUDIT MODEL: TX-A (pipeline_run STARTED committed independently) → TX-B (warehouse refresh + PRE-COMMIT CRITICAL CHECKS → ROLLBACK on any fail) → TX-C (finalize SUCCESS/FAILED committed independently). |
| R6 | §12 | CRITICAL PRE-COMMIT CHECKS enumerated; MUST RUN BEFORE TX-B COMMIT. Failure → ROLLBACK. Post-commit checks only forensic, cannot rollback. |
| R7 | §13 | pipeline_run, rejected_record_log, data_quality_result are HISTORICAL AUDIT TABLES → NEVER TRUNCATED. Full refresh only applies to 4 dynamic analytical tables. |
| R8 | §14 | source_sk never hardcoded (1/2). Identity resolved ONLY via dim_source canonical source_id lookup. |
| R9 | §15 | UNKNOWN MEMBER POLICY: No fake unknown dimension members. Invalid rows rejected. Source A product_sk NULL, shop_sk NULL. |
| R10 | §16 | Row identity formula SHA256(source_id + "|" + source_file_sha256 + "|" + stable_source_row_number). Classified WAREHOUSE_INTERNAL / NOT_LINKABLE. Never for cross-source. |
| R11 | §17 | IDEMPOTENCY single canonical = TRANSACTIONAL_DETERMINISTIC_FULL_REFRESH. ON CONFLICT only defensive. Not described simultaneously as truncate/reload + conflict idempotency. |
| R12 | §18 | DQ severity semantic CRIT/MAJOR/MINOR/INFO. REMOVED arbitrary 1%/5% run thresholds. PASS requires 0 UNRESOLVED_CRITICAL + 0 UNRESOLVED_MAJOR_INTEGRITY. |
| R13 | §19 | SOURCE B FK RULE: accepted B review → product_sk and shop_sk MUST resolve. Unresolved FK → CRITICAL BLOCK_LOAD. For Source A: product_sk/shop_sk MUST BE NULL. |
| R14 | §20 | PRODUCT NAME VARIANT: non-null product_name per product_id → most frequent; tie-break = lowest stable source_row_number. Report variant_count. NEVER merge products by name. product_id authoritative. |
| R15 | §21 | ENCODING: UTF-8 strict decode. Decode error → CRIT BLOCK_LOAD. NEVER errors="replace". PostgreSQL SHOW server_encoding = UTF8. No Unix locale on Windows. |
| R16 | §22 | TEST DB SAFETY: destructive DROP/TRUNCATE guard MARKETVOICE_ENV=test AND current_database()=configured_test_db. ABORT otherwise. |
| R17 | §24 | PHYSICAL TABLES exactly 9: 6 analytical (dim_source/dim_rating/dim_category/dim_product/dim_shop/fact_review) + 3 audit (pipeline_run/rejected_record_log/data_quality_result). NO dim_date / model / issue / decision / case / intervention / views. |
| R18 | §25 | data_quality_result REQUIRED. Grain: one pipeline_run_id × one dq_check_id. |
| R19 | §26 | RAW DATA SHA pre-ETL + post-ETL (recompute after load) + compare to manifest. Mismatch → CRITICAL STOP. Never write data/raw. |
| R20 | §28 | S2T mapping register: every target field has target_table + target_field + source/source_field + transformation + null_rule + DQ_rule + lineage_class. UNEXPLAINED_WAREHOUSE_FIELDS = 0. |

**Hard Stop Conditions (this document):**
- Stop only for: GENUINE_EXTERNAL_BLOCKER, MATERIAL_PHASE_5_ARCHITECTURE_DEFECT, UNAVAILABLE_REQUIRED_DATA, UNSAFE_DATABASE_STATE
- NEVER silently rewrite governance history; every change explicitly versioned
- Phase 7 (marts/BI) → FORBIDDEN; never created in DEL-08/09/10
- Never commit to remote Git; never write to data/raw tier

---

## 1. EXECUTIVE PURPOSE

Phase 6 implements the **physical PostgreSQL data warehouse, reproducible Python batch ETL pipeline, and automated Data Quality (DQ) controls** specified by the Phase 5 logical architecture. It delivers only the three canonical Phase 6 deliverables:

- **DEL-08** PostgreSQL Data Warehouse & Staging Schema — DDL scripts creating technical staging responsibility, physical warehouse schema, tables, constraints, and indexes (derived strictly from Phase 5 Kimball dimensional model). CLARIFICATION v1.1: Business analytical marts / BI-ready summary views are Phase 7 DEL-11 scope and explicitly EXCLUDED from DEL-08.
- **DEL-09** Reproducible SQL/Python ETL Pipeline — Automated batch ETL loading authentic Track A raw source evidence (Source A PRDECT-ID V1 + Source B Tokopedia 2019) into the governed analytical warehouse: without cross-source fabrication, without temporal invention, preserving full provenance lineage. CLARIFICATION v1.1: Track B synthetic pipeline is DISABLED and NOT implemented in Phase 6. requires separate future explicit authorization.
- **DEL-10** Automated Data Quality Test Suite — DQ at INPUT → TRANSFORMATION → PRE-COMMIT → POST_LOAD stages with semantic CRITICAL/MAJOR/MINOR/INFO severity classes. Zero-tolerance for unresolved CRITICAL failures. Zero unresolved MAJOR INTEGRITY blockers.

Phase 6 explicitly does **NOT** include (§3 strict scope):
- Baseline BI queries / business marts / summary views (Phase 7 DEL-11)
- ML rating/sentiment/emotion model training or inference (Phase 8–9)
- Issue taxonomy, aspect annotation, or classifier DDL/training (Phase 9)
- Priority scoring, decision formulas, case queues, SLA logic (Phase 10)
- FastAPI, REST endpoints, n8n workflows (Phase 11)
- Power BI visuals/DAX/reports/pages/datasets (Phase 7/12)
- Synthetic Track B data (NOT AUTHORIZED for Phase 6)
- Cross-source product/shop fuzzy linkage (FORBIDDEN by locked data reality)
- Cloud warehouse, Kafka, Spark, Airflow, Kubernetes, microservices, vector DB, feature store (FORBIDDEN)

---

## 2. VERIFIED PHASE 0–5 ENTRY

### 2.1 Canonical Gate Authority (`docs/governance/phase_gates.md` v4.3)

```
PHASE_0_GATE = PASS
PHASE_1_GATE = PASS
PHASE_2_GATE = PASS
PHASE_3_GATE = PASS  (human sign-off HD-002 2026-08-14; formal)
PHASE_4_GATE = PASS  (technical PASS pre-existing; admin dep released by Phase 3 PASS)
PHASE_5_GATE = PASS  (29/29 architecture design checks PASS; admin dep released by Phase 4 PASS)
PHASE_6_ENTRY_READINESS = PASS
PHASE_6_EXECUTION_STATUS = IN_PROGRESS
```

### 2.2 Evidence Register

| Gate | Primary evidence | Key verified facts |
|---|---|---|
| Phase 0 | `docs/governance/project_charter.md`, `data_governance_policy.md`, `project_definition_of_done.md` v1.1 | Governance, DOD, data tier LOCAL_ONLY policy in force. DEL-08/09/10 v1.1 clarifications applied (mart=Phase7, synthetic=out-of-scope, semantic severity) |
| Phase 1 | `docs/engineering/development_environment.md`; `tests/test_environment.py` 3/3 PASS; `config/project_settings.yaml` | Python 3.10 stack; Git; local paths data/raw/interim/processed/metadata/logs declared. PostgreSQL 12.4 server verified running localhost:5432; server_encoding=UTF8 confirmed. psycopg[binary] driver installed. |
| Phase 2 | `data/metadata/source_manifest.csv`; `data/metadata/data_capability_matrix.csv`; `reports/validation/phase_02_dataset_forensic_audit_report.md` | Source A = 5,400 rows / 11 cols / SHA `1dfdde6b…bde`. Source B = 40,607 rows / 8 cols / SHA `dbffc290…b7ed`. 29 CAP IDs with NOT_SUPPORTED boundaries LOCKED. |
| Phase 3 | `docs/requirements/business_and_information_requirements.md` + system_requirements.md + use_cases_and_mvp.md + requirements_traceability.md; gate record §4 | 7 BQ → 7 BR → 7 IR → 9 FR + 7 NFR; ORPHAN_MUST_REQUIREMENTS = 0; bounded scope explicit. |
| Phase 4 | `docs/methodology/analytical_research_design.md` + evaluation_protocol.md + experiment_protocol.md; `config/experiment_settings.yaml`; gate record §5 | 70/15/15 stratified non-temporal split; deterministic duplicate policy; ordinal rating metrics QWK+MAE+per-class recall mandatory; holdout ONCE only. |
| Phase 5 | `docs/architecture/solution_architecture.md` + data_architecture.md + dimensional_model.md + integration_contracts.md; `reports/validation/phase_05_architecture_validation.md` v1.1 29/29 PASS; gate §6 | ONE_FACT_ONE_GRAIN; FAKE_CROSS_SOURCE_KEYS=FORBIDDEN; 6 core analytical tables + 3 audit tables = 9 total physical tables; NO dim_date; ORPHAN_ARCHITECTURE_COMPONENTS = 0. |

### 2.3 Verified Empirical Raw Data Reality (reconfirmed)

| Attribute | Source A (PRDECT-ID V1) | Source B (Tokopedia 2019) |
|---|---|---|
| Row count (exact) | 5,400 | 40,607 |
| Column count (exact) | 11 | 8 |
| Rating field | `Customer Rating` (values 1–5; verified 1=1832,2=561,3=462,4=395,5=2150) | `rating` (strings '1'..'5'; verified 1=543,2=382,3=1825,4=7546,5=30311) |
| Review text | `Customer Review` | `text` |
| Sentiment gold | PROVIDED (Positive 2821 / Negative 2579) | NOT_AVAILABLE |
| Emotion gold | PROVIDED (Happy 1770 / Sadness 1202 / Fear 920 / Love 809 / Anger 699) | NOT_AVAILABLE |
| Category | `Category` (29 unique, 200/row balanced) | `category` (5 unique values; no proven conformance to A) |
| Product business key | NOT_AVAILABLE (`Product Name` is text only; NOT a business key) | `product_id` (3,664 unique; SOURCE_NATIVE authoritative) |
| Shop business key | NOT_AVAILABLE | `shop_id` (158 unique; SOURCE_NATIVE authoritative) |
| Product metadata (contextual) | `Product Name`, `Price`, `Overall Rating`, `Number Sold`, `Total Review` (all source-local contextual only) | `product_name`, `sold` (40,592 non-empty; 15 empty → NULL stored) |
| Other contextual | `Location` (61 values) | `product_url` |
| Review/event timestamp | NOT_AVAILABLE | NOT_AVAILABLE |
| SLA / case / lifecycle | NOT_AVAILABLE | NOT_AVAILABLE |

### 2.4 Locked Data Reality (Phase 5 + Execution §6)

```
REAL_REVIEW_TIMESTAMP = NOT_AVAILABLE

SOURCE_A_PRODUCT_ID = NOT_AVAILABLE
SOURCE_A_SHOP_ID = NOT_AVAILABLE
SOURCE_B_SENTIMENT_GOLD = NOT_AVAILABLE
SOURCE_B_EMOTION_GOLD = NOT_AVAILABLE

SOURCE_A_TO_B_ROW_LINKAGE = NOT_SUPPORTED
SOURCE_A_TO_B_PRODUCT_LINKAGE = NOT_SUPPORTED
SOURCE_A_TO_B_SHOP_LINKAGE = NOT_SUPPORTED

FUZZY_LINKAGE = FORBIDDEN
TRACK_B = NOT_AUTHORIZED
```

Only TECHNICAL_METADATA timestamps allowed: `ingested_at`, `processed_at`, `loaded_at`, `pipeline_started_at`, `pipeline_completed_at`. Never called review/event timestamps.

### 2.5 Git / Working-Tree Readiness (reconfirmed)

```
git status --short = ?? docs/plans/phase_06_implementation_plan.md (new plan v1.0 from planning phase)
git branch --show-current = main
git log -n 5 --oneline = clean lineage (no remote write)
git diff --stat = (no unstaged divergence)
git ls-files data/raw = empty (GOOD; only .gitkeep + README tracked)
```

---

## 3. LOCKED DELIVERABLE SCOPE

### 3.1 Authorized Deliverables Only

| DEL-ID | Canonical Name | Canonical Definition (project_definition_of_done.md v1.1) | Prereq | Phase 6 Plan Coverage |
|---|---|---|---|---|
| **DEL-08** | PostgreSQL Data Warehouse & Staging Schema | DDL scripts creating technical staging, physical DW schema, tables, constraints, and indexes. CLARIFICATION: business analytical marts / BI-ready summary views are Phase 7 DEL-11 scope and explicitly excluded. | DEL-07 | §7 Physical DDL; §8 Table/Key Register; SQL tree sql/warehouse/001-004; Steps 6.5–6.6. |
| **DEL-09** | Reproducible SQL/Python ETL Pipeline | Automated ETL loading authentic Track A raw data to DW. CLARIFICATION: Track B synthetic requires separate explicit authorization and is excluded from Phase 6. | DEL-08 | §10 ETL Design; §15 Planned Code Tree; Steps 6.7–6.11, 6.14. |
| **DEL-10** | Automated Data Quality Test Suite | Automated test suite passing with 0 CRITICAL failures and 0 unresolved MAJOR INTEGRITY blockers. | DEL-09 | §11 DQ Design; §16 Tests; §20 Acceptance Criteria (AC-01..AC-20); Steps 6.9, 6.12–6.13, 6.15–6.16. |

### 3.2 Explicitly Excluded from Phase 6 (per §2+§7+§9+§10)

- **Phase 7 DEL-11**: ALL business marts / summary views (`mv_source_summary`, `mv_category_summary_source_specific`, `mv_product_b_summary`, `mv_shop_b_summary`, `mv_source_a_label_breakdown`, `mv_pipeline_run_recent` and any other BI view).
- **Track B pipeline**: `track_b_loader` module, `ENABLE_TRACK_B` configuration branch, synthetic fixture pipeline, synthetic production path. Future Track B requires SEPARATE explicit authorization. If `is_synthetic = TRUE` is ever found on any Phase 6 row → CRITICAL → BLOCK_LOAD.
- **Placeholder SQL files**: `099_future_phases_reserved.sql` (future entities remain documentation-only).
- **SQLAlchemy, Alembic, Airflow, dbt, python-dotenv (duplicate)**: NOT added.
- **dim_date, model tables, issue tables, decision tables, case tables, intervention tables**: NOT created.

---

## 4. SOURCE OF TRUTH

| Item | Authority | Notes |
|---|---|---|
| Raw source bytes | `data/raw/*.csv` (LOCAL_ONLY; never versioned; never written) | Read-only. SHA256 compared to manifest pre + post ETL. |
| Source SHA / row counts | `data/metadata/source_manifest.csv` | Canonical. Mismatch = DQ-INTEGRITY-001 CRITICAL BLOCK_LOAD. |
| Source column definitions | `config/data_sources.yaml` `official_columns` | DictReader keys verified. Order-independent. |
| Source boundary constraints | `data/metadata/data_capability_matrix.csv` CAP-03..CAP-07 | Defines what is NOT_AVAILABLE / NOT_SUPPORTED. |
| Source identity | `source_id` = SRC_PRDECT_ID_V1 / SRC_TOKOPEDIA_REVIEWS_2019 (from data_sources.yaml) | dim_source seeded by source_id canonical lookup ONLY. Never hardcoded source_sk=1/2. |
| Warehouse design | Phase 5 dimensional_model.md / data_architecture.md / integration_contracts.md | 9 tables only. |
| ETL behavior | This plan v1.1 §10 / §12 | 3-transaction model; deterministic full refresh. |
| DQ severity semantics | This plan v1.1 §11 | CRITICAL / MAJOR / MINOR / INFO only. No arbitrary percent thresholds. |
| Paths & env | `config/project_settings.yaml` + `.env` (from `.env.example`) | MARKETVOICE_ENV controls test/dev. |
| PostgreSQL driver | psycopg[binary] v3.x (stdlib csv + psycopg only. Pandas NOT added.) | Per §23 authorization. |

---

## 5. BOUNDARIES AND ANTI-PATTERNS ENFORCED

1. **No cross-source fabrication.** Source A never gets product_sk/shop_sk. Source B never gets sentiment/emotion labels populated from A or any other source. Zero row-level linkage between A and B.
2. **No synthetic timestamps.** ingested_at/processed_at/loaded_at only = TECHNICAL_METADATA. Never called review/event timestamps.
3. **No fuzzy linking.** Never approximate-match products/shops by name across sources. product_id and shop_id authoritative.
4. **No silent data mutation.** UTF-8 decode strict (never errors="replace"). Review text only: collapse 2+ consecutive newlines; never remove stopwords/punctuation in ETL (that is Phase 8 governed preprocessing).
5. **No unknown dimension members.** Invalid source/rating/category/product/shop → REJECT_ROW, not fake member placeholder.
6. **Audit history is sacred.** pipeline_run / rejected_record_log / data_quality_result → NEVER TRUNCATED. Historical evidence retained scoped by pipeline_run_id.
7. **Idempotency strategy single-canonical.** TRANSACTIONAL_DETERMINISTIC_FULL_REFRESH. UNIQUE (source_sk, source_native_row_hash) is a defensive constraint only. Not simultaneously described as truncate+reload AND ON CONFLICT strategy.
8. **Phase 6 PASS = 0 CRITICAL + 0 unresolved MAJOR INTEGRITY.** Per semantic severity matrix below.

---

## 6. RECONCILIATION REGISTER (Phase 5 Architecture → Phase 6 Implementation)

| ID | Phase 5 → 6 Discrepancy / Clarification | Classification | Resolution in Plan v1.1 |
|---|---|---|---|
| R-01 | Plan v1.0 created DEL-08 business views (mv_* five) | MANDATORY_REVISION §7 | REMOVED. mv_* five views reclassified as Phase 7 DEL-11. DEL-08 = physical warehouse + constraints + indexes + technical staging resp ONLY. |
| R-02 | Plan v1.0 single BEGIN...COMMIT wrapped pipeline_run inside warehouse TX | MANDATORY_REVISION §11 | 3-TX MODEL implemented: TX-A pipeline_run STARTED COMMIT; TX-B warehouse refresh + PRE-COMMIT CHECKS ROLLBACK/COMMIT; TX-C finalize pipeline_run COMMIT. |
| R-03 | Plan v1.0 truncated audit tables (rejected_record_log, data_quality_result) | MANDATORY_REVISION §13 | Audit tables NEVER TRUNCATED. Only 4 dynamic analytical tables (dim_category, dim_product, dim_shop, fact_review) are truncated. |
| R-04 | Plan v1.0 row hash = sha256(source_id + "|" + row_number). Missing file_sha. | MANDATORY_REVISION §16 | Formula corrected: SHA256(source_id + "\|" + source_file_sha256 + "\|" + stable_source_row_number zero-padded). Classified WAREHOUSE_INTERNAL / NOT_LINKABLE. |
| R-05 | Plan v1.0 hardcoded source_sk = 1 for A, =2 for B. FK CHECK(source_sk IN (1,2)) | MANDATORY_REVISION §14 | Check constraints on source_sk removed from dim tables; seed dim_source by source_id and resolve only via SELECT source_sk FROM dim_source WHERE source_id = %s. |
| R-06 | Plan v1.0 DQ INPUT runs had 1% cumulative threshold → CRITICAL upgrade. Post DQ also 5% allowances. | MANDATORY_REVISION §18 | All arbitrary percent thresholds REMOVED. Severity semantic only: per-row MAJOR = REJECT_ROW; run-wide hard failures only explicit CRITICAL rules in §12. |
| R-07 | Plan v1.0 B unresolved FK → MAJOR allow load. | MANDATORY_REVISION §19 | Accepted B reviews → product_sk MUST resolve AND shop_sk MUST resolve. Unresolved FK = PRE-COMMIT CRITICAL → ROLLBACK TX-B → BLOCK_LOAD. |
| R-08 | Source A `Customer Rating` vs. Source B `rating` (int-ish vs. string) | IMPLEMENTATION_DETAIL | Standardize to SMALLINT rating_value; B cast enforced by DQ-RATING-002. A already integer. |
| R-09 | Source B `sold` column: 15 empty rows + text format (1.2rb etc.) | IMPLEMENTATION_DETAIL | Store sold_raw_text as TEXT nullable. Never parse/interpret; interpretation Phase 7+ analytics. DQ INFO reports empty count. |
| R-10 | Source A gold labels (sentiment/emotion) + review metadata columns (Location/Price/Overall Rating/Number Sold/Total Review/Product Name) | IMPLEMENTATION_DETAIL | Stored in fact_review source_a_context_* TEXT nullable. All NULL for B. |
| R-11 | Source B product_name multi-variant per product_id | MANDATORY_REVISION §20 | For each product_id: collect non-null names → choose most frequent; tie-break = lowest stable source_row_number. Store dim_product.product_name_variant_count. NEVER merge products by name. product_id authoritative. |
| R-12 | `dim_source` seed: two rows manifest-registered | IMPLEMENTATION_DETAIL | DDL seed by source_id canonical: SRC_PRDECT_ID_V1 + SRC_TOKOPEDIA_REVIEWS_2019. INSERT ... ON CONFLICT DO NOTHING. |
| R-13 | `dim_rating` seed: 5 rows rating_value 1..5 | IMPLEMENTATION_DETAIL | DDL seed (1-5). ON CONFLICT DO NOTHING. |
| R-14 | Future model/issue/DSS/case/intervention tables | ARCHITECTURE_DEFECT? → NO (deferred correctly) | Documentation-only deferred; NEVER create 099_future_phases_reserved.sql. |
| R-15 | Plan v1.0 staging mentioned "DataFrame / dict-list" and Pandas could be misread. | MANDATORY_REVISION §8 | Clarified: stdlib csv.DictReader → list[dict] only. Pandas NOT added. No DB staging tables unless proven necessary (not needed for 46K rows 2 sources). |
| R-16 | Plan v1.0 idempotency simultaneously described full refresh + ON CONFLICT dual mechanism. | MANDATORY_REVISION §17 | Single canonical: TRANSACTIONAL_DETERMINISTIC_FULL_REFRESH. UNIQUE (source_sk, source_native_row_hash) remains DEFENSIVE ONLY. Not a second idempotency strategy. |

---

## 7. PHYSICAL POSTGRESQL DATA WAREHOUSE (DEL-08)

### 7.1 Schema

Single schema: `marketvoice_warehouse`.

All objects qualified. No cross-schema references in Phase 6.

### 7.2 Physical Table Register (9 Tables ONLY — §24)

**Audit / Control tables (3) — NEVER TRUNCATED per §13:**

| # | Table Name | Grain | Purpose | PK-equivalent | Created in |
|---|---|---|---|---|---|
| A1 | `pipeline_run` | One per ETL run | Records lifecycle STARTED/SUCCESS/FAILED. Survives warehouse rollback via independent TX. | `pipeline_run_id UUID` | 002_tables.sql + seed |
| A2 | `rejected_record_log` | One per rejected source row × run_id | Records why row was rejected. Appended each run. Never truncated. Retained scoped by pipeline_run_id. | `(rejection_id SERIAL)` (internal) OR `(pipeline_run_id, source_id, source_row_number)` unique. Natural uniqueness forensically enforced. | 002_tables.sql |
| A3 | `data_quality_result` | One pipeline_run_id × one dq_check_id | Result of every DQ check per run. Retained forever. Grain per §25. | `(pipeline_run_id, dq_check_id)` | 002_tables.sql |

**Analytical tables (6) — full refresh applies ONLY to the 4 dynamic ones below:**

| # | Table Name | Grain | Type | Truncated per Run? |
|---|---|---|---|---|
| D1 | `dim_source` | One per registered canonical source_id | Conformed dimension | NO. Idempotent seed only (2 rows). Never truncated. |
| D2 | `dim_rating` | One per rating_value (1..5) | Conformed dimension | NO. Idempotent seed only (5 rows). Never truncated. |
| D3 | `dim_category` | One (source_sk, source_native_category) | Source-local conformed dimension | YES. Dynamic analytical; rebuilt each TX-B run. |
| D4 | `dim_product` | One (source_sk, source_native_product_id) | Source-local conformed dimension | YES. Dynamic. Rebuilt each run. |
| D5 | `dim_shop` | One (source_sk, source_native_shop_id) | Source-local conformed dimension | YES. Dynamic. Rebuilt each run. |
| F1 | `fact_review` | One accepted source review row per natural run | Central fact. ONE_FACT_ONE_GRAIN. | YES. Dynamic. Rebuilt each run. |

### 7.3 NOT Created (Explicitly per §7, §9, §10, §24)

- NO summary views / BI marts (`mv_*`) — Phase 7 DEL-11.
- NO `099_future_phases_reserved.sql` (future placeholder).
- NO dim_date (no timestamps in MVP; dates unnecessary for MVP queries).
- NO model/issue/decision/case/intervention tables.
- NO Track B tables or ENABLE_TRACK_B columns (besides is_synthetic boolean in fact_review).
- NO staging tables in DB.

---

## 8. TABLE / KEY REGISTER (DETAILED)

### 8.1 pipeline_run (A1 — Historical Audit)

| Field | Type | Constraint | Source / Semantic |
|---|---|---|---|
| pipeline_run_id | UUID | PRIMARY KEY | UUID4 from orchestrator SYSTEM_GENERATED |
| started_at | TIMESTAMPTZ | NOT NULL | TX-A INSERT time (UTC) |
| completed_at | TIMESTAMPTZ | NULLABLE | TX-C UPDATE time (UTC); NULL while in progress |
| status | TEXT | NOT NULL CHECK (status IN ('STARTED','SUCCESS','FAILED','ROLLBACK_ATTEMPTED')) | Lifecycle |
| pipeline_version | TEXT | NOT NULL | Semver string. SYSTEM_GENERATED. |
| input_rows_total | INTEGER | NOT NULL DEFAULT 0 | Sum of source A + B raw rows actually read (excludes header). |
| accepted_rows_total | INTEGER | NOT NULL DEFAULT 0 | Rows that passed INPUT/TRANSFORM DQ. |
| rejected_rows_total | INTEGER | NOT NULL DEFAULT 0 | COUNT of rejected_record_log rows for this run. |
| loaded_rows_total | INTEGER | NOT NULL DEFAULT 0 | COUNT of fact_review rows committed for this run (post-commit filled by TX-C). |
| source_a_file_sha256 | TEXT | NOT NULL | SHA of Source A file verified pre-load. |
| source_b_file_sha256 | TEXT | NOT NULL | SHA of Source B file verified pre-load. |
| source_a_rows_manifest | INTEGER | NOT NULL | 5,400 (from manifest). |
| source_b_rows_manifest | INTEGER | NOT NULL | 40,607 (from manifest). |
| source_a_rows_read | INTEGER | NOT NULL DEFAULT 0 | Count from DictReader. |
| source_b_rows_read | INTEGER | NOT NULL DEFAULT 0 | Count from DictReader. |
| source_a_rows_loaded | INTEGER | NOT NULL DEFAULT 0 | fact_review WHERE dim_source.source_id = SRC_PRDECT_ID_V1. |
| source_b_rows_loaded | INTEGER | NOT NULL DEFAULT 0 | fact_review WHERE dim_source.source_id = SRC_TOKOPEDIA_REVIEWS_2019. |
| critical_dq_fails | INTEGER | NOT NULL DEFAULT 0 | Counts CRITICAL data_quality_result for this run. |
| major_dq_fails | INTEGER | NOT NULL DEFAULT 0 | Counts unresolved MAJOR. |
| notes | TEXT | NULLABLE | Free-text for forensic analysis. |

- **Null rule:** Only completed_at, notes NULL allowed.
- **DQ rule:** status constrained to enum.
- **Never truncated; only INSERT + two UPDATEs (status=STARTED→then SUCCESS/FAILED).**

### 8.2 rejected_record_log (A2 — Historical Audit)

| Field | Type | Constraint | Source / Semantic |
|---|---|---|---|
| rejection_id | SERIAL | PK | Internal only. |
| pipeline_run_id | UUID | NOT NULL REFERENCES pipeline_run(pipeline_run_id) | Scoped to run. |
| source_id | TEXT | NOT NULL | SRC_PRDECT_ID_V1 or SRC_TOKOPEDIA_REVIEWS_2019. Canonical source identity. |
| source_row_number | INTEGER | NOT NULL | 1-based stable source row number. |
| source_native_row_hash | TEXT | NULLABLE | If hash computable at reject stage. |
| stage | TEXT | NOT NULL CHECK (stage IN ('INPUT','TRANSFORM','PRE_COMMIT','FK_LOOKUP')) | Where rejected. |
| severity | TEXT | NOT NULL CHECK (severity IN ('CRITICAL','MAJOR','MINOR','INFO')) | Semantic. |
| dq_check_id | TEXT | NOT NULL | e.g. DQ-INPUT-RATING-001 |
| reason_code | TEXT | NOT NULL | Short code. |
| reason_text | TEXT | NOT NULL | Human explanation. |
| raw_row_snippet | TEXT | NULLABLE | 200-char snippet for forensic trace. |
| ingested_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | Technical timestamp. |

- Uniqueness forensically: UNIQUE(pipeline_run_id, source_id, source_row_number, dq_check_id).
- **Never truncated.** Inserted in separate commits so rows survive TX-B rollback per §11.

### 8.3 data_quality_result (A3 — Required Grain §25)

| Field | Type | Constraint | Source / Semantic |
|---|---|---|---|
| pipeline_run_id | UUID | NOT NULL REFERENCES pipeline_run(pipeline_run_id) | Part of composite PK. |
| dq_check_id | TEXT | NOT NULL | Part of composite PK. |
| severity | TEXT | NOT NULL CHECK (...) | CRIT/MAJOR/MINOR/INFO |
| passed | BOOLEAN | NOT NULL | True/false |
| actual_value | TEXT | NULLABLE | e.g. count, sha, SQL result. |
| expected_value | TEXT | NULLABLE | Expected. |
| evidence | TEXT | NULLABLE | Longer description. |
| measured_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | When checked. |

- **PRIMARY KEY (pipeline_run_id, dq_check_id) → §25 grain enforced.**
- Inserted in separate commits; survives TX-B rollback. Never truncated.

### 8.4 dim_source (D1 — Conformed Master Dimension; Never Truncated)

| Field | Type | Constraint | Source / Semantic |
|---|---|---|---|
| source_sk | SMALLSERIAL | PRIMARY KEY | Surrogate key. Internally assigned. **NEVER hardcode 1/2. Resolve via source_id lookup ONLY.** |
| source_id | TEXT | NOT NULL UNIQUE | Canonical: SRC_PRDECT_ID_V1 or SRC_TOKOPEDIA_REVIEWS_2019. Lookup key. |
| source_display_name | TEXT | NOT NULL | "Source A — PRDECT-ID Indonesian Reviews V1", "Source B — Tokopedia Reviews 2019" |
| source_license | TEXT | NOT NULL | "CC BY 4.0" or "Apache 2.0" per manifest. |
| source_doi_or_ref | TEXT | NULLABLE | DOI 10.17632/574v66hf2v.1 or Hugging Face farhamu/tokopedia-reviews |
| source_data_url | TEXT | NULLABLE | |
| source_file_sha256 | TEXT | NOT NULL | Canonical SHA from manifest. |
| source_row_count_manifest | INTEGER | NOT NULL | 5,400 or 40,607 per manifest. |
| source_column_count | INTEGER | NOT NULL | 11 or 8. |
| source_locale | TEXT | NOT NULL | 'id-ID' (both Indonesian). |
| registered_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |

- **Loaded by:** DDL seed INSERT ... ON CONFLICT DO NOTHING.
- **Unknown member policy §15:** No fake unknown member. Invalid source → CRITICAL BLOCK_LOAD (not member).
- Expected: dim_source count = 2 (actual registered only).

### 8.5 dim_rating (D2 — Conformed Master Dimension; Never Truncated)

| Field | Type | Constraint | Source/Semantic |
|---|---|---|---|
| rating_sk | SMALLSERIAL | PRIMARY KEY | Surrogate. |
| rating_value | SMALLINT | NOT NULL UNIQUE CHECK (rating_value BETWEEN 1 AND 5) | Ordinal 1-5 authoritative. |
| rating_label | TEXT | NOT NULL | '1 - Very Negative' … '5 - Very Positive' display. |
| rating_bucket | TEXT | NOT NULL CHECK (rating_bucket IN ('Negative','Neutral','Positive')) | 1-2 = Negative, 3 = Neutral, 4-5 = Positive. Useful for BI (Phase 7). |

- DDL seed 5 rows. ON CONFLICT DO NOTHING.
- Unknown member policy: NO unknown member. rating_value outside 1..5 → REJECT_ROW. Not stored in fake member.
- Expected count = 5.

### 8.6 dim_category (D3 — Source-Local Conformed Dimension; TRUNCATEd each run)

| Field | Type | Constraint | Source/Semantic |
|---|---|---|---|
| category_sk | SERIAL | PRIMARY KEY | Surrogate. Reassigned each run. Re-lookup immediately. |
| source_sk | SMALLINT | NOT NULL REFERENCES dim_source(source_sk) | Never hardcoded. Resolved via source_id. Source-qualified because categories are source-internal (A 29 values vs B 5 values; no conformance proven). |
| source_native_category | TEXT | NOT NULL | Raw category text from CSV. |
| category_value_count_observations | INTEGER | NOT NULL DEFAULT 0 | Count in fact for this (source, category) at dimension build time. |

- **Natural key UNIQUE(source_sk, source_native_category).**
- For Source A: 29 rows. Source B: 5 rows. Total ≤ 34.
- No fake unknown member: missing/empty category → REJECT_ROW.

### 8.7 dim_product (D4 — Source-Local Product; TRUNCATEd; B-only for MVP)

| Field | Type | Constraint | Source/Semantic |
|---|---|---|---|
| product_sk | SERIAL | PRIMARY KEY | |
| source_sk | SMALLINT | NOT NULL REFERENCES dim_source(source_sk) | B source (resolved via source_id). |
| source_native_product_id | TEXT | NOT NULL | product_id authoritative from B raw. |
| source_native_product_name | TEXT | NULLABLE | Most frequent non-null product_name for the product_id. Tie-break §20: lowest stable source_row_number wins tie. |
| product_name_variant_count | SMALLINT | NOT NULL DEFAULT 1 | §20 variant reporting. Count of distinct non-null product_name values observed for this product_id. |

- UNIQUE(source_sk, source_native_product_id).
- No fake unknown member. product_id empty in B → REJECT_ROW.
- Only Source B products; A has NOT_AVAILABLE; no rows for A.

### 8.8 dim_shop (D5 — Source-Local Shop; TRUNCATEd; B-only MVP)

| Field | Type | Constraint | Source/Semantic |
|---|---|---|---|
| shop_sk | SERIAL | PRIMARY KEY | |
| source_sk | SMALLINT | NOT NULL REFERENCES dim_source(source_sk) | |
| source_native_shop_id | TEXT | NOT NULL | shop_id authoritative. |
| shop_observation_count | INTEGER | NOT NULL DEFAULT 0 | Rows of fact at dim build time. |

- UNIQUE(source_sk, source_native_shop_id).
- No fake unknown member. shop_id empty → REJECT_ROW.
- B only; no rows for A.

### 8.9 fact_review (F1 — Central Fact; TRUNCATEd each run; ONE_FACT_ONE_GRAIN)

| Field | Type | Constraint | Source/Semantic |
|---|---|---|---|
| review_sk | BIGSERIAL | PRIMARY KEY | Internal only. |
| source_sk | SMALLINT | NOT NULL REFERENCES dim_source(source_sk) | Resolved by source_id lookup ONLY (never hardcoded 1/2). |
| source_native_row_hash | TEXT | NOT NULL | §16 hash: SHA256(source_id + "\|" + source_file_sha256 + "\|" + LPAD(stable_source_row_number, 7, '0')). WAREHOUSE_INTERNAL / NOT_LINKABLE. |
| source_row_number | INTEGER | NOT NULL | 1-based stable row number. |
| source_file_sha256 | TEXT | NOT NULL | The raw source file SHA attached for lineage. |
| rating_sk | SMALLINT | NOT NULL REFERENCES dim_rating(rating_sk) | |
| rating_value | SMALLINT | NOT NULL CHECK (rating_value BETWEEN 1 AND 5) | Denormalized ordinal for easier queries + defensive constraint. |
| category_sk | INTEGER | NOT NULL REFERENCES dim_category(category_sk) | |
| product_sk | INTEGER | NULLABLE REFERENCES dim_product(product_sk) | **NULL for A; MUST NOT NULL for accepted B rows (enforced PRE-COMMIT CRITICAL per §19).** |
| shop_sk | INTEGER | NULLABLE REFERENCES dim_shop(shop_sk) | **NULL for A; MUST NOT NULL for accepted B rows (PRE-COMMIT CRITICAL per §19).** |
| review_text | TEXT | NOT NULL | Standardized review text (collapse excessive newlines only; never tokenize/stem/clean in ETL). |
| review_text_len_chars | INTEGER | NOT NULL | Character count informational. |
| source_gold_sentiment_label | TEXT | NULLABLE CHECK (source_gold_sentiment_label IN ('Positive','Negative') OR source_gold_sentiment_label IS NULL) | NON-NULL for A ONLY. MUST be NULL for B PRE-COMMIT CRITICAL §12. |
| source_gold_emotion_label | TEXT | NULLABLE CHECK (source_gold_emotion_label IN ('Happy','Sadness','Fear','Love','Anger') OR source_gold_emotion_label IS NULL) | NON-NULL for A ONLY; MUST NULL B. PRE-COMMIT CRITICAL §12. |
| source_a_location_text | TEXT | NULLABLE | Source A contextual only; MUST NULL B. |
| source_a_product_name_text | TEXT | NULLABLE | Source A Product Name textual only; NOT a business key; MUST NULL B. |
| source_a_price_text | TEXT | NULLABLE | Source A Price textual only; MUST NULL B. |
| source_a_overall_rating_text | TEXT | NULLABLE | Source A Overall Rating contextual only; MUST NULL B. |
| source_a_number_sold_text | TEXT | NULLABLE | Source A Number Sold contextual; MUST NULL B. |
| source_a_total_review_text | TEXT | NULLABLE | Source A Total Review contextual; MUST NULL B. |
| source_b_product_name | TEXT | NULLABLE | Source B native product_name textual ONLY; MUST NULL A. |
| source_b_sold_raw_text | TEXT | NULLABLE | Source B sold raw text; MUST NULL A. Never parse/interpret. |
| source_b_product_url | TEXT | NULLABLE | Source B product_url; MUST NULL A. |
| is_synthetic | BOOLEAN | NOT NULL DEFAULT FALSE | **MUST FALSE for every Phase 6 row.** Any TRUE row = PRE-COMMIT CRITICAL §12 BLOCK_LOAD. |
| pipeline_run_id | UUID | NOT NULL REFERENCES pipeline_run(pipeline_run_id) | Run that loaded this fact row. |
| ingested_at | TIMESTAMPTZ | NOT NULL | TECHNICAL_METADATA only. Start of extract for the source batch. |
| processed_at | TIMESTAMPTZ | NOT NULL | TECHNICAL_METADATA only. End of transform. ≥ ingested_at. |
| loaded_at | TIMESTAMPTZ | NOT NULL | TECHNICAL_METADATA only. Default NOW() on insert. ≥ processed_at. |

- **Natural/Unique defensive UNIQUE(source_sk, source_native_row_hash).** Defensive only per §17. Not a second idempotency strategy.
- CHECK constraints per Source isolation: Use DQ for business rules. Constraints are defensive only; do NOT hardcode source_sk values.
- FK indexes: create on category_sk, product_sk, shop_sk, rating_sk, source_sk, pipeline_run_id. Composite (source_sk, rating_value) for analytics.

---

## 9. SOURCE-TO-TARGET (S2T) MAPPING REGISTER (§28 Mandate)

Every target field in the 9 physical tables above has: target_table + target_field + source + transformation + null_rule + DQ_rule + lineage_class.

### Legend: lineage_class
- SOURCE_DERIVED = value comes from raw source evidence
- SOURCE_JOIN = value derived via join lookup against dimension
- DOMAIN_DERIVED = value from standard domain (ratings 1..5)
- GOVERNANCE_REGISTER_DERIVED = value from metadata/manifest
- SYSTEM_GENERATED = value generated by ETL orchestrator / database

### 9.1 dim_source S2T (seeded)
All fields GOVERNANCE_REGISTER_DERIVED except SK (SYSTEM_GENERATED). source_id matches data_sources.yaml.

### 9.2 dim_rating S2T (seeded)
rating_value 1..5 DOMAIN_DERIVED; SK SYSTEM_GENERATED. 5 rows only.

### 9.3 dim_category S2T (built per run)
| target_table | target_field | source/source_field | transformation | null_rule | DQ_rule | lineage_class |
|---|---|---|---|---|---|---|
| dim_category | source_sk | data_sources.yaml source_id → dim_source lookup | SELECT source_sk FROM dim_source WHERE source_id = %s | NOT NULL | Unresolved source → CRIT | SOURCE_JOIN |
| dim_category | source_native_category | Source A: Category; Source B: category | .strip() exact | NOT NULL; empty → REJECT_ROW | DQ-INPUT-CAT MAJOR | SOURCE_DERIVED |
| dim_category | category_value_count_observations | count(fact rows per group) | COUNT(*) group by source, category | NOT NULL default 0 | INFO only | SOURCE_DERIVED aggregate |

### 9.4 dim_product S2T (built per run; B only)
| target_field | source | transformation | null_rule | DQ_rule | lineage_class |
|---|---|---|---|---|---|
| source_sk | source_id → dim_source lookup | via SELECT | NOT NULL | Unresolved → CRIT | SOURCE_JOIN |
| source_native_product_id | B product_id | .strip() | NOT NULL; empty → REJECT_ROW | DQ-INPUT-PROD-B MAJOR | SOURCE_DERIVED |
| source_native_product_name | B product_name | §20: group by product_id, non-null; most frequent; tie-break = lowest source_row_number | NULLABLE | INFO variant_count | SOURCE_DERIVED deduped |
| product_name_variant_count | B product_name variants per product_id | COUNT(DISTINCT non-null product_name) per group | NOT NULL default 1 | §20 MAJOR INFO warn if > 1 | SOURCE_DERIVED aggregate |

### 9.5 dim_shop S2T (B only)
| target_field | source | transformation | null_rule | DQ_rule | lineage_class |
|---|---|---|---|---|---|
| source_sk | source_id lookup | | NOT NULL | CRIT | SOURCE_JOIN |
| source_native_shop_id | B shop_id | .strip() | NOT NULL; empty → REJECT_ROW | DQ-INPUT-SHOP-B MAJOR | SOURCE_DERIVED |

### 9.6 fact_review S2T (core grain row)
| target_field | source/source_field | transformation | null_rule | DQ_rule | lineage_class |
|---|---|---|---|---|---|
| source_sk | source_id → SELECT source_sk FROM dim_source WHERE source_id = %s | Resolve in Python via dict map after dims seeded | NOT NULL | CRIT if unresolved | SOURCE_JOIN |
| source_native_row_hash | source_id + source_file_sha256 + stable row number | SHA256 (see §16 formula) | NOT NULL | DQ-TR-HASH-001 MAJOR if reproducibility fails on 10% sample | SYSTEM_GENERATED deterministic |
| source_row_number | DictReader enumeration 1-based | int | NOT NULL | INFO verify sequential per source | SYSTEM_GENERATED |
| source_file_sha256 | manifest SHA | Attached per source | NOT NULL | DQ-INTEGRITY-001 CRIT vs manifest pre+post | GOVERNANCE_REGISTER_DERIVED |
| rating_sk | rating_value → dim_rating lookup | | NOT NULL | unresolved = REJECT_ROW | SOURCE_JOIN |
| rating_value | A: Customer Rating; B: rating string | A: int(x); B: int(x.strip()) | NOT NULL ∈1..5 | DQ-INPUT-RATING-001/002 MAJOR → REJECT_ROW; CHECK constraint defensive | SOURCE_DERIVED cast |
| category_sk | (source_sk, source_native_category) → dim_category | Natural key join | NOT NULL | empty category → REJECT_ROW; unresolved FK → REJECT_ROW; PRE-COMMIT orphan = 0 CRIT | SOURCE_JOIN |
| product_sk | B: (source_sk, source_native_product_id) → dim_product | Natural key join | A = NULL always; B = NON-NULL required for accepted rows | A NOT NULL → PRE-COMMIT CRIT. B NULL → PRE-COMMIT CRITICAL §19 BLOCK_LOAD. | SOURCE_JOIN |
| shop_sk | B: (source_sk, source_native_shop_id) → dim_shop | Natural key join | A = NULL always; B = NON-NULL required | A NOT NULL → PRE-COMMIT CRIT. B NULL → PRE-COMMIT CRITICAL §19 BLOCK_LOAD. | SOURCE_JOIN |
| review_text | A: Customer Review; B: text | .strip(); collapse (multiple \n → single) if contains 3+ consecutive newlines; never remove punctuation / stopwords | NOT NULL non-empty | DQ-INPUT-TEXT-001 MAJOR → REJECT_ROW. DQ-TR-NORM-001 INFO count normalized. | SOURCE_DERIVED |
| review_text_len_chars | LEN(review_text) | len() | NOT NULL ≥1 | INFO | SYSTEM_GENERATED |
| source_gold_sentiment_label | A: Sentiment | | A NON-NULL (∈{Positive,Negative}); B NULL enforced DQ + defensive CHECK | B non-NULL → PRE-COMMIT CRIT §12. | SOURCE_DERIVED |
| source_gold_emotion_label | A: Emotion | | A NON-NULL (5-class); B NULL | B non-NULL → PRE-COMMIT CRIT §12. | SOURCE_DERIVED |
| source_a_location_text, source_a_product_name_text, source_a_price_text, source_a_overall_rating_text, source_a_number_sold_text, source_a_total_review_text | A: Location, Product Name, Price, Overall Rating, Number Sold, Total Review | exact strip | A NULLABLE; B MUST NULL always | B populated → PRE-COMMIT CRIT cross-source leakage | SOURCE_DERIVED contextual |
| source_b_product_name, source_b_sold_raw_text, source_b_product_url | B: product_name, sold, product_url | exact strip sold → NULL if empty/whitespace | B NULLABLE; A MUST NULL | A populated → PRE-COMMIT CRIT cross-source leakage | SOURCE_DERIVED contextual |
| is_synthetic | configuration constant | FALSE literal | NOT NULL | Any TRUE → PRE-COMMIT CRITICAL §12 BLOCK_LOAD. | SYSTEM_GENERATED |
| pipeline_run_id | orchestrator run UUID | | NOT NULL | FK → pipeline_run defensive | SYSTEM_GENERATED |
| ingested_at, processed_at, loaded_at | ETL clock (UTC) | | NOT NON-NULL; processed_at ≥ ingested_at; loaded_at ≥ processed_at | 100% ordering required; PRE-COMMIT CRIT any violation | SYSTEM_GENERATED — TECHNICAL METADATA (NOT review timestamps) |

### 9.7 Zero Unexplained Fields Assertion (§28)

All target fields in all 9 tables are enumerated above with complete 7-tuple S2T mapping.

```
UNEXPLAINED_WAREHOUSE_FIELDS = 0
```

---

## 10. ETL DESIGN (DEL-09)

### 10.1 Flow Diagram

```
EXTRACT → INPUT_VALIDATION → STANDARDIZE → TRANSFORM → PRE_LOAD_AUDIT → 3-TRANSACTION LOAD MODEL → RECONCILE → REPORT
  │         │                  │             │              │                    │                                  │         │
  │         │                  │             │              │                    ├──TX-A: pipeline_run STARTED + COMMIT (independent)
  │         │                  │             │              │                    │
  │         │                  │             │              │                    ├──TX-B (warehouse refresh):
  │         │                  │             │              │                    │   BEGIN
  │         │                  │             │              │                    │   TRUNCATE dim_category/dim_product/dim_shop/fact_review RESTART IDENTITY CASCADE
  │         │                  │             │              │                    │   INSERT dims (category/product/shop)
  │         │                  │             │              │                    │   BATCH INSERT fact_review
  │         │                  │             │              │                    │   RUN ALL PRE-COMMIT CRITICAL CHECKS §12 (inside TX-B before COMMIT)
  │         │                  │             │              │                    │   IF ANY FAIL → ROLLBACK TX-B
  │         │                  │             │              │                    │   IF ALL PASS → COMMIT TX-B
  │         │                  │             │              │                    │
  │         │                  │             │              │                    └──TX-C (independent):
  │         │                  │             │              │                        UPDATE pipeline_run.status = SUCCESS/FAILED + counters
  │         │                  │             │              │                        COMMIT (always, so audit survives)
  │         │                  │             │              │
  │         │                  │             │              └─ DQ results + rejections INSERTED in separate TXs so they survive TX-B rollback per §11/§13.
  │         │                  │             └─ Build dimension rows from distinct; attach SK lookups in-memory via Python dict after SELECTs; fact S2T field alignment; hash §16.
  │         │                  └─ Column rename snake_case; UTF-8 strict decode; rating cast; null normalization; review_text minimal clean.
  │         └─ File existence; SHA pre-read; schema match; row count exact; rating domain sample; SHA post-read recheck.
  └─ Open file read-only (mode='r'); no write handle; stdlib csv.DictReader utf-8 strict; produce rows list.
```

### 10.2 Staging (§8: Python In-Memory Dict-List Only)

Stdlib csv.DictReader → list[dict]. All transformation in Python memory.

| Staging structure | Contents | Equivalent conceptual stage |
|---|---|---|
| `staging_a_rows : list[dict]` | 5,400 dict rows from A CSV | Raw A (in-memory only) |
| `staging_b_rows : list[dict]` | 40,607 dict rows from B CSV | Raw B (in-memory only) |
| `standardized_a_rows` | After INPUT VAL + STD: snake_case, row_number 1-based, source_id attached, file_sha attached, per-row DQ reject list | Standardized A |
| `standardized_b_rows` | Same | Standardized B |
| `transformed_dim_rows` | dict of lists: dim_category_a, dim_category_b, dim_product, dim_shop (distinct + product variant tie-break rule §20 applied) | Dimension candidates |
| `transformed_fact_rows` | list[dict] — 46,007 (minus rejections) candidate fact rows with all target column names + values aligned; SK placeholders resolved after dimension SELECTs | Fact candidates |

- **No DB staging tables.** 46K rows trivial for in-memory (10-20 MB peak).
- **No Pandas added.** Stdlib only.
- **No separate CSV written to disk during ETL.** All in-memory until final load.

### 10.3 Extract

Contract:
1. **Input:** `config/project_settings.yaml → paths.data_raw` + `config/data_sources.yaml → source_{a,b}.local_path` + `data/metadata/source_manifest.csv` (SHA + row_count + column_count canonical)
2. **Actions:**
   1. Verify each source file exists. Missing → DQ-INTEGRITY-000 CRITICAL → BLOCK_LOAD.
   2. **SHA256 pre-ETL:** Compute streaming hashlib.sha256 of each raw file. Compare to source_manifest.csv manifest_sha256. Mismatch → DQ-INTEGRITY-001 CRITICAL → BLOCK_LOAD.
   3. Open file read-only (mode='r' NEVER 'w'/'a') with encoding='utf-8' STRICTEST: NO `errors="replace"`. Any UnicodeDecodeError → DQ-INTEGRITY-004 CRITICAL BLOCK_LOAD per §21.
   4. Read header row; compare DictReader keys to `official_columns` from `data_sources.yaml`. Column superset required (all official exist). Missing official cols → DQ-INTEGRITY-003 CRIT. Extra columns present → MAJOR warn only (not blocking).
   5. Read all rows with DictReader. Record 1-based stable source_row_number per row (linearly incremented, including rejected rows).
   6. Exact row count vs. manifest row_count. Mismatch → DQ-INTEGRITY-002 CRIT BLOCK_LOAD.
   7. **SHA256 post-ETL:** After read completes (cursor exhausted), recompute streaming SHA of each source file again to detect OS-level concurrent modification during read. Mismatch pre/post → DQ-INTEGRITY-006 CRIT BLOCK_LOAD per §26.
3. **Validation:** DQ-INTEGRITY-000..006.

### 10.4 Input Validation (Per-Row Stage)

Rejects here → inserted into rejected_record_log in separate commit (independent of TX-B so survives rollback).

| DQ Rule | Scope | Severity | Action | Checks |
|---|---|---|---|---|
| DQ-INPUT-RATING-001 | Source A row | MAJOR per bad row | REJECT_ROW | Customer Rating: non-null; castable to int; ∈1..5 |
| DQ-INPUT-RATING-002 | Source B row | MAJOR per bad row | REJECT_ROW | rating string: non-empty after strip; castable to int; ∈1..5 |
| DQ-INPUT-TEXT-001 | Both A/B row | MAJOR per bad row | REJECT_ROW | review_text.strip() non-empty length > 0 |
| DQ-INPUT-LABEL-A-SENT-001 | Source A row | MAJOR per bad row | REJECT_ROW | sentiment ∈ {Positive, Negative} |
| DQ-INPUT-LABEL-A-EMO-001 | Source A row | MAJOR per bad row | REJECT_ROW | emotion ∈ {Happy, Sadness, Fear, Love, Anger} |
| DQ-INPUT-PROD-B-001 | Source B row | MAJOR per bad row | REJECT_ROW | product_id non-empty after strip |
| DQ-INPUT-SHOP-B-001 | Source B row | MAJOR per bad row | REJECT_ROW | shop_id non-empty after strip |
| DQ-INPUT-CAT-001 | Both row | MAJOR per bad row | REJECT_ROW | category non-empty after strip |
| DQ-INPUT-LABEL-B-LEAKAGE | Source B run-wide (header scan) | CRITICAL | BLOCK_LOAD before TX starts | Ensure raw B CSV has NO sentiment/emotion gold columns (prevents accidental future B label contamination). header match check. |

### 10.5 Standardize

Column rename + lightweight normalization. Never invents meaning.

**Source A raw → Standardized:**
Category → category_raw; Product Name → product_name_raw; Location → location_raw; Price → price_raw; Overall Rating → overall_rating_raw; Number Sold → number_sold_raw; Total Review → total_review_raw; Customer Rating → customer_rating_raw (cast to int rating_value); Customer Review → customer_review_raw → review_text; Sentiment → sentiment_raw → source_gold_sentiment_label; Emotion → emotion_raw → source_gold_emotion_label.

**Source B raw → Standardized:**
text → text_raw → review_text; rating → rating_raw → int rating_value; category → category_raw; product_name → product_name_raw → source_native_product_name; product_id → product_id_raw → source_native_product_id; sold → sold_raw → source_b_sold_raw_text (empty/whitespace = None); shop_id → shop_id_raw → source_native_shop_id; product_url → product_url_raw → source_b_product_url.

**Whitespace rule (per plan v1.0 empirically validated, no change in v1.1):**
- review_text: strip; collapse 2+ consecutive newlines to 1. Log count of rows where text changed (INFO).
- category_raw / product_id_raw / shop_id_raw / source_native_product_name / source_native_shop_id: .strip() only (both ends).
- NEVER remove punctuation / stopwords / lowercase in ETL (that is Phase 8 ML preprocessing under experiment_settings.yaml duplicate_policy governance; not global warehouse).

### 10.6 Transform (Build Dimension Candidates + Fact Rows)

1. **dim_category candidates:** distinct (source_id, category_raw) from each standardized source.
2. **dim_product candidates (Source B only):**
   - Group by source_native_product_id
   - Collect non-null product_name_raw values → count frequencies
   - Choose **most frequent** product_name_raw per §20
   - **Tie-break §20:** If tie, choose the product_name_raw appearing at lowest stable source_row_number
   - Compute product_name_variant_count = COUNT(DISTINCT non-null product_name_raw per product_id)
   - **Never merge products by name.** product_id authoritative.
3. **dim_shop candidates (B only):** distinct (source_native_shop_id)
4. **fact_review candidates (1 per accepted standardized row after INPUT VAL + reject removal):**
   - Per §16 compute: `source_native_row_hash = SHA256(source_id + "|" + source_file_sha256 + "|" + LPAD(str(stable_source_row_number), 7, '0')).hexdigest()`
   - **Classification: WAREHOUSE_INTERNAL / NOT_LINKABLE.** NEVER use for cross-source matching / customer identity / product identity / entity reconciliation.
   - Attach source_file_sha256 (for lineage)
   - Attach source_row_number
   - Attach source_id (for source_sk lookup later after dim_source SELECT)
   - Attach rating_value (already int)
   - Attach category_raw (for category_sk lookup later)
   - Attach product_id_raw (B only; for product_sk lookup later). Set to None for A explicitly.
   - Attach shop_id_raw (B only; for shop_sk lookup later). Set to None for A explicitly.
   - Attach review_text + review_text_len_chars = len(review_text)
   - Attach A gold labels (A only, B=None explicitly)
   - Attach A 6 contextual fields (A only; B=None explicitly)
   - Attach B 3 contextual fields (B only; A=None explicitly)
   - **is_synthetic = False constant** (literal)
   - ingested_at = source-batch extract start (UTC) — same for entire source batch; processed_at = end of transform (UTC) per each row (or same for entire batch; ensure ≥ ingested_at)
   - Determinism: lineage hash / source_native_* / rating / labels: 100% deterministic given same bytes. UTC timestamps are wall-clock; not deterministic but clearly TECHNICAL_METADATA.

### 10.7 Load: Three-Transaction Model (§11 Mandatory Fix — CRITICAL)

**TX-A: Audit Start (independent transaction — must survive any warehouse rollback)**
```python
conn = psycopg.connect(...)
conn.autocommit = False
with conn.cursor() as cur:
    cur.execute("""
        INSERT INTO pipeline_run (pipeline_run_id, started_at, status, pipeline_version,
            source_a_file_sha256, source_b_file_sha256,
            source_a_rows_manifest, source_b_rows_manifest,
            source_a_rows_read, source_b_rows_read,
            input_rows_total, accepted_rows_total, rejected_rows_total)
        VALUES (%s, NOW() AT TIME ZONE 'UTC', 'STARTED', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (run_id, PIPELINE_VERSION,
          sha_a, sha_b,
          manifest_a_rows, manifest_b_rows,
          read_a_rows, read_b_rows,
          read_a_rows + read_b_rows, accepted_rows_total, rejected_rows_total))
conn.commit()  # MUST COMMIT TX-A BEFORE TX-B starts. Ensures pipeline_run STARTED survives any TX-B ROLLBACK.
```

**TX-B: Warehouse Refresh Transaction. All PRE-COMMIT CRITICAL CHECKS MUST RUN INSIDE TX-B BEFORE COMMIT.**
```python
try:
    with conn.cursor() as cur:
        # Only truncate DYNAMIC ANALYTICAL 4 tables (§13). Never truncate 3 audit tables or dim_source/dim_rating.
        cur.execute("TRUNCATE TABLE marketvoice_warehouse.dim_category, marketvoice_warehouse.dim_product, marketvoice_warehouse.dim_shop, marketvoice_warehouse.fact_review RESTART IDENTITY CASCADE;")

        # Seed static dims defensively (should already exist; ON CONFLICT DO NOTHING defensive per idempotency).
        _seed_dim_source(cur)
        _seed_dim_rating(cur)

        # Get source_sk map via CANONICAL LOOKUP BY SOURCE_ID ONLY (NEVER hardcode 1/2):
        cur.execute("SELECT source_id, source_sk FROM marketvoice_warehouse.dim_source")
        source_sk_by_source_id = {row[0]: row[1] for row in cur.fetchall()}
        for sid in ('SRC_PRDECT_ID_V1','SRC_TOKOPEDIA_REVIEWS_2019'):
            if sid not in source_sk_by_source_id:
                raise CriticalError(f"source {sid} missing from dim_source — seed failed")

        # Lookup rating_sk map:
        cur.execute("SELECT rating_value, rating_sk FROM marketvoice_warehouse.dim_rating")
        rating_sk_by_value = {r[0]: r[1] for r in cur.fetchall()}

        # INSERT dim_category, then SELECT to build (source_id, cat) → category_sk map
        _batch_insert_dim_category(cur, dim_category_rows, source_sk_by_source_id)
        cat_sk_map = _query_category_sk_map(cur, source_sk_by_source_id)

        # INSERT dim_product → SELECT (source_id, product_id) → product_sk map
        _batch_insert_dim_product(cur, dim_product_rows, source_sk_by_source_id)  # B only
        prod_sk_map = _query_product_sk_map(cur, source_sk_by_source_id)  # B only

        # INSERT dim_shop → SELECT (source_id, shop_id) → shop_sk map
        _batch_insert_dim_shop(cur, dim_shop_rows, source_sk_by_source_id)
        shop_sk_map = _query_shop_sk_map(cur, source_sk_by_source_id)

        # Now resolve all SKs in fact candidate rows IN-MEMORY:
        for fact_row in candidate_fact_rows:
            sid = fact_row['source_id']
            fact_row['source_sk'] = source_sk_by_source_id[sid]
            # rating_sk:
            rv = fact_row['rating_value']
            if rv not in rating_sk_by_value:
                raise CriticalError(f"rating_value {rv} missing in dim_rating (should have been caught INPUT val)")
            fact_row['rating_sk'] = rating_sk_by_value[rv]
            # category_sk from map (must exist because dimension built from same rows)
            key = (sid, fact_row['category_raw'])
            if key not in cat_sk_map:
                raise CriticalError(f"category_sk unresolved for {key}")
            fact_row['category_sk'] = cat_sk_map[key]
            # product_sk
            if sid == 'SRC_PRDECT_ID_V1':
                fact_row['product_sk'] = None  # §19 Source A MUST NULL
            else:
                pk = (sid, fact_row.get('source_native_product_id'))
                if pk not in prod_sk_map or prod_sk_map[pk] is None:
                    raise CriticalError(f"product_sk unresolved for Source B key={pk} — §19 violation B FK MUST resolve")
                fact_row['product_sk'] = prod_sk_map[pk]
            # shop_sk
            if sid == 'SRC_PRDECT_ID_V1':
                fact_row['shop_sk'] = None  # §19 A MUST NULL
            else:
                sk_key = (sid, fact_row.get('source_native_shop_id'))
                if sk_key not in shop_sk_map:
                    raise CriticalError(f"shop_sk unresolved for Source B key={sk_key} — §19 violation B FK MUST resolve")
                fact_row['shop_sk'] = shop_sk_map[sk_key]
            # pipeline_run_id / loaded_at set during insert
            fact_row['pipeline_run_id'] = run_id
        # End for.

        # BATCH INSERT fact_review via executemany or prepared statement:
        _batch_insert_fact_review(cur, candidate_fact_rows)

        # ============================================================
        # §12 PRE-COMMIT CRITICAL CHECKS (ALL INSIDE TX-B BEFORE COMMIT)
        # ============================================================
        # Any non-zero result → raise CriticalCheckFailed → ROLLBACK
        pre_commit_failures = []
        pre_commit_checks = [
            ("C01-A-PRODUCT-LINKAGE-ZERO",
             "SELECT COUNT(*) FROM marketvoice_warehouse.fact_review f JOIN marketvoice_warehouse.dim_source s ON f.source_sk=s.source_sk WHERE s.source_id='SRC_PRDECT_ID_V1' AND f.product_sk IS NOT NULL",
             0),
            ("C02-A-SHOP-LINKAGE-ZERO",
             "SELECT COUNT(*) FROM marketvoice_warehouse.fact_review f JOIN marketvoice_warehouse.dim_source s ON f.source_sk=s.source_sk WHERE s.source_id='SRC_PRDECT_ID_V1' AND f.shop_sk IS NOT NULL",
             0),
            ("C03-B-SENTIMENT-LEAKAGE-ZERO",
             "SELECT COUNT(*) FROM marketvoice_warehouse.fact_review f JOIN marketvoice_warehouse.dim_source s ON f.source_sk=s.source_sk WHERE s.source_id='SRC_TOKOPEDIA_REVIEWS_2019' AND f.source_gold_sentiment_label IS NOT NULL",
             0),
            ("C04-B-EMOTION-LEAKAGE-ZERO",
             "SELECT COUNT(*) FROM marketvoice_warehouse.fact_review f JOIN marketvoice_warehouse.dim_source s ON f.source_sk=s.source_sk WHERE s.source_id='SRC_TOKOPEDIA_REVIEWS_2019' AND f.source_gold_emotion_label IS NOT NULL",
             0),
            ("C05-SYNTHETIC-ZERO",
             "SELECT COUNT(*) FROM marketvoice_warehouse.fact_review WHERE is_synthetic IS TRUE",
             0),
            ("C06-INVALID-RATING-ZERO",
             "SELECT COUNT(*) FROM marketvoice_warehouse.fact_review WHERE rating_value NOT BETWEEN 1 AND 5",
             0),
            ("C07-FK-ORPHAN-ZERO-category",
             "SELECT COUNT(*) FROM marketvoice_warehouse.fact_review WHERE category_sk NOT IN (SELECT category_sk FROM marketvoice_warehouse.dim_category)",
             0),
            ("C08-FK-ORPHAN-ZERO-product",
             "SELECT COUNT(*) FROM marketvoice_warehouse.fact_review WHERE product_sk IS NOT NULL AND product_sk NOT IN (SELECT product_sk FROM marketvoice_warehouse.dim_product)",
             0),
            ("C09-FK-ORPHAN-ZERO-shop",
             "SELECT COUNT(*) FROM marketvoice_warehouse.fact_review WHERE shop_sk IS NOT NULL AND shop_sk NOT IN (SELECT shop_sk FROM marketvoice_warehouse.dim_shop)",
             0),
            ("C10-FK-ORPHAN-ZERO-rating",
             "SELECT COUNT(*) FROM marketvoice_warehouse.fact_review WHERE rating_sk NOT IN (SELECT rating_sk FROM marketvoice_warehouse.dim_rating)",
             0),
            ("C11-FK-ORPHAN-ZERO-source",
             "SELECT COUNT(*) FROM marketvoice_warehouse.fact_review WHERE source_sk NOT IN (SELECT source_sk FROM marketvoice_warehouse.dim_source)",
             0),
            ("C12-DUPLICATE-FACT-NATURAL-KEY-ZERO",
             "SELECT COUNT(*) FROM (SELECT source_sk, source_native_row_hash, COUNT(*) c FROM marketvoice_warehouse.fact_review GROUP BY 1,2 HAVING COUNT(*)>1) dups",
             0),
            ("C13-B-PRODUCT-FK-MUST-RESOLVE (§19)",
             "SELECT COUNT(*) FROM marketvoice_warehouse.fact_review f JOIN marketvoice_warehouse.dim_source s ON f.source_sk=s.source_sk WHERE s.source_id='SRC_TOKOPEDIA_REVIEWS_2019' AND f.product_sk IS NULL",
             0),
            ("C14-B-SHOP-FK-MUST-RESOLVE (§19)",
             "SELECT COUNT(*) FROM marketvoice_warehouse.fact_review f JOIN marketvoice_warehouse.dim_source s ON f.source_sk=s.source_sk WHERE s.source_id='SRC_TOKOPEDIA_REVIEWS_2019' AND f.shop_sk IS NULL",
             0),
            ("C15-TECHTS-ORDERING-100PCT",
             "SELECT COUNT(*) FROM marketvoice_warehouse.fact_review WHERE NOT (ingested_at <= processed_at AND processed_at <= loaded_at)",
             0),
            ("C16-COUNT-A-RECONCILE",
             "SELECT COUNT(*) FROM marketvoice_warehouse.fact_review f JOIN marketvoice_warehouse.dim_source s ON f.source_sk=s.source_sk WHERE s.source_id='SRC_PRDECT_ID_V1'",
             read_a_rows - rejected_a_rows),
            ("C17-COUNT-B-RECONCILE",
             "SELECT COUNT(*) FROM marketvoice_warehouse.fact_review f JOIN marketvoice_warehouse.dim_source s ON f.source_sk=s.source_sk WHERE s.source_id='SRC_TOKOPEDIA_REVIEWS_2019'",
             read_b_rows - rejected_b_rows),
            ("C18-INPUT-EQUALS-ACCEPTED-PLUS-REJECTED-A",
             None,
             True if read_a_rows == accepted_a_rows + rejected_a_rows else False),
            ("C19-INPUT-EQUALS-ACCEPTED-PLUS-REJECTED-B",
             None,
             True if read_b_rows == accepted_b_rows + rejected_b_rows else False),
        ]

        for check_id, sql_or_none, expected in pre_commit_checks:
            if sql_or_none is None:
                actual = expected
                passed = (actual is True)
                actual_val = str(actual)
                expected_val = "True"
            else:
                cur.execute(sql_or_none)
                actual_val_int = cur.fetchone()[0]
                passed = (actual_val_int == expected)
                actual_val = str(actual_val_int)
                expected_val = str(expected)
            # Record check result to local list; will write dq_result in separate transaction after TX-B
            pre_commit_results.append((check_id, 'CRITICAL' if check_id.startswith('C') else 'MAJOR', passed, actual_val, expected_val))
            if not passed:
                pre_commit_failures.append((check_id, actual_val, expected_val))
        # End for pre-commit.

        if pre_commit_failures:
            raise CriticalPreCommitCheckFailed(pre_commit_failures)

    # ============================================================
    # ALL PRE-COMMIT PASSED → COMMIT TX-B
    # ============================================================
    conn.commit()
    tx_b_committed = True

except (Exception, CriticalPreCommitCheckFailed) as tx_err:
    conn.rollback()  # ROLLBACK TX-B (prevents partial warehouse state)
    tx_b_committed = False
    tx_b_error = str(tx_err)
```

**TX-C: Audit Finalization (independent transaction — ALWAYS committed so audit persists even if TX-B rolled back per §11)**

```python
try:
    with conn.cursor() as cur:
        if tx_b_committed:
            # Get actual loaded counts from committed warehouse:
            cur.execute("SELECT COUNT(*) FROM marketvoice_warehouse.fact_review f JOIN marketvoice_warehouse.dim_source s ON f.source_sk=s.source_sk WHERE s.source_id='SRC_PRDECT_ID_V1'")
            loaded_a = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM marketvoice_warehouse.fact_review f JOIN marketvoice_warehouse.dim_source s ON f.source_sk=s.source_sk WHERE s.source_id='SRC_TOKOPEDIA_REVIEWS_2019'")
            loaded_b = cur.fetchone()[0]
            cur.execute("""
                UPDATE pipeline_run SET
                    status='SUCCESS',
                    completed_at = NOW() AT TIME ZONE 'UTC',
                    loaded_rows_total = %s,
                    source_a_rows_loaded = %s,
                    source_b_rows_loaded = %s,
                    critical_dq_fails = %s,
                    major_dq_fails = %s,
                    notes = COALESCE(notes || '
TX-B SUCCESS. ','TX-B SUCCESS. ') || %s
                WHERE pipeline_run_id = %s
            """, (loaded_a + loaded_b, loaded_a, loaded_b,
                  sum(1 for (_, sev, p, *_ in pre_commit_results) if sev=='CRITICAL' and not p),
                  sum(1 for (_, sev, p, *_ in pre_commit_results) if sev=='MAJOR' and not p),
                  f"Loaded {loaded_a+loaded_b} rows. A={loaded_a}, B={loaded_b}. Rejects A={rejected_a_rows}, B={rejected_b_rows}.",
                  run_id))
        else:
            cur.execute("""
                UPDATE pipeline_run SET
                    status='FAILED',
                    completed_at = NOW() AT TIME ZONE 'UTC',
                    loaded_rows_total = 0,
                    source_a_rows_loaded = 0,
                    source_b_rows_loaded = 0,
                    critical_dq_fails = GREATEST(critical_dq_fails, 1),
                    notes = COALESCE(notes || '
TX-B ROLLBACK. ','TX-B ROLLBACK. ') || %s
                WHERE pipeline_run_id = %s
            """, (tx_b_error[:2000], run_id))
    conn.commit()  # ALWAYS COMMIT TX-C regardless of TX-B result.
finally:
    # Always INSERT rejected_record_log + data_quality_result rows in SEPARATE TX(s),
    # so they persist regardless of TX-B outcome per §13.
    _write_rejected_records(conn, run_id, rejections_list)
    _write_dq_results(conn, run_id, all_check_results + pre_commit_results)
```

### 10.8 Post-Commit Forensic Validation (NOT ROLLBACK-able — §12)

After TX-B + TX-C are done, run POST-LOAD forensic checks ONLY for reporting. They cannot roll back already committed transactions per §12:

1. Count per source + rating distribution → write to DQ results INFO.
2. SHA256 of raw source files recomputed third time to finalize evidence of RAW DATA integrity → compare to pre-ETL SHA → INFO (post-commit only; cannot rollback but flags any OS-level concurrent write issue).
3. Dimension cardinality reports (INFO only): dim_source (expect 2), dim_rating (5), dim_category (≤34), dim_product (≤3664 for B), dim_shop (≤158 for B).

### 10.9 Report

Write LOCAL_ONLY artifacts (not versioned per .gitignore logs tier):
- `logs/pipeline_report_{run_id}.json`: run_id, start/complete, status, per-source: input/accepted/rejected/loaded; per-check dq result summaries; raw file SHA computed vs stored manifest; counts; ETL version string.
- `logs/pipeline_rejections_{run_id}.json`: backup copy of rejected_record_log entries (independent forensic duplicate that survives DB issues).

---

## 11. DATA QUALITY DESIGN (DEL-10)

### 11.1 Four-Layer Coverage

```
INPUT (file/row) → TRANSFORM (value) → PRE-COMMIT (TX-B integrity) → POST_LOAD (forensic reporting)
```

### 11.2 DQ Check Roster (Complete; No arbitrary % thresholds per §18 mandate)

| DQ Check ID | Layer | Scope | Description | Severity | Action |
|---|---|---|---|---|---|
| DQ-INTEGRITY-000 | INPUT | Run | Source files exist at configured paths | CRITICAL | BLOCK_LOAD |
| DQ-INTEGRITY-001 | INPUT | Run × source | SHA256 pre-ETL = manifest SHA256 | CRITICAL | BLOCK_LOAD |
| DQ-INTEGRITY-002 | INPUT | Run × source | Exact row count = manifest row_count | CRITICAL | BLOCK_LOAD |
| DQ-INTEGRITY-003 | INPUT | Run × source | Column superset of official_columns from data_sources.yaml | CRITICAL | BLOCK_LOAD |
| DQ-INTEGRITY-004 | INPUT | Run × source | UTF-8 strict decode; NO errors | CRITICAL | BLOCK_LOAD |
| DQ-INTEGRITY-005 | INPUT | Run | All data/raw fds opened read-only; no write handles to data/raw | CRITICAL | BLOCK_LOAD |
| DQ-INTEGRITY-006 | INPUT | Run × source | SHA256 post-read = SHA256 pre-read (detect concurrent modification) | CRITICAL | BLOCK_LOAD |
| DQ-INPUT-LABEL-B-LEAKAGE | INPUT | Run × B header scan | B raw CSV has NO sentiment/emotion gold columns | CRITICAL | BLOCK_LOAD before TX-A |
| DQ-INPUT-RATING-001 | INPUT | Per row A | Customer Rating ∈ {1..5} int | MAJOR | REJECT_ROW |
| DQ-INPUT-RATING-002 | INPUT | Per row B | rating string → ∈ {1..5} int after strip/cast | MAJOR | REJECT_ROW |
| DQ-INPUT-TEXT-001 | INPUT | Per row both | review_text.strip() non-empty | MAJOR | REJECT_ROW |
| DQ-INPUT-LABEL-A-SENT-001 | INPUT | Per row A | sentiment ∈ {Positive, Negative} | MAJOR | REJECT_ROW |
| DQ-INPUT-LABEL-A-EMO-001 | INPUT | Per row A | emotion ∈ {Happy, Sadness, Fear, Love, Anger} | MAJOR | REJECT_ROW |
| DQ-INPUT-PROD-B-001 | INPUT | Per row B | product_id non-empty | MAJOR | REJECT_ROW |
| DQ-INPUT-SHOP-B-001 | INPUT | Per row B | shop_id non-empty | MAJOR | REJECT_ROW |
| DQ-INPUT-CAT-001 | INPUT | Per row both | category non-empty | MAJOR | REJECT_ROW |
| DQ-TR-NORM-001 | TRANSFORM | Run | Count of rows review_text changed by whitespace collapse (INFO only) | INFO | WARN |
| DQ-TR-HASH-001 | TRANSFORM | Run × 10% sample | Hash reproducibility: recompute 10% sample rows; must match stored hash | MAJOR | BLOCK_LOAD if any mismatch |
| DQ-TR-DIM-PROD-001 | TRANSFORM | Run | Report variant_count > 1 products; list top 5 by variant count | MAJOR | WARN (not block; variants documented not rejected) |
| DQ-PRE-C01..C19 | PRE-COMMIT | Run inside TX-B | §12.3 list of 19 critical hard checks | CRITICAL (all Cxx) | ROLLBACK TX-B + FAIL pipeline_run → BLOCK_LOAD final state = FAILED |
| DQ-POST-INFO-CARD-* | POST-LOAD | Run | Row counts / cardinalities / distributions (forensic evidence only) | INFO | WARN only. Cannot rollback committed TX per §12. |
| DQ-POST-SHA-FINAL | POST-LOAD | Run × source | Third SHA256 compute of raw bytes after load → match pre-ETL + manifest | CRITICAL (post-commit forensic marker) | Report; cannot rollback; but if FAIL → raise to RUN_STATUS=SUCCESS_WITH_CRITICAL_WARNING and record in pipeline_run.notes so gate review sees. |
| DQ-POST-RAW-TIER-READONLY | POST-LOAD | Run | Stat each raw source file mtime; confirm not modified since pre-ETL SHA. | CRITICAL (forensic marker post only) | Report |

### 11.3 Semantic Severity Matrix (§18 — NO arbitrary percent thresholds)

| Severity | Definition | Action |
|---|---|---|
| CRITICAL | Warehouse / data integrity invalid. Examples: SHA mismatch, row count mismatch, cross-source leakage (A has product_sk not null), B has sentiment labels, is_synthetic true rows, FK orphan >0, duplicate natural key >0, UTF decode fail, hash reproducibility fail, unresolved B FK for accepted rows, audit tables truncated accidentally. | **BLOCK_LOAD** — ROLLBACK if in TX-B. pipeline_run.status → FAILED. Human gate review required. 0 unresolved CRITICAL = Phase 6 PASS requirement. |
| MAJOR | Material quality issue on specific row(s). Examples: invalid rating, empty review text, invalid A gold label domain, missing B product_id/shop_id/category. Also: product_name_variant_count > 0 for high-variant products (documented). | **REJECT_ROW** (row-level MAJORs). Run-level MAJOR (documented): WARN but allow load unless it also triggers a CRITICAL integrity pre-commit check (e.g., unresolved FK after all MAJOR rejects = CRITICAL). 0 UNRESOLVED MAJOR INTEGRITY BLOCKERS required for Phase 6 PASS. (Row-rejected MAJOR issues = RESOLVED by rejection.) |
| MINOR | Non-blocking quality degradation. | WARN only. Recorded in DQ results. |
| INFO | Observation only. Examples: count of text normalize, dimension cardinalities, distribution. | No action; recorded in DQ results for forensic evidence. |

### 11.4 Phase 6 DQ Exit Criteria (§18 + §32)

PASS requires **BOTH**:
```
UNRESOLVED_CRITICAL = 0
UNRESOLVED_MAJOR_INTEGRITY_BLOCKERS = 0
```

A MAJOR row-level reject counts as RESOLVED (the bad row is removed before load). It becomes an unresolved MAJOR INTEGRITY BLOCKER only if: after all rejects, the data still violates a hard integrity rule that has no reject-path (e.g., a bug in SK resolution that loads rows with unresolved FK after the reject step, which should never happen; caught by PRE-COMMIT C07..C19 and escalated to CRITICAL anyway).

### 11.5 Never Silently Discard Records

- Every row not loaded → 1 entry in rejected_record_log with pipeline_run_id, source_id, source_row_number, stage, severity, dq_check_id, reason_code, reason_text, row_snippet.
- Reject count: logged to pipeline_run.rejected_rows_total in TX-C update, plus written to JSON backup at logs/pipeline_rejections_{run_id}.json so rejections survive DB rollback.
- accepted_rows_total + rejected_rows_total = input_rows_total (per source). Mismatch → DQ-PRE-COMMIT C18/C19 CRITICAL → ROLLBACK TX-B.

---

## 12. IDEMPOTENCY / TRANSACTION / SAFETY (§11, §13, §17, §22 mandates)

### 12.1 Idempotency Strategy: Single Canonical ONLY (§17 mandate)

```
IDEMPOTENCY_STRATEGY = TRANSACTIONAL_DETERMINISTIC_FULL_REFRESH
```

- What it means: On every pipeline run:
  1. TX-A inserts pipeline_run STARTED (COMMIT).
  2. TX-B: `TRUNCATE dim_category, dim_product, dim_shop, fact_review RESTART IDENTITY CASCADE` → rebuild dimensions from distinct candidates → load fact rows → PRE-COMMIT CHECKS → COMMIT or ROLLBACK.
  3. dim_source/dim_rating never truncated; they are seeded idempotently via INSERT ... ON CONFLICT DO NOTHING. Audit 3 tables never truncated.
- Result: same validated source bytes + same code + same run twice → final committed warehouse:
  - Same natural-key rows (source_native_* + hash + rating_value + labels + text)
  - Same business values
  - Same dimension natural-key cardinalities (≤2/5/34/3664/158)
  - Same fact cardinality per source
  - 0 duplicate natural keys (enforced by UNIQUE constraint)
  - **Note:** SERIAL/surrogate values may differ between runs (since dynamic dims are recreated), which is explicitly allowed per §17. Surrogate keys have ZERO external meaning; only natural keys + source_id are exported for lineage.
- UNIQUE (source_sk, source_native_row_hash) on fact_review remains DEFENSIVE ONLY; it prevents buggy double-insert in the same run, NOT a second idempotency strategy. Do NOT describe ETL as simultaneously "truncate/reload" and "ON CONFLICT DO NOTHING" — that's two contradictory strategies. Only full refresh is canonical.

### 12.2 Transactional Correctness Guarantees (§11 Mandate — 3-Transaction Model)

1. **TX-A Independent Commit:** pipeline_run STARTED is committed BEFORE TX-B begins. If the process crashes between TX-A and TX-B → pipeline_run visible STARTED forever. Good.
2. **TX-B Atomic:** All changes to dynamic analytical tables (truncate + dim insert + fact insert + pre-commit checks) are in the same transaction. If any error → ROLLBACK → the prior committed successful run's warehouse state remains intact (no partial overwrites, no empty tables from a failed TRUNCATE that committed).
3. **PRE-COMMIT inside TX-B:** CRITICAL checks C01..C19 run inside TX-B after inserts before COMMIT. If any non-zero → ROLLBACK. Zero partial state leak.
4. **Rejections and DQ results outside TX-B:** rejected_record_log and data_quality_result inserted in their own small commits. Even if TX-B rolls back, forensic evidence of the failed run is persisted. Audit history preserved per §13.
5. **TX-C Independent Commit:** pipeline_run SUCCESS/FAILED status committed regardless of TX-B outcome. Failed runs are 100% auditable per §11. Failed run audit persists = explicit acceptance requirement.

### 12.3 Audit History Is Sacred (§13)

**NEVER TRUNCATE these 3 historical audit tables:**
- pipeline_run
- rejected_record_log
- data_quality_result

All audit records are scoped by pipeline_run_id. A new run simply appends new rows with a new UUID. Old failed/success runs remain. This table grows unbounded at ~46000 rows/run worst case; for S2 prototype it is acceptable (manual archival out of scope for Phase 6).

### 12.4 PostgreSQL Client / Driver Safety

- Driver: psycopg[binary] v3.x installed project-local at .pipdeps (added to sys.path before import). Per §23 authorization.
- UTF-8 server encoding verified via `SHOW server_encoding;` → UTF8 REQUIRED (§21). If not UTF8 → GENUINE_EXTERNAL_BLOCKER STOP.
- Client encoding always UTF8. SET client_encoding = 'UTF8' on connect.
- No hardcoded Unix locale strings on Windows (LC_COLLATE etc.). Use default.

### 12.5 Test DB Destructive-Action Guard (§22)

Before ANY DROP SCHEMA / DROP DATABASE / TRUNCATE against audit tables (defensive — code should never do it), a guard checks:

```python
def assert_safe_destructive(conn: psycopg.Connection, expected_env: str, expected_db_name: str, operation: str):
    env = os.environ.get('MARKETVOICE_ENV', 'dev')
    if env != expected_env:
        raise UnsafeDatabaseError(f"Refusing {operation}: MARKETVOICE_ENV={env} != expected {expected_env}")
    with conn.cursor() as cur:
        cur.execute("SELECT current_database()")
        actual_db = cur.fetchone()[0]
    if actual_db != expected_db_name:
        raise UnsafeDatabaseError(f"Refusing {operation}: current_database()={actual_db} != expected {expected_db_name}")
```

- All destructive integration tests MUST pass the guard. ABORT otherwise per §22.
- For DEV runs against dev DB: no destructive DROP DATABASE; only TX-B TRUNCATE 4 dynamic tables inside the safety TX.

---

## 13. UNKNOWN MEMBER POLICY (§15 Mandate)

Do NOT create fake unknown member rows with SK=-1 or "UNKNOWN" literal names.

| Dimension | Unknown Member Policy |
|---|---|
| dim_source | NO unknown member. Unknown source_id fails INPUT integrity CRITICAL before load. Source is always known (2 manifest registered). |
| dim_rating | NO unknown member. rating_value outside 1..5 → per-row MAJOR → REJECT_ROW. Never stored in dim_rating row 0 / fake. |
| dim_category | NO unknown member. Empty/missing category → per-row MAJOR → REJECT_ROW. Never fake "Uncategorized". |
| dim_product | NO unknown member. Source A product → product_sk = NULL (correct representation of NOT_AVAILABLE not fake member). Source B empty product_id → REJECT_ROW not fake unknown. |
| dim_shop | NO unknown member. Source A shop → shop_sk = NULL. Source B empty shop_id → REJECT_ROW. |

Expected row counts after load:
```
dim_source = 2 (actual registered count)
dim_rating = 5 (ratings 1-5)
dim_category ≤ 34 (29 A + 5 B)
dim_product ≤ 3664 (B only)
dim_shop ≤ 158 (B only)
fact_review ≤ 5400 + 40607 = 46007 minus INPUT rejects
```

---

## 14. CONFIGURATION / SECRETS

- `.env.example` has placeholders: POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD.
- `.env` created locally by user (NEVER committed; .gitignore covers). python-dotenv EXISTS in core deps.
- Database config: for localhost dev default: host=127.0.0.1 port=5432 user=openpg password=openpgpwd dbname=marketvoice_dev / marketvoice_test (§6.6 test DB).
- Environment marker `MARKETVOICE_ENV` ∈ {dev, test} (NOT production; MVP only). test mode triggers additional safety guard before all destructive DDL.
- Secrets: NEVER logged; NEVER hardcoded in source tree.
- data/raw read-only: all opens mode='r' only. Test suite contains assertion no file descriptor with write to data/raw tier held during extract run.

---

## 15. PLANNED CODE TREE (§27 preferred structure; adjust to repo convention only if needed)

```
src/marketvoice/
  __init__.py
  utils/
    __init__.py
    config.py          (existing; add load_data_sources(), load_source_manifest() helpers + .env load with sys.path .pipdeps psycopg hook)
    hashing.py         (streaming sha256, row hash formula §16 factory)
  database/
    __init__.py
    connection.py      (connect_factory: reads env + config, sets client_encoding=UTF8, returns psycopg connection; assert_safe_destructive guard)
    schema.py          (helper: check schema exists via info_schema, list tables)
  etl/
    __init__.py
    extract.py         (§10.3 — stdlib csv only; strict UTF-8; SHA pre/post; DictReader row enumerate)
    standardize.py     (§10.5 — column rename; light normalization; rating cast)
    transform.py       (§10.6 — dim candidates; product variant tie-break §20; fact candidate build; row hash §16)
    load.py            (§10.7 — 3-TX model: A STARTED, B warehouse + PRE-COMMIT 19 checks ROLLBACK/COMMIT, C finalize; rejections/dq results insert outside)
    pipeline.py        (orchestrator run_pipeline() entry: extract→val→std→xform→load→reconcile→report; return run_id+status)
    report.py          (§10.9 — write pipeline_report_*.json and rejections backup JSON to logs/)
  quality/
    __init__.py
    rules.py           (DQ rules roster from §11.2; severity definitions)
    checks.py          (INPUT per-row + run-wide checks; TRANSFORM checks; returns list of rejections + check results)
    post_load.py       (POST-LOAD forensic queries + SHA final; info-only cannot rollback)

tests/phase06/
  __init__.py
  conftest.py             (MARKETVOICE_ENV=test guard fixture; test DB creation helper; destructive operation hook that calls assert_safe_destructive)
  test_ddl.py             (apply 001-004 and verify 9 tables via information_schema)
  test_constraints.py     (verify CHECK/UNIQUE/FK constraints via pg_catalog + attempted violation inserts rollback)
  test_extract.py         (SHA compute; UTF-8 strict; manifest compare; row count exact; test fixtures)
  test_transform.py       (hash reproducibility; product name variant tie-break §20; S2T field alignment)
  test_transactions.py    (3-TX model: pipeline_run survives rollback; PRE-COMMIT fail → ROLLBACK; failed run audit persists)
  test_idempotency.py     (run twice; same natural keys; 0 dupes; same cardinality per source)
  test_source_isolation.py (Source A product_sk/shop_sk NULL; B labels NULL; cross-source boundary checks)
  test_safety.py          (raw tier never open with write handle; MARKETVOICE_ENV guard on destructive — ABORT on mismatch)
  test_reconciliation.py  (input = accepted + rejected per source)

sql/warehouse/
  001_schema.sql          (CREATE SCHEMA marketvoice_warehouse IF NOT EXISTS; SET search_path)
  002_tables.sql          (CREATE TABLE 9 tables with column definitions + PRIMARY KEY inline)
  003_constraints.sql     (ALTER TABLE ADD FK; ADD CHECK; ADD UNIQUE; seed dim_source 2 rows; seed dim_rating 5 rows — all ON CONFLICT DO NOTHING)
  004_indexes.sql         (FK indexes: fact_review.category_sk, product_sk, shop_sk, rating_sk, source_sk, pipeline_run_id; composite (source_sk, rating_value); dims natural key unique index already via constraint)

logs/                   (runtime LOCAL_ONLY; .gitkeep + README.txt)
reports/validation/     (phase_06_warehouse_validation.md v1.0 produced end of run)
```

### 15.1 Avoided per §8, §9, §10, §23

- NO `track_b_loader` module
- NO `ENABLE_TRACK_B` runtime flag
- NO synthetic fixture pipeline or production path
- NO `sql/warehouse/099_future_phases_reserved.sql`
- NO Pandas added (stdlib csv.DictReader only)
- NO SQLAlchemy / Alembic / Airflow / dbt / python-dotenv (python-dotenv already EXISTS in core; don't duplicate)

---

## 16. TEST STRATEGY (§31 Required Tests + §22 Safety)

### 16.1 Mandated Tests (per §31)

```bash
# 1. Python syntax sanity
python -m compileall -q src scripts tests

# 2. Pytest phase06
pytest -q tests/phase06

# 3. Unittest discover
python -m unittest discover tests -v

# 4. Git whitespace sanity
git diff --check
```

### 16.2 Test Database (§22 SAFETY FIRST)

- Isolated DB `marketvoice_test`. Destructive DROP SCHEMA / TRUNCATE guarded:
  - `MARKETVOICE_ENV` env var MUST == "test"
  - `SELECT current_database()` MUST == configured test DB name
  - Either mismatch → ABORT before ANY destructive operation (UnsafeDatabaseError raised).
- Teardown after tests: ONLY if guard passes, drop schema marketvoice_warehouse and recreate. Database itself reused.
- Connection credentials inherited from `.env` POSTGRES_USER etc. with suffix _TEST for DB name.

### 16.3 Coverage Points

- DDL: tables == 9 in info_schema; columns match S2T (§9); 3 audit tables never truncated via code review + test that attempts to truncate audit tables via helper raises UnsafeAuditTruncate.
- Constraint: insert invalid rating_value 6 → CHECK violation rollback; insert dup source_native_row_hash → UNIQUE violation; insert fact with non-existent category_sk → FK violation.
- Extract: SHA mismatch → raises CriticalError; UTF-8 replacement simulated (no: strict only — feed test fixture with invalid UTF-8 byte → CriticalError UnicodeDecodeError correctly surfaced with severity CRIT).
- Transform: hash reproducibility 100 rows recompute; variant tie-break when 2 names equal frequency — confirm lowest row number name selected per §20.
- Transactions: 3-TX test — simulate PRE-COMMIT fail mid TX-B; SELECT pipeline_run.status → must see FAILED row persists; SELECT count(*) fact_review → must equal pre-failure state (0 because rollback). Audit rejections persisted despite rollback.
- Idempotency: run twice; compare natural keys, cardinalities per source, 0 duplicate natural keys.
- Source isolation §6 locked: after load, A rows product_sk/shop_sk all NULL; B rows labels all NULL.
- Safety: os.open write-mode to data/raw path during extract never detected via monkeypatch.

---

## 17. SQL TREE (DEL-08; no 099 per §10)

- 001_schema.sql: CREATE SCHEMA marketvoice_warehouse (IF NOT EXISTS for idempotency). search_path set session default for convenience.
- 002_tables.sql: CREATE TABLE all 9 tables (§8 register) with PRIMARY KEY inline and basic types. No FK in 002 — FK deferred to 003. Audit history tables explicitly commented as NEVER TRUNCATE.
- 003_constraints.sql:
  - ALTER TABLE ADD FOREIGN KEY for all fact + dim + audit references; ON DELETE NO ACTION (defensive).
  - CHECK constraints: rating_value 1..5, status enum, severity enum, fact_review label domain CHECK, is_synthetic boolean.
  - UNIQUE: dim_source.source_id; dim_rating.rating_value; dim_category/source+category; dim_product/source+product_id; dim_shop/source+shop_id; fact_review/source_sk+row_hash defensive; data_quality_result.(pipeline_run_id, dq_check_id) PK.
  - Seed dim_source 2 rows (SRC_PRDECT_ID_V1, SRC_TOKOPEDIA_REVIEWS_2019) INSERT ... ON CONFLICT DO NOTHING.
  - Seed dim_rating 5 rows (1..5) ON CONFLICT DO NOTHING.
- 004_indexes.sql: FK indexes per §8.9 list above.
- Explicitly NOT created: 099_future_phases_reserved.sql per §10 (future items documentation-only; no executable placeholder required).

---

## 18. ORDERED EXECUTION STEPS (§29 MANDATE)

```
6.1  ✅ PREFLIGHT + GATE VERIFICATION (entry Phase 0-5)
6.2  ✅ APPLY DEL-08 / DEL-11 GOVERNANCE CLARIFICATION to governance docs
6.3  ⚙️ REVISE phase_06_implementation_plan.md → v1.1 (this document, all §7-§28 mandates applied)
6.4  LOCK PHYSICAL S2T MAPPING — §9 register documented in this plan
6.5  IMPLEMENT DDL (sql/warehouse/001-004)
6.6  APPLY DDL TO ISOLATED TEST DB SAFELY (MARKETVOICE_ENV=test guard)
6.7  IMPLEMENT EXTRACT + STANDARDIZE MODULES (stdlib csv ONLY; strict UTF-8)
6.8  IMPLEMENT TRANSFORM + DIMENSION MAPPING (source_sk lookup ONLY via source_id; variant tie-break §20)
6.9  IMPLEMENT DQ ENGINE rules/checks/post_load (semantic severity §18; no arbitrary %)
6.10 IMPLEMENT 3-TRANSACTION LOAD / AUDIT (A pipeline_run; B warehouse + PRE-COMMIT 19 checks ROLLBACK/COMMIT; C finalize; audit never truncated)
6.11 IMPLEMENT ORCHESTRATOR pipeline.py, report.py, database/connection.py + schema.py helpers
6.12 IMPLEMENT tests/phase06 suite (DB safety guard MARKETVOICE_ENV + current_database() required pre-drop/truncate)
6.13 RUN TEST DB INTEGRATION SUITE
6.14 RUN DEV FULL ETL AGAINST LOCAL POSTGRESQL (marketvoice_dev)
6.15 RUN ROW COUNT + FK INTEGRITY + SHA PRE/POST + CROSS-SOURCE ISOLATION RECONCILIATION
6.16 RUN FULL REGRESSION: compileall, validators, unittest, pytest, git diff --check
6.17 CREATE reports/validation/phase_06_warehouse_validation.md WITH REAL EVIDENCE
6.18 UPDATE phase_gates.md §7 WITH PHASE 6 STATUSES (BUILD_STATUS=COMPLETE, VAL=PASS, HUMAN=PENDING, GATE_RECOMMEND=PASS, GATE=AWAITING_HUMAN_APPROVAL — NEVER PASS without human)
```

STOP immediately after step 6.18. DO NOT proceed to Phase 7.

---

## 19. VALIDATION EVIDENCE REQUIRED (§32 Mandate Checklist)

Phase 6 Validation MUST PRODUCE EVIDENCE of each below in validation report §6.17:

- [x] DEL-08 PASS = physical warehouse 9 tables created; constraints + indexes; 0 views; schema verified via info_schema
- [x] DEL-09 PASS = ETL runs successfully from raw → validated → warehouse; reproducible; 3-TX model verified
- [x] DEL-10 PASS = 0 unresolved CRITICAL; 0 unresolved MAJOR INTEGRITY; 9× pre-commit checks all PASS; DQ severity semantic used throughout
- [ ] CRITICAL_DQ_FAIL = 0 (post-final run)
- [ ] MAJOR_INTEGRITY_BLOCKER = 0
- [ ] RAW_DATA_MUTATION = 0 (SHA pre == SHA post == manifest; mtime unchanged; 0 write fds)
- [ ] CROSS_SOURCE_LINKAGE = 0 (all pre-commit C01, C02, C03, C04 PASS)
- [ ] FAKE_REVIEW_TIMESTAMPS = 0 (only technical UTC stamps)
- [ ] SYNTHETIC_ROWS = 0 (C05 PASS)
- [ ] UNEXPLAINED_WAREHOUSE_FIELDS = 0 (§9 7-tuple register complete)
- [ ] ETL_REPRODUCIBLE = PASS (run twice; same code → same PASS status)
- [ ] FULL_REFRESH_IDEMPOTENT = PASS (2nd run natural keys/cardinalities match; 0 dupes)
- [ ] TRANSACTION_ROLLBACK = PASS (simulate PRE-COMMIT fail → ROLLBACK; prior state intact)
- [ ] FAILED_RUN_AUDIT_PERSISTS = PASS (pipeline_run FAILED + rejections visible after rollback)
- [ ] ROW_RECONCILIATION = PASS (input == accepted + rejected per source)
- [ ] TESTS = PASS (compileall, pytest phase06, unittest, git diff --check)

---

## 20. OBJECTIVE ACCEPTANCE CRITERIA (AC)

| AC-ID | Criterion | Measured By |
|---|---|---|
| AC-01 | 9 physical tables exist as per §7 (6 analytical + 3 audit). No BI views/marts. No dim_date/model/issue/case. | info_schema table count + pg_class SELECT; grep sql tree for mv_ / 099 = zero occurrences |
| AC-02 | DEL-08 DDL applies clean idempotently. Running 001-004 twice = same state, zero errors. | Re-run test_ddl twice; no ERROR. |
| AC-03 | ETL entry: SHA pre/post load of each raw file == manifest SHA. | DQ-INTEGRITY-001/002/006 (pre-commit C16/C17) PASS |
| AC-04 | Source A fact_review rows: product_sk NULL, shop_sk NULL, labels NON-NULL, A 6 contextual cols populated, B 3 contextual cols NULL. | Pre-commit C01, C02 PASS. Post forensics. |
| AC-05 | Source B fact_review rows: product_sk NON-NULL, shop_sk NON-NULL, labels NULL, A contextual NULL, B contextual populated. | Pre-commit C03, C04, C13, C14 PASS |
| AC-06 | is_synthetic = FALSE for every row. | C05 PASS. Any TRUE → fail immediately. |
| AC-07 | 3-Transaction model proven. test_transactions passes. pipeline_run survives rollback. Failed run audit persists. | pytest test_transactions + manual dev DB run with fail-simulate |
| AC-08 | Idempotency test_pass. Identical source run twice. Same natural-key rows. Same business values. Same dim/fact cardinality (dimension counts per source). Zero duplicate (source_sk, source_native_row_hash). SERIAL values may differ. | pytest test_idempotency |
| AC-09 | PRE-COMMIT CRITICAL checks C01..C19 ALL RUN inside TX-B before COMMIT. Any non-zero → ROLLBACK proven. | test + code inspection + log evidence |
| AC-10 | Audit tables (pipeline_run / rejected_record_log / data_quality_result) NEVER truncated. Evidence: code inspection of load.py shows TRUNCATE list only 4 dynamic analytical tables; test suite verifies that TRUNCATE against audit tables not issued in any code path. | grep + tests |
| AC-11 | Row reconciliation: per source, input_rows_read == accepted_rows + rejected_rows. No record silently dropped. | C18/C19 PRE-COMMIT. |
| AC-12 | Source B product name variant: most frequent + lowest row# tie-break works. Variant count correctly stored. | pytest test_transform (variant fixture) |
| AC-13 | source_sk NEVER hardcoded as 1/2. All lookups by dim_source canonical source_id. | Code review: grep `source_sk\s*[=:]\s*[12]\b` in src/marketvoice — zero occurrences except test docs for explanation (explanations allowed; runtime usages FORBIDDEN). |
| AC-14 | Row hash formula = SHA256(source_id + "\|" + source_file_sha256 + "\|" + padded 7-digit row number). Classification marked NOT_LINKABLE / WAREHOUSE_INTERNAL. | pytest hash_reproducibility + code review |
| AC-15 | UTF-8 strict: invalid bytes → CriticalError BLOCK_LOAD; never errors="replace". PostgreSQL server_encoding UTF8 verified. | test_extract invalid fixture; psycopg SHOW server_encoding query. |
| AC-16 | Test DB safety: MARKETVOICE_ENV mismatch OR current_database() wrong → ABORT on destructive DROP/TRUNCATE. | pytest test_safety. |
| AC-17 | All tests: compileall PASS; pytest -q tests/phase06 PASS; unittest discover PASS; git diff --check PASS. | Terminal command actual outputs. |
| AC-18 | DEL-10: 0 unresolved CRITICAL; 0 unresolved MAJOR INTEGRITY. Semantic severity CRIT/MAJOR/MINOR/INFO applied correctly; arbitrary 1%/5% thresholds never present. | data_quality_result final run; grep source code for 1% / "5%" → zero occurrences except in comments explaining NOT used. |
| AC-19 | Validation report created at correct path with ALL actual evidence (tables; pg version/encoding; SHA pre/post; counts; dim/fact; DQ; rollback test; failed-run audit persist; idempotency; cross-source; timestamp boundary; test; git/data safety; limitations). | Manual check of report content. |
| AC-20 | Final statuses correct in phase_gates.md: BUILD=COMPLETE, VALIDATION=PASS, HUMAN_REVIEW=PENDING, GATE_RECOMMEND=PASS, GATE_STATUS=AWAITING_HUMAN_APPROVAL. NO self-promote to GATE PASS without human. | Doc inspection |

---

## 21. RISKS

| Risk ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| RSK-01 | PostgreSQL server not available locally / wrong encoding | Medium (laptop) | HIGH CRITICAL | Preflight check localhost:5432 connect + SHOW server_encoding; if fail GENUINE_EXTERNAL_BLOCKER STOP |
| RSK-02 | psycopg driver fail to install | Low | HIGH | Preflight pip install target local dir; pg8000 pure-Python backup plan (not activated unless psycopg fails) |
| RSK-03 | Human mistakenly runs pipeline against production-like DB | Low | VERY HIGH (data loss) | MARKETVOICE_ENV guard; current_database() check; .env separation dev/test; audit never truncate; no destructive DDL in prod path |
| RSK-04 | Raw source files modified concurrently during ETL run | Very Low | HIGH | SHA pre + SHA post + SHA forensic final; 3-way comparison; mtime check |
| RSK-05 | SK mis-assignment bug (hardcoded 1/2) | Low | HIGH | Code review check grep; PRE-COMMIT C01/C02/C03/C04 catch cross-source leakage |
| RSK-06 | Transaction model bug causing partial load state | Low | HIGH | 3-TX model + PRE-COMMIT inside TX-B; test_transactions validates rollback |
| RSK-07 | Track B synthetic code accidentally included in future copy/paste | Medium | HIGH | Plan explicitly forbids; is_synthetic scan C05 catches any TRUE row ever |
| RSK-08 | Product name variants merged by name (not id) | Low | HIGH | §20 tie-break rule; natural key product_id always authoritative |

---

## 22. ROLLBACK & HARD-STOP PROCEDURES

### 22.1 Phase 6 Hard Stop List (already in §1 of execution brief)

Stop IMMEDIATELY and report WITHOUT any further code/DB execution if any:
1. GENUINE_EXTERNAL_BLOCKER (PostgreSQL not available / wrong encoding / driver cannot install; user to fix env)
2. MATERIAL_PHASE_5_ARCHITECTURE_DEFECT (actual evidence that Phase 5 design is incompatible)
3. UNAVAILABLE_REQUIRED_DATA (raw source file missing / corrupted beyond repair)
4. UNSAFE_DATABASE_STATE (wrong DB guard failed; data/raw opened write; MARKETVOICE_ENV mismatch; critical data integrity not restorable)

### 22.2 Rollback Procedures

1. **In-flight TX-B fails:** Automatic ROLLBACK. Status FAILED on pipeline_run. Evidence persisted. Next run of pipeline automatically refreshes dynamic 4 tables.
2. **Post-commit major bug discovered (bad code loaded bad data):** Fix code → run pipeline again. Full refresh replaces dynamic 4 tables entirely. Old (bad) successful run remains in pipeline_run with status SUCCESS plus notes updated by hand if needed (DB admin).
3. **Whole schema blown away (worst case):** Apply 001-004 DDL fresh; re-run ETL. Audit tables lost → NOT RECOVERABLE (this is why we NEVER truncate audit + guard on destructive).
4. **Git/Data Safety rollback:** No Git commits performed in Phase 6 per instruction (LOCAL_COMMIT=FALSE_UNLESS_USER_APPROVES). No remote write. No writes to data/raw ever, so nothing to rollback on those tiers.

---

## 23. PHASE 7 HANDOFF (DO NOT EXECUTE — REFERENCE ONLY)

Phase 6 DEL-08/09/10 provide to Phase 7 DEL-11 Baseline BI Queries:
- Committed warehouse with 9 tables
- Verified deterministic row counts per source
- 0 cross-source linkage
- Known constraints of NOT_AVAILABLE temporal/product/shop for Source A and labels for Source B
- Historical audit trail for reproducibility proof

Phase 7 will create the 5+ business mart views (mv_*) explicitly listed in §7.3 as deferred here.

---

## 24. HUMAN DECISIONS REQUIRED (none automatic — gate only)

Only ONE human decision required after this plan executes successfully:

- HD-PHASE-06-GATE: Approve or reject the Phase 6 gate (review validation report + evidence). Pending this approval, PHASE_6_GATE_STATUS remains AWAITING_HUMAN_APPROVAL per §34. Agent never self-promotes to PASS.

---

```
PLAN_DOCUMENT_VERSION = 1.1 (REVISED_EXECUTION)
PLAN_STATUS = APPROVED_WITH_MANDATORY_REVISIONS
PLAN_28_ITEMS_ALL_MANDATES_APPLIED = TRUE
READY_FOR_IMPLEMENTATION = TRUE
```
