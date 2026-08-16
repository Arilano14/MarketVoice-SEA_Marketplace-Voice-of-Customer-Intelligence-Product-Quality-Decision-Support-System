# MARKETVOICE SEA — PHASE 6 WAREHOUSE VALIDATION REPORT

**Report Version**: 1.0  
**Phase**: 6 — ETL & Data Warehouse  
**Deliverables**: DEL-08, DEL-09, DEL-10  
**Pipeline Version**: 6.0.1  
**Report Date**: 2026-08-16  
**Validation Environment**: `marketvoice_dev` (PostgreSQL 12.4, UTF8)  
**Test Environment**: `marketvoice_test` (PostgreSQL 12.4, UTF8)  

---

## 1. EXECUTIVE SUMMARY

| Criterion | Result |
|---|---|
| **DEL-08** Physical PostgreSQL Warehouse | **PASS** |
| **DEL-09** Reproducible Python/PostgreSQL ETL | **PASS** |
| **DEL-10** Automated Data Quality + Validation | **PASS** |
| CRITICAL_DQ_FAIL | **0** |
| MAJOR_INTEGRITY_BLOCKER | **0** |
| RAW_DATA_MUTATION | **0** |
| CROSS_SOURCE_LINKAGE | **0** |
| FAKE_REVIEW_TIMESTAMPS | **0** |
| SYNTHETIC_ROWS | **0** |
| UNEXPLAINED_WAREHOUSE_FIELDS | **0** |
| ETL_REPRODUCIBLE | **PASS** |
| FULL_REFRESH_IDEMPOTENT | **PASS** |
| TRANSACTION_ROLLBACK | **PASS** (3-TX model enforced) |
| FAILED_RUN_AUDIT_PERSISTS | **PASS** (TX-A survives TX-B rollback) |
| ROW_RECONCILIATION | **PASS** |
| TESTS | **19/19 PASS** |

```
PHASE_6_BUILD_STATUS        = COMPLETE
PHASE_6_VALIDATION_STATUS   = PASS
PHASE_6_HUMAN_REVIEW_STATUS = PENDING
PHASE_6_GATE_RECOMMENDATION = PASS
PHASE_6_GATE_STATUS         = AWAITING_HUMAN_APPROVAL
```

---

## 2. IMPLEMENTED TABLES (§24 — 9 PHYSICAL TABLES)

| # | Table | Category | Truncation Policy | DEV Row Count |
|---|---|---|---|---:|
| 1 | `pipeline_run` | Audit | NEVER (§13) | 1 |
| 2 | `rejected_record_log` | Audit | NEVER (§13) | 0 |
| 3 | `data_quality_result` | Audit | NEVER (§13) | 11 |
| 4 | `dim_source` | Conformed Master | NEVER (seed) | 2 |
| 5 | `dim_rating` | Conformed Master | NEVER (seed) | 5 |
| 6 | `dim_category` | Dynamic Analytical | TRUNCATE each TX-B | 34 |
| 7 | `dim_product` | Dynamic Analytical | TRUNCATE each TX-B | 3,664 |
| 8 | `dim_shop` | Dynamic Analytical | TRUNCATE each TX-B | 158 |
| 9 | `fact_review` | Central Fact | TRUNCATE each TX-B | 46,007 |

**Total tables**: 9 (verified via `information_schema.tables`)  
**Extra/forbidden objects**: 0 (no `mv_*` views, no `dim_date`, no Track B tables, no `099_future_phases_reserved.sql`)  

### Seed Verification

| Dimension | Expected | Actual | Status |
|---|---|---|---|
| `dim_source` | 2 (SRC_PRDECT_ID_V1, SRC_TOKOPEDIA_REVIEWS_2019) | 2 | ✅ |
| `dim_rating` | 5 (values 1–5, buckets Negative/Neutral/Positive) | 5 | ✅ |

---

## 3. POSTGRESQL VERSION & ENCODING (§21)

| Property | Expected | Actual | Status |
|---|---|---|---|
| PostgreSQL Version | ≥ 10 | 12.4 | ✅ |
| `server_encoding` | UTF8 | UTF8 | ✅ |
| Schema | `marketvoice_warehouse` | Present | ✅ |

---

