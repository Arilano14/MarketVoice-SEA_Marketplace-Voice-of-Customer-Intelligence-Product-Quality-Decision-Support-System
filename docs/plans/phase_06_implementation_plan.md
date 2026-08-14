# MARKETVOICE SEA — PHASE 6 IMPLEMENTATION PLAN

**Phase:** 6 — ETL & Data Warehouse

**Document Version:** 1.0 (Implementation Ready — PLAN_ONLY; no execution performed)

**Date Created:** 2026-08-14

**Status:** `PHASE_6_PLAN_STATUS = READY_FOR_HUMAN_REVIEW`
`PHASE_6_EXECUTION_STATUS = NOT_STARTED`
`PHASE_6_EXECUTION_AUTHORIZED = FALSE`
`PHASE_7_IMPLEMENTATION = FORBIDDEN`

**Authority:** Phase 5 gate PASS recorded in `docs/governance/phase_gates.md` v4.3 (2026-08-14). Phase 5 logical architecture (29/29 design checks PASS via `reports/validation/phase_05_architecture_validation.md` v1.1).

**Hard Stop Conditions (this document):**
- NO DDL executed
- NO database created
- NO ETL code executed
- NO processed data generated
- NO raw data mutated
- NO git commit performed
- NO git push performed
- Human approval required before any execution run

---

## 1. EXECUTIVE PURPOSE

Phase 6 implements the **physical PostgreSQL data warehouse, reproducible Python batch ETL pipeline, and automated Data Quality (DQ) controls** specified by the Phase 5 logical architecture. It is the first implementation phase of the MarketVoice SEA project and delivers only the three canonical Phase 6 deliverables:

- **DEL-08** PostgreSQL Data Warehouse & Staging Schema — DDL scripts creating the warehouse schema, tables, constraints, and indexes derived strictly from the Phase 5 Kimball dimensional model.
- **DEL-09** Reproducible SQL/Python ETL Pipeline — Automated batch ETL that loads immutable validated raw source evidence into the governed Track A analytical warehouse without cross-source fabrication, without temporal invention, and preserving full provenance lineage.
- **DEL-10** Automated Data Quality Test Suite — DQ check suite operating at INPUT → TRANSFORMATION → LOAD → POST_LOAD stages with severity classification, rejection reason codes, and zero-tolerance for CRITICAL failures.

