"""Baseline Policy Benchmarking Engine.

Phase 10 Decision Support System.
Compares the proposed Multi-Factor DSS against three naive operational policies:
    - Baseline 0: FIFO / Default order
    - Baseline 1: Volume-Only Policy (ranked purely by total complaint volume)
    - Baseline 2: Severity-Only Policy (ranked purely by critical severity proportion)
    - Proposed: Multi-Factor DSS Priority Score

Methodological Constraint:
    All comparative results are labeled: SIMULATED_DECISION_EVALUATION.
    No claims of real operational workload reduction or revenue impact are made.
"""
from __future__ import annotations

from typing import Dict, List, Optional
import numpy as np
import pandas as pd


def compute_gini(values: np.ndarray) -> float:
    """Compute Gini concentration coefficient of a 1D array."""
    v = np.sort(np.asarray(values, dtype=float))
    n = len(v)
    if n == 0 or np.sum(v) == 0:
        return 0.0
    index = np.arange(1, n + 1)
    return float((2 * np.sum(index * v) - (n + 1) * np.sum(v)) / (n * np.sum(v)))


def evaluate_policy_benchmarks(
    decision_queue_df: pd.DataFrame,
    top_k_pcts: List[float] = [0.05, 0.10, 0.20],
) -> Dict:
    """Evaluate proposed DSS against standard naive baseline policies.

    Target Proxy Class: High-Impact Chronic Defect Cases
    Defined as: critical_severity_count >= 3 AND distinct_review_events >= 3.

    Parameters
    ----------
    decision_queue_df : pd.DataFrame
        Scored decision queue DataFrame (e.g. from generate_decision_queue_product).
    top_k_pcts : list of float
        Cutoff fractions for evaluation (e.g. [0.05, 0.10, 0.20]).

    Returns
    -------
    dict
        Benchmark evaluation dictionary containing comparative metrics.
    """
    if decision_queue_df.empty:
        return {}

    df = decision_queue_df.copy()
    n_total = len(df)

    # Define high-impact proxy target
    df["is_high_impact_proxy"] = (
        (df["critical_severity_count"] >= 3) & (df["distinct_review_events"] >= 3)
    ).astype(int)

    total_high_impact = int(df["is_high_impact_proxy"].sum())

    # Generate Rankings for Policies
    # 1. Proposed DSS
    df_dss = df.sort_values("priority_score", ascending=False).reset_index(drop=True)
    # 2. Baseline 1: Volume-Only
    df_vol = df.sort_values("evidence_support", ascending=False).reset_index(drop=True)
    # 3. Baseline 2: Severity-Only
    df_sev = df.sort_values(["severity_impact_score", "evidence_support"], ascending=False).reset_index(drop=True)
    # 4. Baseline 0: FIFO (Original Index)
    df_fifo = df.copy().reset_index(drop=True)

    policies = {
        "Proposed_MultiFactor_DSS": df_dss,
        "Baseline_Volume_Only": df_vol,
        "Baseline_Severity_Only": df_sev,
        "Baseline_FIFO_Default": df_fifo,
    }

    results = {
        "evaluation_type": "SIMULATED_DECISION_EVALUATION",
        "total_cases_evaluated": n_total,
        "total_high_impact_targets": total_high_impact,
        "high_impact_base_rate_pct": round(100.0 * total_high_impact / n_total, 2) if n_total > 0 else 0.0,
        "policy_metrics": {},
    }

    for pol_name, p_df in policies.items():
        pol_res = {"gini_concentration": round(compute_gini(p_df["priority_score"].values), 4)}

        for k in top_k_pcts:
            k_int = max(1, int(n_total * k))
            top_slice = p_df.head(k_int)

            captured = int(top_slice["is_high_impact_proxy"].sum())
            prec_at_k = captured / k_int if k_int > 0 else 0.0
            rec_at_k = captured / total_high_impact if total_high_impact > 0 else 0.0
            small_sample_rate = float((top_slice["evidence_support"] < 5).mean())

            k_label = f"top_{int(k*100)}pct"
            pol_res[k_label] = {
                "cutoff_n": k_int,
                "precision_at_k": round(prec_at_k, 4),
                "recall_at_k": round(rec_at_k, 4),
                "small_sample_false_alarm_rate": round(small_sample_rate, 4),
            }

        results["policy_metrics"][pol_name] = pol_res

    # Comparative Summary at Top 10%
    summary_table = []
    for pol_name, m in results["policy_metrics"].items():
        t10 = m.get("top_10pct", {})
        summary_table.append({
            "policy": pol_name,
            "precision_at_10pct": t10.get("precision_at_k", 0.0),
            "recall_at_10pct": t10.get("recall_at_k", 0.0),
            "small_sample_rate_at_10pct": t10.get("small_sample_false_alarm_rate", 0.0),
            "gini_concentration": m.get("gini_concentration", 0.0),
        })
    results["summary_table"] = summary_table

    return results
