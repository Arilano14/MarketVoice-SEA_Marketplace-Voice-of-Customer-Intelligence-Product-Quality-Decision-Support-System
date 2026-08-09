# MARKETVOICE SEA — REPOSITORY ARCHITECTURE & STRUCTURE

**Document Version**: 1.0  
**Phase**: Phase 1 (Environment, Repository Foundation & Data Acquisition)  
**Classification**: Software Engineering Documentation  

---

## 1. REPOSITORY STRUCTURE GOVERNANCE

MarketVoice SEA strictly enforces standard software engineering repository layout rules:
* **Function-Based Placement**: Files are placed strictly within their designated functional directory.
* **Minimal Root Directory**: The repository root contains only mandatory project-level files (`README.md`, `LICENSE`, `pyproject.toml`, `.gitignore`, `.env.example`).
* **No Tool/Assistant Footprint**: Development tools or assistant chat logs must never be committed to the repository.
* **Git Version History**: Temporary, version-suffixed, or backup filenames (e.g. `final.py`, `test123.py`, `script_v2.py`) are strictly prohibited.

---

## 2. DIRECTORY ARCHITECTURE & RESPONSIBILITIES

```
MarketVoice-SEA/
├── .env.example                  # Template environment variable configuration
├── .gitignore                    # Git tracking exclusion rules (Data/Env protection)
├── CITATION.cff                  # Project academic citation metadata
├── CONTRIBUTING.md               # Developer contribution guidelines
├── LICENSE                       # MIT Source Code License
├── README.md                     # Main repository documentation & setup guide
├── SECURITY.md                   # Security & vulnerability reporting policy
├── pyproject.toml                # Canonical Python package & build metadata
│
├── config/                       # Non-secret application configuration
│   ├── data_sources.yaml         # Dataset source definitions & licensing rules
│   └── project_settings.yaml     # Application environment & path configurations
│
├── data/                         # Governed multi-tier data directory
│   ├── README.md                 # Data governance & tier semantics definition
│   ├── raw/                      # Immutable raw competition data landing (Gitignored)
│   ├── interim/                  # Intermediate ETL outputs (Gitignored)
│   ├── processed/                # Validated data warehouse outputs (Gitignored)
│   └── metadata/                 # Source manifests, checksums, and dataset lineage
│
├── docs/                         # Governed project documentation
│   ├── engineering/              # Technical environment & repository specs
│   ├── governance/               # Charter, policies, risk registers, DoD, gates
│   └── requirements/             # BRD, SRS, RQs, and Requirements Traceability Matrix
│
├── reports/                      # System validation reports & portfolio outputs
│   └── validation/               # Phase validation audit reports
│
├── scripts/                      # Operational automation utilities
│   ├── data_acquisition/         # Dataset registration & checksum calculation
│   └── environment/              # Environment health validation scripts
│
├── src/                          # Main Python source package
│   └── marketvoice/              # Main application namespace
│       ├── __init__.py           # Package declaration (v0.1.0)
│       └── utils/                # Configuration and system utilities
│
└── tests/                        # Automated test suite
    ├── __init__.py
    └── test_environment.py       # Phase 1 environment smoke tests
```

---

## 3. FUTURE PHASE ARTIFACT PLACEMENT

To prevent clutter as the project advances across the 15 canonical phases:
* **Phase 2–3**: Dataset audit logs → `reports/validation/`, BRD/SRS updates → `docs/requirements/`.
* **Phase 5–6**: Database DDL & SQL ETL scripts → `src/marketvoice/etl/` and `src/marketvoice/db/`.
* **Phase 8–9**: Model training modules → `src/marketvoice/models/`, ML reports → `reports/ml/`.
* **Phase 10–11**: Priority engine & FastAPI microservice → `src/marketvoice/api/` and `src/marketvoice/decision/`.
* **Phase 12**: Power BI template files (`.pbit`/`.pbix`) → `reports/bi/`.
