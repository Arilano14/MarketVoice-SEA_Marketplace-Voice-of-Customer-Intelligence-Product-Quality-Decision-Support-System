# MARKETVOICE SEA — SYSTEM REQUIREMENTS

**Version:** 2.0 (Phase 3 revision)  
**Phase scope:** Logical capabilities and acceptance criteria only  
**Architecture status:** `FINAL_ARCHITECTURE = PHASE_5_DECISION`  
**Gate status:** `PHASE_3_GATE = NOT_EVALUATED`

## 1. Functional requirements

| ID / priority | Capability requirement | Availability / future phase | Acceptance criteria |
|---|---|---|---|
| `FR-001` MUST | The system shall normalize verified review sources into a consistent analytical representation while preserving source provenance and original identifiers. | `VERIFIED`; Phase 6. | Each represented record identifies its source; Source A and B remain independently traceable. |
| `FR-002` MUST | The system shall validate required review fields, rating validity, completeness, and reconciliation results before analytical use. | `VERIFIED`; Phase 6. | Validation records identify deviations and reconcile analytical input to accepted source counts. |
| `FR-003` MUST | The system shall provide review and rating analytical capability at source and category grain. | `VERIFIED`; Phase 7. | Results distinguish sources and do not produce temporal analyses. |
| `FR-004` MUST | The system shall provide Source A baseline analysis for its provided sentiment and emotion labels. | `VERIFIED`; Phase 8. | Outputs retain the Source A-only qualification and reconcile to all label-bearing records. |
| `FR-005` MUST | The system shall provide Source B product-level review intelligence using verified `product_id`. | `VERIFIED`; Phase 7. | Product outputs preserve Source B provenance and cover verified product identifiers. |
| `FR-006` SHOULD | The system shall provide Source B shop-level review indicators using verified `shop_id`. | `VERIFIED`; Phase 7. | Outputs describe review experience indicators only; they make no seller-performance or enforcement claim. |
| `FR-007` SHOULD | The system shall support issue-intelligence outputs only after issue taxonomy, annotation, method, and evaluation are validated. | `TO_BE_VALIDATED`; Phase 9. | Pre-Phase-9 outputs are labelled candidate/conditional; no issue taxonomy is presented as verified. |
| `FR-008` SHOULD | The system shall support explainable human-review prioritization with rationale, uncertainty, and audit reference. | `CONDITIONAL`; Phase 10. | A reviewer can inspect the rationale and record a human decision; no automated punitive action occurs. |
| `FR-009` SHOULD | The system shall make the required management information domains available: Executive Overview, Voice of Customer, Product Review Quality, Issue Intelligence, Decision Support, Model Validation, and Data Quality & Governance. | Mixed availability; Phases 7–12. | Each information domain identifies its source, availability, limitation, and implementation dependency. This requirement does not prescribe a reporting tool, page, visual, or layout. |

## 2. Non-functional requirements

| ID / priority | Requirement | Validation / future phase |
|---|---|---|
| `NFR-001` MUST | Analytical outputs shall preserve source provenance, original identifiers where present, and analytical lineage. | Traceability and reconciliation review; Phases 6, 13. |
| `NFR-002` MUST | The system shall not intentionally enrich PII, create customer profiles, or expose review text without a documented privacy review. | Privacy-review and output inspection; Phases 6, 13. |
| `NFR-003` MUST | The system shall maintain an auditable record of source limitations, data-quality findings, transformations, and human decisions relevant to decision support. | Auditability review; Phases 6, 10, 13. |
| `NFR-004` MUST | Decision-support outputs shall be explainable, display relevant uncertainty or confidence, and require human review before consequential action. | Scenario validation; Phases 10, 13. |
| `NFR-005` MUST | The system shall be reproducible from approved source evidence and shall not silently alter raw datasets. | Reproducibility and raw-integrity review; Phases 6, 13. |
| `NFR-006` MUST | The system shall clearly distinguish authentic evidence from any future approved synthetic operational demonstration. | Synthetic-governance inspection if Track B is approved; Phases 10–13. |
| `NFR-007` MUST | The system shall not present NPS, CSAT, real temporal trends, seller performance, or operational SLA effectiveness unless authentic supporting data is later approved. | Claims and documentation audit; every downstream phase. |

## 3. Explicit design deferrals

Phase 3 does not select a database, tables, interfaces, endpoints, orchestration nodes, reporting technology, physical data model, ML algorithm, annotation size, or priority formula. Those choices are made and validated in their respective future phases.
