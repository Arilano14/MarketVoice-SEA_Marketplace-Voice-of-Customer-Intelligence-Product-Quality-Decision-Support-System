"""Tiered Decision Action Queue Generator across Isolated Grains.

Phase 10 Decision Support System.
Generates priority decision cases across 3 explicitly separated grains:
    Grain A: Product x Issue (Source B only, N=4,913)
    Grain B: Category x Issue (Source A & B, N=167, source-aware)
    Grain C: Source x Issue (Global portfolio, N=10)

Priority Tiers (Analytical Guidance):
    P1: Immediate Review Recommendation (Score >= 70.0)
    P2: Near-Term Review Recommendation (50.0 <= Score < 70.0)
    P3: Monitoring Recommendation (30.0 <= Score < 50.0)
    P4: Informational (Score < 30.0)
"""
from __future__ import annotations

from typing import Dict, List, Optional
import pandas as pd
import numpy as np

from marketvoice.decision.priority_score import (
    CALCULATION_VERSION,
    DEFAULT_WEIGHTS,
    compute_priority_score,
)
from marketvoice.decision.reason_codes import generate_reason_codes

PRIORITY_TIERS = {
    1: {
        "tier_code": "P1_CRITICAL",
        "tier_name": "Immediate Human Review Recommendation",
        "score_min": 70.0,
        "score_max": 100.0,
        "guidance": "High-severity, chronic customer defect; prioritize for root-cause analysis.",
    },
    2: {
        "tier_code": "P2_HIGH_PRIORITY",
        "tier_name": "Near-Term Review Recommendation",
        "score_min": 50.0,
        "score_max": 69.99,
        "guidance": "Substantial dissatisfaction or recurring issue; investigate quality drivers.",
    },
    3: {
        "tier_code": "P3_MONITORING",
        "tier_name": "Quality Monitoring Recommendation",
        "score_min": 30.0,
        "score_max": 49.99,
        "guidance": "Moderate risk; monitor for recurrence or low-rating escalation.",
    },
    4: {
        "tier_code": "P4_INFORMATIONAL",
        "tier_name": "Informational",
        "score_min": 0.0,
        "score_max": 29.99,
        "guidance": "Low severity or baseline incidental feedback; standard automated logging.",
    },
}


def score_to_tier(score: float) -> Tuple[int, str]:
    """Map a Priority Risk Score to tier ID and code."""
    if score >= 70.0:
        return 1, "P1_CRITICAL"
    elif score >= 50.0:
        return 2, "P2_HIGH_PRIORITY"
    elif score >= 30.0:
        return 3, "P3_MONITORING"
    else:
        return 4, "P4_INFORMATIONAL"


