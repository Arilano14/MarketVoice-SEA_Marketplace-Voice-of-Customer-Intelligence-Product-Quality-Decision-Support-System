# MARKETVOICE SEA — BUSINESS & INFORMATION REQUIREMENTS

**Version:** 2.0 (Phase 3 revision)  
**Phase:** 3 — Business & System Requirements  
**Data foundation:** `SRC_PRDECT_ID_V1` and `SRC_TOKOPEDIA_REVIEWS_2019`  
**Requirement status:** `REVISED_ARTIFACTS_PREPARED_FOR_HUMAN_REVIEW`  
**Gate status:** `PHASE_3_GATE = NOT_EVALUATED`

## 1. Evidence and scope lock

| Source | Verified analytical capability | Material limitation |
|---|---|---|
| Source A — PRDECT-ID | 5,400 review texts, 1–5 ratings, provided sentiment and emotion labels, category and product attributes | No verified product or shop identifier; no review timestamp |
| Source B — Tokopedia Product Reviews 2019 | 40,607 review texts, 1–5 ratings, category, `product_id`, `product_name`, and `shop_id` | No sentiment/emotion gold labels; no review timestamp, operational case, SLA, or resolution data |

The datasets are complementary and remain isolated. `CROSS_SOURCE_ROW_LINKAGE = NOT_SUPPORTED`; `FUZZY_PRODUCT_LINKAGE = NOT_APPROVED`. Project inspiration is distinct from the actual analytical data sources; neither source is represented as Shopee data.

Authentic time trend, period-over-period deterioration, and temporal alerting are not supported. Issue taxonomy and issue gold labels are not assumed. Review free text requires privacy review because it may contain incidental sensitive information. `NO_INTENTIONAL_PII_ENRICHMENT = TRUE` and `NO_CUSTOMER_PROFILING = TRUE`.

## 2. Business objectives and questions

| Business objective | Business question |
|---|---|
| Turn marketplace review evidence into interpretable customer-experience and product-quality information. | `BQ-001` What review and rating signals describe customer experience in each verified source? |
| Enable product-quality investigation using verified identifiers. | `BQ-002` Which Source B product listings have concentrated negative-review signals? |
| Provide bounded shop review context without asserting seller performance. | `BQ-003` Which Source B shops have notable review-experience indicators? |
| Enable future issue understanding only when its analytical basis is validated. | `BQ-004` Which issue themes can be responsibly identified from review text? |
| Support accountable human decision-making. | `BQ-005` What evidence and uncertainty should inform a human review priority decision? |
| Demonstrate analytical reliability and responsible use. | `BQ-006` How can users assess data quality, provenance, baseline labels, and limitations? |

## 3. Business requirements

| ID / priority | Why / who | Required outcome | Data / availability | Validation / future phase |
|---|---|---|---|---|
| `BR-001` MUST | CX and management need a factual experience baseline. | Review and rating summaries distinguish source provenance and do not imply time trends. | Review text and rating, Sources A+B — `VERIFIED`. | Reconcile all source rows and verify no temporal measure. Phases 6–7. |
| `BR-002` MUST | Product-quality users need listing-level evidence. | Product review volume, rating, and negative-review concentration are available per verified Source B `product_id`. | Source B `product_id`, name, rating, text — `VERIFIED`. | Coverage reconciles to 3,664 Source B products. Phases 6–7. |
| `BR-003` SHOULD | Shop-review users need contextual review indicators. | Review volume, rating, negative-review concentration, and product coverage are available per Source B `shop_id`. No seller-performance claim or punitive use. | Source B `shop_id`, `product_id`, rating, text — `VERIFIED`. | Coverage reconciles to 158 shops; language remains bounded. Phases 6–7. |
| `BR-004` MUST | CX and data-science users need a benchmark for provided labels. | Source A sentiment and emotion distributions can be examined separately from Source B. | Source A `Sentiment`, `Emotion`, rating, review text — `VERIFIED`. | Results reconcile to 5,400 records and make source-only scope explicit. Phase 8. |
| `BR-005` SHOULD | Product-quality users need issue intelligence, if valid. | The system shall support candidate issue intelligence from review text only after a taxonomy, annotation basis, and evaluation approach are validated. | Review text A+B — `TO_BE_VALIDATED` for issue labels/taxonomy. | Phase 9 validates taxonomy, annotation, and evaluation; no issue label is claimed before then. Phase 9. |
| `BR-006` SHOULD | Decision users need accountable prioritization, not automated enforcement. | The system shall support explainable prioritization, rationale, uncertainty visibility, auditability, and mandatory human review. | Ratings and later validated analytical outputs — `CONDITIONAL`. | Phase 10 validates explanation, review, and audit criteria; formula, weights, and thresholds are deferred. Phases 9–10. |
| `BR-007` MUST | Governance users need trustworthy analysis. | Provenance, source isolation, data-quality results, free-text privacy review, and limitations are visible to authorized users. | Source manifest, capability matrix, source fields, review text — `VERIFIED`. | Traceability, reconciliation, privacy review, and limitation checks pass. Phases 6, 13. |

