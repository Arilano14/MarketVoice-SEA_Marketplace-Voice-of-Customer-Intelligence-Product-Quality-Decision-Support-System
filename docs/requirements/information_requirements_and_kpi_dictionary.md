# MARKETVOICE SEA — INFORMATION REQUIREMENTS & KPI DICTIONARY v1.0

**Document Version**: 1.0 (Phase 3 Baseline v1.0)  
**Deliverable ID**: `DEL-04 / DEL-05 Extension`  
**Phase**: Phase 3 (Business & System Requirements Specification & Governance Baseline)  
**Data Foundation Baseline**: `DATA_FOUNDATION_VERSION = 1.0` (Dual-Source: `SRC_PRDECT_ID_V1` & `SRC_TOKOPEDIA_REVIEWS_2019`)  
**Phase 3 Status**: `PHASE_3_EXECUTION_STATUS = COMPLETED`, `PHASE_3_REVIEW_STATUS = READY_FOR_HUMAN_REVIEW`, `PHASE_3_GATE_STATUS = NOT_EVALUATED`  

---

## 1. INFORMATION REQUIREMENTS (IR)

Every approved Business Question (`BQ-CX`, `BQ-PRODUCT`, `BQ-SHOP`, `BQ-ISSUE`, `BQ-DSS`, `BQ-MODEL`, `BQ-DQ`) maps to at least one explicit Information Requirement:

### IR-001: CX Platform Rating & Feedback Signals
- **IR_ID**: `IR-001`
- **INFORMATION_NEED**: Platform-wide star rating volume, rating breakdown (1 to 5 stars), and negative feedback share.
- **STAKEHOLDER**: Head of Customer Experience, Management / Executive User
- **DECISION_SUPPORTED**: Macro customer experience condition monitoring and baseline rating health evaluation.
- **BUSINESS_QUESTION**: `BQ-CX`
- **GRAIN**: Platform level & Source level aggregate
- **DIMENSIONS**: `source_id`, `rating`
- **MEASURE_OR_INDICATOR**: Total Review Volume, Average Star Rating, Rating Count Distribution, Negative Review Rate.
- **SOURCE_DATA**: Source A (`SRC_PRDECT_ID_V1`) & Source B (`SRC_TOKOPEDIA_REVIEWS_2019`)
- **AUTHENTIC_OR_SIMULATED**: `AUTHENTIC_DATA`
- **SUPPORT_STATUS**: `SUPPORTED`
- **LIMITATION**: Unsupported for temporal trend analytics due to missing authentic review timestamps.
- **FUTURE_OUTPUT**: `mart_cx_overview` data mart & Executive CX Overview dashboard page.

### IR-002: Provided Sentiment & Emotion Class Signals (Source A)
- **IR_ID**: `IR-002`
- **INFORMATION_NEED**: Sentiment (Positive/Negative) and emotion (5 classes) label breakdowns from research annotations.
- **STAKEHOLDER**: Head of CX, Data Science Team
- **DECISION_SUPPORTED**: Benchmark validation of provided research annotations and rating-sentiment alignment.
- **BUSINESS_QUESTION**: `BQ-CX`, `BQ-MODEL`
- **GRAIN**: Individual review record level & label class aggregate
- **DIMENSIONS**: `Sentiment`, `Emotion`, `Customer Rating`
- **MEASURE_OR_INDICATOR**: Sentiment Class Count/Share, Emotion Class Count/Share, Rating x Sentiment Crosstab.
- **SOURCE_DATA**: Source A (`SRC_PRDECT_ID_V1`)
- **AUTHENTIC_OR_SIMULATED**: `AUTHENTIC_DATA`
- **SUPPORT_STATUS**: `SUPPORTED_SOURCE_A_ONLY`
- **LIMITATION**: Unavailable for Source B (`SRC_TOKOPEDIA_REVIEWS_2019`).
- **FUTURE_OUTPUT**: `mart_model_governance_eval` data mart.

### IR-003: Product Listing Quality & Feedback Signals (Source B)
- **IR_ID**: `IR-003`
- **INFORMATION_NEED**: Product listing review volume, average rating, and negative review share grouped by `product_id`.
- **STAKEHOLDER**: Product Quality Manager, BI / Data Analyst
- **DECISION_SUPPORTED**: High-risk product listing identification and listing-level quality control.
- **BUSINESS_QUESTION**: `BQ-PRODUCT`
- **GRAIN**: Product Listing level (`product_id`)
- **DIMENSIONS**: `product_id`, `product_name`, `category`
- **MEASURE_OR_INDICATOR**: Product Review Volume, Product Average Rating, Product Negative Review Rate.
- **SOURCE_DATA**: Source B (`SRC_TOKOPEDIA_REVIEWS_2019`)
- **AUTHENTIC_OR_SIMULATED**: `AUTHENTIC_DATA`
- **SUPPORT_STATUS**: `SUPPORTED_SOURCE_B_ONLY`
- **LIMITATION**: Source A lacks listing-level `product_id` identifiers.
- **FUTURE_OUTPUT**: `mart_product_quality` data mart.

### IR-004: Category-Level Quality & Volume Benchmarks
- **IR_ID**: `IR-004`
- **INFORMATION_NEED**: Category-level review volume, average rating, and negative feedback share across categories.
- **STAKEHOLDER**: Category Manager, Product Quality Manager
- **DECISION_SUPPORTED**: Cross-category risk comparison and category quality baseline setting.
- **BUSINESS_QUESTION**: `BQ-PRODUCT`
- **GRAIN**: Category level (`Category` / `category`)
- **DIMENSIONS**: `category_raw`, `canonical_category_family`
- **MEASURE_OR_INDICATOR**: Category Review Volume, Category Average Rating, Category Negative Review Rate.
- **SOURCE_DATA**: Source A & Source B
- **AUTHENTIC_OR_SIMULATED**: `AUTHENTIC_DATA`
- **SUPPORT_STATUS**: `SUPPORTED`
- **LIMITATION**: Cross-source comparison requires category harmonization mapping rules.
- **FUTURE_OUTPUT**: `mart_product_quality` data mart.

### IR-005: Shop-Level Review Intelligence (Source B)
- **IR_ID**: `IR-005`
- **INFORMATION_NEED**: Shop-level review volume, average star rating, negative review share, and product listing count.
- **STAKEHOLDER**: Seller / Shop Operations, BI / Data Analyst
- **DECISION_SUPPORTED**: Shop review risk monitoring and high-risk merchant review tracking.
- **BUSINESS_QUESTION**: `BQ-SHOP`
- **GRAIN**: Shop level (`shop_id`)
- **DIMENSIONS**: `shop_id`
- **MEASURE_OR_INDICATOR**: Shop Review Volume, Shop Average Rating, Shop Negative Review Rate, Shop Product Count.
- **SOURCE_DATA**: Source B (`SRC_TOKOPEDIA_REVIEWS_2019`)
- **AUTHENTIC_OR_SIMULATED**: `AUTHENTIC_DATA`
- **SUPPORT_STATUS**: `SUPPORTED_SOURCE_B_ONLY`
- **LIMITATION**: Source B exclusive (158 shops). Evaluated strictly as Shop-Level Review Intelligence.
- **FUTURE_OUTPUT**: `mart_seller_intelligence` data mart.

### IR-006: Candidate Issue & Aspect Keyword Extraction (Conditional)
- **IR_ID**: `IR-006`
- **INFORMATION_NEED**: Candidate issue frequency, issue theme share, and aspect co-occurrence across review text.
- **STAKEHOLDER**: Product Quality Manager, Data Science Team
- **DECISION_SUPPORTED**: Root-cause issue theme discovery and customer complaint categorization.
- **BUSINESS_QUESTION**: `BQ-ISSUE`
- **GRAIN**: Review text token level & Issue theme level
- **DIMENSIONS**: `issue_category_candidate`, `keyword_token`
- **MEASURE_OR_INDICATOR**: Issue Theme Frequency, Issue Theme Share.
- **SOURCE_DATA**: Source A & Source B review text strings
- **AUTHENTIC_OR_SIMULATED**: `AUTHENTIC_TEXT_DERIVED`
- **SUPPORT_STATUS**: `CONDITIONAL_PENDING_PHASE_9_ANNOTATION`
- **LIMITATION**: Supervised multi-label aspect classification requires Phase 9 human annotation protocol ($N=1,000$).
- **FUTURE_OUTPUT**: `mart_issue_aspect_intelligence` data mart.

### IR-007: Priority Decision Review Queue
- **IR_ID**: `IR-007`
- **INFORMATION_NEED**: Multi-criteria Priority Score (0-100), severity ranking, and actionable case flag for negative reviews.
- **STAKEHOLDER**: Customer Service Manager, Management / Executive User
- **DECISION_SUPPORTED**: Prioritized CS complaint ordering and human review queue assignment.
- **BUSINESS_QUESTION**: `BQ-DSS`
- **GRAIN**: Review record level (`source_record_key`)
- **DIMENSIONS**: `source_record_key`, `rating`, `predicted_sentiment`, `priority_score`
- **MEASURE_OR_INDICATOR**: Priority Score (0-100), Priority Rank, Priority Case Flag.
- **SOURCE_DATA**: Derived from authentic review text and model prediction outputs
- **AUTHENTIC_OR_SIMULATED**: `AUTHENTIC_DERIVED_MODEL_OUTPUT`
- **SUPPORT_STATUS**: `SUPPORTED_VIA_ANALYTICAL_MODEL`
- **LIMITATION**: Exact scoring formula parameters and thresholds belong to Phase 10 design.
- **FUTURE_OUTPUT**: `mart_priority_decision_queue` data mart.

