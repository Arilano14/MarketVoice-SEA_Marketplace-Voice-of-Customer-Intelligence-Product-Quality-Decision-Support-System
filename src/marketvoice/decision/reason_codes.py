"""Explainable Reason Code Generation Engine.

Phase 10 Decision Support System.
Generates deterministic, standardized reason codes explaining the exact
drivers of a priority score.

Data governance:
    - Fully explainable and auditable.
    - Each reason code is bound to a measurable analytical threshold.
    - No black-box or non-deterministic natural language generation.
"""
from __future__ import annotations

from typing import Dict, List, Optional


# Standardized reason code registry
REASON_CODES = {
    "RC_CRITICAL_SEVERITY_DOMINANCE": {
        "title": "Critical Severity Dominance",
        "description": "Over 50% of issue assignments are in the Critical/High rating proxy tier (rating <= 2).",
        "dimension": "Severity Impact",
    },
    "RC_HIGH_DISSATISFACTION_DRIVER": {
        "title": "High Dissatisfaction Driver",
        "description": "Issue is over-represented in dissatisfied reviews by >= 2.0x relative to corpus baseline.",
        "dimension": "Dissatisfaction Overrepresentation",
    },
    "RC_CHRONIC_EVENT_RECURRENCE": {
        "title": "Chronic Review-Event Recurrence",
        "description": "5 or more distinct review events independently report this issue for the entity.",
        "dimension": "Recurrence Intensity",
    },
    "RC_BROAD_EVIDENCE_SUPPORT": {
        "title": "Broad Evidence Support",
        "description": "Total issue volume exceeds 50 distinct reviews, confirming widespread impact.",
        "dimension": "Evidence Volume",
    },
    "RC_HIGH_CONFIDENCE_SIGNAL": {
        "title": "High Classification Confidence",
        "description": "Mean NLP/keyword classification confidence is >= 0.70.",
        "dimension": "Classification Quality",
    },
    "RC_SMALL_SAMPLE_CAUTION": {
        "title": "Small Sample Caution Flag",
        "description": "Issue support is below 5 reviews; priority score has higher uncertainty.",
        "dimension": "Sample Caution",
    },
}


def generate_reason_codes(
    severity_ratio: float,
    dissatisfaction_ratio: float,
    recurrence_count: int,
    volume: int,
    confidence: float,
    z_score: Optional[float] = None,
) -> List[str]:
    """Generate standardized reason codes for a scored entity.

    Parameters
    ----------
    severity_ratio : float
        Proportion of Critical + High severity facts in [0, 1].
    dissatisfaction_ratio : float
        Low-rating dissatisfaction rate ratio (>= 0.0).
    recurrence_count : int
        Distinct review event count (>= 0).
    volume : int
        Total issue fact volume (>= 0).
    confidence : float
        Mean classification confidence in [0, 1].
    z_score : float, optional
        Two-proportion z-score from overrepresentation analysis.

    Returns
    -------
    list of str
        List of triggered reason code identifiers.
    """
    codes = []

    # 1. Severity Trigger
    if severity_ratio >= 0.50:
        codes.append("RC_CRITICAL_SEVERITY_DOMINANCE")

    # 2. Dissatisfaction Trigger
    if dissatisfaction_ratio >= 2.0 or (z_score is not None and z_score >= 2.0):
        codes.append("RC_HIGH_DISSATISFACTION_DRIVER")

    # 3. Recurrence Trigger
    if recurrence_count >= 5:
        codes.append("RC_CHRONIC_EVENT_RECURRENCE")

    # 4. Volume Support Trigger
    if volume >= 50:
        codes.append("RC_BROAD_EVIDENCE_SUPPORT")

    # 5. Confidence Trigger
    if confidence >= 0.70:
        codes.append("RC_HIGH_CONFIDENCE_SIGNAL")

    # 6. Small Sample Caution
    if volume < 5:
        codes.append("RC_SMALL_SAMPLE_CAUTION")

    # Fallback if no specific trigger fired but score exists
    if not codes:
        codes.append("RC_BASELINE_MONITORING")

    return codes


def format_decision_explanation(
    entity_name: str,
    issue_name: str,
    priority_band: str,
    priority_score: float,
    reason_codes: List[str],
) -> str:
    """Format a human-readable explanation card for decision support.

    Parameters
    ----------
    entity_name : str
        Product name or Category name.
    issue_name : str
        Issue category name.
    priority_band : str
        P1, P2, P3, or P4.
    priority_score : float
        Composite score (0-100).
    reason_codes : list of str
        Triggered reason code identifiers.

    Returns
    -------
    str
        Formatted explanation text.
    """
    lines = [
        f"DECISION CASE: {entity_name} | {issue_name}",
        f"PRIORITY: {priority_band} (Score: {priority_score:.1f} / 100)",
        "REASONS:",
    ]
    for code in reason_codes:
        meta = REASON_CODES.get(code, {"title": code, "description": "Standard monitoring signal."})
        lines.append(f"  * [{code}] {meta['title']}: {meta['description']}")
    return "\n".join(lines)
