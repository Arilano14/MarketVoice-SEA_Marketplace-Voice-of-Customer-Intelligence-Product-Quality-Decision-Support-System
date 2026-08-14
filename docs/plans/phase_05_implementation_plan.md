# MARKETVOICE SEA — PHASE 5 IMPLEMENTATION PLAN

**Phase:** 5 — Solution Architecture & Logical Data Model

**Document Version:** 1.0 (Implementation Ready)

**Date Created:** 2026-08-14

**Status:** `PHASE_5_PLAN_STATUS = READY_FOR_HUMAN_REVIEW`

**Authority:** Phase 4 forensic audit completed; all technical prerequisites satisfied.

---

## EXECUTIVE PURPOSE

Phase 5 transforms Phase 3 business/system requirements and Phase 4 analytical research design into a detailed **logical solution architecture and dimensional data model** ready for implementation.

Phase 5 explicitly does **NOT** include:
- Database DDL (that is Phase 6)
- ETL implementation (Phase 6)
- Data loading (Phase 6)
- Model training (Phase 8)
- Issue taxonomy creation (Phase 9)
- Decision-support formulas (Phase 10)
- API/FastAPI/n8n/Power BI implementation (Phases 11-12)
- Synthetic data generation (Phase 10/11, conditional)

Phase 5 specifies **what logical entities, relationships, and contracts are needed** so Phase 6 and later phases know exactly what to build and hand off.

---

## VERIFIED ENTRY CONDITIONS

### Phase 0 — Governance & Scope ✓
- **Technical Status:** PASS (Project Charter, Governance Policy, Traceability Matrix complete)
- **Human Review Status:** APPROVED (documented in repository)
- **Evidence:** docs/governance/project_charter.md, docs/governance/data_governance_policy.md

### Phase 1 — Environment & Data Acquisition ✓
- **Technical Status:** PASS (Python 3.10, PostgreSQL available, Git configured, datasets downloaded)
- **Human Review Status:** APPROVED (implicit in project setup)
- **Evidence:** docs/engineering/development_environment.md, data/raw/ directories populated

### Phase 2 — Dataset Forensic Audit & Readiness ✓
- **Technical Status:** PASS (Source A: 5,400 rows; Source B: 40,607 rows; checksums verified)
- **Human Review Status:** APPROVED (documented in phase_02_dataset_forensic_audit_report.md)
- **Evidence:** data/metadata/ validation reports and source manifest

### Phase 3 — Business & System Requirements ✓
- **Technical Status:** COMPLETE (BRD v2.0, SRS v2.0, RTM v2.0, traceability verified)
- **Human Review Status:** PENDING (awaiting project owner approval signature)
- **Gate Status:** AWAITING_HUMAN_APPROVAL (external blocker, not a technical defect)
- **Evidence:** docs/requirements/, docs/governance/phase_gates.md v4.2

### Phase 4 — Research & Analytical Design ✓
- **Technical Status:** COMPLETE (all artifacts created and validated)
- **Validation Status:** PASS (80 empirical checks completed)
- **Human Review Status:** PENDING (awaiting project owner approval)
- **Gate Status:** AWAITING_PHASE_3_APPROVAL (external blocker; Phase 4 is technically ready)
- **Evidence:** reports/validation/phase_04_forensic_audit_and_remediation.md

### Phase 5 Entry Readiness
```
Phase 3 technical = COMPLETE
Phase 3 human approval = PENDING (external gate)
Phase 4 technical = COMPLETE
Phase 4 human approval = PENDING (external gate, dependent on Phase 3)

PHASE_5_CAN_PLAN = TRUE (now)
PHASE_5_CAN_EXECUTE = BLOCKED until Phase 3 & 4 gates PASS
```

---

## DECISION: PLAN NOW, EXECUTE LATER

This run creates the implementation plan. Execution requires:
1. Phase 3 gate approval
2. Phase 4 gate approval  
3. **Separate explicit user authorization** for Phase 5 execution

---

## SOURCE-OF-TRUTH MATRIX

Phase 5 implementation will consume and reference these frozen artifacts:

| Artifact | Source | Role | Frozen? |
|---|---|---|---|
| Project Charter | docs/governance/project_charter.md | Scope, positioning, boundaries | ✓ Yes |
| Data Governance Policy | docs/governance/data_governance_policy.md | Privacy, PII, compliance constraints | ✓ Yes |
| Synthetic Data Policy | docs/governance/synthetic_data_policy.md | Track A/B rules | ✓ Yes |
| Business Requirements v2.0 | docs/requirements/business_and_information_requirements.md | Business objectives and questions | ✓ Yes (v2.0) |
| System Requirements v2.0 | docs/requirements/system_requirements.md | Functional/non-functional requirements | ✓ Yes (v2.0) |
| Requirements Traceability v2.0 | docs/requirements/requirements_traceability.md | BQ → BR → IR → FR → DR mapping | ✓ Yes (v2.0) |
| Phase 2 Audit Report | reports/validation/phase_02_dataset_forensic_audit_report.md | Data reality, capabilities, limitations | ✓ Yes |
| Data Capability Matrix | data/metadata/data_capability_matrix.csv | Feature/field availability by source | ✓ Yes |
| Source Manifest | data/metadata/source_manifest.csv | Checksums, publishers, versions | ✓ Yes |
| Analytical Research Design | docs/methodology/analytical_research_design.md | Evidence lock, RQ mapping, dataset roles | ✓ Yes |
| Experiment Protocol | docs/methodology/experiment_protocol.md | Split strategy, leakage controls, baselines | ✓ Yes |
| Evaluation Protocol | docs/methodology/evaluation_protocol.md | Metrics, champion selection, error analysis | ✓ Yes |
| Experiment Configuration | config/experiment_settings.yaml | Governance, datasets, tasks, split, evaluation | ✓ Yes |

All locked as of Data Foundation Version 1.0.

---

## ARCHITECTURE INPUT RECONCILIATION

### Evidence Corrections & Clarifications

| Finding | Status | Evidence | Impact on Architecture |
|---|---|---|---|
| Phase 3 gate currently NOT_EVALUATED (not PASS) | Verified in phase_03_validation.md; phase_gates.md v4.2 corrected | External blocker, not technical defect | Architecture proceeds to specification; execution blocked until approval |
| Source A has no authentic product identifier | Verified: product_name text only, no product_id | Prevents Source A → dim_product linkage | Product dimension is Source B `product_id` only |
| Source B has no review timestamps | Verified: no date column in raw data | Prevents time-grain dimensions and trend analytics | No `dim_date` or temporal keys; source/category/product/shop grain only |
| Cross-source row linkage unsupported | Verified in Phase 2; locked in analytical_research_design.md §1 | Fact and dimensional isolation | No view or physical join across Source A and B fact records |
| Source A is sole sentiment/emotion gold label | Verified: Source B has no sentiment/emotion columns | Forces source-specific task design | `fact_model_prediction` for sentiment/emotion references SRC_PRDECT_ID_V1 only |
| Ordinal rating semantics (1 < 2 < 3 < 4 < 5) | Verified in evaluation_protocol.md | Evaluation includes QWK and MAE | Dimensional model supports 1–5 rating dimension without invented ordering |

All clarifications incorporated into Phase 5 architecture below.

---

## LOCKED SCOPE DEFINITION

### IN SCOPE — Phase 5 Responsibilities

| Category | Item | Phase 5 creates | Phase 6+ implements |
|---|---|---|---|
| **Architecture** | Solution architecture diagram | Logical flow diagram (.md + mermaid) | Infrastructure/cloud diagram |
| **Logical Model** | Dimensional model specification | Entity definitions, grain, attributes, relationships | DDL, indexes, partitions |
| **Lineage** | Data lineage concept | Source → validation → staging → warehouse → marts → outputs | ETL implementation |
| **Entities** | Core Track A entities (dimensions and facts) | Logical grain, keys, attributes, relationships | Physical design, surrogate keys, compression |
| **Contracts** | Consumer output contracts | Logical output structure, lineage, quality metadata | Endpoint/payload/report implementation |
| **Traceability** | Phase 3/4 → Phase 5 architecture mapping | Requirement trace to architectural component | Implementation code trace |
| **Track A/B** | Separation policy and structure | Logical isolation of authentic vs. synthetic | Warehouse schema isolation, row flags |
| **Validation** | Data quality responsibility | What must be validated and recorded | Quality control implementation |

### OUT OF SCOPE — Phase 6+ Responsibilities

| Item | Reason | Deferred Phase |
|---|---|---|
| PostgreSQL DDL | Physical database design decision | 6 |
| ETL code (Python/SQL) | Implementation responsibility | 6 |
| Data loading | Execution responsibility | 6 |
| Schema/indexes/partitions | Physical tuning | 6 |
| Referential integrity enforcement | Database implementation | 6 |
| Privacy review | Governance approval (per Phase 3) | 6, 13 |
| Model training | ML responsibility | 8 |
| Issue taxonomy | Research responsibility | 9 |
| Decision-support formulas | Business logic responsibility | 10 |
| API/FastAPI implementation | Service responsibility | 11 |
| n8n workflow nodes | Orchestration responsibility | 11 |
| Power BI reports/DAX | BI responsibility | 12 |
| Synthetic data generation | Track B conditional approval | 10/11 |

---

## ARCHITECTURE OBJECTIVES

Phase 5 logical architecture must satisfy every MUST requirement from Phase 3 and every research objective from Phase 4.