### IR-008: Model Evaluation & Validation Logging
- **IR_ID**: `IR-008`
- **INFORMATION_NEED**: Model classification metrics (Accuracy, Macro/Weighted F1, Per-Class Precision/Recall, Confusion Matrix, QWK).
- **STAKEHOLDER**: Data Science Team, Data Governance / Engineering
- **DECISION_SUPPORTED**: Model performance benchmarking, model selection, and governance tracking.
- **BUSINESS_QUESTION**: `BQ-MODEL`
- **GRAIN**: Model experiment run level & Class level
- **DIMENSIONS**: `model_id`, `model_architecture`, `target_task`, `class_label`
- **MEASURE_OR_INDICATOR**: Accuracy, Macro F1, Weighted F1, Precision, Recall, Confusion Matrix, QWK.
- **SOURCE_DATA**: Model prediction outputs on validation/test splits
- **AUTHENTIC_OR_SIMULATED**: `AUTHENTIC_DERIVED_EVALUATION`
- **SUPPORT_STATUS**: `SUPPORTED`
- **LIMITATION**: Numeric target thresholds are set as `TARGET_THRESHOLD = TO_BE_DETERMINED_IN_PHASE_4`.
- **FUTURE_OUTPUT**: `mart_model_governance_eval` data mart.

### IR-009: Data Pipeline Quality & Audit Lineage
- **IR_ID**: `IR-009`
- **INFORMATION_NEED**: Ingestion row counts, reconciliation match, `source_record_key` uniqueness, null counts, and SHA256 hashes.
- **STAKEHOLDER**: Data Governance / Engineering, BI / Data Analyst
- **DECISION_SUPPORTED**: Pipeline integrity auditing, raw immutability compliance, and data governance verification.
- **BUSINESS_QUESTION**: `BQ-DQ`
- **GRAIN**: Data pipeline execution batch level & Source level
- **DIMENSIONS**: `source_id`, `import_batch_id`, `file_sha256`
- **MEASURE_OR_INDICATOR**: Ingested Row Count, Reconciliation %, Primary Key Uniqueness %, Null Count, SHA256 Match Status.
- **SOURCE_DATA**: System metadata and pipeline log outputs
- **AUTHENTIC_OR_SIMULATED**: `AUTHENTIC_PIPELINE_METADATA`
- **SUPPORT_STATUS**: `SUPPORTED`
- **LIMITATION**: None. Lineage generator fully implemented in Phase 2.
- **FUTURE_OUTPUT**: `mart_data_pipeline_audit` data mart.

### IR-010: Simulated Operational Workflow Logs (Track B)
- **IR_ID**: `IR-010`
- **INFORMATION_NEED**: Simulated CS ticket status, simulated operational handling events, and webhook dispatch dispatches.
- **STAKEHOLDER**: Customer Service Manager, Data Governance / Engineering
- **DECISION_SUPPORTED**: Testing operational workflow automation and webhook integration.
- **BUSINESS_QUESTION**: `BQ-DSS`
- **GRAIN**: Simulated operational ticket event level
- **DIMENSIONS**: `simulated_ticket_id`, `source_record_key`, `scenario_version`
- **MEASURE_OR_INDICATOR**: Simulated Case Count, Simulated Ticket Dispatch Status.
- **SOURCE_DATA**: Track B synthetic workflow generator
- **AUTHENTIC_OR_SIMULATED**: `SIMULATED_OPERATIONAL_ONLY`
- **SUPPORT_STATUS**: `SUPPORTED_AS_SIMULATION_ONLY`
- **LIMITATION**: Strictly carries `is_synthetic = TRUE`. Zero synthetic data injected into authentic source files.
- **FUTURE_OUTPUT**: FastAPI JSON endpoints & n8n webhook dispatches.

---

## 2. KPI DICTIONARY v1.0

The KPI Dictionary formally defines all quantitative analytical indicators supporting MarketVoice SEA.

```
Forbidden Claim Enforcement:
- NO NPS (Net Promoter Score) or CSAT proxy metrics are defined.
- NO authentic temporal trend metrics (monthly/weekly complaint trends) are defined.
```

### Domain 1: Customer Experience (CX) KPIs

#### KPI-CX-01: Total Review Volume
- **KPI_ID**: `KPI-CX-01`
- **KPI_NAME**: Total Review Volume
- **BUSINESS_PURPOSE**: Measure total volume of customer feedback records available for analysis.
- **STAKEHOLDER**: Head of CX, Management User
- **BUSINESS_QUESTION**: `BQ-CX`
- **DEFINITION**: Count of distinct customer review records ingested into the platform.
- **NUMERATOR**: Count of `source_record_key`
- **DENOMINATOR**: `NOT_APPLICABLE`
- **FORMULA**: $\text{Total Review Volume} = \text{COUNT}(\text{source\_record\_key})$
- **UNIT**: Reviews (Count)
- **GRAIN**: Platform level / Source level
- **DIMENSIONS**: `source_id`, `category`
- **FILTER_RULES**: None (100% of validated ingested rows).
- **SOURCE_DATASET**: `data/interim/validated/prdect_reviews_standardized.csv` & `tokopedia_reviews_2019_standardized.csv`
- **SOURCE_FIELDS**: `source_record_key`, `source_id`
- **AUTHENTIC_DERIVED_SIMULATED**: `AUTHENTIC_DATA`
- **DATA_SUPPORT_STATUS**: `SUPPORTED`
- **NULL_HANDLING**: `source_record_key` is 100% non-null.
- **EDGE_CASES**: Zero rows ingested yields 0.
- **EXPECTED_INTERPRETATION**: Higher volume increases analytical sample size.
- **LIMITATION**: Does not represent live platform review volume.
- **RECONCILIATION_METHOD**: Equals sum of raw CSV rows (Source A: 5,400 + Source B: 40,607 = 46,007).
- **FUTURE_VALIDATION_PHASE**: Phase 6 & Phase 7

#### KPI-CX-02: Average Customer Star Rating
- **KPI_ID**: `KPI-CX-02`
- **KPI_NAME**: Average Customer Star Rating
- **BUSINESS_PURPOSE**: Measure mean numerical star rating across customer reviews.
- **STAKEHOLDER**: Head of CX, Category Manager
- **BUSINESS_QUESTION**: `BQ-CX`
- **DEFINITION**: Arithmetic mean of discrete customer star ratings (1 to 5).
- **NUMERATOR**: Sum of `rating` (or `Customer Rating`)
- **DENOMINATOR**: Count of `rating`
- **FORMULA**: $\text{Average Rating} = \frac{\sum \text{rating}}{\text{COUNT}(\text{rating})}$
- **UNIT**: Star Rating (1.0 to 5.0 scale)
- **GRAIN**: Aggregate / Category / Product / Shop level
- **DIMENSIONS**: `source_id`, `category`, `product_id`, `shop_id`
- **FILTER_RULES**: `rating` MUST be between 1 and 5 inclusive.
- **SOURCE_DATASET**: Validated interim datasets
- **SOURCE_FIELDS**: `Customer Rating` (Source A), `rating` (Source B)
- **AUTHENTIC_DERIVED_SIMULATED**: `AUTHENTIC_DATA`
- **DATA_SUPPORT_STATUS**: `SUPPORTED`
- **NULL_HANDLING**: Ignore NULL values (0 nulls exist in raw data).
- **EDGE_CASES**: None. All ratings are integers 1 to 5.
- **EXPECTED_INTERPRETATION**: Higher values indicate higher aggregate customer satisfaction.
- **LIMITATION**: Ratings in e-commerce are heavily skewed toward 5 stars.
- **RECONCILIATION_METHOD**: Computed via SQL `AVG(rating)`.
- **FUTURE_VALIDATION_PHASE**: Phase 7

#### KPI-CX-03: Rating Distribution Count
- **KPI_ID**: `KPI-CX-03`
- **KPI_NAME**: Rating Distribution Count
- **BUSINESS_PURPOSE**: Measure total review volume broken down by individual star rating level (1, 2, 3, 4, 5 stars).
- **STAKEHOLDER**: Head of CX, Data Science Team
- **BUSINESS_QUESTION**: `BQ-CX`
- **DEFINITION**: Count of review records for each discrete star rating $k \in \{1, 2, 3, 4, 5\}$.
- **NUMERATOR**: Count of `source_record_key` where $\text{rating} = k$
- **DENOMINATOR**: `NOT_APPLICABLE`
- **FORMULA**: $\text{Rating Count}_k = \text{COUNT}(\text{source\_record\_key} \mid \text{rating} = k)$
- **UNIT**: Reviews (Count per Star Level)
- **GRAIN**: Star level (1 to 5)
- **DIMENSIONS**: `rating`, `source_id`
- **FILTER_RULES**: None.
- **SOURCE_DATASET**: Validated interim datasets
- **SOURCE_FIELDS**: `rating`, `Customer Rating`
- **AUTHENTIC_DERIVED_SIMULATED**: `AUTHENTIC_DATA`
- **DATA_SUPPORT_STATUS**: `SUPPORTED`
- **NULL_HANDLING**: 0 nulls exist.
- **EDGE_CASES**: Ratings outside [1, 5] flagged invalid.
- **EXPECTED_INTERPRETATION**: Identifies class imbalance across rating levels.
- **LIMITATION**: Static snapshot distribution.
- **RECONCILIATION_METHOD**: Sum of distribution counts equals total review volume.
- **FUTURE_VALIDATION_PHASE**: Phase 7

