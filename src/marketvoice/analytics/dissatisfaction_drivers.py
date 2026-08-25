"""Customer Dissatisfaction Driver / Low-Rating Issue Overrepresentation Analysis.

FORMAL NOMENCLATURE & METHODOLOGICAL CLARIFICATION:
    No review timestamps exist in the dataset (NO_TEMPORAL_DATA).
    Therefore, time-series "emerging issue detection" is DEFERRED
    to future dataset releases.

    This module performs statistical OVERREPRESENTATION ANALYSIS:
    identifying issue categories that are disproportionately prevalent
    in dissatisfied reviews (rating <= 2) relative to the overall
    marketplace corpus baseline.

Methodology:
    For each issue category:
    1. Compute issue rate in low-rating segment (rating <= 2).
    2. Compute issue rate across the overall corpus baseline.
    3. Calculate the dissatisfaction rate ratio (segment_rate / baseline_rate).
    4. Compute a two-proportion z-test statistic comparing the two rates.
    5. Flag as DISSATISFACTION_DRIVER if:
       - dissatisfaction_rate_ratio > 1.25
       - z_score > 2.0 (p < 0.05)
       - minimum negative support >= 30 reviews

Data governance:
    - READ-ONLY against classified and fact data.
    - Zero temporal ordering inferred or simulated.
    - Source isolation strictly preserved.
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional

import pandas as pd

MIN_DISSATISFACTION_SUPPORT = 30   # minimum negative reviews to flag driver
Z_THRESHOLD = 2.0                  # two-proportion z-test critical value (alpha=0.05)
RATE_RATIO_THRESHOLD = 1.25        # minimum 25% overrepresentation in low ratings


def proportion_z_test(p1: float, n1: int, p2: float, n2: int) -> float:
    """Compute two-proportion z-test statistic.

    Tests H0: p1 == p2 vs H1: p1 > p2
    where p1 is segment rate (low rating) and p2 is baseline rate (full corpus).

    Parameters
    ----------
    p1 : float
        Proportion in low-rating segment.
    n1 : int
        Sample size of low-rating segment.
    p2 : float
        Proportion in baseline corpus.
    n2 : int
        Sample size of baseline corpus.

    Returns
    -------
    float
        z-score statistic. Positive indicates overrepresentation in low ratings.
    """
    if n1 == 0 or n2 == 0:
        return 0.0

    p_pool = (p1 * n1 + p2 * n2) / (n1 + n2)
    if p_pool <= 0.0 or p_pool >= 1.0:
        return 0.0

    se = math.sqrt(p_pool * (1.0 - p_pool) * (1.0 / n1 + 1.0 / n2))
    if se == 0.0:
        return 0.0

    return (p1 - p2) / se


def analyze_dissatisfaction_drivers(
    classified_df: pd.DataFrame,
    fact_df: pd.DataFrame,
    source_id: str,
    review_sk_col: str = "review_sk",
    rating_col: str = "rating_value",
    min_support: int = MIN_DISSATISFACTION_SUPPORT,
    z_threshold: float = Z_THRESHOLD,
    rate_ratio_threshold: float = RATE_RATIO_THRESHOLD,
) -> pd.DataFrame:
    """Identify issues over-represented in low-rating reviews.

    Parameters
    ----------
    classified_df : pd.DataFrame
        Output of classify_reviews() for one source.
    fact_df : pd.DataFrame
        Full fact_review for the same source.
    source_id : str
        Source identifier string.
    min_support : int
        Minimum issue occurrences in rating <= 2 segment.
    z_threshold : float
        Minimum z-score for statistical significance.
    rate_ratio_threshold : float
        Minimum rate ratio for practical significance.

    Returns
    -------
    pd.DataFrame
        One row per issue category with overrepresentation statistics.
    """
    total_reviews = len(fact_df)
    total_neg = int((fact_df[rating_col] <= 2).sum())

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

        # Issue rate in low-rating segment vs baseline
        neg_rate = neg_vol / total_neg if total_neg > 0 else 0.0
        full_rate = full_vol / total_reviews if total_reviews > 0 else 0.0

        # Dissatisfaction Rate Ratio
        rate_ratio = neg_rate / full_rate if full_rate > 0 else 0.0

        # Two-proportion z-score
        z_score = proportion_z_test(neg_rate, total_neg, full_rate, total_reviews)

        # Dissatisfaction driver flag
        is_driver = (
            z_score > z_threshold
            and rate_ratio >= rate_ratio_threshold
            and neg_vol >= min_support
        )

        rows.append({
            "source_id": source_id,
            "issue_id": int(iid),
            "issue_name": name,
            "segment": "rating_le_2",
            "low_rating_issue_count": neg_vol,
            "low_rating_total_reviews": total_neg,
            "low_rating_issue_rate": round(neg_rate, 6),
            "baseline_issue_count": full_vol,
            "dissatisfaction_rate_ratio": round(rate_ratio, 4),
            "overrepresentation_z_score": round(z_score, 4),
            # Backwards-compatibility aliases
            "rate_ratio": round(rate_ratio, 4),
            "z_score": round(z_score, 4),
            "min_support_met": neg_vol >= min_support,
            "statistical_significance_met": z_score > z_threshold,
            "is_dissatisfaction_driver": is_driver,
            "emerging_signal": is_driver,
            "status": "DISSATISFACTION_DRIVER" if is_driver else "BASELINE_DISTRIBUTION",
            "analysis_type": "LOW_RATING_OVERREPRESENTATION",
            "temporal_limitation_note": "TEMPORAL_EMERGING_ISSUE_ANALYSIS = DEFERRED (no timestamps)",
        })

    return pd.DataFrame(rows).sort_values("overrepresentation_z_score", ascending=False).reset_index(drop=True)
