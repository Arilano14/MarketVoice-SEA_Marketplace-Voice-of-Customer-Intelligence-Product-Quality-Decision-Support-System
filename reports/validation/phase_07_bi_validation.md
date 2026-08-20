# MARKETVOICE SEA — PHASE 7 BI VALIDATION REPORT

**Report Version**: 1.0  
**Phase**: 7 — Baseline Business Intelligence & Voice-of-Customer Analytics  
**Deliverable**: DEL-11 (Baseline Business Intelligence Queries)  
**Report Date**: 2026-08-20  
**Validation Target**: `marketvoice_dev` & `marketvoice_test` (PostgreSQL 12.4, UTF8)  

---

## 1. EXECUTIVE SUMMARY

| Metric / Criterion | Expected | Actual | Status |
|---|---|---|---|
| Predecessor Phase Gates (Phases 0–6) | ALL PASS | ALL PASS | ✅ PASS |
| Physical Database Schema | 9 tables exactly | 9 tables exactly | ✅ PASS |
| DEL-11 Mart Views Created | 6 views | 6 views | ✅ PASS |
| Test Suite Execution | 100% pass | 31 / 31 tests PASS | ✅ PASS |
| Review Count Reconciliation | 46,007 total | 46,007 total (Diff = 0) | ✅ PASS |
| Source A Review Reconciliation | 5,400 rows | 5,400 rows (Diff = 0) | ✅ PASS |
| Source B Review Reconciliation | 40,607 rows | 40,607 rows (Diff = 0) | ✅ PASS |
| Cross-Source Isolation | 0 cross-linkage | 0 cross-linkage | ✅ PASS |
| Synthetic Review Contamination | 0 rows | 0 rows (`is_synthetic = FALSE`) | ✅ PASS |
| Customer Review Timestamps | NOT_AVAILABLE | Excluded from analytical marts | ✅ PASS |
| DDL Formal Limitation Clauses | Present in all 6 | 6 / 6 verified in SQL DDL | ✅ PASS |
| Remote Git Operations | FORBIDDEN | 0 remote operations executed | ✅ PASS |

```
PHASE_7_BUILD_STATUS        = COMPLETE
PHASE_7_VALIDATION_STATUS   = PASS
PHASE_7_HUMAN_REVIEW_STATUS = PENDING
PHASE_7_GATE_RECOMMENDATION = PASS
PHASE_7_GATE_STATUS         = AWAITING_HUMAN_APPROVAL
```

---

## 2. DEL-11 MART VIEWS REGISTER (§24)

All 6 views are implemented as standard PostgreSQL views in schema `marketvoice_warehouse`:

| View Name | Grain | Scope & Requirements | Target Source | Output Rows |
|---|---|---|---|---:|
| `mv_source_summary` | One row per registered source | FR-003, UC-001, Contract 1 | All (A + B) | 2 |
| `mv_category_summary` | One row per source and category | FR-003, UC-001, Contract 1 | All (A + B) | 34 |
| `mv_product_summary` | One row per verified product listing | FR-005, UC-002, Contract 2 | Source B only | 3,664 |
| `mv_shop_summary` | One row per verified shop | FR-006, UC-003, Contract 3 | Source B only | 158 |
| `mv_source_a_label_breakdown` | One row per sentiment × emotion pair | FR-004 prep, Contract 4 | Source A only | 5 |
| `mv_pipeline_health` | One row per pipeline execution run | NFR-003, UC-007, Audit | Operational | 1+ |

---

## 3. FORMAL KPI SPECIFICATION & RECONCILIATION (§11, §17)

### 3.1 KPI Inventory & Calculation Results

