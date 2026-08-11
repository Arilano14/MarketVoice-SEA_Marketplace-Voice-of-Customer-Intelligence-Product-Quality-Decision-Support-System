# MARKETVOICE SEA — BUSINESS REQUIREMENTS DOCUMENT (BRD)

**Document Version**: 1.0 (Phase 3 Requirements Baseline v1.0)  
**Deliverable ID**: `DEL-04`  
**Phase**: Phase 3 (Business & System Requirements Specification & Governance Baseline)  
**Data Foundation Baseline**: `DATA_FOUNDATION_VERSION = 1.0` (Dual-Source: `SRC_PRDECT_ID_V1` & `SRC_TOKOPEDIA_REVIEWS_2019`)  
**Phase 3 Status**: `PHASE_3_EXECUTION_STATUS = COMPLETED`, `PHASE_3_REVIEW_STATUS = READY_FOR_HUMAN_REVIEW`, `PHASE_3_GATE_STATUS = NOT_EVALUATED`  

---

## 1. EXECUTIVE SUMMARY & MANDATE

MarketVoice SEA (*Marketplace Voice-of-Customer Intelligence & Product Quality Decision Support System*) is an independent academic/portfolio postgraduate (S2-level) prototype inspired by e-commerce feedback intelligence.

The system converts unstructured marketplace customer feedback into structured intelligence, shop-level review metrics, aspect-based issue discovery, decision prioritization, and executive reporting while respecting strict empirical data boundaries.

### Data Foundation & Boundary Principles
1. **Dual-Source Architecture**:
   - **Source A (`SRC_PRDECT_ID_V1`)**: Primary annotated research benchmark (Mendeley Data, DOI `10.17632/574v66hf2v.1`, 5,400 rows, 29 categories, 0 nulls, provided gold 2-class sentiment and 5-class emotion labels).
   - **Source B (`SRC_TOKOPEDIA_REVIEWS_2019`)**: Secondary BI scale dataset (Hugging Face `farhamu/tokopedia-product-reviews-2019`, 40,607 rows, 3,664 product listings, 158 shops, 5 categories).
2. **Strict Dual-Source Isolation**: Source A and Source B are distinct datasets. `CROSS_SOURCE_PRODUCT_LINKAGE = false` and `CROSS_SOURCE_SHOP_LINKAGE = false`. Zero cross-source entity linkage assumptions.
3. **Temporal & Operational Boundaries**:
   - `REAL_REVIEW_TIMESTAMP = NOT_AVAILABLE` and `REAL_TEMPORAL_REVIEW_ANALYTICS = NOT_SUPPORTED_BY_DATA_FOUNDATION_V1`. Authentic raw datasets lack review creation dates.
   - `SYNTHETIC_OPERATIONAL_TIMELINE = CANDIDATE_ONLY`. Operational case lifecycle logs for Track B workflow simulation strictly carry `is_synthetic = TRUE`, `scenario_version`, and `simulation_rule_version`.
4. **Issue Classification Boundary**: `ISSUE_DISCOVERY = SUPPORTED` via unsupervised text mining. `SUPERVISED_ISSUE_CLASSIFICATION = CONDITIONAL_PENDING_PHASE_9_HUMAN_ANNOTATION` (`DEPENDS_ON = PHASE_9_TAXONOMY_AND_ANNOTATION_GATE`).

---

## 2. SIMULATED STAKEHOLDER DECISION MATRIX

To anchor business requirements in authentic decision-making without claiming real-world deployment or corporate endorsement, 9 simulated stakeholder roles are defined:

| Stakeholder Role | Primary Responsibilities | Key Decision Supported | Primary Interface |
|---|---|---|---|
| **Head of Customer Experience (CX)** | Macro customer experience monitoring, rating distribution health, negative review risk tracking. | Platform-wide rating distribution health & negative feedback ratio (`BR-001`, `BR-002`). | Executive CX Dashboard |
| **Product Quality Manager** | Category and product-level quality control, product listing defect risk ranking. | High-defect product listing identification & category quality risk (`BR-003`, `BR-004`). | Product Quality Mart |
| **Category Manager** | Category performance monitoring, cross-category rating benchmarks. | Category customer satisfaction rankings & category volume share (`BR-004`). | Category Intelligence Mart |
| **Seller / Shop Operations** | Shop-level review monitoring, high-risk merchant review tracking. | Shop-level review volume, average rating, & shop negative review rate (`BR-005`). | Shop Review Intelligence Mart |
| **Customer Support (CS) Manager** | Priority case queue management, urgent complaint routing, review escalation. | High-risk customer complaint priority ordering & escalation queue (`BR-007`). | Priority Case Queue & Webhook |
| **BI / Data Analyst** | Data warehouse query execution, summary mart analysis, report design. | Structured dimensional queries, metric aggregations, & schema compliance (`BR-009`). | SQL Data Marts & BI Reporting |
| **Data Science Team** | Rating/sentiment prediction model development, evaluation, & governance. | Model performance tracking, confusion matrix analysis, & error auditing (`BR-008`). | Model Validation Mart |
| **Data Governance / Engineering** | Pipeline auditability, raw immutability, data lineage, quality monitoring. | Data lineage verification, SHA256 checksums, missing value/duplicate audits (`BR-010`). | Data Governance Mart |
| **Management / Executive Decision User** | Strategic oversight, decision support system governance, resource allocation. | System-wide quality summaries, model trust, & decision-support efficacy (`BR-001`, `BR-007`). | Executive Overview |

