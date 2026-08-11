# MARKETVOICE SEA — SYSTEM REQUIREMENTS SPECIFICATION (SRS)

**Document Version**: 1.0 (Phase 3 Requirements Baseline v1.0)  
**Deliverable ID**: `DEL-05`  
**Phase**: Phase 3 (Business & System Requirements Specification & Governance Baseline)  
**Architecture Target Status**: `LOGICAL_CAPABILITIES_DEFINED`, `FINAL_ARCHITECTURE = PHASE_5_DECISION`  
**Phase 3 Status**: `PHASE_3_EXECUTION_STATUS = COMPLETED`, `PHASE_3_REVIEW_STATUS = READY_FOR_HUMAN_REVIEW`, `PHASE_3_GATE_STATUS = NOT_EVALUATED`  

---

## 1. LOGICAL SYSTEM CAPABILITIES & CURRENT IMPLEMENTATION DIRECTION

Phase 3 defines **WHAT** logical capabilities MarketVoice SEA must support. It does **NOT** freeze physical database schemas or technical architectures.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                      LOGICAL SYSTEM CAPABILITIES OVERVIEW                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│ 1. GOVERNED DATA INGESTION CAPABILITY                                           │
│    • Ingestion, checksum verification, and raw immutability auditing.           │
│                                                                                 │
│ 2. ANALYTICAL DATA STORAGE CAPABILITY                                           │
│    • Staging, dimensional data modeling, and summary data mart persistence.     │
│                                                                                 │
│ 3. ML INFERENCE & ANALYTICAL CAPABILITY                                         │
│    • Text preprocessing, rating/sentiment classification, and issue discovery.  │
│                                                                                 │
│ 4. DECISION-SUPPORT CAPABILITY                                                  │
│    • Multi-criteria priority scoring engine and review case ordering.           │
│                                                                                 │
│ 5. WORKFLOW ORCHESTRATION CAPABILITY                                            │
│    • API endpoint exposure and simulated operational ticket webhook dispatch.   │
│                                                                                 │
│ 6. MANAGEMENT BUSINESS INTELLIGENCE CAPABILITY                                  │
│    • Multi-domain executive reporting and interactive analytical visualization. │
│                                                                                 │
│ 7. AUDIT & GOVERNANCE CAPABILITY                                                │
│    • System lineage tracking, data quality monitoring, and model auditability.  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Current Implementation Direction (Subject to Phase 5 Architecture Decision)
- **Core Environment**: Python 3.10+, Git version control.
- **Analytical Storage**: PostgreSQL Data Warehouse (Kimball Star Schema candidate).
- **ML / NLP Pipeline**: Scikit-Learn / PyTorch candidate modeling frameworks.
- **API & Webhook Engine**: FastAPI REST service candidate + n8n automation candidate.
- **Reporting Interface**: Power BI Desktop interactive dashboard candidate.

---

## 2. FUNCTIONAL REQUIREMENTS (FR)

### Module 1: Data Ingestion, Lineage & Validation (`FR-001` to `FR-003`)

#### FR-001: Dual-Source Multi-File Ingestion
- **FR_ID**: `FR-001`
- **TITLE**: Dual-Source Multi-File Ingestion
- **DESCRIPTION**: The system shall ingest Source A (`SRC_PRDECT_ID_V1`) and Source B (`SRC_TOKOPEDIA_REVIEWS_2019`) into isolated data structures preserving original file schema and structure.
- **INPUT**: `data/raw/prdect_id/PRDECT-ID Dataset.csv` and `data/raw/tokopedia_product_reviews_2019/tokopedia-product-reviews-2019.csv`.
- **PROCESSING**: Parse raw CSV lines losslessly; maintain independent ingestion paths (`CROSS_SOURCE_PRODUCT_LINKAGE = false`).
- **OUTPUT**: Raw ingestion records populated in staging storage.
- **ACCEPTANCE_CRITERIA**: 100% of raw rows ingested without syntax or parsing failure.
- **TRACEABILITY**: Maps to `BR-001`, `BR-003`, `BR-005` $\rightarrow$ `IR-001`, `IR-003`, `IR-005`.

