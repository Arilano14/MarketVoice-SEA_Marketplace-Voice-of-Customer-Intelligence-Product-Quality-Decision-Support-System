# MARKETVOICE SEA — BUSINESS REQUIREMENTS DOCUMENT (BRD)

**Document Version**: 2.0 (Phase 3 Requirements Baseline)  
**Deliverable ID**: `DEL-04`  
**Phase**: Phase 3 (Business & System Requirements Specification & Governance Baseline)  
**Classification**: Business Requirements Document  
**Data Foundation Baseline**: `DATA_FOUNDATION_VERSION = 1.0` (Dual-Source: `SRC_PRDECT_ID_V1` & `SRC_TOKOPEDIA_REVIEWS_2019`)  

---

## 1. EXECUTIVE SUMMARY & PROJECT MANDATE

MarketVoice SEA (*Marketplace Voice-of-Customer Intelligence & Product Quality Decision Support System*) is an independent academic/portfolio postgraduate (S2-level) prototype inspired by e-commerce feedback intelligence.

The project translates unstructured marketplace review text and rating data into actionable business intelligence (BI), predictive rating/sentiment models, aspect-based issue intelligence, and a decision-prioritization engine for e-commerce quality assurance.

### Data Foundation & Boundary Principles
1. **Dual-Source Architecture**:
   - **Source A (`SRC_PRDECT_ID_V1`)**: Primary annotated research benchmark (Mendeley Data, DOI `10.17632/574v66hf2v.1`, 5,400 rows, 29 categories, 0 nulls, provided gold 2-class sentiment and 5-class emotion labels).
   - **Source B (`SRC_TOKOPEDIA_REVIEWS_2019`)**: Secondary BI scale dataset (Hugging Face `farhamu/tokopedia-product-reviews-2019`, 40,607 rows, 3,664 product listings, 158 shops, 5 categories).
2. **Strict Dual-Source Isolation**: Source A and Source B are distinct datasets. `CROSS_SOURCE_PRODUCT_LINKAGE = NOT_SUPPORTED` and `CROSS_SOURCE_SHOP_LINKAGE = NOT_SUPPORTED`. Zero cross-source row concatenation or entity identity assumptions.
3. **Temporal & Operational Realities**:
   - `REAL_TEMPORAL_REVIEW_ANALYTICS = NOT_SUPPORTED_BY_CORE_RAW_DATA` (Neither raw source contains native review creation timestamps).
   - `SYNTHETIC_OPERATIONAL_TIMELINE = CANDIDATE_ONLY` (Operational case/SLA logs for Track B workflow simulation will strictly carry `is_synthetic = TRUE` and `scenario_version`).

---

## 2. STAKEHOLDER PERSONAS & DECISION REQUIREMENTS

| Stakeholder Role | Primary Responsibilities | Core Decision Information Needed | Primary Interface |
|---|---|---|---|
| **Head of Customer Experience (CX)** | Platform-wide customer satisfaction monitoring, NPS/CSAT health, macro quality trends. | Platform-wide average rating, rating distribution, negative review %, category satisfaction ranking (`BIR-01`). | Executive CX Overview Dashboard |
| **Product Quality Manager** | Category-level quality control, recurring defect detection, product line risk assessment. | Category complaint share, high-defect product rankings, candidate issue breakdown (`BIR-02`, `BIR-03`). | Category & Product Quality Mart |
| **Seller Operations Manager** | Seller performance monitoring, high-risk merchant identification, seller quality SLA tracking. | Seller/Shop defect ratio, shop rating distributions, seller escalation count (`BIR-03`). | Seller Intelligence Mart |
| **Customer Support (CS) Manager** | Priority case queue management, urgent complaint routing, operational SLA escalation. | Configurable Priority Score queue, high-risk complaint severity rankings (`BIR-04`). | Priority Case Queue & Webhook |
| **Data Science Lead** | Rating/sentiment prediction model development, emotion classification, model evaluation. | Macro/Weighted F1, Quadratic Weighted Kappa (QWK), confusion matrices (`BIR-05`). | Model Governance & Validation Mart |
| **Data Governance Reviewer** | Pipeline auditability, raw immutability compliance, data lineage, data quality tracking. | Lineage audit logs, SHA256 checksums, missing value/duplicate rates (`BIR-06`). | Data Governance & Lineage Mart |

---

## 3. BUSINESS QUESTIONS (BQ)

The platform must answer the following 6 core Business Questions:

