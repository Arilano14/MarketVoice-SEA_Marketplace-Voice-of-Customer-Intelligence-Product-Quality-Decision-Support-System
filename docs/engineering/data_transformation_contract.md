# MARKETVOICE SEA — DATA TRANSFORMATION CONTRACT SPECIFICATION

**Document Version**: 1.0 (Phase 2 Hardening)  
**Phase**: Phase 2 (Dataset Forensic Audit & Data Readiness)  
**Classification**: Software Engineering Specification  

---

## 1. OBJECTIVE & BOUNDARY

This specification defines the deterministic rules for deriving standardized datasets (`prdect_reviews_standardized.csv` and `tokopedia_reviews_2019_standardized.csv`) from immutable raw data (`data/raw/`).

- **Raw Data Immutability**: `RAW_EDIT = FORBIDDEN`. Raw files under `data/raw/` are immutable source evidence.
- **Interim Layer Placement**: Standardized datasets are placed under `data/interim/validated/`.
- **System Lineage Key**: Every record receives a deterministic `source_record_key = SHA256(source_id | file_sha256 | row_number)`. This key is a system technical lineage identifier, NOT a marketplace review ID.

---

## 2. TRANSFORMATION RULES MATRIX

### Source A (`SRC_PRDECT_ID_V1`)

| Raw Field | Example Raw Value | Standardized Field | Logical Type | Transformation Rule | Semantics / Status |
|---|---|---|---|---|---|
| `Category` | `Elektronik` | `category_raw` & `category_normalized` | `VARCHAR(255)` | Preserved raw & stripped string. | `EXACT` |
| `Product Name` | `Acer Aspire 4739` | `product_name_raw` | `TEXT` | Preserved raw text string. | `EXACT` |
| `Location` | `Jakarta` | `location_raw` | `VARCHAR(255)` | Preserved raw text string. | `EXACT` |
| `Price` | `Rp1.000` | `price_raw` & `price_idr` | `NUMERIC(12,2)` | Strip `Rp`, remove `.` thousand separator, parse integer/decimal. | `price_parse_status = EXACT` |
| `Overall Rating` | `4.9` | `overall_rating_raw` & `product_overall_rating` | `NUMERIC(3,2)` | Parse float value. | `overall_rating_parse_status = EXACT` |
| `Number Sold` | `100` | `number_sold_raw` & `number_sold_value` | `INTEGER` | Strip whitespace, parse integer. | `number_sold_semantics = EXACT` |
| `Total Review` | `50` | `total_review_raw` & `total_review_value` | `INTEGER` | Strip whitespace, parse integer. | `total_review_parse_status = EXACT` |
| `Customer Rating` | `5` | `customer_rating` | `INTEGER` | Parse integer (range check 1-5). | `EXACT` |
| `Customer Review` | `Produk bagus!` | `review_text_raw` & `review_text_normalized_match` | `TEXT` | Raw preserved; normalized match used ONLY for duplicate matching. | `EXACT` |
| `Sentiment` | `Positive` | `sentiment_label_raw` | `VARCHAR(50)` | Provided annotated sentiment label. | `PROVIDED_ANNOTATED_LABEL` |
| `Emotion` | `Happy` | `emotion_label_raw` | `VARCHAR(50)` | Provided annotated emotion label. | `PROVIDED_ANNOTATED_LABEL` |

### Source B (`SRC_TOKOPEDIA_REVIEWS_2019`)

| Raw Field | Example Raw Value | Standardized Field | Logical Type | Transformation Rule | Semantics / Status |
|---|---|---|---|---|---|
| `text` | `Barang cepat sampai` | `review_text_raw` & `review_text_normalized_match` | `TEXT` | Raw text preserved; normalized match created for matching. | `EXACT` |
| `rating` | `5` | `customer_rating` | `INTEGER` | Parse integer (range check 1-5). | `EXACT` |
| `category` | `elektronik` | `category_raw` & `category_normalized` | `VARCHAR(255)` | Lowercase raw category preserved. | `EXACT` |
| `product_name` | `Adaptor Acer` | `product_name_raw` | `TEXT` | Raw product title string. | `EXACT` |
| `product_id` | `70462002` | `product_id_raw` | `VARCHAR(100)` | Preserved as string identifier. | `MARKETPLACE_PRODUCT_IDENTIFIER` |
| `shop_id` | `1510444` | `shop_id_raw` | `VARCHAR(100)` | Preserved as string identifier. | `MARKETPLACE_SHOP_IDENTIFIER` |
| `sold` | `'2,9rb'`, `'10rb+'` | `sold_raw`, `sold_numeric_value`, `sold_value_semantics` | `VARCHAR(100)` & `INTEGER` | Raw preserved. `'250'` $\rightarrow$ `250` (`EXACT`), `'2,9rb'` $\rightarrow$ `2900` (`APPROXIMATE`), `'10rb+'` $\rightarrow$ `10000` (`LOWER_BOUND`), `NULL` $\rightarrow$ `NULL` (`MISSING`). | `sold_missing_flag = TRUE` if NULL |
| `product_url` | `https://...` | `product_url_raw` | `TEXT` | Preserved. `PRODUCT_URL_PUBLIC_ANALYTICS = DISABLED`. | `EXACT` |

---

## 3. MISSING VALUE & IMPUTATION POLICY

- **Zero Silent Imputation**: `SILENT_IMPUTATION = FORBIDDEN`. No mean, median, or neighbor imputation is permitted.
- **NULL Preservation**: Missing values (such as 14 NULL `sold` values in Source B) are preserved as `NULL` with `sold_missing_flag = TRUE`.