#### FR-002: System Lineage Key Generation
- **FR_ID**: `FR-002`
- **TITLE**: System Lineage Key Generation
- **DESCRIPTION**: The system shall generate a deterministic system lineage key `source_record_key = SHA256(source_id | file_sha256 | row_number)` for 100% of ingested records.
- **INPUT**: `source_id`, raw file SHA256 string, 1-indexed row number.
- **PROCESSING**: Compute 64-character hex SHA256 string for each row.
- **OUTPUT**: `source_record_key` column populated across all staging and analytical datasets.
- **ACCEPTANCE_CRITERIA**: Lineage key uniqueness $= 100\%$, null count $= 0$ across 46,007 records.
- **TRACEABILITY**: Maps to `BR-009` $\rightarrow$ `IR-009` $\rightarrow$ `KPI-DQ-05`.

#### FR-003: Raw Hash Verification & Immutability Audit
- **FR_ID**: `FR-003`
- **TITLE**: Raw Hash Verification & Immutability Audit
- **DESCRIPTION**: The system shall calculate local SHA256 checksums for raw files before ingestion and compare them against `source_manifest.csv`.
- **INPUT**: Physical raw files on disk and registered manifest checksums.
- **PROCESSING**: Assert equality of computed vs. registered SHA256 hashes.
- **OUTPUT**: Ingestion audit status (`PASS` / `FAIL`).
- **ACCEPTANCE_CRITERIA**: Abort pipeline if SHA256 mismatch is detected.
- **TRACEABILITY**: Maps to `BR-009` $\rightarrow$ `IR-009` $\rightarrow$ `KPI-DQ-06`.

---

### Module 2: Analytical Processing & Data Marts (`FR-004` to `FR-008`)

#### FR-004: CX Signal Aggregation & Star Rating Analytics
- **FR_ID**: `FR-004`
- **TITLE**: CX Signal Aggregation & Star Rating Analytics
- **DESCRIPTION**: The system shall calculate total review volume, average star rating, rating count distribution (1 to 5 stars), and negative review share across ingested records.
- **INPUT**: Ingested rating integer values (1-5).
- **PROCESSING**: Compute count, average, rating distribution percentages, and negative review percentage ($\text{Rating} \le 2$).
- **OUTPUT**: Summary aggregation records for CX reporting (`mart_cx_overview`).
- **ACCEPTANCE_CRITERIA**: Metrics computed accurately for 100% of valid rating rows.
- **TRACEABILITY**: Maps to `BR-001` $\rightarrow$ `IR-001` $\rightarrow$ `KPI-CX-01..05`.

#### FR-005: Provided Sentiment & Emotion Label Processing
- **FR_ID**: `FR-005`
- **TITLE**: Provided Sentiment & Emotion Label Processing
- **DESCRIPTION**: The system shall process research-annotated gold sentiment (Positive/Negative) and emotion (Happy, Sadness, Fear, Love, Anger) labels from Source A.
- **INPUT**: Provided `Sentiment` and `Emotion` columns in `SRC_PRDECT_ID_V1`.
- **PROCESSING**: Aggregate sentiment distribution, emotion distribution, and crosstabs against Customer Rating.
- **OUTPUT**: Benchmark analytical tables for Source A (`mart_model_governance_eval`).
- **ACCEPTANCE_CRITERIA**: 100% of 5,400 Source A rows categorized correctly without silent drops.
- **TRACEABILITY**: Maps to `BR-002` $\rightarrow$ `IR-002` $\rightarrow$ `KPI-CX-06..07`.

#### FR-006: Product Listing Quality Analytics (Source B)
- **FR_ID**: `FR-006`
- **TITLE**: Product Listing Quality Analytics (Source B)
- **DESCRIPTION**: The system shall aggregate review volume, average rating, and negative review share grouped by `product_id` listing identifier.
- **INPUT**: `product_id`, `product_name`, `rating`, `text` in Source B.
- **PROCESSING**: Group by `product_id` across 3,664 unique products; rank products by negative review rate.
- **OUTPUT**: Product listing quality dataset (`mart_product_quality`).
- **ACCEPTANCE_CRITERIA**: Generate listing metrics for all 3,664 unique products in Source B.
- **TRACEABILITY**: Maps to `BR-003` $\rightarrow$ `IR-003` $\rightarrow$ `KPI-PRD-01..03`.