| Objective | Requirement trace | Architecture decision |
|---|---|---|
| Preserve source provenance end-to-end | FR-001, NFR-001, NFR-005 | `fact_review` and all derived facts retain source identifier and source-row lineage |
| Enable source-specific independent analysis | FR-003, IR-001, IR-002, IR-003 | Track A facts use source as natural grain; Source A and B products/shops never cross-join |
| Provide sentiment/emotion benchmark | FR-004, IR-004 | `fact_model_prediction` for Source A sentiment/emotion; other sources explicitly null/not applicable |
| Support product-level intelligence | FR-005, IR-002 | `dim_product` grain per Source B `product_id`; no inferred Source A products |
| Support bounded shop indicators | FR-006, IR-003 | `dim_shop` grain per Source B `shop_id`; shop language limited to review-experience indicators (no seller-performance claims) |
| Support reproducible ML research | FR-004, NFR-003 | `dim_model`, `fact_model_prediction`, `fact_model_evaluation` with full experiment/split/seed/preprocessing metadata |
| Support future issue intelligence | FR-007 | `dim_issue`, `fact_issue_prediction` with versioned taxonomy reference; conditional on Phase 9 approval |
| Support explainable decision support | FR-008, NFR-004 | `fact_decision_support` with rationale, uncertainty, evidence reference, human-review outcome |
| Enable auditable review management | NFR-003 | All Track A facts reference source lineage and validation status |
| Prevent PII enrichment | NFR-002 | Architecture does not create customer profiles or intentional PII relationships; review text is tracked as sensitive |
| Support Track A / Track B separation | Synthetic Data Policy | `fact_case` and `fact_intervention` explicitly marked synthetic and isolated from authentic review facts |
| Maintain reproducibility | NFR-005 | Every fact and output traces to frozen source evidence and versioned methodology |

---

## LOGICAL ARCHITECTURE DOMAINS

Phase 5 establishes six logical architectural domains (not physical schemas; schemas are Phase 6):

### Domain 1: Source Evidence
**Purpose:** Immutable record of accepted analytical data sources.

**Entities:**
- `dim_source` — One row per registered analytical source (PRDECT-ID v1, Tokopedia Reviews 2019)

**Characteristics:**
- Grain: One source per row
- Keys: source_id (SRC_PRDECT_ID_V1, SRC_TOKOPEDIA_REVIEWS_2019)
- Lineage: Publisher, version, license, checksum, ingestion reference
- Locked Data:** Both sources frozen; no new sources without separate Phase 3 requirement approval

---

### Domain 2: Track A Core Facts & Dimensions
**Purpose:** Authentic review evidence and normalized canonical dimensions.

**Entities:**
- `fact_review` — One row per verified review from exactly one source
  - Grain: One source-native review row
  - Natural key: source_id + source_row_identifier
  - Attributes: review_text_reference, supplied_rating, source_category
  - Optional references: Source B `product_id`, Source B `shop_id` (null for Source A)
  - Source A only: provided_sentiment, provided_emotion
  - Quality: validation_status, reconciliation_reference, privacy_review_status

- `dim_rating` — One row per permitted rating value (1, 2, 3, 4, 5)
  - Grain: One valid rating value
  - Key: rating_value
  - Attributes: rating_display_value, rating_order (1 < 2 < 3 < 4 < 5)
  - Supports ordinal semantics for evaluation

- `dim_category` — One row per raw category within one source
  - Grain: One source-specific category
  - Key: source_id + category_raw_value
  - Rationale: Categories are not proven conformable across sources
  - Attributes: category_display, source_reference

- `dim_product` — One row per Source B product listing
  - Grain: One unique Source B `product_id`
  - Key: `product_id` (Source B business key)
  - Attributes: product_name, category_reference, source_reference
  - Source A exclusion: Source A product-name text is review-context only; no Source A products in this dimension

- `dim_shop` — One row per Source B shop context
  - Grain: One unique Source B `shop_id`
  - Key: `shop_id` (Source B business key)
  - Attributes: source_reference
  - Semantics: Review-experience indicators only; no seller-performance claims

**Relationships:**
- `fact_review` → `dim_source` (required, many-to-one)
- `fact_review` → `dim_rating` (required, many-to-one)
- `fact_review` → `dim_category` (required, many-to-one)
- `fact_review` → `dim_product` (optional for Source B, null for Source A, many-to-one)
- `fact_review` → `dim_shop` (optional for Source B, null for Source A, many-to-one)

---

### Domain 3: ML Research & Evaluation (Phase 8–9)
**Purpose:** Store reproducible model/issue research results separate from source truth.

**Entities:**
- `dim_model` — One row per unique model version and run identity
  - Grain: One model identifier + one experiment run
  - Key: model_id, experiment_run_id
  - Attributes: task, model_architecture, training_environment, source_reference, split_identifier, seed, preprocessing_version
  - Traceability: Links to experiment configuration (Phase 4 frozen)

- `fact_model_prediction` — One row per model prediction for one review, one task, one model/run
  - Grain: One review + one task + one model/run + one candidate
  - Key: review_key + model_run_id + task_id
  - Attributes: predicted_label, prediction_confidence, prediction_probability_distribution
  - Never overwrites source truth; separate logical layer

- `fact_model_evaluation` — One row per evaluated model, task, source, and split
  - Grain: One model + one task + one source + one evaluation split
  - Attributes: All metrics specified in evaluation_protocol.md (Accuracy, F1, Precision, Recall, QWK, MAE, confusion_matrix, coverage)
  - References: Model identity, evaluation split (train/validation/holdout), target metrics
  - No predeclared success thresholds; interpretation identifies class distribution, exclusions, limitations

- `dim_issue` — One row per approved issue identity in one taxonomy version
  - Grain: One issue within one taxonomy version
  - Key: taxonomy_version_id + issue_id
  - Attributes: issue_definition, approval_status
  - Activation: Only after Phase 9 taxonomy/annotation/evaluation approval

- `fact_issue_prediction` — One row per review–issue result for one method and model/run
  - Grain: One review + one issue + one method/run
  - Key: review_key + issue_id + method_run_id
  - Attributes: result, confidence, evidence_reference
  - Audit: Links to Phase 9 taxonomy/evaluation evidence

**Relationships:**
- `fact_model_prediction` → `fact_review` (required, many-to-one)
- `fact_model_prediction` → `dim_model` (required, many-to-one)
- `fact_model_evaluation` → `dim_model` (required, many-to-one)
- `fact_model_evaluation` → `dim_source` (required, many-to-one)
- `fact_issue_prediction` → `fact_review` (required, many-to-one)
- `fact_issue_prediction` → `dim_issue` (required, many-to-one)

---

### Domain 4: Decision Support (Phase 10)
**Purpose:** Explainable assessment results for human review and decision-making.

**Entities:**
- `fact_decision_support` — One row per decision assessment for one review and rule version
  - Grain: One review + one decision rule version + one assessment
  - Key: review_key + decision_rule_version_id + assessment_id
  - Attributes: priority_representation, priority_rationale, uncertainty_assessment, evidence_references, human_review_status, human_review_outcome, human_review_decision
  - Properties:
    - Explicit rationale (why this review, why this priority)
    - Uncertainty/confidence disclosure
    - No automated punitive action
    - Required human review before consequential decision
    - Reversible (decision can be overridden)

**Relationships:**
- `fact_decision_support` → `fact_review` (required, many-to-one)
- `fact_decision_support` → applicable `fact_model_prediction` / `fact_issue_prediction` (optional reference for rationale)

---

### Domain 5: Track B Synthetic Extension (Phase 10/11, Conditional)
**Purpose:** Explicitly separate operational synthetic case and workflow data from authentic evidence.

**Entities:**
- `fact_case` — One explicitly synthetic operational case
  - Grain: One synthetic case identifier
  - Key: case_id (synthetic, non-identifying)
  - Attributes: synthetic_status (always TRUE), priority_level, case_status, created_date (operational, not review date)
  - Relationship to reviews: Optional reference to `fact_review` for context only; never as parent
  - Track: B only; must be visibly separate from Track A

- `fact_intervention` — One explicitly synthetic intervention event
  - Grain: One synthetic intervention identifier
  - Key: event_id (synthetic, non-identifying)
  - Attributes: synthetic_status (always TRUE), intervention_type, event_status, event_date (operational, not review date)
  - Relationship to cases: Many-to-one to `fact_case`
  - Audit: Intervention never overwrites review truth or decision status

**Relationships:**
- `fact_case` → `fact_review` (optional reference, never as parent)
- `fact_intervention` → `fact_case` (many-to-one)

**Characteristics:**
- Track A/B separation is enforced logically (all Track B facts explicitly flagged)
- Track B event dates are never confused with authentic review time
- Track B data is conditional on Phase 10/11 approval and not generated until then

---

### Domain 6: Curated Analytical Outputs (Phase 7–12)
**Purpose:** Presentation-ready aggregations and quality metadata.

**Entities:**
- Curated marts (logical views/tables):
  - Source/category review summaries (supporting BI, FR-003)
  - Product review intelligence (Source B only, FR-005)
  - Shop review indicators (Source B only, FR-006)
  - Quality/coverage metadata (all Track A outputs)

**Characteristics:**
- Source-aware (every output retains source identity)
- No time grain (no authentic time trends)
- Limitation-labeled (every output states its source, method, and known limitations)
- Not derived from cross-source joins
- Phase 7 specification will detail each mart structure

---

## GRAIN REGISTER

Every proposed logical entity must have explicit grain justification.

