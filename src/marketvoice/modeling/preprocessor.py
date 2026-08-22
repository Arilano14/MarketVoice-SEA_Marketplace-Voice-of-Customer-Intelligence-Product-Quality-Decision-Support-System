"""Deterministic text preprocessor for Indonesian marketplace reviews.

Design principles:
- Deterministic: same input always produces same output.
- Non-destructive: preserves sentiment-bearing punctuation and negation.
- Unicode-safe: normalises to NFC form.
- Minimal: only applies transformations that measurably help downstream tasks.
"""
from __future__ import annotations

import re
import unicodedata


def preprocess(text: str) -> str:
    """Apply the canonical preprocessing pipeline.

    Steps
    -----
    1. Unicode NFC normalisation.
    2. Replace NULL-like sentinels with empty string.
    3. Strip leading/trailing whitespace.
    4. Collapse internal whitespace sequences to single space.
    5. Lower-case.

    Intentionally NOT applied (may destroy sentiment signal):
    - Aggressive stopword removal
    - Punctuation stripping (exclamation marks carry sentiment weight)
    - Negation word removal
    - Emoji removal (emojis carry sentiment signal)
    - Stemming (Indonesian morphology is complex; stemming without
      validation risks destroying meaning)

    Parameters
    ----------
    text : str
        Raw review text from the warehouse.

    Returns
    -------
    str
        Preprocessed text.
    """
    if not isinstance(text, str):
        return ""

    # 1. Unicode NFC normalisation
    text = unicodedata.normalize("NFC", text)

    # 2. Replace known NULL-like sentinels
    if text.strip().lower() in ("null", "none", "nan", "n/a", ""):
        return ""

    # 3. Strip edges
    text = text.strip()

    # 4. Collapse internal whitespace
    text = re.sub(r"\s+", " ", text)

    # 5. Lower-case
    text = text.lower()

    return text


def normalise_for_dedup(text: str) -> str:
    """Stronger normalisation used ONLY for duplicate grouping.

    Applies preprocessing + strips all punctuation + collapses spaces.
    This is intentionally more aggressive because it is only used
    to identify duplicate review *content*, not as model input.

    Parameters
    ----------
    text : str
        Raw or preprocessed text.

    Returns
    -------
    str
        Normalised text suitable for dedup hashing.
    """
    text = preprocess(text)
    # Remove all non-alphanumeric (keep spaces between words)
    text = re.sub(r"[^\w\s]", "", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text).strip()
    return text