## 4. SOURCE SHA256 PRE/POST ETL (§26)

| Source | Phase | SHA256 | Match |
|---|---|---|---|
| Source A (PRDECT-ID) | Pre-ETL | `1dfdde6bb169ad57aab4211ecf45a75a4111b774ab43932f6d39c349bfd92bde` | ✅ Manifest |
| Source A (PRDECT-ID) | Post-ETL | `1dfdde6bb169ad57aab4211ecf45a75a4111b774ab43932f6d39c349bfd92bde` | ✅ Unchanged |
| Source B (Tokopedia) | Pre-ETL | `dbffc29078db1894e60884c526fe4d0ccbc592f33fe95d2e5ac2d8f96336b7ed` | ✅ Manifest |
| Source B (Tokopedia) | Post-ETL | `dbffc29078db1894e60884c526fe4d0ccbc592f33fe95d2e5ac2d8f96336b7ed` | ✅ Unchanged |

**Raw data mutation**: NONE. `data/raw/` was never written to.

---

## 5. INPUT / ACCEPTED / REJECTED / LOADED COUNTS

| Metric | Source A | Source B | Total |
|---|---:|---:|---:|
| Manifest row count | 5,400 | 40,607 | 46,007 |
| Rows read | 5,400 | 40,607 | 46,007 |
| Accepted | 5,400 | 40,607 | 46,007 |
| Rejected (transform) | 0 | 0 | 0 |
| Rejected (FK lookup) | 0 | 0 | 0 |
| **Loaded to fact_review** | **5,400** | **40,607** | **46,007** |

### Reconciliation

```
manifest_total (46,007) == rows_read (46,007) == accepted (46,007) == loaded (46,007) ✅
Source A loaded (5,400) + Source B loaded (40,607) == fact_review total (46,007) ✅
Duplicate natural keys: 0 ✅
```

---

## 6. DIMENSION / FACT COUNTS

| Dimension | Count | Notes |
|---|---:|---|
| `dim_source` | 2 | Conformed master (never truncated) |
| `dim_rating` | 5 | Values 1–5, buckets Negative/Neutral/Positive |
| `dim_category` | 34 | 29 from Source A + 5 from Source B |
| `dim_product` | 3,664 | Source B only (§15: Source A has no product_id) |
| `dim_shop` | 158 | Source B only (§15: Source A has no shop_id) |
| `fact_review` | 46,007 | Central fact table |

---

## 7. PRE-COMMIT DATA QUALITY CHECKS (§12)

All 11 checks ran **BEFORE** COMMIT in TX-B:

| # | Check ID | Severity | Actual | Expected | Status |
|---|---|---|---|---|---|
| 1 | `DQ-PRE-SRC_A-PRODUCT-LINKAGE-ZERO` | CRITICAL | 0 | 0 | ✅ PASS |
| 2 | `DQ-PRE-SRC_A-SHOP-LINKAGE-ZERO` | CRITICAL | 0 | 0 | ✅ PASS |
| 3 | `DQ-PRE-SRC_B-SENTIMENT-LEAKAGE-ZERO` | CRITICAL | 0 | 0 | ✅ PASS |
| 4 | `DQ-PRE-SRC_B-EMOTION-LEAKAGE-ZERO` | CRITICAL | 0 | 0 | ✅ PASS |
| 5 | `DQ-PRE-SYNTHETIC-ZERO` | CRITICAL | 0 | 0 | ✅ PASS |
| 6 | `DQ-PRE-INVALID-RATING-ZERO` | CRITICAL | 0 | 0 | ✅ PASS |
| 7 | `DQ-PRE-FK-ORPHAN-CATEGORY` | CRITICAL | 0 | 0 | ✅ PASS |
| 8 | `DQ-PRE-FK-ORPHAN-PRODUCT` | CRITICAL | 0 | 0 | ✅ PASS |
| 9 | `DQ-PRE-FK-ORPHAN-SHOP` | CRITICAL | 0 | 0 | ✅ PASS |
| 10 | `DQ-PRE-DUPLICATE-NATURAL-KEY` | CRITICAL | 0 | 0 | ✅ PASS |
| 11 | `DQ-PRE-SOURCE-RECONCILIATION` | CRITICAL | A=5400+B=40607=46007 | sum==total | ✅ PASS |