---

## 3. CORE BUSINESS QUESTIONS (BQ)

The platform addresses 7 core Business Questions anchored strictly in data capabilities:

- **BQ-CX (CX Platform Signals)**: What are the overall review-based customer experience signals, star rating distributions, and negative review rates across marketplace feedback?
- **BQ-PRODUCT (Product & Category Signals)**: Which specific product listings and product category groups exhibit elevated negative customer review rates?
- **BQ-SHOP (Shop-Level Review Intelligence)**: Which Source B shops exhibit elevated negative review signals and low average ratings based on authentic customer feedback? (*Note: Evaluated as Shop-Level Review Intelligence, not overall seller performance*).
- **BQ-ISSUE (Issue & Aspect Themes)**: What specific customer complaint themes (e.g., packaging damage, product defect, shipping delay) occur within review text? (*Status: CONDITIONAL_PENDING_PHASE_9_ANNOTATION*).
- **BQ-DSS (Decision Support Prioritization)**: Which specific customer review cases require prioritized human review based on low star ratings, negative sentiment, and issue severity?
- **BQ-MODEL (Model Efficacy & Governance)**: How reliable, explainable, and consistent are candidate ML model predictions supporting decision workflows?
- **BQ-DQ (Data Quality & Governance Boundaries)**: What data quality characteristics, missing values, duplicates, and governance boundaries must stakeholders understand when interpreting analytical reports?

---

## 4. FORMAL BUSINESS REQUIREMENTS (BR)

```
Prioritization Standard:
- MUST: Critical capability required for Phase 3 baseline & core pipeline.
- SHOULD: Important capability to be implemented if resources permit.
- COULD: Desirable enhancement for downstream phases.
- WONT_CURRENT_RELEASE: Out of scope for current release.
```

### BR-001: Macro Customer Experience Signal Analytics
- **BR_ID**: `BR-001`
- **TITLE**: Macro Customer Experience Signal Analytics
- **BUSINESS_NEED**: Platform leadership requires aggregate visibility into customer feedback signals to monitor overall satisfaction trends.
- **STAKEHOLDER**: Head of Customer Experience, Management / Executive Decision User
- **BUSINESS_QUESTION**: `BQ-CX`
- **RATIONALE**: Aggregate star rating distributions and negative review rates provide baseline visibility into customer experience health.
- **DATA_REQUIREMENT**: Discrete star ratings (1-5) and review text from Source A and Source B.
- **DATA_SUPPORT_CLASSIFICATION**: `SUPPORTED_BY_AUTHENTIC_DATA`
- **PRIORITY**: `MUST`
- **SUCCESS_CRITERIA**: System aggregates average star rating, rating distribution counts, and negative review rates across datasets without data loss.
- **LIMITATION**: Temporal trend analytics (monthly/weekly) are unsupported due to missing authentic review timestamps.
- **DEPENDENCY**: `DATA_FOUNDATION_VERSION = 1.0`
- **ACCEPTANCE_CRITERIA**: System reports accurate overall average rating and 1-to-5 star rating breakdown for 100% of ingested rows.
- **TRACEABILITY**: Maps to `BQ-CX` $\rightarrow$ `IR-001` $\rightarrow$ `KPI-CX-01..05` $\rightarrow$ `FR-004` $\rightarrow$ `mart_cx_overview`.

