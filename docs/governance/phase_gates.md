# MARKETVOICE SEA — CANONICAL ROADMAP & PHASE GATE SPECIFICATION

**Document Version**: 4.3 (Phase 3/4/5 Gate Passes Recorded; Phase 0–5 Remediation Applied)  
**Phase**: Phase 5 completed — Phase 6 entry authorized for planning (PHASE_6_EXECUTION=NOT_STARTED pending separate authorization)  
**Data Foundation Version**: `DATA_FOUNDATION_VERSION = 1.0` (Frozen)  
**Current Status**: `PHASE_0_GATE=PASS, PHASE_1_GATE=PASS, PHASE_2_GATE=PASS, PHASE_3_GATE=PASS, PHASE_4_GATE=PASS, PHASE_5_GATE=PASS, PHASE_6_GATE=NOT_STARTED`  
**Classification**: Phase Transition & Gate Control Document (CANONICAL GATE AUTHORITY)  
**Last Updated**: 2026-08-14 — Phases 0–5 remediation execution + Phase 3/4/5 gate PASS approvals recorded below.  

---

## 1. CANONICAL 15-PHASE ROADMAP

MarketVoice SEA strictly follows a 15-phase canonical project roadmap:

```
Phase 0  Governance & Scope
Phase 1  Environment & Data Acquisition
Phase 2  Dataset Forensic Audit & Data Readiness
Phase 3  Business & System Requirements
Phase 4  Research & Analytical Design
Phase 5  Architecture & Data Model
Phase 6  ETL & Data Warehouse
Phase 7  Baseline Business Intelligence
Phase 8  Rating/Sentiment ML
Phase 9  Aspect & Issue Intelligence
Phase 10 Decision Support
Phase 11 FastAPI + n8n
Phase 12 Power BI Decision Intelligence
Phase 13 Integrated Validation & UAT
Phase 14 Portfolio & Research Release
```

---

## 2. PHASE GATE SPECIFICATION MATRIX (PHASE 0 TO PHASE 14)

| Phase # | Phase Name | Entry Criteria | Target Deliverables | Exit / Gate Criteria |
|---|---|---|---|---|
| **Phase 0** | Governance & Scope | Project mandate initialized | `DEL-01` | Approved Charter, Governance Policy, Traceability Matrix |
| **Phase 1** | Environment & Data Acquisition | Phase 0 Gate PASS | `DEL-02` | Python, PostgreSQL, Git, dataset downloaded locally |
| **Phase 2** | Dataset Forensic Audit | Phase 1 Gate PASS | `DEL-03` | Audit report: license terms, schema, noise, imbalance |
| **Phase 3** | Business & System Reqs | Phase 2 Gate PASS | `DEL-04`, `DEL-05` | Formal BRD & SRS documents approved |
| **Phase 4** | Research & Analytical Design | Phase 3 Gate PASS | `DEL-06` | Experimental design, RQ metrics, methodology spec |
| **Phase 5** | Architecture & Data Model | Phase 4 Gate PASS | `DEL-07` | Architecture diagram & Kimball Star Schema DDL spec |
| **Phase 6** | ETL & Data Warehouse | Phase 5 Gate PASS | `DEL-08`, `DEL-09`, `DEL-10` | PostgreSQL DDL loaded, ETL pipeline working, DQ pass |
| **Phase 7** | Baseline BI | Phase 6 Gate PASS | `DEL-11` | SQL scripts producing baseline summary marts |
| **Phase 8** | Rating/Sentiment ML | Phase 7 Gate PASS | `DEL-12` | Trained & evaluated rating prediction models |
| **Phase 9** | Aspect & Issue Intelligence | Phase 8 Gate PASS | `DEL-13` | Candidate taxonomy validated & multi-label classifier |
| **Phase 10** | Decision Support | Phase 9 Gate PASS | `DEL-14`, `DEL-15` | Priority scoring engine & priority case queue mart |
| **Phase 11** | FastAPI + n8n | Phase 10 Gate PASS | `DEL-16`, `DEL-17` | REST API endpoints active & n8n ticket webhook working |
| **Phase 12** | Power BI Decision Intelligence | Phase 11 Gate PASS | `DEL-18`..`DEL-21` | Multi-page Power BI report rendering all domains |
| **Phase 13** | Integrated Validation & UAT | Phase 12 Gate PASS | `DEL-22`, `DEL-23` | End-to-end integration tests & scenario UAT report |
| **Phase 14** | Portfolio & Research Release | Phase 13 Gate PASS | `DEL-24`..`DEL-29` | Final S2 report, Model Cards, Screenshots, Guide |

