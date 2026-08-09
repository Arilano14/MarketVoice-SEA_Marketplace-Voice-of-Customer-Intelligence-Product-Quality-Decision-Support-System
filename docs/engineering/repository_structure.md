# MARKETVOICE SEA — REPOSITORY ARCHITECTURE & STRUCTURE

**Document Version**: 1.1 (Remediated)  
**Phase**: Phase 1 (Environment, Repository Foundation & Data Acquisition)  
**Classification**: Software Engineering Documentation  

---

## 1. REPOSITORY STRUCTURE GOVERNANCE

MarketVoice SEA strictly enforces standard software engineering repository layout rules:
* **Function-Based Placement**: Files are placed strictly within designated functional directories.
* **Minimal Root Directory**: Root contains only mandatory configuration and documentation assets.
* **No Tool/Assistant Footprint**: Assistant-specific chat logs or tool-named files are strictly prohibited.
* **Strict Remote Git Policy**: Remote repository controls belong exclusively to the human user (`REMOTE_REPOSITORY_CONTROL = USER_ONLY`). Assistant execution of `git push` or `git push --force` is strictly forbidden.

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
│   └── validation/               # Phase validation & remediation audit reports
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

## 3. N8N WORKFLOW ARCHITECTURE DECISION RECORD

* **Decision ID**: `ADR-001-N8N-CUSTOM-WORKFLOW`
* **Core Strategy**: `CORE_WORKFLOW = CUSTOM_PROJECT_WORKFLOW`. The n8n workflow for operational case routing (Phase 11) will be built custom (80–100% custom project logic).
* **Reference Usage**: Public n8n templates may be used solely as architectural references for node patterns, batching, error handling, and routing logic.
* **Scraping Boundary**: Live marketplace scraping is strictly barred (`LIVE_SHOPEE_SCRAPING = FALSE`).
* **Inference Separation**: Python / FastAPI analytical microservice is the primary sentiment/aspect inference engine. n8n serves strictly as the operational workflow orchestrator.
