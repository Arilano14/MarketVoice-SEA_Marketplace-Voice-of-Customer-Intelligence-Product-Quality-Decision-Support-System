# MARKETVOICE SEA — REQUIREMENTS TRACEABILITY MATRIX (RTM) v1.0

**Document Version**: 1.0 (Phase 3 Requirements Baseline v1.0)  
**Deliverable ID**: `RTM Baseline v1.0`  
**Phase**: Phase 3 (Business & System Requirements Specification & Governance Baseline)  
**Data Foundation Baseline**: `DATA_FOUNDATION_VERSION = 1.0` (Dual-Source: `SRC_PRDECT_ID_V1` & `SRC_TOKOPEDIA_REVIEWS_2019`)  
**Phase 3 Status**: `PHASE_3_EXECUTION_STATUS = COMPLETED`, `PHASE_3_REVIEW_STATUS = READY_FOR_HUMAN_REVIEW`, `PHASE_3_GATE_STATUS = NOT_EVALUATED`  

---

## 1. FULL BI-DIRECTIONAL TRACEABILITY MATRIX

The Requirements Traceability Matrix establishes bi-directional traceability linking Business Objectives down to Validation Phases across all 10 Business Requirements (`BR`), 10 Information Requirements (`IR`), 32 KPIs, 14 Functional Requirements (`FR`), 14 Non-Functional Requirements (`NFR`), and Data Capabilities:

| Req ID | Business Question | Business Requirement (BR) | Information Req (IR) | Primary KPI(s) | Functional Req (FR) | Non-Functional Req (NFR) | Data Capability | Primary Data Source | Future Deliverable | Target Validation Phase | Dependency / Boundary |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **RTM-01** | `BQ-CX` | `BR-001` (Macro CX Signals) | `IR-001` | `KPI-CX-01` to `KPI-CX-05` | `FR-004`, `FR-014` | `NFR-001`, `NFR-002` | `CAP-01`, `CAP-02` | Source A & Source B | `DEL-11`, `DEL-18` | Phase 7 / Phase 12 | None |
| **RTM-02** | `BQ-CX`, `BQ-MODEL` | `BR-002` (Provided Annotations) | `IR-002` | `KPI-CX-06`, `KPI-CX-07` | `FR-005`, `FR-011` | `NFR-001`, `NFR-012` | `CAP-03`, `CAP-04` | Source A (`SRC_PRDECT_ID_V1`) | `DEL-11`, `DEL-12` | Phase 7 / Phase 8 | Source A Exclusive |
| **RTM-03** | `BQ-PRODUCT` | `BR-003` (Product Quality Risk) | `IR-003` | `KPI-PRD-01` to `KPI-PRD-03` | `FR-006`, `FR-014` | `NFR-001`, `NFR-002` | `CAP-05` | Source B (`SRC_TOKOPEDIA_REVIEWS_2019`) | `DEL-11`, `DEL-19` | Phase 7 / Phase 12 | Source B Listing IDs |
| **RTM-04** | `BQ-PRODUCT` | `BR-004` (Category Quality Share) | `IR-004` | `KPI-CAT-01` to `KPI-CAT-03` | `FR-007`, `FR-014` | `NFR-001`, `NFR-002` | `CAP-05` | Source A & Source B | `DEL-11`, `DEL-19` | Phase 7 / Phase 12 | Category Mapping Policy |
| **RTM-05** | `BQ-SHOP` | `BR-005` (Shop Review Intelligence) | `IR-005` | `KPI-SHP-01` to `KPI-SHP-04` | `FR-008`, `FR-014` | `NFR-001`, `NFR-005` | `CAP-06` | Source B (`SRC_TOKOPEDIA_REVIEWS_2019`) | `DEL-11`, `DEL-20` | Phase 7 / Phase 12 | Shop Review Intelligence Only |
| **RTM-06** | `BQ-ISSUE` | `BR-006` (Issue Discovery) | `IR-006` | `KPI-ISS-01`, `KPI-ISS-02` | `FR-009`, `FR-014` | `NFR-001`, `NFR-006` | `CAP-01` | Source A & Source B Text | `DEL-13`, `DEL-19` | Phase 9 / Phase 12 | `DEPENDS_ON = PHASE_9_TAXONOMY_AND_ANNOTATION_GATE` |
| **RTM-07** | `BQ-DSS` | `BR-007` (Priority Review Queue) | `IR-007` | `KPI-DSS-01` to `KPI-DSS-03` | `FR-012`, `FR-014` | `NFR-006`, `NFR-007` | Model Inference | Derived Analytical Storage | `DEL-14`, `DEL-15`, `DEL-20` | Phase 10 / Phase 12 | Phase 10 Priority Scoring Design |
| **RTM-08** | `BQ-MODEL` | `BR-008` (Model Evaluation & Governance) | `IR-008` | `KPI-MDL-01` to `KPI-MDL-05` | `FR-010`, `FR-011` | `NFR-012`, `NFR-010` | Model Predictions | Model Validation Logs | `DEL-12`, `DEL-21` | Phase 8 / Phase 13 | `TARGET_THRESHOLD = TO_BE_DETERMINED_IN_PHASE_4` |
| **RTM-09** | `BQ-DQ` | `BR-009` (Data Pipeline Quality) | `IR-009` | `KPI-DQ-01` to `KPI-DQ-06` | `FR-001` to `FR-003` | `NFR-001` to `NFR-003`, `NFR-011` | Ingestion & Lineage Engine | System Pipeline Metadata | `DEL-08` to `DEL-10`, `DEL-21` | Phase 6 / Phase 12 | `DATA_FOUNDATION_VERSION = 1.0` |
| **RTM-10** | `BQ-DSS` | `BR-010` (Simulated Workflow Track B) | `IR-010` | `KPI-DSS-04` | `FR-013` | `NFR-007`, `NFR-008` | Synthetic Event Generator | Track B Synthetic Workflow Logs | `DEL-16`, `DEL-17` | Phase 11 | `is_synthetic = TRUE`, `scenario_version` |

