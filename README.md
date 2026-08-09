# MarketVoice SEA — Marketplace Voice-of-Customer Intelligence & Product Quality Decision Support System

[![Phase](https://img.shields.io/badge/Phase-01--Environment%20%26%20Data%20Acquisition-blue)](docs/governance/phase_gates.md)
[![Status](https://img.shields.io/badge/Status-In%20Development-orange)](#project-status)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](pyproject.toml)

> **Independent Academic & Portfolio Prototype**  
> MarketVoice SEA is an independent postgraduate/S2-level portfolio prototype inspired by and extending the analytical task of the **Shopee Code League Sentiment Analysis Challenge**.

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
| **Phase 1** | Environment & Data Acquisition | `IN_PROGRESS` |
| **Phase 2** | Dataset Forensic Audit | `PLANNED` |
| **Phase 3** | Business & System Requirements | `PLANNED` |
| **Phase 4** | Research & Analytical Design | `PLANNED` |
| **Phase 5** | Architecture & Data Model | `PLANNED` |
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

# Install Phase 1 dependencies in editable mode
pip install -e .

# Copy environment configuration
copy .env.example .env

# Run environment validation script
python scripts/environment/validate_environment.py
```

---

## 🔒 DATA GOVERNANCE & PRIVACY

* **Track A (Original Challenge Data)**: Read-only competition baseline. Raw files in `data/raw/` are gitignored to comply with redistribution restrictions.
* **Track B (Conditional Synthetic Data)**: Generated deterministically only if Phase 2 audit identifies missing operational metadata. All synthetic records carry explicit `is_synthetic = TRUE` database flags and UI watermarks.
* **PII Protection**: Automated regex redaction of user contact details during staging.

---

## 📄 LICENSE & CITATION

* Source Code: Released under the [MIT License](LICENSE).
* Dataset Rights: Governed separately by the original competition source terms.
* Citation: See [CITATION.cff](CITATION.cff) for academic citation instructions.