#### KPI-CX-04: Negative Review Rate
- **KPI_ID**: `KPI-CX-04`
- **KPI_NAME**: Negative Review Rate
- **BUSINESS_PURPOSE**: Measure percentage share of low customer ratings (1 and 2 stars).
- **STAKEHOLDER**: Head of CX, Product Quality Manager
- **BUSINESS_QUESTION**: `BQ-CX`, `BQ-PRODUCT`
- **DEFINITION**: Proportion of total reviews receiving a 1-star or 2-star rating.
- **NUMERATOR**: Count of reviews where $\text{rating} \le 2$
- **DENOMINATOR**: Total count of reviews with non-null rating
- **FORMULA**: $\text{Negative Review Rate} = \frac{\text{COUNT}(\text{rating} \le 2)}{\text{COUNT}(\text{rating})} \times 100\%$
- **UNIT**: Percentage (%)
- **GRAIN**: Platform / Category / Product / Shop level
- **DIMENSIONS**: `source_id`, `category`, `product_id`, `shop_id`
- **FILTER_RULES**: Ratings 1 and 2 classified as negative.
- **SOURCE_DATASET**: Validated interim datasets
- **SOURCE_FIELDS**: `rating`, `Customer Rating`
- **AUTHENTIC_DERIVED_SIMULATED**: `AUTHENTIC_DERIVED`
- **DATA_SUPPORT_STATUS**: `SUPPORTED`
- **NULL_HANDLING**: Non-null denominator required.
- **EDGE_CASES**: Zero total reviews yields 0%.
- **EXPECTED_INTERPRETATION**: Higher percentage indicates elevated customer dissatisfaction risk.
- **LIMITATION**: Treats 3-star reviews separately as neutral/mixed.
- **RECONCILIATION_METHOD**: $(\text{Count}_{1\star} + \text{Count}_{2\star}) / \text{Total Count}$.
- **FUTURE_VALIDATION_PHASE**: Phase 7

#### KPI-CX-05: Positive Review Rate
- **KPI_ID**: `KPI-CX-05`
- **KPI_NAME**: Positive Review Rate
- **BUSINESS_PURPOSE**: Measure percentage share of high customer ratings (4 and 5 stars).
- **STAKEHOLDER**: Head of CX, Category Manager
- **BUSINESS_QUESTION**: `BQ-CX`
- **DEFINITION**: Proportion of total reviews receiving a 4-star or 5-star rating.
- **NUMERATOR**: Count of reviews where $\text{rating} \ge 4$
- **DENOMINATOR**: Total count of reviews with non-null rating
- **FORMULA**: $\text{Positive Review Rate} = \frac{\text{COUNT}(\text{rating} \ge 4)}{\text{COUNT}(\text{rating})} \times 100\%$
- **UNIT**: Percentage (%)
- **GRAIN**: Platform / Category / Product / Shop level
- **DIMENSIONS**: `source_id`, `category`, `product_id`, `shop_id`
- **FILTER_RULES**: Ratings 4 and 5 classified as positive.
- **SOURCE_DATASET**: Validated interim datasets
- **SOURCE_FIELDS**: `rating`, `Customer Rating`
- **AUTHENTIC_DERIVED_SIMULATED**: `AUTHENTIC_DERIVED`
- **DATA_SUPPORT_STATUS**: `SUPPORTED`
- **NULL_HANDLING**: Non-null denominator required.
- **EDGE_CASES**: Zero total reviews yields 0%.
- **EXPECTED_INTERPRETATION**: Higher percentage indicates strong customer satisfaction.
- **LIMITATION**: Skewed high by standard e-commerce rating habits.
- **RECONCILIATION_METHOD**: $(\text{Count}_{4\star} + \text{Count}_{5\star}) / \text{Total Count}$.
- **FUTURE_VALIDATION_PHASE**: Phase 7

#### KPI-CX-06: Sentiment Class Share (Source A Benchmark)
- **KPI_ID**: `KPI-CX-06`
- **KPI_NAME**: Sentiment Class Share (Source A Benchmark)
- **BUSINESS_PURPOSE**: Measure percentage distribution of research-annotated Positive vs Negative sentiment labels.
- **STAKEHOLDER**: Head of CX, Data Science Team
- **BUSINESS_QUESTION**: `BQ-CX`, `BQ-MODEL`
- **DEFINITION**: Percentage share of records labeled Positive or Negative in Source A.
- **NUMERATOR**: Count of reviews for specific `Sentiment` label class
- **DENOMINATOR**: Total count of Source A records (5,400)
- **FORMULA**: $\text{Sentiment Share}_c = \frac{\text{COUNT}(\text{Sentiment} = c)}{5400} \times 100\%$
- **UNIT**: Percentage (%)
- **GRAIN**: Class level (`Positive`, `Negative`)
- **DIMENSIONS**: `Sentiment`, `Category`
- **FILTER_RULES**: Applies to Source A (`SRC_PRDECT_ID_V1`) only.
- **SOURCE_DATASET**: `prdect_reviews_standardized.csv`
- **SOURCE_FIELDS**: `Sentiment`
- **AUTHENTIC_DERIVED_SIMULATED**: `AUTHENTIC_DATA`
- **DATA_SUPPORT_STATUS**: `SUPPORTED_SOURCE_A_ONLY`
- **NULL_HANDLING**: 0 nulls exist in Source A.
- **EDGE_CASES**: Unavailable for Source B.
- **EXPECTED_INTERPRETATION**: Source A contains 2,416 Negative (44.7%) and 2,984 Positive (55.3%) reviews.
- **LIMITATION**: Source A exclusive benchmark label.
- **RECONCILIATION_METHOD**: Sum of Positive % + Negative % = 100.0%.
- **FUTURE_VALIDATION_PHASE**: Phase 7 & Phase 8

#### KPI-CX-07: Emotion Class Share (Source A Benchmark)
- **KPI_ID**: `KPI-CX-07`
- **KPI_NAME**: Emotion Class Share (Source A Benchmark)
- **BUSINESS_PURPOSE**: Measure percentage distribution of research-annotated 5-class emotion labels in Source A.
- **STAKEHOLDER**: Head of CX, Data Science Team
- **BUSINESS_QUESTION**: `BQ-CX`, `BQ-MODEL`
- **DEFINITION**: Percentage share of records labeled Happy, Sadness, Fear, Love, or Anger in Source A.
- **NUMERATOR**: Count of reviews for specific `Emotion` label class
- **DENOMINATOR**: Total count of Source A records (5,400)
- **FORMULA**: $\text{Emotion Share}_e = \frac{\text{COUNT}(\text{Emotion} = e)}{5400} \times 100\%$
- **UNIT**: Percentage (%)
- **GRAIN**: Emotion class level (5 classes)
- **DIMENSIONS**: `Emotion`, `Customer Rating`
- **FILTER_RULES**: Applies to Source A only.
- **SOURCE_DATASET**: `prdect_reviews_standardized.csv`
- **SOURCE_FIELDS**: `Emotion`
- **AUTHENTIC_DERIVED_SIMULATED**: `AUTHENTIC_DATA`
- **DATA_SUPPORT_STATUS**: `SUPPORTED_SOURCE_A_ONLY`
- **NULL_HANDLING**: 0 nulls exist in Source A.
- **EDGE_CASES**: Unavailable for Source B.
- **EXPECTED_INTERPRETATION**: Measures fine-grained emotion distribution across reviews.
- **LIMITATION**: Source A exclusive benchmark label.
- **RECONCILIATION_METHOD**: Sum of all 5 emotion class shares = 100.0%.
- **FUTURE_VALIDATION_PHASE**: Phase 7 & Phase 8

---

### Domain 2: Product & Category Quality KPIs

#### KPI-PRD-01: Product Review Volume (Source B)
- **KPI_ID**: `KPI-PRD-01`
- **KPI_NAME**: Product Review Volume (Source B)
- **BUSINESS_PURPOSE**: Measure total review count per specific product listing identifier.
- **STAKEHOLDER**: Product Quality Manager, Category Manager
- **BUSINESS_QUESTION**: `BQ-PRODUCT`
- **DEFINITION**: Total count of customer review records for a given `product_id`.
- **NUMERATOR**: Count of `source_record_key` where $\text{product\_id} = p$
- **DENOMINATOR**: `NOT_APPLICABLE`
- **FORMULA**: $\text{Product Review Volume}_p = \text{COUNT}(\text{source\_record\_key} \mid \text{product\_id} = p)$
- **UNIT**: Reviews (Count per Product Listing)
- **GRAIN**: Product Listing level (`product_id`)
- **DIMENSIONS**: `product_id`, `product_name`, `category`
- **FILTER_RULES**: Source B records only.
- **SOURCE_DATASET**: `tokopedia_reviews_2019_standardized.csv`
- **SOURCE_FIELDS**: `product_id`, `source_record_key`
- **AUTHENTIC_DERIVED_SIMULATED**: `AUTHENTIC_DATA`
- **DATA_SUPPORT_STATUS**: `SUPPORTED_SOURCE_B_ONLY`
- **NULL_HANDLING**: 0 null `product_id` values.
- **EDGE_CASES**: Products with $< 5$ reviews flagged as low-sample.
- **EXPECTED_INTERPRETATION**: Higher volume improves statistical confidence in product rating.
- **LIMITATION**: Evaluates listing-level `product_id` (3,664 products).
- **RECONCILIATION_METHOD**: Sum of product volumes equals Source B row count (40,607).
- **FUTURE_VALIDATION_PHASE**: Phase 7