---

## 8. POST-LOAD FORENSIC CHECKS (§32)

12 forensic checks ran **AFTER** commit (verification only — cannot rollback):

| # | Check ID | Severity | Actual | Expected | Status |
|---|---|---|---|---|---|
| 1 | `DQ-POST-FACT-COUNT-POSITIVE` | CRITICAL | 46007 | >0 | ✅ PASS |
| 2 | `DQ-POST-DIM-SOURCE-COUNT` | CRITICAL | 2 | 2 | ✅ PASS |
| 3 | `DQ-POST-DIM-RATING-COUNT` | CRITICAL | 5 | 5 | ✅ PASS |
| 4 | `DQ-POST-CROSS-SOURCE-ISOLATION` | CRITICAL | 0 | 0 | ✅ PASS |
| 5 | `DQ-POST-SYNTHETIC-ZERO` | CRITICAL | 0 | 0 | ✅ PASS |
| 6 | `DQ-POST-TIMESTAMP-ORDERING` | CRITICAL | 0 | 0 | ✅ PASS |
| 7 | `DQ-POST-SRC-B-PRODUCT-NONNULL` | CRITICAL | 0 | 0 | ✅ PASS |
| 8 | `DQ-POST-SRC-B-SHOP-NONNULL` | CRITICAL | 0 | 0 | ✅ PASS |
| 9 | `DQ-POST-SRC-B-SENTIMENT-LEAKAGE` | CRITICAL | 0 | 0 | ✅ PASS |
| 10 | `DQ-POST-SRC-B-EMOTION-LEAKAGE` | CRITICAL | 0 | 0 | ✅ PASS |
| 11 | `DQ-POST-RATING-DISTRIBUTION` | INFO | {1:2375, 2:943, 3:2287, 4:7941, 5:32461} | valid | ✅ PASS |
| 12 | `DQ-POST-PIPELINE-RUN-FINALIZED` | CRITICAL | status=SUCCESS | finalized | ✅ PASS |

---

## 9. TRANSACTION MODEL VERIFICATION (§11)

| Transaction | Purpose | Behavior | Status |
|---|---|---|---|
| **TX-A** | Insert `pipeline_run` STARTED | Commits independently; survives TX-B rollback | ✅ |
| **TX-B** | Full warehouse refresh (truncate dynamic → load dims → load facts → pre-commit checks) | Single atomic transaction; ROLLBACK on any CRITICAL check failure | ✅ |
| **TX-C** | Finalize `pipeline_run` SUCCESS/FAILED | Commits independently after TX-B result | ✅ |

- `pipeline_run`, `rejected_record_log`, `data_quality_result` are **never truncated** (§13).
- TX-A uses `autocommit=True` → survives TX-B rollback.
- TX-B uses `autocommit=False` → atomic warehouse refresh.
- Pre-commit checks run **inside** TX-B **before** COMMIT (§12).
- Post-load forensic checks run **after** TX-B COMMIT and **cannot rollback**.

---

## 10. IDEMPOTENCY TEST (§17)

```
IDEMPOTENCY_STRATEGY = TRANSACTIONAL_DETERMINISTIC_FULL_REFRESH
```

Two consecutive pipeline runs produced:

| Metric | Run 1 | Run 2 | Match |
|---|---|---|---|
| fact_review count | 46,007 | 46,007 | ✅ |
| dim_category count | 34 | 34 | ✅ |
| dim_product count | 3,664 | 3,664 | ✅ |
| dim_shop count | 158 | 158 | ✅ |
| Duplicate natural keys | 0 | 0 | ✅ |

**Note**: SERIAL/surrogate key values are NOT required to be identical across runs (§17).

---

## 11. CROSS-SOURCE ISOLATION (§6)

| Check | Expected | Actual | Status |
|---|---|---|---|
| Source A `product_sk` = NULL for all rows | 0 non-NULL | 0 | ✅ |
| Source A `shop_sk` = NULL for all rows | 0 non-NULL | 0 | ✅ |
| Source B `source_gold_sentiment_label` = NULL | 0 non-NULL | 0 | ✅ |
| Source B `source_gold_emotion_label` = NULL | 0 non-NULL | 0 | ✅ |
| Source B `product_sk` resolves (non-NULL) | 0 NULL | 0 | ✅ |
| Source B `shop_sk` resolves (non-NULL) | 0 NULL | 0 | ✅ |
| `is_synthetic` = FALSE for all rows | 0 TRUE | 0 | ✅ |
| Cross-source product/shop linkage | FORBIDDEN | 0 | ✅ |

