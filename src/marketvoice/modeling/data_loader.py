"""Data loader — read-only extraction from the MarketVoice warehouse.

Extracts review text, rating, and gold labels from fact_review with
strict source isolation.  Never modifies warehouse tables.

Uses cursor-based fetch (not pd.read_sql) for psycopg3 compatibility.
"""
from __future__ import annotations

import os
import sys
from typing import Optional

import pandas as pd

_PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)
_PIPDEPS = os.path.join(_PROJECT_ROOT, ".pipdeps")
if os.path.isdir(_PIPDEPS) and _PIPDEPS not in sys.path:
    sys.path.insert(0, _PIPDEPS)

from marketvoice.database.connection import DBSettings, connect
from marketvoice.database.schema import SCHEMA


# Canonical source identifiers
SOURCE_A = "SRC_PRDECT_ID_V1"
SOURCE_B = "SRC_TOKOPEDIA_REVIEWS_2019"

_COLUMNS = [
    "review_sk", "source_sk", "source_id", "review_text", "rating_value",
    "source_gold_sentiment_label", "source_gold_emotion_label",
    "review_text_len_chars", "category_sk", "product_sk", "shop_sk",
]


def load_reviews(
    source_id: str,
    dbname_override: Optional[str] = None,
) -> pd.DataFrame:
    """Extract reviews for a single source.  READ-ONLY.

    Parameters
    ----------
    source_id : str
        One of SOURCE_A or SOURCE_B.
    dbname_override : str, optional
        Override the target database name (e.g. for test).

    Returns
    -------
    pd.DataFrame
        Columns: review_sk, source_sk, source_id, review_text, rating_value,
                 source_gold_sentiment_label, source_gold_emotion_label,
                 review_text_len_chars, category_sk, product_sk, shop_sk.
    """
    if source_id not in (SOURCE_A, SOURCE_B):
        raise ValueError(f"Unknown source_id: {source_id}")

    settings = DBSettings.from_env()
    conn = connect(settings, dbname_override=dbname_override or settings.dev_dbname)
    try:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT
                    fr.review_sk,
                    fr.source_sk,
                    ds.source_id,
                    fr.review_text,
                    fr.rating_value,
                    fr.source_gold_sentiment_label,
                    fr.source_gold_emotion_label,
                    fr.review_text_len_chars,
                    fr.category_sk,
                    fr.product_sk,
                    fr.shop_sk
                FROM {SCHEMA}.fact_review fr
                JOIN {SCHEMA}.dim_source ds ON fr.source_sk = ds.source_sk
                WHERE ds.source_id = %s
                  AND fr.is_synthetic = FALSE
                ORDER BY fr.review_sk
            """, (source_id,))
            rows = cur.fetchall()
    finally:
        conn.close()

    # Build DataFrame from cursor rows (dict-mode from psycopg)
    if rows and isinstance(rows[0], dict):
        df = pd.DataFrame(rows)
    else:
        df = pd.DataFrame(rows, columns=_COLUMNS)

    return df