def generate_decision_queue_product(
    classified_b: pd.DataFrame,
    fact_b: pd.DataFrame,
    overrep_b: pd.DataFrame,
    weights: Optional[Dict[str, float]] = None,
) -> pd.DataFrame:
    """Generate Grain A Decision Queue: Product x Issue (Source B only).

    Parameters
    ----------
    classified_b : pd.DataFrame
        Classified reviews for Source B.
    fact_b : pd.DataFrame
        Fact reviews for Source B.
    overrep_b : pd.DataFrame
        Dissatisfaction driver analysis for Source B.
    weights : dict, optional
        Custom scoring weights.

    Returns
    -------
    pd.DataFrame
        Decision queue DataFrame for Product x Issue grain.
    """
    if classified_b.empty:
        return pd.DataFrame()

    # Map overrepresentation ratio per issue
    dissat_ratios = {}
    z_scores = {}
    for _, r in overrep_b.iterrows():
        dissat_ratios[r["issue_id"]] = r["dissatisfaction_rate_ratio"]
        z_scores[r["issue_id"]] = r["overrepresentation_z_score"]

    records = []
    # Group by (product_sk, issue_id)
    grouped = classified_b[classified_b["product_sk"].notnull() & (classified_b["product_sk"] != 0)].groupby(
        ["product_sk", "issue_id"]
    )

    for (prod_sk, iid), grp in grouped:
        vol = len(grp)
        distinct_reviews = grp["review_sk"].nunique()
        issue_name = grp["issue_name"].iloc[0]
        source_sk = int(grp["source_sk"].iloc[0])

        # Severity ratio: proportion of rating <= 2 (severity_id 1 or 2)
        crit_count = int((grp["severity_id"] <= 2).sum())
        sev_ratio = crit_count / vol if vol > 0 else 0.0

        # Mean classification confidence
        mean_conf = float(grp["confidence"].mean()) if "confidence" in grp.columns else 0.50

        # Dissatisfaction ratio from category/source level
        d_ratio = dissat_ratios.get(iid, 1.0)
        z_val = z_scores.get(iid, 0.0)

        # Compute priority score
        scores = compute_priority_score(
            severity_ratio=sev_ratio,
            dissatisfaction_ratio=d_ratio,
            recurrence_count=distinct_reviews,
            volume=vol,
            confidence=mean_conf,
            weights=weights,
        )

        prs = scores["priority_score"]
        tier_id, tier_code = score_to_tier(prs)

        # Generate reason codes
        rcs = generate_reason_codes(
            severity_ratio=sev_ratio,
            dissatisfaction_ratio=d_ratio,
            recurrence_count=distinct_reviews,
            volume=vol,
            confidence=mean_conf,
            z_score=z_val,
        )

        records.append({
            "source_sk": source_sk,
            "grain_type": "PRODUCT_X_ISSUE",
            "product_sk": int(prod_sk),
            "category_sk": int(grp["category_sk"].iloc[0]) if "category_sk" in grp.columns and pd.notnull(grp["category_sk"].iloc[0]) else None,
            "issue_id": int(iid),
            "issue_name": issue_name,
            "priority_score": prs,
            "tier_id": tier_id,
            "tier_code": tier_code,
            "severity_impact_score": scores["severity_impact_score"],
            "dissatisfaction_score": scores["dissatisfaction_score"],
            "recurrence_score": scores["recurrence_score"],
            "volume_score": scores["volume_score"],
            "confidence_score": scores["confidence_score"],
            "evidence_support": vol,
            "distinct_review_events": distinct_reviews,
            "critical_severity_count": crit_count,
            "reason_codes": rcs,
            "calculation_version": CALCULATION_VERSION,
        })

    df_out = pd.DataFrame(records)
    if not df_out.empty:
        df_out = df_out.sort_values("priority_score", ascending=False).reset_index(drop=True)
    return df_out


def generate_decision_queue_category(
    classified_a: pd.DataFrame,
    classified_b: pd.DataFrame,
    overrep_a: pd.DataFrame,
    overrep_b: pd.DataFrame,
    weights: Optional[Dict[str, float]] = None,
) -> pd.DataFrame:
    """Generate Grain B Decision Queue: Source x Category x Issue (Source A & B).

    Parameters
    ----------
    classified_a : pd.DataFrame
        Classified reviews for Source A.
    classified_b : pd.DataFrame
        Classified reviews for Source B.
    overrep_a : pd.DataFrame
        Dissatisfaction driver analysis for Source A.
    overrep_b : pd.DataFrame
        Dissatisfaction driver analysis for Source B.

    Returns
    -------
    pd.DataFrame
        Decision queue DataFrame for Category x Issue grain.
    """
    classified_all = pd.concat([classified_a, classified_b], ignore_index=True)
    if classified_all.empty:
        return pd.DataFrame()

    overrep_map = {}
    for _, r in pd.concat([overrep_a, overrep_b], ignore_index=True).iterrows():
        overrep_map[(r["source_id"], r["issue_id"])] = (r["dissatisfaction_rate_ratio"], r["overrepresentation_z_score"])

    records = []
    grouped = classified_all[classified_all["category_sk"].notnull()].groupby(
        ["source_sk", "category_sk", "issue_id"]
    )

    for (ssk, csk, iid), grp in grouped:
        vol = len(grp)
        distinct_reviews = grp["review_sk"].nunique()
        issue_name = grp["issue_name"].iloc[0]
        crit_count = int((grp["severity_id"] <= 2).sum())
        sev_ratio = crit_count / vol if vol > 0 else 0.0
        mean_conf = float(grp["confidence"].mean()) if "confidence" in grp.columns else 0.50

        src_id = "SRC_PRDECT_ID_V1" if ssk == 1 else "SRC_TOKOPEDIA_REVIEWS_2019"
        d_ratio, z_val = overrep_map.get((src_id, iid), (1.0, 0.0))

        scores = compute_priority_score(
            severity_ratio=sev_ratio,
            dissatisfaction_ratio=d_ratio,
            recurrence_count=distinct_reviews,
            volume=vol,
            confidence=mean_conf,
            weights=weights,
        )
        prs = scores["priority_score"]
        tier_id, tier_code = score_to_tier(prs)
        rcs = generate_reason_codes(
            severity_ratio=sev_ratio,
            dissatisfaction_ratio=d_ratio,
            recurrence_count=distinct_reviews,
            volume=vol,
            confidence=mean_conf,
            z_score=z_val,
        )

        records.append({
            "source_sk": int(ssk),
            "grain_type": "CATEGORY_X_ISSUE",
            "product_sk": None,
            "category_sk": int(csk),
            "issue_id": int(iid),
            "issue_name": issue_name,
            "priority_score": prs,
            "tier_id": tier_id,
            "tier_code": tier_code,
            "severity_impact_score": scores["severity_impact_score"],
            "dissatisfaction_score": scores["dissatisfaction_score"],
            "recurrence_score": scores["recurrence_score"],
            "volume_score": scores["volume_score"],
            "confidence_score": scores["confidence_score"],
            "evidence_support": vol,
            "distinct_review_events": distinct_reviews,
            "critical_severity_count": crit_count,
            "reason_codes": rcs,
            "calculation_version": CALCULATION_VERSION,
        })

    df_out = pd.DataFrame(records)
    if not df_out.empty:
        df_out = df_out.sort_values("priority_score", ascending=False).reset_index(drop=True)
    return df_out


