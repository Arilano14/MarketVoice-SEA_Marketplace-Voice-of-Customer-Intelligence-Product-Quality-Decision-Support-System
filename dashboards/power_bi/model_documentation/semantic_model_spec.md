# MarketVoice SEA — Power BI Semantic Model Specification

**Schema**: `marketvoice_warehouse`  
**Model Architecture**: Kimball Dimensional Conformed Star Schema + Decision Marts  
**Validated Date**: 2026-08-28  

---

## 1. Conformed Dimensions

### 1.1 `dim_source` (2 rows)
* **Primary Key**: `source_sk` (smallint)
* **Grain**: One record per distinct marketplace review dataset source.
* **Attributes**:
  * `source_id` (text): Unique identifier (`SRC_PRDECT_ID_V1`, `SRC_TOKOPEDIA_REVIEWS_2019`)
  * `source_display_name` (text): Formatted business label
  * `source_license` (text): Academic / Public license descriptor
  * `source_file_sha256` (text): Cryptographic integrity hash of raw source file
  * `source_row_count_manifest` (integer): Baseline row count in manifest
* **Power BI Setting**: Hidden key `source_sk`, Display column `source_display_name`.

### 1.2 `dim_category` (34 rows)
* **Primary Key**: `category_sk` (integer)
* **Grain**: One record per product category.
* **Attributes**:
  * `source_native_category` (character varying): Native Indonesian marketplace category name
  * `category_name_en` (character varying): Standardized English translation
* **Power BI Setting**: Relationship to `fact_review[category_sk]` (1:N) and `fact_decision_queue[category_sk]` (1:N).

### 1.3 `dim_product` (3,664 rows)
* **Primary Key**: `product_sk` (integer)
* **Grain**: One record per distinct product in Source B (Tokopedia).
* **Attributes**:
  * `source_native_product_id` (character varying): Native SKU / product identifier
  * `product_name` (character varying): Standardized product name
* **Power BI Setting**: Relationship to `fact_review[product_sk]` (1:N) and `fact_decision_queue[product_sk]` (1:N).

### 1.4 `dim_issue` (5 rows)
* **Primary Key**: `issue_id` (smallint)
* **Grain**: One record per frozen issue taxonomy category (Taxonomy v1.0).
* **Attributes**:
  * `issue_name` (character varying): Business name of defect/issue
  * `issue_definition` (text): Formal scope definition
  * `evidence_keywords` (text): Lexical detection triggers
  * `taxonomy_version` (character varying): `1.0`
* **Hierarchy**:
  1. `1: Product Defect / Quality`
  2. `2: Packaging / Shipping Damage`
  3. `3: Order Inaccuracy / Missing Items`
  4. `4: Delivery / Logistics Issue`
  5. `5: Seller Service / Responsiveness`

### 1.5 `dim_severity` (4 rows)
* **Primary Key**: `severity_id` (smallint)
* **Grain**: One record per severity level.
* **Attributes**:
  * `severity_code` (character varying): `CRITICAL`, `HIGH`, `MODERATE`, `LOW`
  * `severity_name` (character varying): User-friendly display label
  * `rating_proxy_rule` (text): Rating-based severity mapping rule (1★ → CRITICAL, 2★ → HIGH, 3★ → MODERATE, 4-5★ → LOW)

### 1.6 `dim_priority_tier` (4 rows)
* **Primary Key**: `tier_id` (smallint)
* **Grain**: One record per decision support priority tier.
* **Attributes**:
  * `tier_code` (character varying): `P1_CRITICAL`, `P2_HIGH_PRIORITY`, `P3_MONITORING`, `P4_INFORMATIONAL`
  * `tier_name` (character varying): Formal recommendation name
  * `min_score_threshold` / `max_score_threshold` (numeric): PRS score bounds
  * `guidance_recommendation` (text): Standard operational procedure recommendation

### 1.7 `dim_reason_code` (7 rows)
* **Primary Key**: `reason_code_sk` (smallint)
* **Grain**: One record per explainable decision reason trigger.
* **Attributes**:
  * `reason_code` (text): Machine-readable trigger (`RC_CRITICAL_SEVERITY_DOMINANCE`, `RC_HIGH_DISSATISFACTION_DRIVER`, etc.)
  * `reason_description` (text): Plain-language justification for triage analysts

---

## 2. Central Fact Tables

