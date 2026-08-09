# MARKETVOICE SEA — BUSINESS & SYSTEM REQUIREMENTS BASELINE

**Document Version**: 1.0  
**Phase**: Phase 0 (Governance & Scope)  
**Classification**: System Requirements Specification  

---

## 1. BUSINESS QUESTIONS (BQ)

The MarketVoice SEA platform is designed to answer the following business questions:

1. **BQ-1 (CX Condition)**: What is the overall review-based customer experience condition and average rating trend over time across the platform? (*Creation Phase: Phase 7*)
2. **BQ-2 (Root-Cause Issues)**: What complaint categories occur most frequently across customer reviews? (*Creation Phase: Phase 9*)
3. **BQ-3 (Quality Anomalies)**: Which categories or specific products exhibit significant increases in negative customer feedback? (*Creation Phase: Phase 7/9*)
4. **BQ-4 (Decision Prioritization)**: Which specific review cases require priority operational attention based on sentiment severity and operational risk? (*Creation Phase: Phase 10*)
5. **BQ-5 (Operational Workflow)**: How effectively are critical customer complaints routed to simulated operational handling queues? (*Creation Phase: Phase 11*)
6. **BQ-6 (Model Governance)**: How reliable and explainable are the analytical and ML model outputs supporting business decision-making? (*Creation Phase: Phase 8/13*)

---

## 2. RESEARCH QUESTIONS (RQ)

* **RQ-1 (Rating / Sentiment Modeling)**: How accurately can machine learning models predict discrete 1-to-5 star ratings from unstructured customer review text? (*Evaluated via Macro F1, Weighted F1, QWK in Phase 8*).
* **RQ-2 (Aspect / Issue Classification)**: To what extent can multi-label classification methods extract candidate issue categories from unstructured feedback? (*Evaluated via Micro F1, Hamming Loss in Phase 9*).
* **RQ-3 (Decision Prioritization)**: Does a configurable decision-priority engine improve the separation of high-severity customer issues compared to simple star-rating thresholds? (*Evaluated via Top-K Precision and Separation Ratio in Phase 10*).
* **RQ-4 (BI System Integration)**: How effectively can NLP model outputs and dimensional data modeling be integrated into a Power BI semantic layer to ensure data lineage traceability, schema consistency, and decision usability? (*Evaluated via schema audit, lineage validation, and benchmark testing in Phase 12*).

---

## 3. BUSINESS INFORMATION REQUIREMENTS (BIR)

| Req ID | Information Requirement | Required Metric / Indicator | Target User | Data Source | Availability Status | Creation Phase |
|---|---|---|---|---|---|---|
| **BIR-01** | CX Condition & Rating Distribution | Average Rating, Negative Review %, Review Volume | Head of CX | Review Fact Mart | `KNOWN` | Phase 7 |
| **BIR-02** | Issue Category Breakdown | Issue Frequency, % Share of Total Issues | Product Quality Mgr | Issue Fact Mart | `REQUIRES_PHASE_2_DATA_AUDIT` | Phase 9 |
| **BIR-03** | Product & Seller Quality Risk | Negative Review Spike Velocity, Defect Ratio | Category Mgr / Seller Ops | Product/Seller Marts | `CONDITIONAL` | Phase 7/9 |
| **BIR-04** | Priority Decision Review Queue | Priority Score, Priority Rank, SLA Status | CS Manager | Priority Queue Mart | `TO_BE_DEFINED` | Phase 10 |
| **BIR-05** | Model Validation & Transparency | Macro F1, Micro F1, Confusion Matrix, Confidence | Data Science Team | Model Eval Mart | `KNOWN` | Phase 8/9 |
| **BIR-06** | Data Pipeline Quality & Audit | Missing Value Rate, Duplicate Count, Row Count Audit | Data Governance Rev | Pipeline Audit Logs | `KNOWN` | Phase 6 |

---

## 4. FUNCTIONAL REQUIREMENTS BASELINE (FR)

