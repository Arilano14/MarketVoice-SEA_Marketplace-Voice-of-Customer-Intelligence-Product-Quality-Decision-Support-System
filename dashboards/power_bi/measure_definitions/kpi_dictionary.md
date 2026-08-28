# MarketVoice SEA — KPI & DAX Measure Dictionary

**Version**: `1.0.0`  
**Governing Calculation Standard**: MarketVoice SEA Calculation Standard v1.0  
**Warehouse Target**: `marketvoice_warehouse`  

---

## 1. Executive Core Volume & Quality KPIs

### 1.1 `Total Reviews`
* **Business Definition**: Total number of ingested marketplace customer review transactions.
* **DAX Formula**:
  ```dax
  Total Reviews = COUNTROWS('fact_review')
  ```
* **Format**: Integer (`#,##0`)
* **Expected Total**: `46,007`
* **Grain**: Review level.
* **Interpretation**: Baseline volume indicator.

### 1.2 `Average Rating`
* **Business Definition**: Mean customer star rating across all reviews.
* **DAX Formula**:
  ```dax
  Average Rating = AVERAGE('fact_review'[rating_value])
  ```
* **Format**: Decimal (`0.00`)
* **Expected Total**: `4.46`
* **Grain**: Aggregate.
* **Interpretation**: Overall customer satisfaction benchmark.

### 1.3 `Negative Review Count`
* **Business Definition**: Count of reviews with star rating 1 or 2.
* **DAX Formula**:
  ```dax
  Negative Review Count = 
  CALCULATE(
      COUNTROWS('fact_review'),
      'fact_review'[rating_value] <= 2
  )
  ```
* **Format**: Integer (`#,##0`)
* **Expected Total**: `3,318`
* **Interpretation**: Raw dissatisfaction volume requiring monitoring.

### 1.4 `Negative Review %`
* **Business Definition**: Proportion of total reviews that expressed negative sentiment (rating 1 or 2).
* **DAX Formula**:
  ```dax
  Negative Review % = 
  DIVIDE(
      [Negative Review Count],
      [Total Reviews],
      0
  )
  ```
* **Format**: Percentage (`0.00%`)
* **Expected Total**: `7.21%`
* **Interpretation**: Key dissatisfaction risk benchmark.

---

## 2. Issue Intelligence & Aspect KPIs

### 2.1 `Total Detected Issues`
* **Business Definition**: Total number of issue occurrences extracted via NLP taxonomy classification.
* **DAX Formula**:
  ```dax
  Total Detected Issues = COUNTROWS('fact_review_issue')
  ```
* **Format**: Integer (`#,##0`)
* **Expected Total**: `18,863`
* **Grain**: Issue assignment level (multi-label).
* **Interpretation**: Total defect signal volume.

### 2.2 `Reviews With Issues`
* **Business Definition**: Distinct count of reviews that contain at least one detected issue.
* **DAX Formula**:
  ```dax
  Reviews With Issues = DISTINCTCOUNT('fact_review_issue'[review_sk])
  ```
* **Format**: Integer (`#,##0`)
* **Expected Total**: `15,270`
* **Interpretation**: Customer reach of marketplace friction.

### 2.3 `Issue Attachment Rate %`
* **Business Definition**: Percentage of all reviews that contain at least one detected issue aspect.
* **DAX Formula**:
  ```dax
  Issue Attachment Rate % = 
  DIVIDE(
      [Reviews With Issues],
      [Total Reviews],
      0
  )
  ```
* **Format**: Percentage (`0.00%`)
* **Expected Total**: `33.19%`
* **Interpretation**: Share of customer feedback discussing actionable service or product attributes.

### 2.4 `Average Model Confidence`
* **Business Definition**: Mean classification certainty of detected issue keywords.
* **DAX Formula**:
  ```dax
  Average Model Confidence = AVERAGE('fact_review_issue'[confidence])
  ```
* **Format**: Decimal (`0.0000`)
* **Expected Total**: `0.3758`
* **Interpretation**: Overall NLP classification signal certainty.

### 2.5 `Critical Defect Count`
* **Business Definition**: Count of issue occurrences classified as Critical Severity (associated with 1-star reviews).
* **DAX Formula**:
  ```dax
  Critical Defect Count = 
  CALCULATE(
      COUNTROWS('fact_review_issue'),
      'fact_review_issue'[severity_id] = 1
  )
  ```
* **Format**: Integer (`#,##0`)
* **Interpretation**: Severe product failures or non-functional items.

---

## 3. Decision Support System (DSS) KPIs

### 3.1 `Decision Queue Total`
* **Business Definition**: Total number of evaluated decision cases across all grains.
* **DAX Formula**:
  ```dax
  Decision Queue Total = COUNTROWS('fact_decision_queue')
  ```
* **Format**: Integer (`#,##0`)
* **Expected Total**: `5,090`
* **Interpretation**: Total universe of triaged entities.