#### KPI-PRD-02: Product Average Rating (Source B)
- **KPI_ID**: `KPI-PRD-02`
- **KPI_NAME**: Product Average Rating (Source B)
- **BUSINESS_PURPOSE**: Measure mean star rating for a specific product listing.
- **STAKEHOLDER**: Product Quality Manager
- **BUSINESS_QUESTION**: `BQ-PRODUCT`
- **DEFINITION**: Mean rating of reviews for a given `product_id`.
- **NUMERATOR**: Sum of `rating` for product $p$
- **DENOMINATOR**: Count of `rating` for product $p$
- **FORMULA**: $\text{Product Avg Rating}_p = \frac{\sum \text{rating}_p}{\text{COUNT}(\text{rating}_p)}$
- **UNIT**: Star Rating (1.0 to 5.0 scale)
- **GRAIN**: Product Listing level (`product_id`)
- **DIMENSIONS**: `product_id`, `product_name`
- **FILTER_RULES**: Source B records only.
- **SOURCE_DATASET**: `tokopedia_reviews_2019_standardized.csv`
- **SOURCE_FIELDS**: `product_id`, `rating`
- **AUTHENTIC_DERIVED_SIMULATED**: `AUTHENTIC_DATA`
- **DATA_SUPPORT_STATUS**: `SUPPORTED_SOURCE_B_ONLY`
- **NULL_HANDLING**: 0 null ratings exist.
- **EDGE_CASES**: Products with single review have equal mean and raw rating.
- **EXPECTED_INTERPRETATION**: Lower mean rating indicates product quality risk.
- **LIMITATION**: Applies to Source B listings.
- **RECONCILIATION_METHOD**: Computed via SQL `GROUP BY product_id`.
- **FUTURE_VALIDATION_PHASE**: Phase 7

#### KPI-PRD-03: Product Negative Review Rate (Source B)
- **KPI_ID**: `KPI-PRD-03`
- **KPI_NAME**: Product Negative Review Rate (Source B)
- **BUSINESS_PURPOSE**: Measure percentage share of 1-star and 2-star reviews for a specific product listing.
- **STAKEHOLDER**: Product Quality Manager
- **BUSINESS_QUESTION**: `BQ-PRODUCT`
- **DEFINITION**: Proportion of product reviews with rating $\le 2$.
- **NUMERATOR**: Count of reviews for product $p$ where $\text{rating} \le 2$
- **DENOMINATOR**: Total count of reviews for product $p$
- **FORMULA**: $\text{Product Neg Rate}_p = \frac{\text{COUNT}(\text{rating}_p \le 2)}{\text{COUNT}(\text{rating}_p)} \times 100\%$
- **UNIT**: Percentage (%)
- **GRAIN**: Product Listing level (`product_id`)
- **DIMENSIONS**: `product_id`, `product_name`, `category`
- **FILTER_RULES**: Source B records only.
- **SOURCE_DATASET**: `tokopedia_reviews_2019_standardized.csv`
- **SOURCE_FIELDS**: `product_id`, `rating`
- **AUTHENTIC_DERIVED_SIMULATED**: `AUTHENTIC_DERIVED`
- **DATA_SUPPORT_STATUS**: `SUPPORTED_SOURCE_B_ONLY`
- **NULL_HANDLING**: Non-null product review volume required.
- **EDGE_CASES**: 0 negative reviews yields 0.0%.
- **EXPECTED_INTERPRETATION**: Ranks products by defect/dissatisfaction density.
- **LIMITATION**: Small review volumes yield volatile percentage rates.
- **RECONCILIATION_METHOD**: SQL product aggregation.
- **FUTURE_VALIDATION_PHASE**: Phase 7

#### KPI-CAT-01: Category Review Volume
- **KPI_ID**: `KPI-CAT-01`
- **KPI_NAME**: Category Review Volume
- **BUSINESS_PURPOSE**: Measure total customer review volume per product category group.
- **STAKEHOLDER**: Category Manager, Product Quality Manager
- **BUSINESS_QUESTION**: `BQ-PRODUCT`
- **DEFINITION**: Total count of review records belonging to a category.
- **NUMERATOR**: Count of `source_record_key` for category $c$
- **DENOMINATOR**: `NOT_APPLICABLE`
- **FORMULA**: $\text{Category Volume}_c = \text{COUNT}(\text{source\_record\_key} \mid \text{category} = c)$
- **UNIT**: Reviews (Count per Category)
- **GRAIN**: Category level
- **DIMENSIONS**: `category_raw`, `canonical_category_family`, `source_id`
- **FILTER_RULES**: None.
- **SOURCE_DATASET**: Validated interim datasets
- **SOURCE_FIELDS**: `Category`, `category`
- **AUTHENTIC_DERIVED_SIMULATED**: `AUTHENTIC_DATA`
- **DATA_SUPPORT_STATUS**: `SUPPORTED`
- **NULL_HANDLING**: 0 null category values in raw data.
- **EDGE_CASES**: Unmapped categories grouped under `UNMAPPED`.
- **EXPECTED_INTERPRETATION**: Measures marketplace review volume distribution across categories.
- **LIMITATION**: Source A has 29 categories; Source B has 5 categories.
- **RECONCILIATION_METHOD**: Sum across categories equals dataset total.
- **FUTURE_VALIDATION_PHASE**: Phase 7

#### KPI-CAT-02: Category Average Rating
- **KPI_ID**: `KPI-CAT-02`
- **KPI_NAME**: Category Average Rating
- **BUSINESS_PURPOSE**: Measure mean customer star rating per product category.
- **STAKEHOLDER**: Category Manager, Head of CX
- **BUSINESS_QUESTION**: `BQ-PRODUCT`
- **DEFINITION**: Arithmetic mean of review ratings within a category.
- **NUMERATOR**: Sum of ratings in category $c$
- **DENOMINATOR**: Count of ratings in category $c$
- **FORMULA**: $\text{Category Avg Rating}_c = \frac{\sum \text{rating}_c}{\text{COUNT}(\text{rating}_c)}$
- **UNIT**: Star Rating (1.0 to 5.0 scale)
- **GRAIN**: Category level
- **DIMENSIONS**: `category_raw`, `canonical_category_family`
- **FILTER_RULES**: None.
- **SOURCE_DATASET**: Validated interim datasets
- **SOURCE_FIELDS**: `rating`, `Category`, `category`
- **AUTHENTIC_DERIVED_SIMULATED**: `AUTHENTIC_DATA`
- **DATA_SUPPORT_STATUS**: `SUPPORTED`
- **NULL_HANDLING**: 0 null ratings.
- **EDGE_CASES**: Categories with low volume marked low-sample.
- **EXPECTED_INTERPRETATION**: Compares baseline customer satisfaction across product categories.
- **LIMITATION**: Category rating distributions vary by product type.
- **RECONCILIATION_METHOD**: SQL category aggregation.
- **FUTURE_VALIDATION_PHASE**: Phase 7

#### KPI-CAT-03: Category Negative Review Rate
- **KPI_ID**: `KPI-CAT-03`
- **KPI_NAME**: Category Negative Review Rate
- **BUSINESS_PURPOSE**: Measure percentage share of negative reviews (1-2 stars) within a product category.
- **STAKEHOLDER**: Category Manager, Product Quality Manager
- **BUSINESS_QUESTION**: `BQ-PRODUCT`
- **DEFINITION**: Proportion of category reviews receiving ratings $\le 2$.
- **NUMERATOR**: Count of reviews in category $c$ with $\text{rating} \le 2$
- **DENOMINATOR**: Total count of reviews in category $c$
- **FORMULA**: $\text{Category Neg Rate}_c = \frac{\text{COUNT}(\text{rating}_c \le 2)}{\text{COUNT}(\text{rating}_c)} \times 100\%$
- **UNIT**: Percentage (%)
- **GRAIN**: Category level
- **DIMENSIONS**: `category_raw`, `canonical_category_family`
- **FILTER_RULES**: Ratings 1 and 2 classified as negative.
- **SOURCE_DATASET**: Validated interim datasets
- **SOURCE_FIELDS**: `rating`, `category`
- **AUTHENTIC_DERIVED_SIMULATED**: `AUTHENTIC_DERIVED`
- **DATA_SUPPORT_STATUS**: `SUPPORTED`
- **NULL_HANDLING**: Non-null denominator required.
- **EDGE_CASES**: Zero negative reviews yields 0.0%.
- **EXPECTED_INTERPRETATION**: Highlights categories with elevated customer complaint density.
- **LIMITATION**: Aggregate category measure.
- **RECONCILIATION_METHOD**: SQL category aggregation.
- **FUTURE_VALIDATION_PHASE**: Phase 7

---

### Domain 3: Shop Review Intelligence KPIs (Source B)

#### KPI-SHP-01: Shop Review Volume (Source B)
- **KPI_ID**: `KPI-SHP-01`
- **KPI_NAME**: Shop Review Volume (Source B)
- **BUSINESS_PURPOSE**: Measure total customer review count hosted by a specific merchant shop.
- **STAKEHOLDER**: Seller / Shop Operations, BI / Data Analyst
- **BUSINESS_QUESTION**: `BQ-SHOP`
- **DEFINITION**: Total count of customer review records associated with a `shop_id`.
- **NUMERATOR**: Count of `source_record_key` where $\text{shop\_id} = s$
- **DENOMINATOR**: `NOT_APPLICABLE`
- **FORMULA**: $\text{Shop Review Volume}_s = \text{COUNT}(\text{source\_record\_key} \mid \text{shop\_id} = s)$
- **UNIT**: Reviews (Count per Shop)
- **GRAIN**: Merchant Shop level (`shop_id`)
- **DIMENSIONS**: `shop_id`
- **FILTER_RULES**: Applies to Source B (158 shops).
- **SOURCE_DATASET**: `tokopedia_reviews_2019_standardized.csv`
- **SOURCE_FIELDS**: `shop_id`, `source_record_key`
- **AUTHENTIC_DERIVED_SIMULATED**: `AUTHENTIC_DATA`
- **DATA_SUPPORT_STATUS**: `SUPPORTED_SOURCE_B_ONLY`
- **NULL_HANDLING**: 0 null `shop_id` values.
- **EDGE_CASES**: Shops host between 1 and 350 product listings.
- **EXPECTED_INTERPRETATION**: Evaluates shop review activity volume.
- **LIMITATION**: Evaluated as Shop-Level Review Intelligence, not overall seller operational performance.
- **RECONCILIATION_METHOD**: Sum across 158 shops equals 40,607 rows.
- **FUTURE_VALIDATION_PHASE**: Phase 7

