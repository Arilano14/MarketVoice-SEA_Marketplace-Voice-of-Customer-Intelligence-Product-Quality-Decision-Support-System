"""PostgreSQL connection helpers + safety (§22 guard).

§22 Destructive action safety:
  Before any DROP/TRUNCATE, BOTH must hold:
    1. MARKETVOICE_ENV == "test"
    2. current_database() == configured test database

If either fails -> ABORT via UnsafeDatabaseError.

PostgreSQL server_encoding must be UTF8 (§21) per post-deployment verify.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from typing import Optional

_PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)
_PIPDEPS = os.path.join(_PROJECT_ROOT, ".pipdeps")
if os.path.isdir(_PIPDEPS) and _PIPDEPS not in sys.path:
    sys.path.insert(0, _PIPDEPS)

try:
    import psycopg
    from psycopg import Connection, Cursor
except ImportError as exc:  # pragma: no cover - import guard
    raise RuntimeError(
        "psycopg driver missing. Install psycopg[binary] into .pipdeps "
        "(see plan §23) or pip install --target .pipdeps 'psycopg[binary]'."
    ) from exc

from psycopg.rows import dict_row


class UnsafeDatabaseError(Exception):
    """§22 raised if destructive guard fails. Do NOT suppress."""


def _load_dotenv_if_present() -> None:
    """Load local .env file if present without overriding existing env vars."""
    env_file = os.path.join(_PROJECT_ROOT, ".env")
    if os.path.isfile(env_file):
        try:
            with open(env_file, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    k, v = k.strip(), v.strip()
                    if k not in os.environ:
                        os.environ[k] = v
        except Exception:
            pass


@dataclass
class DBSettings:
    host: str
    port: int
    dbname: str
    user: str
    password: str
    test_dbname: str = "marketvoice_test"
    dev_dbname: str = "marketvoice_dev"

    @classmethod
    def from_env(cls) -> "DBSettings":
        _load_dotenv_if_present()
        password = os.getenv("POSTGRES_PASSWORD")
        if not password:
            raise ValueError(
                "Missing required environment variable 'POSTGRES_PASSWORD'. "
                "Please configure POSTGRES_PASSWORD in your environment or local .env file."
            )
        return cls(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", "5432")),
            dbname=os.getenv("POSTGRES_DB", "marketvoice_dev"),
            user=os.getenv("POSTGRES_USER", "openpg"),
            password=password,
            test_dbname=os.getenv("POSTGRES_TEST_DB", "marketvoice_test"),
            dev_dbname=os.getenv("POSTGRES_DEV_DB", "marketvoice_dev"),
        )

    def target_dbname(self, env: Optional[str] = None) -> str:
        env = env or os.getenv("MARKETVOICE_ENV", "dev")
        if env == "test":
            return self.test_dbname
        return self.dev_dbname


def get_marketvoice_env() -> str:
    return os.getenv("MARKETVOICE_ENV", "dev").lower()


def connect(settings: DBSettings | None = None, *, dbname_override: str | None = None,
            autocommit: bool = True) -> Connection:
    """Open connection to the target DB (per MARKETVOICE_ENV).

    Verifies server_encoding=UTF8 (§21) right after connect.
    Raises RuntimeError if server_encoding != UTF8.
    """
    settings = settings or DBSettings.from_env()
    if dbname_override:
        dbname = dbname_override
    else:
        dbname = settings.target_dbname()
    conn = psycopg.connect(
        host=settings.host,
        port=settings.port,
        dbname=dbname,
        user=settings.user,
        password=settings.password,
        row_factory=dict_row,
        autocommit=autocommit,
    )
    with conn.cursor() as cur:
        cur.execute("SHOW server_encoding")
        enc = cur.fetchone()["server_encoding"].upper()
        if enc != "UTF8":
            conn.close()
            raise RuntimeError(
                f"PostgreSQL server_encoding={enc!r}, required=UTF8 (§21)."
            )
    return conn


def assert_safe_destructive(conn: Connection, settings: DBSettings | None = None) -> None:
    """§22 Mandatory guard. Call before DROP / TRUNCATE / schema DROP.

    Both required:
      MARKETVOICE_ENV == "test"  AND  current_database() == configured test_dbname

    Raises UnsafeDatabaseError if either condition fails.
    """
    settings = settings or DBSettings.from_env()
    env = get_marketvoice_env()
    with conn.cursor() as cur:
        cur.execute("SELECT current_database() AS db")
        current_db = cur.fetchone()["db"]
    if env != "test":
        raise UnsafeDatabaseError(
            f"§22 Destructive guard: MARKETVOICE_ENV={env!r}, required='test'. "
            f"Aborting on database {current_db!r}."
        )
    if current_db != settings.test_dbname:
        raise UnsafeDatabaseError(
            f"§22 Destructive guard: current_database()={current_db!r} "
            f"!= configured test_dbname={settings.test_dbname!r}. ABORT."
        )


def ensure_database_exists(settings: DBSettings | None = None, *, dbname: str) -> bool:
    """Connect to postgres default maintenance DB and CREATE DATABASE if needed.

    Returns: True if created freshly, False if already present.
    """
    settings = settings or DBSettings.from_env()
    maintenance_db = "postgres"
    created = False
    with psycopg.connect(
        host=settings.host,
        port=settings.port,
        dbname=maintenance_db,
        user=settings.user,
        password=settings.password,
        autocommit=True,
    ) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s", (dbname,)
            )
            row = cur.fetchone()
            if row is None:
                cur.execute(f'CREATE DATABASE "{dbname}"')
                created = True
    return created


__all__ = [
    "DBSettings",
    "UnsafeDatabaseError",
    "connect",
    "assert_safe_destructive",
    "ensure_database_exists",
    "get_marketvoice_env",
    "Connection",
    "Cursor",
]
