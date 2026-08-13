# MARKETVOICE SEA — CANONICAL ROADMAP & PHASE GATE SPECIFICATION

**Document Version**: 4.1 (Phase 3 Reconciled; Phase 4–5 Controlled Execution)
**Phase**: Phase 5 (Architecture & Data Model)
**Data Foundation Version**: `DATA_FOUNDATION_VERSION = 1.0` (Frozen)  
**Current Status**: `PHASE_3_GATE_STATUS = PASS`, `PHASE_4_GATE_STATUS = PASS`, `PHASE_5_GATE_STATUS = PASS`
**Classification**: Phase Transition & Gate Control Document  

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

## 4. PHASE 3 GATE STATUS RECORD

```
====================================================================
                  PHASE 3 GATE STATUS RECORD                        
====================================================================

  PHASE_3_EXECUTION_STATUS  = COMPLETED
  PHASE_3_REVIEW_STATUS     = RECONCILED_UNDER_CONTROLLED_EXECUTION
  PHASE_3_VALIDATION_STATUS = PASS
  PHASE_3_GATE_STATUS       = PASS

====================================================================
```

**Canonical reference correction:**

| Field | Record |
|---|---|
| `OLD_REFERENCE` | `business_requirements_document.md`, `system_requirements_specification.md`, `information_requirements_and_kpi_dictionary.md`, `requirements_traceability_matrix.md`, `business_and_system_requirements.md`, `phase_03_requirements_recap_report.md` |
| `NEW_REFERENCE` | `business_and_information_requirements.md`, `system_requirements.md`, `use_cases_and_mvp.md`, `requirements_traceability.md`, `phase_03_validation.md` |
| `REASON` | Phase 3 v2 consolidated requirements and removed implementation detail inconsistent with the logical-requirements boundary. |
| `IMPACT` | Current gate references point to v2. Phase 0–2 evidence remains unchanged; the legacy v1 structural validator is not gate evidence. |

## 5. PHASE 4 GATE STATUS RECORD

```
PHASE_4_BUILD_STATUS = COMPLETE
PHASE_4_VALIDATION_STATUS = PASS
PHASE_4_GATE_STATUS = PASS
```

## 6. PHASE 5 GATE STATUS RECORD

```
PHASE_5_BUILD_STATUS = COMPLETE
PHASE_5_VALIDATION_STATUS = PASS
PHASE_5_GATE_STATUS = PASS
PHASE_6_EXECUTION_STATUS = NOT_STARTED
```
