# MARKETVOICE SEA — PROJECT CHARTER & GOVERNANCE BASELINE

**Document Version**: 1.0  
**Phase**: Phase 0 (Governance & Scope)  
**Project Name**: MarketVoice SEA  
**Full Title**: Marketplace Voice-of-Customer Intelligence & Product Quality Decision Support System  
**Project Position**: Independent Postgraduate/S2-Quality Academic & Portfolio Prototype  

---

## 1. PROJECT CONTEXT & POSITIONING

MarketVoice SEA is an independent academic/portfolio system inspired by and extending the analytical foundation of the **Shopee Code League Sentiment Analysis Challenge**. 

While the original competition task focused strictly on predicting numerical ratings from review text strings, MarketVoice SEA extends this capability into a full-scale Business Intelligence (BI) and Decision Support System (DSS). The architecture transforms raw, unstructured marketplace customer feedback into structured aspect intelligence, prioritized operational review queues, automated case routing, and interactive executive reporting.

### Project Boundaries & Non-Affiliation Statement
MarketVoice SEA is explicitly **NOT**:
* An official Shopee product, service, or system;
* Developed in partnership with or endorsed by Shopee;
* A commercial production deployment;
* A live monitoring or web scraping service targeting Shopee platforms.

---

## 2. PROBLEM STATEMENT

E-commerce marketplaces process large volumes of unstructured customer review text daily across diverse product categories. Standard 1-to-5 star numerical ratings alone fail to explain the underlying root causes of customer dissatisfaction (e.g., specific product defects, damaged packaging, seller shipping delays, or unresponsiveness). 

Without automated aspect/issue extraction and explainable decision prioritization:
1. **Product Quality & Category Managers** lack structured visibility into recurring product defect patterns across categories.
2. **Customer Experience (CX) Leadership** cannot easily distinguish between minor customer dissatisfaction and critical operational risk events.
3. **Customer Service (CS) & Seller Operations** face inefficient, unprioritized manual review queues, delaying interventions for high-severity customer complaints.

---

## 3. PROJECT OBJECTIVES

### A. Primary Business Objective
Deliver an enterprise-grade Business Intelligence and Decision Support prototype that automatically extracts customer issue facets, ranks high-severity complaints using an explainable priority scoring mechanism, and presents multi-page interactive BI dashboards for quality management and executive monitoring.

### B. Analytical Objective
Develop a reproducible Natural Language Processing (NLP) pipeline to predict review sentiment/rating and extract multi-label candidate issue categories, integrated seamlessly into a Kimball Star Schema data warehouse hosted on PostgreSQL.

### C. Academic / Research Objective
Evaluate the integration of multi-class sentiment modeling, multi-label aspect classification, and configurable decision-priority scoring within a unified BI and workflow automation architecture, comparing baseline statistical models against modern candidate NLP architectures.

---

## 4. MANDATORY GOVERNANCE FLAGS

The following governance constraints strictly govern all project execution:

```ini
PROJECT_MODE = INDEPENDENT_ACADEMIC_PORTFOLIO
OFFICIAL_SHOPEE_SYSTEM = FALSE
SHOPEE_AFFILIATION = FALSE
PRODUCTION_SYSTEM = FALSE
LIVE_SHOPEE_SCRAPING = DISABLED
UNAUTHORIZED_SHOPEE_API_ACCESS = DISABLED
RAW_COMPETITION_DATA_PUBLIC_REDISTRIBUTION = DISABLED_UNTIL_LICENSE_VERIFIED
SYNTHETIC_OPERATIONAL_EXTENSION = CONDITIONAL_AND_EXPLICITLY_LABELED
REAL_SELLER_PERFORMANCE_CLAIMS = DISABLED_UNLESS_SUPPORTED_BY_REAL_DATA
REAL_PRODUCT_PERFORMANCE_CLAIMS = DISABLED_UNLESS_SUPPORTED_BY_REAL_DATA
REAL_REVENUE_IMPACT_CLAIMS = DISABLED
CAUSAL_CLAIMS = DISABLED_UNLESS_CAUSAL_METHOD_IMPLEMENTED
AUTOMATIC_PUNITIVE_ACTION = DISABLED
HUMAN_IN_THE_LOOP = REQUIRED_FOR_HIGH_PRIORITY_DECISIONS
MODEL_OUTPUT = DECISION_SUPPORT_ONLY
```

---

## 5. SCOPE BOUNDARIES