---

## 12. TIMESTAMP BOUNDARY (§6)

Only **TECHNICAL_METADATA** timestamps are used:

| Timestamp | Classification | Value |
|---|---|---|
| `ingested_at` | SYSTEM_GENERATED | Pipeline extraction time |
| `processed_at` | SYSTEM_GENERATED | Pipeline transform time |
| `loaded_at` | SYSTEM_GENERATED | PostgreSQL load time |
| `pipeline_started_at` | SYSTEM_GENERATED | Via `pipeline_run.started_at` |
| `pipeline_completed_at` | SYSTEM_GENERATED | Via `pipeline_run.completed_at` |

**No review/event timestamps exist.** Neither raw source contains review dates.

---

## 13. RATING DISTRIBUTION

| Rating | Count | Percentage | Bucket |
|---|---:|---|---|
| 1 (Very Negative) | 2,375 | 5.16% | Negative |
| 2 (Negative) | 943 | 2.05% | Negative |
| 3 (Neutral) | 2,287 | 4.97% | Neutral |
| 4 (Positive) | 7,941 | 17.26% | Positive |
| 5 (Very Positive) | 32,461 | 70.56% | Positive |
| **Total** | **46,007** | **100%** | |

---

## 14. AUTOMATED TEST RESULTS (§31)

```
python -m compileall -q src scripts tests    → EXIT 0  ✅
python -m unittest tests.phase06.test_phase06 -v → 19/19 PASS  ✅
```

### Test Breakdown

| Test Class | Tests | Status |
|---|---|---|
| `TestExtract` (§21/§26) | 5 | ✅ All PASS |
| `TestTransform` (§6/§9/§16/§19/§20) | 6 | ✅ All PASS |
| `TestDatabaseSchema` (§22/§24) | 5 | ✅ All PASS |
| `TestFullPipeline` (§11/§12/§17/§32) | 3 | ✅ All PASS |
| **Total** | **19** | **✅ ALL PASS** |

---

## 15. GIT / DATA SAFETY (§26)

| Check | Status |
|---|---|
| `data/raw/` never written to | ✅ |
| SHA256 pre-ETL matches manifest | ✅ |
| SHA256 post-ETL matches pre-ETL | ✅ |
| No files force-added to git | ✅ |
| `REMOTE_GIT_WRITE` | NONE (user-controlled only) |
| `.pipdeps/` in `.gitignore` | ✅ |

---

## 16. CODE TREE

```
sql/warehouse/
  001_schema.sql          — CREATE SCHEMA marketvoice_warehouse
  002_tables.sql          — 9 physical tables (PK inline)
  003_constraints.sql     — FK/CHECK/UNIQUE + seed dim_source (2) + dim_rating (5)
  004_indexes.sql         — FK indexes + composite indexes

src/marketvoice/
  database/
    __init__.py
    connection.py         — §22 safety guard, §21 UTF8 verify, DBSettings
    schema.py             — DDL apply, 9-table verify, seed verify
  etl/
    __init__.py
    extract.py            — §21 strict UTF-8 CSV, §26 SHA256 verify
    transform.py          — §16 row hash, §19 FK rules, §20 product variant
    load.py               — §11 3-TX model, §12 pre-commit checks, §13 audit
    pipeline.py           — Orchestrator (extract→transform→3TX→verify)
  quality/
    __init__.py
    checks.py             — Post-load forensic verification (§32)

tests/phase06/
    __init__.py
    test_phase06.py       — 19 tests (extract, transform, schema, pipeline)
```

---

## 17. DELIVERABLE COMPLIANCE MATRIX

| Deliverable | Description | Evidence | Status |
|---|---|---|---|
| **DEL-08** | Physical PostgreSQL Warehouse | 9 tables, constraints, indexes, seeds — verified on `marketvoice_dev` and `marketvoice_test` | **PASS** |
| **DEL-09** | Reproducible Python/PostgreSQL ETL | Full pipeline: extract→transform→3-TX load, idempotent full refresh, 46,007 rows loaded | **PASS** |
| **DEL-10** | Automated Data Quality + Validation | 11 pre-commit checks + 12 post-load checks, all PASS; 19 unit/integration tests all PASS | **PASS** |

