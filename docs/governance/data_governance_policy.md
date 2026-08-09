# MARKETVOICE SEA — DATA GOVERNANCE & SOURCE STRATEGY POLICY

**Document Version**: 1.1 (Remediated)  
**Phase**: Phase 1 (Environment, Repository Foundation & Data Acquisition)  
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
│ • Canonical: shopee-sentiment-  │                         │ • Product Master & Seller Master│
│   analysis (Kaggle Official)    │                         │ • Category Hierarchy            │
│ • Official Files: train.csv,    │                         │ • Event Timestamps              │
│   test.csv, sample_submission   │                         │ • Case Handling & SLA Logs      │
│ • Read-Only Staging             │                         │ • Track B is CONDITIONAL        │
│ • Excluded from Public Git      │                         │ • Explicit Flag: is_synthetic=1 │
│ • Authentic Benchmark Base      │                         │ • Unbound Parameters: TBD       │
└─────────────────────────────────┘                         └─────────────────────────────────┘
```

---

## 2. TRACK A: CANONICAL CHALLENGE DATASET POLICY

### A. Canonical Source Identity
* **Official Competition**: `[Open] Shopee Code League - Sentiment Analysis`
* **Competition Slug**: `shopee-sentiment-analysis`
* **Platform**: Kaggle
* **Organizer**: Shopee
* **Canonical URL**: `https://www.kaggle.com/c/shopee-sentiment-analysis`

### B. Source Hierarchy Protocol
1. Official Kaggle Competition Page (`shopee-sentiment-analysis`).
2. Official Organizer Material / Repository.
3. Archived Competition Copy (with documented provenance).
4. Third-Party Mirror (Only as last resort, requiring explicit user review and provenance logging).

### C. Phase 1 Data-Use Eligibility Audit
1. **Local Academic & Portfolio Rights**: Local non-commercial research and academic portfolio prototyping are permitted under competition terms.
2. **Public Redistribution Constraints**: Raw competition CSV files must remain strictly excluded from public Git repositories via `.gitignore` (`data/raw/*`).
3. **Immutability**: Raw competition files in `data/raw/` are immutable source landing assets. Cleaning or transformation inside `data/raw/` is strictly prohibited (`RAW_EDIT = FORBIDDEN`).

---

## 3. TRACK B: CONDITIONAL SYNTHETIC OPERATIONAL EXTENSION POLICY

### A. Conditionality Principle
Track B synthetic operational data generation is **CONDITIONAL**. Synthetic data shall **ONLY** be generated if the Phase 2 Dataset Forensic Audit establishes that authentic operational attributes (e.g., Product Master, Seller Master, Category Hierarchy, Order Timestamps, Case Handling Logs, SLA tracking) are absent from raw competition files.

### B. Unbound Synthetic Parameters
All synthetic generation parameters remain marked as `TO_BE_DEFINED` until Phase 2 audit findings and Phase 3 requirements specify missing schema components:
* **Random Seed**: `TO_BE_DEFINED`
* **Generation Volume**: `TO_BE_DEFINED`
* **Synthetic Schema**: `TO_BE_DEFINED`

### C. Mandatory Synthetic Labeling Rules
1. **Database Flag**: Every synthetic record must carry `is_synthetic = TRUE`.
2. **UI Watermarks**: Power BI visuals and API payloads containing synthetic data must display `[SYNTHETIC DATA EXTENSION]` banners.
3. **No False Commercial Claims**: Synthetic metrics must never be presented as empirical reflections of real Shopee sellers or real commercial products.

---

## 4. DATA PRIVACY & ANONYMIZATION POLICY

Automated regex PII scrubbing (phone numbers, email addresses, names) will be executed during Phase 6 staging before database insertion.

---

## 5. DATA LINEAGE & PROVENANCE POLICY

Every database record must maintain lineage metadata (`src_file_name`, `ingested_at`, `is_synthetic`).