### 3.2 `Actionable Cases (P1+P2)`
* **Business Definition**: High-priority decision cases requiring near-term investigation or urgent audit.
* **DAX Formula**:
  ```dax
  Actionable Cases (P1+P2) = 
  CALCULATE(
      COUNTROWS('fact_decision_queue'),
      'fact_decision_queue'[tier_id] IN {1, 2}
  )
  ```
* **Format**: Integer (`#,##0`)
* **Expected Total**: `192` (all P2 cases in current frozen warehouse)
* **Interpretation**: Immediate operations workload.

### 3.3 `Actionable Cases %`
* **Business Definition**: Share of total decision queue categorized as P1 or P2.
* **DAX Formula**:
  ```dax
  Actionable Cases % = 
  DIVIDE(
      [Actionable Cases (P1+P2)],
      [Decision Queue Total],
      0
  )
  ```
* **Format**: Percentage (`0.00%`)
* **Expected Total**: `3.77%`
* **Interpretation**: Demonstrates noise filtration efficiency (96.23% filtered into monitoring or informational).

### 3.4 `Average Priority Risk Score (PRS)`
* **Business Definition**: Mean multi-factor Priority Risk Score across evaluated cases.
* **DAX Formula**:
  ```dax
  Average PRS = AVERAGE('fact_decision_queue'[priority_score])
  ```
* **Format**: Decimal (`0.00`)
* **Expected Total**: `18.24` (Bounded between `3.62` and `68.62`)
* **Interpretation**: Central tendency of portfolio risk.

### 3.5 `Max Priority Risk Score`
* **Business Definition**: Maximum observed Priority Risk Score.
* **DAX Formula**:
  ```dax
  Max PRS = MAX('fact_decision_queue'[priority_score])
  ```
* **Format**: Decimal (`0.00`)
* **Expected Total**: `68.62`
* **Interpretation**: Peak risk ceiling.

---

## 4. Operational Automation KPIs (Demonstration Scope)

### 4.1 `Operational Events Logged`
* **Business Definition**: Total incoming webhook review events ingested through n8n pipeline.
* **DAX Formula**:
  ```dax
  Operational Events Logged = COUNTROWS('operational_event_log')
  ```
* **Format**: Integer (`#,##0`)
* **Expected Total**: `37`
* **Note**: Synthetic operational demonstration data.

### 4.2 `Human Review Cases Created`
* **Business Definition**: Cases routed by decision switch to human review queue.
* **DAX Formula**:
  ```dax
  Human Review Cases Created = COUNTROWS('human_review_case')
  ```
* **Format**: Integer (`#,##0`)
* **Expected Total**: `13`

### 4.3 `Human Review Resolution Count`
* **Business Definition**: Recorded human review resolution outcomes.
* **DAX Formula**:
  ```dax
  Human Review Resolution Count = COUNTROWS('human_review_outcome')
  ```
* **Format**: Integer (`#,##0`)
* **Expected Total**: `14`

---

## 5. Measure Governance Matrix

| Measure Name | Home Table | Format String | Reconciled SQL Query |
|---|---|---|---|
| `Total Reviews` | `fact_review` | `#,##0` | `SELECT COUNT(*) FROM fact_review` |
| `Average Rating` | `fact_review` | `0.00` | `SELECT AVG(rating_value) FROM fact_review` |
| `Negative Review Count` | `fact_review` | `#,##0` | `SELECT COUNT(*) FROM fact_review WHERE rating_value <= 2` |
| `Negative Review %` | `fact_review` | `0.00%` | `SELECT COUNT(*)::numeric / 46007 FROM fact_review WHERE rating_value <= 2` |
| `Total Detected Issues` | `fact_review_issue` | `#,##0` | `SELECT COUNT(*) FROM fact_review_issue` |
| `Reviews With Issues` | `fact_review_issue` | `#,##0` | `SELECT COUNT(DISTINCT review_sk) FROM fact_review_issue` |
| `Issue Attachment Rate %`| `fact_review_issue` | `0.00%` | `SELECT COUNT(DISTINCT review_sk)::numeric / 46007 FROM fact_review_issue` |
| `Average Model Confidence`| `fact_review_issue` | `0.0000`| `SELECT AVG(confidence) FROM fact_review_issue` |
| `Decision Queue Total` | `fact_decision_queue`| `#,##0` | `SELECT COUNT(*) FROM fact_decision_queue` |
| `Actionable Cases (P1+P2)`| `fact_decision_queue`| `#,##0` | `SELECT COUNT(*) FROM fact_decision_queue WHERE tier_id IN (1,2)` |
| `Actionable Cases %` | `fact_decision_queue`| `0.00%` | `SELECT COUNT(*)::numeric / 5090 FROM fact_decision_queue WHERE tier_id IN (1,2)` |
| `Average PRS` | `fact_decision_queue`| `0.00` | `SELECT AVG(priority_score) FROM fact_decision_queue` |
