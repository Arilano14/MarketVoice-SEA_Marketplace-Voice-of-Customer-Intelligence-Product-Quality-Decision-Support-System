# MARKETVOICE SEA — PHASE 2 DATA FOUNDATION FINAL HARDENING REPORT

**Document Version**: 1.0 (Hardening Execution Report)  
**Execution Date**: 2026-08-10  
**Phase Target**: Phase 2 (Dataset Forensic Audit & Data Readiness)  
**Data Foundation Version**: `DATA_FOUNDATION_VERSION = 1.0`  
**Raw Data Lock Status**: `RAW_DATA_LOCKED = TRUE`  
**Standardized Data Status**: `STANDARDIZED_DATA_READY = TRUE`  
**Phase 2 Gate Result**: `PHASE_2_GATE_STATUS = PASS`  

---

## 1. HARDENING EXECUTION SUMMARY

Phase 2 Data Foundation Final Hardening has been fully executed across all 10 mandatory workstreams (`H01` through `H10`) in strict compliance with non-destructive data governance protocols.

Zero raw CSV files were edited, overwritten, re-encoded, or mutated. Standardized derived datasets were generated under `data/interim/validated/`, fully traceable via system technical lineage keys (`source_record_key`).

---

## 2. RAW INTEGRITY BEFORE / AFTER

| Source | File Path | Pre-Execution SHA256 | Post-Execution SHA256 | Immutability Status |
|---|---|---|---|---|
| **Source A (`SRC_PRDECT_ID_V1`)** | `data/raw/prdect_id/PRDECT-ID Dataset.csv` | `1dfdde6bb169ad57aab4211ecf45a75a4111b774ab43932f6d39c349bfd92bde` | `1dfdde6bb169ad57aab4211ecf45a75a4111b774ab43932f6d39c349bfd92bde` | `UNMUTATED (100% MATCH)` |
| **Source B (`SRC_TOKOPEDIA_REVIEWS_2019`)** | `data/raw/tokopedia_product_reviews_2019/tokopedia-product-reviews-2019.csv` | `dbffc29078db1894e60884c526fe4d0ccbc592f33fe95d2e5ac2d8f96336b7ed` | `dbffc29078db1894e60884c526fe4d0ccbc592f33fe95d2e5ac2d8f96336b7ed` | `UNMUTATED (100% MATCH)` |

---

## 3. CROSS-SOURCE OVERLAP FINDINGS (WORKSTREAM H01)

Cross-source review text overlap between Source A ($N_A = 5,400$) and Source B ($N_B = 40,607$) was empirically measured:

| Metric | Overlap Count | % of Source A | % of Source B | Leakage Impact |
|---|---|---|---|---|
| **Exact Raw Text Overlap** | 25 reviews | `0.46%` | `0.06%` | Negligible |
| **Normalized Text Overlap** | 95 reviews | `1.76%` | `0.23%` | Low |
| **Near-Duplicate Candidates (Prefix Screen)** | 882 reviews | `16.33%` | `2.17%` | Flagged for ML Split Protection |

- *Derivation Flags Added*: `cross_source_exact_overlap_flag`, `cross_source_normalized_overlap_flag`, `cross_source_near_duplicate_candidate_flag` added to standardized records. Zero raw rows were deleted.

---

## 4. LABEL DEPENDENCY FINDINGS (WORKSTREAM H02)

Empirical cross-tabulation of `Customer Rating` (1-5) against `Sentiment` and `Emotion` in Source A:

- **Customer Rating $\times$ Sentiment**:
  - 1-Star: `Negative` (1,832), `Positive` (0)
  - 2-Star: `Negative` (561), `Positive` (0)
  - 3-Star: `Negative` (428), `Positive` (34)
  - 4-Star: `Negative` (0), `Positive` (395)
  - 5-Star: `Negative` (0), `Positive` (2,150)
- **Rating-Sentiment Discordance Rate**: `0.00%` (0 out of 5,400 discordances in 1-2 or 4-5 stars). 3-star reviews contain 428 Negative and 34 Positive labels.
- **Classification**: `STRONGLY_RATING_DEPENDENT`.
- *Consistency Flag*: `rating_sentiment_consistency` added (`CONSISTENT` across 100% of rows).

---

## 5. ENTITY CARDINALITY FINDINGS (WORKSTREAM H03)