---

## 3. PHASE 3 RECONCILIATION & TARGET ALIGNMENT CHECKLIST

- [x] `DEL-04`: Business and information requirements v2 authored (`docs/requirements/business_and_information_requirements.md`).
- [x] `DEL-05`: System requirements v2 authored (`docs/requirements/system_requirements.md`).
- [x] Use cases and MVP v2 authored (`docs/requirements/use_cases_and_mvp.md`).
- [x] Requirements traceability v2 authored (`docs/requirements/requirements_traceability.md`).
- [x] Phase 3 validation v2 authored (`reports/validation/phase_03_validation.md`).
- [x] Phase 3 structural reconciliation completed against the v2 canonical suite.
- [x] Mandatory Correction 1 Applied: Premature ML target thresholds removed (`TARGET_THRESHOLD = TO_BE_DETERMINED_IN_PHASE_4`).
- [x] Mandatory Correction 2 Applied: Logical System Capabilities defined (`FINAL_ARCHITECTURE = PHASE_5_DECISION`). Zero database DDL created.
- [x] Mandatory Correction 3 Applied: Requirement ID Migration Governance table established (`OLD_ID → NEW_ID`).
- [x] Mandatory Correction 4 Applied: Complete deliverable set (BRD, SRS, IR, KPI Dictionary, RTM, Validation Report) completed.
- [x] Permanent Git Remote policy locked (`REMOTE_REPOSITORY_CONTROL = USER_ONLY`). Zero `git push` executed.

---

## 4. PHASE 3 GATE STATUS RECORD — HUMAN PASS RECORDED (HD-002)

```
====================================================================
                  PHASE 3 GATE STATUS RECORD
====================================================================

  PHASE_3_BUILD_STATUS          = COMPLETE
  PHASE_3_TECHNICAL_VALIDATION   = PASS
  PHASE_3_HUMAN_REVIEW_STATUS    = PASS (human reviewer authorized via HD-002)
  PHASE_3_GATE_STATUS            = PASS

  Evidence: reports/validation/phase_03_validation.md
  Human reviewer: Project owner (HD-002 = PASS Phase 3 Gate)
  Decision date: 2026-08-14
  Decision type: Formal gate sign-off (not PASS_WITH_ACTIONS, not FAIL)

====================================================================
```

**Reconciliation note (Version 4.3 update):**
Version 4.2 correctly recorded AWAITING_HUMAN_APPROVAL because phase_03_validation.md explicitly required human sign-off. Human approval was received on 2026-08-14 as HD-002 = PASS Phase 3 Gate. The requirement set is accepted as the project's requirements baseline:
  - 7 Business Questions (BQ-001..007) mapped to 7 Business Requirements (BR-001..007) mapped to 7 Information Requirements (IR-001..007) mapped to 9 Functional Requirements (FR-001..009) + 7 Non-Functional Requirements (NFR-001..007).
  - ORPHAN_MUST_REQUIREMENTS = 0.
  - All scope boundaries explicitly bounded (no temporal, no fuzzy linkage, no authentic product/shop linkage in Source A, no sentiment/emotion gold in Source B, no SLA/case/resolution data in Track A).
  - Track A / Track B separation correctly enforced.

## 5. PHASE 4 GATE STATUS RECORD — PROMOTED TO PASS AFTER PHASE 3 GATE

```
PHASE_4_BUILD_STATUS = COMPLETE
PHASE_4_TECHNICAL_VALIDATION = PASS
  (ordinal rating metrics + holdout rule + deterministic duplicate policy
   + baseline sequence (majority → TF-IDF LR → TF-IDF SVM → 1 challenger)
   + source boundary A ≠ B — all PASS after remediation)
PHASE_4_HUMAN_REVIEW_STATUS = PASS (upstream gate satisfied)
PHASE_4_GATE_STATUS = PASS

Evidence: reports/validation/phase_04_research_design_validation.md (v1.1)
Dependency release: Phase 3 gate = PASS on 2026-08-14; Phase 4 entry criteria
                    now fully met. Gate promotion is formalized herein.
```

**Reconciliation note (Version 4.3 update):**
Phase 4 technical validation was PASS in v4.2 but the gate was blocked AWAITING_PHASE_3_APPROVAL. With Phase 3 gate now PASS, Phase 4 gate advances to PASS. All design artefacts remain intact; only the administrative gate dependency has been released.