* **FR-001 (Data Ingestion)**: Ingest raw CSV reviews into PostgreSQL staging tables without row loss or schema corruption. (*Phase 6*)
* **FR-002 (Data Validation & PII Sanitization)**: Validate schema integrity, filter corrupt records, and sanitize PII (phone numbers, emails) during staging. (*Phase 6*)
* **FR-003 (Text Preprocessing)**: Preprocess review text (normalization, tokenization, emoji handling) for downstream NLP tasks. (*Phase 8*)
* **FR-004 (Rating / Sentiment Model Inference)**: Execute ML model inference to predict discrete review ratings and output confidence probability scores. (*Phase 8*)
* **FR-005 (Aspect / Issue Classification)**: Classify reviews against a validated multi-label issue taxonomy (e.g., candidate packaging, defect, delay categories). (*Phase 9*)
* **FR-006 (Conditional Synthetic Metadata Enrichment)**: If raw attributes are absent, join reviews with deterministic synthetic operational dimensions (Product Master, Seller Master, Order Timestamp, SLA Flags) carrying explicit `is_synthetic = TRUE` flags. (*Phase 6*)
* **FR-007 (Decision Priority Scoring)**: Compute a normalized, explainable Priority Score based on configurable sentiment severity, issue weight, and seller risk inputs. (*Phase 10*)
* **FR-008 (Dimensional DW ETL)**: Execute reproducible SQL ETL scripts transforming staged data into a Kimball Star Schema data warehouse. (*Phase 6*)
* **FR-009 (FastAPI Microservice Endpoints)**: Expose REST API endpoints delivering priority queues, model evaluation metrics, and summary KPIs in JSON format. (*Phase 11*)
* **FR-010 (Operational Workflow Triggering)**: Trigger automated n8n webhooks for high-priority complaints to simulate CS ticket creation. (*Phase 11*)
* **FR-011 (Power BI Multi-Page Reporting)**: Render interactive Power BI reports covering Executive CX, Product Quality, Decision Support, Model Performance, and Governance. (*Phase 12*)
* **FR-012 (Model & Data Governance Reporting)**: Publish automated Model Cards and Data Quality audit logs. (*Phase 14*)

---

## 5. NON-FUNCTIONAL REQUIREMENTS BASELINE (NFR)

* **NFR-001 (Reproducibility)**: Data processing, synthetic data generation, and model training pipelines must be 100% reproducible via single-command scripts using documented fixed random seeds. (*Phase 6/8*)
* **NFR-002 (Traceability & Lineage)**: Every database record and BI metric must maintain end-to-end lineage back to its raw source file or generation script via `source_file` and `is_synthetic` flags. (*Phase 6/12*)
* **NFR-003 (Data Privacy)**: User contact details or PII must be automatically sanitized during ETL staging. (*Phase 6*)
* **NFR-004 (Auditability)**: All data quality violations, model predictions, and workflow webhooks must produce immutable audit logs in PostgreSQL. (*Phase 6/11*)
* **NFR-005 (Code Quality & Maintainability)**: All Python code must adhere to PEP 8 standards, include docstrings, maintain unit test coverage >= 70%, and pass linting clean. (*Phase 13*)
* **NFR-006 (Model Explainability)**: Sentiment and issue predictions must include feature contribution scores or confidence metrics; black-box predictions without confidence are prohibited. (*Phase 8/9*)
* **NFR-007 (Configuration Management)**: Environment configurations (database credentials, API keys, paths) must be managed via `.env` files and never hardcoded in source code. (*Phase 1*)
* **NFR-008 (Licensing Compliance)**: No raw dataset covered by restrictive competition licenses shall be committed to public Git repositories (`.gitignore` enforcement). (*Phase 1/2*)

---

## 6. REQUIREMENTS TRACEABILITY MATRIX