#### FR-007: Category-Level Quality & Share Analytics
- **FR_ID**: `FR-007`
- **TITLE**: Category-Level Quality & Share Analytics
- **DESCRIPTION**: The system shall aggregate review volume, average rating, and negative review share grouped by raw category and mapped canonical category family.
- **INPUT**: Category raw strings and category mapping policy.
- **PROCESSING**: Group metrics by category; apply category harmonization mappings where defined.
- **OUTPUT**: Category quality dataset (`mart_product_quality`).
- **ACCEPTANCE_CRITERIA**: Metrics generated across all categories in Source A (29) and Source B (5).
- **TRACEABILITY**: Maps to `BR-004` $\rightarrow$ `IR-004` $\rightarrow$ `KPI-CAT-01..03`.

#### FR-008: Shop-Level Review Intelligence (Source B)
- **FR_ID**: `FR-008`
- **TITLE**: Shop-Level Review Intelligence (Source B)
- **DESCRIPTION**: The system shall aggregate review volume, average star rating, negative review share, and product listing count grouped by `shop_id`.
- **INPUT**: `shop_id`, `product_id`, `rating` in Source B.
- **PROCESSING**: Group by `shop_id` across 158 shops; calculate shop-level review metrics.
- **OUTPUT**: Shop review intelligence dataset (`mart_seller_intelligence`).
- **ACCEPTANCE_CRITERIA**: Generate shop metrics for all 158 shops in Source B. Evaluated strictly as Shop-Level Review Intelligence.
- **TRACEABILITY**: Maps to `BR-005` $\rightarrow$ `IR-005` $\rightarrow$ `KPI-SHP-01..04`.

---

### Module 3: NLP Inference & Issue Intelligence (`FR-009` to `FR-011`)

#### FR-009: Unsupervised Issue Discovery & Conditional Aspect Extraction
- **FR_ID**: `FR-009`
- **TITLE**: Unsupervised Issue Discovery & Conditional Aspect Extraction
- **DESCRIPTION**: The system shall support unsupervised text mining and keyword extraction from review text. Supervised multi-label aspect classification remains conditional until Phase 9 human annotation.
- **INPUT**: Customer review text strings.
- **PROCESSING**: Extract text tokens/topics; flag supervised aspect classification as `DEPENDS_ON = PHASE_9_TAXONOMY_AND_ANNOTATION_GATE`.
- **OUTPUT**: Candidate issue theme features (`mart_issue_aspect_intelligence`).
- **ACCEPTANCE_CRITERIA**: System executes unsupervised topic discovery; supervised aspect inference outputs are explicitly flagged as conditional pending Phase 9 ground truth.
- **TRACEABILITY**: Maps to `BR-006` $\rightarrow$ `IR-006` $\rightarrow$ `KPI-ISS-01..03`.

#### FR-000: Rating & Sentiment Predictive Modeling (Phase 8 Candidate)
- **FR_ID**: `FR-010`
- **TITLE**: Rating & Sentiment Predictive Modeling (Phase 8 Candidate)
- **DESCRIPTION**: The system shall provide ML pipelines to train and evaluate candidate classifiers predicting 1-5 star ratings and binary sentiment from review text.
- **INPUT**: Preprocessed review text tokens and target rating/sentiment labels.
- **PROCESSING**: Train candidate ML models (e.g., Logistic Regression, SVM, IndoBERT candidates); evaluate performance.
- **OUTPUT**: Predicted ratings, predicted sentiment probabilities, and model artifact parameters.
- **ACCEPTANCE_CRITERIA**: Model metrics evaluated without hardcoded numeric thresholds (`TARGET_THRESHOLD = TO_BE_DETERMINED_IN_PHASE_4`).
- **TRACEABILITY**: Maps to `BR-008` $\rightarrow$ `IR-008` $\rightarrow$ `KPI-MDL-01..05`.

#### FR-011: Model Validation & Evaluation Logging
- **FR_ID**: `FR-011`
- **TITLE**: Model Validation & Evaluation Logging
- **DESCRIPTION**: The system shall log model performance metrics (Accuracy, Macro F1, Weighted F1, Per-Class Precision/Recall, Confusion Matrix, QWK) in a structured evaluation mart.
- **INPUT**: Model predictions and test set ground truth labels.
- **PROCESSING**: Calculate classification evaluation metrics across test splits.
- **OUTPUT**: Model evaluation log dataset (`mart_model_governance_eval`).
- **ACCEPTANCE_CRITERIA**: Log evaluation metrics for 100% of candidate model runs.
- **TRACEABILITY**: Maps to `BR-008` $\rightarrow$ `IR-008` $\rightarrow$ `KPI-MDL-01..05`.

---

