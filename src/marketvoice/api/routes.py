"""FastAPI Endpoint Route Handlers.

Phase 11: Operational Automation & Inference Service.
Exposes endpoints for liveness, readiness, review analysis,
contextual decision evaluation, and human-review outcome recording.
"""
from __future__ import annotations

from datetime import datetime
from typing import Dict
from fastapi import APIRouter, HTTPException, status

from marketvoice.api.schemas import (
    HealthResponse,
    ReadyResponse,
    ModelMetadataResponse,
    ReviewAnalyzeRequest,
    ReviewAnalyzeResponse,
    DecisionEvaluateRequest,
    DecisionEvaluateResponse,
    HumanReviewOutcomeRequest,
    HumanReviewOutcomeResponse,
)
from marketvoice.api.services import InferenceService
from marketvoice.analytics.taxonomy import ISSUE_TAXONOMY, TAXONOMY_VERSION
from marketvoice.decision.priority_score import DEFAULT_WEIGHTS, CALCULATION_VERSION
from marketvoice.database.connection import DBSettings, connect
from marketvoice.database.schema import SCHEMA
from marketvoice.integration.idempotency import compute_idempotency_key
from marketvoice.integration.event_processor import mask_pii

router = APIRouter()
_service = InferenceService()


# -------------------------------------------------------------------
# Liveness & Readiness Endpoints
# -------------------------------------------------------------------

@router.get("/health", response_model=HealthResponse, tags=["System"])
def get_health() -> HealthResponse:
    """Liveness check endpoint."""
    return HealthResponse(status="healthy", timestamp=datetime.utcnow())


@router.get("/ready", response_model=ReadyResponse, tags=["System"])
def get_ready() -> ReadyResponse:
    """Readiness probe checking PostgreSQL connectivity and model availability."""
    db_connected = False
    try:
        settings = DBSettings.from_env()
        conn = connect(settings, dbname_override=settings.dev_dbname)
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
        conn.close()
        db_connected = True
    except Exception:
        db_connected = False

    models_loaded = bool(ISSUE_TAXONOMY and DEFAULT_WEIGHTS)
    status_str = "ready" if (db_connected and models_loaded) else "unready"

    if not db_connected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connectivity check failed.",
        )

    return ReadyResponse(
        status=status_str,
        database_connected=db_connected,
        models_loaded=models_loaded,
        taxonomy_version=TAXONOMY_VERSION,
        calculation_version=CALCULATION_VERSION,
        timestamp=datetime.utcnow(),
    )


@router.get("/model", response_model=ModelMetadataResponse, tags=["Metadata"])
def get_model_metadata() -> ModelMetadataResponse:
    """Model cards and taxonomy metadata endpoint."""
    issue_names = [v["name"] for v in ISSUE_TAXONOMY.values()]
    return ModelMetadataResponse(
        taxonomy_version=TAXONOMY_VERSION,
        calculation_version=CALCULATION_VERSION,
        active_issues=issue_names,
        severity_levels=["CRITICAL", "HIGH", "MODERATE", "LOW"],
        priority_scoring_weights=DEFAULT_WEIGHTS,
        reference_models={
            "sentiment_classifier": "tfidf_linear_svc_sentiment_srca_v1.0.0",
            "emotion_classifier": "tfidf_logistic_regression_emotion_srca_v1.0.0",
            "rating_sourcea": "tfidf_tfidf_linear_svc_rating_sourcea_v1.0.0",
            "rating_sourceb": "tfidf_tfidf_linear_svc_rating_sourceb_v1.0.0",
        },
    )


# -------------------------------------------------------------------
# Endpoint 1: Single-Review Analysis (POST /v1/review/analyze)
# -------------------------------------------------------------------

@router.post("/v1/review/analyze", response_model=ReviewAnalyzeResponse, tags=["Inference"])
def analyze_review(req: ReviewAnalyzeRequest) -> ReviewAnalyzeResponse:
    """Analyze single review text for detected issue aspects, severity proxy, and confidence.

    Note: This endpoint performs single-text NLP inference only. It does NOT
    calculate multi-factor Decision Priority Scores (use /v1/decision/evaluate).
    """
    sanitized_text = mask_pii(req.review_text)
    res = _service.analyze_review_text(
        review_text=sanitized_text,
        rating=req.rating,
        source_id=req.source_id.value,
    )

    return ReviewAnalyzeResponse(
        request_id=str(req.request_id),
        source_id=req.source_id.value,
        review_text_sanitized=sanitized_text,
        rating=req.rating,
        detected_issues=res["detected_issues"],
        primary_issue_id=res["primary_issue_id"],
        primary_issue_name=res["primary_issue_name"],
        overall_confidence=res["overall_confidence"],
        is_negative_sentiment_proxy=res["is_negative_sentiment_proxy"],
        analyzed_at=datetime.utcnow(),
    )


