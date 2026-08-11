# MARKETVOICE SEA — SYSTEM REQUIREMENTS SPECIFICATION (SRS)

**Document Version**: 2.0 (Phase 3 System Specification)  
**Deliverable ID**: `DEL-05`  
**Phase**: Phase 3 (Business & System Requirements Specification & Governance Baseline)  
**Classification**: System Requirements Specification  
**Architecture Boundary**: Local FastAPI + PostgreSQL Data Warehouse + Python ML + Power BI  

---

## 1. SYSTEM ARCHITECTURE & SCOPE OVERVIEW

MarketVoice SEA is structured as a modular 4-tier decision support system operating locally:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          MARKETVOICE SEA ARCHITECTURE                           │
├─────────────────────────────────────────────────────────────────────────────────┤
│ 1. DATA ACQUISITION & INTERIM STAGING LAYER                                      │
│    • Immutable Raw: data/raw/prdect_id/ & data/raw/tokopedia_reviews_2019/      │
│    • Validated Interim: data/interim/validated/                                 │
│                                                                                 │
│ 2. POSTGRESQL DATA WAREHOUSE LAYER (Kimball Star Schema)                        │
│    • Schema: staging -> edw (dim_product, dim_seller, fact_review) -> mart      │
│                                                                                 │
│ 3. ANALYTICAL, ML INFERENCE & DECISION ENGINE LAYER                            │
│    • Python / FastAPI REST API (/api/v1/predict, /api/v1/priority-cases)        │
│    • Rating/Sentiment Classifier (Phase 8), Priority Scoring Engine (Phase 10)  │
│    • n8n Operational Webhook Integration (Phase 11)                             │
│                                                                                 │
│ 4. POWER BI DECISION INTELLIGENCE DASHBOARD LAYER                               │
│    • Executive CX Overview, Product Quality, Seller Ops, CS Priority Queue      │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. STANDARDIZED TARGET PERFORMANCE BENCHMARKS

The system components must satisfy the following standardized performance target thresholds:

- **Rating Prediction Model (RQ-1 / FR-301)**: Macro F1 $\ge 0.70$, Weighted F1 $\ge 0.75$, Quadratic Weighted Kappa (QWK) $\ge 0.75$.
- **Emotion Classification Model (RQ-1 / FR-303)**: Macro F1 $\ge 0.65$.
- **Aspect Classification Model (RQ-2 / FR-303)**: Micro F1 $\ge 0.70$, Hamming Loss $\le 0.10$.
- **Priority Scoring Engine (RQ-3 / FR-401)**: Separation Ratio $\ge 2.5$, Top-K Precision ($K=50$) $\ge 0.80$.
- **Data Pipeline Quality (FR-104 / NFR-202)**: Row Reconciliation $= 100\%$ ($0$ lost rows), Lineage Key Uniqueness $= 100\%$.

---

## 3. FUNCTIONAL REQUIREMENTS (FR)

### Module 1: Data Ingestion & Lineage (`FR-100 Series`)
- **FR-101 (Multi-Source Ingestion)**: System shall ingest Source A (`SRC_PRDECT_ID_V1`) and Source B (`SRC_TOKOPEDIA_REVIEWS_2019`) into separate PostgreSQL staging tables (`staging.stg_prdect_id_reviews` and `staging.stg_tokopedia_2019_reviews`).
- **FR-102 (System Lineage Tagging)**: System shall generate `source_record_key = SHA256(source_id | sha256 | row_number)` for 100% of staging rows.
- **FR-103 (Raw Hash Audit)**: System shall verify raw file SHA256 hashes against `source_manifest.csv` before running ETL.
- **FR-104 (Row Reconciliation)**: System shall enforce $100\%$ row reconciliation ($\text{Raw Rows} = \text{Staging Rows}$).

### Module 2: Dimensional Modeling & Data Warehouse (`FR-200 Series`)
- **FR-201 (Kimball Star Schema)**: System shall implement PostgreSQL Enterprise Data Warehouse (`edw`) containing conforming dimensions (`dim_category`, `dim_product`, `dim_seller`, `dim_source`) and fact tables (`fact_review`).
- **FR-202 (Metric Transformation)**: System shall parse raw metrics losslessly (`price_idr`, `sold_numeric_value`, `sold_value_semantics`).
- **FR-203 (Domain Mart Creation)**: System shall build dedicated analytical summary marts (`mart_cx_overview`, `mart_product_quality`, `mart_seller_intelligence`, `mart_priority_decision_queue`, `mart_model_governance_eval`, `mart_data_pipeline_audit`).

