# MARKETVOICE SEA — BUSINESS & SYSTEM REQUIREMENTS BASELINE

**Document Version**: 1.0  
**Phase**: Phase 0 (Governance & Scope Baseline)  
**Classification**: System Requirements Specification  

---

## 1. BUSINESS QUESTIONS (BQ)

The MarketVoice SEA platform is designed to answer the following business questions:

1. **BQ-1 (CX Condition)**: What is the overall review-based customer experience condition and average rating trend over time across the platform? (*Creation Phase: Phase 7*)
2. **BQ-2 (Root-Cause Issues)**: What complaint categories occur most frequently across customer reviews? (*Creation Phase: Phase 9*)
3. **BQ-3 (Quality Anomalies)**: Which categories or specific products exhibit significant increases in negative customer feedback? (*Creation Phase: Phase 7/9*)
4. **BQ-4 (Decision Prioritization)**: Which specific review cases require priority operational attention based on sentiment severity and operational risk? (*Creation Phase: Phase 10*)
5. **BQ-5 (Operational Workflow)**: How effectively are critical customer complaints routed to simulated operational handling queues? (*Creation Phase: Phase 11*)
6. **BQ-6 (Model Governance)**: How reliable and explainable are the analytical and ML model outputs supporting business decision-making? (*Creation Phase: Phase 8/13*)

---

## 2. RESEARCH QUESTIONS (RQ)

* **RQ-1 (Rating / Sentiment Modeling)**: How accurately can machine learning models predict discrete 1-to-5 star ratings from unstructured customer review text? (*Evaluated via Macro F1, Weighted F1, QWK in Phase 8*).
* **RQ-2 (Aspect / Issue Classification)**: To what extent can multi-label classification methods extract candidate issue categories from unstructured feedback? (*Evaluated via Micro F1, Hamming Loss in Phase 9*).
* **RQ-3 (Decision Prioritization)**: Does a configurable decision-priority engine improve the separation of high-severity customer issues compared to simple star-rating thresholds? (*Evaluated via Top-K Precision and Separation Ratio in Phase 10*).
* **RQ-4 (BI System Integration)**: How effectively can NLP model outputs and dimensional data modeling be integrated into a Power BI semantic layer to ensure data lineage traceability, schema consistency, and decision usability? (*Evaluated via schema audit, lineage validation, and benchmark testing in Phase 12*).

---

## 3. BUSINESS INFORMATION REQUIREMENTS (BIR)

| Req ID | Information Requirement | Required Metric / Indicator | Target User | Data Source | Availability Status | Creation Phase |
|---|---|---|---|---|---|---|
| **BIR-01** | CX Condition & Rating Distribution | Average Rating, Negative Review %, Review Volume | Head of CX | Review Fact Mart | `KNOWN` | Phase 7 |
| **BIR-02** | Issue Category Breakdown | Issue Frequency, % Share of Total Issues | Product Quality Mgr | Issue Fact Mart | `REQUIRES_PHASE_2_DATA_AUDIT` | Phase 9 |
| **BIR-03** | Product & Seller Quality Risk | Negative Review Spike Velocity, Defect Ratio | Category Mgr / Seller Ops | Product/Seller Marts | `CONDITIONAL` | Phase 7/9 |
| **BIR-04** | Priority Decision Review Queue | Priority Score, Priority Rank, SLA Status | CS Manager | Priority Queue Mart | `TO_BE_DEFINED` | Phase 10 |
| **BIR-05** | Model Validation & Transparency | Macro F1, Micro F1, Confusion Matrix, Confidence | Data Science Team | Model Eval Mart | `KNOWN` | Phase 8/9 |
| **BIR-06** | Data Pipeline Quality & Audit | Missing Value Rate, Duplicate Count, Row Count Audit | Data Governance Rev | Pipeline Audit Logs | `KNOWN` | Phase 6 |

---

## 7. CANDIDATE ISSUE TAXONOMY

The issue taxonomy is treated as a **CANDIDATE** model. Categories such as *Packaging Damage*, *Product Defect*, *Delivery Delay*, and *Seller Unresponsiveness* serve as baseline examples. The final issue taxonomy will be validated during Phase 2 dataset review and Phase 9 taxonomy annotation:

```
[CANDIDATE ISSUE TAXONOMY (Subject to Phase 2/9 Validation)]
├── Packaging & Shipping (e.g., damaged box, missing outer seal, delayed delivery)
├── Product Quality & Authenticity (e.g., defective unit, broken part, counterfeit claim)
├── Order Accuracy (e.g., wrong size, wrong color, missing item in parcel)
└── Seller Communication (e.g., slow chat response, unhelpful seller, refund dispute)
```
