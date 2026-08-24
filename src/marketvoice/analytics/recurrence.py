"""Recurrence analysis — identifying recurring issues across distinct reviews.

Recurrence definition:
    Same issue category appearing in reviews from >= 3 DISTINCT customers
    (distinct review_sk with distinct review_text) for the same
    product or category.

    This is NOT duplicate text detection. Different customers independently
    reporting the same issue type is a stronger operational signal.

Data governance:
    - READ-ONLY against classified and fact data.
    - Source isolation preserved.
    - Product-level recurrence for Source B only (Source A has no product_sk).
"""
from __future__ import annotations

from typing import Dict, List

import pandas as pd

MIN_RECURRENCE_THRESHOLD = 3   # minimum distinct reviews for recurrence flag


def compute_category_recurrence(
    classified_df: pd.DataFrame,
    category_col: str = "category_sk",
    review_sk_col: str = "review_sk",
    min_threshold: int = MIN_RECURRENCE_THRESHOLD,
) -> pd.DataFrame:
    """Compute issue recurrence at category level.

    Recurrence = same issue category reported by >= min_threshold distinct
    reviews within the same category.

    Parameters
    ----------
    classified_df : pd.DataFrame
        Classified reviews with category_sk.
    category_col : str
        Column for category grouping.
    min_threshold : int
        Minimum distinct review_sk to flag as recurring.

    Returns
    -------
    pd.DataFrame
        One row per (category, issue) pair with recurrence metrics.
    """
    if classified_df.empty or category_col not in classified_df.columns:
        return pd.DataFrame()

    rows = []
    for (cat_sk, iid), grp in classified_df.groupby([category_col, "issue_id"]):
        distinct_reviews = grp[review_sk_col].nunique()
        name = grp["issue_name"].iloc[0]

        rows.append({
            "category_sk": int(cat_sk),
            "issue_id": int(iid),
            "issue_name": name,
            "distinct_review_count": distinct_reviews,
            "is_recurring": distinct_reviews >= min_threshold,
            "recurrence_level": _recurrence_level(distinct_reviews, min_threshold),
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("distinct_review_count", ascending=False).reset_index(drop=True)
    return df


def compute_product_recurrence(
    classified_df: pd.DataFrame,
    product_col: str = "product_sk",
    review_sk_col: str = "review_sk",
    min_threshold: int = MIN_RECURRENCE_THRESHOLD,
) -> pd.DataFrame:
    """Compute issue recurrence at product level (Source B only).

    Parameters
    ----------
    classified_df : pd.DataFrame
        Classified reviews with product_sk.
    product_col : str
        Column for product grouping.
    min_threshold : int
        Minimum distinct review_sk to flag as recurring.

    Returns
    -------
    pd.DataFrame
        One row per (product, issue) pair with recurrence metrics.
    """
    if classified_df.empty or product_col not in classified_df.columns:
        return pd.DataFrame()

    # Filter to valid product_sk
    valid = classified_df[classified_df[product_col].notna() & (classified_df[product_col] != 0)]
    if valid.empty:
        return pd.DataFrame()

    rows = []
    for (psk, iid), grp in valid.groupby([product_col, "issue_id"]):
        distinct_reviews = grp[review_sk_col].nunique()
        name = grp["issue_name"].iloc[0]

        rows.append({
            "product_sk": int(psk),
            "issue_id": int(iid),
            "issue_name": name,
            "distinct_review_count": distinct_reviews,
            "is_recurring": distinct_reviews >= min_threshold,
            "recurrence_level": _recurrence_level(distinct_reviews, min_threshold),
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("distinct_review_count", ascending=False).reset_index(drop=True)
    return df


def _recurrence_level(count: int, threshold: int) -> str:
    """Assign a recurrence severity level.

    LOW      = threshold <= count < 2*threshold
    MODERATE = 2*threshold <= count < 5*threshold
    HIGH     = count >= 5*threshold
    NONE     = count < threshold
    """
    if count < threshold:
        return "NONE"
    elif count < 2 * threshold:
        return "LOW"
    elif count < 5 * threshold:
        return "MODERATE"
    else:
        return "HIGH"