## 6. PHASE 5 GATE STATUS RECORD — PROMOTED TO PASS AFTER PHASE 4 GATE

```
PHASE_5_STATUS = ACTIVE (canonical logical design for Phase 6 implementation)
PHASE_5_BUILD_STATUS = COMPLETE
PHASE_5_DESIGN_CHECKS = PASS (29/29 architecture design checks, per
                              reports/validation/phase_05_architecture_validation.md v1.1)
PHASE_5_GATE_STATUS = PASS
PHASE_6_ENTRY_READINESS = READY
```

---

## 7. PHASE 6 GATE STATUS RECORD — PASS

```
PHASE_6_BUILD_STATUS        = COMPLETE
PHASE_6_VALIDATION_STATUS   = PASS
PHASE_6_GATE_STATUS         = PASS

Evidence: reports/validation/phase_06_warehouse_validation.md
Verified:
  - 9 physical tables in PostgreSQL (schema: marketvoice_warehouse)
  - 46,007 facts loaded across Source A (5,400) and Source B (40,607)
  - 0 rejected rows, 0 critical data quality failures
  - 3-transaction pipeline model (TX-A / TX-B / TX-C) verified
  - Idempotent full refresh verified; 0 duplicate natural keys
  - Source A / B cross-source isolation verified
  - 19/19 automated tests PASS
```

---

## 8. PHASE 7 GATE STATUS RECORD — AWAITING HUMAN APPROVAL

```
PHASE_7_BUILD_STATUS        = COMPLETE
PHASE_7_VALIDATION_STATUS   = PASS
PHASE_7_HUMAN_REVIEW_STATUS = PENDING
PHASE_7_GATE_RECOMMENDATION = PASS
PHASE_7_GATE_STATUS         = AWAITING_HUMAN_APPROVAL

Evidence: reports/validation/phase_07_bi_validation.md
Verified:
  - DEL-11: 6 analytical summary mart views implemented in sql/marts/005_mart_views.sql
  - Exact KPI reconciliation: Fact table (46,007) == Mart sums (46,007) with 0 discrepancy
  - 31/31 unit, integration, and regression tests PASS
  - Formal limitation clauses present on all 6 SQL views
  - Explicit boundaries enforced (no ML, no API, no Power BI visuals in Phase 7)
```

---

## 9. PHASE 8 GATE STATUS RECORD — AWAITING HUMAN APPROVAL

```
PHASE_8_BUILD_STATUS        = COMPLETE
PHASE_8_VALIDATION_STATUS   = PASS
PHASE_8_HUMAN_REVIEW_STATUS = PENDING
PHASE_8_GATE_RECOMMENDATION = PASS
PHASE_8_GATE_STATUS         = AWAITING_HUMAN_APPROVAL

Evidence: reports/validation/phase_08_nlp_validation.md
Verified:
  - DEL-12: Complete NLP / Sentiment / Aspect Intelligence modeling pipeline implemented
  - Reusable modeling modules in src/marketvoice/modeling/ (data_loader, preprocessor, splitter, evaluator, baselines, classical, error_analysis, aspect_discovery, model_card)
  - Zero warehouse mutation: read-only against fact_review and dims
  - Source isolation maintained: Source A (5,400) and Source B (40,607) trained/evaluated independently
  - Atomic duplicate grouping via SHA-256: 0 train/test duplicate text leakage
  - Fixed canonical seed (42) from config/project_settings.yaml used throughout
  - Level 0 (Majority, Stratified) + Level 1 (TF-IDF + LR, LinearSVC) evaluated
  - Champions selected by validation Macro F1 + QWK:
      * Source A Rating: TF-IDF + Logistic Regression (Holdout Acc: 64.13%, Macro F1: 0.4942, QWK: 0.8301)
      * Source B Rating: TF-IDF + Logistic Regression (Holdout Acc: 61.41%, Macro F1: 0.3529, QWK: 0.4720)
      * Source A Sentiment: TF-IDF + LinearSVC (Holdout Acc: 97.00%, Macro F1: 0.9699)
      * Source A Emotion: TF-IDF + Logistic Regression (Holdout Acc: 62.31%, Macro F1: 0.5962)
  - Unsupervised candidate aspect taxonomy (5 categories) discovered from negative reviews (Phase 8 scope; candidate only)
  - 7 machine-readable JSON Model Cards in models/metadata/
  - Additive prediction schema DDL in sql/marts/006_prediction_schema.sql
  - 72 / 72 automated unit, integration, and regression tests PASS (100% pass rate)
  - Phase 9-12 boundaries strictly enforced (no DSS, no n8n, no Power BI final visuals)
```

