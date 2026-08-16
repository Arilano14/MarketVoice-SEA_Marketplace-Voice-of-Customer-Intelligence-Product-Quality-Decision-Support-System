"""DDL apply / verify helpers for DEL-08 physical schema (9 tables)."""
from __future__ import annotations

import os
from typing import Iterable, Sequence

from .connection import Connection, DBSettings, connect

SCHEMA = "marketvoice_warehouse"
EXPECTED_TABLES = {
    # audit (never truncate)
    "pipeline_run",
    "rejected_record_log",
    "data_quality_result",
    # conformed master dims (never truncate)
    "dim_source",
    "dim_rating",
    # dynamic analytical (truncated each TX-B run)
    "dim_category",
    "dim_product",
    "dim_shop",
    # central fact (truncated each run)
    "fact_review",
}


def _sql_root() -> str:
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "sql")
    )


def ddl_file_order() -> list[str]:
    return [
        os.path.join(_sql_root(), "warehouse", "001_schema.sql"),
        os.path.join(_sql_root(), "warehouse", "002_tables.sql"),
        os.path.join(_sql_root(), "warehouse", "003_constraints.sql"),
        os.path.join(_sql_root(), "warehouse", "004_indexes.sql"),
    ]


def apply_ddl(conn: Connection, sql_files: Sequence[str] | None = None,
              *, reset_schema: bool = False) -> None:
    """Apply the 4 DDL files sequentially in order.

    Runs in autocommit per file (each file is a logical checkpoint).

    If reset_schema=True, drops and recreates the schema first for
    idempotent re-application (safe for test/dev environments).
    """
    sql_files = list(sql_files or ddl_file_order())
    with conn.cursor() as cur:
        if reset_schema:
            cur.execute(f"DROP SCHEMA IF EXISTS {SCHEMA} CASCADE")
            cur.execute(f"CREATE SCHEMA {SCHEMA}")
        for fp in sql_files:
            if not os.path.isfile(fp):
                raise FileNotFoundError(f"DDL file missing: {fp}")
            with open(fp, "r", encoding="utf-8") as fh:
                sql = fh.read()
            try:
                cur.execute(sql)
            except Exception as exc:
                raise RuntimeError(f"DDL apply FAILED on {os.path.basename(fp)}: {exc}") from exc


def list_physical_tables(conn: Connection, schema: str = SCHEMA) -> set[str]:
    """Return table names from information_schema for this schema."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = %s AND table_type = 'BASE TABLE'
            """,
            (schema,),
        )
        return {row["table_name"] for row in cur.fetchall()}


def verify_9_tables_exactly(conn: Connection) -> tuple[bool, set[str], set[str]]:
    """§24 / §32 evidence: confirm 9 tables exactly with no extras, no missing.

    Returns: (ok_bool, missing, extras)
    """
    actual = list_physical_tables(conn)
    missing = EXPECTED_TABLES - actual
    extras = actual - EXPECTED_TABLES
    ok = (len(missing) == 0) and (len(extras) == 0)
    return ok, missing, extras


def verify_seed_counts(conn: Connection, schema: str = SCHEMA) -> dict[str, int]:
    """After DDL seed, dim_source MUST = 2, dim_rating MUST = 5."""
    with conn.cursor() as cur:
        cur.execute(f"SELECT COUNT(*) c FROM {schema}.dim_source")
        dim_source = cur.fetchone()["c"]
        cur.execute(f"SELECT COUNT(*) c FROM {schema}.dim_rating")
        dim_rating = cur.fetchone()["c"]
    return {"dim_source": dim_source, "dim_rating": dim_rating}


def postgresql_version(conn: Connection) -> str:
    with conn.cursor() as cur:
        cur.execute("SELECT version() AS v")
        return str(cur.fetchone()["v"]).split(",")[0].strip()


def server_encoding(conn: Connection) -> str:
    with conn.cursor() as cur:
        cur.execute("SHOW server_encoding")
        return cur.fetchone()["server_encoding"].upper()


__all__ = [
    "SCHEMA",
    "EXPECTED_TABLES",
    "ddl_file_order",
    "apply_ddl",
    "list_physical_tables",
    "verify_9_tables_exactly",
    "verify_seed_counts",
    "postgresql_version",
    "server_encoding",
]
