# MARKETVOICE SEA — REQUIREMENTS TRACEABILITY MATRIX (RTM)

**Document Version**: 2.0 (Phase 3 Full Traceability Matrix)  
**Phase**: Phase 3 (Business & System Requirements Specification & Governance Baseline)  
**Classification**: Traceability & Verification Baseline  

---

## 1. FULL REQUIREMENT TRACEABILITY MATRIX

The RTM establishes bi-directional traceability linking Business Questions (`BQ`), Research Questions (`RQ`), and Business Information Requirements (`BIR`) to Functional Requirements (`FR`), Non-Functional Requirements (`NFR`), Target Data Marts, Standardized Metric Benchmarks, and Verification Phases:

| Req ID | Business / Research Question | Business Information Requirement (BIR) | Functional Req (FR) | Non-Functional Req (NFR) | Target Data Source / Mart | Standardized Metric Target | Validation Phase |
|---|---|---|---|---|---|---|---|
| **RTM-01** | `BQ-1` (CX Health) | `BIR-01` (CX Condition & Rating Distribution) | `FR-101`, `FR-201`, `FR-203`, `FR-601` | `NFR-202`, `NFR-301` | `mart_cx_overview` | Average Rating, Negative %, Category Rank | Phase 7 / 12 |
| **RTM-02** | `BQ-2`, `RQ-2` (Issue Breakdown & Aspect Extraction) | `BIR-02` (Issue Category Breakdown) | `FR-303`, `FR-203`, `FR-601` | `NFR-202` | `mart_issue_aspect_intelligence` | Micro F1 $\ge 0.70$, Hamming Loss $\le 0.10$ | Phase 9 / 12 |
| **RTM-03** | `BQ-3` (Quality Anomalies) | `BIR-03` (Product & Seller Quality Risk) | `FR-201`, `FR-203`, `FR-601` | `NFR-102`, `NFR-202` | `mart_product_quality` & `mart_seller_intelligence` | Product Defect Ratio, Shop Rating Dist | Phase 7 / 9 / 12 |
| **RTM-04** | `BQ-4`, `RQ-3` (Decision Prioritization) | `BIR-04` (Priority Decision Review Queue) | `FR-401`, `FR-402`, `FR-203`, `FR-601` | `NFR-202` | `mart_priority_decision_queue` | Separation Ratio $\ge 2.5$, Top-K Precision $\ge 0.80$ | Phase 10 / 12 |
| **RTM-05** | `BQ-5` (Operational Workflow) | `BIR-04` (Priority Decision Queue) | `FR-501`, `FR-502` | `NFR-302` | FastAPI `/api/v1/priority/cases` & n8n Webhook | API Latency $< 100$ ms, 100% Webhook Dispatch | Phase 11 |
| **RTM-06** | `BQ-6`, `RQ-1` (Rating Prediction & Governance) | `BIR-05` (Model Validation & Transparency) | `FR-301`, `FR-302`, `FR-304` | `NFR-202` | `mart_model_governance_eval` | Macro F1 $\ge 0.70$, Weighted F1 $\ge 0.75$, QWK $\ge 0.75$ | Phase 8 / 13 |
| **RTM-07** | `RQ-4` (BI System Integration & Traceability) | `BIR-06` (Data Pipeline Quality & Audit) | `FR-102`, `FR-103`, `FR-104`, `FR-202` | `NFR-101`, `NFR-201`, `NFR-401` | `mart_data_pipeline_audit` | Row Reconciliation $= 100\%$, Key Uniqueness $= 100\%$ | Phase 6 / 12 |

---

## 2. TRACEABILITY VERIFICATION SUMMARY

- **Business Questions Covered**: 6 of 6 (`BQ-1` through `BQ-6`) $\rightarrow 100\%$ Coverage.
- **Research Questions Covered**: 4 of 4 (`RQ-1` through `RQ-4`) $\rightarrow 100\%$ Coverage.
- **Information Requirements Covered**: 6 of 6 (`BIR-01` through `BIR-06`) $\rightarrow 100\%$ Coverage.
- **Target Metrics Standardized**: 100% of performance targets are explicitly defined with quantitative validation thresholds.
