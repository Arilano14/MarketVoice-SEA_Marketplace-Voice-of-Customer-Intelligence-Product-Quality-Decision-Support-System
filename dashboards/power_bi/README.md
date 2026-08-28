# MarketVoice SEA — Power BI Decision Intelligence & Quality Dashboards

**Domain**: Phase 12 — Executive Quality Intelligence & Product Reliability Dashboards  
**Status**: Production Ready / Validated  
**Connection**: Direct PostgreSQL Analytical Warehouse (`marketvoice_warehouse` schema)  
**Taxonomy Version**: `1.0` | **Calculation Version**: `1.0`  

---

## 1. Directory Structure

```text
dashboards/
└── power_bi/
    ├── README.md                             # Master Power BI architecture & user guide
    ├── model_documentation/
    │   ├── semantic_model_spec.md            # Table schemas, grain definitions, relationships
    │   └── db_object_metadata.json           # Validated schema metadata for all 31 objects
    ├── measure_definitions/
    │   └── kpi_dictionary.md                 # Complete DAX measure catalog with formal definitions
    └── validation/
        ├── reconciliation_results.md         # Exact PostgreSQL ↔ Power BI reconciliation matrix
        └── kpi_reconciliation_raw.json       # Machine-readable reconciliation baseline
```

---

## 2. PostgreSQL Connection Parameters

The Power BI reporting suite connects directly to the local PostgreSQL warehouse instance:

| Parameter | Setting | Notes |
|---|---|---|
| **Server** | `localhost:5432` | PostgreSQL 15+ analytical server |
| **Database** | `marketvoice_dev` | Core analytical warehouse database |
| **Schema** | `marketvoice_warehouse` | Kimball star schema & decision marts |
| **Connection Mode** | **Import** (Recommended) / DirectQuery | Import mode ensures sub-second visual performance |
| **Authentication** | Database User / Password | Default local development credentials (`openpg` / env var) |

### Power Query M Connection Snippet
```powerquery-m
let
    Source = PostgreSQL.Database("localhost:5432", "marketvoice_dev", [CreateNavigationProperties=false]),
    Schema = Source{[Schema="marketvoice_warehouse"]}[Data]
in
    Schema
```

---

## 3. Semantic Star Schema Architecture

```text
               +-------------------+       +--------------------+
               |    dim_source     |       |    dim_category    |
               | (source_sk: PK)   |       | (category_sk: PK)  |
               +---------+---------+       +---------+----------+
                         |                           |
                         | 1:N                       | 1:N
                         v                           v
+------------------+   +------------------------------------+   +------------------+
|     dim_shop     |-->|            fact_review             |<--|   dim_product    |
|  (shop_sk: PK)   |   |          (review_sk: PK)           |   | (product_sk: PK) |
+------------------+   |             46,007 rows            |   +------------------+
                       +-----------------+------------------+
                                         |
                                         | 1:N
                                         v
+------------------+   +------------------------------------+   +------------------+
|    dim_issue     |-->|         fact_review_issue          |<--|   dim_severity   |
|  (issue_id: PK)  |   |        (assignment_sk: PK)         |   | (severity_id: PK)|
+------------------+   |             18,863 rows            |   +------------------+
                       +------------------------------------+

                                      Decision Mart
                       +------------------------------------+
                       |        fact_decision_queue         |
                       |         (decision_sk: PK)          |
                       |             5,090 rows             |
                       +-----------------+------------------+
                                         |
                         +---------------+---------------+
                         | 1:N                           | 1:N
                         v                               v
               +-------------------+           +--------------------+
               | dim_priority_tier |           |  dim_reason_code   |
               |  (tier_id: PK)    |           |  (reason_code_sk)  |
               +-------------------+           +--------------------+
```

---

## 4. 7-Page Executive & Operational Report Layout

### Page 1 — Executive Overview
* **Target Audience**: Chief Commercial Officer (CCO), Head of Marketplace Quality, VP Product.
* **Core Business Question**: *"What is the overall customer sentiment and quality posture across platforms?"*
* **Key Visuals**:
  1. **Top KPI Scorecards**: Total Reviews (46,007), Avg Rating (4.46 ⭐), Negative Review % (7.21%), Issue Rate (33.19%), Actionable Queue (192 cases).
  2. **Star Rating Distribution**: 5-Star (70.56%), 4-Star (17.26%), 3-Star (4.97%), 2-Star (2.05%), 1-Star (5.16%).
  3. **Issue Attachment by Source**: PRDECT-ID (11.74%) vs Tokopedia (88.26%).
  4. **Decision Priority Breakdown**: P2 Near-Term (3.77%), P3 Monitoring (14.22%), P4 Informational (82.00%).

### Page 2 — Voice of Customer (VoC) Intelligence
* **Target Audience**: Customer Experience (CX) Directors, Support Leads.
* **Core Business Question**: *"What specific pain points dominate customer feedback, and how do they correlate with star ratings?"*
* **Key Visuals**:
  1. **5-Issue Aspect Breakdown**: Seller Service (33.71%), Packaging/Damage (20.72%), Delivery/Logistics (17.63%), Product Defect (15.90%), Order Inaccuracy (12.04%).
  2. **Rating-Aspect Matrix**: Cross-tabulation of issue mentions across 1-star through 5-star reviews.
  3. **Customer Review Evidence Explorer**: Filterable review verbatim grid with PII-redacted text.

