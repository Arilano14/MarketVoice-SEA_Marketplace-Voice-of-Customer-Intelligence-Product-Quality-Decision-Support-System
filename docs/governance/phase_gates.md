# MARKETVOICE SEA — CANONICAL ROADMAP & PHASE GATE SPECIFICATION

**Document Version**: 2.1 (Phase 2 Hardened & Frozen v1.0)  
**Phase**: Phase 2 (Dataset Forensic Audit & Data Readiness)  
**Data Foundation Version**: `DATA_FOUNDATION_VERSION = 1.0` (Frozen)  
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

## 3. PHASE 2 FINAL HARDENING CHECKLIST

- [x] Pre/Post SHA256 hashes 100% matched (`RAW_DATA_LOCKED = TRUE`).
- [x] Derived standardized datasets generated in `data/interim/validated/`.
- [x] System lineage key `source_record_key` 100% unique, 0 nulls.
- [x] Cross-source text overlap (exact, normalized, near-duplicate) quantified.
- [x] Label dependency crosstabs generated (STRONGLY_RATING_DEPENDENT).
- [x] Source B entity cardinality mapped (`product_id` listing key verified).
- [x] PRDECT product context stability evaluated.
- [x] Advanced text forensics profiled (emojis, URLs, HTML entities, length statistics).
- [x] Transformation contracts executed losslessly.
- [x] Category harmonization mapped without fake categories.
- [x] Human aspect annotation protocol defined (`docs/research/issue_annotation_protocol.md`).
- [x] Track B synthetic data simulation policy locked (`is_synthetic = TRUE`).
- [x] Reproducibility test 100% PASS.
- [x] Permanent Git Remote policy locked (`REMOTE_REPOSITORY_CONTROL = USER_ONLY`). Zero `git push` executed.
- [x] Zero database table creation, zero DDL execution occurred.

---

## 4. FORMAL PHASE 2 GATE & DATA FOUNDATION FREEZE RESULT

```
====================================================================
                  PHASE 2 FINAL GATE & FREEZE RESULT                
====================================================================

  PHASE_2_EXECUTION_STATUS      = COMPLETED
  PHASE_2_GATE_STATUS           = PASS
  DATA_FOUNDATION_VERSION       = 1.0
  RAW_DATA_LOCKED               = TRUE
  STANDARDIZED_DATA_READY       = TRUE
  DATABASE_IMPLEMENTATION_READY = TRUE

====================================================================
```

### Gate Evaluation Rationale
All Phase 2 Hardening workstreams, non-destructive interim layer generations, system lineage keys, cross-source overlap analyses, label dependency crosstabs, entity cardinalities, and text forensics have been completely executed and verified deterministically.

The project is officially authorized to proceed to **Phase 3: Business & System Requirements**.
