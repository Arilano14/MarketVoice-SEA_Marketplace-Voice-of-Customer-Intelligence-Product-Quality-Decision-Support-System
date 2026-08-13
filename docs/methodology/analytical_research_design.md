# MARKETVOICE SEA — ANALYTICAL RESEARCH DESIGN

**Phase:** 4 — Research & Analytical Design  
**Version:** 1.0  
**Status:** `PHASE_4_DESIGN = COMPLETE`  
**Scope:** methodology only; no model training, synthetic data, new source, or temporal analysis.

## 1. Evidence lock

| Constraint | Design consequence |
|---|---|
| Source A has review text, 1–5 rating, provided sentiment and emotion labels. | It is the supervised benchmark source for sentiment/emotion and a valid source-specific rating task. |
| Source B has review text, 1–5 rating, category, `product_id`, and `shop_id`, but no sentiment/emotion labels. | It supports source-specific rating experiments and authentic product/shop review analytics; it is not a sentiment/emotion gold-label source. |
| Neither source has review timestamps. | No temporal split, temporal feature, trend target, or temporal validation is designed. |
| Cross-source linkage is unsupported. | Experiments, product analytics, and provenance remain source-specific; no rows are joined across sources. |
| Issue taxonomy and labels are unverified. | Phase 4 specifies only a Phase 9 research protocol; it does not create issue categories or train an issue model. |

## 2. Research task mapping

| RQ | Requirement trace | Analytical task | Dataset role / target | Method family | Evaluation | Future phase |
|---|---|---|---|---|---|---|
| `RQ-001` | `BQ-001` → `BR-001` → `IR-001` → `FR-003` | Descriptive review/rating analysis | A+B; supplied rating and category | Reconciled descriptive aggregation | Row reconciliation, source/category coverage | 7 |
| `RQ-002` | `BQ-002` → `BR-002` → `IR-002` → `FR-005` | Product review intelligence | B only; verified `product_id` | Product-grain descriptive aggregation | Product coverage, rating/low-rating definitions | 7 |
| `RQ-003` | `BQ-003` → `BR-003` → `IR-003` → `FR-006` | Shop review indicators | B only; verified `shop_id` | Shop-grain descriptive aggregation | Shop coverage; bounded review-indicator wording | 7 |
| `RQ-004` | `BQ-001`,`BQ-006` → `BR-004` → `IR-004` → `FR-004` | Sentiment and emotion benchmark analysis | A only; provided `Sentiment` / `Emotion` | Descriptive label analysis and later supervised classification | Class coverage and source-specific reconciliation | 8 |
| `RQ-005` | `BR-001` / `FR-003` | Source-specific rating classification research | A and B evaluated as separate experiment datasets; supplied 1–5 rating | Majority reference, TF-IDF + Logistic Regression, TF-IDF + Linear SVM, one evidence-justified challenger | Accuracy, macro/weighted F1, precision, recall, per-class recall, confusion matrix, coverage | 8 |
| `RQ-006` | `BQ-004` → `BR-005` → `IR-005` → `FR-007` | Issue-intelligence methodology | A+B review text; no approved issue target | Corpus review, taxonomy proposal, annotation and evaluation protocol | Taxonomy/annotation/evaluation gate | 9 |
| `RQ-007` | `BQ-005` → `BR-006` → `IR-006` → `FR-008` | Decision-support evidence design | Validated later outputs only | Explainability, uncertainty, and human-review design | Rationale/audit/human-review checks | 10 |

## 3. Dataset roles and analytical boundaries

1. Source A is the sole gold-label benchmark for sentiment and emotion. Its labels must never be imputed to Source B.
2. Both sources may support independent rating-classification research because each supplies a rating. Results retain dataset identity; pooled rows are not assumed to be a single population.
3. Source B is authoritative for product and shop review indicators. `product_id` and `shop_id` never establish a relationship to Source A.
4. Product name/category text can support source-local descriptive context but never supplies a cross-source product key.
5. Review text is processed only after the required privacy review and without intentional PII enrichment or customer profiling.

## 4. Rating, sentiment, and emotion task design

| Task | Target | Eligible source | Unit | Phase 4 decision |
|---|---|---|---|---|
| Rating classification | Supplied 1–5 rating | A or B, in separate experiments | One verified review | Primary supervised task family; no source pooling. |
| Sentiment classification | Provided binary sentiment label | A only | One verified review | Benchmark task; Source B remains unlabeled. |
| Emotion classification | Provided five-class emotion label | A only | One verified review | Benchmark task; class distribution and minority-class reliability must be examined. |

The exact Phase 8 task sequence is selected from class balance, duplicate diagnostics, validation performance, and resource cost. No production architecture, model, threshold, or champion is selected in Phase 4.

## 5. Issue-intelligence research protocol

Phase 9 begins only after a versioned candidate taxonomy is derived from evidence and reviewed by humans. The protocol is: define scope from review text; sample and inspect evidence; propose taxonomy version; prepare annotation guidance; measure annotation quality; create a gold set; evaluate candidate extraction/classification methods; review errors and taxonomy gaps. No fixed issue name, label, annotation size, or classifier is asserted here.

## 6. Reproducibility and stopping rule

Every future experiment identifies dataset, source version/checksum reference, task, split identifier, random-state policy, preprocessing version, model identifier, execution environment, and evaluation output. Experimentation stops when required baselines, one justified challenger, holdout evaluation, and error analysis are complete and additional complexity has no clear research or business value.
