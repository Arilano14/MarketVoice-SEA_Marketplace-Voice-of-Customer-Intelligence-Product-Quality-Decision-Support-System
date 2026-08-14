# Interim Data Zone

GOVERNANCE STATUS: `LOCAL_ONLY`. All files in this directory (except this README and .gitkeep) are excluded from public Git tracking per `.gitignore` and [data_governance_policy.md](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/docs/governance/data_governance_policy.md).

Contents (rebuilt locally after clone):
  - `validated/prdect_reviews_standardized.csv`   — Source A standardized corpus
  - `validated/tokopedia_reviews_2019_standardized.csv` — Source B standardized corpus
  - Any intermediate audit artefacts, split indices, grouping tables produced by hardening / split scripts

REGENERATE AFTER CLONE:
  1. Place raw source files in `data/raw/` per `config/data_sources.yaml` column schema.
  2. Run hardening / acquisition pipeline (see `scripts/data_audit/` and `scripts/data_acquisition/`).
     The standard Phase 2 hardened output reproduces the standardized tier deterministically.
  3. Do NOT commit actual CSV files here. Only commit metadata/column-changes that move
     the pipeline (govern docs; no data in git).

