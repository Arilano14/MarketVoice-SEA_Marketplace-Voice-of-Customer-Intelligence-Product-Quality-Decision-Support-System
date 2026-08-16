"""Pipeline orchestrator — full ETL run (steps 6.7–6.11 combined).

Lifecycle:
  1. SHA256 pre-ETL verify (§26)
  2. Extract both sources (§21 strict UTF-8)
  3. Transform (validate, build dims, prepare facts)
  4. TX-A: register pipeline_run STARTED
  5. TX-B: full warehouse refresh + pre-commit checks
  6. Log rejected records + DQ results (audit tables)
  7. TX-C: finalize pipeline_run SUCCESS/FAILED
  8. SHA256 post-ETL verify (§26)
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from typing import Optional

# Ensure .pipdeps is on path for psycopg
_PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)
_PIPDEPS = os.path.join(_PROJECT_ROOT, ".pipdeps")
if os.path.isdir(_PIPDEPS) and _PIPDEPS not in sys.path:
    sys.path.insert(0, _PIPDEPS)

from ..database.connection import (
    DBSettings, connect, ensure_database_exists, get_marketvoice_env,
)
from ..database.schema import (
    SCHEMA, apply_ddl, verify_9_tables_exactly, verify_seed_counts,
)
from .extract import (
    SOURCE_A, SOURCE_B, extract_all, verify_sha256,
    SHA256Mismatch, compute_sha256,
)
from .transform import transform, TransformResult
from .load import (
    tx_a_start_pipeline_run, tx_b_warehouse_refresh,
    log_rejected_records, log_dq_results,
    tx_c_finalize_pipeline_run, PreCommitCheckFailure,
)

import psycopg

PIPELINE_VERSION = "6.0.1"


class PipelineResult:
    """Structured result of a pipeline run."""

    def __init__(self):
        self.run_id: Optional[str] = None
        self.status: str = "NOT_STARTED"
        self.sha256_pre_a: Optional[str] = None
        self.sha256_pre_b: Optional[str] = None
        self.sha256_post_a: Optional[str] = None
        self.sha256_post_b: Optional[str] = None
        self.source_a_rows_read: int = 0
        self.source_b_rows_read: int = 0
        self.source_a_accepted: int = 0
        self.source_b_accepted: int = 0
        self.source_a_rejected: int = 0
        self.source_b_rejected: int = 0
        self.total_accepted: int = 0
        self.total_rejected: int = 0
        self.total_loaded: int = 0
        self.dim_category_count: int = 0
        self.dim_product_count: int = 0
        self.dim_shop_count: int = 0
        self.fact_fk_rejected: int = 0
        self.pre_commit_checks: list[dict] = []
        self.post_load_checks: list[dict] = []
        self.critical_fails: int = 0
        self.major_fails: int = 0
        self.errors: list[str] = []
        self.raw_data_mutated: bool = False
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

    def summary(self) -> str:
        lines = [
            f"Pipeline Run: {self.run_id}",
            f"Status: {self.status}",
            f"Started: {self.started_at}",
            f"Completed: {self.completed_at}",
            f"",
            f"SHA256 Pre  A: {self.sha256_pre_a}",
            f"SHA256 Pre  B: {self.sha256_pre_b}",
            f"SHA256 Post A: {self.sha256_post_a}",
            f"SHA256 Post B: {self.sha256_post_b}",
            f"Raw Data Mutated: {self.raw_data_mutated}",
            f"",
            f"Source A: read={self.source_a_rows_read} accepted={self.source_a_accepted} rejected={self.source_a_rejected}",
            f"Source B: read={self.source_b_rows_read} accepted={self.source_b_accepted} rejected={self.source_b_rejected}",
            f"Total: accepted={self.total_accepted} rejected={self.total_rejected} loaded={self.total_loaded} fk_rejected={self.fact_fk_rejected}",
            f"",
            f"Dimensions: categories={self.dim_category_count} products={self.dim_product_count} shops={self.dim_shop_count}",
            f"",
            f"Pre-commit checks: {len(self.pre_commit_checks)} run, {self.critical_fails} critical fails",
        ]
        for c in self.pre_commit_checks:
            status = "PASS" if c["passed"] else "FAIL"
            lines.append(f"  [{status}] {c['check_id']}: actual={c['actual']} expected={c['expected']}")
        if self.errors:
            lines.append(f"\nErrors:")
            for e in self.errors:
                lines.append(f"  - {e}")
        return "\n".join(lines)


def run_pipeline(
    project_root: Optional[str] = None,
    target_db: Optional[str] = None,
    ensure_schema: bool = True,
) -> PipelineResult:
    """Execute the full ETL pipeline.

    Args:
        project_root: Path to project root. Defaults to auto-detect.
        target_db: Override target database name.
        ensure_schema: If True, ensure DB exists and apply DDL before ETL.
    """
    project_root = project_root or _PROJECT_ROOT
    result = PipelineResult()
    result.started_at = datetime.now(timezone.utc)

    settings = DBSettings.from_env()
    env = get_marketvoice_env()
    dbname = target_db or settings.target_dbname(env)

    print(f"[PIPELINE] MARKETVOICE_ENV={env} target_db={dbname}")
    print(f"[PIPELINE] version={PIPELINE_VERSION}")

    # ── Step 1: SHA256 pre-ETL verify (§26) ──
    try:
        result.sha256_pre_a = verify_sha256(SOURCE_A, project_root)
        result.sha256_pre_b = verify_sha256(SOURCE_B, project_root)
        print(f"[PIPELINE] §26 SHA256 pre-ETL verified OK")
    except SHA256Mismatch as e:
        result.status = "FAILED"
        result.errors.append(str(e))
        print(f"[PIPELINE] §26 CRITICAL: {e}")
        result.completed_at = datetime.now(timezone.utc)
        return result

    # ── Step 2: Ensure DB + schema ──
    if ensure_schema:
        ensure_database_exists(settings, dbname=dbname)
        conn_setup = connect(settings, dbname_override=dbname)
        apply_ddl(conn_setup, reset_schema=True)
        ok, missing, extras = verify_9_tables_exactly(conn_setup)
        if not ok:
            result.status = "FAILED"
            result.errors.append(f"DDL verify failed: missing={missing} extras={extras}")
            conn_setup.close()
            result.completed_at = datetime.now(timezone.utc)
            return result
        conn_setup.close()

    # ── Step 3: Extract ──
    print(f"[PIPELINE] Extracting sources...")
    extracted = extract_all(project_root)
    result.source_a_rows_read = extracted["source_a_row_count"]
    result.source_b_rows_read = extracted["source_b_row_count"]
    print(f"[PIPELINE] Extracted: A={result.source_a_rows_read} B={result.source_b_rows_read}")

    # ── Step 4: Transform ──
    print(f"[PIPELINE] Transforming...")
    tx_result = transform(
        extracted["source_a_rows"],
        extracted["source_b_rows"],
        extracted["source_a_sha256"],
        extracted["source_b_sha256"],
    )
    result.source_a_accepted = tx_result.source_a_accepted
    result.source_b_accepted = tx_result.source_b_accepted
    result.source_a_rejected = tx_result.source_a_rejected
    result.source_b_rejected = tx_result.source_b_rejected
    result.total_accepted = tx_result.source_a_accepted + tx_result.source_b_accepted
    result.total_rejected = tx_result.source_a_rejected + tx_result.source_b_rejected
    result.dim_category_count = len(tx_result.categories)
    result.dim_product_count = len(tx_result.products)
    result.dim_shop_count = len(tx_result.shops)
    print(f"[PIPELINE] Transform complete: accepted={result.total_accepted} rejected={result.total_rejected}")
    print(f"[PIPELINE] Dims: cat={result.dim_category_count} prod={result.dim_product_count} shop={result.dim_shop_count}")

    # ── Step 5: TX-A — register pipeline_run (§11-A) ──
    conn_audit = connect(settings, dbname_override=dbname)  # autocommit=True
    result.run_id = tx_a_start_pipeline_run(
        conn_audit,
        pipeline_version=PIPELINE_VERSION,
        source_a_sha256=result.sha256_pre_a,
        source_b_sha256=result.sha256_pre_b,
        source_a_rows_manifest=SOURCE_A.expected_row_count,
        source_b_rows_manifest=SOURCE_B.expected_row_count,
        source_a_rows_read=result.source_a_rows_read,
        source_b_rows_read=result.source_b_rows_read,
    )
    print(f"[PIPELINE] TX-A: pipeline_run {result.run_id} STARTED")

    # Log transform-phase rejected rows (into audit table, survives TX-B)
    all_rejected = list(tx_result.rejected)
    log_rejected_records(conn_audit, result.run_id, all_rejected)
    print(f"[PIPELINE] Logged {len(all_rejected)} transform-phase rejections")

    # ── Step 6: TX-B — warehouse refresh (§11-B) ──
    conn_txn = psycopg.connect(
        host=settings.host,
        port=settings.port,
        dbname=dbname,
        user=settings.user,
        password=settings.password,
        autocommit=False,
        row_factory=psycopg.rows.dict_row,
    )

    try:
        print(f"[PIPELINE] TX-B: BEGIN warehouse refresh")
        load_counts = tx_b_warehouse_refresh(conn_txn, result.run_id, tx_result)

        result.total_loaded = load_counts["fact_review_loaded"]
        result.fact_fk_rejected = load_counts["fact_fk_rejected"]
        result.pre_commit_checks = load_counts.get("_pre_commit_checks", [])

        # Log FK-rejected rows from load phase
        fk_rejected = load_counts.get("_fk_rejected_rows", [])
        if fk_rejected:
            # These must go into audit conn (autocommit) since TX-B might rollback
            log_rejected_records(conn_audit, result.run_id, fk_rejected)
            all_rejected.extend(fk_rejected)
            result.total_rejected += len(fk_rejected)

        # Pre-commit checks passed → COMMIT
        conn_txn.commit()
        print(f"[PIPELINE] TX-B: COMMIT (loaded={result.total_loaded})")

        # Log DQ results (post-commit, into audit table)
        log_dq_results(conn_audit, result.run_id, result.pre_commit_checks)

        result.status = "SUCCESS"

    except PreCommitCheckFailure as e:
        conn_txn.rollback()
        result.status = "FAILED"
        result.errors.append(str(e))
        print(f"[PIPELINE] TX-B: ROLLBACK — {e}")

        # Log DQ results even on failure (§13 audit persistence)
        checks = load_counts.get("_pre_commit_checks", []) if 'load_counts' in dir() else []
        if checks:
            log_dq_results(conn_audit, result.run_id, checks)

    except Exception as e:
        conn_txn.rollback()
        result.status = "FAILED"
        result.errors.append(f"TX-B unexpected error: {e}")
        print(f"[PIPELINE] TX-B: ROLLBACK — unexpected: {e}")

    finally:
        conn_txn.close()

    # ── Step 7: Count failures ──
    result.critical_fails = sum(
        1 for c in result.pre_commit_checks
        if not c["passed"] and c["severity"] == "CRITICAL"
    )
    result.major_fails = sum(
        1 for r in all_rejected if r.severity == "MAJOR"
    ) if all_rejected else 0

    # ── Step 8: TX-C — finalize pipeline_run (§11-C) ──
    tx_c_finalize_pipeline_run(
        conn_audit,
        result.run_id,
        status=result.status,
        accepted_total=result.total_accepted,
        rejected_total=result.total_rejected,
        loaded_total=result.total_loaded,
        source_a_loaded=result.source_a_accepted - result.source_a_rejected if result.status == "SUCCESS" else 0,
        source_b_loaded=result.source_b_accepted - result.source_b_rejected if result.status == "SUCCESS" else 0,
        critical_dq_fails=result.critical_fails,
        major_dq_fails=result.major_fails,
    )
    print(f"[PIPELINE] TX-C: pipeline_run finalized status={result.status}")
    conn_audit.close()

    # ── Step 9: SHA256 post-ETL verify (§26) ──
    result.sha256_post_a = compute_sha256(
        os.path.join(project_root, SOURCE_A.file_path)
    )
    result.sha256_post_b = compute_sha256(
        os.path.join(project_root, SOURCE_B.file_path)
    )
    if (result.sha256_post_a != result.sha256_pre_a or
            result.sha256_post_b != result.sha256_pre_b):
        result.raw_data_mutated = True
        result.status = "FAILED"
        result.errors.append(
            "§26 CRITICAL: Raw data SHA256 changed during ETL! "
            f"A: {result.sha256_pre_a} → {result.sha256_post_a}, "
            f"B: {result.sha256_pre_b} → {result.sha256_post_b}"
        )
        print(f"[PIPELINE] §26 CRITICAL: RAW DATA MUTATED!")
    else:
        print(f"[PIPELINE] §26 SHA256 post-ETL verified: raw data unchanged")

    result.completed_at = datetime.now(timezone.utc)
    print(f"[PIPELINE] Complete. Status={result.status}")
    return result


__all__ = ["PipelineResult", "run_pipeline", "PIPELINE_VERSION"]
