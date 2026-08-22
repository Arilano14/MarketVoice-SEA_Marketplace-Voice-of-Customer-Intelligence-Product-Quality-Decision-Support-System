"""Error analysis module for classification model diagnostics.

Slices predictions by review length, rating boundary, and text
characteristics to identify systematic failure modes.
"""
from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
import pandas as pd


def error_slice_analysis(
    df: pd.DataFrame,
    y_true_col: str,
    y_pred_col: str,
    text_col: str = "review_text_preprocessed",
    text_len_col: str = "review_text_len_chars",
) -> Dict[str, Any]:
    """Perform stratified error analysis across review slices.

    Slices
    ------
    - By text length: short (<30 chars), medium (30-100), long (>100)
    - By rating boundary: 2-3 boundary, 3-4 boundary
    - Overall error rate

    Returns
    -------
    dict
        Error rates and counts per slice.
    """
    df = df.copy()
    df["_correct"] = df[y_true_col] == df[y_pred_col]

    results = {}

    # Overall
    total = len(df)
    correct = df["_correct"].sum()
    results["overall"] = {
        "total": total,
        "correct": int(correct),
        "errors": total - int(correct),
        "error_rate": round(1 - correct / total, 4) if total > 0 else 0,
    }

    # By text length
    if text_len_col in df.columns:
        bins = [0, 30, 100, float("inf")]
        labels_len = ["short_lt30", "medium_30_100", "long_gt100"]
        df["_len_bucket"] = pd.cut(df[text_len_col], bins=bins, labels=labels_len, right=False)
        for bucket in labels_len:
            subset = df[df["_len_bucket"] == bucket]
            n = len(subset)
            if n > 0:
                err = (subset["_correct"] == False).sum()
                results[f"length_{bucket}"] = {
                    "total": n,
                    "errors": int(err),
                    "error_rate": round(int(err) / n, 4),
                }

    # By true label (per-class error rate)
    per_class = {}
    for lbl in sorted(df[y_true_col].unique()):
        subset = df[df[y_true_col] == lbl]
        n = len(subset)
        if n > 0:
            err = (subset["_correct"] == False).sum()
            per_class[str(lbl)] = {
                "total": n,
                "errors": int(err),
                "error_rate": round(int(err) / n, 4),
            }
    results["per_class_errors"] = per_class

    # Confused pairs (most common misclassifications)
    errors_df = df[~df["_correct"]]
    if len(errors_df) > 0:
        confused = (
            errors_df.groupby([y_true_col, y_pred_col])
            .size()
            .reset_index(name="count")
            .sort_values("count", ascending=False)
            .head(10)
        )
        results["top_confused_pairs"] = [
            {"true": str(row[y_true_col]), "pred": str(row[y_pred_col]), "count": int(row["count"])}
            for _, row in confused.iterrows()
        ]

    return results


def confidence_analysis(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_proba: np.ndarray,
    labels: List,
) -> Dict[str, Any]:
    """Analyse model confidence vs correctness.

    Parameters
    ----------
    y_true : array-like
        Ground truth labels.
    y_pred : array-like
        Predicted labels.
    y_proba : array-like (n_samples, n_classes)
        Predicted probability distribution.
    labels : list
        Ordered class labels matching proba columns.

    Returns
    -------
    dict
        Confidence statistics for correct vs incorrect predictions.
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    y_proba = np.asarray(y_proba)

    max_proba = y_proba.max(axis=1)
    correct_mask = y_true == y_pred

    results = {
        "mean_confidence_correct": round(float(max_proba[correct_mask].mean()), 4) if correct_mask.any() else None,
        "mean_confidence_incorrect": round(float(max_proba[~correct_mask].mean()), 4) if (~correct_mask).any() else None,
        "median_confidence_correct": round(float(np.median(max_proba[correct_mask])), 4) if correct_mask.any() else None,
        "median_confidence_incorrect": round(float(np.median(max_proba[~correct_mask])), 4) if (~correct_mask).any() else None,
        "total_correct": int(correct_mask.sum()),
        "total_incorrect": int((~correct_mask).sum()),
    }

    # Confidence buckets
    buckets = [(0.0, 0.5), (0.5, 0.7), (0.7, 0.9), (0.9, 1.01)]
    bucket_stats = []
    for lo, hi in buckets:
        mask = (max_proba >= lo) & (max_proba < hi)
        n = int(mask.sum())
        if n > 0:
            acc = float(correct_mask[mask].mean())
            bucket_stats.append({
                "range": f"{lo:.1f}-{hi:.1f}",
                "count": n,
                "accuracy": round(acc, 4),
            })
    results["confidence_buckets"] = bucket_stats

    return results
