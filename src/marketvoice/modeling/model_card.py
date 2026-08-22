"""Model Card generator — structured JSON metadata for every trained model.

Follows a minimal Model Card schema that captures:
  model identity, training configuration, evaluation metrics,
  limitations, and downstream usage contract.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional


def create_model_card(
    model_name: str,
    model_version: str,
    source_scope: str,
    task: str,
    target_variable: str,
    dataset_reference: str,
    preprocessing_version: str,
    seed: int,
    training_config: Dict[str, Any],
    validation_metrics: Dict[str, Any],
    test_metrics: Optional[Dict[str, Any]] = None,
    selected_status: str = "candidate",
    selection_rationale: str = "",
    limitations: Optional[list] = None,
    training_date: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a structured model card dictionary.

    Parameters
    ----------
    model_name : str
        Functional model name (e.g. 'tfidf_logistic_regression_rating_srca').
    model_version : str
        Semantic version string.
    source_scope : str
        Which source this model was trained on.
    task : str
        Classification task name (e.g. 'rating_classification').
    target_variable : str
        Target column name.
    dataset_reference : str
        Dataset or table reference.
    preprocessing_version : str
        Preprocessing pipeline version.
    seed : int
        Random seed used.
    training_config : dict
        Model hyperparameters and training configuration.
    validation_metrics : dict
        Metrics on validation set.
    test_metrics : dict, optional
        Metrics on holdout test set (populated after final evaluation).
    selected_status : str
        One of 'candidate', 'champion', 'not_selected'.
    selection_rationale : str
        Explanation for champion selection or non-selection.
    limitations : list, optional
        Known model limitations.
    training_date : str, optional
        ISO format training date.

    Returns
    -------
    dict
        Structured model card.
    """
    card = {
        "model_card_version": "1.0",
        "model_name": model_name,
        "model_version": model_version,
        "phase": "Phase 8",
        "task": task,
        "target_variable": target_variable,
        "source_scope": source_scope,
        "dataset_reference": dataset_reference,
        "preprocessing_version": preprocessing_version,
        "seed": seed,
        "training_date": training_date or datetime.now(timezone.utc).isoformat(),
        "training_config": training_config,
        "validation_metrics": validation_metrics,
        "test_metrics": test_metrics,
        "selected_status": selected_status,
        "selection_rationale": selection_rationale,
        "limitations": limitations or [],
    }
    return card


def save_model_card(card: Dict[str, Any], output_dir: str) -> str:
    """Save model card as JSON to the metadata directory.

    Parameters
    ----------
    card : dict
        Model card dictionary.
    output_dir : str
        Directory path (e.g. models/metadata/).

    Returns
    -------
    str
        Path to the saved JSON file.
    """
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{card['model_name']}_v{card['model_version']}.json"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(card, f, indent=2, ensure_ascii=False, default=str)
    return filepath