| Entity | Grain | Business Justification | Source | Natural Key | Versioned? |
|---|---|---|---|---|---|
| `dim_source` | One analytical source | Foundational lineage for all Track A facts | Phase 2 manifest | source_id | No (frozen v1.0) |
| `dim_rating` | One rating value (1–5) | Enables ordinal semantics and classification metrics | Both sources | rating_value | No (finite domain) |
| `dim_category` | One raw category per source | Preserves source-local category without forced conformance | Both sources | source_id + category_value | Source-specific only |
| `dim_product` | One Source B product listing | Supports product-level review intelligence (FR-005) | B only | product_id | Source B identity only |
| `dim_shop` | One Source B shop context | Supports shop-level review indicators (FR-006) | B only | shop_id | Source B identity only |
| `fact_review` | One review row from exactly one source | Unit of analysis for all downstream tasks | Both sources | source_id + source_row_id | Both sources, independently |
| `dim_model` | One model version + one experiment run | Reproducible research tracking (NFR-003) | Phase 8+ | model_id + experiment_run_id | Versioned per run |
| `fact_model_prediction` | One review + one task + one model/run | Track predictions separately from source truth | Phase 8+ | review_key + model_run_id + task_id | Repeatable per run |
| `fact_model_evaluation` | One model + one task + one source + one split | Evaluation results per source and split (no pooling) | Phase 8+ | model_id + task_id + source_id + split_id | Versioned per run |
| `dim_issue` | One issue in one taxonomy version | Support versioned, auditable taxonomy evolution | Phase 9+ | taxonomy_version_id + issue_id | Versioned with taxonomy |
| `fact_issue_prediction` | One review + one issue + one method/run | Track issue predictions separately from source truth | Phase 9+ | review_key + issue_id + method_run_id | Repeatable per run |
| `fact_decision_support` | One review + one rule version + one assessment | Enable explainable, auditable human decision | Phase 10+ | review_key + rule_version_id + assessment_id | Versioned per rule change |
| `fact_case` | One synthetic operational case (conditional) | Track B: operational workflow context distinct from reviews | Phase 10/11 | case_id | Synthetic labeling required |
| `fact_intervention` | One synthetic operational event (conditional) | Track B: support multiple events per case | Phase 10/11 | event_id | Synthetic labeling required |

---

## SOURCE OWNERSHIP MATRIX

For every logical field in the model, designate authoritative source.

| Logical Field | Entity | Source A | Source B | Phase 5 Decision |
|---|---|---|---|---|
| review_text | fact_review | Yes (Customer Review) | Yes (text) | Both sources supply; preserve original reference |
| supplied_rating | fact_review | Yes (Customer Rating) | Yes (rating) | Both sources supply independently; source-specific analysis |
| category | dim_category / fact_review | Yes (Category) | Yes (category) | Source-specific categories; no cross-source mapping |
| product_name | fact_review context OR dim_product | A: product-name text only (not a key) | B: product_id + product_name | No Source A → product dimension linkage |
| product_id | dim_product | Not available | Yes (product_id) | Source B only; Source A has no product identifier |
| shop_id | dim_shop | Not available | Yes (shop_id) | Source B only; no cross-source shop reference |
| sentiment | fact_review attribute | Yes (Sentiment) | Not available | Source A only; never imputed to Source B |
| emotion | fact_review attribute | Yes (Emotion) | Not available | Source A only; never imputed to Source B |
| location | fact_review context | Yes (Location) | Not available | Source A only; review context only |
| price | fact_review context | Yes (Price) | Not available | Source A only; review context only |
| overall_rating | fact_review context | Yes (Overall Rating) | Not available | Source A only; review context only |
| number_sold | fact_review context | Yes (Number Sold) | Not available | Source A only; review context only |
| total_review | fact_review context | Yes (Total Review) | Not available | Source A only; review context only |
| sold | fact_review context | Not available | Yes (sold, with 14 nulls and formatting issues) | Source B only; quality limitation documented |
| product_url | Not included in core model | Not available | Yes (product_url) | Restricted from public analytics by default (Phase 6 privacy review) |

---

## KEY & IDENTIFIER POLICY

### Surrogate Key Strategy

| Entity | Business Key | Surrogate Key? | Rationale |
|---|---|---|---|
| `dim_source` | source_id | No | Small dimension; business key is stable identifier |
| `dim_rating` | rating_value | No | 5-member fixed domain; business key is natural and immutable |
| `dim_category` | source_id + category_value | Optional (Phase 6 decision) | Stable within source; surrogate may simplify joins or preserve history |
| `dim_product` | product_id | Optional (Phase 6 decision) | Preserve `product_id` in model; surrogate for internal warehouse joins |
| `dim_shop` | shop_id | Optional (Phase 6 decision) | Preserve `shop_id` in model; surrogate for internal warehouse joins |
| `fact_review` | source_id + source_row_id | Required for linea | Surrogate enables stable internal key; business key for audit trail |
| `dim_model` | model_id + experiment_run_id | Required | Internal versioning; research identity must be preserved |
| `fact_model_prediction` | review_key + model_run + task | Required | Allows repeatable runs without overwriting |
| `fact_model_evaluation` | model + task + source + split | Required | Evaluation identity per experiment family |
| `dim_issue` | taxonomy_version + issue_id | Required | Prevents meaning shift when taxonomy evolves |
| `fact_issue_prediction` | review + issue + method_run | Required | Separates method versions without label overwrite |
| `fact_decision_support` | review + rule_version + assessment | Required | Preserves audit history and re-assessment capability |
| `fact_case` | case_id (synthetic) | Yes, non-identifying | Track B identity is not customer/case ID; purely operational |
| `fact_intervention` | event_id (synthetic) | Yes, non-identifying | Track B identity is not operational event ID; purely workflow |

### Linkage Classification

| Relationship | Classification | Validation | Policy |
|---|---|---|---|
| Source A review → Source B product | NOT_LINKABLE | Phase 2 evidence: Source A has no product_id | Forbidden; Source A product_name never joins dim_product |
| Source A review → Source B shop | NOT_LINKABLE | Phase 2 evidence: Source A has no shop_id | Forbidden; no inferred seller matching |
| Source A review → Source A review | SOURCE_LOCAL | Normalized text duplicate detection | Within-source duplicate grouping (Phase 6) |
| Source B review → Source B product | SUPPORTED | product_id is Source B business key | Join enabled; referential integrity Phase 6 |
| Source B review → Source B shop | SUPPORTED | shop_id is Source B business key | Join enabled; referential integrity Phase 6 |
| Prediction → Review | CROSS_FACT | Review key is stable reference | Join enabled; prediction never overwrites source |
| Issue result → Review | CROSS_FACT | Review key is stable reference | Join enabled; prediction never overwrites source |
| Decision support → Review | CROSS_FACT | Review key is stable reference | Join enabled for decision rationale lookup |

---

## RELATIONSHIP MATRIX

Explicit classification of every proposed relationship.

| From | To | Relationship | Cardinality | Dependency | Status | Allowed? |
|---|---|---|---|---|---|---|
| `fact_review` | `dim_source` | Review belongs to source | M:1 | Required | SUPPORTED | YES |
| `fact_review` | `dim_rating` | Review has supplied rating | M:1 | Required | SUPPORTED | YES |
| `fact_review` | `dim_category` | Review belongs to source-category | M:1 | Required | SUPPORTED | YES |
| `fact_review` | `dim_product` | Source B review may reference product | M:1 | Optional (null for A) | SUPPORTED | YES |
| `fact_review` | `dim_shop` | Source B review may reference shop | M:1 | Optional (null for A) | SUPPORTED | YES |
| `dim_product` | `dim_shop` | Products and shops co-occur analytically | Not direct | Optional | CONDITIONAL | NO* |
| `fact_model_prediction` | `fact_review` | Prediction for one review | M:1 | Required | SUPPORTED | YES |
| `fact_model_prediction` | `dim_model` | Prediction from one model run | M:1 | Required | SUPPORTED | YES |
| `fact_model_evaluation` | `dim_model` | Evaluation for one model run | M:1 | Required | SUPPORTED | YES |
| `fact_model_evaluation` | `dim_source` | Evaluation on one source | M:1 | Required | SUPPORTED | YES |
| `fact_issue_prediction` | `fact_review` | Issue result for one review | M:1 | Required | SUPPORTED | YES |
| `fact_issue_prediction` | `dim_issue` | Issue result for one issue | M:1 | Required | SUPPORTED | YES |
| `fact_decision_support` | `fact_review` | Decision for one review | M:1 | Required | SUPPORTED | YES |
| `fact_case` | `fact_review` | Case context to one review | 1:M or M:1 | Optional | SUPPORTED | YES |
| `fact_intervention` | `fact_case` | Intervention belongs to case | M:1 | Required for B | SUPPORTED | YES (Track B) |

**NO* reason: dim_product and dim_shop share no direct key or business relationship. Their co-occurrence is at review level only (Source B fact_review may reference both). Any analysis combining products and shops goes through fact_review, preserving source isolation.

---

## DATA LINEAGE PLAN

Conceptual end-to-end flow from raw source to management consumption.

