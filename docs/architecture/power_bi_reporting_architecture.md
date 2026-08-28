# MarketVoice SEA — Power BI Reporting Architecture & Implementation Guide

**Document ID**: `ARCH-PBI-001`  
**System**: MarketVoice SEA Business Intelligence & Reporting Layer  
**Governing Phase**: Phase 12 (Final Delivery)  
**Author**: Antigravity Intelligence Architecture  
**Validated**: 2026-08-28  

---

## 1. Architectural Overview

The MarketVoice SEA Power BI reporting architecture translates raw multi-platform customer reviews, machine learning aspect models, and multi-factor decision queues into an executive-ready business intelligence platform.

```text
[Data Sources]
  ├── Source A: PRDECT-ID Indonesian Reviews V1 (5,400 reviews, multi-label)
  └── Source B: Tokopedia Reviews 2019 (40,607 reviews, single-label, SKU metadata)
        │
        ▼
[PostgreSQL 15 Analytical Warehouse: marketvoice_warehouse]
  ├── Conformed Star Dimensions (dim_source, dim_category, dim_product, dim_issue, dim_severity, dim_priority_tier)
  ├── Core Fact Tables (fact_review, fact_review_issue, fact_decision_queue)
  └── High-Performance Pre-Aggregated Views (mv_issue_summary, mv_product_summary, mv_category_summary, etc.)
        │
        ▼  [DirectQuery / Scheduled Import via PostgreSQL ODBC/OLEDB Connector]
[Power BI Semantic Model Engine]
  ├── Relational Star Schema (Strict 1:Many, Unidirectional Filtering)
  ├── 18 Standardized DAX Business Measures (Zero Ad-Hoc Calculated Columns)
  └── Row-Level & Platform Isolation Controls
        │
        ▼
[Executive & Operational BI Visual Interface (7 Focused Pages)]
  ├── Page 1: Executive Overview (Platform CX Posture & Alert KPIs)
  ├── Page 2: Voice of Customer Intelligence (Aspect Deep-Dive & Verbatim Explorer)
  ├── Page 3: Product Quality Intelligence (SKU-Level Chronic Defect Triage — Source B)
  ├── Page 4: Issue Category Deep Dive (Overrepresentation & Recurrence Analysis)
  ├── Page 5: Decision Support Queue (P1/P2 Operational Action Backlog & Reason Codes)
  ├── Page 6: Operational Automation Monitoring (n8n Webhook Latency & HITL Resolution)
  └── Page 7: Data Quality & Model Governance (11 Pre-Flight Checks & Taxonomy Lineage)
```

---

## 2. Ingestion & Semantic Layer Design Principles

### 2.1 Direct-to-Warehouse Principle
Power BI connects directly to the validated PostgreSQL database schema `marketvoice_warehouse`. No interim CSV extracts or unmanaged Excel workbooks are utilized. This guarantees that all executive visuals reference an immutable, single source of truth.

### 2.2 Reusable DAX Measure Governance
* **No Inline Calculation Columns**: Business logic (such as Negative Review %, Overrepresentation Ratio, and Issue Attachment Rate) is encapsulated exclusively in explicit DAX measures.
* **Separation of Concerns**: Fact tables store raw surrogate keys and numerical metrics; dimensional attributes provide filter slicing; DAX measures calculate aggregates dynamically.

### 2.3 Strict Source Grain Isolation
* **Source A Isolation**: Visualizations on Page 3 (Product Quality) explicitly enforce `dim_source[source_id] = "SRC_TOKOPEDIA_REVIEWS_2019"` or aggregate at the Category level to prevent artificial product-level distortion for Source A (which lacks native SKU identifiers).
* **Source B Grain**: Supports drill-down into 3,664 individual products and 158 merchant shops.

---

## 3. Power BI Visual Design & Navigation Standards

### 3.1 Color Palette & Accessibility Standard
* **Brand Primary**: Deep Indigo (`#1E293B`) for navigation headers and primary cards.
* **Alert Statuses**:
  * **Critical / P1**: Crimson (`#DC2626`) — Immediate operational escalation.
  * **High Priority / P2**: Amber Orange (`#F59E0B`) — Near-term quality audit.
  * **Monitoring / P3**: Sky Blue (`#0284C7`) — Statistical surveillance.
  * **Informational / P4**: Slate Gray (`#64748B`) — Baseline logging.
* **Positive Benchmarks**: Emerald Green (`#10B981`) for 5-star ratings and data quality pass indicators.

### 3.2 Visual Density Rules
* Every visual communicates exactly one analytical message.
* No 3D charts, decorative graphics, or chart overload.
* Slicers and cross-filters are synchronized across relevant report pages via standard Power BI filter synchronization.

---

## 4. Setup & Deployment Instructions

### Prerequisites
1. Power BI Desktop (installed locally).
2. PostgreSQL ODBC Driver (Npgsql / PostgreSQL Unicode x64 Driver).
3. Active connection to `localhost:5432` (`marketvoice_dev`).

### Step-by-Step Setup Guide
1. Open **Power BI Desktop**.
2. Click **Get Data** $\to$ **PostgreSQL database**.
3. Set **Server**: `localhost:5432`, **Database**: `marketvoice_dev`.
4. Select Data Connectivity mode: **Import**.
5. In the Navigator dialog, expand `marketvoice_warehouse` schema.
6. Check all dimensions (`dim_*`), fact tables (`fact_*`), operational tables, and summary views (`mv_*`).
7. Click **Load** (or **Transform Data** to verify column data types).
8. In the **Model View**, verify star schema relationships match `semantic_model_spec.md`.
9. Create a dedicated **Measures Table** and paste DAX measures from `kpi_dictionary.md`.
10. Build report pages following the visual layout specifications.
11. Perform refresh validation and verify KPI scorecards match `reconciliation_results.md`.
