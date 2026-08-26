"""FastAPI Pydantic Schemas and Contracts.

Phase 11: Operational Automation & Inference Service.
Strict schema validation for all endpoints, ensuring type safety,
UUID assertions, rating bounds, and deterministic error responses.
"""
from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, UUID4


class SourceIdEnum(str, Enum):
    """Supported source identifiers."""
    SOURCE_A = "SRC_PRDECT_ID_V1"
    SOURCE_B = "SRC_TOKOPEDIA_REVIEWS_2019"


class PriorityTierEnum(str, Enum):
    """Supported priority tier codes."""
    P1_CRITICAL = "P1_CRITICAL"
    P2_HIGH_PRIORITY = "P2_HIGH_PRIORITY"
    P3_MONITORING = "P3_MONITORING"
    P4_INFORMATIONAL = "P4_INFORMATIONAL"


class ActionTypeEnum(str, Enum):
    """Supported human review action types."""
    QUALITY_AUDIT_INITIATED = "QUALITY_AUDIT_INITIATED"
    VENDOR_INQUIRY = "VENDOR_INQUIRY"
    LOGISTICS_REVIEW = "LOGISTICS_REVIEW"
    DISMISSED_FALSE_POSITIVE = "DISMISSED_FALSE_POSITIVE"
    MONITORING_CONFIRMED = "MONITORING_CONFIRMED"


# -------------------------------------------------------------------
# Health and Readiness Schemas
# -------------------------------------------------------------------

class HealthResponse(BaseModel):
    status: str = Field("healthy", description="Service liveness state")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ReadyResponse(BaseModel):
    status: str = Field("ready", description="Service readiness state")
    database_connected: bool = Field(..., description="PostgreSQL connectivity state")
    models_loaded: bool = Field(..., description="NLP and Decision models loaded")
    taxonomy_version: str = Field("1.0", description="Active issue taxonomy version")
    calculation_version: str = Field("1.0", description="Active scoring calculation version")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ModelMetadataResponse(BaseModel):
    service_name: str = "MarketVoice SEA Inference & Decision Service"
    taxonomy_version: str = "1.0"
    calculation_version: str = "1.0"
    active_issues: List[str]
    severity_levels: List[str]
    priority_scoring_weights: Dict[str, float]
    reference_models: Dict[str, str]


# -------------------------------------------------------------------
# Endpoint 1: Single-Review Analysis Schemas (POST /v1/review/analyze)
# -------------------------------------------------------------------

class DetectedIssueItem(BaseModel):
    issue_id: int = Field(..., ge=1, le=5)
    issue_name: str
    keyword_matched: str
    severity_id: int = Field(..., ge=1, le=4)
    severity_name: str
    confidence: float = Field(..., ge=0.0, le=1.0)


class ReviewAnalyzeRequest(BaseModel):
    request_id: UUID4 = Field(..., description="Unique client UUID")
    source_id: SourceIdEnum = Field(..., description="Data source identifier")
    review_text: str = Field(..., min_length=3, max_length=5000, description="Customer review text")
    rating: int = Field(..., ge=1, le=5, description="Customer star rating (1-5)")
    payload_version: str = Field("1.0", description="Payload schema version")


class ReviewAnalyzeResponse(BaseModel):
    request_id: str
    source_id: str
    review_text_sanitized: str
    rating: int
    detected_issues: List[DetectedIssueItem]
    primary_issue_id: Optional[int]
    primary_issue_name: Optional[str]
    overall_confidence: float
    is_negative_sentiment_proxy: bool
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)


# -------------------------------------------------------------------
# Endpoint 2: Contextual Decision Evaluation Schemas (POST /v1/decision/evaluate)
# -------------------------------------------------------------------

class DecisionEvaluateRequest(BaseModel):
    request_id: UUID4 = Field(..., description="Unique client UUID")
    source_id: SourceIdEnum = Field(..., description="Data source identifier")
    issue_id: int = Field(..., ge=1, le=5, description="Target issue category ID (1-5)")
    product_id: Optional[str] = Field(None, description="Product native ID (Source B only)")
    category_id: Optional[str] = Field(None, description="Category identifier")
    current_review_text: Optional[str] = Field(None, max_length=5000, description="Optional incoming review text")
    current_rating: Optional[int] = Field(None, ge=1, le=5, description="Optional incoming rating")
    payload_version: str = Field("1.0", description="Payload schema version")


class DecisionEvaluateResponse(BaseModel):
    request_id: str
    idempotency_key: str
    source_id: str
    grain_type: str  # PRODUCT_X_ISSUE, CATEGORY_X_ISSUE, SOURCE_X_ISSUE
    entity_id: str
    issue_id: int
    issue_name: str
    priority_score: float = Field(..., ge=0.0, le=100.0)
    priority_tier_code: str
    priority_tier_name: str
    guidance_recommendation: str
    reason_codes: List[str]
    context_metrics: Dict[str, float]
    sub_scores: Dict[str, float]
    calculation_version: str = "1.0"
    evaluated_at: datetime = Field(default_factory=datetime.utcnow)


# -------------------------------------------------------------------
# Endpoint 3: Human Review Outcome Schemas (POST /v1/workflow/human-review)
# -------------------------------------------------------------------

class HumanReviewOutcomeRequest(BaseModel):
    case_id: str = Field(..., min_length=5, description="Unique human review case identifier")
    action_type: ActionTypeEnum = Field(..., description="Action taken by human reviewer")
    action_notes: str = Field(..., min_length=5, max_length=2000, description="Rationale notes")
    performed_by: str = Field(..., min_length=2, max_length=100, description="Reviewer name / ID")


class HumanReviewOutcomeResponse(BaseModel):
    outcome_sk: int
    case_id: str
    review_status: str
    action_type: str
    performed_by: str
    recorded_at: datetime = Field(default_factory=datetime.utcnow)


# -------------------------------------------------------------------
# Error Response Schema
# -------------------------------------------------------------------

class ErrorResponse(BaseModel):
    error_code: str
    error_message: str
    request_id: Optional[str] = None
    retryable: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)
