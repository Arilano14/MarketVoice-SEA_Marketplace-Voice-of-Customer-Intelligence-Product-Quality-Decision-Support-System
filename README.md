# MarketVoice SEA — Marketplace Voice-of-Customer Intelligence & Product Quality Decision Support System

---


MarketVoice SEA is an independent academic and portfolio research system. 

This project is **NOT**:
* An official Shopee or Tokopedia product, service, or operational software;
* Developed in partnership with, endorsed by, or affiliated with Shopee or GoTo/Tokopedia;
* A production deployment or live commercial service;
* A live monitoring tool or web scraper targeting commercial platforms.

---

## 🎯 Project Overview

MarketVoice SEA transforms unstructured marketplace customer review text into structured aspect intelligence, prioritized operational review queues, automated case routing, and interactive executive reporting.

While traditional sentiment analysis models focus solely on predicting numerical star ratings, MarketVoice SEA integrates Natural Language Processing (NLP) into a Kimball Star Schema data warehouse, an explainable decision priority scoring engine, REST API microservices, n8n operational workflow automation, and multi-page Power BI decision intelligence dashboards.

---

## 🗺️ Project Engineering Roadmap

| Milestone | Scope & Domain | Status | Validation Evidence |
|---|---|---|---|
| **01. Environment & Data Acquisition** | Dual corpus ingestion & SHA-256 integrity | `COMPLETED` | [`data_acquisition_audit.txt`](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/reports/validation/data_acquisition_audit.txt) |
| **02. Forensic Data Audit** | Quality profiling & text forensics | `COMPLETED` | [`data_forensics_hardening_audit.txt`](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/reports/validation/data_forensics_hardening_audit.txt) |
| **03. Requirements & Traceability** | Business requirements & RTM matrix | `COMPLETED` | [`requirements_verification_audit.txt`](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/reports/validation/requirements_verification_audit.txt) |
| **04. Research Design & Methodology** | Statistical testing & Gold Benchmark | `COMPLETED` | [`research_design_methodology_audit.txt`](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/reports/validation/research_design_methodology_audit.txt) |
| **05. Architecture & Dimensional Model** | Kimball star schema specifications | `COMPLETED` | [`data_architecture_warehouse_audit.txt`](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/reports/validation/data_architecture_warehouse_audit.txt) |
| **06. ETL & Data Warehouse Load** | PostgreSQL DDL & 46,007 review facts | `COMPLETED` | [`data_architecture_warehouse_audit.txt`](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/reports/validation/data_architecture_warehouse_audit.txt) |
| **07. Baseline Business Intelligence** | Analytical summary mart views | `COMPLETED` | [`business_intelligence_marts_audit.txt`](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/reports/validation/business_intelligence_marts_audit.txt) |
| **08. Sentiment & Rating ML Models** | TF-IDF LinearSVC & Logistic Regression | `COMPLETED` | [`nlp_sentiment_rating_model_audit.txt`](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/reports/validation/nlp_sentiment_rating_model_audit.txt) |
| **09. Product Issue Intelligence** | 7-category taxonomy & multi-label NLP | `COMPLETED` | [`issue_intelligence_taxonomy_audit.txt`](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/reports/validation/issue_intelligence_taxonomy_audit.txt) |
| **10. Decision Support System (DSS)** | Priority Ranking Score & reason codes | `COMPLETED` | [`decision_support_priority_scoring_audit.txt`](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/reports/validation/decision_support_priority_scoring_audit.txt) |
| **11. Operational Automation & API** | FastAPI microservice & n8n webhook | `COMPLETED` | [`operational_workflow_integration_audit.txt`](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/reports/validation/operational_workflow_integration_audit.txt) |
| **12. Power BI Decision Dashboards** | Executive Quality Intelligence reports | `IN_PROGRESS` | [`dashboards/power_bi/`](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/dashboards/power_bi/) |

---

## 🛠️ Environment Setup & Reproducibility

### Prerequisites
* Python 3.10+
* Git 2.50+
* PostgreSQL 14+

### Installation
```powershell
# Clone the repository
git clone https://github.com/Arilano14/MarketVoice-SEA_Marketplace-Voice-of-Customer-Intelligence-Product-Quality-Decision-Support-System.git
cd MarketVoice-SEA_Marketplace-Voice-of-Customer-Intelligence-Product-Quality-Decision-Support-System

# Create & activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install core & development dependencies
pip install -e ".[dev]"

# Copy environment configuration
copy .env.example .env

# Run full automated regression suite (146 tests)
pytest tests/ -v
```

---

## 📚 Technical Documentation Index

Detailed architectural, engineering, governance, and research specifications are documented in:
👉 [`docs/engineering/documentation_index.txt`](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/docs/engineering/documentation_index.txt)

---

## 🔒 Data Governance & Security

* **Data Governance & Privacy**: See [`docs/governance/data_governance_and_privacy_policy.txt`](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/docs/governance/data_governance_and_privacy_policy.txt).
* **Security & Vulnerability Reporting**: See [`SECURITY.md`](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/SECURITY.md).
* **PII Protection**: Automated regex redaction of customer contact details (`[REDACTED_EMAIL]`, `[REDACTED_PHONE]`, `[REDACTED_USER]`).

---

## 📄 License & Citation

* Source Code: Released under the [MIT License](LICENSE).
* Citation Metadata: Provided in [`CITATION.cff`](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/CITATION.cff).