Phase 6 explicitly does **NOT** include:
- Baseline BI queries / marts (Phase 7, DEL-11)
- ML rating / sentiment / emotion model training or inference (Phase 8–9)
- Issue taxonomy, aspect annotation, or issue-classifier DDL/training (Phase 9)
- Priority scoring, decision formulas, case queues, SLA logic (Phase 10)
- FastAPI, REST endpoints, n8n workflow nodes (Phase 11)
- Power BI visuals, DAX, reports, pages, datasets (Phase 7/12)
- Synthetic Track B data, synthetic timestamps, synthetic cases (CONDITIONAL, NOT AUTHORIZED)
- Cross-source product/shop fuzzy linkage (FORBIDDEN by locked data reality)
- Cloud warehouse, Kafka, Spark, Airflow, Kubernetes, microservices, vector DB, feature store (FORBIDDEN by anti-overengineering)

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
PHASE_6_ENTRY_READINESS = READY
PHASE_6_EXECUTION_STATUS = NOT_STARTED
```

### 2.2 Evidence Register

| Gate | Primary evidence | Key verified facts |
|---|---|---|
| Phase 0 | `docs/governance/project_charter.md`, `data_governance_policy.md`, `project_definition_of_done.md` | Governance, DOD, data tier LOCAL_ONLY policy in force. |
| Phase 1 | `docs/engineering/development_environment.md`; `tests/test_environment.py` 3/3 PASS; `config/project_settings.yaml` | Python 3.10 stack; Git; local paths `data/raw`, `data/interim`, `data/processed`, `data/metadata`, `logs` declared and present. |
| Phase 2 | `data/metadata/source_manifest.csv`; `data/metadata/data_capability_matrix.csv`; `reports/validation/phase_02_dataset_forensic_audit_report.md` | Source A = 5,400 rows / 11 cols / SHA `1dfdde6b…bde`; Source B = 40,607 rows / 8 cols / SHA `dbffc290…b7ed`; 29 CAP IDs with NOT_SUPPORTED boundaries locked. |
| Phase 3 | `docs/requirements/business_and_information_requirements.md`, `system_requirements.md`, `use_cases_and_mvp.md`, `requirements_traceability.md`; `reports/validation/phase_03_validation.md`; gate record §4 | 7 BQ → 7 BR → 7 IR → 9 FR + 7 NFR; `ORPHAN_MUST_REQUIREMENTS = 0`; HD-002 PASS; bounded scope explicit. |
| Phase 4 | `docs/methodology/analytical_research_design.md`, `evaluation_protocol.md`, `experiment_protocol.md`; `config/experiment_settings.yaml`; `reports/validation/phase_04_research_design_validation.md`; gate record §5 | 70/15/15 stratified non-temporal split; deterministic duplicate policy (normalized text → group_id → one-split-only; exclusion FORBIDDEN without governance exception); ordinal rating metrics (QWK + MAE + per-class recall mandatory); baseline sequence majority → LR → SVM → ≤1 challenger; holdout used ONCE only. |
| Phase 5 | `docs/architecture/solution_architecture.md`, `data_architecture.md`, `dimensional_model.md`, `integration_contracts.md`; `reports/validation/phase_05_architecture_validation.md` v1.1 29/29 PASS; gate record §6 | ONE_FACT_ONE_GRAIN; FAKE_CROSS_SOURCE_KEYS=FORBIDDEN; 6 Track A entities (`dim_source`, `dim_rating`, `dim_category`, `dim_product`, `dim_shop`, `fact_review`) + 9 future/conditional entities deferred; NO `dim_date`; `ORPHAN_ARCHITECTURE_COMPONENTS = 0`; single warehouse anti-over-engineering decision. |

### 2.3 Verified Empirical Raw Data Reality (reconfirmed)

| Attribute | Source A (PRDECT-ID V1) | Source B (Tokopedia 2019) |
|---|---|---|
| Row count (exact) | 5,400 | 40,607 |
| Column count (exact) | 11 | 8 |
| Rating field | `Customer Rating` (values 1–5, verified 1=1832..5=2150) | `rating` (values '1'..'5' string, verified 1=543..5=30311) |
| Review text field | `Customer Review` | `text` |
| Sentiment gold | PROVIDED (Positive/Negative; 2821/2579) | NOT_AVAILABLE |
| Emotion gold | PROVIDED (5 classes: Happy 1770 / Sadness 1202 / Fear 920 / Love 809 / Anger 699) | NOT_AVAILABLE |
| Category | `Category` (29 unique values, 200/row balanced) | `category` (5 values; no conformance to A proven) |
| Product business key | NOT_AVAILABLE (`Product Name` is text descriptor only; NOT a business key) | `product_id` (3,664 unique; SOURCE_NATIVE authoritative) |
| Shop business key | NOT_AVAILABLE | `shop_id` (158 unique; SOURCE_NATIVE authoritative) |
| Product metadata (contextual) | `Product Name`, `Price`, `Overall Rating`, `Number Sold`, `Total Review` (all source-local contextual only) | `product_name`, `sold` (40,592 non-empty, 15 empty null → limitation documented) |
| Other contextual | `Location` (61 values) | `product_url` (restricted public analytics by default) |
| Review timestamp | NOT_AVAILABLE | NOT_AVAILABLE |
| SLA / case / lifecycle | NOT_AVAILABLE | NOT_AVAILABLE |

### 2.4 Git / Working-Tree Readiness

```
git status --short = (empty, CLEAN)
git branch --show-current = main
git log -n 5 --oneline = 4969027..5c4c009 (clean lineage; no remote mutation)
git diff --stat = (empty, no unstaged/staged divergence)
git ls-files data/raw = empty (GOOD; only .gitkeep + README tracked)
git ls-files data/interim = .gitkeep + README.md (GOOD; standardized CSVs now gitignored LOCAL_ONLY)
git ls-files logs = .gitkeep + README.txt (GOOD; runtime artefacts LOCAL_ONLY)
```

---

## 3. DEL-08 / DEL-09 / DEL-10 MAPPING

Canonical definitions sourced from `docs/governance/project_definition_of_done.md`:

| DEL-ID | Canonical Name | Canonical Definition | Prereq DEL(s) | Phase 6 Plan Coverage |
|---|---|---|---|---|
| **DEL-08** | PostgreSQL Data Warehouse & Staging Schema | DDL scripts creating staging, DW, and marts | DEL-07 | §7 Physical Warehouse Plan; §16 Planned SQL Tree; Steps 6.4/6.5. **Decision on staging:** DEL-08 wording "staging, DW, and marts" requires a staging layer; we implement staging as **in-memory Python Pandas structures only (no DB staging tables)** — equivalent functional staging. Staging-as-Python achieves identical lineage/validation outcomes with simpler architecture for a ~46K-row dataset. This is an `ARCHITECTURE_CLARIFICATION` (see §6 R-02), not a defect. |
| **DEL-09** | Reproducible SQL/Python ETL Pipeline | Automated ETL loading raw/synthetic data to DW | DEL-08 | §10 ETL Design; §15 Planned Code Tree; Steps 6.6–6.10. Synthetic clause scoped to `is_synthetic=TRUE` loading path that is CONDITIONAL and DISABLED BY DEFAULT in Track A MVP configuration. Track B path compiles but produces zero rows unless explicitly separately authorized. |
| **DEL-10** | Automated Data Quality Test Suite | Automated test suite passing with 0 critical fails | DEL-09 | §11 Data-Quality Design; §17 Test Strategy; §20 Objective Acceptance Criteria (AC-01..AC-20); Steps 6.11–6.16. |

`ORPHAN_PHASE6_DELIVERABLES = 0`

---

## 4. SOURCE-OF-TRUTH REGISTER

Priority (high → low); any conflict is resolved by the higher-priority file:

1. **Local working repository state** (git tracked files only; LOCAL_ONLY artefacts are regenerated)
2. **Current git diff** — working tree modifications override committed files for ambiguity
3. `docs/governance/phase_gates.md` v4.3 — single canonical gate authority
4. **Phase 5 architecture suite**:
   - `docs/architecture/dimensional_model.md` v1.0 — entity/grain/key register
   - `docs/architecture/data_architecture.md` v1.0 — layer responsibilities + conceptual S2T
   - `docs/architecture/solution_architecture.md` v1.0 — component responsibility matrix
   - `docs/architecture/integration_contracts.md` v1.0 — downstream contracts + trace + anti-over-engineering
   - `reports/validation/phase_05_architecture_validation.md` v1.1 — 29/29 checks + stop conditions
5. **Phase 2 capability/provenance**:
   - `data/metadata/source_manifest.csv` v1.0 — SHA/file size/row count/license/path
   - `data/metadata/data_capability_matrix.csv` v1.0 — CAP-01..CAP-08 + SUPPORTED/NOT_SUPPORTED boundaries
6. **Phase 3 requirements/RTM**:
   - `docs/requirements/requirements_traceability.md` v2.0 — BQ→BR→IR→(FR/NFR/DR/UC) matrix; ORPHAN=0
   - `docs/requirements/business_and_information_requirements.md` v2.0
   - `docs/requirements/system_requirements.md` v2.0
   - `docs/requirements/use_cases_and_mvp.md` v2.0
7. **Phase 4 analytical methodology**:
   - `docs/methodology/analytical_research_design.md` — ordinal rating + split rules
   - `docs/methodology/experiment_protocol.md` — deterministic duplicate policy
   - `config/experiment_settings.yaml` — split/duplicate/hardware parameters
8. **Config files**:
   - `config/project_settings.yaml` — paths, seeds, phase identifier
   - `config/data_sources.yaml` — source IDs, paths, columns, `cross_source_*_linkage: false`
   - `config/experiment_settings.yaml` — split/duplicate/hardware parameters
9. **Validation reports**: `reports/validation/phase_0[1-5]*.md` — active/canonical validation reports only (`phase_01_remediation_report.md` is SUPERSEDED/HISTORICAL)
10. `README.md` — user-facing project state, install steps, badges
11. Legacy/AI summaries — informational only; overridden by all above

---

## 5. LOCKED SCOPE / BOUNDARIES

These boundaries are frozen for the entire Phase 6 implementation. Any change requires a separate governance document and a new gate decision; they are **NON-NEGOTIABLE**:

```
REAL_REVIEW_TIMESTAMP = NOT_AVAILABLE
AUTHENTIC_TIME_ANALYTICS = NOT_SUPPORTED
SOURCE_A↔SOURCE_B_ROW_LINKAGE = NOT_SUPPORTED
SOURCE_A↔SOURCE_B_PRODUCT_LINKAGE = NOT_SUPPORTED
SOURCE_A↔SOURCE_B_SHOP_LINKAGE = NOT_SUPPORTED
FUZZY_LINKAGE = FORBIDDEN
SOURCE_A_PRODUCT_ID = NOT_AVAILABLE (Source A fact_review.product_sk = NULL always)
SOURCE_A_SHOP_ID = NOT_AVAILABLE    (Source A fact_review.shop_sk = NULL always)
TRACK_B_SYNTHETIC = NOT_AUTHORIZED  (is_synthetic path compiles but loads 0 rows; DISABLED by default)
```

**Derived consequences (implementation implications)**:

1. `dim_date` — Phase 6 MUST NOT create any date/calendar dimension for authentic review facts. A `dim_date` is FORBIDDEN because it would imply temporal analytical capability. Technical timestamps (`ingested_at`, `processed_at`, `loaded_at`, `pipeline_started_at`, `pipeline_completed_at`) are permitted as UTC system-generated audit columns; they are NEVER exposed as review-event dates and are labeled `SYSTEM_GENERATED / lineage_class = TECHNICAL_METADATA_ONLY`.
2. `dim_product` — contains ONLY Source B `product_id` entries (3,664 expected; 0 rows derived from Source A).
3. `dim_shop` — contains ONLY Source B `shop_id` entries (158 expected; 0 rows derived from Source A).
4. `dim_category` — 29 Source A rows + 5 Source B rows, each with its own `source_sk` parent; no cross-source category key. Two rows sharing a raw category text but different `source_sk` are NOT comparable and NOT merged.
5. `fact_review.product_sk` — NON-NULL for 40,607 Source B rows only; NULL for 5,400 Source A rows (no fake "unknown product" member filling Source A).
6. `fact_review.shop_sk` — same pattern: Source B NON-NULL; Source A NULL always.
7. `fact_review.source_gold_sentiment_label` + `source_gold_emotion_label` — NON-NULL only for Source A; ALWAYS NULL for Source B (no copying predictions or invented labels).
8. No issue taxonomy table; no issue gold labels; no priority table; no case/intervention table; no model/dim/prediction/evaluation tables — all deferred to their respective future phases. Only the 6 Track A Phase 6 entities + pipeline metadata tables are created.

**Data Governance LOCAL_ONLY policy (reaffirmed from Phase 5 remediation)**:

| Path | Policy | Git-tracked exceptions only |
|---|---|---|
| `data/raw/*` | LOCAL_ONLY | `data/raw/.gitkeep`, `data/raw/README.md` |
| `data/interim/*` | LOCAL_ONLY | `data/interim/.gitkeep`, `data/interim/README.md` |
| `data/processed/*` | LOCAL_ONLY | `data/processed/.gitkeep`, `data/processed/README.md` |
| `logs/*` | LOCAL_ONLY | `logs/.gitkeep`, `logs/README.txt` |

Raw source CSVs are read-only for Phase 6 ETL. The ETL `extract()` step must open files in mode `"r"` only; no write file handle is ever opened against any path under `data/raw/`.

---

## 6. PHASE 5 → PHASE 6 RECONCILIATION

Every discrepancy between the Phase 5 logical design and what Phase 6 physically needs is classified as IMPLEMENTATION_DETAIL (resolved in plan), ARCHITECTURE_CLARIFICATION (documented note), or ARCHITECTURE_DEFECT (would BLOCK plan).

| Finding ID | Observation | Classification | Resolution |
|---|---|---|---|
| **R-01** | DEL-08 text: "DDL scripts creating **staging**, DW, and marts". Phase 5 `data_architecture.md` §1 defines a "Staging" layer (row 13) but dimensional_model.md §2 entity register lists zero staging entities. The word "staging" has ambiguous physical meaning: DB staging tables vs. in-memory Python staging frames. | `ARCHITECTURE_CLARIFICATION` | Staging is implemented as **in-memory Python DataFrames** during the `EXTRACT → INPUT_VALIDATION → STANDARDIZE → TRANSFORM` chain. No staging tables in PostgreSQL. Justification: dataset is ~46K rows (<10 MB memory); DB staging tables add zero analytical or DQ value while doubling DDL/load code. Lineage: every source row is traced via `source_row_id` + `source_id`; staging shape is logged as part of pipeline metadata record. Marts (Phase 6 "marts" clause of DEL-08) — delivered as simple SQL VIEWs only (not physical tables) for the 6 basic downstream browse paths (per-source summary, per-category, per-product B, per-shop B, Source A label summary). Phase 7 DEL-11 owns real BI marts; Phase 6 only delivers minimal "marts" as VIEWS to satisfy DEL-08 wording. |
| **R-02** | DEL-09 text: "Automated ETL loading **raw/synthetic** data to DW". Synthetic path is Track B (NOT_AUTHORIZED). | `ARCHITECTURE_CLARIFICATION` | ETL code includes a `track_b_loader` module that is structurally valid (has unit tests with empty fixtures) but loads 0 rows in default Track A MVP configuration. A config flag `ENABLE_TRACK_B=false` (default) disables the loader; if later authorized and set true, every loaded row has `is_synthetic=TRUE` and uses explicit synthetic IDs. No synthetic data is loaded in Phase 6 MVP execution. |
| **R-03** | `dim_rating` is described as "5 fixed members; optional surrogate key" in `dimensional_model.md` §2 row 2. | `IMPLEMENTATION_DETAIL` | Physical decision: use a small static `dim_rating` with `rating_sk` surrogate (SMALLSERIAL PK) and 5 seed rows inserted by DDL 003_constraints.sql (idempotent INSERT ON CONFLICT DO NOTHING). Benefits: downstream joins are uniform, consistent `ORDER BY rating_value` guaranteed, CHECK constraint on `fact_review.rating_value BETWEEN 1 AND 5` complemented by FK. |
| **R-04** | Source A `Customer Rating` vs. Source B `rating` — both verified as 1–5 domain but stored differently (int-ish vs. string). | `IMPLEMENTATION_DETAIL` | Standardize to `SMALLINT rating_value` in fact_review; Source B "1"→1 cast enforced by DQ check DQ-RATING-002. Source A already integer. |
| **R-05** | Source B `sold` column: 15 empty rows + text format (e.g., "1.2rb" thousand suffixes — needs audit). | `IMPLEMENTATION_DETAIL` | Store `sold_raw_text` as TEXT nullable column in fact_review; do NOT parse/interpret. Leave interpretation to Phase 7+ analytics. DQ check DQ-CONTEXT-B-SOLD-001 reports: sold empty count =15 (INFO); non-empty count =40,592 (INFO). No load blocking. |
| **R-06** | Source A has contextual metadata columns: `Price`, `Overall Rating`, `Number Sold`, `Total Review`, `Location`, `Product Name`. `data_architecture.md` §2 row 28 says "Retain only where Phase 6 verifies analytical necessity". | `IMPLEMENTATION_DETAIL` | Physical decision: retain ALL of them as nullable source-context columns in `fact_review` (low cost; avoids future re-run requirement). Lineage class = `SOURCE_DERIVED / CONTEXTUAL_SOURCE_LOCAL`. No dimension built; no cross-source joining. Columns: `source_a_price_text`, `source_a_overall_rating_text`, `source_a_number_sold_text`, `source_a_total_review_text`, `source_a_location_text`, `source_a_product_name_text`. All NULL for Source B rows. |
| **R-07** | Source B `product_url` — restricted per `data_architecture.md` §2 row 35. | `IMPLEMENTATION_DETAIL` | Store as nullable TEXT column in `fact_review` (`source_b_product_url`); DQ-DISPLAY-001 marks it "restricted from default analytical output by default". BI views in Phase 7 should EXCLUDE this column unless an admin explicitly enables it. No encryption needed (public marketplace URL already public; restriction is about analytical-scope, not PII). |
| **R-08** | `fact_review` natural/source key: dimensional_model.md says "stable analytical review key plus source-row lineage". Neither source has a stable review_id column. | `IMPLEMENTATION_DETAIL` | Deterministic internal row identity: for each source row compute `source_native_row_hash = sha256(source_id || '|' || zero_padded_row_number)`. Then the full natural/source key for `fact_review` is `(source_sk, source_native_row_hash)`. The surrogate `review_sk` (BIGSERIAL) is the warehouse key. **Hash classification:** `WAREHOUSE_INTERNAL / NOT_LINKABLE`. Hash must NEVER be used for cross-source deduplication or real-world entity matching. It exists solely to provide a deterministic natural key for idempotency. |
| **R-09** | `dim_product` uniqueness: Source B rows may repeat product_id across reviews (expected 40,607 reviews → 3,664 distinct products). | `IMPLEMENTATION_DETAIL` | Extract unique product_id + product_name from Source B staging; build dim_product with UNIQUE(source_sk, source_native_product_id). If same product_id has multiple product_name variants across rows → keep the first (most-frequent if tie). DQ-DIM-PRODUCT-001 reports count of name variants as MAJOR (a warning; no blocking). |
| **R-10** | `dim_shop` same pattern: 158 shops from B only. | `IMPLEMENTATION_DETAIL` | Extract unique shop_id from B; UNIQUE(source_sk, source_native_shop_id). No name column; Source B has none. DQ-DIM-SHOP-001 reports count (INFO only). |
| **R-11** | `dim_source` — Phase 2 manifest has 2 rows. | `IMPLEMENTATION_DETAIL` | DDL seeds 2 rows: SRC_PRDECT_ID_V1 + SRC_TOKOPEDIA_REVIEWS_2019 with metadata from source_manifest.csv. |
| **R-12** | Unknown-member policy: `dimensional_model.md` §4 says source-specific unknown/not-supplied member + validation finding for records retained for audit. | `IMPLEMENTATION_DETAIL` | dim_source/dim_rating have fixed closed-domain unknown members N/A (`source_sk` 0 never used as FK because source_id is always valid; rating_sk 0 exists and is used if DQ encounters out-of-domain rating with REJECT_ROW). dim_category/dim_product/dim_shop unknown members: NO — we keep Source A product_sk=shop_sk=NULL (without unknown member filling). This avoids the "fake unknown product" anti-pattern. |
| **R-13** | Future model/issue/DSS/case/intervention tables from dimensional_model.md §2 rows 27–34. | `ARCHITECTURE_DEFECT? → NO (deferred correctly)` | Phase 5 design explicitly labels them Future / Conditional. Plan correctly does NOT create them. Reclassification NONE. |

**Tally:** 0 ARCHITECTURE_DEFECTs; 2 ARCHITECTURE_CLARIFICATIONs (R-01, R-02); 11 IMPLEMENTATION_DETAILs (R-03..R-12 inclusive).

**Phase 5 architecture is IMPLEMENTABLE as-is without redesign.**

---

## 7. PHYSICAL WAREHOUSE PLAN

### 7.1 Schema Decision

**Single schema:** `marketvoice_warehouse`. Justification: single-purpose prototype with 6 core entities + 2–3 metadata/log tables; multi-schema (bronze/silver/gold) separation is over-engineering for this scale and violates `integration_contracts.md §4` anti-over-engineering principle. The "staging" layer is Python in-memory.

### 7.2 Table Roster (Track A MVP Core + Pipeline Metadata)

Every table has explicit grain per §14 rule.

#### 7.2.1 Pipeline Metadata Tables (operational, not dimensional facts)

**Table PM-1: `pipeline_run`**

| Property | Value |
|---|---|
| Purpose | Record one ETL pipeline execution end-to-end for audit/lineage/idempotency. |
| Grain | One row = one orchestrated pipeline run invocation (independent of whether it succeeds or fails). |
| Source | SYSTEM_GENERATED by ETL orchestrator on startup. |
| Natural/source key | `pipeline_run_id` (UUID; generated at orchestrator start). |
| Warehouse key | `pipeline_run_sk` BIGSERIAL PK (optional convenience surrogate). |
| Foreign keys | None. It is the root parent of all lineage references. |
| Attributes | `pipeline_version TEXT NOT NULL`, `started_at TIMESTAMPTZ NOT NULL`, `completed_at TIMESTAMPTZ`, `status TEXT NOT NULL CHECK (status IN ('STARTED','SUCCESS','FAILED','ROLLBACK'))`, `input_rows_total INTEGER`, `accepted_rows_total INTEGER`, `rejected_rows_total INTEGER`, `loaded_rows_total INTEGER`, `git_commit_ref TEXT`, `environment_name TEXT`, `error_message TEXT` (NULL on SUCCESS). |
| Measures | Counts only (integer aggregates of child DQ/load stats). |
| Null policy | Only `completed_at`, `error_message`, and counts may be NULL until load finishes. |
| DQ rules | Pipeline-run status transitions validated by ETL code. |
| Load strategy | INSERT on start; UPDATE `completed_at` + `status` + counts on end. |
| Lineage | SYSTEM_GENERATED `TECHNICAL_METADATA`. |

**Table PM-2: `rejected_record_log`**

| Property | Value |
|---|---|
| Purpose | Accountable trace of every single source row NOT loaded to fact_review with reason codes. |
| Grain | One row = one rejected source record (one row per rejection event; counts are additive). |
| Source | ETL DQ engine during INPUT/TRANSFORMATION/LOAD stages. |
| Natural/source key | `(pipeline_run_id, source_id, source_row_number)`. |
| Warehouse key | `rejection_sk` BIGSERIAL PK. |
| Foreign keys | `pipeline_run_id → pipeline_run.pipeline_run_id`. |
| Attributes | `source_id TEXT NOT NULL`, `source_row_number INTEGER NOT NULL`, `stage TEXT CHECK (stage IN ('INPUT','TRANSFORM','LOAD'))`, `severity TEXT CHECK (severity IN ('CRITICAL','MAJOR','MINOR','INFO'))`, `dq_rule_id TEXT NOT NULL`, `reason TEXT NOT NULL`, `raw_value_snippet TEXT`, `action_applied TEXT DEFAULT 'REJECT_ROW' CHECK (action_applied IN ('BLOCK_LOAD','REJECT_ROW','WARN'))`. |
| Measures | Count by severity / stage / dq_rule_id. |
| Null policy | Only `raw_value_snippet` may be NULL. |
| DQ rules | CRITICAL severity implies action_applied = BLOCK_LOAD (blocks entire run). |
| Load strategy | INSERT-only as rejections are encountered; no updates. Transaction-batched with load. |
| Lineage | SYSTEM_GENERATED `TECHNICAL_METADATA`; referenced by acceptance criteria AC-13. |

**Table PM-3: `data_quality_result` (optional; post-load DQ findings)**

| Property | Value |
|---|---|
| Purpose | Store structured POST_LOAD DQ check outcomes (count-based integrity KPIs). |
| Grain | One row = one DQ check id × one pipeline run. |
| Source | DQ engine post-load step. |
| Natural/source key | `(pipeline_run_id, dq_check_id)`. |
| Warehouse key | `dq_result_sk` BIGSERIAL PK. |
| Foreign keys | `pipeline_run_id → pipeline_run.pipeline_run_id`. |
| Attributes | `dq_check_id TEXT NOT NULL`, `dq_check_name TEXT`, `actual_value NUMERIC`, `expected_min NUMERIC`, `expected_max NUMERIC`, `severity TEXT`, `passed BOOLEAN`, `evidence TEXT`. |
| Measures | actual_value is numerical measure of check outcome. |
| Null policy | expected_min/expected_max NULL for non-range checks; evidence NULL if no auxiliary info. |
| DQ rules | Any CRITICAL passed=FALSE → run status FAIL. |
| Load strategy | Batch INSERT after post-load checks. |
| Lineage | SYSTEM_GENERATED. |

#### 7.2.2 Dimensional Core Tables (Track A MVP — Phase 6 scope)

**Table D-1: `dim_source`**

| Property | Value |
|---|---|
| Purpose | Reference master for registered analytical sources; parent of ALL dimensional entities and facts. |
| Grain | One row = one registered accepted source ID (exactly 2 rows: Source A + Source B). |
| Source | `data/metadata/source_manifest.csv` (governed); `config/data_sources.yaml` (source_id / column register). |
| Natural/source key | `SOURCE_NATIVE: source_id` (values: `SRC_PRDECT_ID_V1`, `SRC_TOKOPEDIA_REVIEWS_2019`). |
| Warehouse key | `source_sk` SMALLSERIAL PK (1,2 assigned; 0 reserved for unknown/audit). |
| Foreign keys | None; dimension root. |
| Attributes | `source_id TEXT NOT NULL UNIQUE`, `source_name TEXT NOT NULL`, `source_role TEXT`, `publisher TEXT`, `canonical_reference TEXT`, `dataset_version TEXT`, `declared_license TEXT`, `license_evidence_type TEXT`, `project_raw_distribution_policy TEXT DEFAULT 'LOCAL_ONLY'`, `raw_filename TEXT`, `sha256 TEXT`, `row_count_manifest INTEGER`, `column_count INTEGER`, `access_date_from_manifest TEXT`. |
| Measures | `row_count_manifest INTEGER` (audit measure). |
| Null policy | Canonical_reference may be NULL for Source A (has DOI in separate field; DOUBLE STORED). |
| DQ rules | UNIQUE(source_id) enforced; source_id ∈ {manifest 2 values}; NOT_NULL on core. |
| Load strategy | DDL seed INSERT ON CONFLICT DO NOTHING (idempotent). 2 rows only. |
| Lineage | GOVERNANCE_REGISTER_DERIVED. |

**Table D-2: `dim_rating`**

| Property | Value |
|---|---|
| Purpose | Closed-domain reference dimension for ordinal 1–5 star ratings. |
| Grain | One row = one permitted rating value (exactly 5 rows). |
| Source | Verified rating domain (Phase 2 forensic audit + raw CSVs reconfirmation §2.3). |
| Natural/source key | `rating_value SMALLINT` (values 1,2,3,4,5). |
| Warehouse key | `rating_sk` SMALLSERIAL PK (1–5 assigned; 0 reserved for unknown not-supplied audit member). |
| Foreign keys | None. |
| Attributes | `rating_value SMALLINT NOT NULL UNIQUE`, `rating_label_en TEXT` ('1 Star'..'5 Star'), `rating_ordinal_rank SMALLINT NOT NULL` (=rating_value; ordinality explicit for queries that may not know domain). |
| Measures | None. Dimension only. |
| Null policy | All attributes NOT NULL. |
| DQ rules | CHECK(rating_value BETWEEN 1 AND 5); UNIQUE(rating_value). |
| Load strategy | DDL seed INSERT ON CONFLICT DO NOTHING. 5 rows only. |
| Lineage | DOMAIN_DERIVED. |

**Table D-3: `dim_category`**

| Property | Value |
|---|---|
| Purpose | Source-aware category dimension. Categories are NOT conformed across sources. |
| Grain | One row = one raw category value within one source (expected 29 Source A + 5 Source B = 34 rows). |
| Source | A: `Category` column (29 unique); B: `category` column (5 unique). |
| Natural/source key | `(source_sk, source_native_category_raw_text)` — compound because same text from two sources is NOT semantically equivalent. |
| Warehouse key | `category_sk` SERIAL PK. |
| Foreign keys | `source_sk → dim_source.source_sk` NOT NULL. |
| Attributes | `source_native_category_raw_text TEXT NOT NULL`, `category_normalized_label TEXT` (same as raw; Phase 6 reserves column for future normalization only if approved; identical value in Phase 6 MVP — no invented mapping). |
| Measures | None. Dimension. |
| Null policy | `category_normalized_label` NOT NULL default = raw (no nullable ambiguity). |
| DQ rules | UNIQUE(source_sk, source_native_category_raw_text). FK to dim_source enforced. |
| Load strategy | Extracted from each source during transform step; upsert by natural key. |
| Lineage | `SOURCE_DERIVED`; lineage_class = SOURCE_AWARE_CATEGORY (not conformed across sources). |

**Table D-4: `dim_product`**

| Property | Value |
|---|---|
| Purpose | Source B product master (Source B only; Source A has NO product entities). |
| Grain | One row = one Source B product listing (expected 3,664 rows; 0 rows from Source A). |
| Source | B: `product_id` + `product_name`. |
| Natural/source key | `(source_sk, source_native_product_id)` — source-qualified because product_id is Source B native. |
| Warehouse key | `product_sk` SERIAL PK. |
| Foreign keys | `source_sk → dim_source.source_sk` NOT NULL CHECK (source_sk = 2 for now; can be relaxed if new B-like sources arrive). |
| Attributes | `source_native_product_id TEXT NOT NULL`, `source_native_product_name TEXT`, `product_name_variant_count SMALLINT DEFAULT 1` (see R-09 — reports if same id had multiple names). |
| Measures | `product_name_variant_count`. |
| Null policy | `source_native_product_name` NULL if all rows had null (but Source B data shows non-null 100% — unverified; plan keeps nullable). |
| DQ rules | UNIQUE(source_sk, source_native_product_id). NO FK to dim_shop (per dimensional_model.md §3 point 2: no direct product↔shop relationship; co-occurrence only via fact_review). |
| Load strategy | Deduplicate unique Source B product_id; insert-or-update by natural key. |
| Lineage | `SOURCE_DERIVED / SOURCE_LOCAL (Source B only)`; KEY CLASS = SOURCE_NATIVE. |

**Table D-5: `dim_shop`**

| Property | Value |
|---|---|
| Purpose | Source B shop identity context (Source B only; 158 rows expected). |
| Grain | One row = one Source B shop identifier. |
| Source | B: `shop_id`. |
| Natural/source key | `(source_sk, source_native_shop_id)`. |
| Warehouse key | `shop_sk` SERIAL PK. |
| Foreign keys | `source_sk → dim_source.source_sk` NOT NULL. |
| Attributes | `source_native_shop_id TEXT NOT NULL` (no shop name column; Source B has none — no invented). |
| Measures | None. |
| Null policy | Core NOT_NULL; no name field so no null name trap. |
| DQ rules | UNIQUE(source_sk, source_native_shop_id). |
| Load strategy | Deduplicate from B; upsert. |
| Lineage | `SOURCE_DERIVED / SOURCE_LOCAL (Source B only)`. |

**Table F-1: `fact_review` (central Track A fact)**

| Property | Value |
|---|---|
| Purpose | One verified accepted review record from exactly one source row. Central analytical fact for Track A MVP. |
| Grain | **ONE SOURCE ROW = ONE FACT ROW.** Accepted records only (rejected rows → rejected_record_log). Expected row count: ≤ 5,400 + ≤ 40,607 = 46,007 total accepted (exact count depends on INPUT/TRANSFORM stage DQ rejections; should be 46,007 if zero failures). |
| Source | A: all 11 raw columns; B: all 8 raw columns + system lineage columns. |
| Natural/source key | `(source_sk, source_native_row_hash)`; see R-08 — `NOT_LINKABLE / WAREHOUSE_INTERNAL` deterministic hash. |
| Warehouse key | `review_sk` BIGSERIAL PK (monotonically increasing; no business meaning). |
| Foreign keys | `source_sk → dim_source.source_sk NOT NULL`; `rating_sk → dim_rating.rating_sk NOT NULL`; `category_sk → dim_category.category_sk NOT NULL`; `product_sk → dim_product.product_sk NULLABLE` (ONLY NON-NULL for Source B; ALWAYS NULL for Source A); `shop_sk → dim_shop.shop_sk NULLABLE` (ONLY NON-NULL for Source B; ALWAYS NULL for Source A); `pipeline_run_id → pipeline_run.pipeline_run_id NOT NULL` (audit line to load run). |
| **Source-agnostic review attributes** | `rating_value SMALLINT NOT NULL` (denormalized + FK for analytical convenience); `review_text TEXT NOT NULL` (A: Customer Review; B: text → preserved original; privacy status tracked in separate boolean columns); `source_gold_sentiment_label TEXT NULLABLE` (Source A only — exact raw Sentiment; NULL B always); `source_gold_emotion_label TEXT NULLABLE` (Source A only — exact raw Emotion; NULL B always); `review_text_privacy_status TEXT NOT NULL DEFAULT 'RAW_PENDING_REVIEW' CHECK (review_text_privacy_status IN ('RAW_PENDING_REVIEW','PRIVACY_OK','REDACTED_REQUIRED'))`. |
| **Source B contextual attributes (NULL for Source A always)** | `source_b_sold_raw_text TEXT NULLABLE`; `source_b_product_url TEXT NULLABLE`. |
| **Source A contextual attributes (NULL for Source B always)** | `source_a_price_text TEXT`, `source_a_overall_rating_text TEXT`, `source_a_number_sold_text TEXT`, `source_a_total_review_text TEXT`, `source_a_location_text TEXT`, `source_a_product_name_text TEXT` (Category already normalized to category_sk; not stored redundantly except via dim_category join). |
| **System audit lineage columns (SYSTEM_GENERATED / TECHNICAL_METADATA_ONLY)** | `source_row_number INTEGER NOT NULL` (zero-padded row number in source CSV 1-based); `source_native_row_hash TEXT NOT NULL` (R-08); `source_file_sha256 TEXT NOT NULL` (from manifest for run verification); `ingested_at TIMESTAMPTZ NOT NULL` (time extract step read this row; NEVER authentic review time); `processed_at TIMESTAMPTZ NOT NULL` (time transform standardized this row; NEVER authentic review time); `loaded_at TIMESTAMPTZ NOT NULL` (time insert executed; NEVER authentic review time); `is_synthetic BOOLEAN NOT NULL DEFAULT FALSE` (FALSE always in Track A MVP; synthetic path sets TRUE — separate authorization only). |
| Measures | `rating_value` (ordinal; QWK/MAE subject of Phase 8); implicit COUNT(review_sk) per-dimension. |
| Null policy | rating_value NOT NULL; source_gold_sentiment_label / source_gold_emotion_label: NULL for B, NON-NULL for A (enforced by check constraint below); product_sk/shop_sk: NULL for A, NON-NULL for B validated via DQ (not enforced by FK to avoid future flexibility issues, but DQ check DQ-FK-B-001 reports MAJOR if any Source B row has NULL product_sk). |
| DQ rules (enforced by constraints + DQ engine) | 1. CHECK(rating_value BETWEEN 1 AND 5); 2. CHECK(is_synthetic = FALSE OR (source_gold_sentiment_label IS NULL AND source_gold_emotion_label IS NULL AND source_a_price_text IS NULL)) — synthetic rows never masquerade as authentic A with labels; 3. CHECK(NOT(source_sk = 1 AND product_sk IS NOT NULL)) — Source A never has product; 4. CHECK(NOT(source_sk = 1 AND shop_sk IS NOT NULL)) — Source A never has shop; 5. UNIQUE(source_sk, source_native_row_hash) — idempotency at DB level. |
| Load strategy | Transactional batch INSERT only within a single BEGIN...COMMIT; see §12. |
| Lineage | Fact-attribute classification per §31 S2T mapping below. Every attribute is SOURCE_DERIVED or SYSTEM_GENERATED. Zero unexplained fields. |

### 7.3 Extension Points for Future Phases (No Tables Created in Phase 6)

The following Phase 5 entities are explicitly documented as FUTURE; Phase 6 DDL does NOT contain a single CREATE TABLE statement for them:

- `dim_model`, `fact_model_prediction`, `fact_model_evaluation` (Phase 8–9)
- `dim_issue`, `fact_issue_prediction` (Phase 9, conditional)
- `fact_decision_support` (Phase 10, conditional)
- `fact_case`, `fact_intervention` (Phase 10–11, Track B conditional, NOT AUTHORIZED)

`sql/warehouse/` directory will have a placeholder comment-only file `099_future_phases_reserved.sql` that explicitly lists them — zero executable DDL in it.

### 7.4 Phase 6 "Marts" (VIEWS — per R-01 CLARIFICATION)

To satisfy the DEL-08 wording "DDL scripts creating staging, DW, **and marts**", Phase 6 creates 6 lightweight VIEWS only. They are NOT materialized (so DDL CREATE VIEW; no load). Real Phase 7 DEL-11 marts will likely reuse/extend these or replace them.

| View Name | Purpose | Base table(s) |
|---|---|---|
| `mv_source_summary` | Reviews per source: count, rating mean, sentiment/emotion counts (A only) | fact_review + dim_source + dim_rating |
| `mv_category_summary_source_specific` | Reviews per category **WITHIN each source** (source-aware; no cross-category join) | fact_review + dim_category + dim_source |
| `mv_product_b_summary` | Source B product-level review counts / rating mean (product_id only; no cross-source) | fact_review (WHERE source_sk=2) + dim_product |
| `mv_shop_b_summary` | Source B shop-level review counts / rating mean (shop_id only) | fact_review (WHERE source_sk=2) + dim_shop |
| `mv_source_a_label_breakdown` | Source A gold sentiment × emotion × rating crosstab base | fact_review (WHERE source_sk=1) |
| `mv_pipeline_run_recent` | Last 20 pipeline runs with status (DQ/ops surface) | pipeline_run + data_quality_result |

**CRITICAL:** Every view definition explicitly filters by `source_sk` for product/shop domains (prevents accidental cross-source aggregates). Category views always GROUP BY `(source_sk, category_sk)`, never by category text alone.

---

## 8. TABLE GRAIN / KEY REGISTER

Consolidated register of every Phase 6 physical table with classification per §16 key policy:

| Table / View | Grain (one row =) | Source Key | Natural Key Compound | Warehouse PK | FKs | Key Classification |
|---|---|---|---|---|---|---|
| `pipeline_run` | One ETL execution run | UUID `pipeline_run_id` | `pipeline_run_id` | `pipeline_run_sk` BIGSERIAL | None | WAREHOUSE_INTERNAL |
| `rejected_record_log` | One rejected source row | Source_id + row# | `(pipeline_run_id, source_id, source_row_number)` | `rejection_sk` BIGSERIAL | pipeline_run → PM-1 | WAREHOUSE_INTERNAL (for source identity audit) |
| `data_quality_result` | One DQ check × one run | Check id | `(pipeline_run_id, dq_check_id)` | `dq_result_sk` BIGSERIAL | pipeline_run → PM-1 | WAREHOUSE_INTERNAL |
| `dim_source` | One accepted source | `source_id` (SRC_PRDECT_ID_V1 / SRC_TOKOPEDIA_REVIEWS_2019) | `source_id` UNIQUE | `source_sk` SMALLSERIAL | None | SOURCE_NATIVE (mapped from manifest) |
| `dim_rating` | One rating value | `rating_value` 1..5 | `rating_value` UNIQUE | `rating_sk` SMALLSERIAL | None | DOMAIN_CLOSED (verifiable from data) |
| `dim_category` | One category text × one source | Raw category text | `(source_sk, raw_category)` UNIQUE | `category_sk` SERIAL | source_sk → dim_source | SOURCE_NATIVE, NOT_LINKABLE across sources |
| `dim_product` | One Source B product listing | Source B `product_id` | `(source_sk, product_id)` UNIQUE | `product_sk` SERIAL | source_sk → dim_source | SOURCE_NATIVE (Source B scope) |
| `dim_shop` | One Source B shop context | Source B `shop_id` | `(source_sk, shop_id)` UNIQUE | `shop_sk` SERIAL | source_sk → dim_source | SOURCE_NATIVE (Source B scope) |
| `fact_review` | **One accepted review × one source row** (ONE_FACT_ONE_GRAIN) | Source row# × source_id → deterministic hash | `(source_sk, source_native_row_hash)` UNIQUE | `review_sk` BIGSERIAL | source_sk/rating_sk/category_sk + nullable product_sk/shop_sk + pipeline_run_id | WAREHOUSE_INTERNAL (not cross-source linkable) |

Key classification rules applied (§16):
- `SOURCE_NATIVE`: dim_source (source_id), dim_product (product_id Source B), dim_shop (shop_id Source B), dim_category (raw per source)
- `WAREHOUSE_INTERNAL`: pipeline_run, rejected_record_log, data_quality_result, fact_review review_sk/hash
- `CROSS_SOURCE_VALIDATED`: None (FORBIDDEN; CROSS_SOURCE_LINKAGE=NOT_SUPPORTED)
- `NOT_LINKABLE`: dim_category (A categories vs B categories with same text are different entities); fact_review hash (NOT entity match)
- No surrogate key anywhere is claimed to represent a real-world cross-source identity.

---

## 9. SOURCE-TO-TARGET MAPPING PLAN

Per §31 requirement. Every target warehouse field has explicit provenance. Classification: `SOURCE_DERIVED` (exact raw or deterministic transform) vs. `SYSTEM_GENERATED` (pipeline internal). Shown for dimensional entities + fact_review; metadata tables are implicitly SYSTEM_GENERATED.

### 9.1 dim_source (2 rows)

| target_table | target_field | source | source_field | transformation | null_rule | DQ_rule | lineage_class |
|---|---|---|---|---|---|---|---|
| dim_source | source_id | source_manifest.csv | source_id | Exact text | NOT NULL | UNIQUE; ∈ manifest | GOVERNANCE_DERIVED (SOURCE_DERIVED) |
| dim_source | source_name | source_manifest.csv | source_name | Exact text | NOT NULL | Non-empty string | SOURCE_DERIVED |
| dim_source | source_role | source_manifest.csv | source_role | Exact text | NOT NULL | ∈ {PRIMARY.., SECONDARY..} | SOURCE_DERIVED |
| dim_source | publisher | source_manifest.csv | publisher | Exact text | NULLABLE if blank | — | SOURCE_DERIVED |
| dim_source | canonical_reference | source_manifest.csv | canonical_reference | Exact text | NULLABLE for Source A (has DOI) | — | SOURCE_DERIVED |
| dim_source | dataset_version | source_manifest.csv | dataset_version | Exact text | NULLABLE | — | SOURCE_DERIVED |
| dim_source | declared_license | source_manifest.csv | license_declared | Exact text | NOT NULL | Non-empty | SOURCE_DERIVED |
| dim_source | license_evidence_type | source_manifest.csv | license_evidence_type | Exact text | NOT NULL | — | SOURCE_DERIVED |
| dim_source | project_raw_distribution_policy | source_manifest.csv | project_raw_distribution_policy | Exact text | NOT NULL DEFAULT LOCAL_ONLY | =LOCAL_ONLY (Phase 6 frozen) | SOURCE_DERIVED |
| dim_source | raw_filename | source_manifest.csv | raw_filename | Exact text | NOT NULL | Non-empty | SOURCE_DERIVED |
| dim_source | sha256 | source_manifest.csv | sha256 | Exact text | NOT NULL | Matches computed hash at extract time (DQ-INTEGRITY-001) | SOURCE_DERIVED |
| dim_source | row_count_manifest | source_manifest.csv | row_count | Exact integer cast | NOT NULL | Equals actual csv reader count (DQ-INTEGRITY-002) | SOURCE_DERIVED |
| dim_source | column_count | source_manifest.csv | column_count | Exact integer cast | NOT NULL | Equals csv header len | SOURCE_DERIVED |
| dim_source | access_date_from_manifest | source_manifest.csv | access_date | Exact text (ISO preserved; not parsed to date) | NULLABLE | — | SOURCE_DERIVED |

### 9.2 dim_rating (5 rows — DOMAIN_DERIVED)

| target_field | source | transformation | null_rule | DQ_rule | lineage_class |
|---|---|---|---|---|---|
| rating_value | Verified rating domain (Phase 2) | 1..5 literal | NOT NULL | CHECK 1..5; UNIQUE | DOMAIN_DERIVED (SOURCE_VERIFIED) |
| rating_label_en | Static mapping | '1 Star'..'5 Star' | NOT NULL | Non-empty | SYSTEM_GENERATED (label) |
| rating_ordinal_rank | Verified ordinality | = rating_value | NOT NULL | = rating_value | DOMAIN_DERIVED |

### 9.3 dim_category (29 A + 5 B = 34 rows)

| target_field | source_field (per source) | transformation | null_rule | DQ_rule | lineage_class |
|---|---|---|---|---|---|
| source_sk (FK) | A=1, B=2 | Assigned via dim_source | NOT NULL | FK → dim_source | SOURCE_DERIVED |
| source_native_category_raw_text | A: `Category`; B: `category` | Exact case-preserving raw | NOT NULL | UNIQUE with source_sk | SOURCE_DERIVED |
| category_normalized_label | same raw | copy identical (no norm in Phase 6) | NOT NULL DEFAULT raw | = raw text | SOURCE_DERIVED (no invented meaning) |

### 9.4 dim_product (3,664 rows — B only)

| target_field | source_field (B) | transformation | null_rule | DQ_rule | lineage_class |
|---|---|---|---|---|---|
| source_sk (FK) | fixed=2 | Assigned | NOT NULL | FK; =2 for MVP | SOURCE_DERIVED |
| source_native_product_id | `product_id` | Exact text from B | NOT NULL | UNIQUE with source_sk | SOURCE_NATIVE |
| source_native_product_name | `product_name` | First-most frequent per product_id | NULLABLE if missing | DQ-DIM-PRODUCT-001 name-variant count reported | SOURCE_DERIVED |
| product_name_variant_count | per product_id distinct product_name | COUNT(distinct name) | NOT NULL DEFAULT 1 | If >1 → MAJOR warning | SYSTEM_GENERATED (statistic) |

### 9.5 dim_shop (158 rows — B only)

| target_field | source_field (B) | transformation | null_rule | DQ_rule | lineage_class |
|---|---|---|---|---|---|
| source_sk (FK) | fixed=2 | Assigned | NOT NULL | FK → dim_source | SOURCE_DERIVED |
| source_native_shop_id | `shop_id` | Exact text from B | NOT NULL | UNIQUE with source_sk | SOURCE_NATIVE |

### 9.6 fact_review (≤ 5,400 A + ≤ 40,607 B rows)

#### Key / FK Columns

| target_field | source / rule | transformation | null_rule | DQ_rule | lineage_class |
|---|---|---|---|---|---|
| review_sk | WAREHOUSE_INTERNAL | BIGSERIAL assign | NOT NULL PK | — | WAREHOUSE_INTERNAL |
| source_sk | A=1, B=2 | From dim_source | NOT NULL | FK; CHECK ∈{1,2} MVP | SOURCE_DERIVED |
| rating_sk | rating_value 1..5 → dim_rating | JOIN lookup | NOT NULL | FK → dim_rating | DOMAIN_JOIN |
| category_sk | A: raw Category + source_sk=1 → dim_category; B: raw category + source_sk=2 → dim_category | Natural key JOIN | NOT NULL | FK → dim_category | SOURCE_JOIN |
| product_sk | B only: product_id + source_sk=2 → dim_product | Natural key JOIN | NULL for A; NON-NULL expected for B (enforced by DQ not constraint) | DQ-FK-B-001: Source B rows with product_sk NULL → MAJOR | SOURCE_JOIN |
| shop_sk | B only: shop_id + source_sk=2 → dim_shop | Natural key JOIN | NULL for A; NON-NULL expected for B | DQ-FK-B-002: B rows with shop_sk NULL → MAJOR | SOURCE_JOIN |
| pipeline_run_id | Current run UUID | From orchestrator | NOT NULL | FK → pipeline_run | SYSTEM_GENERATED |

#### Analytical Attribute Columns

| target_field | source_field | transformation | null_rule | DQ_rule | lineage_class |
|---|---|---|---|---|---|
| rating_value | A: `Customer Rating`; B: `rating` | Cast A → SMALLINT; B string '1'..'5' → SMALLINT | NOT NULL | CHECK 1..5 | SOURCE_DERIVED |
| review_text | A: `Customer Review`; B: `text` | Preserve original Unicode; NO silent trimming | NOT NULL | Non-empty string (whitespace-only validation → MAJOR) | SOURCE_DERIVED |
| source_gold_sentiment_label | A: `Sentiment` | Exact text (Positive/Negative preserved case) | Source A NON-NULL; Source B ALWAYS NULL | DQ-LABEL-A-001: A rows must be ∈{Positive,Negative}; DQ-LABEL-B-001: B rows must be NULL | SOURCE_DERIVED (gold scope A only) |
| source_gold_emotion_label | A: `Emotion` | Exact text 5-class preserved | A NON-NULL; B ALWAYS NULL | DQ-LABEL-A-002: A rows ∈{Happy,Sadness,Fear,Love,Anger}; DQ-LABEL-B-002: B NULL always | SOURCE_DERIVED (gold scope A only) |
| review_text_privacy_status | SYSTEM_DEFAULT | `RAW_PENDING_REVIEW` | NOT NULL DEFAULT | CHECK enum | SYSTEM_GENERATED (governance state) |

#### Source-B Contextual Columns

| target_field | source_field (B) | transformation | null_rule | DQ_rule | lineage_class |
|---|---|---|---|---|---|
| source_b_sold_raw_text | `sold` | Exact text preserved (no numeric parsing) | NULL if empty/whitespace in raw | DQ-CONTEXT-B-SOLD-001: count NULL + non-NULL INFO | SOURCE_DERIVED |
| source_b_product_url | `product_url` | Exact text preserved | NULL if empty | DQ-DISPLAY-001: column restricted INFO | SOURCE_DERIVED |

#### Source-A Contextual Columns

| target_field | source_field (A) | transformation | null_rule | DQ_rule | lineage_class |
|---|---|---|---|---|---|
| source_a_price_text | `Price` | Exact text; NO currency parsing | NOT NULL (verified 0 empty) | Non-empty | SOURCE_DERIVED |
| source_a_overall_rating_text | `Overall Rating` | Exact text preserved | NOT NULL | Non-empty | SOURCE_DERIVED |
| source_a_number_sold_text | `Number Sold` | Exact text preserved | NOT NULL | Non-empty | SOURCE_DERIVED |
| source_a_total_review_text | `Total Review` | Exact text preserved | NOT NULL | Non-empty | SOURCE_DERIVED |
| source_a_location_text | `Location` | Exact text preserved | NOT NULL | Non-empty | SOURCE_DERIVED |
| source_a_product_name_text | `Product Name` | Exact text preserved | NOT NULL | Non-empty | SOURCE_DERIVED |

#### System Audit / Technical Timestamp Columns

**Classification: TECHNICAL_METADATA_ONLY. Never authentic review-event times.**

| target_field | origin | transformation | null_rule | DQ_rule | lineage_class |
|---|---|---|---|---|---|
| source_row_number | 1-based row# in CSV | Integer counted at extract | NOT NULL | ≥1 | WAREHOUSE_INTERNAL |
| source_native_row_hash | sha256(source_id + '|' + zero_padded_6digit_row) | hashlib.sha256.hexdigest | NOT NULL | UNIQUE with source_sk | WAREHOUSE_INTERNAL (NOT_LINKABLE across sources) |
| source_file_sha256 | data/metadata/source_manifest.csv sha256 column | Exact copy per source | NOT NULL | Matches actual file hash computed at extraction (DQ-INTEGRITY-001) | SOURCE_DERIVED (governance) |
| ingested_at | ETL extract time | `datetime.now(timezone.utc)` | NOT NULL | ≤ processed_at ≤ loaded_at (asserted post-load) | SYSTEM_GENERATED — TECHNICAL TIMESTAMP NOT REVIEW TIME |
| processed_at | ETL transform complete | UTC | NOT NULL | ≥ ingested_at | SYSTEM_GENERATED — TECHNICAL TIMESTAMP NOT REVIEW TIME |
| loaded_at | ETL insert commit | UTC | NOT NULL | ≥ processed_at | SYSTEM_GENERATED — TECHNICAL TIMESTAMP NOT REVIEW TIME |
| is_synthetic | Configuration flag `ENABLE_TRACK_B` | FALSE always for A + B MVP authentic | NOT NULL DEFAULT FALSE | DQ-SYNTH-001: Track A/B authentic rows count FALSE = 5,400+40,607; TRUE=0 | SYSTEM_GENERATED (Track B isolation) |

### 9.7 Zero Unexplained Fields Assertion

All fields in all 6 dimensional/metadata + 3 operational tables above are enumerated. Every field has: `target_table + target_field + source + source_field + transformation + null_rule + DQ_rule + lineage_class`.

`UNEXPLAINED_WAREHOUSE_FIELDS = 0`

---

## 10. ETL DESIGN

### 10.1 Flow Diagram (§17 required steps)

```
EXTRACT → INPUT_VALIDATION → STANDARDIZE → TRANSFORM → DATA_QUALITY → LOAD → RECONCILE → REPORT
  │          │                  │              │            │            │        │         │
  │          │                  │              │            │            │        │         └─> write run_id status SUCCESS/FAIL
  │          │                  │              │            │            │        └─> post-checks: row counts; referential integrity
  │          │                  │              │            │            └─> transactional INSERT only; all-or-nothing
  │          │                  │              │            └─> per-row + post-group checks; write rejected_record_log for rejects
  │          │                  │              └─> build dimension rows from distinct; build fact row per accepted record; join FKs
  │          │                  └─> column names snake_case; encoding utf8; rating cast; null normalization; preserve text
  │          └─> file existence; sha256 match; schema match; row count match; rating domain sample
  └─> open file readonly (mode='r'); no write handle; read DictReader with utf-8; produce source_rows list
```

### 10.2 Staging (Python In-Memory; R-01 CLARIFICATION)

Two DataFrame / dict-list staging structures in Python memory:

| Staging structure | Contents | Equivalent conceptual stage |
|---|---|---|
| `staging_a_rows : list[dict]` | 5,400 dict rows from A CSV under key=official_source_columns | Raw A stage |
| `staging_b_rows : list[dict]` | 40,607 dict rows from B CSV | Raw B stage |
| `standardized_a_rows` | After INPUT_VALIDATION + STANDARDIZE: column renamed to snake_case; row hash added; source_row_number added; manifest SHA attached | Standardized A |
| `standardized_b_rows` | Same | Standardized B |
| `transformed_dim_rows` | Dict of lists: dim_category_a, dim_category_b, dim_product, dim_shop (distinct) | Dimension build |
| `transformed_fact_rows` | list[dict] — 46,007 candidate fact rows with all field names + values aligned to target columns | Fact build |

No DB staging tables. No separate CSV written to disk during ETL. All transformation is pure Python in-memory. Low memory footprint (~10–20 MB peak for 46K rows).

### 10.3 Extract

Contract:

- **Input 1:** `config/project_settings.yaml → paths.data_raw` (root).
- **Input 2:** `config/data_sources.yaml → source_a.local_path`, `source_b.local_path` (relative to project root; resolved via `get_project_root()`).
- **Input 3:** `data/metadata/source_manifest.csv` (registered SHA256 + row_count + column_count per source_id).
- **Actions:**
  1. Verify each source file **exists**; raise BLOCK_LOAD if missing.
  2. Verify each source file opens successfully with `encoding='utf-8'` (read-only `mode='r'`; NEVER open raw with `'w'` or `'a'`).
  3. Compute SHA256 of each file with streaming `hashlib.sha256` (constant memory). Compare against manifest; mismatch → DQ-INTEGRITY-001 CRITICAL → BLOCK_LOAD.
  4. Read header row → compare against `official_columns` from `data_sources.yaml`; order-sensitive? NO (use DictReader key-based access); column superset required (ALL official columns must exist; extra columns → MAJOR warning but not blocking).
  5. Count rows → compare to manifest row_count; mismatch → CRITICAL → BLOCK_LOAD.
  6. Produce list[dict] rows; record 1-based row number per row.
- **Validation:** DQ checks DQ-INTEGRITY-001/002/003/004 CRITICAL on failure.

### 10.4 Input Validation (per-row stage)

| DQ Rule | Scope | Severity | Action | Checks |
|---|---|---|---|---|
| DQ-INPUT-RATING | Both A/B row | MAJOR per bad row; ≥1 present in 1% of rows → CRITICAL | REJECT_ROW bad | rating_value not null; castable to SMALLINT; ∈1..5 |
| DQ-INPUT-TEXT | Both | MAJOR per bad row; ≥1% → CRITICAL | REJECT_ROW | review_text non-empty after `.strip()`; len > 0 |
| DQ-INPUT-LABEL-A | Source A row | MAJOR per bad; ≥1% → CRITICAL | REJECT_ROW | sentiment ∈{Positive,Negative}; emotion ∈{Happy,Sadness,Fear,Love,Anger} |
| DQ-INPUT-NULL-LABEL-B | Source B row | MAJOR per bad | WARN | Verify sentiment/emotion column does NOT exist (to catch accidental future B enrichment) — not a row reject, run-wide check |
| DQ-INPUT-PROD-B | Source B row | MAJOR | REJECT_ROW | product_id non-empty |
| DQ-INPUT-SHOP-B | Source B row | MAJOR | REJECT_ROW | shop_id non-empty |
| DQ-INPUT-CAT | Both | MAJOR | REJECT_ROW | category non-empty |

**Reject accounting:** Every rejected row → INSERT 1 entry to rejected_record_log (with reason_code, severity, stage='INPUT') BEFORE any fact load occurs. Rejections are tracked even if load is blocked.

### 10.5 Standardize

Column rename + type normalization. Never invents meaning. Only:

| Source A raw column | Standardized field name | Standardization |
|---|---|---|
| Category | category_raw | Exact text |
| Product Name | product_name_raw | Exact text (→ source_a_product_name_text later) |
| Location | location_raw | → source_a_location_text |
| Price | price_raw | → source_a_price_text |
| Overall Rating | overall_rating_raw | → source_a_overall_rating_text |
| Number Sold | number_sold_raw | → source_a_number_sold_text |
| Total Review | total_review_raw | → source_a_total_review_text |
| Customer Rating | customer_rating_raw | cast to SMALLINT rating_value |
| Customer Review | customer_review_raw | review_text |
| Sentiment | sentiment_raw | source_gold_sentiment_label |
| Emotion | emotion_raw | source_gold_emotion_label |

| Source B raw column | Standardized field name | Standardization |
|---|---|---|
| text | text_raw | review_text |
| rating | rating_raw | string→SMALLINT rating_value |
| category | category_raw | category_raw |
| product_name | product_name_raw | source_native_product_name |
| product_id | product_id_raw | source_native_product_id |
| sold | sold_raw | → source_b_sold_raw_text |
| shop_id | shop_id_raw | source_native_shop_id |
| product_url | product_url_raw | → source_b_product_url |

Whitespace handling: collapse internal whitespace only in `review_text` if it contains 2+ consecutive newlines only (log count of normalized). `category_raw / product_id_raw / shop_id_raw` are `.strip()`ped (both ends only). **Never** remove punctuation or stopwords from review_text in ETL standardize (that is Phase 8 preprocessing — separate governed step under `experiment_settings.yaml` duplicate_policy only, not global warehouse).

Null representation: empty/whitespace-only `sold_raw` → set Python `None` → stored as SQL NULL in fact_review.source_b_sold_raw_text.

### 10.6 Transform

Builds dimension candidates and fact rows:

1. **dim_category candidates** = distinct (source_sk, category_raw) from each standardized source.
2. **dim_product candidates** = distinct (source_sk=2, product_id_raw) from B → keep first product_name_raw; count name variants.
3. **dim_shop candidates** = distinct (source_sk=2, shop_id_raw) from B.
4. **fact_review candidates** = one per accepted standardized row:
   - compute source_native_row_hash = sha256(f"{source_id}|{row_number:06d}")
   - attach source_file_sha256 from manifest per source_sk
   - attach ingested_at, processed_at UTC stamps
   - join (via in-memory dict lookups, not SQL yet) category_sk/product_sk/shop_sk placeholders (to be re-looked-up after dims are loaded; because dims get serial SKs assigned).
5. is_synthetic=False always for authentic rows.

Transform is pure: same input rows → identical output values (deterministic except 3 UTC timestamps which capture wall-clock; all lineage hash/IDs are deterministic regardless of timing).

### 10.7 Load

- **Deterministic full refresh strategy (§19 idempotency justification):** dataset is 46K rows, <10 MB CSV, local Postgres. Full refresh avoids CDC/incremental/watermark complexity. For this S2 prototype scale, full refresh is the simplest valid strategy and guarantees idempotency: re-running same pipeline version + same validated source → final warehouse state identical (same fact row count, same dimension row count; same SK values preserved because dims loaded by upsert on natural key, not recreated from scratch).
- **Load order (FK dependency topo sort):**
  1. pipeline_run → INSERT STARTED row
  2. dim_source → idempotent seed (already exists; no-op or count reported)
  3. dim_rating → idempotent seed (5 rows; always exists)
  4. dim_category → per natural key `INSERT ON CONFLICT DO UPDATE` (no-attr-change; just ensure exists; retrieve category_sk map)
  5. dim_product → per natural key upsert (retrieve product_sk map)
  6. dim_shop → per natural key upsert (retrieve shop_sk map)
  7. Relabel fact_review candidate rows with now-known real SKs (lookups from step 4–6 Python dict maps)
  8. `INSERT INTO fact_review (...) VALUES ... ON CONFLICT (source_sk, source_native_row_hash) DO NOTHING` — idempotent re-runs do not duplicate rows even if refresh accidentally runs twice (but TRUNCATE below normally clears them)
- **Full refresh clarification:** Before step 2, the orchestrator executes:
  ```
  TRUNCATE fact_review, dim_category, dim_product, dim_shop, rejected_record_log, data_quality_result RESTART IDENTITY CASCADE;
  ```
  dim_source/dim_rating/pipeline_run are NOT truncated (seed/master). This means: source-agnostic dimensions preserved between runs; dynamic source-local dims + facts reset per run. TRUNCATE is the simplest correct full-refresh approach for this scale (≤0.01s for 46K rows).
- **Transaction Safety (§20):** Steps 1–8 above are wrapped in a single `BEGIN TRANSACTION ISOLATION LEVEL READ COMMITTED; ... COMMIT;` block. If ANY step throws exception → `ROLLBACK`; pipeline_run.status = 'FAILED'; no partial state visible to downstream consumers. Failed ETL ≠ partially accepted warehouse state (§20 compliance).
- **Rejected_record_log load:** Rejections encountered in INPUT_VALIDATION/TRANSFORM steps are batched and inserted to rejected_record_log inside the same transaction. If the load rolls back, rejection log rows also roll back; but the orchestrator also writes a local JSON file copy to `logs/pipeline_rejections_{run_id}.json` LOCAL_ONLY so rejected audit survives DB rollback.

### 10.8 Reconcile

After COMMIT, orchestrator runs post-load queries:
1. `SELECT COUNT(*) FROM fact_review WHERE source_sk=1` → should equal 5,400 minus rejected count
2. `SELECT COUNT(*) FROM fact_review WHERE source_sk=2` → should equal 40,607 minus rejected count
3. `SELECT COUNT(DISTINCT product_sk) FROM fact_review WHERE source_sk=2` → ≤ 3,664
4. `SELECT COUNT(DISTINCT shop_sk) FROM fact_review WHERE source_sk=2` → ≤ 158
5. Source A integrity: `SELECT COUNT(*) FROM fact_review WHERE source_sk=1 AND product_sk IS NOT NULL` → MUST = 0 (hard post-load DQ CRITICAL)
6. Source A integrity: `SELECT COUNT(*) FROM fact_review WHERE source_sk=1 AND shop_sk IS NOT NULL` → MUST = 0 (hard post-load DQ CRITICAL)
7. Source B label integrity: `SELECT COUNT(*) FROM fact_review WHERE source_sk=2 AND (source_gold_sentiment_label IS NOT NULL OR source_gold_emotion_label IS NOT NULL)` → MUST = 0 (hard CRITICAL)
8. Rating domain coverage: `SELECT rating_value, COUNT(*) FROM fact_review GROUP BY 1 ORDER BY 1` → all 5 values present in both A and B individually (B might have only ≥3; verify domain non-empty only)

Mismatch beyond tolerance (any hard-CRITICAL CHECK above non-zero) → pipeline_run.status set to 'FAILED' immediately; rollback was already done but we re-check.

### 10.9 Report

Write `logs/pipeline_report_{run_id}.json` LOCAL_ONLY with:
- `run_id`, `started_at`, `completed_at`, `status`
- per-source: `input_rows`, `accepted_rows`, `rejected_rows`, `loaded_rows`
- per-DQ-check: check_id, passed, actual_value, severity, evidence (matches data_quality_result table)
- sha256 of source files (computed) vs manifest (stored)
- row counts of dims + facts post-load
- `ETL_VERSION = "marketvoice-etl/0.1.0/phase6"`

---

## 11. DATA QUALITY DESIGN

### 11.1 Four-Layer Coverage (§18)

```
INPUT → TRANSFORMATION → LOAD → POST_LOAD
 (file/row level)   (value-level)   (FK/constraint)   (aggregate/referential)
```

### 11.2 DQ Rule Roster (complete with severity + action)

| DQ Check ID | Layer | Scope | Description | Severity on Fail | Action | Reject Reason Code (if row-based) |
|---|---|---|---|---|---|---|
| DQ-INTEGRITY-001 | INPUT | Run × source | Source file SHA256 matches manifest | CRITICAL | BLOCK_LOAD | — |
| DQ-INTEGRITY-002 | INPUT | Run × source | Row count = manifest row_count exactly | CRITICAL | BLOCK_LOAD | — |
| DQ-INTEGRITY-003 | INPUT | Run × source | Column superset = data_sources.yaml expected | CRITICAL | BLOCK_LOAD | — |
| DQ-INTEGRITY-004 | INPUT | Run × source | File readable UTF-8; no decode error | CRITICAL | BLOCK_LOAD | — |
| DQ-INTEGRITY-005 | INPUT | Run | Raw file open handle read-only; verify no write fds to data/raw | CRITICAL | BLOCK_LOAD | — |
| DQ-INPUT-RATING-001 | INPUT | Per row A | Customer Rating ∈1..5 int | MAJOR | REJECT_ROW | INVALID_RATING |
| DQ-INPUT-RATING-002 | INPUT | Per row B | rating string castable to 1..5 int | MAJOR | REJECT_ROW | INVALID_RATING |
| DQ-INPUT-RATING-RUN | INPUT | Run | Total rating rejection < 1% of rows for each source | CRITICAL if ≥1% | BLOCK_LOAD | — |
| DQ-INPUT-TEXT-001 | INPUT | Per row both | review_text.strip() non-empty | MAJOR | REJECT_ROW | EMPTY_TEXT |
| DQ-INPUT-TEXT-RUN | INPUT | Run | Total text rejects < 1% | CRITICAL if ≥1% | BLOCK_LOAD | — |
| DQ-INPUT-LABEL-A-SENT | INPUT | Per row A | sentiment ∈ {Positive, Negative} | MAJOR | REJECT_ROW | INVALID_SENTIMENT |
| DQ-INPUT-LABEL-A-EMO | INPUT | Per row A | emotion ∈ 5-class set | MAJOR | REJECT_ROW | INVALID_EMOTION |
| DQ-INPUT-LABEL-A-RUN | INPUT | Run | A label rejects < 1% | CRITICAL if ≥1% | BLOCK_LOAD | — |
| DQ-INPUT-PROD-B | INPUT | Per row B | product_id non-empty | MAJOR | REJECT_ROW | MISSING_PRODUCT_ID |
| DQ-INPUT-SHOP-B | INPUT | Per row B | shop_id non-empty | MAJOR | REJECT_ROW | MISSING_SHOP_ID |
| DQ-INPUT-CAT | INPUT | Per row both | category non-empty | MAJOR | REJECT_ROW | MISSING_CATEGORY |
| DQ-TR-NORM-001 | TRANSFORM | Run | Review text normalize count ≤ 5% (collapse of extreme whitespace only) | INFO | WARN | — |
| DQ-TR-HASH-001 | TRANSFORM | Run | Deterministic hash reproducibility: rehash 10% sample and must equal stored | MAJOR | BLOCK_LOAD on failure | — |
| DQ-TR-DIM-PROD-001 | TRANSFORM | Run | product_name_variant_count > 1 rows: count & list top 5 products with multiple names | MAJOR | WARN | — |
| DQ-LBL-B-SENT-001 | TRANSFORM | Run-wide (not per row) | B rows carry sentiment label column → if exists anywhere in B raw: unexpected! (prevents accidental B label contamination) | CRITICAL | BLOCK_LOAD | — |
| DQ-LBL-B-EMO-001 | TRANSFORM | Run-wide | Same for emotion label column in B | CRITICAL | BLOCK_LOAD | — |
| DQ-LOAD-FK-CAT | LOAD | Per row | category_sk lookup succeeds for all fact rows | MAJOR | REJECT_ROW (log only before load; fail if any) | UNKNOWN_CATEGORY |
| DQ-LOAD-FK-B-PRODUCT | LOAD | Per B row | product_sk lookup success | MAJOR | REJECT_ROW if any | MISSING_PRODUCT_DIM |
| DQ-LOAD-FK-B-SHOP | LOAD | Per B row | shop_sk lookup success | MAJOR | REJECT_ROW if any | MISSING_SHOP_DIM |
| DQ-LOAD-UNQ-HASH | LOAD | Post batch | No duplicate (source_sk, source_native_row_hash) in batch | CRITICAL | BLOCK_LOAD on any | — |
| DQ-POST-COUNT-A | POST_LOAD | Run | fact_review A count = 5,400 - INPUT rejects | CRITICAL if off | BLOCK_LOAD (rollback) | — |
| DQ-POST-COUNT-B | POST_LOAD | Run | fact_review B count = 40,607 - INPUT rejects | CRITICAL if off | BLOCK_LOAD (rollback) | — |
| DQ-POST-NOPROD-A | POST_LOAD | Run | A rows with product_sk NOT NULL = 0 | CRITICAL if > 0 | BLOCK_LOAD (rollback) | — |
| DQ-POST-NOSHOP-A | POST_LOAD | Run | A rows with shop_sk NOT NULL = 0 | CRITICAL if > 0 | BLOCK_LOAD (rollback) | — |
| DQ-POST-NOLABEL-B | POST_LOAD | Run | B rows with sent/emo label NOT NULL = 0 | CRITICAL if > 0 | BLOCK_LOAD (rollback) | — |
| DQ-POST-RATING-DOM | POST_LOAD | Run | rating_value only 1..5 | CRITICAL if any outside | BLOCK_LOAD (rollback) | — |
| DQ-POST-RI-PROD | POST_LOAD | Run | B rows product_sk → all have dim_product match 100% | MAJOR if any orphans | WARN | — |
| DQ-POST-RI-SHOP | POST_LOAD | Run | B rows shop_sk → all have dim_shop match 100% | MAJOR if any orphans | WARN | — |
| DQ-POST-DIM-PROD-COUNT | POST_LOAD | Run | dim_product count between 1 and 3,664 (no invented) | INFO | WARN if < 3,664 | — |
| DQ-POST-DIM-SHOP-COUNT | POST_LOAD | Run | dim_shop count between 1 and 158 | INFO | WARN if < 158 | — |
| DQ-POST-DIM-CAT-COUNT | POST_LOAD | Run | dim_category between 1 and 34 (29+5) | INFO | WARN if < 34 | — |
| DQ-POST-TECHTS-ORDER | POST_LOAD | Run | ingested_at ≤ processed_at ≤ loaded_at (99% of rows) | MAJOR if ≥1% violated | WARN | — |
| DQ-POST-SYNTH-ZERO | POST_LOAD | Run | COUNT WHERE is_synthetic = TRUE must = 0 (default Track A MVP) | CRITICAL if > 0 | BLOCK_LOAD (rollback) | — |
| DQ-RECON-ACC | POST_LOAD | Run | accepted_rows + rejected_rows = input_rows for each source | CRITICAL if unequal | BLOCK_LOAD (rollback) | — |

### 11.3 Severity + Action Matrix (§18)

| Severity | Definition | Action |
|---|---|---|
| CRITICAL | Fundamentals violated (wrong file SHA, count mismatch, cross-source leakage, B labels, A product/shop FK pop, synthetic non-zero, transaction failure) | **BLOCK_LOAD** — raise hard error, ROLLBACK transaction, pipeline_run FAIL. Run stops dead; zero partial rows in warehouse. |
| MAJOR | Per-row data outside allowed domain; run-level variant drift | **REJECT_ROW** for row-level (rejected row logged, not loaded). For run-level: WARN + report, allow load (unless cumulative ≥ threshold converts to CRITICAL). |
| MINOR | Cosmetic / low-impact discrepancy | **WARN** only |
| INFO | Informational diagnostic, no implication for load | No action (logged for audit only) |

### 11.4 Never Silently Discard Records (§18 hard requirement)

- Every row NOT loaded → 1 row in rejected_record_log with `dq_rule_id`, `stage`, `reason`, `severity`, `source_id`, `source_row_number`.
- Reject counts: logged to `logs/pipeline_rejections_{run_id}.json` (LOCAL_ONLY flat backup in case DB rollback erases table).
- Run summary shows: per source, input = accepted + rejected + (if any) error_rows; if any mismatch → DQ-RECON-ACC CRITICAL BLOCK.

---

## 12. IDEMPOTENCY / TRANSACTION STRATEGY

### 12.1 Idempotency (§19)

Goal: same validated source + same pipeline version → **same final warehouse rows (no duplication), consistent SKs for master dimensions**.

Strategy (simplest valid per §19 guidance to evaluate full refresh first):

1. **Deterministic full refresh** of dynamic entities (fact_review, dim_category, dim_product, dim_shop, rejected_record_log, data_quality_result) via `TRUNCATE ... RESTART IDENTITY CASCADE` at start of every run.
2. **Idempotent seed upserts** for static dimensions (dim_source, dim_rating): `INSERT ... ON CONFLICT DO NOTHING`. SKs never change between runs (SMALLSERIAL only increments if new rows; but 2+5 rows never grow in MVP).
3. **Natural-key uniqueness on fact_review**: Even if TRUNCATE is accidentally skipped and a developer runs pipeline twice, `UNIQUE(source_sk, source_native_row_hash) + INSERT ... ON CONFLICT DO NOTHING` prevents duplicate rows. Second run inserts 0 facts.
4. **Deterministic SK retrieval** for dynamic dimensions: because dim_category/dim_product/dim_shop are TRUNCATEd each run, their SKs may be reassigned in a different order — but fact_review re-looks SK up immediately after the upsert in the same run, so FKs always align correctly. For cross-run consistency SKs are not exported / relied upon externally — the exported business/source key is (source_sk, source_native_product_id) etc. SKs are warehouse-internal only.

### 12.2 Transaction Safety (§20)

Rule: `failed ETL != partially accepted final state`.

Implementation:
```
BEGIN (READ COMMITTED);
  TRUNCATE dynamic_tables RESTART IDENTITY CASCADE;
  INSERT seed dims (ON CONFLICT DO NOTHING);
  INSERT pipeline_run (STARTED);
  upsert dim_category → SELECT SK map into Python dict;
  upsert dim_product → SK map;
  upsert dim_shop → SK map;
  batch INSERT rejected_record_log (rows rejected during INPUT/TRANSFORM);
  batch INSERT fact_review (accepted rows only; all FKs resolved to real SKs);
  INSERT data_quality_result (pre-aggregate results; pass/fail flags);
  UPDATE pipeline_run SET status = 'SUCCESS', completed_at, counters;
COMMIT;
```

If ANY exception → handler executes `ROLLBACK`; writes pipeline FAIL to local JSON log (outside DB transaction so it survives). Then re-raises. A developer inspecting warehouse after failure sees the prior successful run's state intact (not partially overwritten because TRUNCATE+inserts were never committed).

### 12.3 Transaction Scope Exceptions

- Rejection JSON backup log + pipeline report JSON are written outside the DB transaction (filesystem LOCAL_ONLY in `logs/`). If DB rollback occurs, audit remains.
- Raw files are never inside any transaction; they are read-only.

---

## 13. PIPELINE METADATA / LOGGING

### 13.1 pipeline_run minimum fields (§21)

All §21 required fields present:

| §21 required field | Implemented as (pipeline_run column) | Notes |
|---|---|---|
| pipeline_run_id | `pipeline_run_id` UUID | PK-equivalent natural |
| source_id | Not stored directly (1 pipeline run loads 2 sources); child rejected_record_log / data_quality_result have per-source granularity; counters are stored aggregated; per-source breakdown is in pipeline_report_{run_id}.json LOCAL_ONLY | Aggregated + per-source breakdown in JSON backup |
| started_at | `started_at TIMESTAMPTZ NOT NULL` | UTC |
| completed_at | `completed_at TIMESTAMPTZ` | UTC; NULL until SUCCESS/FAIL |
| status | `status TEXT NOT NULL` CHECK enum STARTED/SUCCESS/FAILED/ROLLBACK | — |
| input_rows | `input_rows_total INTEGER` | Sum of source A + B input rows |
| accepted_rows | `accepted_rows_total INTEGER` | Post-DQ per-source sum |
| rejected_rows | `rejected_rows_total INTEGER` | Counts rows in rejected_record_log for run |
| loaded_rows | `loaded_rows_total INTEGER` | COUNT of fact_review rows inserted by this run (can be cross-checked post via loaded_at = run window) |
| pipeline_version | `pipeline_version TEXT NOT NULL` | Semver string "0.1.0-phase6" |

### 13.2 Logging destinations

- Python `logging` module to console (INFO default; configured via LOG_LEVEL env + project_settings)
- File log handler → `logs/etl_{run_id}.log` (LOCAL_ONLY; gitignored)
- DB pipeline_run + rejected_record_log + data_quality_result tables
- JSON summary report `logs/pipeline_report_{run_id}.json` LOCAL_ONLY

---

## 14. CONFIGURATION / SECRETS

### 14.1 Reuse existing configuration systems only (§24; no new competing systems)

| Concern | Existing Mechanism | Phase 6 Use |
|---|---|---|
| Project paths | `config/project_settings.yaml` → paths.data_raw / data_interim / data_processed / data_metadata / logs | ETL reads raw paths |
| Source IDs / raw file paths / columns | `config/data_sources.yaml` → source_a.local_path; source_b.local_path; official_columns; cross_source_*: false | All source location + schema authority |
| Split/duplicate/hardware (not used in Phase 6, but loaded via unified util) | `config/experiment_settings.yaml` | — |
| YAML loader | `src/marketvoice/utils/config.py → load_yaml_config()`, `get_project_root()` | ETL uses `load_project_settings()` wrapper + adds new `load_data_sources()` in same module |
| DB credentials | `.env` via `.env.example` POSTGRES_HOST/PORT/DB/USER/PASSWORD; NEVER committed; loaded via `os.environ.get` or python-dotenv | Phase 6 DB engine builder in database/config.py |
| Feature flags | Hard-coded constants `ENABLE_TRACK_B = False` in ETL config; override via env `MARKETVOICE_ENABLE_TRACK_B=1` (always 0/false default) | Track B isolation |
| Environment classification | `ENVIRONMENT=development` in .env | pipeline_run.environment_name column stored |
| Git ref for lineage | `subprocess.check_output(['git','rev-parse','--short','HEAD']).strip()` (or fallback UNKNOWN if git missing) | pipeline_run.git_commit_ref |

### 14.2 Secret Safety

- `.env` is gitignored (check §5 + .gitignore post-remediation — already correctly ignored via standard Python project convention in .gitignore).
- `.env.example` is the ONLY version-controlled document that mentions DB cred placeholders.
- ETL code must NEVER log the actual password; never serialize it in the pipeline_report JSON; never print to console.
- If password env var missing → BLOCK_LOAD with CRITCAL `DQ-SECRET-001`.

### 14.3 New helper in config util (small additive only; no competing system)

Add `load_data_sources() -> Dict[str, Any]` at the bottom of existing `src/marketvoice/utils/config.py` that calls `load_yaml_config("config/data_sources.yaml")`. Consistent with existing `load_project_settings()`.

---

## 15. PLANNED CODE TREE

Aim: small orchestrator + testable domain functions; 1k+ line script forbidden; tiny-modules also avoided.

New modules created in this planned structure (§25 professional structure):

```
src/marketvoice/
├── __init__.py                         (EXISTING; untouched)
├── utils/
│   ├── __init__.py                     (EXISTING; untouched)
│   └── config.py                       (EXISTING; add load_data_sources() helper ONLY)
├── database/                           (NEW — Phase 6)
│   ├── __init__.py
│   ├── config.py                       (DB cred loader + psycopg2/sqlalchemy engine builder)
│   ├── connection.py                   (get_connection / get_engine test/prod isolation)
│   ├── schema.py                       (DDL runner; runs sql/warehouse/*.sql in numeric order; transactional)
│   └── verify.py                       (Post-DDL schema validation: table present, col present, type ok)
├── etl/                                (NEW — Phase 6)
│   ├── __init__.py
│   ├── pipeline.py                     (ORCHESTRATOR — ~200–300 lines MAX; calls domain fns below)
│   ├── extract.py                      (extract_source_a / extract_source_b; readonly)
│   ├── standardize.py                  (rename_cols; cast rating; collapse ws only)
│   ├── transform.py                    (build_dim_candidates, build_fact_candidates, SK maps)
│   ├── load.py                         (truncate; upsert dims; batch INSERT fact; ON CONFLICT)
│   ├── reconcile.py                    (post-load SQL queries; counters; asserts)
│   ├── track_b_loader.py               (DISABLED default; structural only — 0 rows loaded)
│   └── report.py                       (logs JSON report; stdout summary)
└── quality/                            (NEW — Phase 6)
    ├── __init__.py
    ├── input_checks.py                 (DQ-INTEGRITY-*, DQ-INPUT-* per-row + run)
    ├── transform_checks.py             (DQ-TR-*, DQ-LBL-B-* run-wide)
    ├── load_checks.py                  (DQ-LOAD-FK-*, DQ-LOAD-UNQ-HASH)
    ├── post_load_checks.py             (DQ-POST-* — SQL assertions)
    ├── severity.py                     (enum Severity CRIT/MAJOR/MINOR/INFO + Action enum)
    └── rejection_log.py                (Rejection dataclass + to_db_row + to_json_row)


tests/
├── __init__.py                          (EXISTING; untouched)
├── test_environment.py                  (EXISTING; untouched — 3/3 PASS baseline)
├── phase06/                             (NEW — Phase 6 tests)
│   ├── __init__.py
│   ├── conftest.py                      (Isolated test DB: marketvoice_test_* schema / DB; test fixtures)
│   ├── test_database_schema.py          (DDL runs clean; expected tables present; DROP CASCADE post)
│   ├── test_database_constraints.py     (rating CHECK 1..5; UNIQUE; A-no-prod CHECK)
│   ├── test_etl_extract.py              (Mock CSV — file missing; sha mismatch handled)
│   ├── test_etl_standardize.py          (Column rename + rating cast)
│   ├── test_etl_transform.py            (Dim dedup; fact SK map; hash deterministic)
│   ├── test_etl_load_idempotency.py     (Run pipeline twice → same final counts; ON CONFLICT DO NOTHING)
│   ├── test_etl_transaction_safety.py   (Inject failure mid-load → no partial state)
│   ├── test_etl_full_refresh.py         (TRUNCATE behavior; dims rebuilt correctly)
│   ├── test_quality_input_checks.py     (Reject counts on bad rows)
│   ├── test_quality_post_load.py        (Cross-source leakage scenarios: A product NOT NULL → CRIT)
│   ├── test_quality_rejections_log.py   (Rejected rows → accountable non-zero counts + reason codes)
│   └── test_etl_end_to_end_sample.py    (Synthetic tiny fixtures A=5 rows + B=10 rows → load + reconcile)
```

**PostgreSQL driver choice:** Use `psycopg[binary]` (psycopg3) as the DB driver. Add `sqlalchemy` optional but only used for test fixtures (DDL runner uses raw psycopg cursor for simplicity). Justification: psycopg3 is the current Python PostgreSQL standard, handles COPY if needed, and is a lightweight new dependency added only for Phase 6.

**Dependencies added to pyproject.toml (during future execution only; NOT during this planning run):** psycopg[binary]; python-dotenv (if not present — check in execution). The user's HD-003=DOC decision for pytest vs. core dep is NOT affected by this DB driver decision (it is a new core dep unavoidable for Phase 6).

### Protected modules / no over-writing:

- `pyproject.toml` will only be MODIFIED in the future execution phase if psycopg is not present.
- All files in `config/*`, `docs/architecture/*`, `docs/methodology/*`, `docs/requirements/*`, `docs/governance/*` (EXCEPT this plan file itself) are READ-ONLY for the execution phase unless a specific bug/change is required.
- No modification to existing tests: the new tests live under `tests/phase06/` isolated.

---

## 16. PLANNED SQL TREE

Fewer-files approach is acceptable; we use 4 numbered files + 1 future placeholder = 5 total. Follows §26 guidance "Fewer files acceptable if simpler."

```
sql/warehouse/
├── 001_schema.sql                    (CREATE SCHEMA IF NOT EXISTS marketvoice_warehouse;)
├── 002_tables.sql                    (CREATE TABLE for ALL 3 metadata + 6 dimensional + fact + 6 views)
├── 003_constraints_seed.sql          (ALTER TABLE ADD PK/FK/CHECK/UNIQUE constraints + idempotent seed dim_source/dim_rating INSERT ON CONFLICT DO NOTHING)
├── 004_indexes.sql                   (Indexes only for PK/FK + known Phase 7 access patterns — see below)
└── 099_future_phases_reserved.sql    (Comment-only file; lists Phase 8–11 reserved entities; zero DDL)
```

Separation rationale:
- 001–004: ordered numeric prefix so runner can `glob("sql/warehouse/*.sql"); sort(); run_each()` deterministically.
- Constraints (especially FK) are in 003 after all tables exist (avoids ordering errors in CREATE TABLE FK inline — both work, but explicit ALTER is easier to audit).
- Seeds in 003: dim_source (2 rows) + dim_rating (5 rows).

### Index Roster (004_indexes.sql; no over-indexing — §23)

Only:
1. Primary key indexes (implicit from PK creation in 003 — not listed; created automatically by Postgres).
2. Foreign key indexes:
   - `fact_review.source_sk` → big table, common WHERE clause (per-source queries)
   - `fact_review.rating_sk` → common GROUP BY rating
   - `fact_review.category_sk` → common GROUP BY (Phase 7 mv_category_summary)
   - `fact_review.product_sk` → Source B per-product analytics (Phase 7 mv_product_b_summary)
   - `fact_review.shop_sk` → Source B per-shop analytics (mv_shop_b_summary)
   - `fact_review.pipeline_run_id` → lineage audit
3. One analytical index for ML Phase 8 (source_sk + rating_value combined; used where rating_model filters on source and stratifies).
4. No indexes on TEXT columns (review_text — PostgreSQL sequential scan is fine for ~46K rows). No full-text search index in Phase 6.
5. No BRIN/partial/expression indexes until Phase 7/8 can prove requirement.

Index count estimate: ≤ 8 explicit non-PK indexes. Minimal.

---

## 17. TEST STRATEGY

### 17.1 Scope (§27 + DEL-10 automated DQ test suite)

Coverage mapped to §27 required areas:

| §27 Required Test Area | Test module | Execution env |
|---|---|---|
| Configuration | test_database_schema + test_environment (existing) | Python unittest / pytest (both runners) |
| Extract | test_etl_extract.py | Temp CSV fixtures, no real DB needed |
| Transform | test_etl_standardize.py + test_etl_transform.py | Pure Python; fixtures in-memory |
| DQ | test_quality_input_checks.py / transform_checks.py / post_load.py / rejections_log.py | Pure Python + test DB for post_load |
| Database schema | test_database_schema.py | Real isolated test DB (local) |
| Constraints | test_database_constraints.py | Real isolated test DB (INSERT invalid → CHECK violation exception asserted) |
| ETL load | test_etl_end_to_end_sample.py | Real isolated test DB + tiny fixtures (5 A + 10 B) |
| Idempotency | test_etl_load_idempotency.py (run 2x → same count) | Real isolated test DB |
| Referential integrity | test_database_constraints.py + test_quality_post_load.py | Real isolated test DB |
| Row-count reconciliation | test_etl_end_to_end_sample.py asserts counts; test_quality_rejections asserts balanced | Real isolated test DB |
| End-to-end load | test_etl_end_to_end_sample.py; also a 6.12 full build smoke run in dev environment | Real dev PostgreSQL NOT TEST/LOCAL_ONLY |

### 17.2 Test Database Isolation (MANDATORY §27)

Isolated test database name: `marketvoice_test` (hardcoded; separate from dev `POSTGRES_DB=marketvoice_db`). Tests connect via `.env.test` (not committed) or env var overrides. After every test file runs: `DROP SCHEMA marketvoice_warehouse CASCADE` via `conftest.py` teardown. Under NO circumstance do tests run against developer's dev marketvoice_db; under NO circumstance against any remote/shared/cloud DB.

### 17.3 Test Runner Dual Support

- `python -m unittest discover tests/phase06 -v` — must work standalone (core deps only; no pytest). This is the MINIMAL baseline required for DEL-10.
- `python -m pytest tests/phase06 -q` — also works with `pip install -e ".[dev]"` per HD-003. Same test modules.

### 17.4 Dangers Avoided

- No destructive tests against unknown/shared databases.
- No test inserts against production-like data; always tiny fixtures (5–100 rows total).
- No PII/fake raw-data leakage: all fixtures are synthetic short Indonesian-like text but clearly labelled test (not plausible review data). No use of real raw CSVs in tests/phase06; only in the 6.12 full-build smoke (uses actual LOCAL_ONLY raw but only on DEVELOPER machine; not CI).

---

## 18. ORDERED EXECUTION STEPS

Template per step (§32): Step ID / Purpose / Inputs / Evidence / Actions / Files / Database impact / Data impact / Validation / Acceptance criteria / Rollback / Dependencies / Stop condition.

Approximate sequence follows §33 adjusted for repository structure.

### 6.1 Entry Verification

| Field | Content |
|---|---|
| **Step ID** | 6.1 |
| Purpose | Verify Phase 0–5 gates + upstream artefacts intact on execution day. |
| Inputs | Working tree; phase_gates.md v4.3; validation reports. |
| Evidence | §2 of this plan; git status; tests/test_environment.py PASS baseline. |
| Actions | Run `git status --short` clean; run `python -m unittest discover tests -v` (env baseline); read phase_gates.md current status block; assert PHASE_0–5=PASS. |
| Files touched | None (read-only checks). |
| Database impact | None. |
| Data impact | None; raw files open read-only for SHA check only. |
| Validation | env smoke 3/3 PASS; gates PASS; no uncommitted changes to tracked governance files. |
| Acceptance | All green. |
| Rollback | N/A. |
| Dependencies | Developer machine: Python + PostgreSQL installed; .env present; raw CSVs local. |
| Stop condition | Any gate FAIL or unexpected dirty git on governance docs → STOP. Report blocker. |

### 6.2 Phase 5→6 Reconciliation Re-read

| Field | Content |
|---|---|
| **Step ID** | 6.2 |
| Purpose | Reconfirm reconciliation §6 findings still match actual (no post-plan changes in architecture docs). |
| Inputs | docs/architecture/*.md; reports/validation/phase_05*.md. |
| Evidence | This plan §6 FIND-01..13. |
| Actions | Diff each arch file's last-modified; confirm dimensional_model.md entities match plan's 8 physical tables (6 Track A core + 3 metadata). |
| Files touched | None. Optionally add a note to CHANGELOG if any architecture bug was discovered (would BLOCK). |
| Database impact | None. |
| Data impact | None. |
| Validation | Entity count matches (3 metadata tables + 5 dims + 1 fact = 9 physical; 6 views = virtual). Any mismatch → BLOCK. |
| Acceptance | Zero architecture changes vs. plan baseline. |
| Rollback | N/A. |
| Dependencies | 6.1 PASS. |
| Stop condition | Any discovered dimensional_model.md defect → BLOCK → fix under new governance. |

### 6.3 Source-to-Target Mapping Lock

| Field | Content |
|---|---|
| **Step ID** | 6.3 |
| Purpose | Freeze S2T mapping (§9 above) to execution-time version; write frozen md5 for audit. |
| Inputs | This plan file §9. |
| Evidence | Frozen checksum stored in logs/ (LOCAL_ONLY; not committed). |
| Actions | Compute `hashlib.md5(§9 text).hexdigest()`; store in `logs/phase06_s2t_freeze_{ts}.txt` LOCAL_ONLY. |
| Files touched | logs/ only; no tracked files changed. |
| Database impact | None. |
| Data impact | None. |
| Validation | Hash reproducible. |
| Acceptance | Hash written; no further S2T edits without plan v1.1. |
| Rollback | Delete freeze txt if 6.3 restarts (idempotent). |
| Dependencies | 6.2 PASS. |
| Stop condition | N/A (always green). |

### 6.4 Physical DDL Authoring

| Field | Content |
|---|---|
| **Step ID** | 6.4 |
| Purpose | Implement sql/warehouse/*.sql 4 files + placeholder per §16 tree. |
| Inputs | §7 tables + §8 keys + §9 column definitions. |
| Evidence | DDL source SQL files. |
| Actions | Write 001_schema, 002_tables (9 tables CREATE + 6 views CREATE), 003_constraints_seed (PK/FK/CHECK/UNIQUE + seed inserts ON CONFLICT DO NOTHING), 004_indexes (<=8 indexes), 099_placeholder. Follow naming: snake_case; table names match plan exactly; columns aligned with S2T target_field. |
| Files created/modified | `sql/warehouse/001..004 + 099.sql` (new 5 files; tracked in git). |
| Database impact | No DB yet; DDL is file-only. |
| Data impact | NONE. |
| Validation | `tests/phase06/test_database_schema.py` + `test_database_constraints.py` pass against test DB. DDL comments reference this plan's grain. |
| Acceptance | DDL runner executes 001→004 in order clean; no syntax error; all 9 tables + 6 views created; seed counts (2 dim_source + 5 dim_rating) present. |
| Rollback | `rm sql/warehouse/*.sql` or `git checkout` if need to revert DDL pre-commit. |
| Dependencies | 6.3 PASS. psycopg3 driver available. |
| Stop condition | Any DDL syntax error in test DB; or constraints reject seeds → STOP. Fix DDL. |

### 6.5 DB Initialization (DEVELOPMENT + TEST)

| Field | Content |
|---|---|
| **Step ID** | 6.5 |
| Purpose | Create empty marketvoice_test; run DDL 001–004. Confirm structure via verify.py. |
| Inputs | sql/warehouse/*.sql; database/schema.py runner. |
| Evidence | Post-init VERIFY SCHEMA checksum: table/column count stored in logs/. |
| Actions | (a) `CREATE DATABASE marketvoice_test` with test user (if not exists); (b) schema.run(path='sql/warehouse'); (c) verify.post_ddl_asserts(). |
| Files | database/config.py, connection.py, schema.py, verify.py created/used. |
| Database impact | DDL applied to marketvoice_test ONLY. Dev DB untouched in step 6.5. |
| Data impact | Only seed rows (2 source + 5 rating). |
| Validation | verify.py reports 9 TABLES + 6 VIEWS + 3 metadata tables. |
| Acceptance | 100% verified; test_database_schema.py 10/10 pass. |
| Rollback | `DROP DATABASE marketvoice_test;` or `DROP SCHEMA marketvoice_warehouse CASCADE;` in test DB. |
| Dependencies | 6.4 PASS. |
| Stop condition | Verify fails → stop; fix sql/*.sql and rerun. |

### 6.6 Extract Implementation

| Field | Content |
|---|---|
| **Step ID** | 6.6 |
| Purpose | Code extract.py: open readonly CSV; compute SHA; compare manifest; return rows + metadata. |
| Inputs | config/project_settings.yaml paths; config/data_sources.yaml; manifest.csv. |
| Evidence | Extract function return dicts (row list) + source metadata. |
| Actions | Implement extract_source_a, extract_source_b. Use csv.DictReader encoding='utf-8'. Use hashlib streaming. Assert MODE='r' only. |
| Files | etl/extract.py NEW. |
| Database impact | None. |
| Data impact | Raw file READ ONLY; NEVER WRITTEN. |
| Validation | test_etl_extract: missing file → FileNotFoundError handled; bad sha → BLOCK_LOAD raised; correct file → 5400 rows exactly. |
| Acceptance | Tests pass. Mode assertion enforced (code review + test that mocks open() and asserts no 'w'). |
| Rollback | Git checkout etl/extract.py. |
| Dependencies | 6.5 PASS; utils/config helper in place. |
| Stop condition | Extract corrupts data → redesign; otherwise continue. |

### 6.7 Transform + Standardize Implementation

| Field | Content |
|---|---|
| **Step ID** | 6.7 |
| Purpose | Code standardize.py (rename + rating cast) + transform.py (dim/fact rows + SK map builders). |
| Inputs | Raw extract rows. |
| Evidence | Output transformed rows match S2T target_field names/types. |
| Actions | Pure functions. No DB yet. |
| Files | etl/standardize.py NEW; etl/transform.py NEW. |
| Database impact | None. |
| Data impact | None. |
| Validation | test_etl_standardize.py; test_etl_transform.py. Hash deterministic assertion. |
| Acceptance | Tests pass; review text preserved. |
| Rollback | Git checkout etl/*.py. |
| Dependencies | 6.6 PASS. |
| Stop condition | Transform lossy (text stripped punctuation etc.) → revert. |

### 6.8 Data Quality Implementation

| Field | Content |
|---|---|
| **Step ID** | 6.8 |
| Purpose | Implement all quality/*.py modules per DQ roster §11.2. |
| Inputs | standardized / transformed rows. |
| Evidence | DQ results (list of DqResult dataclass) + Rejection rows. |
| Actions | (a) input_checks; (b) transform_checks; (c) load_checks; (d) post_load_checks (SQL-based). Also severity enum + rejection log writer. |
| Files | quality/input_checks.py, transform_checks.py, load_checks.py, post_load_checks.py, severity.py, rejection_log.py. All NEW. |
| Database impact | post_load_checks runs SELECT-only queries; no writes. |
| Data impact | None (checks only). |
| Validation | test_quality_* modules. Critical hard scenarios: A row with product_id injected → DQ-POST-NOPROD-A CRIT raised. |
| Acceptance | All DQ rules covered; every rule has at least one unit test of PASS and FAIL path. |
| Rollback | Git checkout quality/*.py. |
| Dependencies | 6.7 PASS. |
| Stop condition | Missing any CRITICAL check → STOP and add before proceeding. |

### 6.9 Load + Reconcile Implementation

| Field | Content |
|---|---|
| **Step ID** | 6.9 |
| Purpose | Implement load.py (transactional TRUNCATE + upsert dims + batch insert fact) + reconcile.py (post-load aggregate queries). |
| Inputs | Transformed dim + fact rows. DB connection. |
| Evidence | Post-load counts + integrity SQL rows. |
| Actions | Load: BEGIN → TRUNCATE dynamic_tables → seed → upsert dims → insert facts → insert rejections → insert DQ results → UPDATE pipeline_run → COMMIT. Reconcile: run §10.8 8-point SQL queries. |
| Files | etl/load.py NEW; etl/reconcile.py NEW. |
| Database impact | Yes (transactional writes in dev/test DB). |
| Data impact | Loads rows to tables (no raw data changes). |
| Validation | test_etl_load_idempotency.py; test_etl_transaction_safety.py (injected error → zero rows post-rollback). |
| Acceptance | Idempotent; transaction-safe; reconcile balance assert ok. |
| Rollback | DB: ROLLBACK during run. After commit: re-run pipeline (full-refresh will overwrite). Code: git checkout etl/*.py. |
| Dependencies | 6.8 PASS. |
| Stop condition | Transaction failure not rolling back → hard blocker; redesign load.py transaction wrapper. |

### 6.10 Pipeline Orchestration

| Field | Content |
|---|---|
| **Step ID** | 6.10 |
| Purpose | Glue: etl/pipeline.py orchestrator (<300 lines max) + report writer. |
| Inputs | All etl/*. + quality/*. + database/*. |
| Evidence | Running: `python -m marketvoice.etl.pipeline --source all` produces SUCCESS/FAIL exit code. |
| Actions | Code orchestrator only; all logic in domain modules. CLI is minimal (argparse; 2 flags: --source [all,A,B] and --config-path default). |
| Files | etl/pipeline.py NEW; etl/report.py NEW. database/config.py/connection.py also fully utilized. |
| Database impact | Runs full load in target DB. |
| Data impact | Full row count written. LOCAL_ONLY; no data leaves dev machine. |
| Validation | Manual invocation against marketvoice_test with fixtures works. |
| Acceptance | Exit 0 on success; exit 1 on BLOCK_LOAD/FAIL. |
| Rollback | Pipeline orchestrator is idempotent so rerun automatically refreshes. |
| Dependencies | 6.9 PASS; all domain modules in place. |
| Stop condition | Orchestrator deadlocks or 2x runtime > 1 minute for full dataset → investigate (should be <10 seconds normally). |

### 6.11 Tests (DEL-10)

| Field | Content |
|---|---|
| **Step ID** | 6.11 |
| Purpose | Implement tests/phase06/*.py per §17.1; execute both unittest + pytest paths. Ensure DEL-10 all pass. |
| Inputs | All marketvoice Phase 6 modules. |
| Evidence | JUnit-style XML output to logs/ (LOCAL_ONLY) + console PASS/FAIL. |
| Actions | (a) Write conftest.py (test DB isolated) (b) Write all 12 phase06 test files (c) Run unittest discover tests/phase06 (d) Run pytest tests/phase06 -q (e) Write DEL-10 summary to logs/. |
| Files created | tests/phase06/ directory with 12 modules. |
| Database impact | Writes/teardowns to marketvoice_test ONLY; drops schema cascade after session. |
| Data impact | Tiny fixture rows only. Real raw data NOT used in tests. |
| Validation | tests/phase06 100% PASS both runners. |
| Acceptance | DEL-10: all automated tests PASS 0 CRIT; env baseline untouched (old tests still 3/3 PASS — no regression). |
| Rollback | No DB data; test DB schema dropped. Test code git revert. |
| Dependencies | 6.10 PASS. Python [dev] extras installed (needed only for pytest path; unittest path is core). |
| Stop condition | Any test FAIL → fix root cause (NEVER modify test logic to force PASS); then rerun until green. |

### 6.12 End-to-End Warehouse Build (DEVELOPER MACHINE)

| Field | Content |
|---|---|
| **Step ID** | 6.12 |
| Purpose | Run pipeline ONCE against developer's LOCAL marketvoice_db with actual REAL raw CSVs. |
| Inputs | REAL LOCAL_ONLY raw CSVs. |
| Evidence | pipeline_report_<run_id>.json in logs/. Post-build counts. |
| Actions | (a) Ensure marketvoice_db DDL applied (run schema.run against DEV DB once). (b) Execute orchestrator: `python -m marketvoice.etl.pipeline --source all`. (c) Capture exit code + report. |
| Files touched | Only logs/ (runtime artefacts; LOCAL_ONLY). |
| Database impact | Full marketvoice_warehouse schema populated in DEV DB. |
| Data impact | Raw data is read-only; no mutation. Standardized rows in memory only. |
| Validation | Post-build counts: A=5,400 - rejects; B=40,607 - rejects; dim_product ≤ 3,664; dim_shop ≤ 158; dim_category ≤ 34; B-label and A-product/shop anti-leakage hard checks pass. |
| Acceptance | Status SUCCESS; exit 0; all CRITICAL DQ 0 failures; row counts match expectations. |
| Rollback | Full-refresh means rerun any time = clean slate; also can TRUNCATE manually. |
| Dependencies | 6.11 PASS (all green); PostgreSQL server running; .env correct; raw present. |
| Stop condition | BLOCK_LOAD / FAIL status → investigate root cause; fix code under same transaction-safety rules → rerun. |

### 6.13 Reconciliation Sign-Off

| Field | Content |
|---|---|
| **Step ID** | 6.13 |
| Purpose | Explicit per-table reconciliation between expected counts (manifest + raw counts) and warehouse actual counts. |
| Inputs | Step 6.12 report. |
| Evidence | Reconciliation table stored in new validation report (future Phase 6 gate report). |
| Actions | Run manual SQL to re-verify DQ-POST-*; compare against §2.3. Human eyeball. |
| Files | None (future validation report file will be created in 6.15; not 6.13). |
| Database impact | Read-only queries. |
| Data impact | None. |
| Validation | Every DQ-POST-* passes. Every count matches tolerance. |
| Acceptance | 100% reconciliation; zero leakage; zero unknown-domain; zero rejected without reason code. |
| Rollback | N/A. |
| Dependencies | 6.12 PASS. |
| Stop condition | Any count discrepancy unexplained → STOP and fix before validation. |

### 6.14 Reproducibility Documentation

| Field | Content |
|---|---|
| **Step ID** | 6.14 |
| Purpose | Write new sections in README.md "Phase 6 — Build Warehouse Locally" that describe setup. |
| Inputs | Actual install steps executed. |
| Evidence | Step-by-step reproducible instructions in markdown. |
| Actions | Append reproducible section in README: install deps; place raw; create .env; create empty DB; run DDL; run pipeline; verify counts. |
| Files modified | README.md (only Phase 6 instructions block). |
| Database impact | None. |
| Data impact | None. |
| Validation | Fresh developer can clone + install + configure + get identical counts within documented tolerance. |
| Acceptance | README Phase 6 section exists; commands copy-pasteable. |
| Rollback | Git checkout README.md. |
| Dependencies | 6.13 PASS; actual end-to-end verified at least once. |
| Stop condition | N/A (documentation; always green). |

### 6.15 Phase 6 Forensic Validation Report

| Field | Content |
|---|---|
| **Step ID** | 6.15 |
| Purpose | Author new validation report `reports/validation/phase_06_warehouse_validation.md` covering DEL-08/09/10 pass/fail. |
| Inputs | All steps above. |
| Evidence | The validation report itself. |
| Actions | New markdown file. Contains: (i) DDL verification (ii) Pipeline runtime stats (iii) DQ results (iv) Row count reconciliation (v) Anti-leakage checks passed (vi) Test summary. (vii) Remaining known limitations. |
| Files created | `reports/validation/phase_06_warehouse_validation.md` — tracked file. |
| Database impact | Read only; SELECT count queries against DEV DB for evidence. |
| Data impact | None. |
| Validation | Future Phase 6 gate PASS evidence. |
| Acceptance | Naming follows convention; all 7 sections filled with REAL evidence, no placeholders. |
| Rollback | Git checkout / remove new report. |
| Dependencies | 6.13 PASS; 6.14 pass. |
| Stop condition | Report cannot claim gate PASS because any CRIT still present → STOP and fix. |

### 6.16 Gate Preparation

| Field | Content |
|---|---|
| **Step ID** | 6.16 |
| Purpose | Update phase_gates.md (ONLY after human review of 6.15). Propose Phase 6 gate PASS for Phase 7 entry. |
| Inputs | 6.15 report. |
| Evidence | Updated phase_gates.md §7 Phase 6 record (analogous to §4/5/6 existing). |
| Actions | Add §7 Phase 6 status record with PHASE_6_BUILD_STATUS=COMPLETE, TECH_VAL=PASS, HUMAN=AWAITING_APPROVAL. Update header status line. |
| Files modified | `docs/governance/phase_gates.md` (after approval step). |
| Database impact | None. |
| Data impact | None. |
| Validation | Syntax valid; no other gate statuses accidentally clobbered. |
| Acceptance | Gate update template applied correctly; AWAITING_HUMAN_APPROVAL status set (not PASS automatically). |
| Rollback | Git checkout phase_gates.md. |
| Dependencies | ALL steps 6.1–6.15 PASS. Human approval must be obtained before this step modifies the canonical gate file. AWAITING state may be written pre-approval; PASS only after. |
| Stop condition | Do not set PASS without explicit gate sign-off. |

**Total steps: 16 (6.1..6.16).**

---

## 19. VALIDATION STRATEGY

### 19.1 Three Levels of Validation

| Level | Scope | Method | When run |
|---|---|---|---|
| L1 — Unit (pure function) | standardize / transform / input_checks individual calls | tests/phase06/test_*.py unittest isolated | 6.6–6.8 post each module; 6.11 DEL-10 formal suite |
| L2 — Integration (isolated test DB) | schema load + constraint checks + transaction safety + idempotency + end-to-end 5+10 row fixtures | tests/phase06/*_testDB files; marketvoice_test DB + conftest teardown | 6.5/6.9/6.10; 6.11 formal |
| L3 — Full build (DEV DB, real raw CSVs) | Entire pipeline against real 46K rows; real DQ full checks; anti-leakage; count reconciliation | Manual `python -m marketvoice.etl.pipeline --source all` + report JSON inspection + human SELECT queries | 6.12 / 6.13 post DEV build; 6.15 in report |

### 19.2 Future Forensic Audit-Ready Evidence

- L1 + L2 test run XML results in logs/ (LOCAL_ONLY).
- L3 pipeline_report JSONs linked to pipeline_run table.
- Phase 6 validation report (6.15) contains timestamps + run_ids + SHA values + counts with real numbers.

### 19.3 Validator Independence

DQ rules are independent of the load function they are checking. The `quality/post_load_checks.py` module has its own separate DB SELECT logic (not calling reconcile.py's counters; independently counts → then compare). Avoids circular self-validation.

---

## 20. OBJECTIVE ACCEPTANCE CRITERIA (§34 — AC-01..AC-20)

All 20 are objective; evidence is computable or file-exists. No subjective "reasonable" language:

| AC ID | Criterion | Objective Test (measurable / binary) |
|---|---|---|
| AC-01 | DEL-08/09/10 fully mapped | DEL-08: sql/warehouse/*.sql exists and DDL coverage = 9 tables + 3 metadata + 6 views; DEL-09: etl/pipeline.py exists and runs; DEL-10: tests/phase06/ 12 files exist and both test runners exit 0 |
| AC-02 | Every physical table has grain | `SELECT table_name FROM information_schema.tables WHERE table_schema='marketvoice_warehouse'` — all 9 physical tables have §8 grain row filled. |
| AC-03 | Every target column has lineage | S2T mapping (this plan §9) covers every column in every table; no `information_schema.columns` row is unmapped → `UNEXPLAINED_WAREHOUSE_FIELDS=0` |
| AC-04 | No unsupported A↔B links | Post-load SQL: (a) Source-A with non-null product_sk=0; (b) Source-A with non-null shop_sk=0; (c) No cross-source category merge (dim_category: 29+5 = count of rows grouped by source_sk each equal 29/5). |
| AC-05 | No fabricated review timestamp | (a) Schema has no `dim_date` table; (b) Information_schema does NOT contain any column named `review_date` / `review_created_at` / `event_date` etc. (search for LIKE pattern). Only tech timestamp columns allowed. |
| AC-06 | Source B product/shop integrity | Referential integrity: `fact_review WHERE source_sk=2 AND product_sk NOT IN (SELECT product_sk FROM dim_product)` COUNT = 0. Same for shop_sk. |
| AC-07 | Rating domain enforced correctly | `COUNT(*) WHERE rating_value NOT BETWEEN 1 AND 5 = 0`. CHECK constraint exists on fact_review (verified in information_schema.check_constraints). |
| AC-08 | Raw files unchanged | SHA-256 of each raw file pre-ETL vs post-ETL identical. `diff -q` or python compare. Also: no file under data/raw/ has mtime changed (within tolerance). |
| AC-09 | LOCAL_ONLY data remains protected | `git status --short data/ data/interim data/raw data/processed logs` returns NO new files staged/added (only .gitkeep + tier READMEs). |
| AC-10 | ETL reproducible | Run pipeline twice against clean DB sequentially. Final COUNT(fact_review) identical (within reject-count noise determinism; but deterministic input so exact). Hash of concatenated (source_sk, rating_value, product_sk) ordered by review_sk identical between runs. |
| AC-11 | ETL idempotent | Run pipeline twice WITHOUT initial TRUNCATE-only manual call (relies on ON CONFLICT DO NOTHING). Final count identical (no duplicates added on run 2). |
| AC-12 | Row counts reconcile | For each source: `input_rows (manifest) = accepted_rows + rejected_rows (log)`. `loaded_rows (DB) = accepted_rows`. |
| AC-13 | Rejected rows reason-coded | `COUNT(*) FROM rejected_record_log WHERE dq_rule_id IS NULL OR reason IS NULL = 0`. Distribution by dq_rule_id stored & non-zero for any rejection that occurred (if zero rejections, document all checks passed). |
| AC-14 | No silent data loss | `input_rows − accepted_rows − rejected_rows = 0` per source; verified via pipeline_report.json. |
| AC-15 | DDL applies cleanly to clean local DB | Fresh empty DB `marketvoice_clean_test` → run 001→004 → `verify.post_ddl_asserts() PASS`. |
| AC-16 | Post-load DQ passes | After full build L3: ALL `data_quality_result WHERE severity='CRITICAL' AND passed=FALSE → COUNT=0`. MAJOR failures allowed <5% of checks. |
| AC-17 | Tests pass | DEL-10: `python -m unittest discover tests/phase06` 100% PASS. Also `pytest -q tests/phase06` 100% PASS. |
| AC-18 | No credentials committed | `git grep -l 'change_this_password'` → ONLY .env.example has placeholder. `git status --short` shows no staged .env. .gitignore has `.env` line. |
| AC-19 | No Phase 7+ implementation | Phase 7 baseline BI: Only 6 lightweight VIEWs allowed. No DEL-11 marts created. No ML model tables. No issue taxonomy. No priority. No FastAPI. No n8n. No Power BI. Greppable: `SELECT COUNT(*) FROM information_schema.tables WHERE table_name IN ('dim_model','fact_model_prediction',...) = 0`. |
| AC-20 | `git diff --check` passes | Run `git diff --check` (no trailing whitespace violations). Working tree diff clean of forbidden data. |

---

## 21. RISK REGISTER

| Risk ID | Risk | Likelihood | Impact | Mitigation | Trigger to Escalate |
|---|---|---|---|---|---|
| RISK-01 | PostgreSQL driver psycopg3 is not installed / old psycopg2 in env breaks new features. | Medium | High (blocks 6.5+). | Pin `psycopg[binary]>=3.1` in pyproject.toml only when adding. Document install. | If conflict with existing deps → downgrade to psycopg2 with compatible calls. |
| RISK-02 | Developer forgets to use marketvoice_test; accidentally runs tests against dev DB. | Medium | High (wipes dev warehouse). | conftest.py hardcodes test DB connection string + DROP SCHEMA marketvoice_warehouse CASCADE pre-test; test DB user credentials in .env.test that is NEVER used by pipeline. | Any test failure mentions tables with >100 rows → investigate immediately. |
| RISK-03 | `python-dotenv` not installed; env vars not loaded → CRIT DQ-SECRET-001 false positive. | Low | Low (blocks startup only; easy fix). | Document in README Phase 6 section: install python-dotenv if you use .env files; alternatively export vars. | If .env.example has docs updated and still fails → add conditional import. |
| RISK-04 | B `sold` field contains unexpected characters that corrupt loading → TEXT store avoids but review_text may have weird Unicode. | Low | Low | All string columns stored TEXT; no truncation; utf-8 encoding. | If decode errors in Step 6.6 extract → open csv with errors='replace' AND MAJOR warn count. |
| RISK-05 | Full refresh TRUNCATE + INSERT may hit FK serial sequence RESTART IDENTITY reset issue if FKs reference dims. | Low | High (data loss if SKs misalign mid-run). | Load order carefully written as TRUNCATE all dynamic tables together. Fact FKs are resolved AFTER the new dimension SKs are returned from the upsert SELECT. | If any test in 6.9 shows FK violation → fix load order / cascade direction. |
| RISK-06 | Source B duplicate product_id with multiple product_name → attribute drift; not a blocking issue but flagged MAJOR. | Medium | Low (dimensional attribute only, not integrity). | DQ-TR-DIM-PROD-001 reports it. The plan's dim design (R-09) accepts first most-frequent name. | If any product_id has >5 name variants → re-audit source to understand duplicates; may need open discussion. |
| RISK-07 | Developer (during 6.12) opens write handle to data/raw by mistake → raw data mutation | Low | CRITICAL (data integrity violation). | Mode assertion in extract.py: code uses `with open(f, 'r', encoding='utf-8')` ONLY. DQ-INTEGRITY-005 audits the file descriptors in the process. | Any detection of write handle to data/raw → immediate BLOCK_LOAD; rollback entire pipeline; re-verify raw SHA vs manifest. |
| RISK-08 | Locale/collation mismatch in Indonesian text: review_text stored as VARCHAR/TEXT → PostgreSQL default encoding may be WIN1252 on Windows developer machine. | Medium | Medium (potential mojibake). | PostgreSQL DB creation template with ENCODING 'UTF8' LC_COLLATE='en_US.UTF-8' (or Indonesian if available). Document CREATE DATABASE template. | If `SHOW server_encoding;` != UTF8 → recreate DB. |
| RISK-09 | Transaction isolation race: two developers run pipeline simultaneously (unlikely on single-user local), causing double TRUNCATE between step and commit. | Very Low | Low | Single-developer prototype. Not a multi-tenant system. Advisory locks optional future add but not MVP. | Not planned for Phase 6 MVP. Document single-pipeline-at-a-time in README. |
| RISK-10 | `ENABLE_TRACK_B=False` forgotten → accidentally loads synthetic rows. | Very Low | CRITICAL (synthetic contamination in Track A). | Default=False hardcoded constant; env var MARKETVOICE_ENABLE_TRACK_B must be explicitly set to 1 to enable; DQ-POST-SYNTH-ZERO post-load CRITICAL check (guarantees zero even if flag accidentally enabled in load; because default track_b_loader still inserts 0 rows). | Any DQ-POST-SYNTH-ZERO FAIL → BLOCK_LOAD (already). |

Total Risks: 10. No BLOCKED_EXTERNAL. All mitigated within this plan's design.

---

## 22. STOP / ROLLBACK CONDITIONS

### 22.1 Hard Stop Conditions (Any Occurrence Halts Execution Immediately)

1. **Phase 0–5 gate PASS statuses materially invalidated on execution day** → return to upstream gates first.
2. **Raw data SHA mismatch vs manifest** → data corrupted or wrong version on disk. Re-obtain approved dataset.
3. **Row count mismatch vs manifest** → raw file edited or truncated; STOP and re-acquire.
4. **Any CRITICAL DQ failure with BLOCK_LOAD action** → pipeline FAIL; report root cause; no partial load accepted.
5. **Evidence of cross-source leakage** (Source-A product_sk/shop_sk non-zero; Source-B has labels; A-B categories merged) → BLOCK_LOAD immediately; investigate whether etl code bug vs. architecture assumption defect.
6. **Transaction failure leaves partial state** → STOP; investigate transaction wrapper logic; rebuild load.py if needed. Never pass a gate with partial state.
7. **Developer detects working tree dirty on governance/docs files before step 6.16** → uncommitted changes may indicate conflicting edits; commit or stash first.
8. **PostgreSQL server unreachable or authentication fails** → BLOCK_LOAD at 6.5; fix local DB config before resuming.
9. **Raw data missing (data/raw Source A or B file absent)** → BLOCK_LOAD 6.1 step; re-acquire approved datasets.
10. **A DQ rule that was planned as CRITICAL is discovered to have NO unit test with FAIL path** → STOP at step 6.11; add test before proceeding.

### 22.2 Rollback Procedures (per layer, per step)

| Layer / Step | Rollback Action |
|---|---|
| Step 6.4 DDL authoring (pre-DB) | `git checkout sql/warehouse/001_002_003_004.sql` OR remove new files |
| Step 6.5 DB init test DB | `DROP SCHEMA marketvoice_warehouse CASCADE;` in test DB; or `DROP DATABASE marketvoice_test;` |
| Step 6.6–6.8 ETL/Quality code changes | `git checkout src/marketvoice/etl src/marketvoice/quality tests/phase06` — pure code |
| Step 6.9–6.10 Load / Pipeline during run | Transactional ROLLBACK automatically; pipeline_run status FAIL; prior warehouse state preserved because TRUNCATE+inserts uncommitted |
| Step 6.9–6.10 After successful COMMIT (want to undo a bad load) | Re-run pipeline with identical inputs → deterministic full refresh TRUNCATE rebuilds clean state; OR run `TRUNCATE fact_review,dim_category,dim_product,dim_shop,rejected_record_log,data_quality_result RESTART IDENTITY CASCADE;` manually + re-seed static dims if needed |
| Step 6.11 Tests | No real data impact; `DROP SCHEMA marketvoice_warehouse` in test DB; temp dirs cleaned |
| Step 6.12 Full build against dev DB | Rerun pipeline; or `TRUNCATE + reload` pattern |
| Step 6.15 Validation report / 6.16 gate doc edits | `git checkout docs/governance/phase_gates.md reports/validation/phase_06_warehouse_validation.md README.md` |
| LOCAL_ONLY logs / data | Delete files under `logs/` and `data/interim` / `data/processed` (never tracked; delete freely) |
| Accidental raw data mutation | STOP IMMEDIATELY; re-download original from canonical source per manifest SHA; DO NOT continue until SHA matches manifest exactly |

---

## 23. PHASE 7 HANDOFF

Phase 6 exit → Phase 7 (Baseline BI, DEL-11: "SQL scripts producing core CX summary marts") has a clean scoped handoff because Phase 6 deliberately stops short of creating BI marts.

### What Phase 7 Receives (Ready-to-Consume)

1. **PostgreSQL physical warehouse** under schema `marketvoice_warehouse`:
   - 6 Track A core entities populated: dim_source, dim_rating, dim_category, dim_product, dim_shop, fact_review.
   - 3 metadata tables: pipeline_run, rejected_record_log, data_quality_result (last execution evidence).
   - 6 lightweight views (Phase 6 "marts-as-views"): mv_source_summary, mv_category_summary_source_specific, mv_product_b_summary, mv_shop_b_summary, mv_source_a_label_breakdown, mv_pipeline_run_recent.
2. **Row counts populated from real data** (not seeds / fixtures).
3. **Lineage accessible**: every fact row links via pipeline_run_id → last SUCCESS run; manifest SHA recorded in dim_source.
4. **DQ baseline**: data_quality_result populated for CRITICAL/MAJOR checks → 0 CRIT FAIL baseline.
5. **Rejection audit trail**: rejected_record_log + logs/pipeline_report_*.json LOCAL_ONLY.
6. **Reproducible ETL**: README Phase-6 instructions written → Phase 7 can re-run warehouse any time.

### What Phase 7 OWNS (NOT Part of Phase 6)

Per phase_gates.md §2 Phase-7 row + DEL-11 definition:
- DEL-11 "SQL scripts producing core CX summary marts" — Phase 7 authors physical mart scripts (materialized or not, Phase 7 decision).
- Any new BI-oriented derived column, any aggregation marts, any filtering views for specific BQ-001..BQ-007 analytical output → Phase 7 work.
- The 6 views delivered in Phase 6 are starting scaffolds; Phase 7 may rewrite, extend, or drop them when building DEL-11 physical marts. No view in Phase 6 is canonical output for any business question.

### Handoff Integrity Checklist

Phase 7 entry criteria (per gate spec matrix §2) = **Phase 6 GATE PASS** + validated warehouse. The handoff is complete when this plan's AC-01..AC-20 are all PASS; after that Phase 6 gate is approved by human sign-off → Phase 7 planning begins.

---

## 24. HUMAN DECISIONS REQUIRED

### 24.1 Mandatory Pre-Execution Human Decisions (cannot be automated)

Before any Phase-6 EXECUTION RUN (separate future session), the project owner must explicitly state the exact authorization string required by §38 of the master prompt:

```
APPROVE PHASE 6 IMPLEMENTATION PLAN.
AUTHORIZE PHASE 6 EXECUTION.
SCOPE = DEL-08 + DEL-09 + DEL-10 ONLY.
```

This is the SOLE authorization that unlocks steps 6.1–6.16. Until received:
- `PHASE_6_EXECUTION = NOT_STARTED`
- `PHASE_6_EXECUTION_AUTHORIZED = FALSE`
- No DDL applied
- No ETL run
- No raw files read with intent to load (only SHA verification in planning allowed)

### 24.2 Decisions Recorded Within This Plan (Already Signed Off in Prior Sessions)

The following decisions were made in the Phase 0–5 remediation and are carried forward into Phase 6. NO reopening required unless the project owner explicitly requests:

| Decision ID | Decision | Origin | Status |
|---|---|---|---|
| HD-001 = A | Protected-data approach: all raw/interim/processed/logs LOCAL_ONLY. Standardized corpora gitignored. | Phase 0–5 remediation (Option A PROTECT-DATA chosen 2026-08-14) | LOCKED for Phase 6 |
| HD-002 | Phase 3 Gate = PASS; formal sign-off. Scope accepted as-is (7 BQ bounded). | Phase 0–5 remediation (2026-08-14) | LOCKED (drives Phase 4/5 PASS cascade → Phase 6 entry) |
| HD-003 = DOC | pytest: remain in `[dev]` extras only; README documents `pip install -e ".[dev]"` before pytest. Do NOT move pytest to core dependencies. | Phase 0–5 remediation (2026-08-14) | LOCKED; Phase 6 tests MUST also work via `python -m unittest discover` (core-path baseline). |
| P5-IMP-R01 (CLARIFICATION) | Staging layer implemented as Python in-memory DataFrames, NOT DB staging tables. DEL-08 "staging/DW/marts" clause satisfied functionally + via 6 lightweight VIEWs as "marts". | Phase 5→6 reconciliation §6 R-01 | VALIDATED AS CLARIFICATION (not defect); if owner disagrees, convert to staging-table DDL + code change under separate future governance. |
| P5-IMP-R02 (CLARIFICATION) | DEL-09 "raw/synthetic" wording: synthetic Track B loader module structurally exists but loads 0 rows in default configuration. Requires FUTURE separate approval to enable. | Phase 5→6 reconciliation §6 R-02 | VALIDATED AS CLARIFICATION. No separate action now; default disabled = NO Track B content. |
| REMOTE_GIT_WRITE | REMOTE_GIT_CONTROL = USER_ONLY. Assistant never performs `git push` / remote mutations. | Project charter + project memory + Phase 0–5 decision | LOCKED for Phase 6 (all git changes require user approval to commit; push = USER ONLY ALWAYS). |

### 24.3 Decisions That MAY Surface During Execution (Deferred to Human If Triggered)

| Trigger Condition | Decision Required From Owner | How It Escalates |
|---|---|---|
| RISK-01 psycopg3 vs psycopg2 conflict requiring pyproject dep change | Approval to modify pyproject.toml dependencies | Step 6.1 preflight reports; HD needed before step 6.4 writes new modules |
| RISK-06 product name variants >5 for a product_id | Whether to normalize (if so, how) or keep as-is | DQ-TR-DIM-PROD-001 MAJOR flag at step 6.13 |
| Step 6.8 discovers missing CRITICAL DQ rule coverage not caught in planning | Owner approval to add a new DQ rule (updates plan v1.1) | 6.11 validation stops; human decision to expand |
| Step 6.12 finds actual raw row count different from manifest (e.g. local CSV previously edited without governance) | Owner approves new manifest version + SHA; or re-downloads canonical dataset | 6.1 entry SHA mismatch halts immediately |
| Any ARCHITECTURE_DEFECT discovered vs. Phase 5 dimensional_model.md (e.g. new entity needed to satisfy requirements) | Owner approval to open Phase 5 addendum | Reported as BLOCKED to owner; Phase 6 pauses |
| Step 6.16 gate PASS vs PASS_WITH_ACTIONS vs FAIL | Human sign-off equivalent to HD-002 for Phase 3 | Required human review of 6.15 report |

---

## FINAL PLAN STATUS (Document Footer)

```
====================================================================
              PHASE 6 IMPLEMENTATION PLAN — DOCUMENT FOOTER
====================================================================

DOCUMENT_VERSION           = 1.0 (PLAN_ONLY; no execution performed)
DATE_CREATED               = 2026-08-14
DOCUMENT_CLASSIFICATION    = PHASE_6_IMPLEMENTATION_PLAN
AUTHORITATIVE_FILE_PATH    = docs/plans/phase_06_implementation_plan.md

PHASE_6_PLAN_STATUS        = READY_FOR_HUMAN_REVIEW
PHASE_6_EXECUTION_STATUS   = NOT_STARTED
PHASE_6_EXEC_AUTHORIZED    = FALSE (WAITING FOR EXACT APPROVAL STRING)
PHASE_7_IMPLEMENTATION     = FORBIDDEN

UPSTREAM_GATES            = PHASE_0..5_GATE = ALL PASS
DELIVERABLE_SCOPE          = DEL-08 + DEL-09 + DEL-10 ONLY
PROHIBITED_IN_PHASE_6      = FastAPI, n8n, Power BI, ML, LLM, Track-B synthetic,
                             Cross-source linkage, Fake review timestamps,
                             Issue taxonomy, Priority formulas, SLA/Case,
                             Cloud warehouse / Kafka / Spark / Airflow / K8s.

REMOTE_GIT_WRITE           = NONE / FORBIDDEN (USER-ONLY CONTROL PERMANENT)
LOCAL_DATA_MUTATION        = NONE THIS RUN (planning only)
DATABASE_MUTATION          = NONE THIS RUN (planning only; no DDL applied,
                                                   no DB created, no ETL run)
SAFETY_DIFF_CHECK          = GIT DIFF --CHECK PENDING VALIDATION BELOW

REQUIRED_APPROVAL_STRING   =
    APPROVE PHASE 6 IMPLEMENTATION PLAN.
    AUTHORIZE PHASE 6 EXECUTION.
    SCOPE = DEL-08 + DEL-09 + DEL-10 ONLY.

FUTURE_EXECUTION_NOTE      = Once approved, Phase 6 execution SHALL proceed
                             through steps 6.1 → 6.16 in a separate dedicated
                             session under MODE=EXECUTE_APPROVED_PLAN.
====================================================================
```