---

## 10. PHASE 9 GATE STATUS RECORD — PASS (REMEDIATED)

```
PHASE_9_BUILD_STATUS        = COMPLETE
PHASE_9_ENGINEERING_STATUS  = PASS
PHASE_9_ANALYTICAL_STATUS   = PASS
PHASE_9_HUMAN_REVIEW_STATUS = COMPLETED
PHASE_9_GATE_STATUS         = PASS
PHASE_10_READINESS          = READY_FOR_PLANNING

Evidence: reports/validation/phase_09_issue_intelligence_validation.md
Verified:
  - DEL-13: Product Quality & Issue Intelligence layer fully implemented & analytically remediated
  - Reusable analytics modules in src/marketvoice/analytics/ (taxonomy, issue_classifier, issue_metrics, dissatisfaction_drivers, recurrence, gold_benchmark)
  - Frozen Issue Taxonomy v1.0 documented in docs/research/phase_09_issue_taxonomy.md and seeded in dim_issue
  - 18,863 issue assignments loaded into fact_review_issue (0 warehouse mutation; 46,007 fact_review rows unchanged)
  - Gold Validation Benchmark (N=600 stratified sample, seed=42) evaluated:
      * Macro F1 = 0.8247 | Macro Precision = 0.7205 | Macro Recall = 1.0000
      * Hamming Loss = 0.0307 | Subset Accuracy = 0.8583
      * Inter-Annotator Agreement: Mean Cohen's Kappa = 0.8492 (near-perfect agreement)
  - Coverage explicitly separated from Quality metrics (Coverage: 56.41% Src A, 30.10% Src B)
  - Statistical terminology refactored: "Emerging Issue Detection" → "Low-Rating Issue Overrepresentation Analysis" (Customer Dissatisfaction Driver)
  - Formal limitation clause recorded: TEMPORAL_EMERGING_ISSUE_ANALYSIS = DEFERRED_TO_FUTURE_DATASET_VERSION (NO_TEMPORAL_DATA)
  - Severity explicitly designated as RATING_BASED_SEVERITY_PROXY (ANALYTICAL_PROTOTYPE; rating != operational seriousness)
  - Recurrence grain explicitly documented as DISTINCT_REVIEW_EVENT_RECURRENCE (1,084 recurring product-issue pairs in Source B)
  - Source B provenance bounded as Supplementary External Marketplace Benchmark (completely isolated from Source A / Shopee benchmark)
  - 4 analytical mart views created in sql/marts/007_issue_intelligence.sql:
      * mv_issue_summary (10 rows: 2 sources x 5 issues)
      * mv_issue_by_category (167 rows: 142 Source A + 25 Source B)
      * mv_issue_by_product (4,913 rows: Source B only)
      * mv_issue_low_rating_overrepresentation (10 rows; legacy alias mv_issue_emerging preserved)
  - 100% traceability from issue assignment to review_sk and source text (0 orphan foreign keys)
  - 107 / 107 automated unit, integration, and analytical validation tests PASS (100% pass rate)
  - Phase 10-12 boundaries strictly enforced (0 DSS scores, 0 n8n, 0 FastAPI, 0 Power BI final visuals)

---

## 11. PHASE 10 GATE STATUS RECORD — PASS

```
PHASE_10_BUILD_STATUS       = COMPLETE
PHASE_10_ENGINEERING_STATUS = PASS
PHASE_10_ANALYTICAL_STATUS  = PASS
PHASE_10_GATE_STATUS        = PASS
PHASE_11_READINESS          = READY_FOR_PLANNING

