"""Emerging issue detection via rating-segment analysis.

CRITICAL DATA LIMITATION:
    No review timestamps exist in the dataset.
    Traditional time-based trend detection is NOT possible.

    Instead, "emerging" is defined as issues that are STATISTICALLY
    OVER-REPRESENTED in low-rating reviews compared to the overall
    corpus baseline. This identifies issues that disproportionately
    drive negative customer experience.

Methodology:
    For each issue category:
    1. Compute issue rate in low-rating segment (rating <= 2)
    2. Compute issue rate in overall corpus
    3. Compute rate ratio and z-score of the difference
    4. Flag as EMERGING_SIGNAL if z > 2.0 AND support >= 30

Data governance:
    - READ-ONLY against classified and fact data.
    - No temporal ordering inferred or fabricated.
"""
from __future__ import annotations

import math
from typing import Dict, List

import pandas as pd

MIN_EMERGING_SUPPORT = 30   # minimum reviews to flag emerging
Z_THRESHOLD = 2.0           # z-score threshold for emerging flag


def _proportion_z_test(p1: float, n1: int, p2: float, n2: int) -> float:
    """Two-proportion z-test statistic.

    Tests whether p1 (segment rate) is significantly different from p2 (baseline rate).

    Parameters
    ----------
    p1 : float
        Proportion in segment (low-rating).
    n1 : int
        Sample size of segment.
    p2 : float
        Proportion in baseline (full corpus).
    n2 : int
        Sample size of baseline.

    Returns
    -------
    float
        z-score. Positive = over-represented in segment.
    """
    if n1 == 0 or n2 == 0:
        return 0.0

    p_pool = (p1 * n1 + p2 * n2) / (n1 + n2)
    if p_pool <= 0 or p_pool >= 1.0:
        return 0.0

    se = math.sqrt(p_pool * (1 - p_pool) * (1.0 / n1 + 1.0 / n2))
    if se == 0:
        return 0.0

    return (p1 - p2) / se


def detect_emerging_issues(
    classified_df: pd.DataFrame,
    fact_df: pd.DataFrame,
    source_id: str,
    review_sk_col: str = "review_sk",
    rating_col: str = "rating_value",
    min_support: int = MIN_EMERGING_SUPPORT,
    z_threshold: float = Z_THRESHOLD,
) -> pd.DataFrame:
    """Detect issues over-represented in low-rating reviews.

    Parameters
    ----------
    classified_df : pd.DataFrame
        Output of classify_reviews() for one source.
    fact_df : pd.DataFrame
        Full fact_review for the same source.
    source_id : str
        Source identifier.
    min_support : int
        Minimum issue occurrences in low-rating segment to flag.
    z_threshold : float
        Minimum z-score to declare emerging signal.

    Returns
    -------
    pd.DataFrame
        One row per issue with emerging signal analysis.
    """
    total_reviews = len(fact_df)
    total_neg = int((fact_df[rating_col] <= 2).sum())
    total_pos = total_reviews - total_neg

    if classified_df.empty or total_reviews == 0:
        return pd.DataFrame()

    rows = []
    for iid, grp in classified_df.groupby("issue_id"):
        name = grp["issue_name"].iloc[0]

        # Issue occurrences in low-rating segment
        neg_grp = grp[grp[rating_col] <= 2]
        neg_vol = neg_grp[review_sk_col].nunique()

        # Issue occurrences in full corpus
        full_vol = grp[review_sk_col].nunique()

        # Issue rate in low-rating segment vs overall
        neg_rate = neg_vol / total_neg if total_neg > 0 else 0
        full_rate = full_vol / total_reviews if total_reviews > 0 else 0

        # Rate ratio
        rate_ratio = neg_rate / full_rate if full_rate > 0 else 0

        # Z-score for proportion difference
        z_score = _proportion_z_test(neg_rate, total_neg, full_rate, total_reviews)

        # Emerging flag
        is_emerging = (
            z_score > z_threshold
            and neg_vol >= min_support
        )

        rows.append({
            "source_id": source_id,
            "issue_id": int(iid),
            "issue_name": name,
            "segment": "rating_le_2",
            "segment_issue_count": neg_vol,
            "segment_total": total_neg,
            "segment_rate": round(neg_rate, 6),
            "baseline_issue_count": full_vol,
            "baseline_total": total_reviews,
            "baseline_rate": round(full_rate, 6),
            "rate_ratio": round(rate_ratio, 4),
            "z_score": round(z_score, 4),
            "min_support_met": neg_vol >= min_support,
            "z_threshold_met": z_score > z_threshold,
            "emerging_signal": is_emerging,
            "status": "EMERGING_SIGNAL" if is_emerging else "BASELINE",
            "data_limitation": "NO_TEMPORAL_DATA — segment-based proxy only",
        })

    return pd.DataFrame(rows).sort_values("z_score", ascending=False).reset_index(drop=True)
