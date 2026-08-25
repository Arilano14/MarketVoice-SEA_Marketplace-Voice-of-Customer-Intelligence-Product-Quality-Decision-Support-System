"""Multi-Criteria Priority Scoring Mathematical Engine.

Phase 10 Decision Support System.
Implements an explainable, bounded linear utility model:
    PRS = 100 * sum(w_i * phi_i(x_i))

Dimensions:
    DIM-1: Severity Impact (Rating-based severity proxy ratio) - Weight: 0.30
    DIM-2: Dissatisfaction Overrepresentation (Low-rating rate ratio) - Weight: 0.25
    DIM-3: Distinct Review-Event Recurrence (Log-scaled) - Weight: 0.20
    DIM-4: Evidence Support Volume (Log-scaled) - Weight: 0.15
    DIM-5: Model Classification Confidence (Linear rescaled) - Weight: 0.10

Data governance:
    - Deterministic and reproducible.
    - All sub-scores are recoverable and bounded [0, 100].
    - Zero hidden parameters or mutable runtime globals.
"""
from __future__ import annotations

import math
from typing import Dict, Optional, Tuple, Union

CALCULATION_VERSION = "1.0"

# Default baseline weights (sum to 1.0)
DEFAULT_WEIGHTS: Dict[str, float] = {
    "severity": 0.30,
    "dissatisfaction": 0.25,
    "recurrence": 0.20,
    "volume": 0.15,
    "confidence": 0.10,
}

# Fixed reference parameters for deterministic scaling
REFERENCE_PARAMS = {
    "dissat_min": 1.0,
    "dissat_max": 4.0,
    "recurrence_max_ref": 300.0,  # log1p(300) is the reference maximum
    "volume_max_ref": 6000.0,     # log1p(6000) is the reference maximum
    "conf_min": 0.3333,
    "conf_max": 1.0,
}


def normalize_feature(
    val: float,
    feature_type: str,
    custom_params: Optional[Dict[str, float]] = None,
) -> float:
    """Normalize a raw feature into [0.0, 1.0] interval.

    Parameters
    ----------
    val : float
        Raw feature value.
    feature_type : str
        One of 'severity', 'dissatisfaction', 'recurrence', 'volume', 'confidence'.
    custom_params : dict, optional
        Override default reference parameters.

    Returns
    -------
    float
        Normalized value in [0.0, 1.0].
    """
    params = REFERENCE_PARAMS.copy()
    if custom_params:
        params.update(custom_params)

    val = float(val) if val is not None and not math.isnan(val) else 0.0

    if feature_type == "severity":
        # Severity ratio is already a proportion [0.0, 1.0]
        return max(0.0, min(1.0, val))

    elif feature_type == "dissatisfaction":
        # Ratio >= 1.0 (1.0x -> 0.0, >= 4.0x -> 1.0)
        d_min = params["dissat_min"]
        d_max = params["dissat_max"]
        if d_max == d_min:
            return 0.0
        norm = (val - d_min) / (d_max - d_min)
        return max(0.0, min(1.0, norm))

    elif feature_type == "recurrence":
        # Log-scaled distinct review events
        r_max = params["recurrence_max_ref"]
        denom = math.log1p(r_max)
        if denom == 0.0:
            return 0.0
        norm = math.log1p(max(0.0, val)) / denom
        return max(0.0, min(1.0, norm))

    elif feature_type == "volume":
        # Log-scaled issue fact volume
        v_max = params["volume_max_ref"]
        denom = math.log1p(v_max)
        if denom == 0.0:
            return 0.0
        norm = math.log1p(max(0.0, val)) / denom
        return max(0.0, min(1.0, norm))

    elif feature_type == "confidence":
        # Rescale [0.3333, 1.0] -> [0.0, 1.0]
        c_min = params["conf_min"]
        c_max = params["conf_max"]
        if c_max == c_min:
            return 0.0
        norm = (val - c_min) / (c_max - c_min)
        return max(0.0, min(1.0, norm))

    else:
        raise ValueError(f"Unknown feature_type: {feature_type}")


def compute_priority_score(
    severity_ratio: float,
    dissatisfaction_ratio: float,
    recurrence_count: int,
    volume: int,
    confidence: float,
    weights: Optional[Dict[str, float]] = None,
    custom_params: Optional[Dict[str, float]] = None,
) -> Dict[str, float]:
    """Compute composite Priority Risk Score (PRS) and individual sub-scores.

    Parameters
    ----------
    severity_ratio : float
        Critical + High severity fact ratio in [0, 1].
    dissatisfaction_ratio : float
        Low-rating dissatisfaction rate ratio (>= 0.0).
    recurrence_count : int
        Distinct review event count for entity (>= 0).
    volume : int
        Total issue facts for entity (>= 0).
    confidence : float
        Mean classification confidence in [0, 1].
    weights : dict, optional
        Custom weight dictionary. Must sum to 1.0.
    custom_params : dict, optional
        Custom reference parameters for normalization.

    Returns
    -------
    dict
        Dictionary containing:
        - 'priority_score': float in [0.0, 100.0]
        - 'severity_impact_score': float in [0.0, 100.0]
        - 'dissatisfaction_score': float in [0.0, 100.0]
        - 'recurrence_score': float in [0.0, 100.0]
        - 'volume_score': float in [0.0, 100.0]
        - 'confidence_score': float in [0.0, 100.0]
    """
    w = (weights or DEFAULT_WEIGHTS).copy()
    total_w = sum(w.values())
    if abs(total_w - 1.0) > 1e-4:
        # Re-normalize if sum != 1.0
        w = {k: v / total_w for k, v in w.items()}

    phi_sev = normalize_feature(severity_ratio, "severity", custom_params)
    phi_dis = normalize_feature(dissatisfaction_ratio, "dissatisfaction", custom_params)
    phi_rec = normalize_feature(recurrence_count, "recurrence", custom_params)
    phi_vol = normalize_feature(volume, "volume", custom_params)
    phi_cnf = normalize_feature(confidence, "confidence", custom_params)

    # Sub-scores (0-100)
    sub_sev = round(100.0 * phi_sev, 2)
    sub_dis = round(100.0 * phi_dis, 2)
    sub_rec = round(100.0 * phi_rec, 2)
    sub_vol = round(100.0 * phi_vol, 2)
    sub_cnf = round(100.0 * phi_cnf, 2)

    # Composite PRS (0-100)
    raw_prs = (
        w["severity"] * phi_sev
        + w["dissatisfaction"] * phi_dis
        + w["recurrence"] * phi_rec
        + w["volume"] * phi_vol
        + w["confidence"] * phi_cnf
    )
    prs = round(max(0.0, min(100.0, 100.0 * raw_prs)), 2)

    return {
        "priority_score": prs,
        "severity_impact_score": sub_sev,
        "dissatisfaction_score": sub_dis,
        "recurrence_score": sub_rec,
        "volume_score": sub_vol,
        "confidence_score": sub_cnf,
    }
