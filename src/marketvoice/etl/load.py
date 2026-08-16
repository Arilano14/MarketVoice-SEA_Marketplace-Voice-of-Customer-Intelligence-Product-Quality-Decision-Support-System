"""Load module — 3-transaction model (§11), full refresh (§17), pre-commit checks (§12).

Transaction model:
  TX-A: INSERT pipeline_run status=STARTED → COMMIT (survives TX-B rollback)
  TX-B: BEGIN → truncate dynamic tables → load dims → load facts
        → run ALL pre-commit critical checks → COMMIT or ROLLBACK
  TX-C: UPDATE pipeline_run status=SUCCESS|FAILED → COMMIT

§13: NEVER truncate audit tables (pipeline_run, rejected_record_log, data_quality_result).
§17: Idempotency via TRANSACTIONAL_DETERMINISTIC_FULL_REFRESH.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from ..database.connection import Connection
from ..database.schema import SCHEMA
from .transform import TransformResult, RejectedRow


# ─── Tables that get truncated each TX-B run ──────────────────────
TRUNCATABLE_TABLES = ["fact_review", "dim_shop", "dim_product", "dim_category"]
# Order matters: fact first (FK deps), then dims


class PreCommitCheckFailure(Exception):
    """§12 A pre-commit critical check failed → ROLLBACK required."""


def _resolve_source_sk(cur, source_id: str) -> int:
    """§14 Resolve source_sk by canonical source_id lookup. Never hardcode."""
    cur.execute(
        f"SELECT source_sk FROM {SCHEMA}.dim_source WHERE source_id = %s",
        (source_id,),
    )
    row = cur.fetchone()
    if row is None:
        raise ValueError(f"§14 source_id={source_id!r} not found in dim_source. Cannot resolve.")
    return row["source_sk"]


def _resolve_rating_sk(cur, rating_value: int) -> int:
    """Resolve rating_sk by rating_value lookup."""
    cur.execute(
        f"SELECT rating_sk FROM {SCHEMA}.dim_rating WHERE rating_value = %s",
        (rating_value,),
    )
    row = cur.fetchone()
    if row is None:
        raise ValueError(f"rating_value={rating_value} not found in dim_rating.")
    return row["rating_sk"]


def tx_a_start_pipeline_run(
    conn: Connection,
    pipeline_version: str,
    source_a_sha256: str,
    source_b_sha256: str,
    source_a_rows_manifest: int,
    source_b_rows_manifest: int,
    source_a_rows_read: int,
    source_b_rows_read: int,
) -> str:
    """TX-A: Insert pipeline_run with status=STARTED, then COMMIT.

    §11-A: pipeline_run must survive TX-B rollback.
    Returns: pipeline_run_id (UUID string).
    """
    run_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    with conn.cursor() as cur:
        cur.execute(f"""
            INSERT INTO {SCHEMA}.pipeline_run (
                pipeline_run_id, started_at, status, pipeline_version,
                source_a_file_sha256, source_b_file_sha256,
                source_a_rows_manifest, source_b_rows_manifest,
                source_a_rows_read, source_b_rows_read
            ) VALUES (
                %s, %s, 'STARTED', %s,
                %s, %s,
                %s, %s,
                %s, %s
            )
        """, (
            run_id, now, pipeline_version,
            source_a_sha256, source_b_sha256,
            source_a_rows_manifest, source_b_rows_manifest,
            source_a_rows_read, source_b_rows_read,
        ))
    # autocommit=True on conn means this commits immediately
    return run_id


def tx_b_warehouse_refresh(
    conn_txn: Connection,
    run_id: str,
    result: TransformResult,
) -> dict:
    """TX-B: Full warehouse refresh in a single transaction.

    Steps:
      1. Truncate dynamic tables (fact_review, dim_shop, dim_product, dim_category)
      2. Load dim_category
      3. Load dim_product
      4. Load dim_shop
      5. Load fact_review (with FK resolution)
      6. Run ALL pre-commit critical checks (§12)
      7. Return counts dict

    conn_txn MUST have autocommit=False. Caller handles COMMIT/ROLLBACK.

    Raises PreCommitCheckFailure if any §12 check fails.
    """
    counts = {
        "dim_category_loaded": 0,
        "dim_product_loaded": 0,
        "dim_shop_loaded": 0,
        "fact_review_loaded": 0,
        "fact_fk_rejected": 0,
    }

    cur = conn_txn.cursor()

    # ── Step 1: Truncate dynamic tables (§13: NEVER truncate audit tables) ──
    for tbl in TRUNCATABLE_TABLES:
        cur.execute(f"TRUNCATE TABLE {SCHEMA}.{tbl} CASCADE")

    # ── Step 2: Resolve source_sk lookups ──
    sk_a = _resolve_source_sk(cur, "SRC_PRDECT_ID_V1")
    sk_b = _resolve_source_sk(cur, "SRC_TOKOPEDIA_REVIEWS_2019")
    source_sk_map = {
        "SRC_PRDECT_ID_V1": sk_a,
        "SRC_TOKOPEDIA_REVIEWS_2019": sk_b,
    }

    # Pre-resolve rating_sk map
    rating_sk_map = {}
    for rv in range(1, 6):
        rating_sk_map[rv] = _resolve_rating_sk(cur, rv)

    # ── Step 3: Load dim_category ──
    cat_sk_map = {}  # (source_id, native_category) → category_sk
    for cat in result.categories:
        src_sk = source_sk_map[cat["source_id"]]
        cur.execute(f"""
            INSERT INTO {SCHEMA}.dim_category
                (source_sk, source_native_category, category_value_count_observations)
            VALUES (%s, %s, %s)
            RETURNING category_sk
        """, (src_sk, cat["source_native_category"], cat["count"]))
        row = cur.fetchone()
        cat_sk_map[(cat["source_id"], cat["source_native_category"])] = row["category_sk"]
        counts["dim_category_loaded"] += 1

    # ── Step 4: Load dim_product ──
    prod_sk_map = {}  # (source_id, native_product_id) → product_sk
    for prod in result.products:
        src_sk = source_sk_map[prod["source_id"]]
        cur.execute(f"""
            INSERT INTO {SCHEMA}.dim_product
                (source_sk, source_native_product_id,
                 source_native_product_name, product_name_variant_count)
            VALUES (%s, %s, %s, %s)
            RETURNING product_sk
        """, (
            src_sk,
            prod["source_native_product_id"],
            prod["source_native_product_name"],
            prod["product_name_variant_count"],
        ))
        row = cur.fetchone()
        prod_sk_map[(prod["source_id"], prod["source_native_product_id"])] = row["product_sk"]
        counts["dim_product_loaded"] += 1

    # ── Step 5: Load dim_shop ──
    shop_sk_map = {}  # (source_id, native_shop_id) → shop_sk
    for shop in result.shops:
        src_sk = source_sk_map[shop["source_id"]]
        cur.execute(f"""
            INSERT INTO {SCHEMA}.dim_shop
                (source_sk, source_native_shop_id, shop_observation_count)
            VALUES (%s, %s, %s)
            RETURNING shop_sk
        """, (
            src_sk,
            shop["source_native_shop_id"],
            shop["shop_observation_count"],
        ))
        row = cur.fetchone()
        shop_sk_map[(shop["source_id"], shop["source_native_shop_id"])] = row["shop_sk"]
        counts["dim_shop_loaded"] += 1

    # ── Step 6: Load fact_review ──
    fk_rejected: list[RejectedRow] = []

    for fact in result.fact_rows:
        src_id = fact["source_id"]
        src_sk = source_sk_map[src_id]
        rating_sk = rating_sk_map[fact["rating_value"]]

        # Resolve category_sk
        cat_key = (src_id, fact["source_native_category"])
        category_sk = cat_sk_map.get(cat_key)
        if category_sk is None:
            fk_rejected.append(RejectedRow(
                source_id=src_id,
                source_row_number=fact["source_row_number"],
                source_native_row_hash=fact["source_native_row_hash"],
                stage="FK_LOOKUP",
                severity="CRITICAL",
                dq_check_id="DQ-FK-CATEGORY-RESOLVE",
                reason_code="CATEGORY_FK_UNRESOLVED",
                reason_text=f"category={fact['source_native_category']!r} not in dim_category",
            ))
            counts["fact_fk_rejected"] += 1
            continue

        # §19 Source A: product_sk MUST BE NULL, shop_sk MUST BE NULL
        # §19 Source B: product_sk MUST resolve, shop_sk MUST resolve
        product_sk = None
        shop_sk = None

        if src_id == "SRC_PRDECT_ID_V1":
            # §15/§19: Source A → NULL, not fake unknown members
            product_sk = None
            shop_sk = None
        else:
            # Source B: must resolve
            pid = fact["product_lookup_id"]
            sid = fact["shop_lookup_id"]

            prod_key = (src_id, pid)
            product_sk = prod_sk_map.get(prod_key)
            if product_sk is None:
                fk_rejected.append(RejectedRow(
                    source_id=src_id,
                    source_row_number=fact["source_row_number"],
                    source_native_row_hash=fact["source_native_row_hash"],
                    stage="FK_LOOKUP",
                    severity="CRITICAL",
                    dq_check_id="DQ-FK-PRODUCT-RESOLVE",
                    reason_code="PRODUCT_FK_UNRESOLVED",
                    reason_text=f"product_id={pid!r} not in dim_product",
                ))
                counts["fact_fk_rejected"] += 1
                continue

            shop_key = (src_id, sid)
            shop_sk = shop_sk_map.get(shop_key)
            if shop_sk is None:
                fk_rejected.append(RejectedRow(
                    source_id=src_id,
                    source_row_number=fact["source_row_number"],
                    source_native_row_hash=fact["source_native_row_hash"],
                    stage="FK_LOOKUP",
                    severity="CRITICAL",
                    dq_check_id="DQ-FK-SHOP-RESOLVE",
                    reason_code="SHOP_FK_UNRESOLVED",
                    reason_text=f"shop_id={sid!r} not in dim_shop",
                ))
                counts["fact_fk_rejected"] += 1
                continue

        now_loaded = datetime.now(timezone.utc)

        cur.execute(f"""
            INSERT INTO {SCHEMA}.fact_review (
                source_sk, source_native_row_hash, source_row_number,
                source_file_sha256, rating_sk, rating_value,
                category_sk, product_sk, shop_sk,
                review_text, review_text_len_chars,
                source_gold_sentiment_label, source_gold_emotion_label,
                source_a_location_text, source_a_product_name_text,
                source_a_price_text, source_a_overall_rating_text,
                source_a_number_sold_text, source_a_total_review_text,
                source_b_product_name, source_b_sold_raw_text, source_b_product_url,
                is_synthetic, pipeline_run_id,
                ingested_at, processed_at, loaded_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s,
                %s, %s,
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s,
                %s, %s, %s
            )
        """, (
            src_sk, fact["source_native_row_hash"], fact["source_row_number"],
            fact["source_file_sha256"], rating_sk, fact["rating_value"],
            category_sk, product_sk, shop_sk,
            fact["review_text"], fact["review_text_len_chars"],
            fact["source_gold_sentiment_label"], fact["source_gold_emotion_label"],
            fact["source_a_location_text"], fact["source_a_product_name_text"],
            fact["source_a_price_text"], fact["source_a_overall_rating_text"],
            fact["source_a_number_sold_text"], fact["source_a_total_review_text"],
            fact["source_b_product_name"], fact["source_b_sold_raw_text"],
            fact["source_b_product_url"],
            fact["is_synthetic"], run_id,
            fact["ingested_at"], fact["processed_at"], now_loaded,
        ))
        counts["fact_review_loaded"] += 1

    # Store FK-rejected rows for audit logging
    counts["_fk_rejected_rows"] = fk_rejected

    # ── Step 7: Pre-commit critical checks (§12) ──
    checks = run_pre_commit_checks(cur, source_sk_map)
    counts["_pre_commit_checks"] = checks

    failed_checks = [c for c in checks if not c["passed"] and c["severity"] == "CRITICAL"]
    if failed_checks:
        summary = "; ".join(f"{c['check_id']}={c['actual']}" for c in failed_checks)
        raise PreCommitCheckFailure(
            f"§12 ROLLBACK: {len(failed_checks)} critical check(s) failed: {summary}"
        )

    cur.close()
    return counts


def run_pre_commit_checks(cur, source_sk_map: dict) -> list[dict]:
    """§12 Pre-commit critical checks. Run BEFORE COMMIT in TX-B.

    Each check returns: {check_id, severity, passed, actual, expected, evidence}
    """
    checks = []

    sk_a = source_sk_map.get("SRC_PRDECT_ID_V1")
    sk_b = source_sk_map.get("SRC_TOKOPEDIA_REVIEWS_2019")

    # 1. Source A product linkage count = 0
    cur.execute(f"""
        SELECT COUNT(*) c FROM {SCHEMA}.fact_review
        WHERE source_sk = %s AND product_sk IS NOT NULL
    """, (sk_a,))
    cnt = cur.fetchone()["c"]
    checks.append({
        "check_id": "DQ-PRE-SRC_A-PRODUCT-LINKAGE-ZERO",
        "severity": "CRITICAL",
        "passed": cnt == 0,
        "actual": str(cnt),
        "expected": "0",
        "evidence": "§12/§19: Source A product_sk must be NULL for all rows",
    })

    # 2. Source A shop linkage count = 0
    cur.execute(f"""
        SELECT COUNT(*) c FROM {SCHEMA}.fact_review
        WHERE source_sk = %s AND shop_sk IS NOT NULL
    """, (sk_a,))
    cnt = cur.fetchone()["c"]
    checks.append({
        "check_id": "DQ-PRE-SRC_A-SHOP-LINKAGE-ZERO",
        "severity": "CRITICAL",
        "passed": cnt == 0,
        "actual": str(cnt),
        "expected": "0",
        "evidence": "§12/§19: Source A shop_sk must be NULL for all rows",
    })

    # 3. Source B sentiment gold leakage = 0
    cur.execute(f"""
        SELECT COUNT(*) c FROM {SCHEMA}.fact_review
        WHERE source_sk = %s AND source_gold_sentiment_label IS NOT NULL
    """, (sk_b,))
    cnt = cur.fetchone()["c"]
    checks.append({
        "check_id": "DQ-PRE-SRC_B-SENTIMENT-LEAKAGE-ZERO",
        "severity": "CRITICAL",
        "passed": cnt == 0,
        "actual": str(cnt),
        "expected": "0",
        "evidence": "§6/§12: Source B has no gold sentiment labels",
    })

    # 4. Source B emotion gold leakage = 0
    cur.execute(f"""
        SELECT COUNT(*) c FROM {SCHEMA}.fact_review
        WHERE source_sk = %s AND source_gold_emotion_label IS NOT NULL
    """, (sk_b,))
    cnt = cur.fetchone()["c"]
    checks.append({
        "check_id": "DQ-PRE-SRC_B-EMOTION-LEAKAGE-ZERO",
        "severity": "CRITICAL",
        "passed": cnt == 0,
        "actual": str(cnt),
        "expected": "0",
        "evidence": "§6/§12: Source B has no gold emotion labels",
    })

    # 5. is_synthetic TRUE = 0
    cur.execute(f"""
        SELECT COUNT(*) c FROM {SCHEMA}.fact_review WHERE is_synthetic = TRUE
    """)
    cnt = cur.fetchone()["c"]
    checks.append({
        "check_id": "DQ-PRE-SYNTHETIC-ZERO",
        "severity": "CRITICAL",
        "passed": cnt == 0,
        "actual": str(cnt),
        "expected": "0",
        "evidence": "§9: Phase 6 is Track A only; all is_synthetic must be FALSE",
    })

    # 6. Invalid rating = 0
    cur.execute(f"""
        SELECT COUNT(*) c FROM {SCHEMA}.fact_review
        WHERE rating_value NOT BETWEEN 1 AND 5
    """)
    cnt = cur.fetchone()["c"]
    checks.append({
        "check_id": "DQ-PRE-INVALID-RATING-ZERO",
        "severity": "CRITICAL",
        "passed": cnt == 0,
        "actual": str(cnt),
        "expected": "0",
        "evidence": "§12: All fact rows must have rating 1-5",
    })

    # 7. FK orphan check — category
    cur.execute(f"""
        SELECT COUNT(*) c FROM {SCHEMA}.fact_review f
        LEFT JOIN {SCHEMA}.dim_category d ON f.category_sk = d.category_sk
        WHERE d.category_sk IS NULL
    """)
    cnt = cur.fetchone()["c"]
    checks.append({
        "check_id": "DQ-PRE-FK-ORPHAN-CATEGORY",
        "severity": "CRITICAL",
        "passed": cnt == 0,
        "actual": str(cnt),
        "expected": "0",
        "evidence": "§12: All fact_review.category_sk must resolve in dim_category",
    })

    # 8. FK orphan check — product (Source B only; Source A = NULL allowed)
    cur.execute(f"""
        SELECT COUNT(*) c FROM {SCHEMA}.fact_review f
        LEFT JOIN {SCHEMA}.dim_product d ON f.product_sk = d.product_sk
        WHERE f.product_sk IS NOT NULL AND d.product_sk IS NULL
    """)
    cnt = cur.fetchone()["c"]
    checks.append({
        "check_id": "DQ-PRE-FK-ORPHAN-PRODUCT",
        "severity": "CRITICAL",
        "passed": cnt == 0,
        "actual": str(cnt),
        "expected": "0",
        "evidence": "§12: Non-null product_sk must resolve in dim_product",
    })

    # 9. FK orphan check — shop (Source B only; Source A = NULL allowed)
    cur.execute(f"""
        SELECT COUNT(*) c FROM {SCHEMA}.fact_review f
        LEFT JOIN {SCHEMA}.dim_shop d ON f.shop_sk = d.shop_sk
        WHERE f.shop_sk IS NOT NULL AND d.shop_sk IS NULL
    """)
    cnt = cur.fetchone()["c"]
    checks.append({
        "check_id": "DQ-PRE-FK-ORPHAN-SHOP",
        "severity": "CRITICAL",
        "passed": cnt == 0,
        "actual": str(cnt),
        "expected": "0",
        "evidence": "§12: Non-null shop_sk must resolve in dim_shop",
    })

    # 10. Duplicate fact natural key = 0
    cur.execute(f"""
        SELECT COUNT(*) c FROM (
            SELECT source_sk, source_native_row_hash, COUNT(*) cnt
            FROM {SCHEMA}.fact_review
            GROUP BY source_sk, source_native_row_hash
            HAVING COUNT(*) > 1
        ) dups
    """)
    cnt = cur.fetchone()["c"]
    checks.append({
        "check_id": "DQ-PRE-DUPLICATE-NATURAL-KEY",
        "severity": "CRITICAL",
        "passed": cnt == 0,
        "actual": str(cnt),
        "expected": "0",
        "evidence": "§12/§17: No duplicate (source_sk, source_native_row_hash)",
    })

    # 11. Source-specific row reconciliation
    # Source A
    cur.execute(f"""
        SELECT COUNT(*) c FROM {SCHEMA}.fact_review WHERE source_sk = %s
    """, (sk_a,))
    src_a_loaded = cur.fetchone()["c"]

    cur.execute(f"""
        SELECT COUNT(*) c FROM {SCHEMA}.fact_review WHERE source_sk = %s
    """, (sk_b,))
    src_b_loaded = cur.fetchone()["c"]

    total_loaded = src_a_loaded + src_b_loaded
    cur.execute(f"SELECT COUNT(*) c FROM {SCHEMA}.fact_review")
    total_actual = cur.fetchone()["c"]

    checks.append({
        "check_id": "DQ-PRE-SOURCE-RECONCILIATION",
        "severity": "CRITICAL",
        "passed": total_loaded == total_actual,
        "actual": f"total={total_actual} (A={src_a_loaded}+B={src_b_loaded}={total_loaded})",
        "expected": f"sum_by_source == total",
        "evidence": "§12: Source-specific row reconciliation",
    })

    return checks


def log_rejected_records(
    conn: Connection,
    run_id: str,
    rejected_rows: list[RejectedRow],
) -> int:
    """Persist rejected rows to rejected_record_log. Audit table — append only (§13)."""
    if not rejected_rows:
        return 0
    with conn.cursor() as cur:
        for r in rejected_rows:
            cur.execute(f"""
                INSERT INTO {SCHEMA}.rejected_record_log (
                    pipeline_run_id, source_id, source_row_number,
                    source_native_row_hash, stage, severity,
                    dq_check_id, reason_code, reason_text, raw_row_snippet
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                run_id, r.source_id, r.source_row_number,
                r.source_native_row_hash, r.stage, r.severity,
                r.dq_check_id, r.reason_code, r.reason_text,
                r.raw_row_snippet,
            ))
    return len(rejected_rows)