### BR-002: Provided Sentiment & Emotion Benchmark Analytics
- **BR_ID**: `BR-002`
- **TITLE**: Provided Sentiment & Emotion Benchmark Analytics
- **BUSINESS_NEED**: Data science and CX teams require benchmark evaluation of provided research sentiment and emotion labels.
- **STAKEHOLDER**: Head of CX, Data Science Team
- **BUSINESS_QUESTION**: `BQ-CX`, `BQ-MODEL`
- **RATIONALE**: Source A provides gold 2-class sentiment and 5-class emotion labels annotated by research experts.
- **DATA_REQUIREMENT**: Provided `Sentiment` and `Emotion` columns in `SRC_PRDECT_ID_V1`.
- **DATA_SUPPORT_CLASSIFICATION**: `SUPPORTED_SOURCE_A_ONLY`
- **PRIORITY**: `MUST`
- **SUCCESS_CRITERIA**: System reports sentiment distribution and emotion breakdown for Source A records.
- **LIMITATION**: Sentiment and emotion gold labels are unavailable for Source B (`SRC_TOKOPEDIA_REVIEWS_2019`).
- **DEPENDENCY**: Source A (`SRC_PRDECT_ID_V1`)
- **ACCEPTANCE_CRITERIA**: System calculates sentiment and emotion class breakdowns across all 5,400 Source A rows.
- **TRACEABILITY**: Maps to `BQ-CX`, `BQ-MODEL` $\rightarrow$ `IR-002` $\rightarrow$ `KPI-CX-06..07` $\rightarrow$ `FR-005` $\rightarrow$ `mart_model_governance_eval`.

### BR-003: Product Listing Quality Risk Tracking
- **BR_ID**: `BR-003`
- **TITLE**: Product Listing Quality Risk Tracking
- **BUSINESS_NEED**: Product Quality Managers need to identify specific product listings exhibiting high negative review counts.
- **STAKEHOLDER**: Product Quality Manager, BI / Data Analyst
- **BUSINESS_QUESTION**: `BQ-PRODUCT`
- **RATIONALE**: Listing-level metrics pinpoint specific products with recurring quality issues.
- **DATA_REQUIREMENT**: `product_id`, `product_name`, `rating`, `text` in Source B.
- **DATA_SUPPORT_CLASSIFICATION**: `SUPPORTED_SOURCE_B_ONLY`
- **PRIORITY**: `MUST`
- **SUCCESS_CRITERIA**: System groups metrics by `product_id` (3,664 unique listings) and ranks listings by negative review rate.
- **LIMITATION**: Source A lacks `product_id` listing identifiers (contains text titles only).
- **DEPENDENCY**: Source B (`SRC_TOKOPEDIA_REVIEWS_2019`)
- **ACCEPTANCE_CRITERIA**: System generates product listing summary table containing review volume, average rating, and negative review rate for all 3,664 products.
- **TRACEABILITY**: Maps to `BQ-PRODUCT` $\rightarrow$ `IR-003` $\rightarrow$ `KPI-PRD-01..03` $\rightarrow$ `FR-006` $\rightarrow$ `mart_product_quality`.

### BR-004: Category Quality & Volume Benchmark Analytics
- **BR_ID**: `BR-004`
- **TITLE**: Category Quality & Volume Benchmark Analytics
- **BUSINESS_NEED**: Category Managers require cross-category comparisons to evaluate category-level quality risks.
- **STAKEHOLDER**: Category Manager, Product Quality Manager
- **BUSINESS_QUESTION**: `BQ-PRODUCT`
- **RATIONALE**: Category-level aggregation highlights broad product domain risk profiles.
- **DATA_REQUIREMENT**: `category` fields in Source A (29 raw categories) and Source B (5 categories).
- **DATA_SUPPORT_CLASSIFICATION**: `SUPPORTED_BY_AUTHENTIC_DATA`
- **PRIORITY**: `MUST`
- **SUCCESS_CRITERIA**: System aggregates review metrics by raw category and mapped canonical category family.
- **LIMITATION**: Cross-source category comparison requires category harmonization policy mapping.
- **DEPENDENCY**: `DATA_FOUNDATION_VERSION = 1.0`
- **ACCEPTANCE_CRITERIA**: System presents category review volume, average rating, and negative review share across all categories.
- **TRACEABILITY**: Maps to `BQ-PRODUCT` $\rightarrow$ `IR-004` $\rightarrow$ `KPI-CAT-01..03` $\rightarrow$ `FR-007` $\rightarrow$ `mart_product_quality`.

