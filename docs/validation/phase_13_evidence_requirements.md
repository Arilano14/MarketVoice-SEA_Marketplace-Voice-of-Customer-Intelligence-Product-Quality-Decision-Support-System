# MarketVoice SEA — Phase 13 Evidence Requirements Specification

**Document ID**: `EVID-REQ-P13-001`  
**Phase**: Phase 13 — Integrated Validation, UAT & Professional Portfolio Release  
**Status**: Formal Baseline / Audit Checklist  
**Version**: `1.0.0`  
**Governing Standard**: MarketVoice SEA Engineering & Academic Standards  
**Target Repository**: `C:\Users\Arilano\Downloads\Project ARICE\Project SEA\`  

---

## 1. Purpose & Audit Protocol

This specification establishes the comprehensive inventory of empirical evidence required across all 16 project dimensions (A through P) prior to compiling the final project report, executive presentation, and portfolio release.

In accordance with Phase 13 governance:
1. **Zero Assumption Principle**: No metric or analytical claim may be included in the final report without direct evidence from active database queries, test suite executions, or immutable code configurations.
2. **Empirical Primacy**: Active database state and code implementation supersede historical narrative reports.
3. **Traceability**: Every claim must map to a specific artifact, database object, or test assertion.

---

## 2. Evidence Requirements Checklist by Dimension

### A. PROJECT / REQUIREMENTS
* [x] **A.1 Final Problem Statement**: Voice-of-Customer noise, seller defect triage friction, and platform trust erosion in Southeast Asian e-commerce (`docs/architecture/system_architecture_diagram.txt`).
* [x] **A.2 Business Objectives**: 5-aspect taxonomy extraction, contextual Decision Support System (PRS), sub-second microservice triage, and executive BI reporting (`docs/governance/data_governance_policy.md`).
* [x] **A.3 Project Scope**: Ingestion of 46,07 reviews across 2 Indonesian platforms, multi-label NLP aspect classification, Kimball star schema, FastAPI inference service, n8n webhook orchestration, 7-page Power BI dashboard.
* [x] **A.4 Out-of-Scope Declarations**: Autonomous marketplace seller sanctions, customer refunds, live scraping, real-time streaming ingestion, and unverified causal claims.
* [x] **A.5 Stakeholder Definition**: Chief Commercial Officer (CCO), Head of Marketplace Operations, Category Managers, Quality Engineers, and S2 Academic Reviewers.
* [x] **A.6 KPI Dictionary**: Documented at `dashboards/power_bi/measure_definitions/kpi_dictionary.md`.
* [x] **A.7 System & Data Architecture**: `docs/architecture/` and `docs/architecture/power_bi_reporting_architecture.md`.
* [x] **A.8 Technology Stack**: Python 3.10, PostgreSQL 15, FastAPI, Uvicorn, n8n, scikit-learn, pytest, Power BI Desktop.

---

### B. DATA PROVENANCE & FORENSICS
* [x] **B.1 Source Provenance**:
  * **Source A**: PRDECT-ID Indonesian Product Reviews V1 (`SRC_PRDECT_ID_V1`), Mendeley Data (CC BY 4.0), 5,400 reviews.
  * **Source B**: Tokopedia Product Reviews 2019 (`SRC_TOKOPEDIA_REVIEWS_2019`), Kaggle Public Dataset (CC0), 40,607 reviews.
* [x] **B.2 Integrity Hashes (SHA-256)**: Stored immutably in `dim_source` table and `config/project_settings.yaml`.
* [x] **B.3 Row & Column Baseline**: Exactly 46,007 total rows ingested (Source A: 5,400; Source B: 40,607).
* [x] **B.4 Data Quality Pre-Flight Checks**: 11/11 automated checks passing (`data_quality_result` table).
* [x] **B.5 Source Isolation**: Source A strictly isolated from SKU/product-level grains (0 product rows).

---

### C. DATA WAREHOUSE (KIMBALL STAR SCHEMA)
* [x] **C.1 Schema Architecture**: 31 validated objects in `marketvoice_warehouse` (9 dimensions, 3 facts, 5 operational tables, 14 summary views).
* [x] **C.2 Fact Tables**:
  * `fact_review`: 46,007 rows (Review transaction grain).
  * `fact_review_issue`: 18,863 rows (Issue occurrence grain).
  * `fact_decision_queue`: 5,090 rows (Entity $\times$ Issue decision grain).
* [x] **C.3 Key Constraints & Integrity**: 19 Primary Keys, 23 Foreign Keys, 0 orphan product keys, 0 orphan issue keys.
* [x] **C.4 Conformed Dimensions**: `dim_source` (2), `dim_category` (34), `dim_product` (3,664), `dim_issue` (5), `dim_severity` (4), `dim_rating` (5), `dim_priority_tier` (4), `dim_reason_code` (7), `dim_shop` (158).

---

### D. BUSINESS INTELLIGENCE (POWER BI)
* [x] **D.1 Semantic Model Specification**: Documented at `dashboards/power_bi/model_documentation/semantic_model_spec.md`.
* [x] **D.2 DAX Measure Governance**: 18 standard measures in `dashboards/power_bi/measure_definitions/kpi_dictionary.md`.
* [x] **D.3 KPI Reconciliation**: 22 primary metrics audited with 0.00% unexplained variance (`dashboards/power_bi/validation/reconciliation_results.md`).
* [x] **D.4 7-Page Layout Architecture**: Executive Overview, Voice of Customer, Product Quality, Issue Intelligence, Decision Support, Operational Monitoring, Data & Model Quality.

---

### E. NLP & MACHINE LEARNING MODELS
* [x] **E.1 Dataset Split Strategy**: 80/20 train/test stratified split with fixed random seed (`seed=42`).
* [x] **E.2 Model Architecture**: TF-IDF vectorization (1-3 ngrams) + LinearSVC / MultinomialNB / Logistic Regression baselines.
* [x] **E.3 Gold Benchmark Performance (Source A)**:
  * Sentiment Classification: Macro F1 = 0.8878, Weighted F1 = 0.8879.
  * Emotion Classification: Macro F1 = 0.6712, Weighted F1 = 0.6725.
  * Rating Classification: Macro F1 = 0.4496, QWK = 0.7788, MAE = 0.4407.
* [x] **E.4 Model Card Documentation**: `models/model_cards/sentiment_classifier.md` and `models/model_cards/rating_predictor.md`.

---

### F. ISSUE INTELLIGENCE & DEFECT TAXONOMY
* [x] **F.1 Taxonomy v1.0 Definition**: 5 frozen mutually exclusive categories (Product Defect, Packaging Damage, Order Inaccuracy, Logistics Issue, Seller Service).
* [x] **F.2 Issue Distribution**: 18,863 total issue mentions (Seller Service: 33.71%, Packaging: 20.72%, Delivery: 17.63%, Product Defect: 15.90%, Order Inaccuracy: 12.04%).
* [x] **F.3 Rating-Based Severity Proxy**: 1★ $\to$ CRITICAL, 2★ $\to$ HIGH, 3★ $\to$ MODERATE, 4-5★ $\to$ LOW.
* [x] **F.4 Issue Attachment Rate**: 15,270 distinct reviews contain $\ge 1$ issue (33.19% platform penetration).

---

### G. DECISION SUPPORT SYSTEM (DSS)
* [x] **G.1 Multi-Factor Scoring Formula**: $PRS = 100 \times \sum (w_i \cdot \phi_i)$ with weights $\{w_{sev}: 0.30, w_{diss}: 0.25, w_{rec}: 0.20, w_{vol}: 0.15, w_{conf}: 0.10\}$.
* [x] **G.2 Decision Queue Profile**: 5,090 evaluated cases (4,913 Product $\times$ Issue, 167 Category $\times$ Issue, 10 Source $\times$ Issue).
* [x] **G.3 Priority Tiers**: P2 High Priority (192 cases, 3.77%), P3 Monitoring (724 cases, 14.22%), P4 Informational (4,174 cases, 82.00%).
* [x] **G.4 Score Distribution**: PRS bounded strictly in $[3.62, 68.62]$ (Mean: 18.24, Median: 15.31).
* [x] **G.5 Sensitivity & Stability**: 1,000-iteration Monte Carlo perturbation ($\pm 20\%$) confirms High Stability (Spearman $\rho = 0.9983$, Kendall $\tau = 0.9237$, Top-10% Jaccard Overlap = 0.8840).
* [x] **G.6 Policy Benchmarking**: Simulated multi-factor DSS outperforms FIFO, Volume-only, and Severity-only heuristics in risk capture concentration.

---

### H. FASTAPI MICROSERVICE RUNTIME
* [x] **H.1 Service Architecture**: FastAPI ASGI service on Uvicorn (`http://127.0.0.1:8000`).
* [x] **H.2 Health Probes**: `/health` (healthy), `/ready` (database connected, models loaded), `/model` (Taxonomy v1.0 metadata).
* [x] **H.3 Inference & Evaluation Endpoints**:
  * `POST /v1/review/analyze`: Single-text NLP classification & rating severity proxy.
  * `POST /v1/decision/evaluate`: Contextual multi-factor DSS score calculation.
  * `POST /v1/workflow/human-review`: Human-in-the-Loop case outcome logging.
