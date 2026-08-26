# MarketVoice SEA — Power BI Decision Intelligence & Quality Dashboards

**Domain**: Phase 12 — Executive Quality Intelligence & Product Reliability Dashboards  
**Scope**: Semantic Models, DAX Measure Dictionaries, and Analytical Reporting Specifications.

---

## 1. Directory Structure

```text
dashboards/
└── power_bi/
    └── README.md                             # Power BI architectural & semantic documentation
```

---

## 2. Power BI Architecture & Integration

The MarketVoice SEA Power BI reporting suite connects directly to the PostgreSQL analytical warehouse (`marketvoice_warehouse` schema) via DirectQuery or Scheduled Import:

### Core Semantic Mart Connections:
1. **`dim_source`**, **`dim_channel`**, **`dim_category`**, **`dim_product`**: Conformed Dimensions.
2. **`fact_review`**: Central transaction fact table (46,007 rows).
3. **`fact_review_issue`**: Multi-label aspect & defect occurrences (18,863 rows).
4. **`fact_decision_queue`**: Contextual priority triage and action queue (5,090 rows).
5. **`mv_category_benchmark`**, **`mv_product_quality_ranking`**, **`mv_rating_overrepresentation`**: Pre-aggregated summary marts.

---

## 3. Governance & Asset Safety

* **Binary Artifact Isolation**: Large PBIX binary files containing local database connections are managed locally or in staging storage per project data governance rules.
* **DAX Measure Governance**: All core KPIs (Priority Ranking Score, Overrepresentation Ratio, Defect Rate, Net Sentiment Score) are defined deterministically in SQL marts and mirrored in Power BI DAX measures.
