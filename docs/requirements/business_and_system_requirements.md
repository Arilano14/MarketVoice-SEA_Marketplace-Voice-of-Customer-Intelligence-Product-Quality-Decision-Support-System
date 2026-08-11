# MARKETVOICE SEA — BUSINESS & SYSTEM REQUIREMENTS BASELINE v1.0

**Document Version**: 1.0 (Phase 3 Requirements Baseline v1.0 Index)  
**Phase**: Phase 3 (Business & System Requirements Specification & Governance Baseline)  
**Data Foundation Baseline**: `DATA_FOUNDATION_VERSION = 1.0` (Frozen)  
**Phase 3 Status**: `PHASE_3_EXECUTION_STATUS = COMPLETED`, `PHASE_3_REVIEW_STATUS = READY_FOR_HUMAN_REVIEW`, `PHASE_3_GATE_STATUS = NOT_EVALUATED`  

---

## 1. SPECIFICATION SUITE INDEX

The MarketVoice SEA requirement framework consists of five canonical specification deliverables:

1. **[Business Requirements Document (BRD)](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/docs/requirements/business_requirements_document.md)** (`DEL-04`): Establishes executive vision, 9 simulated stakeholder decision personas, 7 Business Questions (`BQ-CX`, `BQ-PRODUCT`, `BQ-SHOP`, `BQ-ISSUE`, `BQ-DSS`, `BQ-MODEL`, `BQ-DQ`), 10 formal Business Requirements (`BR-001`..`BR-010`), and explicit governance boundaries.
2. **[System Requirements Specification (SRS)](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/docs/requirements/system_requirements_specification.md)** (`DEL-05`): Establishes 7 Logical System Capabilities, 14 Functional Requirements (`FR-001`..`FR-014`), 14 Non-Functional Requirements (`NFR-001`..`NFR-014`), Requirement ID Migration Governance, and current implementation technology directions (`FINAL_ARCHITECTURE = PHASE_5_DECISION`).
3. **[Information Requirements & KPI Dictionary v1.0](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/docs/requirements/information_requirements_and_kpi_dictionary.md)** (`DEL-04 / DEL-05 Extension`): Establishes 10 formal Information Requirements (`IR-001`..`IR-010`) and 32 fully specified KPIs across 7 domains with mandatory formulas, grains, numerator/denominator definitions, and null handling rules.
4. **[Requirements Traceability Matrix (RTM)](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/docs/requirements/requirements_traceability_matrix.md)**: Bi-directional matrix mapping Business Objectives $\rightarrow$ Business Questions $\rightarrow$ Business Requirements $\rightarrow$ Information Requirements $\rightarrow$ KPIs $\rightarrow$ Functional Requirements $\rightarrow$ Data Capabilities $\rightarrow$ Data Sources $\rightarrow$ Validation Phases.
5. **[Automated Requirements Alignment Checking System](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/scripts/requirements/validate_requirements_alignment.py)**: Automated zero-dependency structural validation utility checking requirement completeness, orphan status, KPI schema validity, Phase 9 dependencies, and forbidden claim detection.

---

## 2. GOVERNANCE BOUNDARIES & MANDATORY CORRECTIONS APPLIED

1. **Premature ML Targets Removed**: All arbitrary numeric thresholds (`Macro F1 >= 0.70`, `Micro F1 >= 0.70`, `QWK >= 0.75`, `Separation Ratio >= 2.5`) have been removed from Phase 3 specifications. All ML evaluation metrics are specified with `TARGET_THRESHOLD = TO_BE_DETERMINED_IN_PHASE_4`.
2. **Logical Capabilities Defined**: Physical database table creation (`CREATE TABLE staging...`) and DDL execution are strictly prohibited in Phase 3. Architectural choices are specified as `LOGICAL_SYSTEM_CAPABILITIES` with `FINAL_ARCHITECTURE = PHASE_5_DECISION`.
3. **Forbidden Claim Guardrails**: Zero NPS (Net Promoter Score) or CSAT proxy metrics are defined. Zero authentic temporal trend metrics (monthly/weekly review trends) are defined (`REAL_REVIEW_TIMESTAMP = NOT_AVAILABLE`).
4. **Synthetic Operational Boundaries**: Simulated operational logs (Track B CS tickets, SLA tracking) strictly carry `is_synthetic = TRUE`, `scenario_version`, and `simulation_rule_version` metadata. Zero synthetic data injected into authentic raw datasets.
5. **Issue Intelligence Boundary**: `ISSUE_DISCOVERY = SUPPORTED` via unsupervised text mining; `SUPERVISED_ISSUE_CLASSIFICATION = CONDITIONAL_PENDING_PHASE_9_HUMAN_ANNOTATION` (`DEPENDS_ON = PHASE_9_TAXONOMY_AND_ANNOTATION_GATE`).

