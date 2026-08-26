"""Deterministic Idempotency Key Generation and Validation.

Phase 11: Operational Automation & Inference Service.
Computes deterministic SHA-256 idempotency hashes from source, review,
and algorithm version components.
"""
from __future__ import annotations

import hashlib
from typing import Optional


def compute_idempotency_key(
    source_id: str,
    review_id: str,
    calculation_version: str = "1.0",
) -> str:
    """Compute deterministic SHA-256 idempotency key.

    Parameters
    ----------
    source_id : str
        Source identifier (e.g. SRC_TOKOPEDIA_REVIEWS_2019).
    review_id : str
        Source review or entity identifier.
    calculation_version : str
        Algorithm version string.

    Returns
    -------
    str
        64-character lowercase hexadecimal SHA-256 hash.
    """
    raw_key = f"{source_id.strip()}:{review_id.strip()}:{calculation_version.strip()}"
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


def compute_payload_hash(payload_str: str) -> str:
    """Compute SHA-256 hash of the raw string payload."""
    return hashlib.sha256(payload_str.encode("utf-8")).hexdigest()
