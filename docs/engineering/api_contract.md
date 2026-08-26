# MarketVoice SEA — Phase 11 API Contract Specification

**Document Version**: 1.0  
**Phase**: Phase 11 — Operational Automation & Inference Service  
**Architecture**: FastAPI ASGI Microservice  
**Status**: ACTIVE / PRODUCTION-READY  

---

## 1. Executive Overview

The MarketVoice SEA Operational Microservice exposes high-throughput, low-latency endpoints for:
1. **Single-Review NLP Intelligence** (`POST /v1/review/analyze`): Real-time keyword aspect matching against frozen Taxonomy v1.0, rating-based severity proxies, and confidence estimation.
2. **Contextual Decision Support System (DSS) Scoring** (`POST /v1/decision/evaluate`): Multi-criteria Priority Risk Score (PRS) evaluation derived from validated historical evidence across Product, Category, and Source grains.
3. **Human-in-the-Loop Triage Resolution** (`POST /v1/workflow/human-review`): Recording human auditor resolutions, root-cause notes, and operational actions.
4. **Service Health & Metadata** (`GET /health`, `GET /ready`, `GET /model`).

---

## 2. Global Request & Response Specifications

### Base URL
* Local / Dev: `http://localhost:8000`

### Headers
* `Content-Type`: `application/json`
* `Accept`: `application/json`

### Error Response Envelope
```json
{
  "error_code": "INVALID_PAYLOAD_SCHEMA",
  "error_message": "Request validation failed against Pydantic schema.",
  "details": [...],
  "retryable": false,
  "timestamp": "2026-08-26T07:15:00.000000Z"
}
```

---

## 3. Endpoints

### 3.1 `GET /health`
* **Purpose**: Process liveness probe.
* **Response**: `200 OK`
```json
{
  "status": "healthy",
  "timestamp": "2026-08-26T07:15:00.000000Z"
}
```

---

### 3.2 `GET /ready`
* **Purpose**: Full system readiness check (PostgreSQL database connectivity and ML/Taxonomy memory readiness).
* **Response**: `200 OK`
```json
{
  "status": "ready",
  "database_connected": true,
  "models_loaded": true,
  "taxonomy_version": "1.0",
  "calculation_version": "1.0",
  "timestamp": "2026-08-26T07:15:00.000000Z"
}
```

---

### 3.3 `GET /model`
* **Purpose**: Inspect model metadata, active taxonomy issues, severity levels, and priority weights.
* **Response**: `200 OK`
```json
{
  "service_name": "MarketVoice SEA Inference & Decision Service",
  "taxonomy_version": "1.0",
  "calculation_version": "1.0",
  "active_issues": [
    "Product Defect / Quality",
    "Packaging / Shipping Damage",
    "Order Inaccuracy / Missing Items",
    "Delivery / Logistics Issue",
    "Customer Service / Seller Response"
  ],
  "severity_levels": ["CRITICAL", "HIGH", "MODERATE", "LOW"],
  "priority_scoring_weights": {
    "severity_ratio": 0.30,
    "dissatisfaction_ratio": 0.25,
    "recurrence": 0.20,
    "volume": 0.15,
    "confidence": 0.10
  },
  "reference_models": {
    "sentiment_classifier": "tfidf_linear_svc_sentiment_srca_v1.0.0",
    "emotion_classifier": "tfidf_logistic_regression_emotion_srca_v1.0.0",
    "rating_sourcea": "tfidf_tfidf_linear_svc_rating_sourcea_v1.0.0",
    "rating_sourceb": "tfidf_tfidf_linear_svc_rating_sourceb_v1.0.0"
  }
}
```

---

### 3.4 `POST /v1/review/analyze`
* **Purpose**: Aspect keyword classification and severity proxy inference on incoming review text.
* **Request**:
```json
{
  "request_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "source_id": "SRC_TOKOPEDIA_REVIEWS_2019",
  "review_text": "Barang rusak parah, tinta bocor dan tidak terdeteksi sama sekali di printer! Hubungi wa 081234567890",
  "rating": 1,
  "payload_version": "1.0"
}
```
* **Response**: `200 OK`
```json
{
  "request_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "source_id": "SRC_TOKOPEDIA_REVIEWS_2019",
  "review_text_sanitized": "Barang rusak parah, tinta bocor dan tidak terdeteksi sama sekali di printer! Hubungi wa [REDACTED_PHONE]",
  "rating": 1,
  "detected_issues": [
    {
      "issue_id": 1,
      "issue_name": "Product Defect / Quality",
      "keyword_matched": "rusak",
      "severity_id": 1,
      "severity_name": "CRITICAL",
      "confidence": 0.80
    }
  ],
  "primary_issue_id": 1,
  "primary_issue_name": "Product Defect / Quality",
  "overall_confidence": 0.80,
  "is_negative_sentiment_proxy": true,
  "analyzed_at": "2026-08-26T07:15:00.000000Z"
}
```

---

### 3.5 `POST /v1/decision/evaluate`
* **Purpose**: Contextual multi-factor Decision Support System (DSS) evaluation. Retrieves validated evidence support, recurrence, and dissatisfaction metrics from database marts.
* **Request**:
```json
{
  "request_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "source_id": "SRC_TOKOPEDIA_REVIEWS_2019",
  "issue_id": 1,
  "product_id": "24670745",
  "current_rating": 1,
  "payload_version": "1.0"
}
```
* **Response**: `200 OK`
```json
{
  "request_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "idempotency_key": "8498366af58b64614ebf11884a6fd0d1dc1f3a7ce93f8019c4638b613043c16e",
  "source_id": "SRC_TOKOPEDIA_REVIEWS_2019",
  "grain_type": "PRODUCT_X_ISSUE",
  "entity_id": "PROD_24670745",
  "issue_id": 1,
  "issue_name": "Product Defect / Quality",
  "priority_score": 68.62,
  "priority_tier_code": "P2_HIGH_PRIORITY",
  "priority_tier_name": "High Priority",
  "guidance_recommendation": "Priority operational investigation: initiate supplier inquiry or product quality audit.",
  "reason_codes": [
    "RC_CRITICAL_SEVERITY_DOMINANCE",
    "RC_HIGH_DISSATISFACTION_DRIVER",
    "RC_HIGH_CONFIDENCE_SIGNAL",
    "RC_SMALL_SAMPLE_CAUTION"
  ],
  "context_metrics": {
    "evidence_support": 12.0,
    "distinct_review_events": 12.0,
    "critical_severity_ratio": 0.8333
  },
  "sub_scores": {
    "severity_impact_score": 25.0,
    "dissatisfaction_score": 25.0,
    "recurrence_score": 5.4,
    "volume_score": 3.22,
    "confidence_score": 10.0
  },
  "calculation_version": "1.0",
  "evaluated_at": "2026-08-26T07:15:00.000000Z"
}
```

---

### 3.6 `POST /v1/workflow/human-review`
* **Purpose**: Records human triage resolution for P1/P2 cases.
* **Request**:
```json
{
  "case_id": "CASE_8498366AF58B6461",
  "action_type": "VENDOR_INQUIRY",
  "action_notes": "Defect confirmed with supplier. Batch #4402 recalled.",
  "performed_by": "QA_ENGINEER_01"
}
```
* **Response**: `200 OK`
```json
{
  "outcome_sk": 1,
  "case_id": "CASE_8498366AF58B6461",
  "review_status": "RESOLVED",
  "action_type": "VENDOR_INQUIRY",
  "performed_by": "QA_ENGINEER_01",
  "recorded_at": "2026-08-26T07:15:00.000000Z"
}
```