---

## 3. KPI DICTIONARY SUMMARY TABLE (32 APPROVED KPIS)

| KPI ID | KPI Name | Domain | Business Question | Support Status | Formula Summary | Grain |
|---|---|---|---|---|---|---|
| `KPI-CX-01` | Total Review Volume | Customer Experience | `BQ-CX` | `SUPPORTED` | $\text{COUNT}(\text{source\_record\_key})$ | Platform / Source |
| `KPI-CX-02` | Average Customer Star Rating | Customer Experience | `BQ-CX` | `SUPPORTED` | $\text{AVG}(\text{rating})$ | Aggregate / Category / Product / Shop |
| `KPI-CX-03` | Rating Distribution Count | Customer Experience | `BQ-CX` | `SUPPORTED` | $\text{COUNT}(\text{rating} = k)$ | Star Level (1 to 5) |
| `KPI-CX-04` | Negative Review Rate | Customer Experience | `BQ-CX`, `BQ-PRODUCT` | `SUPPORTED` | $\frac{\text{COUNT}(\text{rating} \le 2)}{\text{Total Count}} \times 100\%$ | Aggregate / Category / Product / Shop |
| `KPI-CX-05` | Positive Review Rate | Customer Experience | `BQ-CX` | `SUPPORTED` | $\frac{\text{COUNT}(\text{rating} \ge 4)}{\text{Total Count}} \times 100\%$ | Aggregate / Category / Product / Shop |
| `KPI-CX-06` | Sentiment Class Share | Customer Experience | `BQ-CX`, `BQ-MODEL` | `SUPPORTED_SOURCE_A_ONLY` | $\frac{\text{COUNT}(\text{Sentiment} = c)}{5400} \times 100\%$ | Sentiment Class (Source A) |
| `KPI-CX-07` | Emotion Class Share | Customer Experience | `BQ-CX`, `BQ-MODEL` | `SUPPORTED_SOURCE_A_ONLY` | $\frac{\text{COUNT}(\text{Emotion} = e)}{5400} \times 100\%$ | Emotion Class (Source A) |
| `KPI-PRD-01` | Product Review Volume | Product Quality | `BQ-PRODUCT` | `SUPPORTED_SOURCE_B_ONLY` | $\text{COUNT}(\text{product\_id} = p)$ | Product Listing (`product_id`) |
| `KPI-PRD-02` | Product Average Rating | Product Quality | `BQ-PRODUCT` | `SUPPORTED_SOURCE_B_ONLY` | $\text{AVG}(\text{rating}_p)$ | Product Listing (`product_id`) |
| `KPI-PRD-03` | Product Negative Review Rate | Product Quality | `BQ-PRODUCT` | `SUPPORTED_SOURCE_B_ONLY` | $\frac{\text{COUNT}(\text{rating}_p \le 2)}{\text{COUNT}_p} \times 100\%$ | Product Listing (`product_id`) |
| `KPI-CAT-01` | Category Review Volume | Category Quality | `BQ-PRODUCT` | `SUPPORTED` | $\text{COUNT}(\text{category} = c)$ | Category Level |
| `KPI-CAT-02` | Category Average Rating | Category Quality | `BQ-PRODUCT` | `SUPPORTED` | $\text{AVG}(\text{rating}_c)$ | Category Level |
| `KPI-CAT-03` | Category Negative Review Rate | Category Quality | `BQ-PRODUCT` | `SUPPORTED` | $\frac{\text{COUNT}(\text{rating}_c \le 2)}{\text{COUNT}_c} \times 100\%$ | Category Level |
| `KPI-SHP-01` | Shop Review Volume | Shop Review Intel | `BQ-SHOP` | `SUPPORTED_SOURCE_B_ONLY` | $\text{COUNT}(\text{shop\_id} = s)$ | Merchant Shop (`shop_id`) |
| `KPI-SHP-02` | Shop Average Star Rating | Shop Review Intel | `BQ-SHOP` | `SUPPORTED_SOURCE_B_ONLY` | $\text{AVG}(\text{rating}_s)$ | Merchant Shop (`shop_id`) |
| `KPI-SHP-03` | Shop Negative Review Rate | Shop Review Intel | `BQ-SHOP` | `SUPPORTED_SOURCE_B_ONLY` | $\frac{\text{COUNT}(\text{rating}_s \le 2)}{\text{COUNT}_s} \times 100\%$ | Merchant Shop (`shop_id`) |
| `KPI-SHP-04` | Shop Product Listing Coverage | Shop Review Intel | `BQ-SHOP` | `SUPPORTED_SOURCE_B_ONLY` | $\text{COUNT}(\text{DISTINCT product\_id}_s)$ | Merchant Shop (`shop_id`) |
| `KPI-ISS-01` | Candidate Issue Theme Frequency | Issue Intelligence | `BQ-ISSUE` | `CONDITIONAL_PENDING_PHASE_9` | $\text{COUNT}(\text{Issue}_k = 1)$ | Issue Theme Level |
| `KPI-ISS-02` | Candidate Issue Rate | Issue Intelligence | `BQ-ISSUE` | `CONDITIONAL_PENDING_PHASE_9` | $\frac{\text{COUNT}(\text{Issue}_k = 1)}{\text{Total Reviews}} \times 100\%$ | Issue Theme Level |
| `KPI-DSS-01` | Priority Review Case Count | Decision Support | `BQ-DSS` | `SUPPORTED_VIA_MODEL` | $\text{COUNT}(\text{Priority Score} \ge 75)$ | Priority Queue Level |
| `KPI-DSS-02` | Critical Review Recall | Decision Support | `BQ-DSS` | `FUTURE_DSS_KPI` | $\frac{\text{COUNT}(\text{Severe} \cap \text{Queue})}{\text{COUNT}(\text{Severe})} \times 100\%$ | Priority Queue Level |
| `KPI-DSS-03` | Priority Queue Precision | Decision Support | `BQ-DSS` | `FUTURE_DSS_KPI` | $\frac{\text{COUNT}(\text{Severe} \cap \text{Top-K})}{K} \times 100\%$ | Top-K Queue ($K=50$) |
| `KPI-DSS-04` | Simulated Ticket Dispatch Count | Track B Simulation | `BQ-DSS` | `SUPPORTED_AS_SIMULATION` | $\text{COUNT}(\text{simulated\_ticket\_id})$ | Webhook Dispatch Event |
| `KPI-MDL-01` | Rating Model Accuracy | ML Governance | `BQ-MODEL` | `SUPPORTED` | $\frac{\sum \mathbb{I}(\hat{y}_i = y_i)}{N}$ | Model Run Level |
| `KPI-MDL-02` | Rating Model Macro F1 Score | ML Governance | `BQ-MODEL` | `SUPPORTED` | $\frac{1}{5} \sum_{k=1}^5 \text{F1}_k$ | Model Run Level |
| `KPI-MDL-03` | Rating Model Weighted F1 Score | ML Governance | `BQ-MODEL` | `SUPPORTED` | $\frac{\sum N_k \cdot \text{F1}_k}{N}$ | Model Run Level |
| `KPI-MDL-04` | Quadratic Weighted Kappa (QWK) | ML Governance | `BQ-MODEL` | `SUPPORTED` | $1 - \frac{\sum w_{ij} O_{ij}}{\sum w_{ij} E_{ij}}$ | Model Run Level |
| `KPI-MDL-05` | Rating Prediction Confusion Matrix | ML Governance | `BQ-MODEL` | `SUPPORTED` | $5 \times 5 \text{ Matrix Count } C_{i,j}$ | Class Pair Level ($5 \times 5$) |
| `KPI-DQ-01` | Invalid Record Count | Data Quality | `BQ-DQ` | `SUPPORTED` | $\text{COUNT}(\text{validation\_status} = \text{INVALID})$ | Ingestion Batch Level |
| `KPI-DQ-02` | Quarantined Record Count | Data Quality | `BQ-DQ` | `SUPPORTED` | $\text{COUNT}(\text{is\_quarantined} = \text{TRUE})$ | Ingestion Batch Level |
| `KPI-DQ-03` | Critical Null Count | Data Quality | `BQ-DQ` | `SUPPORTED` | $\text{COUNT}(\text{NULL} \mid \text{col} \in \{\text{text}, \text{rating}\})$ | Column / Dataset Level |
| `KPI-DQ-04` | Cross-Source Duplicate Count | Data Quality | `BQ-DQ` | `SUPPORTED` | $\text{COUNT}(t \mid t \in \text{Text}_A \land t \in \text{Text}_B)$ | Cross-Source Level |
| `KPI-DQ-05` | Lineage Key Uniqueness % | Data Quality | `BQ-DQ` | `SUPPORTED` | $\frac{\text{COUNT}(\text{DISTINCT key})}{N} \times 100\%$ | Dataset Level |
| `KPI-DQ-06` | Ingestion Reconciliation Status | Data Quality | `BQ-DQ` | `SUPPORTED` | $\text{Staging Rows} = \text{Raw Rows}$ | Ingestion Batch Level |
