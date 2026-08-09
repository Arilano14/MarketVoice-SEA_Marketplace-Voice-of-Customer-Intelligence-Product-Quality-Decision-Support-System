# MARKETVOICE SEA — PROJECT DEFINITION OF DONE & DELIVERABLES REGISTER

**Document Version**: 1.0  
**Phase**: Phase 0 (Governance & Scope)  
**Classification**: Quality Assurance & Project Verification Baseline  

---

## 1. PLANNED DELIVERABLE REGISTER

The MarketVoice SEA project defines 29 planned deliverables across the 15-phase canonical roadmap:

| DEL-ID | Deliverable Name | Type | Creation Phase | Dependencies | Acceptance Criteria |
|---|---|---|---|---|---|
| **DEL-01** | Project Governance & Scope Baseline | Required | Phase 0 | None | Approved Phase 0 Plan & Gate Criteria |
| **DEL-02** | Environment Scaffolding & Data Acquisition | Required | Phase 1 | DEL-01 | Python, Postgres, Git tools configured |
| **DEL-03** | Dataset Forensic Audit Report | Required | Phase 2 | DEL-02 | Verified schema, noise, imbalance, license terms |
| **DEL-04** | Business Requirements Document (BRD) | Required | Phase 3 | DEL-03 | BRD covering all business objectives and BQs |
| **DEL-05** | System Requirements Specification (SRS) | Required | Phase 3 | DEL-03 | SRS specifying all FRs, NFRs, and APIs |
| **DEL-06** | Research & Experimental Design Specification | Required | Phase 4 | DEL-04, DEL-05 | Formal experimental methodology & RQ metrics |
| **DEL-07** | System Architecture & Data Model Spec | Required | Phase 5 | DEL-06 | Kimball Star Schema & system architecture diagram |
| **DEL-08** | PostgreSQL Data Warehouse & Staging Schema | Required | Phase 6 | DEL-07 | DDL scripts creating staging, DW, and marts |
| **DEL-09** | Reproducible SQL/Python ETL Pipeline | Required | Phase 6 | DEL-08 | Automated ETL loading raw/synthetic data to DW |
| **DEL-10** | Automated Data Quality Test Suite | Required | Phase 6 | DEL-09 | Automated test suite passing with 0 critical fails |
| **DEL-11** | Baseline Business Intelligence Queries | Required | Phase 7 | DEL-09 | SQL scripts producing core CX summary marts |
| **DEL-12** | Rating/Sentiment ML Models & Evaluation | Required | Phase 8 | DEL-09 | Baseline & candidate models evaluated on test split |
| **DEL-13** | Aspect & Issue Intelligence Classifier | Required | Phase 9 | DEL-03, DEL-12 | Candidate taxonomy validated & classifier evaluated |
| **DEL-14** | Decision Priority Scoring Engine | Required | Phase 10 | DEL-12, DEL-13 | Configurable scoring engine & sensitivity report |
| **DEL-15** | Decision Priority Case Queue Mart | Required | Phase 10 | DEL-14 | DW mart exposing prioritized review cases |
| **DEL-16** | FastAPI Analytical REST Microservice | Required | Phase 11 | DEL-15 | REST API providing priority queue & metrics JSON |
| **DEL-17** | n8n Operational Ticket Workflow | Required | Phase 11 | DEL-16 | n8n workflow triggering webhook tickets |
| **DEL-18** | Power BI Page: Executive CX Overview | Required | Phase 12 | DEL-11, DEL-16 | Multi-page report: Macro CX trends & ratings |
| **DEL-19** | Power BI Page: Product & Aspect Intelligence | Required | Phase 12 | DEL-13, DEL-16 | Multi-page report: Issue breakdown & category risk |
| **DEL-20** | Power BI Page: Operational Decision Support | Required | Phase 12 | DEL-15, DEL-16 | Multi-page report: Priority review case queue |
| **DEL-21** | Power BI Page: Model & Data Governance | Required | Phase 12 | DEL-10, DEL-12 | Multi-page report: Model F1/confusion & DQ health |
| **DEL-22** | Integrated End-to-End Test Suite | Required | Phase 13 | DEL-16, DEL-17 | Automated integration tests passing clean |
| **DEL-23** | Scenario-Based UAT Report | Required | Phase 13 | DEL-22 | Simulated stakeholder scenario test sign-offs |
| **DEL-24** | Model Cards (Model Transparency) | Required | Phase 14 | DEL-12, DEL-13 | Model Card documentation following standard schema |
| **DEL-25** | System Limitations & Technical Risk Report | Required | Phase 14 | DEL-24 | Comprehensive report of system edge cases & risks |
| **DEL-26** | Final Technical S2 Portfolio Report | Required | Phase 14 | DEL-25 | S2-quality academic technical documentation |
| **DEL-27** | Executive Summary Brief | Required | Phase 14 | DEL-26 | High-level non-technical executive summary |
| **DEL-28** | Visual Portfolio Screenshot Assets | Required | Phase 14 | DEL-18..21 | Portfolio screenshot gallery of BI & workflow |
| **DEL-29** | End-to-End Reproducibility Guide | Required | Phase 14 | DEL-09, DEL-22 | Step-by-step single-command setup guide |

---

## 2. PROJECT-LEVEL DEFINITION OF DONE (DoD)

The MarketVoice SEA project will be considered 100% complete when all of the following criteria are satisfied:

1. **Governance & Compliance**:
   * All 13 mandatory governance flags are strictly respected.
   * Dataset licensing permissions are verified in Phase 2; raw data is excluded from public Git repositories.
   * Every Track B synthetic record carries `is_synthetic = TRUE` database flags and `[SYNTHETIC DATA]` UI banners.
   * Zero false commercial performance or unverified revenue claims exist in documentation or reporting.

2. **Data Engineering & Data Warehouse**:
   * Staging, Kimball Star Schema DW, and Data Mart DDL scripts execute cleanly in PostgreSQL.
   * ETL pipelines process raw and synthetic data reproducibly using single-command Python scripts.
   * Automated Data Quality test suite passes cleanly with 0 critical assertion failures.

3. **Machine Learning & Decision Analytics**:
   * Baseline and candidate sentiment/rating models are trained, evaluated, and documented.
   * Candidate issue taxonomy is empirically validated and multi-label aspect classifier evaluated.
   * Explainable decision priority scoring engine is implemented and sensitivity-tested.

4. **Integration & Business Intelligence**:
   * FastAPI analytical REST microservice serves priority queues and model metrics in JSON format.
   * n8n workflow executes automated webhook ticket simulation for high-priority complaints.
   * Power BI multi-page report provides interactive executive, quality, model, and governance insights.
   * Integrated end-to-end test suite passes cleanly across API, workflow, and DW components.

5. **Academic & Portfolio Documentation**:
   * S2-quality technical report, Model Cards, UAT Report, and Reproducibility Guide are completed.
   * Complete 1-to-1 alignment across Charter, Requirements Traceability Matrix, and Phase Gates.
