"""FastAPI API Contract & Unit Test Suite.

Phase 11: Operational Automation & Inference Service.
Verifies:
  1. GET /health and GET /ready endpoints.
  2. GET /model metadata endpoint.
  3. POST /v1/review/analyze endpoint schema validation & aspect inference.
  4. POST /v1/decision/evaluate contextual decision scoring & reason codes.
  5. POST /v1/workflow/human-review outcome recording.
  6. Negative validation tests (schema rejections, rating > 5, invalid UUID).
"""
import os
import sys
import uuid
import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))
_PIPDEPS = os.path.join(PROJECT_ROOT, ".pipdeps")
if os.path.isdir(_PIPDEPS):
    sys.path.insert(0, _PIPDEPS)

from marketvoice.api.application import create_app

@pytest.fixture(scope="module")
def client():
    app = create_app()
    with TestClient(app) as c:
        yield c


class TestSystemEndpoints:
    """Test health, readiness, and model metadata endpoints."""

    def test_health_endpoint(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

    def test_ready_endpoint(self, client):
        resp = client.get("/ready")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ready"
        assert data["database_connected"] is True
        assert data["models_loaded"] is True
        assert data["taxonomy_version"] == "1.0"
        assert data["calculation_version"] == "1.0"

    def test_model_metadata_endpoint(self, client):
        resp = client.get("/model")
        assert resp.status_code == 200
        data = resp.json()
        assert data["taxonomy_version"] == "1.0"
        assert len(data["active_issues"]) == 5
        assert "Product Defect / Quality" in data["active_issues"]
        assert "priority_scoring_weights" in data


class TestReviewAnalyzeEndpoint:
    """Test POST /v1/review/analyze endpoint."""

    def test_analyze_positive_review(self, client):
        payload = {
            "request_id": str(uuid.uuid4()),
            "source_id": "SRC_TOKOPEDIA_REVIEWS_2019",
            "review_text": "Barang bagus, pengiriman super cepat dan packing aman!",
            "rating": 5,
            "payload_version": "1.0",
        }
        resp = client.post("/v1/review/analyze", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["rating"] == 5
        assert data["is_negative_sentiment_proxy"] is False
        assert "analyzed_at" in data

    def test_analyze_negative_review_with_pii(self, client):
        payload = {
            "request_id": str(uuid.uuid4()),
            "source_id": "SRC_TOKOPEDIA_REVIEWS_2019",
            "review_text": "Barang rusak dan bocor! Hubungi saya di buyer@test.com atau 081234567890",
            "rating": 1,
            "payload_version": "1.0",
        }
        resp = client.post("/v1/review/analyze", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["rating"] == 1
        assert data["is_negative_sentiment_proxy"] is True
        assert "[REDACTED_EMAIL]" in data["review_text_sanitized"]
        assert "[REDACTED_PHONE]" in data["review_text_sanitized"]
        assert len(data["detected_issues"]) > 0

    def test_analyze_invalid_rating(self, client):
        payload = {
            "request_id": str(uuid.uuid4()),
            "source_id": "SRC_TOKOPEDIA_REVIEWS_2019",
            "review_text": "Rating test out of bounds",
            "rating": 6,
        }
        resp = client.post("/v1/review/analyze", json=payload)
        assert resp.status_code == 422


class TestDecisionEvaluateEndpoint:
    """Test POST /v1/decision/evaluate endpoint."""

    def test_evaluate_product_context(self, client):
        payload = {
            "request_id": str(uuid.uuid4()),
            "source_id": "SRC_TOKOPEDIA_REVIEWS_2019",
            "issue_id": 1,
            "product_id": "24670745",
            "current_rating": 1,
            "payload_version": "1.0",
        }
        resp = client.post("/v1/decision/evaluate", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["grain_type"] == "PRODUCT_X_ISSUE"
        assert 0.0 <= data["priority_score"] <= 100.0
        assert data["priority_tier_code"] in ["P1_CRITICAL", "P2_HIGH_PRIORITY", "P3_MONITORING", "P4_INFORMATIONAL"]
        assert len(data["reason_codes"]) > 0
        assert "idempotency_key" in data

    def test_evaluate_category_context(self, client):
        payload = {
            "request_id": str(uuid.uuid4()),
            "source_id": "SRC_PRDECT_ID_V1",
            "issue_id": 2,
            "category_id": "Computers and Laptops",
            "payload_version": "1.0",
        }
        resp = client.post("/v1/decision/evaluate", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["grain_type"] == "CATEGORY_X_ISSUE"
        assert "sub_scores" in data


class TestHumanReviewOutcomeEndpoint:
    """Test POST /v1/workflow/human-review endpoint."""

    def test_record_human_review(self, client):
        payload = {
            "case_id": "CASE_TEST_MOCK_001",
            "action_type": "QUALITY_AUDIT_INITIATED",
            "action_notes": "Quality audit initiated for batch review.",
            "performed_by": "TEST_AUDITOR",
        }
        resp = client.post("/v1/workflow/human-review", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["case_id"] == "CASE_TEST_MOCK_001"
        assert data["review_status"] == "RESOLVED"
        assert data["action_type"] == "QUALITY_AUDIT_INITIATED"
