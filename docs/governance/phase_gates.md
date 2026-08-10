# MARKETVOICE SEA — CANONICAL ROADMAP & PHASE GATE SPECIFICATION

**Document Version**: 2.0 (Dual-Source Remediation & Phase 2 Gate PASS)  
**Phase**: Phase 2 (Dataset Forensic Audit & Data Readiness)  
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

## 3. PHASE 2 FORENSIC AUDIT CHECKLIST

To verify the completion of Phase 2 Forensic Audit, the following audit checklist was evaluated:

- [x] Canonical Source A (`SRC_PRDECT_ID_V1`, Mendeley DOI: `10.17632/574v66hf2v.1`) acquired & hash verified (`1dfdde6bb169ad57aab4211ecf45a75a4111b774ab43932f6d39c349bfd92bde`).
- [x] Canonical Source B (`SRC_TOKOPEDIA_REVIEWS_2019`, HuggingFace `farhamu/tokopedia-product-reviews-2019`) acquired & hash verified (`dbffc29078db1894e60884c526fe4d0ccbc592f33fe95d2e5ac2d8f96336b7ed`).
- [x] Raw directories strictly isolated under `data/raw/prdect_id/` and `data/raw/tokopedia_product_reviews_2019/`.
- [x] Empirical schema profiling completed (Source A: 5,400 rows, 11 cols; Source B: 40,607 rows, 8 cols).
- [x] Provided annotated labels (`Sentiment`, `Emotion`) confirmed present in Source A.
- [x] Type forensics completed for Source B (`product_id`, `shop_id`, `sold`).
- [x] Zero cross-source product or shop linkage enforced (`CROSS_SOURCE_LINKAGE = NOT_SUPPORTED`).
- [x] System lineage model updated to `DATA_SOURCE` → `SOURCE_FILE` → `IMPORT_BATCH` → `STAGING`.
- [x] `reports/validation/phase_02_dataset_forensic_audit_report.md` authored.
- [x] Permanent Git Remote policy locked (`REMOTE_REPOSITORY_CONTROL = USER_ONLY`). Zero `git push` commands executed.
- [x] Zero database table creation, zero DDL execution, zero synthetic data generation occurred.

---

## 4. FORMAL PHASE 2 GATE EVALUATION

```
====================================================================
                  PHASE 2 GATE EVALUATION RESULT                    
====================================================================

  PHASE_2_EXECUTION_STATUS  = COMPLETED
  PHASE_2_GATE_STATUS       = PASS

====================================================================
```

### Gate Evaluation Rationale
All Phase 2 Definition of Done criteria, mandatory plan corrections, canonical acquisition steps, forensic schema checks, type analyses, and data quality registers have been satisfied and verified with empirical evidence.

The project is officially authorized to proceed to **Phase 3: Business & System Requirements**.