#### KPI-SHP-02: Shop Average Star Rating (Source B)
- **KPI_ID**: `KPI-SHP-02`
- **KPI_NAME**: Shop Average Star Rating (Source B)
- **BUSINESS_PURPOSE**: Measure mean customer star rating across all reviews received by a shop.
- **STAKEHOLDER**: Seller / Shop Operations
- **BUSINESS_QUESTION**: `BQ-SHOP`
- **DEFINITION**: Arithmetic mean of ratings for reviews belonging to `shop_id`.
- **NUMERATOR**: Sum of `rating` for shop $s$
- **DENOMINATOR**: Count of `rating` for shop $s$
- **FORMULA**: $\text{Shop Avg Rating}_s = \frac{\sum \text{rating}_s}{\text{COUNT}(\text{rating}_s)}$
- **UNIT**: Star Rating (1.0 to 5.0 scale)
- **GRAIN**: Merchant Shop level (`shop_id`)
- **DIMENSIONS**: `shop_id`
- **FILTER_RULES**: Source B records only.
- **SOURCE_DATASET**: `tokopedia_reviews_2019_standardized.csv`
- **SOURCE_FIELDS**: `shop_id`, `rating`
- **AUTHENTIC_DERIVED_SIMULATED**: `AUTHENTIC_DATA`
- **DATA_SUPPORT_STATUS**: `SUPPORTED_SOURCE_B_ONLY`
- **NULL_HANDLING**: 0 null ratings.
- **EDGE_CASES**: Shops with single review have mean equal to raw rating.
- **EXPECTED_INTERPRETATION**: Lower shop average rating indicates merchant review risk.
- **LIMITATION**: Applies strictly to Source B shops.
- **RECONCILIATION_METHOD**: SQL shop aggregation.
- **FUTURE_VALIDATION_PHASE**: Phase 7

#### KPI-SHP-03: Shop Negative Review Rate (Source B)
- **KPI_ID**: `KPI-SHP-03`
- **KPI_NAME**: Shop Negative Review Rate (Source B)
- **BUSINESS_PURPOSE**: Measure percentage share of negative reviews (1-2 stars) received by a shop.
- **STAKEHOLDER**: Seller / Shop Operations
- **BUSINESS_QUESTION**: `BQ-SHOP`
- **DEFINITION**: Proportion of shop reviews receiving ratings $\le 2$.
- **NUMERATOR**: Count of reviews for shop $s$ where $\text{rating} \le 2$
- **DENOMINATOR**: Total count of reviews for shop $s$
- **FORMULA**: $\text{Shop Neg Rate}_s = \frac{\text{COUNT}(\text{rating}_s \le 2)}{\text{COUNT}(\text{rating}_s)} \times 100\%$
- **UNIT**: Percentage (%)
- **GRAIN**: Merchant Shop level (`shop_id`)
- **DIMENSIONS**: `shop_id`
- **FILTER_RULES**: Source B records only.
- **SOURCE_DATASET**: `tokopedia_reviews_2019_standardized.csv`
- **SOURCE_FIELDS**: `shop_id`, `rating`
- **AUTHENTIC_DERIVED_SIMULATED**: `AUTHENTIC_DERIVED`
- **DATA_SUPPORT_STATUS**: `SUPPORTED_SOURCE_B_ONLY`
- **NULL_HANDLING**: Non-null review count required.
- **EDGE_CASES**: 0 negative reviews yields 0.0%.
- **EXPECTED_INTERPRETATION**: Pinpoints merchant shops with high customer complaint ratios.
- **LIMITATION**: Evaluates review signals only.
- **RECONCILIATION_METHOD**: SQL shop aggregation.
- **FUTURE_VALIDATION_PHASE**: Phase 7

#### KPI-SHP-04: Shop Product Listing Coverage (Source B)
- **KPI_ID**: `KPI-SHP-04`
- **KPI_NAME**: Shop Product Listing Coverage (Source B)
- **BUSINESS_PURPOSE**: Measure total count of distinct product listings hosted by a merchant shop.
- **STAKEHOLDER**: Seller / Shop Operations, BI / Data Analyst
- **BUSINESS_QUESTION**: `BQ-SHOP`
- **DEFINITION**: Count of unique `product_id` listings mapped to `shop_id`.
- **NUMERATOR**: Count of distinct `product_id` for shop $s$
- **DENOMINATOR**: `NOT_APPLICABLE`
- **FORMULA**: $\text{Shop Product Coverage}_s = \text{COUNT}(\text{DISTINCT product\_id} \mid \text{shop\_id} = s)$
- **UNIT**: Product Listings (Count per Shop)
- **GRAIN**: Merchant Shop level (`shop_id`)
- **DIMENSIONS**: `shop_id`
- **FILTER_RULES**: Source B records only.
- **SOURCE_DATASET**: `tokopedia_reviews_2019_standardized.csv`
- **SOURCE_FIELDS**: `shop_id`, `product_id`
- **AUTHENTIC_DERIVED_SIMULATED**: `AUTHENTIC_DATA`
- **DATA_SUPPORT_STATUS**: `SUPPORTED_SOURCE_B_ONLY`
- **NULL_HANDLING**: 0 null product_ids.
- **EDGE_CASES**: Shops host between 1 and 350 distinct products.
- **EXPECTED_INTERPRETATION**: Measures merchant shop catalog breadth in dataset.
- **LIMITATION**: Catalog size in dataset.
- **RECONCILIATION_METHOD**: Sum of distinct products across shops equals 3,664.
- **FUTURE_VALIDATION_PHASE**: Phase 7

---

### Domain 4: Issue Intelligence KPIs (Conditional)

#### KPI-ISS-01: Candidate Issue Theme Frequency (Conditional)
- **KPI_ID**: `KPI-ISS-01`
- **KPI_NAME**: Candidate Issue Theme Frequency (Conditional)
- **BUSINESS_PURPOSE**: Measure total occurrence count of specific candidate issue themes in review text.
- **STAKEHOLDER**: Product Quality Manager, Data Science Team
- **BUSINESS_QUESTION**: `BQ-ISSUE`
- **DEFINITION**: Total count of customer reviews containing keywords/labels for issue theme $k$.
- **NUMERATOR**: Count of reviews matching candidate issue theme $k$
- **DENOMINATOR**: `NOT_APPLICABLE`
- **FORMULA**: $\text{Issue Frequency}_k = \text{COUNT}(\text{source\_record\_key} \mid \text{Issue}_k = 1)$
- **UNIT**: Reviews (Count per Issue Theme)
- **GRAIN**: Issue Theme level
- **DIMENSIONS**: `issue_theme_candidate`, `category`
- **FILTER_RULES**: Unsupervised text discovery active; supervised classification conditional.
- **SOURCE_DATASET**: Review text strings
- **SOURCE_FIELDS**: `Customer Review`, `text`
- **AUTHENTIC_DERIVED_SIMULATED**: `AUTHENTIC_TEXT_DERIVED`
- **DATA_SUPPORT_STATUS**: `CONDITIONAL_PENDING_PHASE_9`
- **NULL_HANDLING**: Non-blank text required.
- **EDGE_CASES**: Multi-label reviews may match multiple issue themes.
- **EXPECTED_INTERPRETATION**: Identifies most frequent complaint drivers.
- **LIMITATION**: Conditional on Phase 9 human annotation protocol ($N=1,000$).
- **RECONCILIATION_METHOD**: Evaluated against Phase 9 gold annotations.
- **FUTURE_VALIDATION_PHASE**: Phase 9

#### KPI-ISS-02: Candidate Issue Rate (Conditional)
- **KPI_ID**: `KPI-ISS-02`
- **KPI_NAME**: Candidate Issue Rate (Conditional)
- **BUSINESS_PURPOSE**: Measure percentage share of total reviews associated with specific issue themes.
- **STAKEHOLDER**: Product Quality Manager
- **BUSINESS_QUESTION**: `BQ-ISSUE`
- **DEFINITION**: Proportion of total reviews exhibiting candidate issue theme $k$.
- **NUMERATOR**: Count of reviews matching issue theme $k$
- **DENOMINATOR**: Total count of reviews analyzed
- **FORMULA**: $\text{Issue Rate}_k = \frac{\text{COUNT}(\text{Issue}_k = 1)}{\text{Total Reviews}} \times 100\%$
- **UNIT**: Percentage (%)
- **GRAIN**: Issue Theme level / Category level
- **DIMENSIONS**: `issue_theme_candidate`, `category`
- **FILTER_RULES**: Applies to analyzed review subset.
- **SOURCE_DATASET**: Review text strings
- **SOURCE_FIELDS**: `Customer Review`, `text`
- **AUTHENTIC_DERIVED_SIMULATED**: `AUTHENTIC_TEXT_DERIVED`
- **DATA_SUPPORT_STATUS**: `CONDITIONAL_PENDING_PHASE_9`
- **NULL_HANDLING**: Non-null denominator required.
- **EDGE_CASES**: Multi-label percentage sum may exceed 100%.
- **EXPECTED_INTERPRETATION**: Measures prevalence of specific complaint themes.
- **LIMITATION**: Conditional on Phase 9 human annotation.
- **RECONCILIATION_METHOD**: Evaluated against Phase 9 gold annotations.
- **FUTURE_VALIDATION_PHASE**: Phase 9