* [x] **H.4 Schema Validation**: 422 Unprocessable Entity enforced for missing attributes, out-of-range ratings, oversized reviews, and invalid source IDs.

---

### I. N8N WORKFLOW AUTOMATION
* [x] **I.1 Workflow Configuration**: 12-node visual triage orchestrator at `workflows/n8n/workflows/marketvoice_review_triage.json`.
* [x] **I.2 PII Redaction**: Automatic masking of Indonesian phone numbers (`+62...`), emails, and social handles.
* [x] **I.3 Idempotency Engine**: Deterministic SHA-256 idempotency key prevents duplicate execution.
* [x] **I.4 Routing Logic**: P1/P2 routed to `human_review_case` queue; P3/P4 routed to `operational_event_log`.

---

### J. DATABASE INTEGRITY
* [x] **J.1 Zero Mutation Principle**: `fact_review` (46,007), `fact_review_issue` (18,863), `fact_decision_queue` (5,090) remain 100% immutable across all operational tests.
* [x] **J.2 Operational Audit Trail**: 37 operational event logs, 13 human review cases, 14 resolution outcomes.

---

### K. SECURITY & GOVERNANCE
* [x] **K.1 Secret Hygiene**: No API keys, OAuth tokens, or production passwords tracked in git.
* [x] **K.2 Environment Isolation**: `.env`, `*.env`, `data/raw/*`, `logs/*` properly ignored in `.gitignore`.
* [x] **K.3 License Compliance**: Source A (CC BY 4.0) and Source B (CC0) licensing conditions respected.