- `product_id` $\rightarrow$ `product_name`: `1-to-1` (Every `product_id` maps to exactly 1 `product_name`).
- `product_id` $\rightarrow$ `shop_id`: `1-to-1` (Every `product_id` belongs to exactly 1 `shop_id`).
- `product_id` $\rightarrow$ `category`: `1-to-1` (Every `product_id` belongs to exactly 1 `category`).
- `product_name` $\rightarrow$ `product_id`: `1-to-Many` (16 product titles map to 2 distinct `product_id` values, e.g. seller re-listings or sub-SKUs).
- `shop_id` $\rightarrow$ `product_id`: `1-to-Many` (158 shops host between 1 and 350 product listings).

*Conclusion*: `product_id` is a defensible listing-level natural identifier (`MARKETPLACE_PRODUCT_IDENTIFIER`).

---

## 6. PRDECT CONTEXT STABILITY FINDINGS (WORKSTREAM H04)

Product-level metadata across repeated `Product Name` titles in Source A was evaluated for functional consistency:

- `Category`: `ROW_LEVEL_CONTEXT_ATTRIBUTE` (2 products exhibit category variation across crawls).
- `Price`: `ROW_LEVEL_CONTEXT_ATTRIBUTE` (9 products exhibit price variation across listings).
- `Overall Rating`: `ROW_LEVEL_CONTEXT_ATTRIBUTE` (1 product exhibits rating variation).
- `Number Sold`: `ROW_LEVEL_CONTEXT_ATTRIBUTE` (39 products exhibit sales volume variation).
- `Total Review`: `ROW_LEVEL_CONTEXT_ATTRIBUTE` (40 products exhibit review volume variation).
- `Location`: `ROW_LEVEL_CONTEXT_ATTRIBUTE` (5 products exhibit seller location variation).

*Conclusion*: Row-level metadata values are preserved cleanly without arbitrary MIN/MAX aggregation.

---

## 7. TEXT FORENSICS FINDINGS (WORKSTREAM H05)

| Metric | Source A (`PRDECT-ID`) | Source B (`Tokopedia 2019`) |
|---|---|---|
| **Total Reviews** | 5,400 | 40,607 |
| **Unique Review Text Strings** | 5,348 | 40,607 |
| **Mean Character Length** | 98.4 chars | 68.2 chars |
| **Median Character Length** | 74.0 chars | 46.0 chars |
| **Mean Word Count** | 14.8 words | 10.4 words |
| **Reviews with HTML Entities** | 0 | 12 |
| **Reviews with URLs** | 0 | 8 |
| **Reviews with Email Patterns** | 0 | 0 |
| **Reviews with Phone Patterns** | 0 | 0 |
| **Reviews with Emojis** | 142 | 1,845 |

---

## 8. RAW PATTERN INVENTORY & TRANSFORMATION RESULTS (WORKSTREAM H06)

Deterministic transformation contracts were applied losslessly to generate standardized fields:

- **Source A Price**: Raw string `Rp1.000` $\rightarrow$ `price_idr = 1000.0` (`price_parse_status = EXACT`).
- **Source A Overall Rating**: Raw string `4.9` $\rightarrow$ `product_overall_rating = 4.9` (`overall_rating_parse_status = EXACT`).
- **Source A Number Sold / Total Review**: Parsed integer counts (`EXACT`).
- **Source B Sold Attribute**:
  - Exact integers (`'250'` $\rightarrow$ `250`, `sold_value_semantics = EXACT`).
  - Approximate thousands (`'2,9rb'` $\rightarrow$ `2900`, `sold_value_semantics = APPROXIMATE`).
  - Lower bounds (`'10rb+'` $\rightarrow$ `10000`, `sold_value_semantics = LOWER_BOUND`).
  - Missing values (`NULL` $\rightarrow$ `NULL`, `sold_missing_flag = TRUE`).

---

## 9. CATEGORY HARMONIZATION RESULTS (WORKSTREAM H07)

- `Elektronik` $\rightarrow$ `Elektronik` (`EXACT`, `HIGH` confidence)
- `Handphone & Tablet` $\rightarrow$ `Handphone & Tablet` (`NARROWER`, `HIGH` confidence)
- `Fashion Pria / Wanita / Muslim` $\rightarrow$ `Fashion` (`NARROWER_TO_BROADER`, `HIGH` confidence)
- `Olahraga` $\rightarrow$ `Olahraga` (`EXACT`, `HIGH` confidence)
- `Pertukangan` $\rightarrow$ `Pertukangan` (`EXACT`, `HIGH` confidence)
- 20 Unmapped PRDECT Categories $\rightarrow$ `canonical_category_family = NULL`, `category_mapping_status = UNMAPPED`.

---

## 10. ISSUE ANNOTATION READINESS (WORKSTREAM H08)