---

### Domain 5: Decision Support & Workflow Simulation KPIs

#### KPI-DSS-01: Priority Review Case Count
- **KPI_ID**: `KPI-DSS-01`
- **KPI_NAME**: Priority Review Case Count
- **BUSINESS_PURPOSE**: Measure total count of reviews flagged for priority human review ($\text{Priority Score} \ge 75$).
- **STAKEHOLDER**: Customer Service Manager, Management User
- **BUSINESS_QUESTION**: `BQ-DSS`
- **DEFINITION**: Total count of review records receiving priority score $\ge 75$.
- **NUMERATOR**: Count of reviews where $\text{Priority Score} \ge 75$
- **DENOMINATOR**: `NOT_APPLICABLE`
- **FORMULA**: $\text{Priority Case Count} = \text{COUNT}(\text{source\_record\_key} \mid \text{Priority Score} \ge 75)$
- **UNIT**: Review Cases (Count)
- **GRAIN**: Priority Queue level
- **DIMENSIONS**: `priority_tier`, `rating`, `category`
- **FILTER_RULES**: Flagged high-priority cases.
- **SOURCE_DATASET**: Derived priority score outputs
- **SOURCE_FIELDS**: `priority_score`, `source_record_key`
- **AUTHENTIC_DERIVED_SIMULATED**: `AUTHENTIC_DERIVED_MODEL_OUTPUT`
- **DATA_SUPPORT_STATUS**: `SUPPORTED_VIA_ANALYTICAL_MODEL`
- **NULL_HANDLING**: 0 null priority scores.
- **EDGE_CASES**: Threshold parameter configurable in Phase 10.
- **EXPECTED_INTERPRETATION**: Quantifies operational workload for priority CS escalation.
- **LIMITATION**: Exact scoring formula parameters finalized in Phase 10.
- **RECONCILIATION_METHOD**: Count of rows in priority decision queue.
- **FUTURE_VALIDATION_PHASE**: Phase 10

#### KPI-DSS-02: Critical Review Recall (Future Candidate)
- **KPI_ID**: `KPI-DSS-02`
- **KPI_NAME**: Critical Review Recall (Future Candidate)
- **BUSINESS_PURPOSE**: Measure proportion of severe customer complaint cases successfully captured in the priority queue.
- **STAKEHOLDER**: Customer Service Manager, Data Science Team
- **BUSINESS_QUESTION**: `BQ-DSS`
- **DEFINITION**: Proportion of actual severe reviews captured in top-K priority queue.
- **NUMERATOR**: Count of severe reviews present in priority queue
- **DENOMINATOR**: Total count of actual severe reviews
- **FORMULA**: $\text{Critical Recall} = \frac{\text{COUNT}(\text{Severe} \cap \text{Priority Queue})}{\text{COUNT}(\text{Severe})} \times 100\%$
- **UNIT**: Percentage (%)
- **GRAIN**: Priority Queue level
- **DIMENSIONS**: `priority_score`, `severity_level`
- **FILTER_RULES**: Defined during Phase 10 evaluation.
- **SOURCE_DATASET**: Priority queue evaluation logs
- **SOURCE_FIELDS**: `priority_score`, `gold_severity_flag`
- **AUTHENTIC_DERIVED_SIMULATED**: `AUTHENTIC_DERIVED_EVALUATION`
- **DATA_SUPPORT_STATUS**: `FUTURE_DSS_KPI`
- **NULL_HANDLING**: Non-null denominator required.
- **EDGE_CASES**: Requires ground truth severity definitions in Phase 10.
- **EXPECTED_INTERPRETATION**: Higher recall ensures fewer critical complaints are missed.
- **LIMITATION**: Target threshold set as `TARGET_THRESHOLD = TO_BE_DETERMINED_IN_PHASE_4`.
- **RECONCILIATION_METHOD**: Evaluated on Phase 10 test split.
- **FUTURE_VALIDATION_PHASE**: Phase 10

#### KPI-DSS-03: Priority Queue Precision (Future Candidate)
- **KPI_ID**: `KPI-DSS-03`
- **KPI_NAME**: Priority Queue Precision (Future Candidate)
- **BUSINESS_PURPOSE**: Measure proportion of prioritized queue cases that represent genuine high-severity complaints.
- **STAKEHOLDER**: Customer Service Manager
- **BUSINESS_QUESTION**: `BQ-DSS`
- **DEFINITION**: Proportion of top-K priority queue records that match severe complaint criteria.
- **NUMERATOR**: Count of genuine severe complaints in top-K queue
- **DENOMINATOR**: Total count of records in top-K queue ($K$)
- **FORMULA**: $\text{Top-K Precision} = \frac{\text{COUNT}(\text{Severe} \cap \text{Top-K Queue})}{K} \times 100\%$
- **UNIT**: Percentage (%)
- **GRAIN**: Top-K Queue level ($K = 50$)
- **DIMENSIONS**: `priority_rank`
- **FILTER_RULES**: Top-K items ($K=50$).
- **SOURCE_DATASET**: Priority queue evaluation logs
- **SOURCE_FIELDS**: `priority_rank`, `gold_severity_flag`
- **AUTHENTIC_DERIVED_SIMULATED**: `AUTHENTIC_DERIVED_EVALUATION`
- **DATA_SUPPORT_STATUS**: `FUTURE_DSS_KPI`
- **NULL_HANDLING**: Non-null denominator required.
- **EDGE_CASES**: Evaluated for $K=50$ top priority cases.
- **EXPECTED_INTERPRETATION**: Higher precision minimizes false alarm reviews for CS agents.
- **LIMITATION**: Target threshold set as `TARGET_THRESHOLD = TO_BE_DETERMINED_IN_PHASE_4`.
- **RECONCILIATION_METHOD**: Evaluated on Phase 10 test split.
- **FUTURE_VALIDATION_PHASE**: Phase 10

#### KPI-DSS-04: Simulated Ticket Dispatch Count (Track B)
- **KPI_ID**: `KPI-DSS-04`
- **KPI_NAME**: Simulated Ticket Dispatch Count (Track B)
- **BUSINESS_PURPOSE**: Measure total count of simulated CS tickets dispatched via webhook integration.
- **STAKEHOLDER**: CS Manager, Data Governance / Engineering
- **BUSINESS_QUESTION**: `BQ-DSS`
- **DEFINITION**: Count of simulated ticket payloads dispatched to n8n webhook endpoint.
- **NUMERATOR**: Count of webhook dispatches with HTTP 200/202 status
- **DENOMINATOR**: `NOT_APPLICABLE`
- **FORMULA**: $\text{Simulated Dispatch Count} = \text{COUNT}(\text{simulated\_ticket\_id} \mid \text{dispatch\_status} = \text{SUCCESS})$
- **UNIT**: Webhook Dispatches (Count)
- **GRAIN**: Webhook Dispatch Event level
- **DIMENSIONS**: `scenario_version`, `dispatch_status`
- **FILTER_RULES**: Requires `is_synthetic = TRUE`.
- **SOURCE_DATASET**: Simulated webhook audit log
- **SOURCE_FIELDS**: `simulated_ticket_id`, `is_synthetic`, `scenario_version`
- **AUTHENTIC_DERIVED_SIMULATED**: `SIMULATED_OPERATIONAL_ONLY`
- **DATA_SUPPORT_STATUS**: `SUPPORTED_AS_SIMULATION_ONLY`
- **NULL_HANDLING**: All dispatches must carry `is_synthetic = TRUE`.
- **EDGE_CASES**: Simulated dispatches carry `SIMULATED_OPERATIONAL_EVENT_TIME`.
- **EXPECTED_INTERPRETATION**: Measures operational workflow simulation throughput.
- **LIMITATION**: Purely synthetic simulation logs; zero connection to live Tokopedia systems.
- **RECONCILIATION_METHOD**: Audit log count.
- **FUTURE_VALIDATION_PHASE**: Phase 11

---

### Domain 6: ML Model Governance KPIs

#### KPI-MDL-01: Rating Model Accuracy
- **KPI_ID**: `KPI-MDL-01`
- **KPI_NAME**: Rating Model Accuracy
- **BUSINESS_PURPOSE**: Measure overall proportion of correctly predicted star ratings (1 to 5).
- **STAKEHOLDER**: Data Science Team, Governance Reviewer
- **BUSINESS_QUESTION**: `BQ-MODEL`
- **DEFINITION**: Proportion of test set review records where predicted rating equals actual rating.
- **NUMERATOR**: Count of correct rating predictions ($\hat{y}_i = y_i$)
- **DENOMINATOR**: Total count of test set records
- **FORMULA**: $\text{Accuracy} = \frac{\sum_{i=1}^N \mathbb{I}(\hat{y}_i = y_i)}{N}$
- **UNIT**: Ratio / Percentage
- **GRAIN**: Model Run level
- **DIMENSIONS**: `model_id`, `target_task`
- **FILTER_RULES**: Evaluated on test split.
- **SOURCE_DATASET**: `mart_model_governance_eval`
- **SOURCE_FIELDS**: `y_true`, `y_pred`
- **AUTHENTIC_DERIVED_SIMULATED**: `AUTHENTIC_DERIVED_EVALUATION`
- **DATA_SUPPORT_STATUS**: `SUPPORTED`
- **NULL_HANDLING**: Non-null test records.
- **EDGE_CASES**: Evaluated alongside Macro F1 to account for class imbalance.
- **EXPECTED_INTERPRETATION**: Overall classification accuracy.
- **LIMITATION**: Target threshold set as `TARGET_THRESHOLD = TO_BE_DETERMINED_IN_PHASE_4`.
- **RECONCILIATION_METHOD**: Computed on test set split.
- **FUTURE_VALIDATION_PHASE**: Phase 8

