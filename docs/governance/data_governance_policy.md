# MARKETVOICE SEA — DATA GOVERNANCE & SOURCE STRATEGY POLICY

**Document Version**: 1.0  
**Phase**: Phase 0 (Governance & Scope)  
**Classification**: Data Governance Specification  

---

## 1. DUAL-TRACK DATA ARCHITECTURE

To reconcile authentic research benchmarking with comprehensive Business Intelligence prototyping, MarketVoice SEA enforces a strictly governed Dual-Track Data Architecture:

```
                      ┌─────────────────────────────────────────┐
                      │    MARKETVOICE SEA DATA ARCHITECTURE    │
                      └────────────────────┬────────────────────┘
                                           │
         ┌─────────────────────────────────┴─────────────────────────────────┐
         │                                                                   │
         ▼                                                                   ▼
┌─────────────────────────────────┐                         ┌─────────────────────────────────┐
│            TRACK A              │                         │            TRACK B              │
│    ORIGINAL CHALLENGE DATA      │                         │  SYNTHETIC OPERATIONAL EXTENSION│
├─────────────────────────────────┤                         ├─────────────────────────────────┤
│ • Raw Shopee Code League CSV    │                         │ • Product Master & Seller Master│
│ • Authentic Review Text         │                         │ • Category Hierarchy            │
│ • Integer Rating (1-5 Stars)    │                         │ • Event Timestamps              │
│ • Read-Only Staging             │                         │ • Case Handling & SLA Logs      │
│ • Excluded from Public Git      │                         │ • Track B is CONDITIONAL        │
│ • Authentic Benchmark Base      │                         │ • Explicit Flag: is_synthetic=1 │
└─────────────────────────────────┘                         └─────────────────────────────────┘
```

---

## 2. TRACK A: ORIGINAL CHALLENGE DATASET POLICY

### A. Purpose & Usage
Track A data consists of the authentic Shopee Code League Sentiment Analysis competition dataset. It serves as the primary ground-truth benchmark for rating/sentiment classification models and natural language text analysis.

### B. Access & Licensing Controls
1. **License Verification Requirement**: In Phase 2, a formal forensic audit of dataset license permissions, copyright terms, and redistribution restrictions must be completed before any public code repository release.
2. **Repository Exclusion**: Raw competition CSV files must remain strictly outside public Git repositories. The repository `.gitignore` file must enforce the exclusion of `data/raw/` and all unredacted competition archives.
3. **Immutability**: Raw competition data files in `data/raw/` must be treated as read-only assets. All cleaning, normalization, and transformations must be executed via reproducible ETL scripts loading into separate database schemas.

---

## 3. TRACK B: CONDITIONAL SYNTHETIC OPERATIONAL EXTENSION POLICY

### A. Conditionality Principle
Track B synthetic operational data generation is **CONDITIONAL**. 

Synthetic data shall **ONLY** be generated if the Phase 2 Dataset Forensic Audit establishes that authentic operational attributes (e.g., Product Master, Seller Master, Category Hierarchy, Order Timestamps, Case Handling Logs, SLA tracking) are absent from the raw competition dataset.

### B. Unbound Synthetic Parameters
All synthetic generation parameters must remain marked as `TO_BE_DEFINED` until Phase 2 audit findings and Phase 3 requirements specify the missing schema components:

* **Random Generator Seed**: `TO_BE_DEFINED` (A documented fixed seed will be selected during implementation in Phase 3/6 to guarantee 100% reproducibility).
* **Generation Volume**: `TO_BE_DEFINED` (Proportional to staged raw review row counts).
* **Synthetic Schema & Distribution**: `TO_BE_DEFINED` (Designed to mirror realistic e-commerce operational data structures without simulating specific real-world entities).
* **Generator Script Location**: `TO_BE_DEFINED` (e.g., `src/marketvoice/data/synthetic_generator.py` in Phase 6).

### C. Mandatory Synthetic Labeling Rules
If Track B synthetic data is generated:
1. **Database Schema Enforcement**: Every database table containing synthetic attributes must include a mandatory boolean flag column `is_synthetic INTEGER DEFAULT 1` or `is_synthetic BOOLEAN DEFAULT TRUE`.
2. **User Interface Banners**: Every Power BI visual, dashboard report page, API response JSON payload, and export document containing synthetic attributes must display an explicit `[SYNTHETIC DATA EXTENSION]` watermark or label.
3. **No False Commercial Claims**: Synthetic seller defect rates, product return metrics, or resolution SLAs must never be presented as empirical reflections of real Shopee sellers or real commercial products.

---

## 4. DATA PRIVACY & ANONYMIZATION POLICY

### A. PII Scrubbing Rules
To protect user privacy and comply with data protection principles:
1. **Automated Sanitization**: The ETL pipeline in Phase 6 must incorporate regex-based sanitization steps to detect and redact potential Personally Identifiable Information (PII) embedded within review text strings.
2. **Target PII Types**:
   * Phone numbers (e.g., regional format patterns).
   * Email addresses.
   * Personal names or social media handles (where identifiable).
   * Physical delivery addresses or postal tracking codes.

---

## 5. DATA LINEAGE & PROVENANCE POLICY

1. **Traceability**: Every record residing in the PostgreSQL Data Warehouse staging, star schema, or analytical data marts must maintain complete lineage back to its source file or generator script.
2. **Lineage Metadata Columns**:
   * `src_file_name`: Identifier of source CSV or script.
   * `ingested_at`: UTC timestamp of ETL staging execution.
   * `is_synthetic`: Boolean indicator (0 = Track A authentic, 1 = Track B synthetic).