### Module 3: ML Inference Engine (`FR-300 Series`)
- **FR-301 (Rating Prediction)**: System shall train and evaluate machine learning models (e.g. Logistic Regression, Linear SVM, IndoBERT) to predict star ratings (1-5) from review text (target Macro F1 $\ge 0.70$, QWK $\ge 0.75$).
- **FR-302 (Sentiment Classification)**: System shall evaluate 2-class sentiment prediction performance against Source A provided annotations.
- **FR-303 (Emotion & Aspect Classification)**: System shall evaluate 5-class emotion prediction (target Macro F1 $\ge 0.65$) and aspect classification (target Micro F1 $\ge 0.70$, Hamming Loss $\le 0.10$).
- **FR-304 (Model Governance Logging)**: System shall log evaluation metrics in `mart_model_governance_eval`.

### Module 4: Decision Prioritization Engine (`FR-400 Series`)
- **FR-401 (Configurable Priority Score)**: System shall compute a 0-100 Priority Score for each review record:
  $$\text{Priority Score} = w_1 \cdot (6 - \text{Rating}) + w_2 \cdot \text{Negative Sentiment Score} + w_3 \cdot \text{Issue Severity} + w_4 \cdot \text{Business Impact}$$
  System shall achieve target Separation Ratio $\ge 2.5$ and Top-K Precision $\ge 0.80$.
- **FR-402 (Priority Case Queue)**: System shall order negative reviews by Priority Score and flag high-risk cases ($\text{Score} \ge 75$) for CS escalation.

### Module 5: API & Webhook Integration (`FR-500 Series`)
- **FR-501 (FastAPI Microservice)**: System shall expose REST API endpoints (`/api/v1/health`, `/api/v1/predict/rating`, `/api/v1/priority/cases`).
- **FR-502 (n8n Webhook Dispatcher)**: System shall trigger an automated webhook payload to n8n whenever a priority case ($\text{Score} \ge 75$) is ingested.

### Module 6: Power BI Decision Intelligence (`FR-600 Series`)
- **FR-601 (Multi-Page Interactive Dashboard)**: System shall support Power BI rendering across 4 core pages: (1) Executive CX Overview, (2) Product Quality & Defect Risk, (3) Seller Operations Intelligence, and (4) CS Priority Decision Queue.
- **FR-602 (Synthetic Data Banner)**: Dashboard shall display `[SYNTHETIC OPERATIONAL EXTENSION]` banners on simulated workflow pages.

---

## 4. NON-FUNCTIONAL REQUIREMENTS (NFR)

### Security & Privacy (`NFR-100 Series`)
- **NFR-101 (Local Distribution Policy)**: Raw datasets and database credentials shall remain strictly local (`project_raw_distribution_policy = LOCAL_ONLY`). Raw files are gitignored.
- **NFR-102 (PII Protection)**: Platform analytics shall present aggregate text metrics only. Review URL public display is disabled (`PRODUCT_URL_PUBLIC_ANALYTICS = DISABLED`).

### Auditability & Lineage (`NFR-200 Series`)
- **NFR-201 (Raw Immutability)**: Raw files under `data/raw/` shall never be modified or overwritten (`RAW_EDIT = FORBIDDEN`).
- **NFR-202 (Traceability)**: Every data mart row shall trace back to `source_record_key` and `import_batch_id`.

### Performance & Scalability (`NFR-300 Series`)
- **NFR-301 (ETL Execution Time)**: Full ETL pipeline execution on local PostgreSQL shall complete within $< 120$ seconds for 46,007 records.
- **NFR-302 (API Inference Latency)**: FastAPI single-review prediction endpoint shall respond within $< 100$ ms.

### Maintainability & Environment (`NFR-400 Series`)
- **NFR-401 (Zero-Dependency Smoke Tests)**: System unit test suite (`tests/test_environment.py`) shall execute using Python standard library without external dependencies.
- **NFR-402 (Python 3.10+ Compatibility)**: Codebase shall remain fully compatible with Python 3.10+.

---

## 5. SYSTEM CONSTRAINTS & GOVERNANCE BOUNDARIES

1. **Dual-Source Isolation**: `CROSS_SOURCE_PRODUCT_LINKAGE = NOT_SUPPORTED` and `CROSS_SOURCE_SHOP_LINKAGE = NOT_SUPPORTED`. Source A and Source B entities shall not be merged into single product keys.
2. **Unsupported Data Gaps**: Real review timestamps and operational CS logs are unsupported by raw data. Track B operational simulations strictly carry `is_synthetic = TRUE`.
3. **Remote Git Policy**: `REMOTE_REPOSITORY_CONTROL = USER_ONLY`. The AI assistant is forbidden from performing `git push` or `force push` operations.
