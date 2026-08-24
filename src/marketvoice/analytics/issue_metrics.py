"""Issue rate, frequency, and severity distribution computations.

Phase 9 scope: compute business-ready issue metrics that answer:
    - How frequently does each issue occur?
    - What is the negative issue rate?
    - What is the severity distribution?

Data governance:
    - Metrics are computed from classified review data only.
    - Denominators and filters are explicitly documented.
"""
from __future__ import annotations

from typing import Dict, List, Optional

import pandas as pd


def compute_issue_summary(
    classified_df: pd.DataFrame,
    fact_df: pd.DataFrame,
    source_id: str,
    review_sk_col: str = "review_sk",
    rating_col: str = "rating_value",
) -> pd.DataFrame:
    """Compute per-issue summary metrics for a single source.

    Metrics:
        issue_volume        COUNT(DISTINCT review_sk WHERE issue_id = X)
        issue_rate          issue_volume / total_valid_reviews
        negative_volume     COUNT(DISTINCT review_sk WHERE issue_id = X AND rating <= 2)
        negative_issue_rate negative_volume / total_valid_reviews
        critical_volume     COUNT(WHERE severity_id = 1)
        critical_rate       critical_volume / total_valid_reviews
        mean_confidence     AVG(confidence)
        severity_distribution   JSON-like per severity_id

    Parameters
    ----------
    classified_df : pd.DataFrame
        Output of classify_reviews() filtered to one source.
    fact_df : pd.DataFrame
        fact_review rows for the same source.
    source_id : str
        Source identifier string.

    Returns
    -------
    pd.DataFrame
        One row per issue category.
    """
    total_reviews = len(fact_df)
    total_neg = int((fact_df[rating_col] <= 2).sum())

    if classified_df.empty:
        return pd.DataFrame()

    rows = []
    for iid, grp in classified_df.groupby("issue_id"):
        name = grp["issue_name"].iloc[0]
        vol = grp[review_sk_col].nunique()
        neg_grp = grp[grp[rating_col] <= 2]
        neg_vol = neg_grp[review_sk_col].nunique()
        crit_vol = int((grp["severity_id"] == 1).sum())
        high_vol = int((grp["severity_id"] == 2).sum())
        mod_vol = int((grp["severity_id"] == 3).sum())
        low_vol = int((grp["severity_id"] == 4).sum())

        rows.append({
            "source_id": source_id,
            "issue_id": int(iid),
            "issue_name": name,
            "issue_volume": vol,
            "issue_rate_pct": round(100.0 * vol / total_reviews, 4) if total_reviews > 0 else 0,
            "negative_volume": neg_vol,
            "negative_issue_rate_pct": round(100.0 * neg_vol / total_reviews, 4) if total_reviews > 0 else 0,
            "critical_volume": crit_vol,
            "critical_rate_pct": round(100.0 * crit_vol / total_reviews, 4) if total_reviews > 0 else 0,
            "high_volume": high_vol,
            "moderate_volume": mod_vol,
            "low_volume": low_vol,
            "mean_confidence": round(grp["confidence"].mean(), 4),
            "total_reviews_denominator": total_reviews,
            "total_negative_denominator": total_neg,
        })

    return pd.DataFrame(rows).sort_values("issue_volume", ascending=False).reset_index(drop=True)


def compute_issue_by_category(
    classified_df: pd.DataFrame,
    fact_df: pd.DataFrame,
    source_id: str,
    category_col: str = "category_sk",
    review_sk_col: str = "review_sk",
    rating_col: str = "rating_value",
) -> pd.DataFrame:
    """Compute issue metrics per (category, issue) combination.

    Parameters
    ----------
    classified_df : pd.DataFrame
        Output of classify_reviews() merged with category_sk.
    fact_df : pd.DataFrame
        fact_review with category_sk for the same source.
    source_id : str
        Source identifier.

    Returns
    -------
    pd.DataFrame
        One row per (category, issue) pair.
    """
    if classified_df.empty or category_col not in classified_df.columns:
        return pd.DataFrame()

    # Category-level review counts
    cat_counts = fact_df.groupby(category_col)[review_sk_col].nunique().to_dict()

    rows = []
    for (cat_sk, iid), grp in classified_df.groupby([category_col, "issue_id"]):
        name = grp["issue_name"].iloc[0]
        vol = grp[review_sk_col].nunique()
        cat_total = cat_counts.get(cat_sk, 1)
        neg_vol = grp[grp[rating_col] <= 2][review_sk_col].nunique()

        rows.append({
            "source_id": source_id,
            "category_sk": int(cat_sk),
            "issue_id": int(iid),
            "issue_name": name,
            "issue_volume": vol,
            "category_review_count": cat_total,
            "issue_rate_pct": round(100.0 * vol / cat_total, 4) if cat_total > 0 else 0,
            "negative_volume": neg_vol,
        })

    return pd.DataFrame(rows).sort_values(
        ["category_sk", "issue_volume"], ascending=[True, False]
    ).reset_index(drop=True)


def compute_issue_by_product(
    classified_df: pd.DataFrame,
    fact_df: pd.DataFrame,
    product_col: str = "product_sk",
    review_sk_col: str = "review_sk",
    rating_col: str = "rating_value",
) -> pd.DataFrame:
    """Compute issue metrics per (product, issue) combination.

    Source B only — Source A has no product_sk.

    Parameters
    ----------
    classified_df : pd.DataFrame
        Classified reviews with product_sk.
    fact_df : pd.DataFrame
        fact_review with product_sk for Source B.

    Returns
    -------
    pd.DataFrame
        One row per (product, issue) pair.
    """
    if classified_df.empty or product_col not in classified_df.columns:
        return pd.DataFrame()

    # Filter to valid product_sk (not NULL, not 0)
    valid_class = classified_df[classified_df[product_col].notna() & (classified_df[product_col] != 0)]
    valid_fact = fact_df[fact_df[product_col].notna() & (fact_df[product_col] != 0)]

    if valid_class.empty:
        return pd.DataFrame()

    prod_counts = valid_fact.groupby(product_col)[review_sk_col].nunique().to_dict()
    prod_avg_rating = valid_fact.groupby(product_col)[rating_col].mean().to_dict()

    rows = []
    for (psk, iid), grp in valid_class.groupby([product_col, "issue_id"]):
        name = grp["issue_name"].iloc[0]
        vol = grp[review_sk_col].nunique()
        prod_total = prod_counts.get(psk, 1)
        neg_vol = grp[grp[rating_col] <= 2][review_sk_col].nunique()

        rows.append({
            "product_sk": int(psk),
            "issue_id": int(iid),
            "issue_name": name,
            "issue_volume": vol,
            "product_review_count": prod_total,
            "product_avg_rating": round(prod_avg_rating.get(psk, 0), 2),
            "issue_rate_pct": round(100.0 * vol / prod_total, 4) if prod_total > 0 else 0,
            "negative_volume": neg_vol,
        })

    return pd.DataFrame(rows).sort_values(
        ["issue_volume"], ascending=False
    ).reset_index(drop=True)