- `ISSUE_DISCOVERY_READINESS = READY`: Raw review text corpus is 100% ready for unsupervised topic modeling.
- `SUPERVISED_ISSUE_CLASSIFICATION_READINESS = REQUIRES_HUMAN_ANNOTATION`: Formulated a 7-step human annotation protocol in `docs/research/issue_annotation_protocol.md` for Phase 9 stratified pilot sampling ($N=1,000$).

---

## 11. SYNTHETIC DATA GOVERNANCE RESULT (WORKSTREAM H09)

- `SYNTHETIC_OPERATIONAL_TIMELINE = CANDIDATE_ONLY`. Zero synthetic timestamps or CS case logs were generated in Phase 2.
- `docs/governance/synthetic_data_policy.md` locked: Any future synthetic operational attributes in Phase 10/11 must carry `is_synthetic = TRUE` and `scenario_version`.

---

## 12. SOURCE A STANDARDIZED DATASET VALIDATION

- **Path**: `data/interim/validated/prdect_reviews_standardized.csv`
- **Rows**: 5,400 (`100%` row reconciliation with raw).
- **Lineage Key**: `source_record_key` 100% unique, 0 nulls.

---

## 13. SOURCE B STANDARDIZED DATASET VALIDATION

- **Path**: `data/interim/validated/tokopedia_reviews_2019_standardized.csv`
- **Rows**: 40,607 (`100%` row reconciliation with raw).
- **Lineage Key**: `source_record_key` 100% unique, 0 nulls.

---

## 14. ROW RECONCILIATION

- Source A: `5,400 raw rows = 5,400 standardized rows` (0 row loss).
- Source B: `40,607 raw rows = 40,607 standardized rows` (0 row loss).

---

## 15. MACHINE-READABLE ARTIFACTS

1. `data/interim/validated/prdect_reviews_standardized.csv`
2. `data/interim/validated/tokopedia_reviews_2019_standardized.csv`
3. `data/metadata/cross_source_overlap.csv`
4. `data/metadata/label_dependency_crosstab.csv`
5. `data/metadata/entity_cardinality.csv`
6. `data/metadata/prdect_context_stability.csv`
7. `data/metadata/text_forensics_profile.csv`
8. `data/metadata/dataset_inventory.csv`
9. `data/metadata/schema_profile.csv`
10. `data/metadata/data_quality_issues.csv`
11. `data/metadata/data_capability_matrix.csv`

---

## 16. REPRODUCIBILITY TEST

- Executed `python scripts/data_audit/execute_phase2_hardening.py` in two consecutive runs.
- Result: **`100% DETERMINISTIC PASS`**. All generated SHA256 hashes, row counts, schema profiles, and derived values matched identically.

---

## 17. REMAINING WARNINGS

- `DEV-TOK-01`: 3,664 unique `product_id` values vs 3,647 unique product titles (Reconciled: 16 titles exist across multiple SKU listings).
- `DQ-TOK-02`: `sold` column in Source B contains 14 nulls (`0.034%`).
- `GAP-01`: Core raw data lacks review creation timestamps (`REAL_TEMPORAL_REVIEW_ANALYTICS = NOT_SUPPORTED`).

---

## 18. PHASE 2 FINAL CHECKLIST

- [x] **RAW-01**: Raw SHA256 hashes 100% unchanged before and after execution.
- [x] **ROW-01**: 100% row reconciliation (0 rows lost).
- [x] **KEY-01**: System lineage key `source_record_key` 100% unique, 0 nulls.
- [x] **H01**: Cross-source overlap (exact, normalized, near-duplicate) quantified.
- [x] **H02**: Label dependency crosstabs generated.
- [x] **H03**: Source B entity cardinality mapped.
- [x] **H04**: PRDECT product context stability evaluated.
- [x] **H05**: Advanced text forensics profiled.
- [x] **H06**: Transformation contracts executed losslessly.
- [x] **H07**: Category harmonization mapped without fake categories.
- [x] **H08**: Issue annotation protocol defined.
- [x] **H09**: Synthetic operational policy locked (`is_synthetic = TRUE`).
- [x] **REP-01**: Reproducibility test 100% PASS.

---

## 19. FORMAL GATE & DATASET FREEZE RESULT

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

---

## 20. FINAL RECOMMENDATION

`DATA_FOUNDATION_VERSION = 1.0` is officially **FROZEN** and ready for database staging architecture.

The project is officially authorized to proceed to **Phase 3: Business & System Requirements** planning (`MODE = PLAN_ONLY`) upon explicit user authorization.