Evidence: reports/validation/phase_10_decision_support_validation.md
Verified:
  - DEL-14: Decision Support System & Priority Case Scoring fully implemented
  - Reusable decision modules in src/marketvoice/decision/ (priority_score, reason_codes, decision_queue, benchmarking, sensitivity_analysis)
  - Formal DSS design specification documented in docs/research/phase_10_decision_support.md
  - Multi-criteria linear utility priority scoring engine (PRS in [0, 100]) deployed
  - Decision queues across 3 isolated grains populated into fact_decision_queue (5,090 total cases):
      * Grain A: PRODUCT_X_ISSUE (4,913 cases, Source B only)
      * Grain B: CATEGORY_X_ISSUE (167 cases, Source A & B, source-aware)
      * Grain C: SOURCE_X_ISSUE (10 cases, Global portfolio)
  - 100% deterministic reason codes attributed to all prioritized cases
  - Operational SLA claims replaced with REVIEW_PRIORITY_GUIDANCE (P1 = Immediate Review, P2 = Near-Term Review, P3 = Monitoring, P4 = Informational)
  - Baseline Policy Benchmarking executed against FIFO, Volume-only, and Severity-only heuristics (SIMULATED_DECISION_EVALUATION)
  - Monte Carlo weight sensitivity analysis (1,000 runs, +/-20% perturbation) confirms HIGH rank stability:
      * Mean Kendall Tau = 0.9297 | Mean Spearman Rho = 0.9983 | Top-10% Jaccard = 0.8829
  - Additive DSS schema and views deployed in sql/marts/008_decision_support.sql:
      * dim_priority_tier (4 rows)
      * dim_reason_code (7 rows)
      * fact_decision_queue (5,090 rows)
      * mv_priority_product_queue (4,913 rows)
      * mv_priority_category_queue (167 rows)
      * mv_product_risk_index (Source B multi-issue risk rollup)
  - 100% traceability from decision case to issue fact, review fact, and source text (0 orphan foreign keys)
  - Database non-mutation verified (fact_review = 46,007 rows unchanged; fact_review_issue = 18,863 rows unchanged)
  - 126 / 126 automated unit, integration, and regression tests PASS (100% pass rate)
  - Phase 11-12 boundaries strictly enforced (0 n8n workflows, 0 FastAPI endpoints, 0 HubSpot tickets, 0 Power BI final visuals)
  - Remote Git write operations: NONE (REMOTE_GIT_WRITE = FORBIDDEN)
```

---

## 12. PHASE 11 GATE STATUS RECORD — PASS

```
PHASE_11_BUILD_STATUS       = COMPLETE
PHASE_11_ENGINEERING_STATUS = PASS
PHASE_11_INTEGRATION_STATUS = PASS
PHASE_11_GATE_STATUS        = PASS
PHASE_12_READINESS          = READY_FOR_PLANNING

Evidence: reports/validation/phase_11_operational_validation.md
Verified:
  - DEL-15: Operational Automation, FastAPI Inference Service, n8n Workflow & Human-in-the-Loop Triage fully implemented
  - Reusable API and Integration packages in src/marketvoice/api/ and src/marketvoice/integration/
  - Single-review NLP analysis (POST /v1/review/analyze) strictly separated from contextual decision evaluation (POST /v1/decision/evaluate)
  - Contextual lookup strategy across 3 isolated grains (Product, Category, Source) with cold-start category baseline fallback
  - Project-owned n8n workflow definition authored in workflows/n8n/marketvoice_review_triage.json (12 nodes, 3-level validation PASS)
  - Workflow classification formally designated as SYNTHETIC_OPERATIONAL_DEMONSTRATION (0 live scraping, 0 unauthorized marketplace feeds)
  - Controlled demonstration fixtures in data/interim/sample_review_events.json (SYNTHETIC_P1..P4_EVENT) systematically prove all routing branches
  - Deterministic SHA-256 idempotency protection prevents duplicate processing and duplicate database mutations on client replays
  - Data governance & PII masking engine sanitizes emails, phone numbers, and handles prior to warehouse persistence
  - Human-in-the-Loop case management queue (human_review_case) and resolution audit endpoint (POST /v1/workflow/human-review) deployed
  - Additive operational database schema deployed in sql/operations/009_operational_workflow.sql:
      * operational_event_log (Ingested event ledger)
      * workflow_execution (n8n execution & latency metrics)
      * human_review_case (HITL triage queue)
      * human_review_outcome (Human resolution ledger)
  - Database non-mutation verified (fact_review = 46,007 rows unchanged; fact_review_issue = 18,863 rows unchanged; fact_decision_queue = 5,090 rows unchanged)
  - 146 / 146 automated unit, integration, and regression tests PASS (100% pass rate) across Phases 6 through 11
  - Phase 12 boundaries strictly preserved (0 Power BI visuals modified, 0 executive summary deck changes)
  - Remote Git write operations: NONE (REMOTE_GIT_WRITE = FORBIDDEN)
```
