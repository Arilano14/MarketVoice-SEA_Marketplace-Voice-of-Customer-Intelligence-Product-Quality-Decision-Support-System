"""Post-load forensic verification (§32 evidence checks).

These run AFTER a successful commit. They are forensic verification only.
They CANNOT rollback an already committed transaction (§12 note).
"""
from __future__ import annotations

from ..database.connection import Connection
from ..database.schema import SCHEMA


def run_post_load_checks(conn: Connection, run_id: str) -> list[dict]:
    """Run forensic post-load verification queries.

    Returns list of check dicts: {check_id, severity, passed, actual, expected, evidence}
    """
    checks = []
    cur = conn.cursor()

    # 1. Total fact count > 0
    cur.execute(f"SELECT COUNT(*) c FROM {SCHEMA}.fact_review WHERE pipeline_run_id = %s", (run_id,))
    cnt = cur.fetchone()["c"]
    checks.append({
        "check_id": "DQ-POST-FACT-COUNT-POSITIVE",
        "severity": "CRITICAL",
        "passed": cnt > 0,
        "actual": str(cnt),
        "expected": ">0",
        "evidence": "At least one fact row must be loaded",
    })

    # 2. dim_source = 2 rows (conformed master)
    cur.execute(f"SELECT COUNT(*) c FROM {SCHEMA}.dim_source")
    cnt = cur.fetchone()["c"]
    checks.append({
        "check_id": "DQ-POST-DIM-SOURCE-COUNT",
        "severity": "CRITICAL",
        "passed": cnt == 2,
        "actual": str(cnt),
        "expected": "2",
        "evidence": "Exactly 2 registered sources in dim_source",
    })

    # 3. dim_rating = 5 rows
    cur.execute(f"SELECT COUNT(*) c FROM {SCHEMA}.dim_rating")
    cnt = cur.fetchone()["c"]
    checks.append({
        "check_id": "DQ-POST-DIM-RATING-COUNT",
        "severity": "CRITICAL",
        "passed": cnt == 5,
        "actual": str(cnt),
        "expected": "5",
        "evidence": "Exactly 5 rating rows (1-5) in dim_rating",
    })

    # 4. Cross-source isolation: Source A has NO product/shop links
    cur.execute(f"""
        SELECT ds.source_id, COUNT(*) c
        FROM {SCHEMA}.fact_review fr
        JOIN {SCHEMA}.dim_source ds ON fr.source_sk = ds.source_sk
        WHERE ds.source_id = 'SRC_PRDECT_ID_V1'
          AND (fr.product_sk IS NOT NULL OR fr.shop_sk IS NOT NULL)
        GROUP BY ds.source_id
    """)
    row = cur.fetchone()
    cnt = row["c"] if row else 0
    checks.append({
        "check_id": "DQ-POST-CROSS-SOURCE-ISOLATION",
        "severity": "CRITICAL",
        "passed": cnt == 0,
        "actual": str(cnt),
        "expected": "0",
        "evidence": "§6: Source A must have NULL product_sk and NULL shop_sk",
    })

    # 5. No synthetic rows
    cur.execute(f"SELECT COUNT(*) c FROM {SCHEMA}.fact_review WHERE is_synthetic = TRUE")
    cnt = cur.fetchone()["c"]
    checks.append({
        "check_id": "DQ-POST-SYNTHETIC-ZERO",
        "severity": "CRITICAL",
        "passed": cnt == 0,
        "actual": str(cnt),
        "expected": "0",
        "evidence": "§9: No synthetic rows allowed in Phase 6",
    })

    # 6. Timestamp ordering forensic
    cur.execute(f"""
        SELECT COUNT(*) c FROM {SCHEMA}.fact_review
        WHERE NOT (ingested_at <= processed_at AND processed_at <= loaded_at)
    """)
    cnt = cur.fetchone()["c"]
    checks.append({
        "check_id": "DQ-POST-TIMESTAMP-ORDERING",
        "severity": "CRITICAL",
        "passed": cnt == 0,
        "actual": str(cnt),
        "expected": "0",
        "evidence": "Technical metadata timestamps must satisfy ingested_at <= processed_at <= loaded_at",
    })

    # 7. Source B: all product_sk NOT NULL
    cur.execute(f"""
        SELECT COUNT(*) c FROM {SCHEMA}.fact_review fr
        JOIN {SCHEMA}.dim_source ds ON fr.source_sk = ds.source_sk
        WHERE ds.source_id = 'SRC_TOKOPEDIA_REVIEWS_2019' AND fr.product_sk IS NULL
    """)
    cnt = cur.fetchone()["c"]
    checks.append({
        "check_id": "DQ-POST-SRC-B-PRODUCT-NONNULL",
        "severity": "CRITICAL",
        "passed": cnt == 0,
        "actual": str(cnt),
        "expected": "0",
        "evidence": "§19: Source B product_sk must resolve (non-NULL)",
    })

    # 8. Source B: all shop_sk NOT NULL
    cur.execute(f"""
        SELECT COUNT(*) c FROM {SCHEMA}.fact_review fr
        JOIN {SCHEMA}.dim_source ds ON fr.source_sk = ds.source_sk
        WHERE ds.source_id = 'SRC_TOKOPEDIA_REVIEWS_2019' AND fr.shop_sk IS NULL
    """)
    cnt = cur.fetchone()["c"]
    checks.append({
        "check_id": "DQ-POST-SRC-B-SHOP-NONNULL",
        "severity": "CRITICAL",
        "passed": cnt == 0,
        "actual": str(cnt),
        "expected": "0",
        "evidence": "§19: Source B shop_sk must resolve (non-NULL)",
    })

    # 9. Source B: no gold sentiment leakage
    cur.execute(f"""
        SELECT COUNT(*) c FROM {SCHEMA}.fact_review fr
        JOIN {SCHEMA}.dim_source ds ON fr.source_sk = ds.source_sk
        WHERE ds.source_id = 'SRC_TOKOPEDIA_REVIEWS_2019'
          AND fr.source_gold_sentiment_label IS NOT NULL
    """)
    cnt = cur.fetchone()["c"]
    checks.append({
        "check_id": "DQ-POST-SRC-B-SENTIMENT-LEAKAGE",
        "severity": "CRITICAL",
        "passed": cnt == 0,
        "actual": str(cnt),
        "expected": "0",
        "evidence": "§6: Source B has no gold sentiment labels",
    })

    # 10. Source B: no gold emotion leakage
    cur.execute(f"""
        SELECT COUNT(*) c FROM {SCHEMA}.fact_review fr
        JOIN {SCHEMA}.dim_source ds ON fr.source_sk = ds.source_sk
        WHERE ds.source_id = 'SRC_TOKOPEDIA_REVIEWS_2019'
          AND fr.source_gold_emotion_label IS NOT NULL
    """)
    cnt = cur.fetchone()["c"]
    checks.append({
        "check_id": "DQ-POST-SRC-B-EMOTION-LEAKAGE",
        "severity": "CRITICAL",
        "passed": cnt == 0,
        "actual": str(cnt),
        "expected": "0",
        "evidence": "§6: Source B has no gold emotion labels",
    })

    # 11. Rating value distribution check
    cur.execute(f"""
        SELECT rating_value, COUNT(*) c
        FROM {SCHEMA}.fact_review
        GROUP BY rating_value
        ORDER BY rating_value
    """)
    rows = cur.fetchall()
    rating_dist = {r["rating_value"]: r["c"] for r in rows}
    all_valid = all(rv in {1, 2, 3, 4, 5} for rv in rating_dist.keys())
    checks.append({
        "check_id": "DQ-POST-RATING-DISTRIBUTION",
        "severity": "INFO",
        "passed": all_valid,
        "actual": str(rating_dist),
        "expected": "all keys in {1,2,3,4,5}",
        "evidence": "Rating distribution across all loaded facts",
    })

    # 12. Pipeline run finalization check
    cur.execute(f"""
        SELECT status, completed_at FROM {SCHEMA}.pipeline_run
        WHERE pipeline_run_id = %s
    """, (run_id,))
    pr = cur.fetchone()
    checks.append({
        "check_id": "DQ-POST-PIPELINE-RUN-FINALIZED",
        "severity": "CRITICAL",
        "passed": pr is not None and pr["status"] in ("SUCCESS", "FAILED") and pr["completed_at"] is not None,
        "actual": f"status={pr['status'] if pr else 'MISSING'} completed={pr['completed_at'] if pr else 'N/A'}",
        "expected": "status in (SUCCESS,FAILED) and completed_at IS NOT NULL",
        "evidence": "Pipeline run must be finalized after TX-C",
    })

    cur.close()
    return checks


__all__ = ["run_post_load_checks"]
