# MARKETVOICE SEA — BUSINESS & SYSTEM REQUIREMENTS SPECIFICATION BASELINE

**Document Version**: 2.0 (Phase 3 Requirements Index & Governance Baseline)  
**Phase**: Phase 3 (Business & System Requirements Specification & Governance Baseline)  
**Classification**: System Requirements Specification Baseline  

---

## 1. SPECIFICATION INDEX

The MarketVoice SEA requirement architecture consists of four comprehensive specifications:

1. **[Business Requirements Document (BRD)](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/docs/requirements/business_requirements_document.md)** (`DEL-04`): Establishes executive vision, stakeholder decision personas, Business Questions (BQ-1..BQ-6), Research Questions (RQ-1..RQ-4), Business Information Requirements (BIR-01..BIR-06), and standardized performance target thresholds.
2. **[System Requirements Specification (SRS)](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/docs/requirements/system_requirements_specification.md)** (`DEL-05`): Establishes Functional Requirements (FR-101..FR-605), Non-Functional Requirements (NFR-101..NFR-402), data architecture boundaries, microservices, and Power BI dashboard specifications.
3. **[Requirements Traceability Matrix (RTM)](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/docs/requirements/requirements_traceability_matrix.md)**: Bi-directional matrix mapping business questions, information requirements, functional requirements, data marts, standardized metrics, and validation phases.
4. **[Target Alignment Checking System](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/scripts/requirements/validate_requirements_alignment.py)**: Automated zero-dependency verification utility standardizing target thresholds and validating alignment against `DATA_FOUNDATION_VERSION = 1.0`.

---

## 2. SUMMARY OF STANDARDIZED TARGET METRICS

| Requirement Domain | Target Indicator / Metric | Standardized Threshold | Verification Phase |
|---|---|---|---|
| **Rating Prediction (RQ-1 / BIR-05)** | Macro F1 | $\ge 0.70$ | Phase 8 |
| **Rating Prediction (RQ-1 / BIR-05)** | Weighted F1 | $\ge 0.75$ | Phase 8 |
| **Rating Prediction (RQ-1 / BIR-05)** | Quadratic Weighted Kappa (QWK) | $\ge 0.75$ | Phase 8 |
| **Emotion Classification (RQ-1 / BIR-05)** | Macro F1 | $\ge 0.65$ | Phase 8 |
| **Aspect Classification (RQ-2 / BIR-02)** | Micro F1 | $\ge 0.70$ | Phase 9 |
| **Aspect Classification (RQ-2 / BIR-02)** | Hamming Loss | $\le 0.10$ | Phase 9 |
| **Priority Engine (RQ-3 / BIR-04)** | Separation Ratio | $\ge 2.5$ | Phase 10 |
| **Priority Engine (RQ-3 / BIR-04)** | Top-K Precision ($K=50$) | $\ge 0.80$ | Phase 10 |
| **Data Pipeline Quality (BIR-06)** | Row Reconciliation | $100\%$ ($0$ lost rows) | Phase 6 |
| **Data Pipeline Quality (BIR-06)** | Lineage Key Uniqueness | $100\%$ ($0$ nulls) | Phase 6 |
