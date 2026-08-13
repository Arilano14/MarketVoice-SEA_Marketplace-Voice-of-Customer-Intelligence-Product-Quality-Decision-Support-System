# MARKETVOICE SEA — DATA ARCHITECTURE

**Phase:** 5 — Solution Architecture & Data Model  
**Version:** 1.0  
**Data principle:** source-specific truth and lineage are preserved end-to-end.

## 1. Layer responsibilities

| Layer | Responsibility | Input | Output / consumer | Track |
|---|---|---|---|---|
| Raw source | Immutable accepted evidence. | Canonical source files and manifest evidence. | Source files with checksums/provenance. | A |
| Validation / ingestion | Verify required fields, rating validity, reconciliation, source identification, and privacy-review status. | Raw source. | Validation evidence and accepted/rejected record status. | A |
| Staging | Preserve source-native shape and source-row lineage for controlled transformation. | Validated source records. | Source-specific staging representation. | A |
| Core analytical warehouse | Store governed review truth and conformed dimensions only where valid. | Source-specific staging. | Review facts/dimensions and lineage. | A |
| Curated marts | Produce source/category/product/shop analytical outputs with limitations. | Core Track A entities. | BI and analytical consumers. | A |
| Model / issue / DSS outputs | Store derived results separately from source truth. | Reviewed outputs from later phases. | ML, issue, DSS, and integration consumers. | Future |
| Operational extension | Store explicitly synthetic case/intervention records if separately approved. | Approved synthetic-only workflow data. | Workflow and decision-support context. | B |

## 2. Conceptual source-to-target mapping

| Source | Verified source field | Target concept | Handling rule |
|---|---|---|---|
| A | `Customer Review` | Review text in `fact_review` | Preserve original text reference; privacy review required before exposure. |
| A | `Customer Rating` | Rating reference in `fact_review` / `dim_rating` | Valid 1–5 rating; preserve source provenance. |
| A | `Category` | Source-aware category reference | Preserve raw category; do not force a common cross-source category key. |
| A | `Product Name` | Source-local product descriptor | Retain as review context; not a `dim_product` business key. |
| A | `Sentiment`, `Emotion` | Provided-label attributes of source truth | Source A only; never copied to Source B or overwritten by predictions. |
| A | `Location`, `Price`, `Overall Rating`, `Number Sold`, `Total Review` | Source-local contextual attributes | Retain only where Phase 6 verifies analytical necessity; no invented normalization. |
| B | `text` | Review text in `fact_review` | Preserve original text reference; privacy review required before exposure. |
| B | `rating` | Rating reference in `fact_review` / `dim_rating` | Valid 1–5 rating; preserve source provenance. |
| B | `category` | Source-aware category reference | Preserve raw category and source identity. |
| B | `product_id`, `product_name` | `dim_product` and review product reference | `product_id` is the only authoritative product business key. |
| B | `shop_id` | `dim_shop` and review shop reference | Supports review indicators only; no seller-performance semantics. |
| B | `sold` | Source-local contextual attribute | Raw text metric; 14 nulls and text formatting are retained as a quality limitation. |
| B | `product_url` | Restricted source reference | Not public analytical output by default. |

## 3. Lineage, quality, and source isolation

Every Track A review representation retains source identifier, source-row identity, source-file/checksum reference, and validation/reconciliation reference. A review cannot receive a Source B product/shop reference unless the raw Source B record supplied it. Source A records do not receive inferred product or shop keys.

Quality expectations for Phase 6 are: preserve all accepted source records; validate 1–5 ratings; report nulls rather than silently impute; retain documented Source B `sold` limitations; prevent public analytical use of product URL by default; and record privacy-review status for free text.

## 4. Track separation

Track A contains only authentic review evidence and derived analytical results tied to it. Track B may later contain non-identifying synthetic `case_id`, `event_id`, case/status/priority/intervention attributes, and operational event dates. Track B event dates are never review timestamps, cannot populate authentic time trends, and must remain visibly and structurally synthetic.
