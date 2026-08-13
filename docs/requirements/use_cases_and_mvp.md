# MARKETVOICE SEA — USE CASES & MVP

**Version:** 2.0 (Phase 3 revision)  
**Persona status:** `SIMULATED_BUSINESS_PERSONAS = DESIGN_ASSUMPTIONS`  
**Formal approver:** `PROJECT_OWNER_REVIEWER = USER`

## 1. Persona information needs

| Persona assumption | Information need | Boundary |
|---|---|---|
| CX / management reviewer | Review and rating signals with source limitations. | No authentic time-trend claim. |
| Product-quality reviewer | Product and category review evidence. | Product analysis uses Source B `product_id` only. |
| Shop-review reviewer | Shop-level review indicators. | Not seller performance, quality, compliance, or operational effectiveness. |
| Data-science / governance reviewer | Provided-label baseline, quality, provenance, and limitations. | Source A labels do not label Source B. |
| Human decision reviewer | Priority rationale, uncertainty, and auditable review record. | No automatic action; prioritization depends on later validation. |

No interview was simulated and no persona constitutes stakeholder sign-off.

## 2. Use cases

| ID / priority | Actor | Goal and outcome | Data / availability | Validation / phase |
|---|---|---|---|---|
| `UC-001` MUST | CX reviewer | Review source/category rating signals and their limitations. | A+B review/rating/category — `VERIFIED`. | Totals reconcile; no time grain. Phase 7. |
| `UC-002` MUST | Product-quality reviewer | Identify Source B product listings for review investigation. | B `product_id`, name, rating, text — `VERIFIED`. | Outputs cover verified IDs with provenance. Phase 7. |
| `UC-003` SHOULD | Shop-review reviewer | Review Source B shop-level review indicators. | B `shop_id`, product ID, rating, text — `VERIFIED`. | Wording remains non-punitive and bounded. Phase 7. |
| `UC-004` MUST | Data-science reviewer | Examine provided Source A sentiment/emotion labels as a benchmark. | A labels and review text — `VERIFIED`. | Label scope is source-specific. Phase 8. |
| `UC-005` SHOULD | Product-quality reviewer | Inspect validated candidate issue intelligence and supporting text evidence. | A+B review text — `TO_BE_VALIDATED`. | Phase 9 taxonomy and evaluation gate pass first. Phase 9. |
| `UC-006` SHOULD | Human decision reviewer | Review a proposed priority with rationale and uncertainty, then record a human decision. | Validated analytical outputs — `CONDITIONAL`. | Phase 10 explanation and audit validation. Phase 10. |
| `UC-007` MUST | Governance reviewer | Inspect provenance, data-quality findings, privacy review, and limitations. | Manifest/audit/capability evidence — `VERIFIED`. | Traceability and privacy validation. Phases 6, 13. |

## 3. Authentic-data MVP (Track A)

| Included capability | Source evidence | MVP boundary |
|---|---|---|
| Verified review ingestion and quality validation | Both accepted sources | Preserve provenance and source isolation. |
| Review/rating and category analytics | Both sources | No date-based trends. |
| Baseline sentiment/emotion analysis | Source A only | Labels are provided benchmarks, not issue labels. |
| Product-level review intelligence | Source B only | Uses verified `product_id`; no cross-source match. |
| Shop-level review indicators | Source B only | Informational, non-punitive review experience evidence. |
| Issue-intelligence requirement | Both review-text sources | Capability is specified; taxonomy/classifier is not implemented in MVP. |
| Model/data validation and governance information | Source evidence plus later analytical outputs | Metrics and targets are defined in their future analytical phases. |
| Explainable decision-support requirement | Later validated outputs | Human review mandatory; no priority formula in Phase 3. |

## 4. Track B — explicitly deferred

Track B is not part of the authentic-data MVP: synthetic timeline, operational cases, SLA/resolution workflow, workflow orchestration, production API, live marketplace integration, and temporal alerts. Future operational demonstration data requires separate approval and must be clearly labelled synthetic; it cannot contain customer identity, personal profiles, or real review timestamps.

## 5. MVP acceptance boundary

The MVP is ready for later implementation only when every MUST use case has a traced requirement chain, uses verified data, and includes an acceptance criterion. A capability with `CONDITIONAL`, `NOT_AVAILABLE`, or `TO_BE_VALIDATED` status cannot be presented as an authentic MVP result.
