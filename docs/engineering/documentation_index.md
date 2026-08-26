# MarketVoice SEA — Documentation Index & Architecture Sitemap

**Document Version**: 1.0  
**Scope**: Authoritative Single Source of Truth Mapping across Architecture, Engineering, Governance, Research, and Validation Suites.

---

## 1. Governance & Project Foundations

| Topic | Canonical File Path | Description |
|---|---|---|
| **Project Charter** | [`docs/governance/project_charter.md`](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/docs/governance/project_charter.md) | Business rationale, stakeholders, scope boundaries, and high-level milestones. |
| **Definition of Done** | [`docs/governance/project_definition_of_done.md`](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/docs/governance/project_definition_of_done.md) | Quality gates and deliverables criteria for all 15 project phases. |
| **Phase Gate Register** | [`docs/governance/phase_gates.md`](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/docs/governance/phase_gates.md) | Formal audit checklist and pass/fail gate log for Phases 0 through 14. |
| **Data Governance Policy** | [`docs/governance/data_governance_policy.md`](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/docs/governance/data_governance_policy.md) | Local-only dataset rules, PII protection, and source provenance standards. |
| **Synthetic Data Policy** | [`docs/governance/synthetic_data_policy.md`](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/docs/governance/synthetic_data_policy.md) | Guidelines for synthetic event demonstrations and validation fixtures. |
| **Risk & Assumptions** | [`docs/governance/risk_and_assumption_register.md`](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/docs/governance/risk_and_assumption_register.md) | Risk register, mitigations, and architectural assumptions. |

---

## 2. Requirements & Traceability

| Topic | Canonical File Path | Description |
|---|---|---|
| **Requirements Baseline** | [`docs/requirements/business_and_information_requirements.md`](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/docs/requirements/business_and_information_requirements.md) | Core business requirements, information model, and functional capabilities. |
| **Traceability Matrix** | [`docs/requirements/requirements_traceability.md`](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/docs/requirements/requirements_traceability.md) | End-to-end mapping from business requirements to deliverables (DEL-01–29). |
| **System Requirements** | [`docs/requirements/system_requirements.md`](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/docs/requirements/system_requirements.md) | Technical stack, OS, Python, and PostgreSQL environment requirements. |
| **Use Cases & MVP** | [`docs/requirements/use_cases_and_mvp.md`](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/docs/requirements/use_cases_and_mvp.md) | Operational triage scenarios for QA leads and product operations managers. |

---

## 3. Architecture & Data Engineering

| Topic | Canonical File Path | Description |
|---|---|---|
| **System Architecture** | [`docs/architecture/solution_architecture.md`](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/docs/architecture/solution_architecture.md) | End-to-end microservice, ETL, warehouse, and BI architecture. |
| **Data Architecture** | [`docs/architecture/data_architecture.md`](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/docs/architecture/data_architecture.md) | Data ingestion flow, staging layers, partition design, and storage policies. |
| **Dimensional Model** | [`docs/architecture/dimensional_model.md`](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/docs/architecture/dimensional_model.md) | Kimball star schema specifications (conformed dimensions, fact_review, additive marts). |
| **Integration Contracts** | [`docs/architecture/integration_contracts.md`](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/docs/architecture/integration_contracts.md) | Service boundary interfaces between FastAPI, PostgreSQL, and n8n. |

---

## 4. Engineering Specifications

| Topic | Canonical File Path | Description |
|---|---|---|
| **API Contract** | [`docs/engineering/api_contract.md`](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/docs/engineering/api_contract.md) | OpenAPI REST contract for review analysis and contextual decision evaluation. |
| **n8n Workflow Design** | [`docs/engineering/n8n_workflow_design.md`](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/docs/engineering/n8n_workflow_design.md) | 12-node DAG topology, switch routing rules, and idempotency ledger logic. |
| **Data Transformations** | [`docs/engineering/data_transformation_contract.md`](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/docs/engineering/data_transformation_contract.md) | Column-level casting, cleaning, null imputation, and encoding contracts. |
| **Category Mapping** | [`docs/engineering/category_harmonization_mapping.md`](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/docs/engineering/category_harmonization_mapping.md) | Cross-source taxonomy harmonization between Shopee and Tokopedia. |
| **Operational Runbook** | [`docs/operations/operational_runbook.md`](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/docs/operations/operational_runbook.md) | Service launch instructions, readiness checks, and Human-in-the-Loop case resolution. |

---

## 5. Research & Methodology

| Topic | Canonical File Path | Description |
|---|---|---|
| **Research Design** | [`docs/methodology/analytical_research_design.md`](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/docs/methodology/analytical_research_design.md) | Research questions (RQ1–RQ4), statistical hypotheses, and validation protocols. |
| **Issue Taxonomy** | [`docs/research/issue_taxonomy.md`](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/docs/research/issue_taxonomy.md) | 7-category product quality issue taxonomy and aspect keyword catalogs. |
| **Decision Support** | [`docs/research/decision_support.md`](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/docs/research/decision_support.md) | Multi-criteria Priority Ranking Score (PRS) mathematics and sensitivity analysis. |
| **Annotation Protocol** | [`docs/research/issue_annotation_protocol.md`](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/docs/research/issue_annotation_protocol.md) | Gold validation benchmark sampling, annotation guidelines, and inter-rater metrics. |

---

## 6. Audit, Validation Evidence & History

| Topic | Canonical Directory / Path | Description |
|---|---|---|
| **Phase Validation Evidence** | [`reports/validation/`](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/reports/validation/) | 14 formal validation reports containing immutable empirical evidence (Phases 1–11). |
| **Technical Development History** | [`reports/archive/project_development_history.txt`](file:///C:/Users/Arilano/Downloads/Project%20ARICE/Project%20SEA/reports/archive/project_development_history.txt) | Consolidated historical chronicle of architecture decisions and milestones. |