### Module 4: Decision Support & Workflow Simulation (`FR-012` to `FR-014`)

#### FR-012: Priority Decision Scoring & Escalation Queue
- **FR_ID**: `FR-012`
- **TITLE**: Priority Decision Scoring & Escalation Queue
- **DESCRIPTION**: The system shall compute a 0-100 Priority Score for customer reviews using multi-criteria inputs (star rating, sentiment score, issue severity) and sort negative reviews into a prioritized queue.
- **INPUT**: Review rating, predicted sentiment, and candidate issue severity indicators.
- **PROCESSING**: Calculate priority score; order records by descending priority score; flag high-priority cases.
- **OUTPUT**: Prioritized decision review queue dataset (`mart_priority_decision_queue`).
- **ACCEPTANCE_CRITERIA**: Priority queue generated with clear ordering. Exact scoring formula weights determined in Phase 10.
- **TRACEABILITY**: Maps to `BR-007` $\rightarrow$ `IR-007` $\rightarrow$ `KPI-DSS-01..04`.

#### FR-013: Simulation-Aware Operational Workflow Integration
- **FR_ID**: `FR-013`
- **TITLE**: Simulation-Aware Operational Workflow Integration
- **DESCRIPTION**: The system shall support exposing REST API endpoints and dispatching simulated case handling webhooks for high-priority review cases.
- **INPUT**: Priority decision queue records and simulation configuration parameters.
- **PROCESSING**: Format JSON payloads containing `is_synthetic = TRUE`, `scenario_version`, and authentic `source_record_key` reference keys.
- **OUTPUT**: REST API JSON response payloads and webhook POST dispatches.
- **ACCEPTANCE_CRITERIA**: Webhook payloads carry mandatory synthetic metadata flags. Zero raw data mutation.
- **TRACEABILITY**: Maps to `BR-010` $\rightarrow$ `IR-010` $\rightarrow$ `KPI-DSS-04`.

#### FR-014: Interactive BI Reporting & Executive Dashboards
- **FR_ID**: `FR-014`
- **TITLE**: Interactive BI Reporting & Executive Dashboards
- **DESCRIPTION**: The system shall expose analytical summary marts to support multi-page interactive BI dashboard authoring across CX Overview, Product Quality, Shop Review Intelligence, Priority Queue, and Model Governance domains.
- **INPUT**: Persisted analytical data marts.
- **PROCESSING**: Structure dimensional tables and measures for BI tool consumption.
- **OUTPUT**: Interactive visual dashboards and executive reports.
- **ACCEPTANCE_CRITERIA**: Dashboard pages render summary metrics accurately without schema errors.
- **TRACEABILITY**: Maps to `BR-001`..`BR-010` $\rightarrow$ All IRs and KPIs.

---

## 3. NON-FUNCTIONAL REQUIREMENTS (NFR)

```
Target Threshold Standard:
- NFR targets are set as TARGET = TO_BE_BASELINED_IN_RELEVANT_VALIDATION_PHASE where empirical benchmarking is required.
```

### NFR-001: Reproducibility & Pipeline Determinism
- **NFR_ID**: `NFR-001`
- **DOMAIN**: Reproducibility
- **REQUIREMENT**: The data processing, auditing, and analytical pipelines shall execute deterministically, producing identical analytical results across repeated runs from identical inputs.
- **TARGET**: 100% deterministic reproducibility (`TARGET = VERIFIED_IN_PHASE_2_AND_PHASE_6`).
- **TRACEABILITY**: Maps to `BR-009`.

### NFR-002: Lineage Traceability & Auditability
- **NFR_ID**: `NFR-002`
- **DOMAIN**: Auditability
- **REQUIREMENT**: Every persisted row in analytical data marts shall trace back to its origin via `source_record_key`, `source_id`, and `source_row_number`.
- **TARGET**: 100% lineage coverage (`TARGET = 100%_COVERAGE`).
- **TRACEABILITY**: Maps to `BR-009`.

### NFR-003: Raw Data Immutability
- **NFR_ID**: `NFR-003`
- **DOMAIN**: Data Quality & Governance
- **REQUIREMENT**: Physical raw datasets in `data/raw/` shall remain immutable and read-only. Pipelines shall never overwrite or edit raw CSV files.
- **TARGET**: Zero raw file mutations (`TARGET = ZERO_MUTATIONS`).
- **TRACEABILITY**: Maps to `BR-009`.