### BR-005: Shop-Level Review Intelligence (Source B)
- **BR_ID**: `BR-005`
- **TITLE**: Shop-Level Review Intelligence (Source B)
- **BUSINESS_NEED**: Seller Operations requires visibility into shop-level customer review signals to detect high-risk merchants.
- **STAKEHOLDER**: Seller / Shop Operations, BI / Data Analyst
- **BUSINESS_QUESTION**: `BQ-SHOP`
- **RATIONALE**: Shop-level review aggregation enables merchant-level review risk assessment across 158 shops in Source B.
- **DATA_REQUIREMENT**: `shop_id`, `product_id`, `rating`, `text` in Source B.
- **DATA_SUPPORT_CLASSIFICATION**: `SUPPORTED_SOURCE_B_ONLY`
- **PRIORITY**: `MUST`
- **SUCCESS_CRITERIA**: System aggregates review metrics by `shop_id` (158 shops) and computes shop negative review rates.
- **LIMITATION**: Applies exclusively to Source B. Evaluated strictly as Shop-Level Review Intelligence, not overall seller operational performance.
- **DEPENDENCY**: Source B (`SRC_TOKOPEDIA_REVIEWS_2019`)
- **ACCEPTANCE_CRITERIA**: System generates shop summary metrics for all 158 shops in Source B.
- **TRACEABILITY**: Maps to `BQ-SHOP` $\rightarrow$ `IR-005` $\rightarrow$ `KPI-SHP-01..04` $\rightarrow$ `FR-008` $\rightarrow$ `mart_seller_intelligence`.

### BR-006: Aspect & Issue Discovery Analytics (Conditional)
- **BR_ID**: `BR-006`
- **TITLE**: Aspect & Issue Discovery Analytics (Conditional)
- **BUSINESS_NEED**: Product Quality Managers need to extract specific issue themes from review text.
- **STAKEHOLDER**: Product Quality Manager, Data Science Team
- **BUSINESS_QUESTION**: `BQ-ISSUE`
- **RATIONALE**: Unsupervised text discovery identifies candidate issue keywords, while supervised classification requires human annotation.
- **DATA_REQUIREMENT**: Customer review text strings from Source A and Source B.
- **DATA_SUPPORT_CLASSIFICATION**: `CONDITIONAL_PENDING_PHASE_9_ANNOTATION`
- **PRIORITY**: `SHOULD`
- **SUCCESS_CRITERIA**: Unsupervised topic discovery supported in Phase 3/4; supervised multi-label classification enabled post-Phase 9 annotation.
- **LIMITATION**: Supervised multi-label aspect ground truth does not exist in raw data.
- **DEPENDENCY**: `DEPENDS_ON = PHASE_9_TAXONOMY_AND_ANNOTATION_GATE`
- **ACCEPTANCE_CRITERIA**: Issue intelligence features carry explicit conditional flags until Phase 9 human annotation protocol ($N=1,000$) is completed.
- **TRACEABILITY**: Maps to `BQ-ISSUE` $\rightarrow$ `IR-006` $\rightarrow$ `KPI-ISS-01..03` $\rightarrow$ `FR-009` $\rightarrow$ `mart_issue_aspect_intelligence`.

### BR-007: Decision-Support Priority Review Queue
- **BR_ID**: `BR-007`
- **TITLE**: Decision-Support Priority Review Queue
- **BUSINESS_NEED**: CS Managers require an ordered, prioritized queue of severe customer complaints for human review.
- **STAKEHOLDER**: Customer Service Manager, Management / Executive User
- **BUSINESS_QUESTION**: `BQ-DSS`
- **RATIONALE**: Prioritizing complaints by multi-criteria scoring ensures high-risk feedback receives immediate attention.
- **DATA_REQUIREMENT**: Review rating, text sentiment, and candidate issue severity.
- **DATA_SUPPORT_CLASSIFICATION**: `SUPPORTED_VIA_ANALYTICAL_MODEL`
- **PRIORITY**: `MUST`
- **SUCCESS_CRITERIA**: System ranks negative reviews by priority score and flags high-risk review cases.
- **LIMITATION**: Exact priority scoring weights and thresholds belong to Phase 10 design.
- **DEPENDENCY**: Phase 8 Rating/Sentiment ML & Phase 10 DSS
- **ACCEPTANCE_CRITERIA**: System generates prioritized list of negative reviews sorted by configurable priority criteria.
- **TRACEABILITY**: Maps to `BQ-DSS` $\rightarrow$ `IR-007` $\rightarrow$ `KPI-DSS-01..04` $\rightarrow$ `FR-010` $\rightarrow$ `mart_priority_decision_queue`.