```
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 1–2: IMMUTABLE RAW EVIDENCE                              │
│                                                                 │
│  Source A (PRDECT-ID)        Source B (Tokopedia 2019)         │
│  data/raw/prdect_id/         data/raw/tokopedia.../           │
│  5,400 rows                  40,607 rows                       │
└─────────────────────────────────────────────────────────────────┘
                                    ↓
                    ┌───────────────────────────────┐
                    │ PHASE 6: VALIDATION & INGESTION│
                    │                               │
                    │ • Register source files       │
                    │ • Verify required fields      │
                    │ • Check rating domain [1–5]   │
                    │ • Validate completeness       │
                    │ • Document privacy status     │
                    │ • Reconcile to row counts     │
                    └───────────────────────────────┘
                                    ↓
                    ┌───────────────────────────────┐
                    │ PHASE 6: SOURCE-SPECIFIC       │
                    │ TRANSFORMATION & STAGING      │
                    │                               │
                    │ • Normalize review text       │
                    │ • Preserve source identifiers │
                    │ • Maintain row lineage        │
                    │ • Document exclusions         │
                    └───────────────────────────────┘
                                    ↓
         ┌──────────────────────────────────────────────────────┐
         │ PHASE 6: POSTGRESQL WAREHOUSE (Track A CORE)         │
         │                                                      │
         │ ┌─────────────────────────────────────────────────┐  │
         │ │ dim_source                                      │  │
         │ │  • SRC_PRDECT_ID_V1                            │  │
         │ │  • SRC_TOKOPEDIA_REVIEWS_2019                  │  │
         │ └─────────────────────────────────────────────────┘  │
         │           ↑         ↑         ↑         ↑            │
         │           │         │         │         │            │
         │ ┌─────────┴──┬──────┴──┬──────┴──┬──────┴──────────┐  │
         │ │            │         │         │                │  │
         │ │ dim_rating │ dim_    │ dim_    │ dim_shop    │  │
         │ │ (1–5)      │category │product  │ (Source B)  │  │
         │ │            │         │ (B)     │             │  │
         │ │            │         │         │             │  │
         │ └─────────────┴─────────┴─────────┴─────────────┘  │
         │           ↑         ↑         ↑         ↑           │
         │            \        \         /        /            │
         │             ╲        ╲       ╱        ╱             │
         │              ╲        ╲     ╱        ╱              │
         │               ╲        ╲   ╱        ╱               │
         │                ╲        ╲ ╱        ╱                │
         │                 ╲        V        ╱                 │
         │                  ╲  fact_review  ╱                  │
         │                   ╲   (unified   ╱                  │
         │                    ╲  review     ╱                  │
         │                     ╲  grain)   ╱                   │
         │                      └──────────┘                    │
         │         (One row per review from exactly one source) │
         │         (Lineage to source file + validation status)│
         │         (Source A attributes: Sentiment, Emotion)   │
         │         (Source B optional: product_id, shop_id)    │
         └──────────────────────────────────────────────────────┘
                                    ↓
         ┌──────────────────────────────────────────────────────┐
         │ PHASE 7: CURATED ANALYTICAL MARTS (BI Input)        │
         │                                                      │
         │ • Review/rating summaries (source/category grain)    │
         │ • Product review indicators (Source B product_id)    │
         │ • Shop review indicators (Source B shop_id)          │
         │ • Quality/coverage metadata                          │
         │ • All outputs retain source, source limitation, and  │
         │   reconciliation reference                           │
         └──────────────────────────────────────────────────────┘
                     ↙                 ↘
              ┌─────────┐          ┌────────────┐
              │ PHASE 8 │          │ PHASE 7/12 │
              │ ML      │          │ BI / Admin │
              └────┬────┘          └────────────┘
                   ↓
        ┌──────────────────────────┐
        │ PHASE 8: ML RESEARCH      │
        │                          │
        │ ├─ dim_model             │
        │ ├─ fact_model_prediction │
        │ └─ fact_model_evaluation │
        │                          │
        │ (Separate from source    │
        │  truth; never overwrites)│
        └────┬───────────────────┘
             ↓
    ┌─────────────────────────┐
    │ PHASE 9: ISSUE          │
    │ INTELLIGENCE            │
    │                         │
    │ ├─ dim_issue            │
    │ └─ fact_issue_          │
    │    prediction           │
    │                         │
    │ (Conditional on         │
    │  taxonomy approval)     │
    └────┬────────────────────┘
         ↓
    ┌─────────────────────────┐
    │ PHASE 10: DECISION      │
    │ SUPPORT                 │
    │                         │
    │ └─ fact_decision_       │
    │    support              │
    │                         │
    │ (Rationale,             │
    │  uncertainty,           │
    │  human review)          │
    └────┬────────────────────┘
         ↓
    ┌─────────────────────────┐
    │ PHASE 11: SERVICE       │
    │ & ORCHESTRATION         │
    │                         │
    │ • Analytical service    │
    │ • Workflow integration  │
    │                         │
    │ (Phase 10/11 only if    │
    │  Track B approved)      │
    │ • fact_case             │
    │ • fact_intervention     │
    └────┬────────────────────┘
         ↓
    ┌────────────────────────┐
    │ PHASE 12: MGMT BI       │
    │ CONSUMPTION             │
    │                         │
    │ Power BI / Dashboard    │
    │ Reporting (curated      │
    │ outputs with limits)    │
    └─────────────────────────┘
```

**Key lineage properties:**

1. **Immutable source layer:** Raw data locked at Phase 2; no retroactive changes
2. **Validation layer:** Quality findings recorded; no silent cleaning
3. **Source-specific staging:** Each source transformed independently; no cross-source blending
4. **Core warehouse:** Single `fact_review` grain per source; all dimensions properly normalized
5. **Curated marts:** Derived aggregations with explicit limitations
6. **Research layers (ML/Issue):** Fully separated from source; predictions never overwrite truth
7. **Decision layer:** Evidence trail preserved for audit and human review
8. **Service layer:** Approved outputs only; no raw files as final interface

---

## ANALYTICAL DATA CONTRACTS

For every major analytical output, Phase 5 specifies logical contract.

### Contract 1: Review/Rating Analytical Output (Phase 7, RQ-001)

| Field | Grain | Requirement | Source | Format |
|---|---|---|---|---|
| source_identifier | One output row | Which source | dim_source | SRC_PRDECT_ID_V1 or SRC_TOKOPEDIA_REVIEWS_2019 |
| category | One output row | Which category within source | dim_category | Raw category value from source |
| review_count | Aggregate | Number of reviews in group | COUNT(fact_review) | Integer ≥ 0 |
| average_rating | Aggregate | Mean supplied rating | AVG(dim_rating.rating_value) | 1.0–5.0 |
| rating_distribution | Aggregate | Count per rating value | COUNT per dim_rating | Histogram: [1: n, 2: n, 3: n, 4: n, 5: n] |
| validation_status | Quality | All records valid or excluded? | fact_review.validation_status | "COMPLETE", "PARTIAL", "EXCLUDED_COUNT" |
| reconciliation_reference | Audit | Link to source inventory | Source manifest + Phase 6 report | Checksum, file name, row reconciliation count |

**Limitation clause:** "This output reflects review text and ratings as provided by the source. It does not imply temporal trend, seller performance, product quality, or decision priority. It is source-specific; Source A and Source B are analyzed independently."

---

### Contract 2: Product Review Intelligence (Phase 7, RQ-002, Source B only)

| Field | Grain | Requirement | Source | Format |
|---|---|---|---|---|
| source_identifier | One product | SRC_TOKOPEDIA_REVIEWS_2019 | dim_source | Always "SRC_TOKOPEDIA_REVIEWS_2019" |
| product_id | One product | Source B `product_id` | dim_product | Source B business key |
| product_name | One product | Product listing name | dim_product | Source B product_name |
| category | One product | Product category (Source B) | dim_category + fact_review | Source B category value |
| review_count | Aggregate | Number of reviews for product | COUNT(fact_review) where product_id | Integer ≥ 0 |
| average_rating | Aggregate | Mean supplied rating for product | AVG(dim_rating.rating_value) | 1.0–5.0 |
| low_rating_count | Aggregate | Reviews with rating ≤ 2 | COUNT where rating ≤ 2 | Integer ≥ 0 |
| low_rating_percentage | Aggregate | Percent of reviews ≤ 2 | low_rating_count / review_count * 100 | 0.0–100.0 |
| validation_status | Quality | Records in product group valid or excluded? | fact_review.validation_status | "COMPLETE", "PARTIAL", "EXCLUDED_COUNT" |
| reconciliation_reference | Audit | Link to source inventory | Source B manifest + Phase 6 report | product_id coverage, null handling |

**Limitation clause:** "This output describes review signals for identified Source B products. It does not imply causation, seller responsibility, product defect confirmation, or enforcement action. It is Source B only; Source A products are not included. No temporal trend or market-wide comparison is supported."

---

### Contract 3: Shop Review Indicators (Phase 7, RQ-003, Source B only)

| Field | Grain | Requirement | Source | Format |
|---|---|---|---|---|
| source_identifier | One shop | SRC_TOKOPEDIA_REVIEWS_2019 | dim_source | Always "SRC_TOKOPEDIA_REVIEWS_2019" |
| shop_id | One shop | Source B `shop_id` | dim_shop | Source B business key |
| review_count | Aggregate | Number of reviews for shop (across all products) | COUNT(fact_review) where shop_id | Integer ≥ 0 |
| average_rating | Aggregate | Mean supplied rating for shop reviews | AVG(dim_rating.rating_value) | 1.0–5.0 |
| low_rating_percentage | Aggregate | Percent of shop reviews ≤ 2 | COUNT(rating ≤ 2) / review_count * 100 | 0.0–100.0 |
| product_count | Aggregate | Number of distinct products in shop | COUNT(DISTINCT product_id) | Integer ≥ 0 |
| validation_status | Quality | Records in shop group valid or excluded? | fact_review.validation_status | "COMPLETE", "PARTIAL", "EXCLUDED_COUNT" |
| reconciliation_reference | Audit | Link to source inventory | Source B manifest + Phase 6 report | shop_id coverage, null handling |

**Limitation clause:** "This output describes review experience indicators for identified Source B shops based on customer-provided reviews. It does not characterize seller performance, seller capability, enforcement status, or seller reputation. It is review-supplied-rating feedback only. No time trend, seller behavior assessment, or automated seller action is implied or supported. It is Source B only."

---

### Contract 4: Source A Sentiment/Emotion Benchmark (Phase 8, RQ-004)

| Field | Grain | Requirement | Source | Format |
|---|---|---|---|---|
| source_identifier | Benchmark | SRC_PRDECT_ID_V1 | dim_source | Always "SRC_PRDECT_ID_V1" |
| sentiment | Label value | Provided binary sentiment in source A | fact_review.provided_sentiment | "POSITIVE" or "NEGATIVE" |
| sentiment_count | Aggregate | Number of reviews with label | COUNT(fact_review) where sentiment | Integer ≥ 0 |
| emotion | Label value | Provided emotion in source A | fact_review.provided_emotion | One of 5-class emotion labels |
| emotion_count | Aggregate | Number of reviews with label | COUNT(fact_review) where emotion | Integer ≥ 0 |
| emotion_distribution | Aggregate | Count per emotion class | COUNT per emotion value | Histogram per class |
| rating_distribution_by_sentiment | Aggregate | Rating distribution per sentiment | Rating counts grouped by sentiment | Cross-tab: sentiment × rating counts |
| validation_status | Quality | All benchmark records valid? | fact_review.validation_status | "COMPLETE", "PARTIAL", "EXCLUDED_COUNT" |
| reconciliation_reference | Audit | Link to source A inventory | Source A manifest + Phase 6 report | Checksum, row reconciliation |