## 4. Information requirements

| ID / priority | Information needed and grain | Source / availability | Decision and validation |
|---|---|---|---|
| `IR-001` MUST | Review count, rating distribution, average rating, and low-rating share; source and category grain. | A+B review text/rating/category — `VERIFIED`. | Supports `BQ-001`; totals reconcile to input rows; no date grain is permitted. |
| `IR-002` MUST | Product review volume, average rating, and low-rating share; `product_id` grain. | Source B — `VERIFIED`. | Supports `BQ-002`; every output product has verified Source B provenance. |
| `IR-003` SHOULD | Shop review volume, average rating, low-rating share, and distinct product count; `shop_id` grain. | Source B — `VERIFIED`. | Supports `BQ-003`; described only as review indicators. |
| `IR-004` MUST | Sentiment and emotion class distributions; Source A label-class grain. | Source A provided labels — `VERIFIED`. | Supports `BQ-001` and `BQ-006`; label scope is not generalized to Source B. |
| `IR-005` SHOULD | Candidate issue theme, supporting text evidence, confidence, and uncertainty; issue-theme grain. | Review text A+B — `TO_BE_VALIDATED`. | Supports `BQ-004`; use begins only after Phase 9 gate. |
| `IR-006` SHOULD | Priority rationale, inputs used, uncertainty, reviewer decision, and audit reference; review-case grain. | Verified review attributes plus validated downstream outputs — `CONDITIONAL`. | Supports `BQ-005`; no fixed score scale, weights, or thresholds in Phase 3. |
| `IR-007` MUST | Source provenance, field availability, quality findings, privacy-review outcome, and analytical limitations; source/dataset grain. | Manifest, forensic audit, capability matrix — `VERIFIED`. | Supports `BQ-006`; evidence is reconciled to Phase 2 artifacts. |

## 5. Data requirements

| ID / priority | Requirement | Availability | Validation / implementation phase |
|---|---|---|---|
| `DR-001` MUST | Preserve source provenance and original identifiers while representing verified review records consistently. | `VERIFIED` | Source-specific identifiers remain distinguishable; Phase 6. |
| `DR-002` MUST | Retain review text, 1–5 rating, category, and source identity only as supplied. | `VERIFIED` | Row and valid-rating reconciliation; Phase 6. |
| `DR-003` MUST | Use `product_id` and `shop_id` only from Source B; do not link them to Source A. | `VERIFIED` | Isolation check confirms zero cross-source linkage; Phase 6. |
| `DR-004` MUST | Treat Source A sentiment/emotion as provided labels and Source B as unlabeled for those tasks. | `VERIFIED` | Label coverage and source scope checked; Phase 8. |
| `DR-005` SHOULD | Use issue taxonomy, annotations, and issue labels only after validation. | `TO_BE_VALIDATED` | Phase 9 methodology and results approval. |
| `DR-006` MUST | Apply no intentional PII enrichment, no customer profiling, and a free-text privacy review before analytical exposure. | `VERIFIED` policy requirement | Privacy review record and output check; Phases 6, 13. |

## 6. MoSCoW scope

**MUST:** `BR-001`, `BR-002`, `BR-004`, `BR-007`; associated MUST IR/DR items.  
**SHOULD:** `BR-003`, `BR-005`, `BR-006`; these remain bounded by their stated dependencies.  
**COULD:** Future additional non-identifying workflow-demonstration fields, only with a separate approved requirement.  
**WON'T (MVP):** authentic temporal analytics; synthetic timeline; operational SLA/resolution workflow; new data source; customer identity/profile; cross-source fuzzy matching; live marketplace integration; production API; n8n; Power BI implementation; physical database design; model selection; priority formula, weights, or thresholds.

## 7. Track classification

| Track | Scope | Entry condition |
|---|---|---|
| Track A — authentic MVP | Requirements using verified review, rating, Source A labels, and Source B product/shop identifiers. | Phase 2 evidence remains accepted. |
| Track B — conditional extension | Issue classification, decision-support scoring, optional synthetic operational demonstration, and any time-based simulation. | Separate future approval plus the relevant Phase 9/10/11 gates. Synthetic records, if later approved, may use only `case_id`, `event_id`, `case_status`, `priority_status`, `created_at`, `reviewed_at`, `sla_target`, `resolution_status`, and `intervention_type`; they must not represent real review time or customer identity. |
