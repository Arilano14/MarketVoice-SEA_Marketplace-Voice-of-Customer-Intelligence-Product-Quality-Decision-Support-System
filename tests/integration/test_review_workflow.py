"""Operational Workflow Integration & Idempotency Test Suite.

Phase 11: Operational Automation & Inference Service.
Verifies:
  1. Synthetic demonstration review events processing (SYNTHETIC_P1..P4).
  2. Human-in-the-Loop decision routing for P1/P2 vs P3/P4 monitoring.
  3. Idempotency protection against duplicate event replays.
  4. PII masking on persisted operational payloads.
  5. Additive operational table integrity and zero upstream database mutation.
"""
import json
import os
import sys
import uuid
import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))
_PIPDEPS = os.path.join(PROJECT_ROOT, ".pipdeps")
if os.path.isdir(_PIPDEPS):
    sys.path.insert(0, _PIPDEPS)

from marketvoice.database.connection import DBSettings, connect
from marketvoice.database.schema import SCHEMA
from marketvoice.integration.event_processor import process_review_event, mask_pii
from marketvoice.integration.idempotency import compute_idempotency_key


@pytest.fixture(scope="module")
def db_conn():
    settings = DBSettings.from_env()
    conn = connect(settings, dbname_override=settings.dev_dbname)
    yield conn
    conn.close()


class TestOperationalEventPipeline:
    """Test operational review event processing and routing."""

    def test_pii_masking_utility(self):
        text = "Hubungi cs kami di admin@tokopedia.com atau whatsapp 081234567890 dan IG @seller_official"
        masked = mask_pii(text)
        assert "[REDACTED_EMAIL]" in masked
        assert "[REDACTED_PHONE]" in masked
        assert "[REDACTED_USER]" in masked
        assert "admin@tokopedia.com" not in masked
        assert "081234567890" not in masked

    def test_synthetic_p1_p2_human_review_routing(self):
        event = {
            "request_id": str(uuid.uuid4()),
            "source_id": "SRC_TOKOPEDIA_REVIEWS_2019",
            "review_id": f"TEST_HITL_{uuid.uuid4().hex[:8]}",
            "product_id": "24670745",
            "category_id": "Komputer & Aksesoris",
            "review_text": "Barang rusak dan bocor tinta parah! Hubungi buyer@test.com",
            "rating": 1,
        }
        res = process_review_event(event)
        assert res["routing_destination"] == "HUMAN_REVIEW_QUEUE"
        assert res["priority_tier_code"] in ["P1_CRITICAL", "P2_HIGH_PRIORITY"]
        assert res["case_id"] is not None
        assert res["is_duplicate"] is False

    def test_synthetic_p4_monitoring_routing(self):
        event = {
            "request_id": str(uuid.uuid4()),
            "source_id": "SRC_TOKOPEDIA_REVIEWS_2019",
            "review_id": f"TEST_MONITOR_{uuid.uuid4().hex[:8]}",
            "product_id": "418660637",
            "category_id": "Handphone & Aksesoris",
            "review_text": "Barang original mantap fast charging berfungsi baik!",
            "rating": 5,
        }
        res = process_review_event(event)
        assert res["routing_destination"] == "MONITORING_LOG"
        assert res["priority_tier_code"] == "P4_INFORMATIONAL"
        assert res["is_duplicate"] is False

    def test_idempotency_duplicate_protection(self, db_conn):
        review_id = f"IDEMPOTENT_TEST_{uuid.uuid4().hex[:8]}"
        event = {
            "request_id": str(uuid.uuid4()),
            "source_id": "SRC_TOKOPEDIA_REVIEWS_2019",
            "review_id": review_id,
            "product_id": "24670745",
            "review_text": "Duplicate test review text",
            "rating": 2,
        }
        # First submission
        res1 = process_review_event(event)
        assert res1["is_duplicate"] is False

        # Duplicate replay submission
        res2 = process_review_event(event)
        assert res2["is_duplicate"] is True
        assert res2["status"] == "CACHED_RESPONSE"
        assert res2["idempotency_key"] == res1["idempotency_key"]

        # Assert exactly 1 row exists in operational_event_log for this key
        with db_conn.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) AS cnt
                FROM marketvoice_warehouse.operational_event_log
                WHERE idempotency_key = %s
            """, (res1["idempotency_key"],))
            assert cur.fetchone()["cnt"] == 1

    def test_warehouse_fact_non_mutation(self, db_conn):
        with db_conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS cnt FROM marketvoice_warehouse.fact_review")
            assert cur.fetchone()["cnt"] == 46007

            cur.execute("SELECT COUNT(*) AS cnt FROM marketvoice_warehouse.fact_review_issue")
            assert cur.fetchone()["cnt"] == 18863

            cur.execute("SELECT COUNT(*) AS cnt FROM marketvoice_warehouse.fact_decision_queue")
            assert cur.fetchone()["cnt"] == 5090
