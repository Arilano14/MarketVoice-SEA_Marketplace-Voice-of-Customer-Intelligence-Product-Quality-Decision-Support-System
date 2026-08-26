# MarketVoice SEA — Marketplace Voice-of-Customer Intelligence & Product Quality Decision Support System
---

## 📌 DISCLAIMER & PROJECT POSITIONING

MarketVoice SEA is an independent academic and portfolio research system. 

This project is **NOT**:
* An official Shopee product, service, or operational software;
* Developed in partnership with, endorsed by, or affiliated with Shopee;
* A production deployment or live commercial service;
* A live monitoring tool or web scraper targeting Shopee platforms.

---

## 🎯 PROJECT OVERVIEW

MarketVoice SEA transforms unstructured marketplace customer review text into structured aspect intelligence, prioritized operational review queues, automated case routing, and interactive executive reporting.

While traditional sentiment analysis models focus solely on predicting numerical star ratings, MarketVoice SEA integrates Natural Language Processing (NLP) into a Kimball Star Schema data warehouse, an explainable decision priority scoring engine, REST API microservices, n8n operational workflow automation, and multi-page Power BI decision intelligence dashboards.

---

## 🗺️ CANONICAL 15-PHASE ROADMAP

MarketVoice SEA strictly follows a 15-phase canonical engineering roadmap:

| Phase | Phase Name | Status |
|---|---|---|
| **Phase 0** | Governance & Scope | `COMPLETED` (Gate: PASS) |
| **Phase 1** | Environment & Data Acquisition | `COMPLETED` (Gate: PASS) |
| **Phase 2** | Dataset Forensic Audit | `COMPLETED` (Gate: PASS) |
| **Phase 3** | Business & System Requirements | `COMPLETED` (Gate: PASS) |
| **Phase 4** | Research & Analytical Design | `COMPLETED` (Gate: PASS) |
| **Phase 5** | Architecture & Data Model | `COMPLETED` (Gate: PASS) |
| **Phase 6** | ETL & Data Warehouse | `PLANNED` |
| **Phase 7** | Baseline Business Intelligence | `PLANNED` |
| **Phase 8** | Rating/Sentiment ML | `PLANNED` |
| **Phase 9** | Aspect & Issue Intelligence | `PLANNED` |
| **Phase 10** | Decision Support | `PLANNED` |
| **Phase 11** | FastAPI + n8n | `PLANNED` |
| **Phase 12** | Power BI Decision Intelligence | `PLANNED` |
| **Phase 13** | Integrated Validation & UAT | `PLANNED` |
| **Phase 14** | Portfolio & Research Release | `PLANNED` |

---

## 🛠️ ENVIRONMENT SETUP & REPRODUCIBILITY

### Prerequisites
* Python 3.10+
* Git 2.50+
* PostgreSQL 14+ (or Docker Engine)

### Installation
```powershell
# Clone the repository
git clone https://github.com/Arilano14/MarketVoice-SEA_Marketplace-Voice-of-Customer-Intelligence-Product-Quality-Decision-Support-System.git
cd MarketVoice-SEA_Marketplace-Voice-of-Customer-Intelligence-Product-Quality-Decision-Support-System

# Create & activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install core dependencies in editable mode
pip install -e .

# Install ALL development dependencies (required before running pytest, linters, or optional heavy validators)
pip install -e ".[dev]"

# Copy environment configuration
copy .env.example .env

# Run environment validation script (stdlib-only; runs immediately after core install)
python scripts/environment/validate_environment.py

# Run smoke tests (both stdlib unittest and pytest work after installing [dev] extras)
python -m unittest discover tests -v
python -m pytest -q
```

---

## 🔒 DATA GOVERNANCE & PRIVACY

* **Canonical Dual-Source Foundation** (per [config/data_sources.yaml](config/data_sources.yaml) and [docs/governance/data_governance_policy.md](docs/governance/data_governance_policy.md)):
  - Source A (`SRC_PRDECT_ID_V1`) — PRDECT-ID Indonesian product reviews 5,400 rows (sentiment + emotion gold)
  - Source B (`SRC_TOKOPEDIA_REVIEWS_2019`) — Tokopedia product reviews 2019 40,607 rows (product_id + shop_id)
* **Distribution**: Data tiers `data/raw/*`, `data/interim/*`, `data/processed/*`, `logs/*` are all `LOCAL_ONLY`. They are excluded from public Git via `.gitignore` (only `*.gitkeep` and tier READMEs are versioned as placeholders). Rebuild locally with acquisition + hardening scripts after clone.
* **Cross-source linkage**: `CROSS_SOURCE_PRODUCT_LINKAGE = NOT_SUPPORTED`; `CROSS_SOURCE_SHOP_LINKAGE = NOT_SUPPORTED`; `CROSS_SOURCE_ROW_LINKAGE = NOT_SUPPORTED`. No fuzzy entity merge.
* **Temporal facts**: Authentic review timestamps are `NOT_AVAILABLE` in both raw sources; no `dim_date` for review facts.
* **Track B (Conditional Synthetic Data)**: Generated deterministically only if governance-approved and missing operational metadata is justified. All synthetic records carry explicit `is_synthetic = TRUE` flags and never leak into Track A gold.
* **PII Protection**: Automated regex redaction of user contact details during staging (case/intervention fact fields only; Phase 9+).

---

## 📄 LICENSE & CITATION

* Source Code: Released under the [MIT License](LICENSE).
* Dataset Rights: Governed separately by the original competition source terms.
* Citation: See [CITATION.cff](CITATION.cff) for academic citation instructions.