#### KPI-MDL-02: Rating Model Macro F1 Score
- **KPI_ID**: `KPI-MDL-02`
- **KPI_NAME**: Rating Model Macro F1 Score
- **BUSINESS_PURPOSE**: Measure unweighted mean F1 score across all 5 star rating classes to evaluate performance on minority rating classes.
- **STAKEHOLDER**: Data Science Team, Governance Reviewer
- **BUSINESS_QUESTION**: `BQ-MODEL`
- **DEFINITION**: Arithmetic mean of per-class F1 scores across 5 star rating classes.
- **NUMERATOR**: Sum of per-class F1 scores ($\sum_{k=1}^5 \text{F1}_k$)
- **DENOMINATOR**: Number of classes (5)
- **FORMULA**: $\text{Macro F1} = \frac{1}{5} \sum_{k=1}^5 \text{F1}_k$
- **UNIT**: Score (0.0 to 1.0)
- **GRAIN**: Model Run level
- **DIMENSIONS**: `model_id`, `target_task`
- **FILTER_RULES**: Evaluated on test split.
- **SOURCE_DATASET**: `mart_model_governance_eval`
- **SOURCE_FIELDS**: `y_true`, `y_pred`
- **AUTHENTIC_DERIVED_SIMULATED**: `AUTHENTIC_DERIVED_EVALUATION`
- **DATA_SUPPORT_STATUS**: `SUPPORTED`
- **NULL_HANDLING**: Non-null predictions required.
- **EDGE_CASES**: Prevents minority rating class underperformance from being masked by 5-star majority class.
- **EXPECTED_INTERPRETATION**: Higher Macro F1 indicates balanced classification across all star levels.
- **LIMITATION**: Target threshold set as `TARGET_THRESHOLD = TO_BE_DETERMINED_IN_PHASE_4`.
- **RECONCILIATION_METHOD**: Computed on test set split.
- **FUTURE_VALIDATION_PHASE**: Phase 8

#### KPI-MDL-03: Rating Model Weighted F1 Score
- **KPI_ID**: `KPI-MDL-03`
- **KPI_NAME**: Rating Model Weighted F1 Score
- **BUSINESS_PURPOSE**: Measure class-weighted mean F1 score accounting for rating class support volume.
- **STAKEHOLDER**: Data Science Team
- **BUSINESS_QUESTION**: `BQ-MODEL`
- **DEFINITION**: Weighted mean of per-class F1 scores weighted by class instance support $N_k$.
- **NUMERATOR**: Sum of $(N_k \times \text{F1}_k)$ across 5 classes
- **DENOMINATOR**: Total test set instances ($N$)
- **FORMULA**: $\text{Weighted F1} = \frac{\sum_{k=1}^5 N_k \cdot \text{F1}_k}{N}$
- **UNIT**: Score (0.0 to 1.0)
- **GRAIN**: Model Run level
- **DIMENSIONS**: `model_id`, `target_task`
- **FILTER_RULES**: Evaluated on test split.
- **SOURCE_DATASET**: `mart_model_governance_eval`
- **SOURCE_FIELDS**: `y_true`, `y_pred`
- **AUTHENTIC_DERIVED_SIMULATED**: `AUTHENTIC_DERIVED_EVALUATION`
- **DATA_SUPPORT_STATUS**: `SUPPORTED`
- **NULL_HANDLING**: Non-null test records.
- **EDGE_CASES**: Evaluated alongside Macro F1.
- **EXPECTED_INTERPRETATION**: Measures overall weighted classification efficacy.
- **LIMITATION**: Target threshold set as `TARGET_THRESHOLD = TO_BE_DETERMINED_IN_PHASE_4`.
- **RECONCILIATION_METHOD**: Computed on test set split.
- **FUTURE_VALIDATION_PHASE**: Phase 8

#### KPI-MDL-04: Quadratic Weighted Kappa (QWK)
- **KPI_ID**: `KPI-MDL-04`
- **KPI_NAME**: Quadratic Weighted Kappa (QWK)
- **BUSINESS_PURPOSE**: Measure ordinal rating prediction agreement penalizing quadratic distance between predicted and actual star ratings.
- **STAKEHOLDER**: Data Science Team, Governance Reviewer
- **BUSINESS_QUESTION**: `BQ-MODEL`
- **DEFINITION**: Inter-rater agreement metric measuring agreement on ordinal rating scales (1 to 5 stars).
- **NUMERATOR**: Observed rating distance matrix agreement
- **DENOMINATOR**: Expected chance agreement distance matrix
- **FORMULA**: $\text{QWK} = 1 - \frac{\sum_{i,j} w_{i,j} O_{i,j}}{\sum_{i,j} w_{i,j} E_{i,j}} \quad \text{where } w_{i,j} = \frac{(i-j)^2}{(N-1)^2}$
- **UNIT**: Score (-1.0 to 1.0)
- **GRAIN**: Model Run level
- **DIMENSIONS**: `model_id`, `target_task`
- **FILTER_RULES**: Applies to ordinal 1-5 rating prediction tasks.
- **SOURCE_DATASET**: `mart_model_governance_eval`
- **SOURCE_FIELDS**: `y_true`, `y_pred`
- **AUTHENTIC_DERIVED_SIMULATED**: `AUTHENTIC_DERIVED_EVALUATION`
- **DATA_SUPPORT_STATUS**: `SUPPORTED`
- **NULL_HANDLING**: Non-null predictions required.
- **EDGE_CASES**: Penalizes misclassifying a 1-star review as 5-star far more heavily than misclassifying as 2-star.
- **EXPECTED_INTERPRETATION**: Standard metric for ordinal rating prediction tasks.
- **LIMITATION**: Target threshold set as `TARGET_THRESHOLD = TO_BE_DETERMINED_IN_PHASE_4`.
- **RECONCILIATION_METHOD**: Computed via Scikit-Learn `cohen_kappa_score(..., weights='quadratic')`.
- **FUTURE_VALIDATION_PHASE**: Phase 8

#### KPI-MDL-05: Rating Prediction Confusion Matrix
- **KPI_ID**: `KPI-MDL-05`
- **KPI_NAME**: Rating Prediction Confusion Matrix
- **BUSINESS_PURPOSE**: Provide full 5x5 contingency matrix of actual vs. predicted star ratings to inspect specific misclassification patterns.
- **STAKEHOLDER**: Data Science Team
- **BUSINESS_QUESTION**: `BQ-MODEL`
- **DEFINITION**: $5 \times 5$ matrix where cell $(i,j)$ represents count of actual class $i$ predicted as class $j$.
- **NUMERATOR**: Count of instances with actual class $i$ and predicted class $j$
- **DENOMINATOR**: `NOT_APPLICABLE`
- **FORMULA**: $C_{i,j} = \text{COUNT}(y_{\text{true}} = i \land y_{\text{pred}} = j)$
- **UNIT**: Matrix of Counts ($5 \times 5$)
- **GRAIN**: Class pair level ($i, j \in \{1..5\}$)
- **DIMENSIONS**: `actual_rating`, `predicted_rating`
- **FILTER_RULES**: Evaluated on test split.
- **SOURCE_DATASET**: `mart_model_governance_eval`
- **SOURCE_FIELDS**: `y_true`, `y_pred`
- **AUTHENTIC_DERIVED_SIMULATED**: `AUTHENTIC_DERIVED_EVALUATION`
- **DATA_SUPPORT_STATUS**: `SUPPORTED`
- **NULL_HANDLING**: 0 nulls.
- **EDGE_CASES**: Sum of all cells equals test set size.
- **EXPECTED_INTERPRETATION**: Off-diagonal elements identify specific rating confusion errors.
- **LIMITATION**: Multi-dimensional matrix representation.
- **RECONCILIATION_METHOD**: Sum of matrix equals test set size.
- **FUTURE_VALIDATION_PHASE**: Phase 8

---

### Domain 7: Data Quality & Governance KPIs

#### KPI-DQ-01: Invalid Record Count
- **KPI_ID**: `KPI-DQ-01`
- **KPI_NAME**: Invalid Record Count
- **BUSINESS_PURPOSE**: Measure total count of ingested records failing structural validation checks.
- **STAKEHOLDER**: Data Governance / Engineering
- **BUSINESS_QUESTION**: `BQ-DQ`
- **DEFINITION**: Count of rows failing data type, rating range [1,5], or mandatory field validation.
- **NUMERATOR**: Count of rows failing assertion checks
- **DENOMINATOR**: `NOT_APPLICABLE`
- **FORMULA**: $\text{Invalid Record Count} = \text{COUNT}(\text{source\_record\_key} \mid \text{validation\_status} = \text{INVALID})$
- **UNIT**: Records (Count)
- **GRAIN**: Ingestion batch level
- **DIMENSIONS**: `source_id`, `rule_failed`
- **FILTER_RULES**: Failed validation assertion checks.
- **SOURCE_DATASET**: `mart_data_pipeline_audit`
- **SOURCE_FIELDS**: `source_record_key`, `validation_status`
- **AUTHENTIC_DERIVED_SIMULATED**: `AUTHENTIC_PIPELINE_METADATA`
- **DATA_SUPPORT_STATUS**: `SUPPORTED`
- **NULL_HANDLING**: 0 null keys.
- **EDGE_CASES**: Phase 2 data hardening achieved 0 invalid records across raw datasets.
- **EXPECTED_INTERPRETATION**: 0 indicates clean ingestion pipeline.
- **LIMITATION**: None.
- **RECONCILIATION_METHOD**: Audit pipeline log count.
- **FUTURE_VALIDATION_PHASE**: Phase 6