def log_dq_results(
    conn: Connection,
    run_id: str,
    checks: list[dict],
) -> int:
    """Persist DQ check results to data_quality_result. §25 grain retained (§13)."""
    if not checks:
        return 0
    with conn.cursor() as cur:
        for c in checks:
            cur.execute(f"""
                INSERT INTO {SCHEMA}.data_quality_result (
                    pipeline_run_id, dq_check_id, severity,
                    passed, actual_value, expected_value, evidence
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                run_id, c["check_id"], c["severity"],
                c["passed"], c.get("actual"), c.get("expected"),
                c.get("evidence"),
            ))
    return len(checks)


def tx_c_finalize_pipeline_run(
    conn: Connection,
    run_id: str,
    status: str,
    accepted_total: int = 0,
    rejected_total: int = 0,
    loaded_total: int = 0,
    source_a_loaded: int = 0,
    source_b_loaded: int = 0,
    critical_dq_fails: int = 0,
    major_dq_fails: int = 0,
    notes: Optional[str] = None,
) -> None:
    """TX-C: Finalize pipeline_run with actual results (§11-C)."""
    now = datetime.now(timezone.utc)
    with conn.cursor() as cur:
        cur.execute(f"""
            UPDATE {SCHEMA}.pipeline_run SET
                completed_at = %s,
                status = %s,
                accepted_rows_total = %s,
                rejected_rows_total = %s,
                loaded_rows_total = %s,
                source_a_rows_loaded = %s,
                source_b_rows_loaded = %s,
                critical_dq_fails = %s,
                major_dq_fails = %s,
                notes = %s
            WHERE pipeline_run_id = %s
        """, (
            now, status,
            accepted_total, rejected_total, loaded_total,
            source_a_loaded, source_b_loaded,
            critical_dq_fails, major_dq_fails,
            notes, run_id,
        ))


__all__ = [
    "TRUNCATABLE_TABLES", "PreCommitCheckFailure",
    "tx_a_start_pipeline_run", "tx_b_warehouse_refresh",
    "run_pre_commit_checks", "log_rejected_records",
    "log_dq_results", "tx_c_finalize_pipeline_run",
]
