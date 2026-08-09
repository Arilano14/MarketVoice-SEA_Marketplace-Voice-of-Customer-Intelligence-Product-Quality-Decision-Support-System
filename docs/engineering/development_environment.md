# MARKETVOICE SEA — DEVELOPMENT ENVIRONMENT SPECIFICATION

**Document Version**: 1.0  
**Phase**: Phase 1 (Environment, Repository Foundation & Data Acquisition)  
**Classification**: System Engineering Documentation  

---

## 1. ENVIRONMENT OVERVIEW

MarketVoice SEA is developed in a local Windows environment utilizing Python for data processing and machine learning, PostgreSQL for data warehousing, FastAPI for API services, n8n for operational workflow automation, and Power BI Desktop for business intelligence reporting.

---

## 2. TOOLCHAIN & SYSTEM INVENTORY

| System / Tool | Verified Version | Availability Status | Usage Domain in Project |
|---|---|---|---|
| **Operating System** | Windows 10/11 x64 | `AVAILABLE` | Core local development host |
| **Python** | 3.10.11 | `AVAILABLE` | Core runtime (ETL, ML, API) |
| **pip** | 23.0.1 | `AVAILABLE` | Package manager |
| **Git** | 2.54.0 | `AVAILABLE` | Version control & source control governance |
| **Docker Engine** | 29.3.1 | `AVAILABLE` | Container host for PostgreSQL & n8n |
| **PostgreSQL** | 14+ (Docker / Local) | `REQUIRED_LATER` | Data Warehouse & Staging database (Phase 6+) |
| **FastAPI** | Current (pyproject.toml) | `REQUIRED_LATER` | REST API analytical service (Phase 11) |
| **n8n** | Desktop / Docker | `REQUIRED_LATER` | Operational workflow ticket automation (Phase 11) |
| **Power BI Desktop** | Local Windows App | `REQUIRED_LATER` | Interactive decision intelligence reporting (Phase 12) |

---

## 3. PYTHON VIRTUAL ENVIRONMENT SETUP

### A. Virtual Environment Policy
To maintain reproducibility and prevent package conflicts across global Python installations, all project dependencies must be isolated within a local virtual environment (`.venv`).

### B. Setup Commands (Windows PowerShell)
```powershell
# Create isolated virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Upgrade pip & install Phase 1 dependencies in editable mode
python -m pip install --upgrade pip
pip install -e .
```

---

## 4. DEPENDENCY MANAGEMENT POLICY

1. **Single Source of Truth**: `pyproject.toml` serves as the authoritative dependency declaration file.
2. **Minimal Phase Dependencies**: Packages are added strictly when required by the current active phase. Phase 1 includes only utility, environment validation, checksum, configuration, and testing tools (`pyyaml`, `python-dotenv`, `requests`, `pytest`).
3. **Phase-Gated Upgrades**: Heavy machine learning dependencies (e.g., PyTorch, Transformers, LightGBM) are deferred to Phase 8/9.

---

## 5. ENVIRONMENT VALIDATION SCRIPT

To verify environment health, execute the automated validation script:

```powershell
python scripts/environment/validate_environment.py
```
