"""Transform module — row validation, dimension mapping, fact preparation.

Key rules enforced:
  §6  — locked data reality (no cross-source linkage, no fake timestamps)
  §9  — Track A only; is_synthetic = FALSE for every row
  §14 — source_sk resolved by dim_source.source_id lookup, never hardcoded
  §15 — no fake unknown members; Source A product_sk/shop_sk = NULL
  §16 — source_native_row_hash = SHA256(source_id|source_file_sha256|row_number)
  §19 — Source B FK must resolve; Source A product_sk/shop_sk MUST be NULL
  §20 — product name variant: most frequent, tie→lowest row_number
"""
from __future__ import annotations

import hashlib
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


# ─── Constants ────────────────────────────────────────────────────
VALID_SENTIMENTS = {"Positive", "Negative"}
VALID_EMOTIONS = {"Happy", "Sadness", "Fear", "Love", "Anger"}
VALID_RATINGS = {1, 2, 3, 4, 5}


@dataclass
class RejectedRow:
    """A row rejected during transformation."""
    source_id: str
    source_row_number: int
    source_native_row_hash: Optional[str]
    stage: str
    severity: str
    dq_check_id: str
    reason_code: str
    reason_text: str
    raw_row_snippet: Optional[str] = None


@dataclass
class TransformResult:
    """Output of the transform phase."""
    # Dimension data
    categories: list[dict]           # [{source_id, source_native_category, count}]
    products: list[dict]             # [{source_id, source_native_product_id, name, variant_count}]
    shops: list[dict]                # [{source_id, source_native_shop_id, observation_count}]

    # Fact rows ready for load
    fact_rows: list[dict]

    # Rejected rows
    rejected: list[RejectedRow] = field(default_factory=list)

    # Counts
    source_a_accepted: int = 0
    source_b_accepted: int = 0
    source_a_rejected: int = 0
    source_b_rejected: int = 0


def _compute_row_hash(source_id: str, source_file_sha256: str, row_number: int) -> str:
    """§16 deterministic lineage hash. WAREHOUSE_INTERNAL, NOT_LINKABLE."""
    raw = f"{source_id}|{source_file_sha256}|{row_number}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _snippet(row: dict, max_len: int = 200) -> str:
    """Create a truncated text snippet for rejected_record_log."""
    txt = str({k: v for k, v in row.items() if not k.startswith("_")})
    return txt[:max_len] if len(txt) > max_len else txt


def _validate_rating_a(row: dict) -> Optional[int]:
    """Parse Source A 'Customer Rating' to int 1-5 or None."""
    raw = row.get("Customer Rating", "")
    if raw is None:
        return None
    try:
        val = int(str(raw).strip())
        if val in VALID_RATINGS:
            return val
    except (ValueError, TypeError):
        pass
    return None


def _validate_rating_b(row: dict) -> Optional[int]:
    """Parse Source B 'rating' to int 1-5 or None."""
    raw = row.get("rating", "")
    if raw is None:
        return None
    try:
        val = int(str(raw).strip())
        if val in VALID_RATINGS:
            return val
    except (ValueError, TypeError):
        pass
    return None


def _validate_sentiment(row: dict) -> Optional[str]:
    """Source A gold sentiment: Positive/Negative or NULL."""
    raw = row.get("Sentiment", "")
    if raw and str(raw).strip() in VALID_SENTIMENTS:
        return str(raw).strip()
    return None


def _validate_emotion(row: dict) -> Optional[str]:
    """Source A gold emotion: 5-class or NULL."""
    raw = row.get("Emotion", "")
    if raw and str(raw).strip() in VALID_EMOTIONS:
        return str(raw).strip()
    return None