### NFR-004: Licensing & Distribution Compliance
- **NFR_ID**: `NFR-004`
- **DOMAIN**: Licensing & Security
- **REQUIREMENT**: Raw datasets shall remain local and gitignored (`project_raw_distribution_policy = LOCAL_ONLY`). No raw data files shall be pushed to public version control.
- **TARGET**: 100% compliance with `.gitignore` policies (`TARGET = 100%_COMPLIANT`).
- **TRACEABILITY**: Maps to Governance Baseline.

### NFR-005: PII Scrubbing & URL Privacy Protection
- **NFR_ID**: `NFR-005`
- **DOMAIN**: Security & Privacy
- **REQUIREMENT**: System outputs shall contain zero personally identifiable information (PII). Public display of review URLs shall be disabled (`PRODUCT_URL_PUBLIC_ANALYTICS = DISABLED`).
- **TARGET**: Zero PII exposure (`TARGET = ZERO_PII_EXPOSURE`).
- **TRACEABILITY**: Maps to Governance Policy.

### NFR-006: Explainability & Decision Support Transparency
- **NFR_ID**: `NFR-006`
- **DOMAIN**: Explainability
- **REQUIREMENT**: Priority scoring outputs and ML classification inferences shall provide human-interpretable feature scores or rule descriptions.
- **TARGET**: Transparent decision scores (`TARGET = TO_BE_BASELINED_IN_PHASE_10`).
- **TRACEABILITY**: Maps to `BR-007`.

### NFR-007: Human-in-the-Loop Safeguard
- **NFR_ID**: `NFR-007`
- **DOMAIN**: Governance & Safety
- **REQUIREMENT**: System outputs shall operate exclusively as decision support. No automated punitive actions (e.g., shop suspension, account ban) shall be triggered without human review.
- **TARGET**: 100% human-in-the-loop requirement (`TARGET = MANDATORY_HUMAN_REVIEW`).
- **TRACEABILITY**: Maps to `BR-007`, `BR-010`.

### NFR-008: Synthetic Data Labeling & Boundary Separation
- **NFR_ID**: `NFR-008`
- **DOMAIN**: Governance
- **REQUIREMENT**: Any operational simulation records shall strictly carry `is_synthetic = TRUE` flags and UI warnings. Authentic datasets shall remain unpolluted by synthetic data.
- **TARGET**: 100% synthetic data separation (`TARGET = 100%_SEPARATED`).
- **TRACEABILITY**: Maps to `BR-010`.

### NFR-009: Codebase Maintainability & Modular Architecture
- **NFR_ID**: `NFR-009`
- **DOMAIN**: Maintainability
- **REQUIREMENT**: Code modules shall follow clear separation of concerns (ingestion, audit, transformation, modeling, API) with documented functions and docstrings.
- **TARGET**: Modular codebase design (`TARGET = VERIFIED_IN_CODE_REVIEWS`).
- **TRACEABILITY**: System Architecture.

### NFR-010: Testability & Smoke Test Validation
- **NFR_ID**: `NFR-010`
- **DOMAIN**: Testability
- **REQUIREMENT**: Core environment and requirements validation utilities shall execute using standard Python libraries with zero external test setup dependencies.
- **TARGET**: 100% passing automated smoke test suite (`TARGET = PASS_SUITE`).
- **TRACEABILITY**: Environment Validation.

### NFR-011: Data Quality Assertion Framework
- **NFR_ID**: `NFR-011`
- **DOMAIN**: Data Quality
- **REQUIREMENT**: Data pipelines shall execute automated data quality assertions verifying non-null primary keys, valid value ranges, and row counts.
- **TARGET**: Zero unhandled critical data quality failures (`TARGET = ZERO_UNHANDLED_CRITICAL_FAILS`).
- **TRACEABILITY**: Maps to `BR-009`.

### NFR-012: Versionability of Models & Artifacts
- **NFR_ID**: `NFR-012`
- **DOMAIN**: Model Governance
- **REQUIREMENT**: Trained ML model artifacts, preprocessing pipelines, and evaluation logs shall be versioned and linked to specific dataset versions (`DATA_FOUNDATION_VERSION = 1.0`).
- **TARGET**: Full model artifact versionability (`TARGET = TO_BE_BASELINED_IN_PHASE_8`).
- **TRACEABILITY**: Maps to `BR-008`.