### IN-SCOPE
1. **Governance & Scope Definition** (Phase 0) - Project charter, requirements baseline, risk register.
2. **Environment & Data Acquisition** (Phase 1) - Toolchain setup, dataset acquisition, config management.
3. **Dataset Forensic Audit** (Phase 2) - Empirical inspection of dataset schema, text noise, class imbalance, and license terms.
4. **Business & System Requirements** (Phase 3) - Formal BRD, SRS, and Information Requirements matrix.
5. **Research & Analytical Design** (Phase 4) - Experimental design, research questions, evaluation framework.
6. **Architecture & Data Model** (Phase 5) - Kimball Star Schema design, data dictionary, system architecture.
7. **ETL & Data Warehouse** (Phase 6) - PostgreSQL staging, transformation scripts, automated data quality assertions.
8. **Baseline Business Intelligence** (Phase 7) - Core SQL data marts and summary reporting queries.
9. **Rating/Sentiment ML** (Phase 8) - Baseline and candidate sentiment/rating classification models.
10. **Aspect & Issue Intelligence** (Phase 9) - Candidate issue taxonomy validation and multi-label aspect extraction.
11. **Decision Support Engine** (Phase 10) - Configurable decision-priority engine design and sensitivity testing.
12. **FastAPI + n8n Integration** (Phase 11) - Analytical REST API microservice and simulated ticket webhook workflows.
13. **Power BI Decision Intelligence** (Phase 12) - Multi-page interactive BI reporting suite across approved domains.
14. **Integrated Validation & UAT** (Phase 13) - End-to-end integration testing and scenario-based UAT execution.
15. **Portfolio & Research Release** (Phase 14) - Technical report, Model Cards, portfolio documentation, reproducibility guide.

### OUT-OF-SCOPE GUARDRAILS
To prevent scope creep, the following capabilities are explicitly prohibited:
* E-commerce marketplace UI clone or shopping cart application
* Personalized product recommender system
* Dynamic pricing optimizer or automated competitor price scraping
* Inventory management or demand forecasting system
* Financial fraud detection or payment gateway analytics
* Automated seller banning or account suspension algorithms
* Real customer PII profiling or identity tracking
* Live web scraping of live Shopee platform
* Off-platform social media sentiment monitoring
* Conversational chatbot assistant
* Real-world revenue impact or causal financial claims (without causal inference)

---

## 6. SIMULATED STAKEHOLDER MAP

| Stakeholder Role | Primary Area of Interest | Key Analytical Output Consumed |
|---|---|---|
| **Head of Customer Experience** | Macro CX performance, review-based sentiment trends, platform quality | Executive CX Dashboard |
| **Product Quality Manager** | Product defect rates, category quality benchmarks, root-cause issue breakdown | Product Quality & Aspect Intelligence Page |
| **Category Manager** | Category-level sentiment distribution, high-risk seller tracking | Category Performance Data Marts |
| **Customer Service Manager** | Priority review queue, operational handling efficiency, SLA tracking | Operational Decision Support Page & Ticket Logs |
| **Seller Operations** | Seller defect ratios, simulated coaching/warning notifications | Seller Performance Data Marts |
| **BI / Data Analyst** | Data warehouse queries, DAX measure development, custom reporting | Kimball Star Schema & Data Marts |
| **Data Science Team** | NLP rating models, multi-label aspect classification, model metrics | Model Performance & Governance Page, Model Cards |
| **Data Governance Reviewer** | Data privacy, licensing compliance, synthetic data labeling audit | Data Quality Audit Logs & Governance Page |
| **Senior Project Manager** | Scope control, roadmap execution, risk register, phase gate approval | Phase Gate Documentation & Technical Reports |

---

## 7. CORE INTENDED TECHNICAL STACK

The technical implementation utilizes an established core stack complemented by candidate technologies subject to empirical evaluation during post-Phase 2 development:

* **Core Intended Stack**: Python 3.10+, PostgreSQL 14+, DataGrip / PyCharm, Power BI Desktop, FastAPI, n8n (Desktop/Docker), Git / GitHub.
* **Candidate Technologies (Subject to Empirical Evaluation)**:
  * ML Frameworks: Scikit-learn, LightGBM, PyTorch, Transformers (Hugging Face).
  * NLP Models: TF-IDF + Classifier baselines, Multilingual Transformer candidates (e.g., XLM-RoBERTa, mBERT).
  * Data Quality: Custom pytest assertions, Great Expectations candidate framework.
  * Experiment Tracking: MLflow, Optuna.