# -------------------------------------------------------------------
# Endpoint 2: Contextual Decision Evaluation (POST /v1/decision/evaluate)
# -------------------------------------------------------------------

@router.post("/v1/decision/evaluate", response_model=DecisionEvaluateResponse, tags=["Decision Support"])
def evaluate_decision(req: DecisionEvaluateRequest) -> DecisionEvaluateResponse:
    """Evaluate multi-factor Priority Risk Score (PRS) using contextual evidence.

    Retrieves validated metrics from Phase 10 Decision Marts across
    Product, Category, or Source grains.
    """
    # Compute deterministic idempotency key
    review_ref = req.product_id or req.category_id or "global"
    idempotency_key = compute_idempotency_key(
        source_id=req.source_id.value,
        review_id=f"{review_ref}_iss_{req.issue_id}",
        calculation_version=CALCULATION_VERSION,
    )

    res = _service.evaluate_decision_context(
        source_id=req.source_id.value,
        issue_id=req.issue_id,
        product_id=req.product_id,
        category_id=req.category_id,
        current_rating=req.current_rating,
    )

    return DecisionEvaluateResponse(
        request_id=str(req.request_id),
        idempotency_key=idempotency_key,
        source_id=req.source_id.value,
        grain_type=res["grain_type"],
        entity_id=res["entity_id"],
        issue_id=res["issue_id"],
        issue_name=res["issue_name"],
        priority_score=res["priority_score"],
        priority_tier_code=res["priority_tier_code"],
        priority_tier_name=res["priority_tier_name"],
        guidance_recommendation=res["guidance_recommendation"],
        reason_codes=res["reason_codes"],
        context_metrics=res.get("context_metrics", {}),
        sub_scores=res.get("sub_scores", {}),
        calculation_version=CALCULATION_VERSION,
        evaluated_at=datetime.utcnow(),
    )


# -------------------------------------------------------------------
# Endpoint 3: Human Review Outcome Recording (POST /v1/workflow/human-review)
# -------------------------------------------------------------------

@router.post("/v1/workflow/human-review", response_model=HumanReviewOutcomeResponse, tags=["Workflow"])
def record_human_review(req: HumanReviewOutcomeRequest) -> HumanReviewOutcomeResponse:
    """Record human review triage resolution for a P1/P2 case."""
    settings = DBSettings.from_env()
    conn = connect(settings, dbname_override=settings.dev_dbname)

    outcome_sk = 0
    try:
        with conn.cursor() as cur:
            # 1. Update human_review_case status
            cur.execute(f"""
                UPDATE {SCHEMA}.human_review_case
                SET review_status = 'RESOLVED',
                    assigned_reviewer = %s,
                    resolution_notes = %s,
                    resolution_action = %s,
                    resolved_at = NOW()
                WHERE case_id = %s
                RETURNING case_sk
            """, (req.performed_by, req.action_notes, req.action_type.value, req.case_id))
            row = cur.fetchone()
            case_sk = row["case_sk"] if row else None

            # 2. Insert into human_review_outcome
            cur.execute(f"""
                INSERT INTO {SCHEMA}.human_review_outcome
                    (case_sk, idempotency_key, action_type, action_notes, performed_by)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING outcome_sk
            """, (case_sk, f"OUTCOME_{req.case_id}", req.action_type.value, req.action_notes, req.performed_by))
            out_row = cur.fetchone()
            outcome_sk = out_row["outcome_sk"] if out_row else 1

        conn.commit()
    finally:
        conn.close()

    return HumanReviewOutcomeResponse(
        outcome_sk=outcome_sk,
        case_id=req.case_id,
        review_status="RESOLVED",
        action_type=req.action_type.value,
        performed_by=req.performed_by,
        recorded_at=datetime.utcnow(),
    )
