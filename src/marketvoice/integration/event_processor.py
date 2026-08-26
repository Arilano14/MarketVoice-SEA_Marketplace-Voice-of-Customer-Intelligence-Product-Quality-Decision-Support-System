"""Event Processing, PII Masking, and Operational Audit Logging.

Phase 11: Operational Automation & Inference Service.
Orchestrates event intake, PII masking, idempotency checking,
FastAPI service invocation, decision routing, and PostgreSQL audit logging.
"""
from __future__ import annotations

import json
import re
import time
from typing import Dict, Optional, Tuple
from datetime import datetime

from marketvoice.database.connection import DBSettings, connect
from marketvoice.database.schema import SCHEMA
from marketvoice.api.services import InferenceService
from marketvoice.integration.idempotency import compute_idempotency_key, compute_payload_hash


# PII Masking Regexes
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_REGEX = re.compile(r"(\+62|62|08)[0-9]{8,12}")
USER_TAG_REGEX = re.compile(r"@\w{3,}")


def mask_pii(text: str) -> str:
    """Mask personally identifiable information (PII) from review text.

    Parameters
    ----------
    text : str
        Input raw text.

    Returns
    -------
    str
        Sanitized text with masked emails, phone numbers, and handles.
    """
    if not text:
        return ""
    masked = EMAIL_REGEX.sub("[REDACTED_EMAIL]", text)
    masked = PHONE_REGEX.sub("[REDACTED_PHONE]", masked)
    masked = USER_TAG_REGEX.sub("[REDACTED_USER]", masked)
    return masked