---

## 18. REMAINING LIMITATIONS

1. **No real review timestamps** — Neither source provides review dates. `ingested_at`, `processed_at`, `loaded_at` are technical metadata only (§6).
2. **Source A lacks product_id and shop_id** — All Source A `fact_review` rows have `product_sk = NULL` and `shop_sk = NULL` (§15/§19). Product/shop BI is Source B only.
3. **Source B lacks gold sentiment/emotion labels** — All Source B `fact_review` rows have `source_gold_sentiment_label = NULL` and `source_gold_emotion_label = NULL` (§6).
4. **Cross-source linkage not supported** — No entity reconciliation between sources (§6).
5. **Track B (synthetic data) not authorized** — `is_synthetic = FALSE` enforced for all rows (§9).
6. **Business BI marts deferred to Phase 7** — No `mv_*` summary views created (§7 DEL-08 vs DEL-11 governance clarification).
7. **PostgreSQL 12.4** — Older version (from Odoo bundled install); functional for Phase 6 but lacks newer PG features.

---

## 19. MANDATORY PLAN REVISIONS APPLIED

| Rev | Mandate | Status |
|---|---|---|
| R-01 | §7 DEL-08 vs DEL-11 governance clarification — no business marts in Phase 6 | ✅ Applied |
| R-02 | §8 In-memory Python staging — no DB staging tables | ✅ Applied |
| R-03 | §9 Track B removed — is_synthetic enforcement | ✅ Applied |
| R-04 | §10 No `099_future_phases_reserved.sql` | ✅ Applied |
| R-05 | §11 3-transaction model — pipeline_run survives rollback | ✅ Applied |
| R-06 | §12 Pre-commit checks BEFORE COMMIT | ✅ Applied |
| R-07 | §13 Audit tables never truncated | ✅ Applied |
| R-08 | §14 source_sk resolved by source_id lookup, never hardcoded | ✅ Applied |
| R-09 | §15 No fake unknown members — NULL FKs for Source A | ✅ Applied |
| R-10 | §16 Deterministic row hash (source_id\|sha256\|row_number) | ✅ Applied |
| R-11 | §17 Idempotency via TRANSACTIONAL_DETERMINISTIC_FULL_REFRESH | ✅ Applied |
| R-12 | §18 Semantic DQ severity — no arbitrary thresholds | ✅ Applied |
| R-13 | §19 Source B FK must resolve; Source A FK must be NULL | ✅ Applied |
| R-14 | §20 Product name variant rule (most frequent, tie→lowest row) | ✅ Applied |
| R-15 | §21 Strict UTF-8 decode (no errors='replace') | ✅ Applied |
| R-16 | §22 Test DB safety guard (ENV=test + current_database()) | ✅ Applied |
| R-17 | §23 Minimal dependencies (psycopg[binary] only) | ✅ Applied |
| R-18 | §25 data_quality_result grain: pipeline_run_id × dq_check_id | ✅ Applied |
| R-19 | §26 SHA256 pre/post ETL raw data integrity | ✅ Applied |
| R-20 | §28 Source-to-target mapping — UNEXPLAINED_WAREHOUSE_FIELDS=0 | ✅ Applied |

---

## 20. PHASE 6 GATE RECOMMENDATION

```
PHASE_6_BUILD_STATUS        = COMPLETE
PHASE_6_VALIDATION_STATUS   = PASS
PHASE_6_HUMAN_REVIEW_STATUS = PENDING
PHASE_6_GATE_RECOMMENDATION = PASS
PHASE_6_GATE_STATUS         = AWAITING_HUMAN_APPROVAL

PHASE_7_EXECUTION_STATUS    = NOT_STARTED
REMOTE_GIT_WRITE            = NONE
```

> [!IMPORTANT]
> Phase 6 technical execution is complete. All deliverables (DEL-08, DEL-09, DEL-10)
> are validated with empirical evidence. Human review and gate approval is required
> before Phase 7 may begin.