| KPI ID | KPI Name | Mathematical / SQL Formula | Source A Value | Source B Value | Warehouse Total |
|---|---|---|---|---|---|
| **KPI-001** | Total Review Count | `COUNT(review_sk)` | 5,400 | 40,607 | **46,007** |
| **KPI-002** | Average Rating | `ROUND(AVG(rating_value)::numeric, 2)` | 3.09 | 4.64 | **4.46** |
| **KPI-003** | Rating Histogram | `COUNT(*) FILTER (WHERE rating_value = N)` | [1:1832, 2:561, 3:462, 4:395, 5:2150] | [1:543, 2:382, 3:1825, 4:7546, 5:30311] | [1:2375, 2:943, 3:2287, 4:7941, 5:32461] |
| **KPI-004** | Negative Review Rate (≤ 2 Stars) | `(COUNT(rating <= 2) / COUNT(*)) * 100` | 44.31% | 2.28% | **7.21%** |
| **KPI-005** | Positive Review Rate (≥ 4 Stars) | `(COUNT(rating >= 4) / COUNT(*)) * 100` | 47.13% | 93.23% | **87.82%** |
| **KPI-006** | Neutral Review Rate (= 3 Stars) | `(COUNT(rating = 3) / COUNT(*)) * 100` | 8.56% | 4.49% | **4.97%** |
| **KPI-007** | Average Review Text Length | `ROUND(AVG(review_text_len_chars)::numeric, 0)` | 104 chars | 55 chars | **61 chars** |
| **KPI-008** | Distinct Category Count | `COUNT(DISTINCT category_sk)` | 29 | 5 | **34** |
| **KPI-009** | Distinct Product Count | `COUNT(DISTINCT product_sk)` | N/A (0) | 3,664 | **3,664** |
| **KPI-010** | Distinct Shop Count | `COUNT(DISTINCT shop_sk)` | N/A (0) | 158 | **158** |

### 3.2 Exact Reconciliation Audit

| Mart View | Aggregation Column | Mart View Sum | Direct Fact Table Query | Discrepancy | Status |
|---|---|---|---|---|---|
| `mv_source_summary` | `review_count` | 46,007 | 46,007 | 0 | ✅ PASS |
| `mv_category_summary` | `review_count` | 46,007 | 46,007 | 0 | ✅ PASS |
| `mv_product_summary` | `review_count` | 40,607 (Source B) | 40,607 (Source B) | 0 | ✅ PASS |
| `mv_shop_summary` | `review_count` | 40,607 (Source B) | 40,607 (Source B) | 0 | ✅ PASS |
| `mv_source_a_label_breakdown` | `review_count` | 5,400 (Source A) | 5,400 (Source A) | 0 | ✅ PASS |

---

## 4. DESCRIPTIVE BI FINDINGS & DOMAIN EVIDENCE

### 4.1 Executive Overview Insights (`mv_source_summary`)
* **Source A (PRDECT-ID)** exhibits a balanced, bimodal rating distribution (Average: 3.09) with a 44.31% negative rate and 47.13% positive rate across 29 diverse e-commerce categories. Average review length is significantly longer (104 characters).
* **Source B (Tokopedia 2019)** reflects typical organic marketplace customer satisfaction distribution (Average: 4.64) heavily skewed toward positive reviews (93.23% positive rate, 70.56% 5-star reviews) across 5 core categories. Average review text is concise (55 characters).

### 4.2 Category Insights (`mv_category_summary`)
* **Source B High Review Concentration Categories**:
  1. `elektronik`: 15,897 reviews (39.15% of Source B), Avg Rating: 4.76, Neg Rate: 1.18%
  2. `fashion`: 8,910 reviews (21.94% of Source B), Avg Rating: 4.67, Neg Rate: 2.17%
  3. `olahraga`: 7,838 reviews (19.30% of Source B), Avg Rating: 4.58, Neg Rate: 1.21%
  4. `handphone`: 6,136 reviews (15.11% of Source B), Avg Rating: 4.38, Neg Rate: 6.93% (Highest low-rating rate in Source B)
  5. `pertukangan`: 1,826 reviews (4.50% of Source B), Avg Rating: 4.64, Neg Rate: 1.31%
* **Source A High Negative Rate Categories**: `Office & Stationery` (60.0% Neg), `Automotive` (59.5% Neg), `Computers & Laptops` (59.0% Neg), `Carpentry` (58.5% Neg).

### 4.3 Product Intelligence Insights (`mv_product_summary`)
* Exactly **3,664 distinct products** identified in Source B.
* Top review volume product: `PID 159398204` (*TINTA / CATRIDGE HP 680 BLACK / COLOR ORIGINAL 100%*) with 1,312 reviews, average rating 4.87, low-rating rate 0.15%.
* Product-level name variations were resolved deterministically in Phase 6 with `product_name_variant_count >= 1`.

### 4.4 Shop Indicators (`mv_shop_summary`)
* Exactly **158 distinct shops** identified in Source B.
* Top shop by volume: `Shop ID 2048686` with 8,832 reviews across 252 products, average rating 4.74, low-rating rate 1.53%.
* Note: All shop metrics represent review experience feedback only; no seller performance or enforcement claim is made.