---

## 2. TRACEABILITY COVERAGE & ORPHAN AUDIT SUMMARY

```
================================================================================
MARKETVOICE SEA — TRACEABILITY COVERAGE & AUDIT SUMMARY
================================================================================
- Business Questions Covered:      7 of 7 (100.0% Coverage)
- Business Requirements Covered:   10 of 10 (100.0% Coverage)
- Information Requirements:        10 of 10 (100.0% Coverage)
- KPIs Fully Traceable:            32 of 32 (100.0% Coverage)
- Functional Requirements:         14 of 14 (100.0% Coverage)
- Non-Functional Requirements:      14 of 14 (100.0% Coverage)
--------------------------------------------------------------------------------
- ORPHAN MUST BUSINESS REQUIREMENTS:     0 (PASS)
- ORPHAN MUST FUNCTIONAL REQUIREMENTS:   0 (PASS)
- ORPHAN APPROVED KPIS:                  0 (PASS)
- CONDITIONAL REQUIREMENTS DEPENDENCY:   100.0% Explicitly Specified
================================================================================
```

---

## 3. DATA CAPABILITY → REQUIREMENT MATRIX

Every requirement record is evaluated against underlying data support in `DATA_FOUNDATION_VERSION = 1.0`:

| Requirement ID | Required Data Elements | Source A Support (`SRC_PRDECT_ID_V1`) | Source B Support (`SRC_TOKOPEDIA_REVIEWS_2019`) | Standardized Target Field(s) | Authentic or Simulated | Support Status | Limitation | Decision |
|---|---|---|---|---|---|---|---|---|
| `BR-001` / `IR-001` | Review text, star rating | `AVAILABLE` | `AVAILABLE` | `rating`, `Customer Rating` | `AUTHENTIC_DATA` | `SUPPORTED` | Unsupported for real temporal trend analytics. | `APPROVE` |
| `BR-002` / `IR-002` | Provided Sentiment & Emotion labels | `AVAILABLE` (Gold annotations) | `NOT_AVAILABLE` | `Sentiment`, `Emotion` | `AUTHENTIC_DATA` | `SUPPORTED_SOURCE_A_ONLY` | Unavailable for Source B dataset. | `APPROVE` |
| `BR-003` / `IR-003` | `product_id`, `product_name`, `rating` | `PARTIAL` (text titles only) | `AVAILABLE` (3,664 listing IDs) | `product_id`, `product_name` | `AUTHENTIC_DATA` | `SUPPORTED_SOURCE_B_ONLY` | Source B exclusive listing identifier. | `APPROVE` |
| `BR-004` / `IR-004` | Category text strings | `AVAILABLE` (29 categories) | `AVAILABLE` (5 categories) | `category_raw`, `canonical_category_family` | `AUTHENTIC_DATA` | `SUPPORTED` | Requires category harmonization mapping rules. | `APPROVE` |
| `BR-005` / `IR-005` | `shop_id`, `product_id`, `rating` | `NOT_AVAILABLE` | `AVAILABLE` (158 shop IDs) | `shop_id` | `AUTHENTIC_DATA` | `SUPPORTED_SOURCE_B_ONLY` | Evaluated strictly as Shop Review Intelligence. | `APPROVE` |
| `BR-006` / `IR-006` | Review text, aspect ground truth | `AVAILABLE` (text only) | `AVAILABLE` (text only) | `review_text_normalized_match` | `AUTHENTIC_TEXT_DERIVED` | `CONDITIONAL_PENDING_PHASE_9` | Supervised aspect ground truth requires Phase 9 annotation. | `APPROVE_CONDITIONALLY` |
| `BR-007` / `IR-007` | Rating, sentiment, issue severity | `AVAILABLE` (derived) | `AVAILABLE` (derived) | `priority_score` | `AUTHENTIC_DERIVED` | `SUPPORTED_VIA_MODEL` | Scoring formula parameters belong to Phase 10. | `APPROVE` |
| `BR-008` / `IR-008` | Prediction logits, gold labels | `AVAILABLE` | `AVAILABLE` | `y_true`, `y_pred` | `AUTHENTIC_DERIVED` | `SUPPORTED` | Numeric thresholds set to TBD in Phase 4. | `APPROVE` |
| `BR-009` / `IR-009` | Checksums, row numbers, key hashes | `AVAILABLE` | `AVAILABLE` | `source_record_key`, `sha256` | `AUTHENTIC_PIPELINE` | `SUPPORTED` | None. Lineage generator fully operational. | `APPROVE` |
| `BR-010` / `IR-010` | CS tickets, SLA tracking logs | `NOT_AVAILABLE` | `NOT_AVAILABLE` | `simulated_ticket_id`, `is_synthetic` | `SIMULATED_OPERATIONAL_ONLY` | `SUPPORTED_AS_SIMULATION_ONLY` | Strictly carries `is_synthetic = TRUE` flags. | `APPROVE_CONDITIONALLY` |
