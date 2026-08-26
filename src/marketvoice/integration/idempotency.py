"""Deterministic Idempotency Key Generation, Payload Hashing, and PII Sanitization.

Phase 11: Operational Automation & Inference Service.
Computes deterministic SHA-256 idempotency hashes from source, review,
and algorithm version components, and provides regex-based PII masking.
"""
from __future__ import annotations

import hashlib
import re
from typing import Optional


# PII Masking Regexes
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_REGEX = re.compile(r"(\+62|62|08)[0-9]{8,12}")
USER_TAG_REGEX = re.compile(r"@\w{3,}")


def mask_pii(text: str) -> str:
    """Mask personally identifiable information (PII) from review text.

    Parameters
    ----------
    text : str
        Input raw text.

    Returns
    -------
    str
        Sanitized text with masked emails, phone numbers, and handles.
    """
    if not text:
        return ""
    masked = EMAIL_REGEX.sub("[REDACTED_EMAIL]", text)
    masked = PHONE_REGEX.sub("[REDACTED_PHONE]", masked)
    masked = USER_TAG_REGEX.sub("[REDACTED_USER]", masked)
    return masked


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