#### KPI-DQ-02: Quarantined Record Count
- **KPI_ID**: `KPI-DQ-02`
- **KPI_NAME**: Quarantined Record Count
- **BUSINESS_PURPOSE**: Track count of records isolated in quarantine storage due to non-fatal data anomalies.
- **STAKEHOLDER**: Data Governance / Engineering
- **BUSINESS_QUESTION**: `BQ-DQ`
- **DEFINITION**: Count of rows set aside into quarantine tables for manual review.
- **NUMERATOR**: Count of quarantined rows
- **DENOMINATOR**: `NOT_APPLICABLE`
- **FORMULA**: $\text{Quarantined Count} = \text{COUNT}(\text{source\_record\_key} \mid \text{is\_quarantined} = \text{TRUE})$
- **UNIT**: Records (Count)
- **GRAIN**: Ingestion batch level
- **DIMENSIONS**: `source_id`, `quarantine_reason`
- **FILTER_RULES**: Quarantined records.
- **SOURCE_DATASET**: `mart_data_pipeline_audit`
- **SOURCE_FIELDS**: `is_quarantined`
- **AUTHENTIC_DERIVED_SIMULATED**: `AUTHENTIC_PIPELINE_METADATA`
- **DATA_SUPPORT_STATUS**: `SUPPORTED`
- **NULL_HANDLING**: 0 nulls.
- **EDGE_CASES**: Phase 2 data hardening registered 0 quarantined rows.
- **EXPECTED_INTERPRETATION**: 0 indicates zero records required quarantine isolation.
- **LIMITATION**: None.
- **RECONCILIATION_METHOD**: Audit pipeline count.
- **FUTURE_VALIDATION_PHASE**: Phase 6

#### KPI-DQ-03: Critical Null Count
- **KPI_ID**: `KPI-DQ-03`
- **KPI_NAME**: Critical Null Count
- **BUSINESS_PURPOSE**: Measure count of missing values in mandatory primary fields (review text, rating).
- **STAKEHOLDER**: Data Governance / Engineering
- **BUSINESS_QUESTION**: `BQ-DQ`
- **DEFINITION**: Count of NULL entries in critical columns (`Customer Review`, `text`, `Customer Rating`, `rating`).
- **NUMERATOR**: Count of NULLs in critical columns
- **DENOMINATOR**: `NOT_APPLICABLE`
- **FORMULA**: $\text{Critical Null Count} = \text{COUNT}(\text{NULL} \mid \text{column} \in \{\text{text}, \text{rating}\})$
- **UNIT**: Null Values (Count)
- **GRAIN**: Column level / Dataset level
- **DIMENSIONS**: `source_id`, `column_name`
- **FILTER_RULES**: Critical mandatory columns.
- **SOURCE_DATASET**: `schema_profile.csv` & validated interim datasets
- **SOURCE_FIELDS**: `null_count`
- **AUTHENTIC_DERIVED_SIMULATED**: `AUTHENTIC_PIPELINE_METADATA`
- **DATA_SUPPORT_STATUS**: `SUPPORTED`
- **NULL_HANDLING**: Explicitly tracked per column.
- **EDGE_CASES**: Source B `sold` attribute contains 14 nulls (0.0345%), explicitly registered as non-critical. Critical text/rating columns contain 0 nulls.
- **EXPECTED_INTERPRETATION**: 0 critical nulls confirms data readiness for modeling.
- **LIMITATION**: None.
- **RECONCILIATION_METHOD**: `schema_profile.csv` audit.
- **FUTURE_VALIDATION_PHASE**: Phase 6

#### KPI-DQ-04: Cross-Source Duplicate Record Count
- **KPI_ID**: `KPI-DQ-04`
- **KPI_NAME**: Cross-Source Duplicate Record Count
- **BUSINESS_PURPOSE**: Measure count of exact raw review text matches occurring across Source A and Source B.
- **STAKEHOLDER**: Data Governance / Engineering, Data Science Team
- **BUSINESS_QUESTION**: `BQ-DQ`
- **DEFINITION**: Count of review text strings appearing identically in both Source A and Source B.
- **NUMERATOR**: Count of exact text string matches between Source A and Source B
- **DENOMINATOR**: `NOT_APPLICABLE`
- **FORMULA**: $\text{Exact Overlap Count} = \text{COUNT}(t \mid t \in \text{Text}_A \land t \in \text{Text}_B)$
- **UNIT**: Duplicate Reviews (Count)
- **GRAIN**: Cross-source comparison level
- **DIMENSIONS**: `metric_name`
- **FILTER_RULES**: Exact text string comparison.
- **SOURCE_DATASET**: `cross_source_overlap.csv`
- **SOURCE_FIELDS**: `metric`, `count`
- **AUTHENTIC_DERIVED_SIMULATED**: `AUTHENTIC_DERIVED_AUDIT`
- **DATA_SUPPORT_STATUS**: `SUPPORTED`
- **NULL_HANDLING**: Non-blank text strings.
- **EDGE_CASES**: Measured as 25 exact raw text overlaps (0.463% of Source A) and 95 normalized text overlaps (1.759% of Source A).
- **EXPECTED_INTERPRETATION**: Negligible cross-source overlap confirms data source independence.
- **LIMITATION**: Flagged in dataset without deleting raw records.
- **RECONCILIATION_METHOD**: `cross_source_overlap.csv` audit output.
- **FUTURE_VALIDATION_PHASE**: Phase 6 & Phase 8

#### KPI-DQ-05: System Lineage Key Uniqueness Percentage
- **KPI_ID**: `KPI-DQ-05`
- **KPI_NAME**: System Lineage Key Uniqueness Percentage
- **BUSINESS_PURPOSE**: Verify 100% uniqueness of generated system lineage primary keys (`source_record_key`).
- **STAKEHOLDER**: Data Governance / Engineering
- **BUSINESS_QUESTION**: `BQ-DQ`
- **DEFINITION**: Percentage of distinct `source_record_key` values relative to total row count.
- **NUMERATOR**: Count of distinct `source_record_key` values
- **DENOMINATOR**: Total row count ($N$)
- **FORMULA**: $\text{Lineage Uniqueness} = \frac{\text{COUNT}(\text{DISTINCT source\_record\_key})}{N} \times 100\%$
- **UNIT**: Percentage (%)
- **GRAIN**: Dataset level
- **DIMENSIONS**: `source_id`
- **FILTER_RULES**: All ingested records.
- **SOURCE_DATASET**: Validated interim datasets
- **SOURCE_FIELDS**: `source_record_key`
- **AUTHENTIC_DERIVED_SIMULATED**: `AUTHENTIC_PIPELINE_METADATA`
- **DATA_SUPPORT_STATUS**: `SUPPORTED`
- **NULL_HANDLING**: 0 nulls permitted.
- **EDGE_CASES**: 100.0% achieved across Source A (5,400/5,400) and Source B (40,607/40,607).
- **EXPECTED_INTERPRETATION**: 100.0% confirms unique primary key generation for every row.
- **LIMITATION**: None.
- **RECONCILIATION_METHOD**: Verified via Python inspection script.
- **FUTURE_VALIDATION_PHASE**: Phase 6

#### KPI-DQ-06: Source Ingestion Reconciliation Status
- **KPI_ID**: `KPI-DQ-06`
- **KPI_NAME**: Source Ingestion Reconciliation Status
- **BUSINESS_PURPOSE**: Verify 100% row reconciliation matching parsed raw rows to staging output rows ($0$ lost rows).
- **STAKEHOLDER**: Data Governance / Engineering
- **BUSINESS_QUESTION**: `BQ-DQ`
- **DEFINITION**: Boolean equality comparison asserting $\text{Raw Rows} = \text{Staging Rows}$.
- **NUMERATOR**: Count of staging rows
- **DENOMINATOR**: Count of parsed raw rows
- **FORMULA**: $\text{Reconciliation Status} = \begin{cases} \text{PASS} & \text{if } \text{Staging Rows} = \text{Raw Rows} \\ \text{FAIL} & \text{otherwise} \end{cases}$
- **UNIT**: Boolean Status (`PASS` / `FAIL`)
- **GRAIN**: Ingestion execution batch level
- **DIMENSIONS**: `source_id`
- **FILTER_RULES**: Evaluated per source file.
- **SOURCE_DATASET**: `dataset_inventory.csv` & `mart_data_pipeline_audit`
- **SOURCE_FIELDS**: `row_count`, `acceptance_status`
- **AUTHENTIC_DERIVED_SIMULATED**: `AUTHENTIC_PIPELINE_METADATA`
- **DATA_SUPPORT_STATUS**: `SUPPORTED`
- **NULL_HANDLING**: Non-null row counts.
- **EDGE_CASES**: Source A: 5,400 raw = 5,400 staging (`PASS`); Source B: 40,607 raw = 40,607 staging (`PASS`).
- **EXPECTED_INTERPRETATION**: `PASS` proves 0 unexplained row loss during ingestion.
- **LIMITATION**: None.
- **RECONCILIATION_METHOD**: `dataset_inventory.csv` reconciliation assertion.
- **FUTURE_VALIDATION_PHASE**: Phase 6
