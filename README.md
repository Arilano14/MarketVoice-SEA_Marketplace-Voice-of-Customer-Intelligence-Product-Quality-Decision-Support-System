# MarketVoice SEA — Marketplace Voice-of-Customer Intelligence & Product Quality Decision Support System

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](pyproject.toml)
[![Database: PostgreSQL 15](https://img.shields.io/badge/Database-PostgreSQL%2015-336791.svg)](sql/warehouse/)
[![Microservice: FastAPI](https://img.shields.io/badge/Microservice-FastAPI-009688.svg)](src/marketvoice/api/)
[![Orchestration: n8n](https://img.shields.io/badge/Orchestrator-n8n-EA4B71.svg)](workflows/n8n/)
[![BI: Power BI](https://img.shields.io/badge/BI-Power%20BI-F2C811.svg)](dashboards/power_bi/)
[![Tests: 146 Passed](https://img.shields.io/badge/Tests-146%20Passed%20(100%25)-brightgreen.svg)](tests/)

---

## 1. Project Overview

**MarketVoice SEA** is an integrated Voice-of-Customer (VoC) analytics and decision support engineering platform designed for Southeast Asian e-commerce marketplaces. The system ingests multi-platform customer reviews, extracts granular product defect aspects using frozen Natural Language Processing (NLP) taxonomies, evaluates multi-factor Priority Risk Scores (PRS), orchestrates automated triage workflows via FastAPI and n8n, and serves executive-grade business intelligence dashboards in Power BI.

---

## 2. Business Problem

Southeast Asian e-commerce platforms process millions of unstructured customer reviews daily across disparate channels. Conventional marketplace analytics suffer from three fundamental limitations:
1. **Rating Polarization Bias**: Over 70% of reviews are 5-star ratings, obscuring critical product defects within textual feedback.
2. **Actionability Gap**: Standard sentiment analysis predicts numerical polarity (+1/-1) without identifying the specific defect aspect (e.g., transit packaging damage vs. chronic battery defect).
3. **Operational Triage Latency**: Quality assurance and merchant operations teams lack automated, explainable prioritization mechanisms to filter high-severity risks from operational noise.

---

## 3. Objectives

* **Aspect Intelligence**: Extract 5 core product and service defect aspects across Indonesian marketplace reviews.
* **Contextual Decision Support**: Compute an explainable Priority Risk Score (PRS) balancing severity impact, dissatisfaction overrepresentation, event recurrence, volume support, and classifier confidence.
* **Sub-Second Microservice Triage**: Provide low-latency REST endpoints for real-time review analysis and human-in-the-loop (HITL) resolution logging.
* **Automated Webhook Orchestration**: Route low-risk cases to background monitoring while escalating high-risk cases to quality audit teams.
* **Executive Decision Intelligence**: Deliver a 7-page Power BI reporting suite reconciling exactly to the underlying PostgreSQL warehouse.

---

## 4. Scope & Non-Goals

### In-Scope
* Ingestion and dimensional modeling of 46,007 marketplace reviews across two Indonesian e-commerce corpora.
* Indonesian text preprocessing, slang normalization, and multi-label aspect classification.
* Kimball Star Schema data warehouse with 31 validated schema objects in PostgreSQL 15.
* FastAPI microservice with Pydantic contract enforcement and SHA-256 idempotency.
* 12-node n8n workflow triage orchestrator with PII redaction.
* Power BI semantic model with 18 DAX measures and 100% SQL reconciliation.

### Out-of-Scope (Non-Goals)
* Live commercial marketplace scraping or real-time streaming infrastructure.
* Autonomous seller sanctions, inventory de-listing, or automated financial refunds.
* Unverified causal assertions or speculative business claims.

---

## 5. Data Sources & Provenance

The system integrates two canonical open-source Indonesian e-commerce review corpora:

| Dataset Identifier | Source Description | Record Count | License | Provenance Reference |
|---|---|---|---|---|
| `SRC_PRDECT_ID_V1` (Source A) | PRDECT-ID Indonesian Product Reviews V1 | **5,400** | CC BY 4.0 | Mendeley Data (DOI: 10.17632/v925f38nsr.1) |
| `SRC_TOKOPEDIA_REVIEWS_2019` (Source B) | Tokopedia Marketplace Reviews 2019 | **40,607** | CC0 Public Domain | Kaggle Open Dataset Archive |
| **Total Ingested** | **Consolidated Multi-Source Warehouse** | **46,007** | — | **100% Reconciled** |

*Note: Source A is strictly partitioned from SKU-level grains due to lack of native product IDs, while Source B supports product-level drill-down across 3,664 SKUs.*

---

## 6. System Architecture

```text
                                  +---------------------------------------+
                                  |    Raw Marketplace Review Corpora     |
                                  | (Source A: 5,400 | Source B: 40,607)  |
                                  +-------------------+-------------------+
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |    Data Quality & Ingestion Engine    |
                                  | (11 Automated Pre-Flight Assertions)  |
                                  +-------------------+-------------------+
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |   PostgreSQL 15 Kimball Data Warehouse |
                                  |    (9 Dimensions, 3 Facts, 14 Marts)  |
                                  +---------+-------------------+---------+
                                            |                   |
                     +----------------------+                   +----------------------+
                     |                                                                 |
                     v                                                                 v
+-------------------------------------------+                     +-------------------------------------------+
|    NLP Aspect & Decision Support Engine   |                     |     Power BI Decision Intelligence Suite  |
|  - 5-Aspect Frozen Taxonomy v1.0          |                     |  - 7-Page Executive & Operational Report  |
|  - Multi-Factor Priority Risk Score (PRS) |                     |  - 18 Standardized DAX Measures           |
|  - Monte Carlo Sensitivity Analysis       |                     |  - 22 Reconciled SQL Business Metrics     |
+--------------------+----------------------+                     +-------------------------------------------+
                     |
                     v
+-------------------------------------------+
|      FastAPI Microservice (Port 8000)     |
|  - POST /v1/review/analyze                |
|  - POST /v1/decision/evaluate             |
|  - POST /v1/workflow/human-review         |
+--------------------+----------------------+
                     |
                     v
+-------------------------------------------+
|       n8n Workflow Engine (Port 5678)     |
|  - 12-Node Webhook Triage Orchestrator    |
|  - PII Masking + SHA-256 Idempotency Key  |
|  - P1/P2 Human Queue | P3/P4 Logging      |
+-------------------------------------------+
```

---

## 7. Data Architecture (Kimball Star Schema)

The analytical data warehouse (`marketvoice_warehouse` schema) consists of:
* **Conformed Dimensions**: `dim_source`, `dim_category`, `dim_product`, `dim_issue`, `dim_severity`, `dim_rating`, `dim_priority_tier`, `dim_reason_code`, `dim_shop`.
* **Central Fact Tables**:
  * `fact_review` (46,007 rows): Core review transaction grain.
  * `fact_review_issue` (18,863 rows): Multi-label issue occurrences.
  * `fact_decision_queue` (5,090 rows): Triaged decision cases.
* **Operational Tables**: `human_review_case`, `human_review_outcome`, `operational_event_log`, `workflow_execution`, `data_quality_result`.

---

## 8. Analytics & NLP Modeling

* **Linguistic Normalization**: Indonesian slang conversion (colloquial-to-formal lexicon), Indonesian stopword removal, punctuation stripping, and lowercasing.
* **Supervised Benchmark Models (Source A Gold Benchmark)**:
  * **Sentiment Classification**: TF-IDF (1-3 ngrams) + LinearSVC $\to$ **Macro F1 = 0.8878**, **Weighted F1 = 0.8879**.
  * **Emotion Classification**: TF-IDF + Logistic Regression $\to$ **Macro F1 = 0.6712**, **Weighted F1 = 0.6725**.
  * **Rating Prediction**: TF-IDF + LinearSVC $\to$ **Quadratic Weighted Kappa (QWK) = 0.7788**, **MAE = 0.4407**.

---

## 9. Issue Intelligence & Aspect Taxonomy

The frozen **Taxonomy v1.0** classifies review text into 5 mutually exclusive operational domains:

1. **Product Defect / Quality** (2,999 mentions, 15.90%): Functional failures, broken parts, dead-on-arrival components.
2. **Packaging / Shipping Damage** (3,908 mentions, 20.72%): Dented boxes, torn bubble wrap, fluid leakage during transit.
3. **Order Inaccuracy / Missing Items** (2,272 mentions, 12.04%): Wrong color/size/SKU shipped, missing accessories.
4. **Delivery / Logistics Issue** (3,326 mentions, 17.63%): Courier delays, tracking issues, failed delivery attempts.
5. **Seller Service / Responsiveness** (6,358 mentions, 33.71%): Unresponsive chat support, slow dispatch, poor resolution.

*Total Issue Mentions: **18,863** across **15,270** distinct customer reviews (33.19% issue attachment rate).*

---

## 10. Decision Support System (DSS)

The Decision Support System calculates a composite **Priority Risk Score (PRS)** bounded in $[0, 100]$:

$$\text{PRS} = 100 \times \left( 0.30 \cdot \phi_{\text{sev}} + 0.25 \cdot \phi_{\text{diss}} + 0.20 \cdot \phi_{\text{rec}} + 0.15 \cdot \phi_{\text{vol}} + 0.10 \cdot \phi_{\text{conf}} \right)$$

### Priority Tier Distribution (5,090 Total Cases)
* **P2 High Priority** (192 cases, **3.77%**): Immediate quality audit recommendation (Score $\ge 50.0$).
* **P3 Monitoring** (724 cases, **14.22%**): Statistical quality surveillance ($30.0 \le \text{Score} < 50.0$).
* **P4 Informational** (4,174 cases, **82.00%**): Baseline operational logging ($\text{Score} < 30.0$).

### Sensitivity & Robustness
Monte Carlo simulation (1,000 runs, $\pm 20\%$ parameter perturbation) confirms **High Stability**:
* Mean Spearman Rank Correlation ($\rho$): **`0.9983`**
* Kendall Tau Concordance ($\tau$): **`0.9237`**
* Top-10% Queue Jaccard Overlap: **`0.8840`**

---

## 11. Operational Automation (FastAPI & n8n)

* **FastAPI Service (`src/marketvoice/api/`)**:
  * Runs on `http://127.0.0.1:8000` with automated OpenAPI Swagger documentation at `/docs`.
  * Provides `/health`, `/ready`, `/model`, `/v1/review/analyze`, `/v1/decision/evaluate`, `/v1/workflow/human-review`.
* **n8n Workflow Engine (`workflows/n8n/`)**:
  * 12-Node visual review triage orchestrator running on `http://localhost:5678`.
  * Performs regex PII sanitization (redacts email, phone numbers, and user handles).
  * Computes deterministic SHA-256 idempotency key to prevent duplicate ticket creation.
  * Routes P1/P2 cases to the human review table and P3/P4 cases to the background log.

---

## 12. Power BI Reporting Suite

The reporting suite connects directly to PostgreSQL (`marketvoice_warehouse`) with 7 purpose-built pages:
* **Page 1: Executive Overview**: High-level platform CX posture, rating curves, top defect cards.
* **Page 2: Voice of Customer (VoC)**: 5-aspect distribution, rating-aspect cross-tabulation, verbatim explorer.
* **Page 3: Product Quality (Source B)**: SKU-level risk quadrant scatterplot, top chronic defect rankings.
* **Page 4: Issue Intelligence**: Dissatisfaction overrepresentation ratios, recurrence multipliers.
* **Page 5: Decision Support**: Actionable 192-case P2 triage queue, reason code trigger breakdown.
* **Page 6: Operational Monitoring**: n8n throughput, webhook execution latency, human review outcomes.
* **Page 7: Data Quality & Governance**: 11 pre-flight check statuses, taxonomy versioning, model lineage.

---

## 13. Verification & Reconciliation Summary

Every primary metric reconciles with **0.00% variance** between PostgreSQL SQL queries and Power BI DAX measures:

| Analytical Metric | PostgreSQL (SQL) Value | Power BI (DAX) Value | Variance | Status |
|---|---|---|---|---|
| Total Reviews Ingested | **46,007** | **46,007** | `0` | ✅ EXACT |
| Source A Reviews (PRDECT-ID) | **5,400** (11.74%) | **5,400** (11.74%) | `0` | ✅ EXACT |
| Source B Reviews (Tokopedia) | **40,607** (88.26%) | **40,607** (88.26%) | `0` | ✅ EXACT |
| Average Platform Star Rating | **4.4600 ⭐** | **4.4600 ⭐** | `0.0000` | ✅ EXACT |
| Negative Review Count (1★ & 2★) | **3,318** (7.21%) | **3,318** (7.21%) | `0` | ✅ EXACT |
| Total Detected Issue Mentions | **18,863** | **18,863** | `0` | ✅ EXACT |
| Reviews Containing Issues | **15,270** (33.19%) | **15,270** (33.19%) | `0` | ✅ EXACT |
| Evaluated Decision Cases | **5,090** | **5,090** | `0` | ✅ EXACT |
| Actionable P2 Triage Cases | **192** (3.77%) | **192** (3.77%) | `0` | ✅ EXACT |
| Mean Priority Risk Score (PRS) | **18.24** | **18.24** | `0.00` | ✅ EXACT |

---

## 14. Limitations & Governance Disclosures

1. **Rating Asymmetry**: The heavy skew toward positive reviews (70.56% 5-star) necessitates statistical overrepresentation ratios rather than raw issue counts.
2. **Source Isolation**: Source A lacks SKU/shop metadata; product-level analytics are strictly restricted to Source B.
3. **Severity Proxy**: Issue severity is mapped from star ratings (1★ = Critical, 2★ = High), representing customer perception rather than direct laboratory failure analysis.
4. **Synthetic Operational Scope**: n8n webhook demonstrations use explicitly documented synthetic fixtures (`SYNTHETIC_OPERATIONAL_DEMONSTRATION`).

---

## 15. Technology Stack

* **Programming Language**: Python 3.10+
* **Analytical Warehouse**: PostgreSQL 15+
* **Microservice Framework**: FastAPI, Uvicorn, Pydantic v2
* **Workflow Automation**: n8n (Node.js runtime)
* **Machine Learning**: scikit-learn, NumPy, pandas, SciPy
* **Testing & Quality Assurance**: pytest, psycopg3
* **Business Intelligence**: Power BI Desktop (Direct PostgreSQL Connector)

---

## 16. Repository Structure

```text
.
├── README.md                                  # Canonical project architecture and user manual
├── LICENSE                                    # MIT License with third-party dataset disclaimer
├── CITATION.cff                               # Academic citation metadata
├── CONTRIBUTING.md                            # Development, coding, and SQL standards
├── SECURITY.md                                # Security, credential isolation, and PII policy
├── .gitignore                                 # Hardened Git exclusion list
├── .env.example                               # Environment variable template
├── pyproject.toml                             # Python package manifest and dependencies
│
├── config/                                    # Project and experiment YAML configurations
├── data/                                      # Data directories (raw, interim, processed, metadata)
├── src/marketvoice/                           # Core application and analytics source code
│   ├── analytics/                             # NLP preprocessing, taxonomy, and issue metrics
│   ├── api/                                   # FastAPI application, routes, and schemas
│   ├── database/                              # PostgreSQL connection, schema, and guards
│   ├── decision/                              # Priority scoring, reason codes, sensitivity
│   ├── etl/                                   # Data warehouse ingestion and loading
│   ├── integration/                           # PII sanitization and idempotency hashing
│   ├── modeling/                              # Aspect discovery and ML model cards
│   └── quality/                               # Automated pre-flight data quality checks
├── sql/                                       # DDL, mart views, operations, and validation queries
├── tests/                                     # Comprehensive pytest test suite (146 tests)
│   ├── unit/                                  # Component unit tests
│   ├── integration/                           # End-to-end workflow integration tests
│   ├── api/                                   # FastAPI contract tests
│   ├── workflow/                              # n8n workflow contract tests
│   └── regression/                            # Decision support and gold benchmark regression
├── scripts/                                   # Functional utility scripts (acquisition, audit, runners)
├── n8n/                                       # Dedicated n8n workspace, workflows, scripts, and fixtures
├── workflows/n8n/                             # Canonical version-controlled n8n workflows archive
├── models/metadata/                           # NLP model parameter and benchmark metadata
├── dashboards/power_bi/                       # Power BI documentation, DAX measures, and specs
├── docs/                                      # Architecture, engineering, governance, methodology docs
└── reports/                                   # Audit reports, validation manifests, and archives
```

---

## 17. Local Setup & Quickstart

### 1. Clone & Environment Setup
```powershell
# Clone repository
git clone https://github.com/Arilano14/MarketVoice-SEA_Marketplace-Voice-of-Customer-Intelligence-Product-Quality-Decision-Support-System.git
cd MarketVoice-SEA_Marketplace-Voice-of-Customer-Intelligence-Product-Quality-Decision-Support-System

# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Configure environment variables
Copy-Item .env.example .env
```

### 2. Configure Database Credentials in `.env`
```text
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=marketvoice_dev
POSTGRES_USER=openpg
POSTGRES_PASSWORD=your_secure_password
```

### 3. Run Test Suite
```powershell
$env:PYTHONPATH = "src;.pipdeps"
python -m pytest tests/ -v
```

### 4. Launch FastAPI Microservice
```powershell
python scripts/runners/start_api.py
```

### 5. Launch n8n Workflow Server
```powershell
cd workflows/n8n
npx n8n start --port 5678
```

---

## 18. Reproducibility Guarantee

All analytical metrics, priority scores, and machine learning models are deterministic:
* **Fixed Random Seed**: `seed = 42` across all training/test splits and Monte Carlo simulations.
* **Zero Post-Hoc Tuning**: Multi-factor DSS weights sum strictly to `1.000000`.
* **Automated Regression**: Executing `pytest tests/` validates all 146 system assertions in ~165 seconds.

---

## 19. Data Usage & Licensing

* **Source Code & Documentation**: Licensed under the [MIT License](LICENSE).
* **Source A Dataset**: PRDECT-ID is distributed under Creative Commons Attribution 4.0 International (CC BY 4.0).
* **Source B Dataset**: Tokopedia Reviews 2019 is distributed under Creative Commons Public Domain Dedication (CC0 1.0).
* **Attribution**: See [CITATION.cff](CITATION.cff) for academic citation formatting.

---

## 20. Future Development Roadmap

* **Transformer Embeddings**: Optional IndoBERT embeddings for nuance extraction in informal Indonesian slang.
* **Streaming Ingestion**: Apache Kafka integration for real-time review stream ingestion.
* **Automated Seller Feedback Loop**: Automated merchant portal integration with rate-limited notification queues.