**Limitation clause:** "This output presents the sentiment and emotion labels as provided by Source A (PRDECT-ID dataset), the sole gold-label benchmark for these attributes in MarketVoice SEA. Labels are not predictions; they are source-supplied annotations. Labels and ratings describe customer-provided review text. They do not characterize product quality or seller performance. Source A baseline is used for Phase 8 model evaluation only; Source B reviews are not labeled with Source A labels. These labels may contain annotation bias, incompleteness, or limitation; Phase 8 will assess label quality empirically."

---

### Contract 5: Model Evaluation Results (Phase 8, RQ-005)

| Field | Grain | Requirement | Source | Format |
|---|---|---|---|---|
| source_identifier | One model + one source | Source A or B | dim_model + dim_source | SRC_PRDECT_ID_V1 or SRC_TOKOPEDIA_REVIEWS_2019 |
| task_identifier | One model + one task | rating_classification, sentiment_classification, or emotion_classification | dim_model | Task name per Phase 4 design |
| model_identifier | One model version | Model architecture + version + experiment run | dim_model | model_id + experiment_run_id |
| dataset_split | One evaluation split | train, validation, or holdout | fact_model_evaluation | Split identifier |
| record_count | Grain count | Records in this split | COUNT(fact_review) for split | Integer ≥ 1 |
| accuracy | Metric | Exact-label agreement | fact_model_evaluation | 0.0–1.0 |
| macro_f1 | Metric | Equal-weight class F1 | fact_model_evaluation | 0.0–1.0 |
| weighted_f1 | Metric | Frequency-weighted F1 | fact_model_evaluation | 0.0–1.0 |
| per_class_recall | Metric | Recall per label class | fact_model_evaluation | Dictionary: {class: recall, ...} |
| confusion_matrix | Metric | Predicted vs. actual label | fact_model_evaluation | Matrix stored as structured data |
| coverage | Metric | Evaluated records / eligible records | fact_model_evaluation | 0.0–1.0 (exclusions noted) |
| quadratic_weighted_kappa | Metric | Ordinal agreement (rating tasks only) | fact_model_evaluation | 0.0–1.0; null if non-ordinal task |
| mean_absolute_error | Metric | Avg. magnitude of error (rating tasks only) | fact_model_evaluation | Non-negative real; null if non-ordinal task |
| preprocessing_version | Method | Which preprocessing pipeline | dim_model | Version identifier from Phase 8 |
| seed | Method | Random seed for reproducibility | dim_model | Integer or documented seed strategy |
| execution_environment | Environment | Python version, library versions | dim_model | Environment description or hash |
| error_analysis_reference | Evidence | Link to error analysis findings | fact_model_evaluation | Phase 8 error analysis document |
| champion_status | Decision | Was this model selected as champion? | fact_model_evaluation | "CHAMPION", "CHALLENGER", "BASELINE", "NOT_SELECTED" |

**Limitation clause:** "This output presents model evaluation results for reproducible Phase 8 research. No numeric success threshold is predeclared. Metrics are interpreted in context of: source, target class distribution, exclusions/missing values, preprocessing, evaluation split identity, and execution environment. Results on validation and holdout sets may differ; holdout evaluation is final and unbiased. All results are source-specific; Source A and Source B models are independent. Models are not deployed; they are research artifacts."

---

### Contract 6: Issue Prediction Results (Phase 9, conditional, RQ-006)

| Field | Grain | Requirement | Source | Format |
|---|---|---|---|---|
| source_identifier | One review | Both sources eligible | dim_source | SRC_PRDECT_ID_V1 or SRC_TOKOPEDIA_REVIEWS_2019 |
| review_key | One review | Unique review identifier | fact_review | review_key |
| taxonomy_version | Taxonomy version | Approved taxonomy version under evaluation | dim_issue | taxonomy_version_id |
| issue_id | One issue in taxonomy | Approved issue identifier | dim_issue | issue_id |
| issue_result | Prediction | Predicted issue assignment | fact_issue_prediction | "PRESENT", "NOT_PRESENT", "UNCERTAIN", or confidence |
| confidence | Confidence | Model confidence in result | fact_issue_prediction | 0.0–1.0 or calibrated probability |
| method_identifier | Method + run | Which extraction/classification method + run | dim_model | method_id + experiment_run_id |
| evidence_reference | Audit | Link to Phase 9 taxonomy approval | fact_issue_prediction | Taxonomy approval document + annotation quality report |
| human_review_status | Review | Has a human reviewed this result? | fact_issue_prediction | "PENDING", "APPROVED", "DISPUTED", "OVERRIDDEN" |
| validation_status | Quality | Source record valid? | fact_review.validation_status | "VALID", "EXCLUDED_COUNT" |

**Limitation clause:** "This output presents issue prediction results based on approved Phase 9 taxonomy and trained classifiers. Results are conditional on taxonomy accuracy, annotation quality, and model generalization. Predictions are not enforcement-ready; they are evidence for human review. Predictions may be overridden or corrected by human annotators. Issue taxonomy may evolve in future versions, which could change meaning of historical predictions. All results remain source-specific unless Phase 9 explicitly validates cross-source comparison."

---

### Contract 7: Decision-Support Output (Phase 10, conditional, RQ-007)

| Field | Grain | Requirement | Source | Format |
|---|---|---|---|---|
| source_identifier | One review | Sources A + B eligible | dim_source | SRC_PRDECT_ID_V1 or SRC_TOKOPEDIA_REVIEWS_2019 |
| review_key | One review | Unique review identifier | fact_review | review_key |
| decision_rule_version | Rule version | Which decision rule version applied | fact_decision_support | rule_version_id |
| priority_representation | Decision | Priority level or score | fact_decision_support | "HIGH", "MEDIUM", "LOW" or ordinal score |
| priority_rationale | Explanation | Why this priority (human-readable) | fact_decision_support | Free-text explanation with evidence citations |
| uncertainty_assessment | Confidence | Stated uncertainty or confidence | fact_decision_support | Confidence statement or probability |
| evidence_references | Audit trail | Which underlying facts/models informed this decision | fact_decision_support | References to model predictions, issue results, review quality flags |
| human_review_required | Control | Does this decision require human review? | fact_decision_support | Always TRUE or per rule-defined threshold |
| human_review_status | Review outcome | Has a human reviewed and decided? | fact_decision_support | "PENDING", "APPROVED", "REJECTED", "MODIFIED" |
| human_review_decision | Final decision | Human's final decision/override | fact_decision_support | Free-text human decision or null if pending |
| human_review_timestamp | Audit | When was the human review completed? | fact_decision_support | ISO timestamp or null if pending |
| reversibility_reference | Control | Can this decision be reversed/modified? | fact_decision_support | "YES" (always for non-enforcement decisions) |

**Limitation clause:** "This output is a decision-support recommendation for human review. It is not an automated decision. No enforcement, punitive, or automated action may occur without explicit human review and approval. All recommendations are provisional and subject to human override. Recommendations may be revised if supporting evidence (models, issues, quality data) is updated. Decisions are not retroactively applied to past reviews; each review receives independent assessment."

---

## TRACK A / TRACK B SEPARATION

### Track A: Authentic Analytical MVP

**Scope:**
- Source A (PRDECT-ID) and Source B (Tokopedia 2019) review evidence
- Supplied ratings and Source A-provided sentiment/emotion
- Source-specific analysis and baseline ML research
- Curated BI and decision-support outputs based on authentic data

**Entities:**
- All core dimensions and facts (dim_source through fact_review, dim_model through fact_decision_support)

**Governance:**
- All Track A data is authentic evidence
- No Track A labels are overwritten or imputed
- No Track A review is marked synthetic
- All Track A data has full source lineage and validation status
- Track A is the authorized MVP scope for Phases 6–10

---

### Track B: Conditional Synthetic/Operational Extension

**Activation:**
- Track B data (case/intervention facts) is **NOT generated** until Phase 10/11 and **ONLY if separately approved**
- Track B approval is not implied by Phase 3/4 gate passage
- Separate explicit authorization required

**Scope (if/when approved):**
- Synthetic operational case IDs and workflow events
- Operational event dates (workflow timestamps, not review timestamps)
- Intervention tracking and human decision outcomes
- Workflow orchestration state

**Entities:**
- `fact_case` — Explicitly marked synthetic
- `fact_intervention` — Explicitly marked synthetic

**Governance:**
- Every Track B row has `synthetic_status = TRUE`
- Track B event dates never populate authentic time dimensions
- Track B data is logically and physically isolated from Track A
- Track B case/intervention identity is non-identifying (synthetic IDs only)
- Reference to Track A reviews is optional context only; never as foreign key parent

**Separation Mechanics (Phase 6):**

| Control | Implementation |
|---|---|
| Logical isolation | `fact_case` and `fact_intervention` are separate tables, not columns in Track A facts |
| Physical isolation | Schema design isolates Track B if implemented (discussed at Phase 5 logical layer only) |
| Flag visibility | Every Track B row has explicit `synthetic_status` and `version_created_after_phase` audit timestamp |
| Referential constraint | Track A facts do not have foreign keys to Track B; Track B may optionally reference Track A for context only |
| Query isolation | Default analytical queries select only Track A; Track B requires explicit inclusion |
| Audit trail | All Track B creation/modification is logged with Phase authorization reference |

---

## DATA QUALITY RESPONSIBILITIES

Every analytical layer has defined quality responsibility.

