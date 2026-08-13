# MARKETVOICE SEA — REQUIREMENTS TRACEABILITY

**Version:** 2.0 (Phase 3 revision)  
**Traceability rule:** Business Objective → Business Question → BR → IR → FR → DR → UC → Future Phase → Validation

| Objective | BQ | BR | IR | FR | DR | UC | Future phase | Validation |
|---|---|---|---|---|---|---|---|---|
| Customer-experience understanding | `BQ-001` | `BR-001` | `IR-001` | `FR-001`, `FR-002`, `FR-003` | `DR-001`, `DR-002` | `UC-001` | 6–7 | Row reconciliation; source/category grain; no temporal claim. |
| Product-quality investigation | `BQ-002` | `BR-002` | `IR-002` | `FR-005` | `DR-001`–`DR-003` | `UC-002` | 6–7 | Source B product coverage and provenance. |
| Bounded shop-review context | `BQ-003` | `BR-003` | `IR-003` | `FR-006` | `DR-003` | `UC-003` | 6–7 | Source B shop coverage and non-performance wording. |
| Provided-label baseline | `BQ-001`, `BQ-006` | `BR-004` | `IR-004` | `FR-004` | `DR-004` | `UC-004` | 8 | Source A-only label scope and class reconciliation. |
| Validated issue intelligence | `BQ-004` | `BR-005` | `IR-005` | `FR-007` | `DR-005` | `UC-005` | 9 | Taxonomy, annotation, and evaluation validation. |
| Accountable decision support | `BQ-005` | `BR-006` | `IR-006` | `FR-008` | `DR-002`, `DR-005` | `UC-006` | 9–10 | Rationale, uncertainty, audit, and human-review validation. |
| Governance and responsible use | `BQ-006` | `BR-007` | `IR-007` | `FR-002`, `FR-009` | `DR-001`, `DR-006` | `UC-007` | 6, 13 | Provenance, privacy-review, limitation, and quality checks. |

## MUST requirement completeness

| MUST requirement | Traceable chain complete | Data status | Disposition |
|---|---|---|---|
| `BR-001` | Yes | `VERIFIED` | Track A |
| `BR-002` | Yes | `VERIFIED` | Track A |
| `BR-004` | Yes | `VERIFIED` | Track A |
| `BR-007` | Yes | `VERIFIED` | Track A |
| `FR-001`–`FR-005` | Yes | `VERIFIED` | Track A |
| `NFR-001`–`NFR-007` | Yes | Requirement/governance-controlled | Applies to applicable future phases |

`ORPHAN_MUST_REQUIREMENTS = 0`  
`CROSS_SOURCE_PRODUCT_LINKAGE = NOT_APPROVED`  
`AUTHENTIC_TIME_TREND_ANALYTICS = NOT_SUPPORTED`

## Conditional traceability

| Requirement | Dependency | Disposition |
|---|---|---|
| `BR-005` / `IR-005` / `FR-007` / `DR-005` / `UC-005` | Phase 9 taxonomy, annotation, and evaluation gate | Conditional Track B capability; not an authentic MVP result. |
| `BR-006` / `IR-006` / `FR-008` / `UC-006` | Validated outputs from Phases 8–9 and Phase 10 design | Conditional Track B capability; priority formula is deferred. |
| `FR-009` | Source-specific information availability and later reporting phase | Information need only; no implementation technology selected. |