### 2.1 `fact_review` (46,007 rows)
* **Primary Key**: `review_sk` (bigint)
* **Grain**: One record per customer review transaction.
* **Measures & Keys**:
  * `rating_value` (smallint): Star rating (1 to 5)
  * `review_text_len_chars` (integer): Review length in characters
  * `source_sk` (smallint, FK → `dim_source`)
  * `category_sk` (integer, FK → `dim_category`)
  * `product_sk` (integer, FK → `dim_product`, nullable for Source A)
  * `shop_sk` (integer, FK → `dim_shop`, nullable for Source A)
  * `rating_sk` (smallint, FK → `dim_rating`)
  * `is_synthetic` (boolean): `false` for historical facts

### 2.2 `fact_review_issue` (18,863 rows)
* **Primary Key**: `assignment_sk` (bigint)
* **Grain**: One record per detected issue occurrence per review (1:N from `fact_review`).
* **Measures & Keys**:
  * `review_sk` (bigint, FK → `fact_review`)
  * `issue_id` (smallint, FK → `dim_issue`)
  * `severity_id` (smallint, FK → `dim_severity`)
  * `confidence` (numeric): Model classification confidence [0.00 to 1.00]
  * `keyword_count` (integer): Number of keyword matches

### 2.3 `fact_decision_queue` (5,090 rows)
* **Primary Key**: `decision_sk` (integer)
* **Grain**: One record per entity × issue triage evaluation.
* **Measures & Keys**:
  * `priority_score` (numeric): Calculated Priority Risk Score (PRS) [3.62 to 68.62]
  * `severity_impact_score` (numeric): Weight 0.30
  * `dissatisfaction_score` (numeric): Weight 0.25
  * `recurrence_score` (numeric): Weight 0.20
  * `volume_score` (numeric): Weight 0.15
  * `confidence_score` (numeric): Weight 0.10
  * `evidence_support` (integer): Total review mentions supporting this case
  * `distinct_review_events` (integer): Unique review count
  * `tier_id` (smallint, FK → `dim_priority_tier`)
  * `grain_type` (character varying): `PRODUCT_X_ISSUE`, `CATEGORY_X_ISSUE`, `SOURCE_X_ISSUE`

---

## 3. Pre-Aggregated Mart Views for Fast Visual DirectQuery / Import

| View Name | Grain | Row Count | Primary Visual Usage |
|---|---|---|---|
| `mv_issue_summary` | `source_sk` × `issue_id` | 10 | Executive issue distribution & overrepresentation |
| `mv_product_summary` | `product_sk` | 3,664 | Product catalog quality ranking & defect count |
| `mv_category_summary` | `category_sk` | 34 | Category benchmarks & average ratings |
| `mv_priority_product_queue` | `product_sk` × `issue_id` | 4,913 | Product-level decision queue ranking |
| `mv_priority_category_queue` | `category_sk` × `issue_id` | 167 | Category-level decision queue ranking |
| `mv_issue_low_rating_overrepresentation` | `source_sk` × `issue_id` | 10 | Low-rating overrepresentation ratio matrix |
| `mv_product_risk_index` | `product_sk` | 2,259 | Risk vs volume scatterplot |
| `mv_source_summary` | `source_sk` | 2 | Platform comparison KPI cards |
| `mv_pipeline_health` | Platform | 1 | Pipeline health status widget |

---

## 4. Relationship Integrity Matrix

| Relationship | From Column | To Column | Cardinality | Cross-Filter |
|---|---|---|---|---|
| `dim_source` → `fact_review` | `source_sk` | `source_sk` | 1 : Many | Single |
| `dim_category` → `fact_review` | `category_sk` | `category_sk` | 1 : Many | Single |
| `dim_product` → `fact_review` | `product_sk` | `product_sk` | 1 : Many | Single |
| `dim_rating` → `fact_review` | `rating_sk` | `rating_sk` | 1 : Many | Single |
| `dim_shop` → `fact_review` | `shop_sk` | `shop_sk` | 1 : Many | Single |
| `fact_review` → `fact_review_issue` | `review_sk` | `review_sk` | 1 : Many | Both (or Single) |
| `dim_issue` → `fact_review_issue` | `issue_id` | `issue_id` | 1 : Many | Single |
| `dim_severity` → `fact_review_issue` | `severity_id` | `severity_id` | 1 : Many | Single |
| `dim_priority_tier` → `fact_decision_queue` | `tier_id` | `tier_id` | 1 : Many | Single |
| `dim_source` → `fact_decision_queue` | `source_sk` | `source_sk` | 1 : Many | Single |
| `dim_product` → `fact_decision_queue` | `product_sk` | `product_sk` | 1 : Many | Single |
| `dim_category` → `fact_decision_queue` | `category_sk` | `category_sk` | 1 : Many | Single |