---

### L. TEST SUITE & REGRESSION
* [x] **L.1 Full Suite Results**: **146 passed, 8 warnings in 164.58s (100% PASS)** across:
  * API contract tests: 9 passed
  * Integration workflow tests: 5 passed
  * Decision support regression tests: 19 passed
  * Gold benchmark tests: 11 passed
  * Environment tests: 3 passed
  * Warehouse ETL tests: 19 passed
  * Issue intelligence tests: 24 passed
  * NLP model tests: 41 passed
  * Semantic mart tests: 9 passed
  * n8n contract tests: 6 passed

---

### M. USER ACCEPTANCE TESTING (UAT)
* [x] **M.1 UAT Plan Design**: 5 end-to-end operational scenarios (Executive CX, Product Investigation, Decision Traceability, Reason Code Comprehension, Operational Proxy Boundary).
* [x] **M.2 Execution Mode**: Formally declared as `UAT_STATUS = INTERNAL_SYSTEM_VALIDATION` (no external production user claim).

---

### N. BUSINESS INSIGHTS
* [x] **N.1 Evidence-Grounded Observations**: All insights strictly cite underlying SQL facts and statistical distributions without unfounded causal leaps.

---

### O. RESEARCH & METHODOLOGY
* [x] **O.1 S2-Level Research Framework**: Documented research questions, empirical methodology, benchmarking baselines, limitation disclosures, and reproducibility protocols.

---

### P. PORTFOLIO MATERIALS
* [x] **P.1 Release Artifacts**:
  * `reports/portfolio/final_project_report.md`
  * `reports/portfolio/final_presentation_outline.md`
  * `reports/portfolio/final_evidence_matrix.csv`
  * `docs/validation/phase_13_uat_plan.md`
  * `reports/validation/phase_13_final_validation.md`