def _build_source_b_dimensions(rows_b: list[dict]) -> tuple[dict, dict, dict]:
    """Build product & shop dimension lookups from Source B.

    §20 Product name variant rule:
      For each product_id → collect non-null product_name values
      → choose most frequent → if tied, choose value at lowest stable source_row_number
      → store variant_count

    Returns: (categories, products, shops) as dicts keyed by native id.
      categories = {native_category: observation_count}
      products = {native_product_id: {name, variant_count}}
      shops = {native_shop_id: observation_count}
    """
    # Categories
    cat_counter: dict[str, int] = Counter()

    # Products: collect name occurrences per product_id
    product_names: dict[str, list[tuple[str, int]]] = defaultdict(list)
    # (name, row_number) for tie breaking

    # Shops
    shop_counter: dict[str, int] = Counter()

    for row in rows_b:
        cat = str(row.get("category", "") or "").strip()
        if cat:
            cat_counter[cat] += 1

        pid = str(row.get("product_id", "") or "").strip()
        pname = row.get("product_name")
        if pid:
            if pname and str(pname).strip():
                product_names[pid].append(
                    (str(pname).strip(), row["_source_row_number"])
                )
            else:
                # Ensure product_id is tracked even with null name
                if pid not in product_names:
                    product_names[pid] = []

        sid = str(row.get("shop_id", "") or "").strip()
        if sid:
            shop_counter[sid] += 1

    # §20 resolve product names
    products = {}
    for pid, name_rows in product_names.items():
        if not name_rows:
            products[pid] = {"name": None, "variant_count": 1}
            continue
        # Count frequencies
        freq: dict[str, int] = Counter()
        first_row: dict[str, int] = {}
        for name, rn in name_rows:
            freq[name] += 1
            if name not in first_row or rn < first_row[name]:
                first_row[name] = rn
        max_freq = max(freq.values())
        candidates = [n for n, c in freq.items() if c == max_freq]
        if len(candidates) == 1:
            chosen_name = candidates[0]
        else:
            # tie: choose value at lowest stable source_row_number
            chosen_name = min(candidates, key=lambda n: first_row[n])
        products[pid] = {
            "name": chosen_name,
            "variant_count": len(freq),  # distinct name count
        }

    shops = dict(shop_counter)

    return dict(cat_counter), products, shops


