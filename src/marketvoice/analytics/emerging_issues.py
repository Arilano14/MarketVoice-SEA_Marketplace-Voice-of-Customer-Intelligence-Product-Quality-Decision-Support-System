"""Backwards compatibility wrapper for dissatisfaction_drivers.py.

DEPRECATION NOTICE:
    The module name 'emerging_issues' is deprecated in Phase 9 Remediation.
    In the absence of temporal timestamps (NO_TEMPORAL_DATA), this analysis
    is formally titled 'Customer Dissatisfaction Driver Analysis' /
    'Low-Rating Issue Overrepresentation Analysis'.

    Please import from `marketvoice.analytics.dissatisfaction_drivers` directly.
"""
from __future__ import annotations

import warnings
from typing import Dict, List

import pandas as pd

from marketvoice.analytics.dissatisfaction_drivers import (
    MIN_DISSATISFACTION_SUPPORT,
    Z_THRESHOLD,
    proportion_z_test as _proportion_z_test,
    analyze_dissatisfaction_drivers as detect_emerging_issues,
)

MIN_EMERGING_SUPPORT = MIN_DISSATISFACTION_SUPPORT

__all__ = [
    "MIN_EMERGING_SUPPORT",
    "Z_THRESHOLD",
    "_proportion_z_test",
    "detect_emerging_issues",
]
