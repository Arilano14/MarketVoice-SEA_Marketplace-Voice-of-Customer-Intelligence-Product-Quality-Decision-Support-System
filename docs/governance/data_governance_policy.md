# MARKETVOICE SEA — DUAL-SOURCE DATA GOVERNANCE & ARCHITECTURE POLICY

**Document Version**: 2.0 (Dual-Source Remediation)  
**Phase**: Phase 1–2 (Data Acquisition & Forensic Audit)  
**Classification**: Data Governance Specification  

---

## 1. DUAL-SOURCE DATA ARCHITECTURE

MarketVoice SEA operates a strictly governed **Dual-Source Indonesian Marketplace Architecture** separating primary annotated research benchmarks from large-scale Business Intelligence prototyping:

```
                      ┌─────────────────────────────────────────┐
                      │    MARKETVOICE SEA DATA ARCHITECTURE    │
                      └────────────────────┬────────────────────┘
                                           │
         ┌─────────────────────────────────┴─────────────────────────────────┐
         │                                                                   │
         ▼                                                                   ▼
┌─────────────────────────────────┐                         ┌─────────────────────────────────┐
│            SOURCE A             │                         │            SOURCE B             │
│   PRIMARY RESEARCH ANNOTATED    │                         │       SECONDARY BI SCALE        │
├─────────────────────────────────┤                         ├─────────────────────────────────┤
│ • Source ID: SRC_PRDECT_ID_V1   │                         │ • Source ID:                    │
│ • Canonical: Mendeley Data      │                         │   SRC_TOKOPEDIA_REVIEWS_2019    │
│   (DOI: 10.17632/574v66hf2v.1)   │                         │ • Canonical: Hugging Face       │
│ • File: PRDECT-ID Dataset.csv   │                         │   (farhamu/tokopedia-2019)      │
│ • License: CC BY 4.0            │                         │ • File: tokopedia-2019.csv      │
│ • Scale: 5,400 rows, 29 cats    │                         │ • License: Apache-2.0           │
│ • Provided Annotated Labels:    │                         │ • Scale: 40,607 rows, 3,664     │
│   Sentiment & Emotion           │                         │   products, 158 shops, 5 cats   │
│ • Landing: data/raw/prdect_id/  │                         │ • Landing: data/raw/tokopedia/  │
└─────────────────────────────────┘                         └─────────────────────────────────┘
```

---

## 2. CRITICAL TWO-SOURCE SEPARATION POLICY

1. **Independent Datasets**: Source A and Source B are distinct datasets. They must never be concatenated, merged, or overwritten during acquisition or staging.
2. **Zero Cross-Source Linkage**:
   - `CROSS_SOURCE_PRODUCT_LINKAGE = NOT_SUPPORTED`
   - `CROSS_SOURCE_SHOP_LINKAGE = NOT_SUPPORTED`
   - `CROSS_SOURCE_ROW_LINKAGE = NOT_SUPPORTED`
   Product names or shop entities from Source A must never be assumed identical to Source B.
3. **Public Distribution Policy**: `project_raw_distribution_policy = LOCAL_ONLY`. Both raw datasets remain excluded from public Git tracking (`data/raw/*` in `.gitignore`).

---

## 3. SOURCE PROVENANCE & LICENSING RECORD

* **Source A (`SRC_PRDECT_ID_V1`)**:
  - *Declared License*: `CC BY 4.0`
  - *Evidence Type*: `CANONICAL_MENDELEY_RECORD`
  - *Annotation Note*: Dataset paper describes emotion annotation criteria developed with clinical-psychology expertise. Labels are documented as `PROVIDED_ANNOTATED_LABEL`.
* **Source B (`SRC_TOKOPEDIA_REVIEWS_2019`)**:
  - *Declared License*: `Apache-2.0`
  - *Evidence Type*: `HUGGINGFACE_DATASET_CARD`
  - *License Confidence*: `DECLARED_BY_REPOSITORY_MAINTAINER`