### 4.5 Source A Benchmark Labels (`mv_source_a_label_breakdown`)
* **Sentiment**: Negative: 2,821 reviews (52.24%), Positive: 2,579 reviews (47.76%).
* **Emotion Breakdown**:
  * Positive - Happy: 1,770 reviews (32.78%, Avg Rating: 4.74)
  * Negative - Sadness: 1,202 reviews (22.26%, Avg Rating: 1.67)
  * Negative - Fear: 920 reviews (17.04%, Avg Rating: 1.51)
  * Positive - Love: 809 reviews (14.98%, Avg Rating: 4.96)
  * Negative - Anger: 699 reviews (12.94%, Avg Rating: 1.26)

---

## 5. AUTOMATED TEST SUITE EXECUTION (§25)

The test suite was executed across the entire repository:

```text
python -m unittest discover -s tests -v
----------------------------------------------------------------------
Ran 31 tests in 140.094s

OK
```

### Breakdown of Test Results:
* **Phase 6 Regression Tests (19 tests)**: All 19 tests PASS (Extract UTF-8/SHA256, Transform hashing/isolation, DDL constraints, 3-transaction warehouse refresh, idempotency, post-load forensic).
* **Phase 7 Mart Tests (9 tests)**: All 9 tests PASS (`test_all_6_views_exist`, `test_mv_source_summary_rows_and_reconciliation`, `test_mv_category_summary_reconciliation`, `test_mv_product_summary_source_b_only`, `test_mv_shop_summary_source_b_only`, `test_mv_source_a_label_breakdown`, `test_mv_pipeline_health`, `test_no_temporal_columns_in_marts`, `test_limitation_clauses_in_ddl`).
* **Environment Smoke Tests (3 tests)**: All 3 tests PASS.

---

## 6. SCOPE BOUNDARY COMPLIANCE (§7)

| Boundary / Guardrail | Compliance Evidence | Status |
|---|---|---|
| No ML / Sentiment prediction | No predictive models implemented (deferred to Phase 8) | ✅ PASS |
| No Aspect / Issue classifier | No issue taxonomy created (deferred to Phase 9) | ✅ PASS |
| No Priority / Decision scoring | No priority formula or queue (deferred to Phase 10) | ✅ PASS |
| No FastAPI / REST microservice | No REST API created (deferred to Phase 11) | ✅ PASS |
| No n8n Automation | No webhook workflows created (deferred to Phase 11) | ✅ PASS |
| No Power BI files / visuals | No `.pbix` / `.pbit` files created (deferred to Phase 12) | ✅ PASS |
| No Fake Review Timestamps | No temporal trend columns exposed in marts | ✅ PASS |
| No Cross-Source Linkage | Source A and Source B kept strictly isolated | ✅ PASS |
| No Synthetic Track B Data | `is_synthetic = FALSE` enforced on all mart queries | ✅ PASS |
| No ETL / Schema Mutation | Phase 6 tables, DDL, and pipeline unchanged | ✅ PASS |

---

## 7. ARTIFACTS & DELIVERABLE LOCATIONS

| Deliverable | Path | Description |
|---|---|---|
| **DEL-11** Mart DDL | `sql/marts/005_mart_views.sql` | 6 SQL Views with limitation clauses |
| Phase 7 Test Suite | `tests/phase07/test_phase07.py` | Automated unit/integration test suite |
| Phase 7 Test Init | `tests/phase07/__init__.py` | Test package initialization |
| Phase 7 Plan | `docs/plans/phase_07_implementation_plan.md` | Formal implementation plan |
| Phase 7 Validation Report | `reports/validation/phase_07_bi_validation.md` | This document |

---

## 8. PHASE 7 GATE RECOMMENDATION

```
PHASE_7_BUILD_STATUS        = COMPLETE
PHASE_7_VALIDATION_STATUS   = PASS
PHASE_7_HUMAN_REVIEW_STATUS = PENDING
PHASE_7_GATE_RECOMMENDATION = PASS
PHASE_7_GATE_STATUS         = AWAITING_HUMAN_APPROVAL

PHASE_8_EXECUTION_STATUS    = NOT_STARTED
REMOTE_GIT_WRITE            = FORBIDDEN
```

> [!IMPORTANT]
> Phase 7 technical execution for DEL-11 (Baseline Business Intelligence Queries) is complete and verified with 0 discrepancies. Human gate review and sign-off is required before Phase 8 (Rating/Sentiment ML) may be planned or executed.
