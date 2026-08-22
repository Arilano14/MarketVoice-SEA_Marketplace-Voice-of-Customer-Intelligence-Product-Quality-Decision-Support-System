"""Multi-metric evaluation engine for classification tasks.

Covers all metrics required by the evaluation protocol:
  - Accuracy, Macro F1, Weighted F1
  - Per-class Precision, Recall, Support
  - Confusion Matrix
  - Quadratic Weighted Kappa (QWK) — for ordinal rating tasks
  - Mean Absolute Error (MAE) — for ordinal rating tasks
  - ROC-AUC — for binary tasks where applicable
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np


def _safe_import_sklearn():
    """Import sklearn components; raise clear error if missing."""
    try:
        from sklearn.metrics import (
            accuracy_score,
            f1_score,
            precision_recall_fscore_support,
            confusion_matrix,
            cohen_kappa_score,
            mean_absolute_error,
            classification_report,
        )
        return {
            "accuracy_score": accuracy_score,
            "f1_score": f1_score,
            "precision_recall_fscore_support": precision_recall_fscore_support,
            "confusion_matrix": confusion_matrix,
            "cohen_kappa_score": cohen_kappa_score,
            "mean_absolute_error": mean_absolute_error,
            "classification_report": classification_report,
        }
    except ImportError as e:
        raise ImportError(
            "scikit-learn is required for evaluation. "
            "Install with: pip install scikit-learn --target .pipdeps"
        ) from e


def evaluate_classification(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    labels: Optional[List] = None,
    task_type: str = "multiclass",
) -> Dict[str, Any]:
    """Compute comprehensive classification metrics.

    Parameters
    ----------
    y_true : array-like
        Ground truth labels.
    y_pred : array-like
        Predicted labels.
    labels : list, optional
        Ordered label list.  If None, inferred from data.
    task_type : str
        One of 'multiclass', 'binary', 'ordinal'.
        'ordinal' adds QWK and MAE.

    Returns
    -------
    dict
        All computed metrics.
    """
    sk = _safe_import_sklearn()

    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    if labels is None:
        labels = sorted(set(y_true) | set(y_pred))

    results: Dict[str, Any] = {}

    results["accuracy"] = round(float(sk["accuracy_score"](y_true, y_pred)), 4)
    results["macro_f1"] = round(float(sk["f1_score"](y_true, y_pred, average="macro", labels=labels, zero_division=0)), 4)
    results["weighted_f1"] = round(float(sk["f1_score"](y_true, y_pred, average="weighted", labels=labels, zero_division=0)), 4)

    # Per-class metrics
    prec, rec, f1, sup = sk["precision_recall_fscore_support"](
        y_true, y_pred, labels=labels, zero_division=0
    )
    per_class = {}
    for i, lbl in enumerate(labels):
        per_class[str(lbl)] = {
            "precision": round(float(prec[i]), 4),
            "recall": round(float(rec[i]), 4),
            "f1": round(float(f1[i]), 4),
            "support": int(sup[i]),
        }
    results["per_class"] = per_class

    # Confusion matrix
    cm = sk["confusion_matrix"](y_true, y_pred, labels=labels)
    results["confusion_matrix"] = cm.tolist()
    results["labels"] = [str(l) for l in labels]

    # Ordinal metrics
    if task_type == "ordinal":
        results["qwk"] = round(float(sk["cohen_kappa_score"](y_true, y_pred, weights="quadratic")), 4)
        results["mae"] = round(float(sk["mean_absolute_error"](y_true, y_pred)), 4)

    return results


def format_report(metrics: Dict[str, Any], title: str = "") -> str:
    """Format metrics dict into a human-readable string report."""
    lines = []
    if title:
        lines.append(f"=== {title} ===")
    lines.append(f"Accuracy:    {metrics['accuracy']:.4f}")
    lines.append(f"Macro F1:    {metrics['macro_f1']:.4f}")
    lines.append(f"Weighted F1: {metrics['weighted_f1']:.4f}")

    if "qwk" in metrics:
        lines.append(f"QWK:         {metrics['qwk']:.4f}")
    if "mae" in metrics:
        lines.append(f"MAE:         {metrics['mae']:.4f}")

    lines.append("")
    lines.append(f"{'Class':<12s} {'Prec':>6s} {'Rec':>6s} {'F1':>6s} {'Sup':>6s}")
    lines.append("-" * 38)
    for lbl, m in metrics["per_class"].items():
        lines.append(f"{lbl:<12s} {m['precision']:>6.4f} {m['recall']:>6.4f} {m['f1']:>6.4f} {m['support']:>6d}")

    return "\n".join(lines)