def process_review_event(
    event_payload: Dict,
    db_settings: Optional[DBSettings] = None,
) -> Dict:
    """Process a single review event through the operational triage pipeline.

    Parameters
    ----------
    event_payload : dict
        Incoming review event containing:
        - 'request_id': str UUID
        - 'source_id': str
        - 'review_id': str
        - 'review_text': str
        - 'rating': int (1-5)
        - 'product_id': Optional[str]
        - 'category_id': Optional[str]
    db_settings : DBSettings, optional
        Database connection settings.

    Returns
    -------
    dict
        Processed workflow response with routing status, priority, and audit trace.
    """
    start_time = time.time()
    db_settings = db_settings or DBSettings.from_env()

    request_id = str(event_payload.get("request_id", "REQ_UNKNOWN"))
    source_id = str(event_payload.get("source_id", "SRC_UNKNOWN"))
    review_id = str(event_payload.get("review_id", "REV_UNKNOWN"))
    raw_text = str(event_payload.get("review_text", ""))
    rating = int(event_payload.get("rating", 3))
    product_id = event_payload.get("product_id")
    category_id = event_payload.get("category_id")

    # 1. PII Sanitization
    sanitized_text = mask_pii(raw_text)

    # 2. Compute Idempotency Key
    idempotency_key = compute_idempotency_key(
        source_id=source_id,
        review_id=review_id,
        calculation_version="1.0",
    )
    payload_str = json.dumps(event_payload, sort_keys=True)
    payload_hash = compute_payload_hash(payload_str)

    conn = connect(db_settings, dbname_override=db_settings.dev_dbname)
    service = InferenceService(db_settings=db_settings)

    try:
        with conn.cursor() as cur:
            # 3. Idempotency Check in Database
            cur.execute(f"""
                SELECT
                    event_sk,
                    routing_destination,
                    priority_score,
                    tier_code,
                    api_response
                FROM {SCHEMA}.operational_event_log
                WHERE idempotency_key = %s
            """, (idempotency_key,))
            existing = cur.fetchone()

            if existing:
                # Return cached response (Idempotent replay)
                return {
                    "request_id": request_id,
                    "idempotency_key": idempotency_key,
                    "is_duplicate": True,
                    "routing_destination": existing["routing_destination"],
                    "priority_score": float(existing["priority_score"]),
                    "priority_tier_code": existing["tier_code"],
                    "status": "CACHED_RESPONSE",
                    "details": existing["api_response"],
                }

        # 4. Step 1: Single-Review Analysis
        analysis = service.analyze_review_text(
            review_text=sanitized_text,
            rating=rating,
            source_id=source_id,
        )

        detected_issues = analysis["detected_issues"]
        primary_issue_id = analysis["primary_issue_id"] or 1

        # 5. Step 2: Contextual Decision Evaluation
        decision = service.evaluate_decision_context(
            source_id=source_id,
            issue_id=primary_issue_id,
            product_id=product_id,
            category_id=category_id,
            current_rating=rating,
        )

        priority_score = float(decision["priority_score"])
        tier_code = str(decision["priority_tier_code"])
        reason_codes = list(decision["reason_codes"])

        # 6. Step 3: Decision Routing
        if tier_code in ["P1_CRITICAL", "P2_HIGH_PRIORITY"]:
            routing_dest = "HUMAN_REVIEW_QUEUE"
        else:
            routing_dest = "MONITORING_LOG"

        api_latency_ms = int((time.time() - start_time) * 1000)

        api_response_payload = {
            "analysis": analysis,
            "decision": decision,
        }

        # 7. Database Logging (Additive Operational Marts)
        with conn.cursor() as cur:
            # Insert operational_event_log
            cur.execute(f"""
                INSERT INTO {SCHEMA}.operational_event_log
                    (idempotency_key, request_id, source_id, source_review_id,
                     payload_hash, rating_value, detected_issues_count,
                     priority_score, tier_code, routing_destination,
                     is_duplicate, raw_payload, api_response)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING event_sk
            """, (
                idempotency_key,
                request_id,
                source_id,
                review_id,
                payload_hash,
                rating,
                len(detected_issues),
                priority_score,
                tier_code,
                routing_dest,
                False,
                json.dumps(event_payload),
                json.dumps(api_response_payload),
            ))
            event_sk = cur.fetchone()["event_sk"]

            # If routed to Human Review, insert into human_review_case
            case_id = None
            if routing_dest == "HUMAN_REVIEW_QUEUE":
                case_id = f"CASE_{idempotency_key[:16].upper()}"
                cur.execute(f"""
                    INSERT INTO {SCHEMA}.human_review_case
                        (case_id, idempotency_key, source_id, product_id, category_id,
                         issue_name, priority_score, tier_code, reason_codes, review_status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (case_id) DO NOTHING
                """, (
                    case_id,
                    idempotency_key,
                    source_id,
                    str(product_id) if product_id else None,
                    str(category_id) if category_id else None,
                    decision["issue_name"],
                    priority_score,
                    tier_code,
                    reason_codes,
                    "PENDING_HUMAN_REVIEW",
                ))

            # Insert workflow_execution metrics
            total_exec_ms = int((time.time() - start_time) * 1000)
            exec_id = f"EXEC_{idempotency_key[:12]}_{int(time.time())}"
            cur.execute(f"""
                INSERT INTO {SCHEMA}.workflow_execution
                    (workflow_id, execution_id, idempotency_key, execution_status,
                     retry_count, api_latency_ms, total_execution_ms)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                "marketvoice_review_triage",
                exec_id,
                idempotency_key,
                "SUCCESS",
                0,
                api_latency_ms,
                total_exec_ms,
            ))

        conn.commit()

        return {
            "request_id": request_id,
            "idempotency_key": idempotency_key,
            "is_duplicate": False,
            "routing_destination": routing_dest,
            "case_id": case_id,
            "priority_score": priority_score,
            "priority_tier_code": tier_code,
            "reason_codes": reason_codes,
            "execution_id": exec_id,
            "status": "PROCESSED_SUCCESSFULLY",
            "evaluated_at": datetime.utcnow().isoformat(),
        }

    finally:
        conn.close()
