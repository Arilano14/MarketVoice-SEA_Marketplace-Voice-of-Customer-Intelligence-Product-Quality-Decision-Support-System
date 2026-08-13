# MARKETVOICE SEA — INTEGRATION CONTRACTS

**Phase:** 5 — Solution Architecture & Data Model  
**Version:** 1.0  
**Scope:** consumer responsibility contracts; no endpoint, payload, workflow-node, or report-visual implementation.

## 1. Downstream consumption contracts

| Consumer | Required curated input | Output / responsibility | Boundary | Phase |
|---|---|---|---|---|
| Baseline BI | Track A review/rating/source/category/product/shop analytical outputs and quality limitations. | Presents approved information domains to analytical users. | Consumes curated mart outputs, not raw CSV as final architecture. | 7, 12 |
| ML research | Source-specific review text/target inputs with split, provenance, and privacy controls. | Produces versioned prediction/evaluation evidence. | Does not overwrite source truth or join sources. | 8–9 |
| Issue intelligence | Review references, approved taxonomy version, model/run evidence. | Produces conditional review–issue results. | Begins only after Phase 9 taxonomy/annotation/evaluation gate. | 9 |
| Decision support | Review evidence and validated downstream outputs. | Produces explainable assessment/rationale/uncertainty for human review. | No formula, threshold, or automatic punitive action. | 10 |
| Analytical service interface | Approved curated analytical/DSS output. | Delivers analytical service capability to approved future consumers. | Role only; no endpoint names or implementation. | 11 |
| Workflow orchestration | Approved future decision-support event/context. | Coordinates workflow action and human-review handoff. | Never performs model inference; no nodes defined. | 11 |
| Management BI | Curated marts, model/issue/DSS outputs with availability labels. | Management and analytical consumption. | No visuals, page count, DAX, or layout defined. | 12 |

## 2. Source truth, prediction, and decision separation

| Layer | Immutable / derived status | Minimum conceptual trace |
|---|---|---|
| Source truth | Immutable evidence | Review key, source identity, source-row/file lineage, supplied attributes/labels. |
| Model prediction | Derived, repeatable | Review key, model/run identity, task, prediction, confidence, execution/evaluation provenance. |
| Issue result | Derived and conditional | Review key, taxonomy version, issue identity, method/run, result/confidence/evidence. |
| Decision-support output | Derived business assessment | Review key, decision-rule version, priority representation, rationale, uncertainty, evidence, human-review outcome. |
| Track B operational extension | Explicitly synthetic | Synthetic case/event ID, synthetic status, operational event time, synthetic label/version. |

## 3. Requirement-to-architecture traceability

| Requirement | Architecture component | Data entity / output | Consumer | Implementation phase | Validation |
|---|---|---|---|---|---|
| `FR-001`, `DR-001` | Ingestion, transformation, warehouse | `dim_source`, `fact_review` | Analytics/ML | 6 | Provenance and source-row reconciliation. |
| `FR-002`, `BR-007` | Validation | Validation evidence linked to Track A entities | Governance | 6, 13 | Required-field/rating/reconciliation/privacy checks. |
| `FR-003`, `IR-001` | Curated analytics | Source/category review outputs | BI | 7 | No date grain; source/category coverage. |
| `FR-005`, `IR-002` | Curated analytics | `dim_product`, product review outputs | Product-quality reviewer | 7 | Source B `product_id` coverage. |
| `FR-006`, `IR-003` | Curated analytics | `dim_shop`, shop review outputs | Shop-review reviewer | 7 | Non-performance wording and Source B coverage. |
| `FR-004`, `IR-004` | ML research/evaluation | `dim_model`, prediction/evaluation facts | Data-science reviewer | 8 | Source A-only label scope and reproducible evaluation. |
| `FR-007`, `IR-005` | Issue-intelligence layer | `dim_issue`, `fact_issue_prediction` | Product-quality reviewer | 9 | Taxonomy/annotation/evaluation gate. |
| `FR-008`, `IR-006` | Decision-support layer | `fact_decision_support` | Human decision reviewer | 10 | Rationale, uncertainty, audit, human-review validation. |
| `FR-009`, `NFR-001`–`NFR-007` | Curated outputs, service, workflow, BI | Availability-labelled curated outputs | Approved consumers | 7–13 | Traceability, privacy, Track A/B and limitation checks. |

`ORPHAN_ARCHITECTURE_COMPONENTS = 0`

## 4. Anti-overengineering decision

The architecture uses one governed warehouse, curated marts, and phase-owned logical layers. It does not require microservices, event buses, Kubernetes, streaming, lakehouse, distributed processing, cloud infrastructure, or feature stores. Each proposed component has a mapped requirement, owned data/responsibility, consumer, and implementation phase.