### Page 3 — Product Quality Intelligence (Source B Scope)
* **Target Audience**: Category Managers, Merchant Quality Auditors.
* **Core Business Question**: *"Which specific products exhibit chronic defects and warrant vendor intervention?"*
* **Key Visuals**:
  1. **Product Risk Index Scatterplot**: Evidence volume vs Priority Risk Score (PRS).
  2. **Top Defective Products**: Ranking of products by critical defect frequency.
  3. **Product Issue Profile Matrix**: Product-level breakdown across all 5 issue categories.

### Page 4 — Issue Category Deep Dive
* **Target Audience**: Operations & Logistics Analysts, Supply Chain Managers.
* **Core Business Question**: *"Which issues have statistically anomalous dissatisfaction overrepresentation?"*
* **Key Visuals**:
  1. **Dissatisfaction Overrepresentation Ratio**: Comparison of issue frequency in low-rating vs baseline reviews.
  2. **Recurrence Multipliers**: High-volume recurring issue clusters.
  3. **Category-Level Issue Distribution**: Issue concentration across 34 product categories.

### Page 5 — Decision Support Queue
* **Target Audience**: Quality Operations Managers, Remediation Specialists.
* **Core Business Question**: *"Which entity-issue combinations require immediate human review and investigation?"*
* **Key Visuals**:
  1. **Triage Action Queue**: 192 actionable P2 cases ranked by Priority Risk Score (PRS).
  2. **Reason Code Breakdown**: Frequency of triggers (`RC_CRITICAL_SEVERITY_DOMINANCE`, `RC_HIGH_DISSATISFACTION_DRIVER`, etc.).
  3. **Guidance Recommendation Panel**: Policy-driven action text dynamically populated per tier.

### Page 6 — Operational Automation Monitoring (Demonstration Data)
* **Target Audience**: DevOps Engineers, Integration Architects.
* **Core Business Question**: *"How reliably is the n8n-FastAPI triage pipeline routing and resolving incoming events?"*
* **Key Visuals**:
  1. **Pipeline Throughput**: 37 operational events processed with 100% idempotency verification.
  2. **Human-in-the-Loop Cases**: 13 human review cases created, 14 resolution outcomes recorded.
  3. **Execution Latency & Routing Split**: Visual split between automated monitoring and human queue routing.
* **Governance Label**: Clearly marked with `SYNTHETIC_OPERATIONAL_DEMONSTRATION`.

### Page 7 — Data Quality & Governance Audit
* **Target Audience**: Data Governance Committee, BI Lead, Audit Officers.
* **Core Business Question**: *"Can the executive metrics be trusted against source data integrity standards?"*
* **Key Visuals**:
  1. **Pre-Flight Data Quality Checks**: 11/11 automated checks passing (Zero duplicate keys, zero orphan FKs, zero cross-source contamination).
  2. **Model Metadata & Lineage Card**: NLP Taxonomy Version 1.0, TF-IDF SVC benchmark models, DSS Calculation Version 1.0.
  3. **Source Traceability Table**: Row counts and SHA-256 hashes for Source A and Source B.

---

## 5. DAX Measure Summary

| Measure Name | DAX Formula | Business Interpretation |
|---|---|---|
| `Total Reviews` | `COUNTROWS('fact_review')` | Ingested review volume |
| `Average Rating` | `AVERAGE('fact_review'[rating_value])` | Platform-wide average star rating |
| `Negative Review %` | `DIVIDE(CALCULATE(COUNTROWS('fact_review'), 'fact_review'[rating_value] <= 2), COUNTROWS('fact_review'))` | Proportion of 1-2 star reviews |
| `Issue Rate %` | `DIVIDE(DISTINCTCOUNT('fact_review_issue'[review_sk]), COUNTROWS('fact_review'))` | Reviews containing ≥1 issue |
| `Decision Queue Total` | `COUNTROWS('fact_decision_queue')` | Evaluated triage cases |
| `Actionable Cases (P1+P2)` | `CALCULATE(COUNTROWS('fact_decision_queue'), 'fact_decision_queue'[tier_id] IN {1, 2})` | Cases requiring investigation |
| `Average PRS` | `AVERAGE('fact_decision_queue'[priority_score])` | Mean Priority Risk Score |
| `Average Model Confidence` | `AVERAGE('fact_review_issue'[confidence])` | NLP classifier certainty |

---

## 6. Governance & Data Integrity

1. **No External Transformations**: All calculations are grounded in the verified PostgreSQL analytical warehouse.
2. **Deterministic Reconciliation**: All metrics reconcile exactly (0.00% variance on integer counts) against SQL queries.
3. **Source Isolation Preserved**: Source A (PRDECT-ID) and Source B (Tokopedia) remain strictly partitioned by `source_sk` across all visuals.