| Layer | Responsibility | Quality Control | Audit Trail |
|---|---|---|---|
| **Raw source** | Publisher integrity | Checksum verification, publication audit | SHA256 per source manifest, Phase 2 audit report |
| **Validation** | Field completeness, rating domain, reconciliation | Validation rules script, exclusion log | Validation evidence table, Phase 6 validation report |
| **Staging** | Duplicate detection, text normalization | Duplicate grouping log, normalization reference | Staging log, Phase 6 staging report |
| **Warehouse core** | Referential integrity, null handling, source lineage | Constraints (Phase 6), reconciliation checks | Source-row lineage, validation-status reference |
| **Curated marts** | Aggregation correctness, limitation documentation | Mart definition (SQL/views), limitation tags | Mart refresh logs, Phase 7 verification |
| **ML layer** | Split integrity, leakage prevention, reproducibility | Experiment record, holdout lock, seed documentation | Experiment log, Phase 8 validation report |
| **Issue layer** | Taxonomy consistency, annotation quality, method reproducibility | Taxonomy versioning, IAA metrics, method documentation | Taxonomy version control, Phase 9 validation report |
| **Decision layer** | Rationale auditability, human-review requirement, reversibility | Decision log with supporting fact references, human-review approval | Decision audit trail, Phase 10 validation report |

---

## GOVERNANCE & PRIVACY ARCHITECTURE

Phase 5 logical architecture must embed governance from the start.

| Governance Layer | Requirement | Architecture Implementation |
|---|---|---|
| **Source attribution** | Every fact must identify its source | `dim_source` reference in every Track A fact |
| **Source-row provenance** | Traceability to original raw file | Surrogate key + business key + lineage reference in `fact_review` |
| **Privacy review status** | Review text marked for privacy evaluation | `privacy_review_status` attribute in `fact_review` |
| **Validation transparency** | Quality findings must be recordable | `validation_status` reference per source record; detailed validation log in Phase 6 |
| **Reproducibility metadata** | Every derived result must link to inputs | `preprocessing_version`, `seed`, `environment` in `dim_model`; `experiment_run_id` in all results |
| **Label immutability** | Source-provided labels never overwritten | `provided_sentiment`, `provided_emotion` are immutable attributes; predictions stored separately |
| **Audit trail for decisions** | Human decisions are logged and reversible | `fact_decision_support` records human review, approval date, decision content; supports modification |
| **Synthetic flagging** | Track B data clearly marked non-authentic | `synthetic_status = TRUE` on every Track B row |
| **Limitation disclosure** | Every analytical output states its scope and limits | Limitation clauses in every data contract (above) |

---

## REQUIREMENT TRACEABILITY

Every Phase 3 / Phase 4 requirement maps to logical architecture.

| Requirement | Type | Requirement Text | Phase 5 Architecture Component | Phase 6+ Implementation |
|---|---|---|---|---|
| `FR-001` | MUST | System shall normalize verified review sources | Ingestion layer, `fact_review` with source lineage | Phase 6: ETL + validation |
| `FR-002` | MUST | System shall validate required fields, rating, completeness, reconciliation | Validation layer, `validation_status` in `fact_review` | Phase 6: validation rules + exclusion log |
| `FR-003` | MUST | Provide review/rating analytical capability | Curated marts (source/category grain) | Phase 7: SQL views/aggregations |
| `FR-004` | MUST | Provide Source A baseline analysis for provided sentiment/emotion | `fact_review` + Source A-only attributes + `dim_model` + `fact_model_evaluation` | Phase 8: model research on Source A |
| `FR-005` | MUST | Provide Source B product-level review intelligence | `dim_product` + product-grain curated mart | Phase 7: product aggregations |
| `FR-006` | SHOULD | Provide Source B shop-level indicators | `dim_shop` + shop-grain curated mart | Phase 7: shop aggregations |
| `FR-007` | SHOULD | Support issue-intelligence outputs | `dim_issue` + `fact_issue_prediction` + conditional Phase 9 taxonomy approval | Phase 9: taxonomy validation + classifier |
| `FR-008` | SHOULD | Support explainable human-review prioritization | `fact_decision_support` with rationale/uncertainty/audit | Phase 10: decision-logic + human-review workflow |
| `FR-009` | SHOULD | Make required management information domains available | All curated marts + ML/issue/DSS outputs with availability labels | Phase 7–12: information domain delivery |
| `NFR-001` | MUST | Analytical outputs shall preserve source provenance and lineage | `dim_source`, source_lineage in `fact_review`, audit trails | Phase 6: lineage reference in all outputs |
| `NFR-002` | MUST | System shall not intentionally enrich PII or create customer profiles | No customer dimension; review text marked `privacy_review_status` | Phase 6: privacy review gate + output restrictions |
| `NFR-003` | MUST | Maintain auditable record of transformations and decisions | Metadata in `fact_review`, `dim_model`, `fact_decision_support`; detailed logs per phase | Phase 6–10: comprehensive logging |
| `NFR-004` | MUST | Decision-support outputs shall be explainable with uncertainty | `fact_decision_support` structure with `priority_rationale`, `uncertainty_assessment` | Phase 10: rationale generation + human review |
| `NFR-005` | MUST | System shall be reproducible from approved source evidence | Lineage, seed, preprocessing, environment metadata in every result | Phase 6–10: versioning + reproducibility validation |
| `NFR-006` | SHOULD | System shall support human-decision override | `human_review_status`, `human_review_decision`, `reversibility_reference` in `fact_decision_support` | Phase 10: human-decision workflow |
| `NFR-007` | SHOULD | System shall enforce Track A / Track B separation | Logical entities `fact_case`, `fact_intervention` marked synthetic; structure supports isolation | Phase 6: schema design; Phase 10/11: deployment control |

---

## PLANNED ARTIFACT TREE

Phase 5 logical architecture will create/update these files during execution:

| File | Purpose | Modification | Status |
|---|---|---|---|
| docs/architecture/solution_architecture.md | High-level architecture context | Revision for Phase 5 execution (if needed) | Existing (v1.0); candidate for Phase 5 refinement |
| docs/architecture/dimensional_model.md | Grain register and entity specifications | Finalization and clarification after Phase 5 analysis | Existing (v1.0); ready for Phase 5 detail |
| docs/architecture/data_architecture.md | Layer responsibilities and source mapping | Finalization; add Phase 5 design decisions | Existing (v1.0); ready for Phase 5 detail |
| docs/architecture/integration_contracts.md | Consumer responsibility contracts | Confirmation and refinement | Existing (v1.0); ready for Phase 5 detail |
| **docs/architecture/analytical_data_contracts.md** | **Detailed output contracts for every analytical entity** | **NEW: Create during Phase 5** | Planned |
| **docs/architecture/data_lineage.md** | **End-to-end conceptual lineage** | **NEW: Create during Phase 5 if not already defined** | Planned |
| **reports/validation/phase_05_architecture_validation.md** | **Phase 5 logical design validation** | **NEW: Create after Phase 5 architecture completion** | Planned |

---

## PHASE 5 EXECUTION ROADMAP

Detailed steps for Phase 5 implementation. Each step includes purpose, inputs, actions, outputs, validation, and stop conditions.

### Step 5.1 — Reconcile Architecture Inputs

**Purpose:** Ensure Phase 5 logical architecture is built on current, verified, non-contradictory inputs from Phases 0–4.

**Inputs:**
- phase_gates.md (current version)
- phase_03_validation.md, phase_02_dataset_forensic_audit_report.md
- analytical_research_design.md, experiment_protocol.md, evaluation_protocol.md
- business_and_information_requirements.md (v2.0), system_requirements.md (v2.0)
- requirements_traceability.md (v2.0)
- data_capability_matrix.csv, source_manifest.csv

**Actions:**
1. Read phase_gates.md; verify which phases have PASS gate status (authority for Phase 5 input lock)
2. Identify any contradictions between governance documents and methodology documents
3. Reconcile Phase 3 requirement IDs to Phase 4 analytical task IDs (verify complete traceability)
4. Verify every MUST requirement has at least one associated architectural component
5. Classify any advisory or conditional requirements for Phase 5 consideration
6. Document all evidence corrections or clarifications

**Files affected:**
- No file modification; analysis only for this step

**Output:**
- Architecture input register (internal working document)
- Traceability verification report (for Phase 5 validation step)

**Validation:**
- Every Phase 3 MUST requirement identified
- Every Phase 4 RQ identified
- 0 orphan requirements; 0 unsupported MUST requirements
- 0 material contradictions (or explicitly flagged)

**Acceptance criteria:**
- Architecture foundations are verified and locked

**Dependencies:**
- Phase 3/4 gate status known (AWAITING_HUMAN_APPROVAL is OK for planning)

**Stop condition:**
- If MUST requirement found without data to support it → BLOCKED (return to Phase 3/4)

---

### Step 5.2 — Review & Audit Existing Phase 5 Artifacts

**Purpose:** Evaluate existing Phase 5 design documents for quality, completeness, and alignment with current Phase 3/4.

**Inputs:**
- docs/architecture/solution_architecture.md (v1.0)
- docs/architecture/dimensional_model.md (v1.0)
- docs/architecture/data_architecture.md (v1.0)
- docs/architecture/integration_contracts.md (v1.0)

**Actions:**
1. Read each existing Phase 5 artifact
2. Classify each artifact as VALID, STALE, CONTRADICTORY, or SUPERSEDED
3. Document any changes to Phase 3/4 that invalidate or require Phase 5 revision
4. For VALID artifacts: flag for Phase 5 detail/finalization
5. For STALE/CONTRADICTORY: identify required revisions
6. For SUPERSEDED: identify replacement approach

**Files affected:**
- Analysis only; no modifications in this step

**Output:**
- Phase 5 artifact audit report

**Validation:**
- All existing Phase 5 artifacts reviewed
- Each artifact classified with evidence

**Acceptance criteria:**
- Phase 5 existing work is assessed; decision made to keep, refine, or replace

**Dependencies:**
- Step 5.1 reconciliation complete

**Stop condition:**
- If CRITICAL contradiction found between existing Phase 5 and Phase 3/4 → Revision required before proceeding

---

### Step 5.3 — Finalize Grain Register & Dimensional Model

**Purpose:** Verify every proposed analytical entity has justified grain and complete specification.