### BR-008: Model Governance & Validation Transparency
- **BR_ID**: `BR-008`
- **TITLE**: Model Governance & Validation Transparency
- **BUSINESS_NEED**: Data Science Lead and governance reviewers require transparent evaluation of ML candidate models.
- **STAKEHOLDER**: Data Science Team, Data Governance / Engineering
- **BUSINESS_QUESTION**: `BQ-MODEL`
- **RATIONALE**: Model validation metrics (F1, Accuracy, Confusion Matrix) ensure model outputs are reliable before downstream use.
- **DATA_REQUIREMENT**: Model predictions, gold ground truth labels, and validation split indices.
- **DATA_SUPPORT_CLASSIFICATION**: `SUPPORTED_VIA_EVALUATION_PIPELINE`
- **PRIORITY**: `MUST`
- **SUCCESS_CRITERIA**: System logs model evaluation metrics without hardcoded numeric target thresholds (`TARGET_THRESHOLD = TO_BE_DETERMINED_IN_PHASE_4`).
- **LIMITATION**: Metric targets will be baselined in Phase 4 after baseline model evaluation.
- **DEPENDENCY**: Phase 4 Research & Analytical Design
- **ACCEPTANCE_CRITERIA**: System logs model evaluation metrics in structured governance format.
- **TRACEABILITY**: Maps to `BQ-MODEL` $\rightarrow$ `IR-008` $\rightarrow$ `KPI-MDL-01..05` $\rightarrow$ `FR-011` $\rightarrow$ `mart_model_governance_eval`.

### BR-009: Data Pipeline Quality & Lineage Traceability
- **BR_ID**: `BR-009`
- **TITLE**: Data Pipeline Quality & Lineage Traceability
- **BUSINESS_NEED**: Data Governance reviewers require full auditability and 100% row reconciliation across data pipelines.
- **STAKEHOLDER**: Data Governance / Engineering, BI / Data Analyst
- **BUSINESS_QUESTION**: `BQ-DQ`
- **RATIONALE**: Technical lineage keys (`source_record_key`) and SHA256 checksums ensure zero unexplained data loss.
- **DATA_REQUIREMENT**: `source_record_key`, `source_id`, `sha256`, `source_row_number`.
- **DATA_SUPPORT_CLASSIFICATION**: `SUPPORTED_BY_AUTHENTIC_DATA`
- **PRIORITY**: `MUST`
- **SUCCESS_CRITERIA**: System tracks row reconciliation ($100\%$ match), lineage key uniqueness ($100\%$), and zero silent imputation.
- **LIMITATION**: None. Lineage key generator fully implemented in Phase 2.
- **DEPENDENCY**: `DATA_FOUNDATION_VERSION = 1.0`
- **ACCEPTANCE_CRITERIA**: System verifies 0 row loss and 100% lineage key uniqueness across 46,007 rows.
- **TRACEABILITY**: Maps to `BQ-DQ` $\rightarrow$ `IR-009` $\rightarrow$ `KPI-DQ-01..06` $\rightarrow$ `FR-002`, `FR-003` $\rightarrow$ `mart_data_pipeline_audit`.

### BR-010: Simulated Operational Workflow Integration (Track B)
- **BR_ID**: `BR-010`
- **TITLE**: Simulated Operational Workflow Integration (Track B)
- **BUSINESS_NEED**: CS leadership needs to simulate case handling workflows and webhook ticket dispatches.
- **STAKEHOLDER**: Customer Service Manager, Data Governance / Engineering
- **BUSINESS_QUESTION**: `BQ-DSS`
- **RATIONALE**: Operational case logs (CS tickets, SLA tracking) allow testing workflow automation without altering authentic data.
- **DATA_REQUIREMENT**: Authentic review reference keys linked to synthetic case attributes (`is_synthetic = TRUE`).
- **DATA_SUPPORT_CLASSIFICATION**: `SIMULATED_OPERATIONAL_ONLY`
- **PRIORITY**: `SHOULD`
- **SUCCESS_CRITERIA**: Simulated workflow records carry mandatory `is_synthetic = TRUE` flags and `scenario_version` metadata. Zero synthetic data injected into raw CSVs.
- **LIMITATION**: Simulated operational data only; does not represent authentic Tokopedia operational logs.
- **DEPENDENCY**: `docs/governance/synthetic_data_policy.md`
- **ACCEPTANCE_CRITERIA**: Simulated records display explicit synthetic banners and metadata tags.
- **TRACEABILITY**: Maps to `BQ-DSS` $\rightarrow$ `IR-010` $\rightarrow$ `KPI-DSS-04` $\rightarrow$ `FR-012` $\rightarrow$ FastAPI & n8n Webhook.
