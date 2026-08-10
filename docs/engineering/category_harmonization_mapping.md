# MARKETVOICE SEA — CATEGORY HARMONIZATION MAPPING SPECIFICATION

**Document Version**: 1.0 (Phase 2 Hardening)  
**Phase**: Phase 2 (Dataset Forensic Audit & Data Readiness)  
**Classification**: Software Engineering & Data Governance Specification  

---

## 1. POLICY & PRINCIPLES

1. **Raw Visibility**: Raw business categories (`category_raw`) must remain visible and un-coerced in all standardized datasets.
2. **No Fake Categories**: Creating arbitrary business categories (such as `"Unmapped Secondary Category"`) is strictly prohibited. Unmapped categories receive `canonical_category_family = NULL` and `category_mapping_status = UNMAPPED`.
3. **Qualified Relationships**: Category mappings are explicitly qualified as `EXACT`, `BROADER`, `NARROWER`, `RELATED`, `AMBIGUOUS`, or `UNMAPPED`.

---

## 2. HARMONIZATION MAPPING CONTRACT

| Source A Category (`PRDECT-ID`) | Proposed Canonical Family | Source B Category (`Tokopedia 2019`) | Mapping Status | Mapping Confidence |
|---|---|---|---|---|
| `Elektronik` | `Elektronik` | `elektronik` | `EXACT` | `HIGH` |
| `Handphone & Tablet` | `Handphone & Tablet` | `handphone` | `NARROWER` | `HIGH` |
| `Fashion Pria`, `Fashion Wanita`, `Fashion Muslim`, `Fashion Anak & Bayi` | `Fashion` | `fashion` | `NARROWER_TO_BROADER` | `HIGH` |
| `Olahraga` | `Olahraga` | `olahraga` | `EXACT` | `HIGH` |
| `Pertukangan` | `Pertukangan` | `pertukangan` | `EXACT` | `HIGH` |
| `Dapur`, `Kesehatan`, `Kecantikan`, `Buku`, `Otomotif`, etc. (20 categories) | `NULL` | `UNMAPPED` | `UNMAPPED` | `N/A` |

---

## 3. STAGING FIELDS

Every standardized dataset record carries:
- `category_raw`: Raw string as captured in raw dataset.
- `category_normalized`: Trimmed lowercase string.
- `canonical_category_family`: Mapped high-level family (or `NULL` if unmapped).
- `category_mapping_status`: `EXACT`, `NARROWER`, `BROADER`, or `UNMAPPED`.
