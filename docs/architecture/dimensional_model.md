# MARKETVOICE SEA — DIMENSIONAL MODEL

**Phase:** 5 — Solution Architecture & Data Model  
**Version:** 1.0  
**Status:** conceptual design; no DDL or physical column specification.

## 1. Modeling rules

`ONE_FACT_ONE_GRAIN = TRUE`  
`BUSINESS_KEYS_PRESERVED = TRUE`  
`SOURCE_LINEAGE_REQUIRED = TRUE`  
`ACCIDENTAL_MANY_TO_MANY = FORBIDDEN`  
`FAKE_CROSS_SOURCE_KEYS = FORBIDDEN`

Surrogate keys are justified for stable warehouse relationships. Source business keys remain retained for provenance. Source-aware category identity is required because categories are not proven conformable across sources. No `dim_date` is designed for authentic reviews.

## 2. Candidate entity register

| Entity | Business purpose / grain | Source / business key | Surrogate-key rationale | Major attributes / relationships | Track / phase |
|---|---|---|---|---|---|
| `dim_source` | One registered analytical source. | Phase 2 manifest / `source_id`. | Stable internal relationship to all Track A facts. | Source name, publisher, version, license, checksum reference; one-to-many to review facts. | A / 6 |
| `dim_rating` | One permitted rating value. | Verified rating domain / rating value. | Optional stable analytic key; five fixed members. | Rating value and ordered meaning; one-to-many to review facts. | A / 6 |
| `dim_category` | One raw category within one source. | A `Category` or B `category`, plus source identity. | Prevents accidental cross-source category equivalence. | Raw category, source reference, availability; one-to-many to review facts. | A / 6 |
| `dim_product` | One Source B product listing. | B / `product_id`. | Supports stable warehouse relationship while preserving `product_id`. | Product ID, product name, source reference; one-to-many to Source B reviews. | A / 6 |
| `dim_shop` | One Source B shop review context. | B / `shop_id`. | Supports stable warehouse relationship while preserving `shop_id`. | Shop ID, source reference; one-to-many to Source B reviews. | A / 6 |
| `fact_review` | One verified review record from exactly one source row. | A or B / stable analytical review key plus source-row lineage. | Review key provides internal referential identity; source-row reference is retained. | Review text reference, supplied rating, source/category references, optional B product/shop references, Source A provided labels, validation/provenance references. Many-to-one to source/rating/category; optional many-to-one to B product/shop. | A / 6 |
| `dim_model` | One model version/run identity. | Future experiment metadata / model and run identity. | Enables reproducible derived-output relationships. | Task, model identifier/version, experiment/split/preprocessing references. One-to-many to prediction/evaluation facts. | Future / 8–9 |
| `fact_model_prediction` | One model prediction for one review, one model/run, and one task. | Derived output / review key + model/run + task. | Internal key supports repeated runs without overwriting source truth. | Predicted label, confidence, execution reference; many-to-one to review and model. | Future / 8–9 |
| `fact_model_evaluation` | One evaluated model/run, task, dataset, and evaluation split. | Derived output / model-run + task + source + split. | Internal evaluation identity preserves repeated experiment evidence. | Metric results, coverage, confusion-matrix reference, error-analysis reference; many-to-one to model and source. | Future / 8–9 |
| `dim_issue` | One approved issue identity in one taxonomy version. | Phase 9 taxonomy / taxonomy version + issue identity. | Versioning avoids rewriting historical prediction meaning. | Taxonomy version, issue identifier, definition/status; one-to-many to issue predictions. | Conditional / 9 |
| `fact_issue_prediction` | One review–issue result for one model/run. | Derived output / review key + issue + model/run. | Internal key preserves multiple method versions. | Result/prediction, confidence, evidence reference; many-to-one to review, issue, and model. | Conditional / 9 |
| `fact_decision_support` | One decision-support assessment for one review and rule version. | Phase 10 output / review key + rule version + assessment reference. | Preserves re-assessment and audit history. | Priority representation, rationale, uncertainty, evidence references, human-review outcome; many-to-one to review and applicable derived outputs. | Conditional / 10 |
| `fact_case` | One explicitly synthetic operational case. | Track B only / approved synthetic `case_id`. | Keeps operational case identity distinct from review identity. | Synthetic status/priority and operational event references; may reference a review only as evidence context. | B conditional / 10–11 |
| `fact_intervention` | One explicitly synthetic intervention event. | Track B only / approved synthetic `event_id`. | Supports multiple events per case without changing review truth. | Intervention type/status and synthetic operational event date; many-to-one to synthetic case. | B conditional / 10–11 |

## 3. Relationship and key strategy

1. `fact_review` is the Track A central fact. It has one source, one supplied rating, and one source-aware category. Product and shop references are populated only for Source B records.
2. `dim_product` and `dim_shop` do not directly relate to each other. Their only analytical co-occurrence is through a Source B `fact_review` record.
3. Source A product-title text is not a product business key. It cannot populate `dim_product` or join to Source B.
4. Model, issue, and DSS facts reference review identity but do not update source attributes or supplied labels.
5. Track B case/intervention facts never become parents of Track A review facts. Any reference to a review is contextual and retains synthetic status.
6. Referential integrity is enforced in Phase 6 for required references. Product/shop references are nullable for records where the source does not supply that entity; null does not imply an inferred unknown product/shop.

## 4. Unknown-member policy

For source, rating, and category values that fail validation but are retained for audit, Phase 6 uses a documented source-specific unknown/not-supplied member and records the validation finding. No unknown member is used to manufacture Source A product or shop identity. Missing Source B `product_id`/`shop_id`, if ever encountered, remains a documented missing source value rather than an inferred entity.

## 5. Explicit exclusions

No authentic review-date dimension, common cross-source product dimension, seller-performance fact, or operational SLA fact is designed. Issue taxonomy values and priority-scoring method remain future Phase 9/10 decisions.