**Inputs:**
- Phase 4 analytical research design (RQ definitions)
- Existing dimensional_model.md v1.0
- Requirements traceability (FR/IR mapping)
- Data capability matrix

**Actions:**
1. For every proposed entity (dim_source, dim_rating, dim_category, dim_product, dim_shop, fact_review, dim_model, fact_model_prediction, fact_model_evaluation, dim_issue, fact_issue_prediction, fact_decision_support, fact_case, fact_intervention):
   - Verify grain is justified by a requirement or research question
   - Verify natural/business key is stable and non-ambiguous
   - Verify surrogate-key strategy is documented
   - Verify all attributes are mapped to a source field or calculated rule
   - Verify no spurious attributes (added for convenience)

2. For every relationship:
   - Verify cardinality is correct
   - Verify linkage is supported by data evidence (no inferred keys)
   - Verify no accidental many-to-many
   - Verify referential integrity is enforceable

3. Challenge every proposed entity: Does it serve the requirements? Is it necessary? Could it be merged or split?

**Files affected:**
- docs/architecture/dimensional_model.md — Update/refine grain register and entity definitions

**Output:**
- Updated dimensional_model.md with finalized grain register and validation notes

**Validation:**
- 0 orphan grain decisions (every grain justified)
- 0 spurious entities or attributes
- 0 inferred keys or unsupported cross-source joins
- All relationships classified

**Acceptance criteria:**
- Dimensional model is complete, justified, and ready for Phase 6 implementation

**Dependencies:**
- Step 5.2 artifact audit complete

**Stop condition:**
- If unsupported requirement found → return to Phase 3/4 for clarification

---

### Step 5.4 — Finalize Data Lineage & Layer Responsibilities

**Purpose:** Document complete conceptual flow from raw evidence through analytical consumption.

**Inputs:**
- Existing data_architecture.md (layer responsibilities)
- Grain register from Step 5.3
- Curated mart design (from integration_contracts.md)

**Actions:**
1. Create or finalize data_lineage.md:
   - Show conceptual flow from raw source through each logical layer
   - Label each layer with ownership and responsibility
   - Document transformation intent at each layer (preserve truth, aggregate, predict, decide)
   - Show Track A / Track B separation points

2. Verify every entity appears in the lineage
3. Verify no entities appear that were not already designed
4. Verify lineage supports all required outputs (curated marts, ML results, decision support)

**Files affected:**
- docs/architecture/data_lineage.md — Create or finalize
- docs/architecture/data_architecture.md — Update if needed

**Output:**
- Complete data lineage documentation (Mermaid or text-based flow)

**Validation:**
- Lineage covers raw source through all analytical outputs
- Every entity has defined responsibility and immutability/mutability status
- Track A/B separation is explicit

**Acceptance criteria:**
- A future reader can trace any analytical output back to raw source evidence

**Dependencies:**
- Step 5.3 grain register complete

**Stop condition:**
- None; if gaps found, revise and re-validate

---

### Step 5.5 — Finalize Analytical Data Contracts

**Purpose:** Specify exactly what each analytical output contains, what it means, and what it does NOT mean.

**Inputs:**
- Phase 4 RQ definitions (RQ-001 through RQ-007)
- System requirements (FR definitions)
- Phase 7–10 planned deliverables
- Curated mart concepts (integration_contracts.md)

**Actions:**
1. For every major analytical output family (Review/Rating, Product Intelligence, Shop Indicators, Sentiment/Emotion Benchmark, Model Evaluation, Issue Prediction, Decision Support):
   - Define logical output grain
   - List every field with requirement/justification
   - Specify format and valid values
   - Write limitation clause (what this output is NOT)
   - Cite source(s) and quality responsibility
   - Specify audit trail

2. Verify limitation clauses prevent misuse:
   - No temporal analysis claims (no time grain)
   - No seller-performance claims (shop indicators only)
   - No enforcement or automated action claims
   - No prediction = truth claims
   - No synthetic data contamination

3. Ensure every contract maps to a Grain Register entity

**Files affected:**
- docs/architecture/analytical_data_contracts.md — Create (new file)

**Output:**
- Comprehensive analytical data contracts document

**Validation:**
- Every major output type has a contract
- Every contract is precise and limitation-aware
- 0 misleading claims; 0 unsupported implications

**Acceptance criteria:**
- Contracts are ready for presentation to stakeholders and for Phase 6/7 implementation

**Dependencies:**
- Step 5.4 lineage complete

**Stop condition:**
- None; if gaps found, revise and re-validate

---

### Step 5.6 — Finalize Track A / Track B Separation Policy

**Purpose:** Document how logical architecture will prevent synthetic Track B data from contaminating authentic Track A analysis.

**Inputs:**
- Synthetic data policy (docs/governance/synthetic_data_policy.md)
- Grain register (fact_case, fact_intervention designs)
- Existing separation mentions in data_architecture.md

**Actions:**
1. Document logical separation strategy:
   - Entity names make synthetic status obvious
   - Primary keys are explicitly non-identifying (case_id, event_id are not customer/case IDs)
   - Track B facts never appear as parents of Track A facts
   - Track B references are optional and contextual only

2. Document governance controls:
   - When Track B data may be created (Phase 10/11 only, conditional approval)
   - How Track B rows are flagged (synthetic_status, version_created_after_phase)
   - Query defaults (Track A only)
   - Audit trail requirements

3. Document implementation handoff to Phase 6:
   - Schema separation strategy
   - Row filtering logic
   - Default query scope
   - Audit logging strategy

**Files affected:**
- docs/architecture/data_architecture.md — Update/refine Track A/B section
- docs/architecture/dimensional_model.md — Update Track A/B entity descriptions

**Output:**
- Updated architecture documents with explicit Track A/B strategy

**Validation:**
- Logical isolation is clear and enforceable
- No Track A output can accidentally include Track B data
- No future ambiguity about synthetic status

**Acceptance criteria:**
- Track A/B separation is ready for Phase 6 physical implementation

**Dependencies:**
- Step 5.3 grain register complete

**Stop condition:**
- None; if gaps found, revise and re-validate

---

### Step 5.7 — Finalize Requirement Traceability (Phase 3/4 → Phase 5)

**Purpose:** Document complete lineage from Phase 3 requirements through Phase 5 logical architecture to Phase 6+ implementation responsibilities.

**Inputs:**
- requirements_traceability.md (Phase 3 BQ → BR → IR → FR)
- analytical_research_design.md (Phase 4 RQ → task mapping)
- Grain register and data contracts from Steps 5.3–5.5

**Actions:**
1. For every MUST requirement (FR/NFR):
   - Identify which Phase 5 architectural component(s) support it
   - Map to logical entity and/or data contract
   - Document Phase 6+ implementation responsibility

2. For every SHOULD/conditional requirement:
   - Identify which Phase 5 component addresses it or explicitly defers it
   - Document any approval gates or conditions

3. For every Phase 4 RQ:
   - Map to Phase 5 architectural component
   - Verify architecture provides data/contract for Phase 8–10 execution

4. Create summary traceability report showing:
   - 0 orphan requirements
   - All MUST requirements addressed
   - All conditional requirements classified and gated
   - All RQs mapped to architecture

**Files affected:**
- docs/architecture/integration_contracts.md — Update traceability section if needed
- docs/architecture/analytical_data_contracts.md — Cross-reference requirements

**Output:**
- Complete traceability matrix (Phase 3/4 → Phase 5 → Phase 6+)

**Validation:**
- No orphan MUST requirements
- Every architectural component traces to a requirement or RQ
- Phase 6+ knows exactly what to build and hand off

**Acceptance criteria:**
- Traceability is complete and bidirectional

**Dependencies:**
- Step 5.5 data contracts complete

**Stop condition:**
- If orphan requirement found → return to Phase 3/4 or extend architecture

---

### Step 5.8 — Validation & Red-Team Phase 5 Architecture

**Purpose:** Challenge the Phase 5 design before hand-off to Phase 6.

**Inputs:**
- All Phase 5 artifacts from Steps 5.1–5.7
- Phase 3/4/2 requirements and evidence
- Existing project constraints

**Actions:**

**Validation Checklist (Objective Criteria):**

1. **Grain Justification**
   - [ ] Every entity has a justified grain
   - [ ] Every grain is derived from a requirement or RQ (not convenience)
   - [ ] No spurious grain combinations

2. **Linkage & Keys**
   - [ ] 0 Source A products in dim_product
   - [ ] 0 unsupported cross-source joins
   - [ ] 0 inferred product_id/shop_id keys
   - [ ] All relationships classified (SUPPORTED / CONDITIONAL / FORBIDDEN)

3. **Source Isolation**
   - [ ] Source A and Source B never pooled at fact grain
   - [ ] Product/shop intelligence is Source B only (explicit in contract)
   - [ ] Sentiment/emotion is Source A only (explicit in contract)
   - [ ] No temporal claims (verified against data capability)

4. **Track A / Track B**
   - [ ] Track B entities are separate (not Track A columns)
   - [ ] Every Track B row can be flagged synthetic
   - [ ] Track B references to Track A are optional, never parent
   - [ ] No Track A output accidentally includes Track B

5. **Label Immutability**
   - [ ] Source-provided labels stored immutably
   - [ ] Predictions stored separately (never overwrite)
   - [ ] Source A labels never imputed to Source B

6. **Lineage & Audit**
   - [ ] Every fact retains source_id + source_row_identity
   - [ ] Every derived fact has versioned metadata
   - [ ] Every decision output has audit trail
   - [ ] 0 silent transformations

7. **Reproducibility**
   - [ ] Experiment metadata captured (seed, preprocessing, environment)
   - [ ] Evaluation results linked to model/split identity
   - [ ] Issue results linked to taxonomy version
   - [ ] Decision results linked to rule version

8. **Limitation Disclosure**
   - [ ] Every output contract has limitation clause
   - [ ] No temporal claims
   - [ ] No seller-performance claims
   - [ ] No enforcement implications

