"""Multi-label keyword-based issue classification with severity assignment.

Phase 9 scope:
    - Classify every review against the frozen issue taxonomy.
    - Assign severity based on rating + issue presence.
    - Produce traceability metadata (review_sk → issue → confidence → model version).

Data governance:
    - READ-ONLY against fact_review (no warehouse mutation).
    - Output is ADDITIVE into Phase 9 tables only.
    - Source isolation preserved.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import pandas as pd

from marketvoice.analytics.taxonomy import CANDIDATE_TAXONOMY, TAXONOMY_VERSION


# ────────────────────────────────────────────────────────────────
# Severity definitions (rule-based, rating proxy)
# ────────────────────────────────────────────────────────────────
SEVERITY_LEVELS = {
    1: {"severity_id": 1, "severity_name": "CRITICAL",
        "definition": "Rating 1 + issue detected. Strongest negative signal."},
    2: {"severity_id": 2, "severity_name": "HIGH",
        "definition": "Rating 2 + issue detected. Significant dissatisfaction."},
    3: {"severity_id": 3, "severity_name": "MODERATE",
        "definition": "Rating 3 + issue detected. Mixed experience."},
    4: {"severity_id": 4, "severity_name": "LOW",
        "definition": "Rating 4-5 + issue detected. Positive review mentioning issue."},
}

SEVERITY_STATUS = "ANALYTICAL_PROTOTYPE"


def _match_keywords(text: str, keywords: List[str]) -> List[str]:
    """Return which keywords are found in the text.

    Parameters
    ----------
    text : str
        Lowercased, whitespace-normalised review text.
    keywords : list of str
        Evidence keywords to search for.

    Returns
    -------
    list of str
        Matched keywords found in text.
    """
    if not text:
        return []
    matched = []
    text_lower = text.lower()
    for kw in keywords:
        if kw in text_lower:
            matched.append(kw)
    return matched


def _compute_confidence(matched_count: int, total_keywords: int) -> float:
    """Compute a simple confidence score based on keyword density.

    Confidence = min(1.0, matched_count / 3)
    Rationale: 3+ keyword matches in one review is strong evidence.

    Returns
    -------
    float
        Confidence score between 0.0 and 1.0.
    """
    if total_keywords == 0:
        return 0.0
    return min(1.0, matched_count / 3.0)


def _rating_to_severity_id(rating: int) -> int:
    """Map star rating to severity level.

    1 → CRITICAL (1)
    2 → HIGH (2)
    3 → MODERATE (3)
    4, 5 → LOW (4)
    """
    if rating <= 1:
        return 1
    elif rating == 2:
        return 2
    elif rating == 3:
        return 3
    else:
        return 4


def classify_reviews(
    df: pd.DataFrame,
    taxonomy: List[Dict] = CANDIDATE_TAXONOMY,
    text_col: str = "review_text",
    rating_col: str = "rating_value",
    review_sk_col: str = "review_sk",
    source_sk_col: str = "source_sk",
) -> pd.DataFrame:
    """Classify all reviews against the frozen issue taxonomy.

    Multi-label: a review may match multiple issue categories.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain review_sk, source_sk, review_text, rating_value.
    taxonomy : list of dict
        Frozen taxonomy with evidence_keywords.
    text_col : str
        Column containing review text.
    rating_col : str
        Column containing star rating (1-5).

    Returns
    -------
    pd.DataFrame
        Columns: review_sk, source_sk, issue_id, issue_name, severity_id,
                 matched_keywords, keyword_count, confidence, model_version,
                 classification_method.
        One row per (review, issue) pair. Reviews with no issue match are excluded.
    """
    active_cats = [c for c in taxonomy if c.get("status", "ACTIVE") != "REJECTED_INSUFFICIENT_EVIDENCE"]

    records = []
    for _, row in df.iterrows():
        text = str(row.get(text_col, "")).lower()
        rating = int(row.get(rating_col, 3))
        rsk = row[review_sk_col]
        ssk = row.get(source_sk_col, 1 if row.get("source_id") == "SRC_PRDECT_ID_V1" else 2)

        for cat in active_cats:
            matched = _match_keywords(text, cat["evidence_keywords"])
            if matched:
                records.append({
                    "review_sk": rsk,
                    "source_sk": ssk,
                    "issue_id": cat["issue_id"],
                    "issue_name": cat["issue_name"],
                    "severity_id": _rating_to_severity_id(rating),
                    "rating_value": rating,
                    "matched_keywords": "|".join(matched),
                    "keyword_count": len(matched),
                    "confidence": round(_compute_confidence(len(matched), len(cat["evidence_keywords"])), 4),
                    "model_version": f"keyword_v{TAXONOMY_VERSION}",
                    "classification_method": "keyword_match",
                    "taxonomy_version": TAXONOMY_VERSION,
                })

    if not records:
        return pd.DataFrame(columns=[
            "review_sk", "source_sk", "issue_id", "issue_name",
            "severity_id", "rating_value", "matched_keywords",
            "keyword_count", "confidence", "model_version",
            "classification_method", "taxonomy_version",
        ])

    return pd.DataFrame(records)


def classification_summary(
    classified_df: pd.DataFrame,
    total_reviews: int,
    total_negative_reviews: int,
) -> Dict:
    """Produce classification summary statistics.

    Parameters
    ----------
    classified_df : pd.DataFrame
        Output of classify_reviews().
    total_reviews : int
        Total reviews in the corpus.
    total_negative_reviews : int
        Reviews with rating <= 2.

    Returns
    -------
    dict
        Summary statistics.
    """
    if classified_df.empty:
        return {
            "total_issue_assignments": 0,
            "distinct_reviews_with_issues": 0,
            "issue_coverage_pct": 0,
            "per_issue": {},
        }

    distinct_reviews = classified_df["review_sk"].nunique()
    per_issue = {}
    for iid, grp in classified_df.groupby("issue_id"):
        name = grp["issue_name"].iloc[0]
        support = grp["review_sk"].nunique()
        neg_support = grp[grp["rating_value"] <= 2]["review_sk"].nunique()
        per_issue[int(iid)] = {
            "issue_name": name,
            "total_assigned": support,
            "issue_rate": round(100.0 * support / total_reviews, 2),
            "negative_assigned": neg_support,
            "negative_issue_rate": round(100.0 * neg_support / total_negative_reviews, 2) if total_negative_reviews > 0 else 0,
            "severity_distribution": grp.groupby("severity_id").size().to_dict(),
            "mean_confidence": round(grp["confidence"].mean(), 4),
        }

    return {
        "total_issue_assignments": len(classified_df),
        "distinct_reviews_with_issues": distinct_reviews,
        "issue_coverage_pct": round(100.0 * distinct_reviews / total_reviews, 2),
        "negative_coverage_pct": round(
            100.0 * classified_df[classified_df["rating_value"] <= 2]["review_sk"].nunique()
            / total_negative_reviews, 2
        ) if total_negative_reviews > 0 else 0,
        "per_issue": per_issue,
    }