- **BQ-1 (CX Platform Health)**: What is the overall review-based customer experience condition, average star rating, and rating distribution across product categories? (*Target Phase: Phase 7*)
- **BQ-2 (Root-Cause Issue Breakdown)**: What complaint categories and feedback themes occur most frequently within customer reviews? (*Target Phase: Phase 9*)
- **BQ-3 (Quality & Defect Anomalies)**: Which specific categories, products, or seller shops exhibit elevated negative customer feedback rates? (*Target Phase: Phase 7/9*)
- **BQ-4 (Decision Prioritization)**: Which specific customer review cases require urgent operational attention based on sentiment severity, low rating, and operational risk? (*Target Phase: Phase 10*)
- **BQ-5 (Operational Workflow Integration)**: How effectively can critical customer complaints be routed to simulated operational handling queues and external webhook endpoints? (*Target Phase: Phase 11*)
- **BQ-6 (Model Governance & Trust)**: How reliable, explainable, and consistent are the ML model outputs supporting business decision-making? (*Target Phase: Phase 8/13*)

---

## 4. RESEARCH QUESTIONS (RQ)

The platform evaluates the following 4 academic Research Questions:

- **RQ-1 (Rating & Sentiment Prediction)**: How accurately can machine learning models predict discrete 1-to-5 star ratings and binary sentiment from unstructured Indonesian marketplace review text? (*Evaluated via Macro F1, Weighted F1, QWK in Phase 8*)
- **RQ-2 (Aspect / Issue Classification)**: To what extent can NLP methods extract candidate issue categories from unstructured customer feedback? (*Evaluated via Micro F1, Hamming Loss in Phase 9*)
- **RQ-3 (Decision Prioritization Efficacy)**: Does a multi-criteria decision priority scoring engine separate severe customer complaints more effectively than a simple star-rating threshold? (*Evaluated via Separation Ratio and Top-K Precision in Phase 10*)
- **RQ-4 (BI System Integration & Traceability)**: How effectively can NLP model inferences and dimensional data modeling be integrated into a Power BI semantic layer to preserve lineage traceability and operational usability? (*Evaluated via schema lineage audit and dashboard benchmark testing in Phase 12*)

---

## 5. BUSINESS INFORMATION REQUIREMENTS (BIR)

| Req ID | Information Requirement | Required Metric / Indicator | Target Stakeholder | Primary Data Source | Target Phase |
|---|---|---|---|---|---|
| **BIR-01** | CX Condition & Category Distribution | Average Rating, Negative Review %, Review Volume by Category | Head of CX | `staging.stg_prdect_id_reviews` & `staging.stg_tokopedia_2019_reviews` | Phase 7 |
| **BIR-02** | Issue Category Breakdown | Issue Frequency, % Share of Total Issues, Aspect Co-occurrence | Product Quality Mgr | `mart_issue_aspect_intelligence` | Phase 9 |
| **BIR-03** | Product & Seller Quality Risk | Product Defect Ratio, Shop Rating Distribution, High-Risk Listing Flag | Category Mgr / Seller Ops | `mart_product_quality` & `mart_seller_intelligence` | Phase 7/9 |
| **BIR-04** | Priority Decision Review Queue | Priority Score (0-100), Severity Rank, Actionable Case Flag | CS Manager | `mart_priority_decision_queue` | Phase 10 |
| **BIR-05** | Model Validation & Transparency | Macro F1, Weighted F1, QWK, Micro F1, Confusion Matrix | Data Science Lead | `mart_model_governance_eval` | Phase 8/9 |
| **BIR-06** | Data Pipeline Quality & Audit | SHA256 Verification, Row Reconciliation (0 loss), Null Rate, Lineage | Data Governance Rev | `mart_data_pipeline_audit` | Phase 6 |

---

## 6. STANDARDIZED TARGET PERFORMANCE BENCHMARKS

To ensure consistent validation across requirement specifications, code pipelines, and reports, the following **Target Performance Metrics** are standardized:

### ML Model Targets (Phase 8 & Phase 9)
1. **Rating Prediction Model (RQ-1 / BIR-05)**:
   - **Macro F1 Target**: $\ge 0.70$
   - **Weighted F1 Target**: $\ge 0.75$
   - **Quadratic Weighted Kappa (QWK) Target**: $\ge 0.75$
2. **Emotion Classification Model (RQ-1 / BIR-05)**:
   - **Macro F1 Target**: $\ge 0.65$
3. **Aspect / Issue Classification Model (RQ-2 / BIR-02)**:
   - **Micro F1 Target**: $\ge 0.70$
   - **Hamming Loss Target**: $\le 0.10$

### Decision Engine Targets (Phase 10)
1. **Priority Scoring Engine (RQ-3 / BIR-04)**:
   - **Separation Ratio Target**: $\ge 2.5$ ($\text{Separation Ratio} = \frac{\text{Mean Priority Score of Severe Cases}}{\text{Mean Priority Score of Non-Severe Cases}}$)
   - **Top-K Precision ($K=50$) Target**: $\ge 0.80$

### Data Pipeline Quality Targets (Phase 6 / BIR-06)
1. **Row Reconciliation**: $\text{Parsed Raw Rows} = \text{Staging Rows}$ ($100\%$ match, $0$ unexplained row loss).
2. **Technical Lineage Key**: `source_record_key` uniqueness $= 100\%$, null count $= 0$.
3. **Imputation Boundary**: Zero silent null imputations ($0\%$ silent coercions).
