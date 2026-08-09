# MARKETVOICE SEA — RISK, ASSUMPTION & DEPENDENCY REGISTERS

**Document Version**: 1.0  
**Phase**: Phase 0 (Governance & Scope Baseline)  
**Classification**: Governance Control Register  

---

## 1. PLANNED RISK REGISTER

The following 16 project risks have been identified, categorized, and assigned mitigation strategies across the canonical 15-phase roadmap:

| Risk ID | Risk Description | Cause | Severity | Planned Mitigation Strategy | Trigger Event | Owner Role | Target Phase |
|---|---|---|---|---|---|---|---|
| **RSK-01** | Dataset License Uncertainty | Competition terms unverified | High | Conduct Phase 2 license audit; exclude raw data from public Git repos. | Phase 2 Start | Data Governance Rev | Phase 2 |
| **RSK-02** | Missing Seller/Product Identifiers | Raw dataset lacks operational fields | High | Implement Track B synthetic metadata extension with explicit `is_synthetic` flags. | Phase 2 Audit | BI Architect | Phase 3/6 |
| **RSK-03** | Severe Rating Class Imbalance | E-commerce reviews skewed to 5-star ratings | High | Apply class re-weighting, stratified splits, SMOTE, and report Macro F1. | Phase 2 EDA | Data Science Team | Phase 8 |
| **RSK-04** | Multilingual & Noisy Review Text | Mixed Bahasa/English/slang/emojis | High | Build custom regex text cleaner + leverage candidate multilingual embeddings. | Phase 8 Baseline | Data Science Team | Phase 8 |
| **RSK-05** | Rating Label Ambiguity | Text sentiment conflicts with star rating | Medium | Flag rating-text discordance during EDA; evaluate models on both rating & sentiment. | Phase 2 EDA | Data Science Team | Phase 2/8 |
| **RSK-06** | Synthetic Data Misinterpretation | Users mistaking synthetic metrics for real data | High | Enforce mandatory `is_synthetic = TRUE` database flags and UI banners. | Phase 3 Synthetic Setup | Data Governance Rev | Phase 3/12 |
| **RSK-07** | Data Leakage in Model Pipeline | Fitting preprocessors on test split | High | Enforce strict Scikit-Learn Pipeline encapsulation; split prior to transformation. | Phase 8 Training | Data Science Team | Phase 8 |
| **RSK-08** | Scope Creep into Live Systems | Attempting live scraping or real APIs | High | Enforce strict Phase 0 Guardrails (`PRODUCTION_SYSTEM = FALSE`). | Architecture Design | Senior PM | All |
| **RSK-09** | Model Overengineering | Excessive focus on complex LLMs over BI DW | Medium | Cap ML phase timeline; require baseline model first; prioritize BI DW pipeline. | Phase 8 Planning | Senior PM / BI Arch | Phase 8 |
| **RSK-10** | Unsupported Business Claims | Claiming financial ROI without causal model | High | Disable real revenue impact claims (`REAL_REVENUE_IMPACT_CLAIMS = DISABLED`). | Report Drafting | Data Governance Rev | Phase 14 |
| **RSK-11** | Weak Issue Taxonomy | Arbitrary or overlapping categories | Medium | Perform empirical review of sample text to define candidate taxonomy. | Phase 2 Audit | Business Analyst | Phase 2/9 |
| **RSK-12** | Low Aspect Classifier Performance | Sparse label density in multi-label task | Medium | Implement hybrid rule-based regex + ML classifier pipeline. | Phase 9 Evaluation | Data Science Team | Phase 9 |
| **RSK-13** | Power BI Semantic Mismatch | DW schema mismatch with Power BI relations | Medium | Implement clean Kimball Star Schema with surrogate keys prior to BI import. | Phase 5 Design | BI Architect | Phase 5/12 |
| **RSK-14** | n8n Webhook Complexity | Brittle integration between API and n8n | Low | Mock n8n payloads; use standard HTTP POST Webhooks with JSON validation. | Phase 11 Setup | System Analyst | Phase 11 |
| **RSK-15** | Data Privacy Violation | Unintentional PII leakage in exports | High | Automated regex PII scrubbing during staging; review export files. | Phase 6 ETL | Data Governance Rev | Phase 6/14 |
| **RSK-16** | Project Timeline Overrun | Underestimating multi-tool complexity | Medium | Sequential modular execution with strict Phase Gate sign-offs. | Phase 1 Planning | Senior PM | All |

---

## 2. PLANNED ASSUMPTION REGISTER

The following project assumptions are explicitly separated from verified facts and will be validated in downstream phases:

| Assumption ID | Statement of Assumption | Rationale / Requirement | Validation Phase | Impact if False |
|---|---|---|---|---|
| **ASM-01** | Target dataset is obtainable locally or via competition archive | Required as authentic baseline for rating modeling | Phase 1 / Phase 2 | High (Fallback to open e-commerce dataset) |
| **ASM-02** | Target dataset contains review text and 1-5 integer rating labels | Core analytical foundation of challenge | `REQUIRES_PHASE_2_DATA_AUDIT` | High (Requires re-scoping rating inference task) |
| **ASM-03** | Target dataset lacks rich seller, product, and timestamp metadata | Common in NLP competition datasets | `REQUIRES_PHASE_2_DATA_AUDIT` | Low (Triggers Track B synthetic data extension) |
| **ASM-04** | PostgreSQL database engine can be hosted locally or via container | Required for Kimball DW data modeling | Phase 1 | Low (Fallback to SQLite if Postgres unavailable) |
| **ASM-05** | Power BI Desktop is available on local Windows environment | Required for interactive BI report authoring | Phase 1 | Medium (Fallback to Streamlit/Metabase if unavailable) |
| **ASM-06** | Deterministic synthetic data is acceptable for BI prototyping | Standard academic portfolio methodology | Phase 0 Charter | Low |

---

## 3. PLANNED DEPENDENCY REGISTER

The following technical and operational dependencies govern system execution:

| Dependency ID | Dependency Description | Required For | Risk Level | Resolution Phase |
|---|---|---|---|---|
| **DEP-01** | Local Python 3.10+ Environment | ETL, Synthetic Data, ML Modeling, FastAPI | Low | Phase 1 |
| **DEP-02** | PostgreSQL 14+ Database Instance | Data Warehouse storage, Staging schemas, Data Marts | Medium | Phase 1 |
| **DEP-03** | Power BI Desktop (Windows) | Semantic Modeling, DAX measures, Interactive Reports | Medium | Phase 1 |
| **DEP-04** | n8n Workflow Automation Instance | Operational ticket simulation & Webhook integration | Low | Phase 1 |
| **DEP-05** | Raw Shopee Code League CSV Access | Phase 2 Dataset Audit and Phase 6 Staging ETL | High | Phase 1 / Phase 2 |
| **DEP-06** | Git / GitHub Repository | Version Control, Documentation, Portfolio Hosting | Low | Phase 1 |
| **DEP-07** | Core Python Package Dependencies | Core technical execution across phases | Low | Phase 1 |
