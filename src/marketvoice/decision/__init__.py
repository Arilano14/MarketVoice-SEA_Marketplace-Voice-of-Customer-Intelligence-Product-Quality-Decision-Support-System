"""MarketVoice SEA — Decision Support & Priority Scoring Package.

Phase 10: Decision Support System (DSS) & Priority Case Scoring.
Provides explainable multi-criteria priority scoring, reason code attribution,
decision queue generation across 3 isolated grains, baseline policy benchmarking,
and Monte Carlo sensitivity analysis.
"""
from marketvoice.decision.priority_score import (
    DEFAULT_WEIGHTS,
    CALCULATION_VERSION,
    compute_priority_score,
    normalize_feature,
)
from marketvoice.decision.reason_codes import (
    REASON_CODES,
    generate_reason_codes,
)
from marketvoice.decision.decision_queue import (
    PRIORITY_TIERS,
    generate_decision_queue_product,
    generate_decision_queue_category,
    generate_decision_queue_source,
)
from marketvoice.decision.benchmarking import (
    evaluate_policy_benchmarks,
)
from marketvoice.decision.sensitivity_analysis import (
    run_monte_carlo_sensitivity,
)

__all__ = [
    "DEFAULT_WEIGHTS",
    "CALCULATION_VERSION",
    "PRIORITY_TIERS",
    "REASON_CODES",
    "compute_priority_score",
    "normalize_feature",
    "generate_reason_codes",
    "generate_decision_queue_product",
    "generate_decision_queue_category",
    "generate_decision_queue_source",
    "evaluate_policy_benchmarks",
    "run_monte_carlo_sensitivity",
]