def transform(
    source_a_rows: list[dict],
    source_b_rows: list[dict],
    source_a_sha256: str,
    source_b_sha256: str,
) -> TransformResult:
    """Full transform pass over both sources.

    Steps:
      1. Build Source B dimensions (categories, products, shops)
      2. Build Source A categories
      3. Validate & prepare fact rows for both sources
      4. Reject invalid rows (bad rating, empty review, etc.)

    Returns TransformResult with dimension data, fact rows, and rejected rows.
    """
    now = datetime.now(timezone.utc)
    rejected: list[RejectedRow] = []

    # ── Build dimensions from Source B ──
    b_categories, b_products, b_shops = _build_source_b_dimensions(source_b_rows)

    # ── Build categories from Source A ──
    a_categories: dict[str, int] = Counter()
    for row in source_a_rows:
        cat = str(row.get("Category", "") or "").strip()
        if cat:
            a_categories[cat] += 1

    # ── Prepare dimension output lists ──
    # Categories: one entry per (source_id, native_category)
    categories_out = []
    for cat, cnt in a_categories.items():
        categories_out.append({
            "source_id": "SRC_PRDECT_ID_V1",
            "source_native_category": cat,
            "count": cnt,
        })
    for cat, cnt in b_categories.items():
        categories_out.append({
            "source_id": "SRC_TOKOPEDIA_REVIEWS_2019",
            "source_native_category": cat,
            "count": cnt,
        })

    products_out = []
    for pid, info in b_products.items():
        products_out.append({
            "source_id": "SRC_TOKOPEDIA_REVIEWS_2019",
            "source_native_product_id": pid,
            "source_native_product_name": info["name"],
            "product_name_variant_count": max(info["variant_count"], 1),
        })

    shops_out = []
    for sid, cnt in b_shops.items():
        shops_out.append({
            "source_id": "SRC_TOKOPEDIA_REVIEWS_2019",
            "source_native_shop_id": sid,
            "shop_observation_count": cnt,
        })

    # ── Process Source A fact rows ──
    fact_rows = []
    a_accepted = 0
    a_rejected = 0

    for row in source_a_rows:
        row_num = row["_source_row_number"]
        row_hash = _compute_row_hash("SRC_PRDECT_ID_V1", source_a_sha256, row_num)

        # Validate rating (§18 CRITICAL → reject)
        rating = _validate_rating_a(row)
        if rating is None:
            rejected.append(RejectedRow(
                source_id="SRC_PRDECT_ID_V1",
                source_row_number=row_num,
                source_native_row_hash=row_hash,
                stage="TRANSFORM",
                severity="CRITICAL",
                dq_check_id="DQ-RATING-VALID",
                reason_code="INVALID_RATING",
                reason_text=f"Customer Rating={row.get('Customer Rating')!r} not in 1-5",
                raw_row_snippet=_snippet(row),
            ))
            a_rejected += 1
            continue

        # Validate review text
        review_text = str(row.get("Customer Review", "") or "").strip()
        if not review_text:
            rejected.append(RejectedRow(
                source_id="SRC_PRDECT_ID_V1",
                source_row_number=row_num,
                source_native_row_hash=row_hash,
                stage="TRANSFORM",
                severity="MAJOR",
                dq_check_id="DQ-REVIEW-TEXT-NONEMPTY",
                reason_code="EMPTY_REVIEW_TEXT",
                reason_text="Customer Review is empty/null",
                raw_row_snippet=_snippet(row),
            ))
            a_rejected += 1
            continue

        # Validate category
        category = str(row.get("Category", "") or "").strip()
        if not category:
            rejected.append(RejectedRow(
                source_id="SRC_PRDECT_ID_V1",
                source_row_number=row_num,
                source_native_row_hash=row_hash,
                stage="TRANSFORM",
                severity="MAJOR",
                dq_check_id="DQ-CATEGORY-NONEMPTY",
                reason_code="EMPTY_CATEGORY",
                reason_text="Category is empty/null",
                raw_row_snippet=_snippet(row),
            ))
            a_rejected += 1
            continue

        sentiment = _validate_sentiment(row)
        emotion = _validate_emotion(row)

        fact_rows.append({
            "source_id": "SRC_PRDECT_ID_V1",
            "source_native_row_hash": row_hash,
            "source_row_number": row_num,
            "source_file_sha256": source_a_sha256,
            "rating_value": rating,
            "source_native_category": category,
            # §19/§15: Source A product_sk = NULL, shop_sk = NULL
            "product_lookup_id": None,
            "shop_lookup_id": None,
            "review_text": review_text,
            "review_text_len_chars": len(review_text),
            "source_gold_sentiment_label": sentiment,
            "source_gold_emotion_label": emotion,
            # Source A specific passthrough fields
            "source_a_location_text": str(row.get("Location", "") or "").strip() or None,
            "source_a_product_name_text": str(row.get("Product Name", "") or "").strip() or None,
            "source_a_price_text": str(row.get("Price", "") or "").strip() or None,
            "source_a_overall_rating_text": str(row.get("Overall Rating", "") or "").strip() or None,
            "source_a_number_sold_text": str(row.get("Number Sold", "") or "").strip() or None,
            "source_a_total_review_text": str(row.get("Total Review", "") or "").strip() or None,
            # Source B specific fields NULL for Source A
            "source_b_product_name": None,
            "source_b_sold_raw_text": None,
            "source_b_product_url": None,
            # §9 Track A only
            "is_synthetic": False,
            # Technical metadata timestamps
            "ingested_at": now,
            "processed_at": now,
        })
        a_accepted += 1

    # ── Process Source B fact rows ──
    b_accepted = 0
    b_rejected = 0

    for row in source_b_rows:
        row_num = row["_source_row_number"]
        row_hash = _compute_row_hash("SRC_TOKOPEDIA_REVIEWS_2019", source_b_sha256, row_num)

        # Validate rating
        rating = _validate_rating_b(row)
        if rating is None:
            rejected.append(RejectedRow(
                source_id="SRC_TOKOPEDIA_REVIEWS_2019",
                source_row_number=row_num,
                source_native_row_hash=row_hash,
                stage="TRANSFORM",
                severity="CRITICAL",
                dq_check_id="DQ-RATING-VALID",
                reason_code="INVALID_RATING",
                reason_text=f"rating={row.get('rating')!r} not in 1-5",
                raw_row_snippet=_snippet(row),
            ))
            b_rejected += 1
            continue

        # Validate review text
        review_text = str(row.get("text", "") or "").strip()
        if not review_text:
            rejected.append(RejectedRow(
                source_id="SRC_TOKOPEDIA_REVIEWS_2019",
                source_row_number=row_num,
                source_native_row_hash=row_hash,
                stage="TRANSFORM",
                severity="MAJOR",
                dq_check_id="DQ-REVIEW-TEXT-NONEMPTY",
                reason_code="EMPTY_REVIEW_TEXT",
                reason_text="text is empty/null",
                raw_row_snippet=_snippet(row),
            ))
            b_rejected += 1
            continue

        # Validate category
        category = str(row.get("category", "") or "").strip()
        if not category:
            rejected.append(RejectedRow(
                source_id="SRC_TOKOPEDIA_REVIEWS_2019",
                source_row_number=row_num,
                source_native_row_hash=row_hash,
                stage="TRANSFORM",
                severity="MAJOR",
                dq_check_id="DQ-CATEGORY-NONEMPTY",
                reason_code="EMPTY_CATEGORY",
                reason_text="category is empty/null",
                raw_row_snippet=_snippet(row),
            ))
            b_rejected += 1
            continue

        # §19 Source B: product_id and shop_id MUST be valid for FK resolution
        pid = str(row.get("product_id", "") or "").strip()
        sid = str(row.get("shop_id", "") or "").strip()

        if not pid:
            rejected.append(RejectedRow(
                source_id="SRC_TOKOPEDIA_REVIEWS_2019",
                source_row_number=row_num,
                source_native_row_hash=row_hash,
                stage="FK_LOOKUP",
                severity="CRITICAL",
                dq_check_id="DQ-FK-PRODUCT-RESOLVE",
                reason_code="MISSING_PRODUCT_ID",
                reason_text="product_id is empty/null; §19 FK must resolve",
                raw_row_snippet=_snippet(row),
            ))
            b_rejected += 1
            continue

        if not sid:
            rejected.append(RejectedRow(
                source_id="SRC_TOKOPEDIA_REVIEWS_2019",
                source_row_number=row_num,
                source_native_row_hash=row_hash,
                stage="FK_LOOKUP",
                severity="CRITICAL",
                dq_check_id="DQ-FK-SHOP-RESOLVE",
                reason_code="MISSING_SHOP_ID",
                reason_text="shop_id is empty/null; §19 FK must resolve",
                raw_row_snippet=_snippet(row),
            ))
            b_rejected += 1
            continue

        # Source B: no gold sentiment/emotion (§6)
        fact_rows.append({
            "source_id": "SRC_TOKOPEDIA_REVIEWS_2019",
            "source_native_row_hash": row_hash,
            "source_row_number": row_num,
            "source_file_sha256": source_b_sha256,
            "rating_value": rating,
            "source_native_category": category,
            "product_lookup_id": pid,
            "shop_lookup_id": sid,
            "review_text": review_text,
            "review_text_len_chars": len(review_text),
            "source_gold_sentiment_label": None,   # §6 NOT_AVAILABLE
            "source_gold_emotion_label": None,      # §6 NOT_AVAILABLE
            # Source A specific fields NULL for Source B
            "source_a_location_text": None,
            "source_a_product_name_text": None,
            "source_a_price_text": None,
            "source_a_overall_rating_text": None,
            "source_a_number_sold_text": None,
            "source_a_total_review_text": None,
            # Source B specific passthrough
            "source_b_product_name": str(row.get("product_name", "") or "").strip() or None,
            "source_b_sold_raw_text": str(row.get("sold", "") or "").strip() or None,
            "source_b_product_url": str(row.get("product_url", "") or "").strip() or None,
            # §9 Track A only
            "is_synthetic": False,
            "ingested_at": now,
            "processed_at": now,
        })
        b_accepted += 1

    return TransformResult(
        categories=categories_out,
        products=products_out,
        shops=shops_out,
        fact_rows=fact_rows,
        rejected=rejected,
        source_a_accepted=a_accepted,
        source_b_accepted=b_accepted,
        source_a_rejected=a_rejected,
        source_b_rejected=b_rejected,
    )


__all__ = [
    "VALID_SENTIMENTS", "VALID_EMOTIONS", "VALID_RATINGS",
    "RejectedRow", "TransformResult",
    "transform",
]