def generate_decision_queue_source(
    classified_a: pd.DataFrame,
    classified_b: pd.DataFrame,
    overrep_a: pd.DataFrame,
    overrep_b: pd.DataFrame,
    weights: Optional[Dict[str, float]] = None,
) -> pd.DataFrame:
    """Generate Grain C Decision Queue: Source x Issue (Global portfolio, N=10).

    Returns
    -------
    pd.DataFrame
        Decision queue DataFrame for Source x Issue grain.
    """
    classified_all = pd.concat([classified_a, classified_b], ignore_index=True)
    if classified_all.empty:
        return pd.DataFrame()

    overrep_map = {}
    for _, r in pd.concat([overrep_a, overrep_b], ignore_index=True).iterrows():
        overrep_map[(r["source_id"], r["issue_id"])] = (r["dissatisfaction_rate_ratio"], r["overrepresentation_z_score"])

    records = []
    grouped = classified_all.groupby(["source_sk", "issue_id"])

    for (ssk, iid), grp in grouped:
        vol = len(grp)
        distinct_reviews = grp["review_sk"].nunique()
        issue_name = grp["issue_name"].iloc[0]
        crit_count = int((grp["severity_id"] <= 2).sum())
        sev_ratio = crit_count / vol if vol > 0 else 0.0
        mean_conf = float(grp["confidence"].mean()) if "confidence" in grp.columns else 0.50

        src_id = "SRC_PRDECT_ID_V1" if ssk == 1 else "SRC_TOKOPEDIA_REVIEWS_2019"
        d_ratio, z_val = overrep_map.get((src_id, iid), (1.0, 0.0))

        scores = compute_priority_score(
            severity_ratio=sev_ratio,
            dissatisfaction_ratio=d_ratio,
            recurrence_count=distinct_reviews,
            volume=vol,
            confidence=mean_conf,
            weights=weights,
        )
        prs = scores["priority_score"]
        tier_id, tier_code = score_to_tier(prs)
        rcs = generate_reason_codes(
            severity_ratio=sev_ratio,
            dissatisfaction_ratio=d_ratio,
            recurrence_count=distinct_reviews,
            volume=vol,
            confidence=mean_conf,
            z_score=z_val,
        )

        records.append({
            "source_sk": int(ssk),
            "grain_type": "SOURCE_X_ISSUE",
            "product_sk": None,
            "category_sk": None,
            "issue_id": int(iid),
            "issue_name": issue_name,
            "priority_score": prs,
            "tier_id": tier_id,
            "tier_code": tier_code,
            "severity_impact_score": scores["severity_impact_score"],
            "dissatisfaction_score": scores["dissatisfaction_score"],
            "recurrence_score": scores["recurrence_score"],
            "volume_score": scores["volume_score"],
            "confidence_score": scores["confidence_score"],
            "evidence_support": vol,
            "distinct_review_events": distinct_reviews,
            "critical_severity_count": crit_count,
            "reason_codes": rcs,
            "calculation_version": CALCULATION_VERSION,
        })

    df_out = pd.DataFrame(records)
    if not df_out.empty:
        df_out = df_out.sort_values("priority_score", ascending=False).reset_index(drop=True)
    return df_out