9. **Requirement Coverage**
   - [ ] Every FR/NFR is addressed by Phase 5 or explicitly deferred
   - [ ] Every RQ is supported by Phase 5 architecture
   - [ ] No contradictions between contracts and requirements

10. **Anti-Overengineering**
    - [ ] No proposed features that don't serve a requirement
    - [ ] Grain register has no unnecessary entities
    - [ ] Architecture is implementable in Phase 6 without invention

**Red-Team Questions:**

1. Does any proposed entity exist only because it is convenient?
   - If yes, remove it or re-justify from requirements
2. Does every grain have a business/analytical justification?
   - If no, re-examine entity necessity
3. Are any Source A and Source B identifiers incorrectly joined?
   - If yes, flag for architecture fix
4. Is review event time being invented?
   - If yes, remove all temporal claims and entities
5. Does shop_id accidentally become seller-performance data?
   - If yes, revise limitation clauses and output contracts
6. Does architecture assume issue taxonomy already exists?
   - If yes, add explicit Phase 9 gate and conditional activation
7. Does design depend on synthetic Track B for authentic MVP?
   - If yes, remove Track B entities from critical path
8. Does decision support contain hidden final scoring logic?
   - If yes, explicit separate decision-support design without final formula
9. Has architecture leaked into physical DDL?
   - If yes, remove SQL/DDL and limit to logical grain/relationships
10. Can Phase 6 implement the plan without inventing requirements?
    - If no, revise plan until implementation is unambiguous
11. Is the design unnecessarily complex for an S2-scale project?
    - If yes, simplify entities, grain, or relationships
12. Are all important architecture decisions traceable to requirements?
    - If no, add traceability for every major decision

**Files affected:**
- reports/validation/phase_05_architecture_validation.md — Create

**Output:**
- Phase 5 architecture validation report with pass/fail on each criterion
- Red-team challenge results with mitigation for each finding

**Validation:**
- All 10 validation checkpoints PASS or explicitly documented as conditional/deferred
- All 12 red-team questions answered with evidence-based response
- 0 unresolved architecture contradictions

**Acceptance criteria:**
- Phase 5 architecture is sound, complete, and ready for hand-off to Phase 6
- Any remaining decisions are explicitly noted as human decisions (below)

**Dependencies:**
- All prior steps complete

**Stop condition:**
- If CRITICAL validation failure → return to Steps 5.1–5.7 for revision

---

### Step 5.9 — Document Human Decisions Required

**Purpose:** Identify which decisions are beyond technical scope and require explicit project owner/architect input.

**Inputs:**
- Phase 5 artifacts from Steps 5.1–5.8
- Outstanding blockers or conditional approvals

**Actions:**

Classify remaining unresolved decisions:

1. **Approval Gate (required before Phase 6):**
   - Phase 3 human gate approval (blocking)
   - Phase 4 gate approval (blocking, dependent on Phase 3)

2. **Architecture Decisions (Phase 5 scope):**
   - Surrogate-key strategy for dim_category, dim_product, dim_shop (vs. business keys only)?
   - Mermaid vs. alternative lineage diagram format?
   - Separate analytical_data_contracts.md or merge into existing architecture docs?

3. **Phase 6 / Phase 10/11 Conditional Decisions:**
   - Track B schema approach: separate tables vs. flags on core facts? (Phase 6)
   - Track B activation: when to generate synthetic case/intervention data? (Phase 10/11)
   - Privacy review: which review-text fields are public vs. restricted? (Phase 6)
   - ETL tooling: Python vs. dbt vs. SQL procedures? (Phase 6)

4. **Phase 7+ Information Decisions:**
   - Which curated marts are priority vs. future? (Phase 7)
   - Which information domains are included in BI (Phase 12)?
   - Which analytical outputs require human review before publishing? (Phases 7–12)

**Files affected:**
- reports/validation/phase_05_architecture_validation.md — Section on outstanding human decisions

**Output:**
- Clear list of which decisions are:
  - Blocking (must be resolved before Phase 6 starts)
  - Recommended for Phase 5 discussion (architectural preferences)
  - Deferred to Phase 6+ (implementation details)

**Validation:**
- Only genuine unresolved decisions listed (not ambiguity or confusion)
- Each decision has clear context and options documented

**Acceptance criteria:**
- Project owner knows exactly which decisions they must make vs. which Phase 6+ can handle

**Dependencies:**
- Step 5.8 red-team complete

**Stop condition:**
- None; human decisions are normal and expected

---

### Step 5.10 — Create Phase 5 → Phase 6 Handoff Contract

**Purpose:** Define exactly what Phase 6 receives and what Phase 6 is responsible for implementing.

**Inputs:**
- All Phase 5 artifacts (dimensional model, lineage, contracts)
- Validation report from Step 5.8

**Actions:**

Document handoff at logical layer only (no physical design from Phase 5):

1. **What Phase 6 Receives (Logical Architecture):**
   - Grain register and entity definitions
   - Dimensional model with attributes, relationships, keys
   - Data lineage (conceptual flow)
   - Analytical output contracts
   - Track A/B separation strategy
   - Requirement traceability

2. **What Phase 6 Must Implement (Physical Design):**
   - PostgreSQL DDL for all entities
   - Surrogate key generation strategy (if Phase 5 approved)
   - Indexes and partitioning strategy
   - Referential integrity constraints (if approved)
   - Null-handling policy
   - Schema separation (if Track B approved)
   - ETL pipeline (data loading, transformation)
   - Validation/quality checks implementation
   - Audit logging

3. **What Phase 6 Must NOT Implement (Phase 7+ scope):**
   - Curated mart SQL/views (Phase 7)
   - BI reporting/visualization (Phase 12)
   - Model training (Phase 8)
   - Issue taxonomy/classifier (Phase 9)
   - Decision-support logic (Phase 10)
   - API endpoints (Phase 11)
   - Workflow nodes (Phase 11)

4. **Verification Strategy for Phase 6:**
   - Reconciliation: All source records loaded to fact_review? Count match?
   - Lineage: Can any fact trace back to source? Lineage fields populated?
   - Keys: All surrogate keys unique and stable?
   - Relationships: All constraints enforced? No orphans?
   - Null handling: Documented policy observed?
   - Coverage: Are all required fields populated?
   - Quality: Do validation flags accurately reflect source data?

5. **Acceptance Criteria for Phase 6 Completion:**
   - [ ] All entities created and populated
   - [ ] 0 orphan rows (referential integrity holds)
   - [ ] Reconciliation: fact_review count = sum of validated source records (by source)
   - [ ] Lineage: 100% of facts traceable to source
   - [ ] Sample validation: 100 random facts can be traced back to raw source row
   - [ ] Null policy: Nulls documented and justified per entity/field
   - [ ] Track A/B: If applicable, Track B data clearly flagged
   - [ ] Audit metadata: Created/modified timestamps and provenance references populated
   - [ ] Phase 6 validation report PASS

**Files affected:**
- docs/architecture/solution_architecture.md — Add Phase 5 → Phase 6 contract section

**Output:**
- Phase 5 → Phase 6 handoff contract (added to solution_architecture.md)

**Validation:**
- Contract is clear and unambiguous
- Phase 6 can build from logical specification without architectural guessing
- Acceptance criteria are objective and measurable

**Acceptance criteria:**
- Phase 6 knows what to build and can validate when complete

**Dependencies:**
- Step 5.9 human decisions documented

**Stop condition:**
- None; handoff contract is final output of Phase 5 planning

---

## RISKS & MITIGATION

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Phase 3 human gate approval delayed or denied | Medium | High | Already documented as external blocker; Phase 5 planning proceeds independently; no impact on Phase 5 logic |
| Phase 4 technical validation finds additional defects after Phase 4 forensic audit | Low | Medium | Phase 5 proceeds from current (audited) Phase 4 state; any new Phase 4 defects → re-plan Phase 5 if required |
| Existing Phase 5 artifacts are stale and contradict Phase 3/4 | Low | High | Mitigated by Step 5.2 audit and Step 5.8 red-team; findings → revise existing artifacts before Phase 6 |
| Data warehouse scale/complexity grows beyond S2-scope design | Low | Medium | Anti-overengineering decisions documented; Phase 6 can keep design minimal if data volume remains modest |
| Cross-source product linkage becomes "necessary" later | Low | High | Decision already locked: no cross-source linkage unless Phase 3 requirement change; new requirement → separate change control |
| Privacy review delays Phase 6 (review-text access) | Medium | Low | Privacy review is Phase 6 gate, not Phase 5 gate; marked in architectural contracts; Phase 6 can proceed with restricted defaults |
| Track B synthetic data approval delayed or denied | Low | Medium | Track B is logically designed but not generated; non-blocking for Track A MVP; conditional activation ready if needed |
| Phase 6 needs to invent requirements because Phase 5 design is ambiguous | Low | High | Mitigated by detailed contracts, grain justification, and Step 5.8 red-team; Phase 5 → Phase 6 handoff is explicit |

---

## CONCLUSION

Phase 5 logical architecture and implementation plan is ready for execution pending:

1. **External Gate 1:** Phase 3 human gate approval (awaiting project owner decision)
2. **External Gate 2:** Phase 4 gate advancement (upon Phase 3 approval)

Once both gates are PASS, Phase 6 execution can begin with the complete logical specification in this plan.

No Phase 5 implementation has occurred. Phase 5 remains authorization-gated per user instructions.

---

**Next Steps:**

1. **Human Review:** Project owner reviews this implementation plan
2. **Approval or Change Requests:** Project owner approves or requests modifications
3. **Phase 3 & 4 Gate Approval:** Project owner completes Phase 3 and Phase 4 human gates
4. **Separate Phase 5 Execution Run:** Only after explicit Phase 5 execution authorization, a new dedicated run implements this plan

---

**Document Prepared By:** MarketVoice SEA Phase 5 Planning Agent

**Date:** 2026-08-14

**Status:** `PHASE_5_PLAN_STATUS = READY_FOR_HUMAN_REVIEW`