| Business Objective | Business Question | Research Question | Information Requirement | Functional Requirement | Deliverable ID | Validation Method |
|---|---|---|---|---|---|---|
| **OBJ-01**: Monitor platform Customer Experience trends | **BQ-1**: Overall CX condition & rating trend | **RQ-1**: Rating prediction accuracy | **BIR-01**: CX Condition & Rating Distribution | **FR-001**, **FR-003**, **FR-004** | `DEL-08`, `DEL-09`, `DEL-12`, `DEL-18` | SQL Data Audit & DAX Measure Validation |
| **OBJ-02**: Identify root-cause product & service defects | **BQ-2**: Frequent complaint categories | **RQ-2**: Multi-label aspect extraction | **BIR-02**: Issue Category Breakdown | **FR-005** | `DEL-13`, `DEL-19` | Multi-label F1 Evaluation & Annotation Audit |
| **OBJ-03**: Identify high-risk products & seller issues | **BQ-3**: Product/seller negative spikes | **RQ-4**: BI integration & consistency | **BIR-03**: Product/Seller Quality Risk | **FR-006**, **FR-008** | `DEL-11`, `DEL-19` | Dimensional Schema Audit & Aggregation Test |
| **OBJ-04**: Prioritize severe complaints for intervention | **BQ-4**: Priority decision review cases | **RQ-3**: Decision priority separation | **BIR-04**: Priority Decision Review Queue | **FR-007** | `DEL-15`, `DEL-20` | Priority Separation Ratio & Sensitivity Test |
| **OBJ-05**: Automate operational case routing | **BQ-5**: Operational ticket routing efficiency | **RQ-3**: Decision priority separation | **BIR-04**: Priority Decision Review Queue | **FR-009**, **FR-010** | `DEL-16`, `DEL-17` | Webhook Trigger Execution & End-to-End Integration Test |
| **OBJ-06**: Ensure model explainability & governance | **BQ-6**: Reliability of AI model outputs | **RQ-4**: BI integration & traceability | **BIR-05**, **BIR-06**: Model & Pipeline Audit | **FR-011**, **FR-012** | `DEL-10`, `DEL-21`, `DEL-23`, `DEL-24` | Automated Test Suite Pass & Model Card Review |

---

## 7. CANDIDATE ISSUE TAXONOMY

The issue taxonomy is treated as a **CANDIDATE** model. Categories such as *Packaging Damage*, *Product Defect*, *Delivery Delay*, and *Seller Unresponsiveness* serve as baseline examples. The final issue taxonomy will be validated during Phase 2 dataset review and Phase 9 taxonomy annotation:

```
[CANDIDATE ISSUE TAXONOMY (Subject to Phase 2/9 Validation)]
├── Packaging & Shipping (e.g., damaged box, missing outer seal, delayed delivery)
├── Product Quality & Authenticity (e.g., defective unit, broken part, counterfeit claim)
├── Order Accuracy (e.g., wrong size, wrong color, missing item in parcel)
└── Seller Communication (e.g., slow chat response, unhelpful seller, refund dispute)
```

---

## 8. UNRESOLVED UNKNOWNS

| Item Code | Unknown Description | Status Tag | Resolution Phase |
|---|---|---|---|
| **UNK-01** | Raw dataset schema, column names, and data types | `REQUIRES_PHASE_2_DATA_AUDIT` | Phase 2 |
| **UNK-02** | Dataset licensing permissions and redistribution rights | `REQUIRES_PHASE_2_DATA_AUDIT` | Phase 2 |
| **UNK-03** | Dataset text language, noise, emoji density, and slang | `REQUIRES_PHASE_2_DATA_AUDIT` | Phase 2 |
| **UNK-04** | Star rating class distribution and imbalance ratio | `REQUIRES_PHASE_2_DATA_AUDIT` | Phase 2 |
| **UNK-05** | Presence of product IDs, seller IDs, timestamps, categories | `REQUIRES_PHASE_2_DATA_AUDIT` | Phase 2 |
| **UNK-06** | Track B synthetic parameters (seed, volume, schema, script) | `CONDITIONAL` | Phase 3 / Phase 6 |
| **UNK-07** | Candidate issue taxonomy structure and category definitions | `CONDITIONAL` | Phase 2 / Phase 9 |
| **UNK-08** | Decision priority score formula, weights, and thresholds | `TO_BE_DEFINED` | Phase 10 |
| **UNK-09** | ML model acceptance criteria and target metrics | `TO_BE_DEFINED` | Phase 2 / Phase 4 |
