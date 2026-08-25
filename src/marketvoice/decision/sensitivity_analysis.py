"""Monte Carlo Weight Sensitivity and Stability Analysis.

Phase 10 Decision Support System.
Evaluates ranking robustness under weight perturbations (+/- 20%)
using 1,000 Monte Carlo iterations.

Metrics:
    - Kendall's rank correlation (tau)
    - Spearman's rank correlation (rho)
    - Top-10% Queue Membership Jaccard Similarity
    - Stability Classification: HIGH, MODERATE, LOW
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from scipy.stats import kendalltau, spearmanr

from marketvoice.decision.priority_score import (
    DEFAULT_WEIGHTS,
    compute_priority_score,
)

CANONICAL_SEED = 42


def run_monte_carlo_sensitivity(
    decision_queue_df: pd.DataFrame,
    n_simulations: int = 1000,
    perturbation_range: float = 0.20,
    seed: int = CANONICAL_SEED,
    top_k_pct: float = 0.10,
) -> Dict:
    """Run Monte Carlo weight sensitivity analysis on the decision queue.

    Parameters
    ----------
    decision_queue_df : pd.DataFrame
        Baseline decision queue DataFrame with raw sub-score components.
    n_simulations : int
        Number of Monte Carlo iterations (default 1000).
    perturbation_range : float
        Fractional perturbation range (+/- 20% = 0.20).
    seed : int
        Random state seed.
    top_k_pct : float
        Cutoff fraction for queue membership stability (default 10%).

    Returns
    -------
    dict
        Sensitivity analysis metrics and stability assessment.
    """
    if decision_queue_df.empty:
        return {}

    rng = np.random.default_rng(seed)
    n_cases = len(decision_queue_df)
    k_cutoff = max(1, int(n_cases * top_k_pct))

    # Extract sub-scores (0-1) for fast matrix computation
    phi_sev = decision_queue_df["severity_impact_score"].values / 100.0
    phi_dis = decision_queue_df["dissatisfaction_score"].values / 100.0
    phi_rec = decision_queue_df["recurrence_score"].values / 100.0
    phi_vol = decision_queue_df["volume_score"].values / 100.0
    phi_cnf = decision_queue_df["confidence_score"].values / 100.0

    phi_matrix = np.column_stack([phi_sev, phi_dis, phi_rec, phi_vol, phi_cnf])
    base_w_arr = np.array([
        DEFAULT_WEIGHTS["severity"],
        DEFAULT_WEIGHTS["dissatisfaction"],
        DEFAULT_WEIGHTS["recurrence"],
        DEFAULT_WEIGHTS["volume"],
        DEFAULT_WEIGHTS["confidence"],
    ])

    # Baseline scores computed from base weights
    baseline_scores = np.dot(phi_matrix, base_w_arr) * 100.0
    baseline_ranks = np.argsort(-baseline_scores)
    baseline_top_k = set(baseline_ranks[:k_cutoff])

    kendall_taus = []
    spearman_rhos = []
    jaccard_sims = []

    # Run simulations
    for _ in range(n_simulations):
        # Perturb weights by uniform random in [1 - range, 1 + range]
        multipliers = rng.uniform(1.0 - perturbation_range, 1.0 + perturbation_range, size=5)
        perturbed_w = base_w_arr * multipliers
        perturbed_w /= np.sum(perturbed_w)  # Re-normalize sum to 1.0

        # Compute perturbed scores
        sim_scores = np.dot(phi_matrix, perturbed_w) * 100.0
        sim_ranks = np.argsort(-sim_scores)
        sim_top_k = set(sim_ranks[:k_cutoff])

        # Correlation metrics on ranks (computed on sample for efficiency if large)
        tau, _ = kendalltau(baseline_scores[:500], sim_scores[:500])
        rho, _ = spearmanr(baseline_scores, sim_scores)

        # Jaccard similarity of top-K queue
        intersection = len(baseline_top_k.intersection(sim_top_k))
        union = len(baseline_top_k.union(sim_top_k))
        jaccard = intersection / union if union > 0 else 1.0

        if not np.isnan(tau):
            kendall_taus.append(tau)
        if not np.isnan(rho):
            spearman_rhos.append(rho)
        jaccard_sims.append(jaccard)

    mean_tau = round(float(np.mean(kendall_taus)), 4) if kendall_taus else 0.0
    mean_rho = round(float(np.mean(spearman_rhos)), 4) if spearman_rhos else 0.0
    mean_jaccard = round(float(np.mean(jaccard_sims)), 4) if jaccard_sims else 0.0

    # Classification
    if mean_tau >= 0.85 and mean_jaccard >= 0.80:
        stability_class = "HIGH"
    elif mean_tau >= 0.70:
        stability_class = "MODERATE"
    else:
        stability_class = "LOW"

    return {
        "n_simulations": n_simulations,
        "perturbation_range_pct": f"{int(perturbation_range * 100)}%",
        "top_k_evaluated_pct": f"{int(top_k_pct * 100)}%",
        "mean_kendall_tau": mean_tau,
        "min_kendall_tau": round(float(np.min(kendall_taus)), 4) if kendall_taus else 0.0,
        "mean_spearman_rho": mean_rho,
        "mean_top_k_jaccard_stability": mean_jaccard,
        "min_top_k_jaccard_stability": round(float(np.min(jaccard_sims)), 4) if jaccard_sims else 0.0,
        "stability_classification": stability_class,
        "desired_target_benchmark": "Kendall tau >= 0.85 | Top-K Jaccard >= 0.80",
    }