### NFR-013: Analytical Query & ETL Execution Performance
- **NFR_ID**: `NFR-013`
- **DOMAIN**: Performance
- **REQUIREMENT**: Data transformation pipelines and summary data mart queries shall execute efficiently on standard local development hardware.
- **TARGET**: Execution time baselined during ETL benchmarking (`TARGET = TO_BE_BASELINED_IN_PHASE_6`).
- **TRACEABILITY**: System Infrastructure.

### NFR-014: Failure Handling & Exception Logging
- **NFR_ID**: `NFR-014`
- **DOMAIN**: Fault Tolerance
- **REQUIREMENT**: Pipeline components shall catch execution exceptions gracefully, emit informative log messages, and prevent silent data corruption.
- **TARGET**: Clean exception logging (`TARGET = ZERO_SILENT_FAILURES`).
- **TRACEABILITY**: System Infrastructure.

---

## 4. REQUIREMENT ID MIGRATION MAPPING (GOVERNANCE AMENDMENT)

In accordance with Mandatory Correction 3 (Requirement ID Governance), the table below establishes explicit bi-directional mapping from pre-Phase 3 draft IDs to frozen Phase 3 Baseline v1.0 IDs:

| Historical / Draft ID | Classification | Phase 3 Baseline v1.0 ID | Description & Rationale | Status |
|---|---|---|---|---|
| `BQ-1` | `REVISE` | `BQ-CX` | Renamed to BQ-CX to emphasize Customer Experience signals | `MAPPED` |
| `BQ-2` | `REVISE` | `BQ-ISSUE` | Renamed to BQ-ISSUE with Phase 9 conditional status | `MAPPED` |
| `BQ-3` | `REVISE` | `BQ-PRODUCT` & `BQ-SHOP` | Split into BQ-PRODUCT and BQ-SHOP (Shop Review Intelligence) | `MAPPED` |
| `BQ-4` | `REVISE` | `BQ-DSS` | Renamed to BQ-DSS for decision support prioritization | `MAPPED` |
| `BQ-5` | `REVISE` | `BQ-DSS` | Integrated into BQ-DSS operational workflow simulation | `MAPPED` |
| `BQ-6` | `REVISE` | `BQ-MODEL` | Renamed to BQ-MODEL for ML model governance | `MAPPED` |
| `N/A` | `NEW` | `BQ-DQ` | Added explicit Data Quality & Governance boundary question | `MAPPED` |
| `BIR-01` | `REVISE` | `IR-001` | Mapped to formal IR-001 (CX Signals) | `MAPPED` |
| `BIR-02` | `REVISE` | `IR-006` | Mapped to formal IR-006 (Issue Discovery - Conditional) | `MAPPED` |
| `BIR-03` | `REVISE` | `IR-003` & `IR-005` | Split into IR-003 (Product Risk) and IR-005 (Shop Intelligence) | `MAPPED` |
| `BIR-04` | `REVISE` | `IR-007` | Mapped to formal IR-007 (Priority Queue) | `MAPPED` |
| `BIR-05` | `REVISE` | `IR-008` | Mapped to formal IR-008 (Model Governance) | `MAPPED` |
| `BIR-06` | `REVISE` | `IR-009` | Mapped to formal IR-009 (Data Pipeline Quality) | `MAPPED` |
| `FR-101..104` | `REVISE` | `FR-001..003` | Consolidated into FR-001 (Ingestion), FR-002 (Lineage), FR-003 (Hash Audit) | `MAPPED` |
| `FR-201..203` | `REVISE` | `FR-004..008` | Mapped to FR-004 (CX), FR-005 (Labels), FR-006 (Product), FR-007 (Cat), FR-008 (Shop) | `MAPPED` |
| `FR-301..304` | `REVISE` | `FR-009..011` | Mapped to FR-009 (Issue), FR-010 (Rating ML), FR-011 (Model Audit) | `MAPPED` |
| `FR-401..402` | `REVISE` | `FR-012` | Consolidated into FR-012 (Priority Scoring Engine) | `MAPPED` |
| `FR-501..502` | `REVISE` | `FR-013` | Consolidated into FR-013 (Workflow & Webhook Integration) | `MAPPED` |
| `FR-601..602` | `REVISE` | `FR-014` | Consolidated into FR-014 (Management BI Reporting) | `MAPPED` |
| `NFR-101..402` | `REVISE` | `NFR-001..014` | Reorganized into 14 formal NFR domain specifications | `MAPPED` |
