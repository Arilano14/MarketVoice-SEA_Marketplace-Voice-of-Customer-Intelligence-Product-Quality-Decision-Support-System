"""Phase 6 test suite — DEL-08/09/10 validation.

Tests require:
  MARKETVOICE_ENV=test
  Running PostgreSQL on localhost:5432
"""
from __future__ import annotations

import hashlib
import os
import sys
import unittest

# Ensure project src and .pipdeps on path
_PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
sys.path.insert(0, os.path.join(_PROJECT_ROOT, "src"))
_PIPDEPS = os.path.join(_PROJECT_ROOT, ".pipdeps")
if os.path.isdir(_PIPDEPS):
    sys.path.insert(0, _PIPDEPS)

os.environ.setdefault("MARKETVOICE_ENV", "test")


class TestExtract(unittest.TestCase):
    """Test extract module (§21 UTF-8, §26 SHA256)."""

    def test_source_a_sha256(self):
        from marketvoice.etl.extract import SOURCE_A, verify_sha256
        sha = verify_sha256(SOURCE_A, _PROJECT_ROOT)
        self.assertEqual(sha, SOURCE_A.expected_sha256)

    def test_source_b_sha256(self):
        from marketvoice.etl.extract import SOURCE_B, verify_sha256
        sha = verify_sha256(SOURCE_B, _PROJECT_ROOT)
        self.assertEqual(sha, SOURCE_B.expected_sha256)

    def test_source_a_read_strict_utf8(self):
        from marketvoice.etl.extract import SOURCE_A, read_csv_strict
        header, rows = read_csv_strict(SOURCE_A, _PROJECT_ROOT)
        self.assertEqual(len(header), SOURCE_A.expected_column_count)
        self.assertEqual(len(rows), SOURCE_A.expected_row_count)
        # Verify stable row numbers
        self.assertEqual(rows[0]["_source_row_number"], 1)
        self.assertEqual(rows[-1]["_source_row_number"], SOURCE_A.expected_row_count)

    def test_source_b_read_strict_utf8(self):
        from marketvoice.etl.extract import SOURCE_B, read_csv_strict
        header, rows = read_csv_strict(SOURCE_B, _PROJECT_ROOT)
        self.assertEqual(len(header), SOURCE_B.expected_column_count)
        self.assertEqual(len(rows), SOURCE_B.expected_row_count)

    def test_extract_all(self):
        from marketvoice.etl.extract import extract_all
        result = extract_all(_PROJECT_ROOT)
        self.assertEqual(result["source_a_row_count"], 5400)
        self.assertEqual(result["source_b_row_count"], 40607)


class TestTransform(unittest.TestCase):
    """Test transform module (§16 hash, §19 FK rules, §20 product name)."""

    @classmethod
    def setUpClass(cls):
        from marketvoice.etl.extract import extract_all
        cls.extracted = extract_all(_PROJECT_ROOT)

    def test_row_hash_deterministic(self):
        """§16 row hash must be deterministic."""
        from marketvoice.etl.transform import _compute_row_hash
        h1 = _compute_row_hash("SRC_A", "abc123", 42)
        h2 = _compute_row_hash("SRC_A", "abc123", 42)
        self.assertEqual(h1, h2)
        # Different inputs → different hash
        h3 = _compute_row_hash("SRC_A", "abc123", 43)
        self.assertNotEqual(h1, h3)

    def test_transform_no_cross_source_linkage(self):
        """§6 Source A facts must have product_lookup_id=None, shop_lookup_id=None."""
        from marketvoice.etl.transform import transform
        result = transform(
            self.extracted["source_a_rows"],
            self.extracted["source_b_rows"],
            self.extracted["source_a_sha256"],
            self.extracted["source_b_sha256"],
        )
        for fact in result.fact_rows:
            if fact["source_id"] == "SRC_PRDECT_ID_V1":
                self.assertIsNone(fact["product_lookup_id"],
                                  "§19: Source A product_lookup_id must be None")
                self.assertIsNone(fact["shop_lookup_id"],
                                  "§19: Source A shop_lookup_id must be None")

    def test_transform_no_synthetic(self):
        """§9 All fact rows must have is_synthetic=False."""
        from marketvoice.etl.transform import transform
        result = transform(
            self.extracted["source_a_rows"],
            self.extracted["source_b_rows"],
            self.extracted["source_a_sha256"],
            self.extracted["source_b_sha256"],
        )
        for fact in result.fact_rows:
            self.assertFalse(fact["is_synthetic"], "§9: is_synthetic must be FALSE")

    def test_transform_source_b_no_sentiment_emotion(self):
        """§6 Source B must have NULL gold sentiment/emotion."""
        from marketvoice.etl.transform import transform
        result = transform(
            self.extracted["source_a_rows"],
            self.extracted["source_b_rows"],
            self.extracted["source_a_sha256"],
            self.extracted["source_b_sha256"],
        )
        for fact in result.fact_rows:
            if fact["source_id"] == "SRC_TOKOPEDIA_REVIEWS_2019":
                self.assertIsNone(fact["source_gold_sentiment_label"],
                                  "§6: Source B sentiment must be None")
                self.assertIsNone(fact["source_gold_emotion_label"],
                                  "§6: Source B emotion must be None")

    def test_transform_produces_dimensions(self):
        from marketvoice.etl.transform import transform
        result = transform(
            self.extracted["source_a_rows"],
            self.extracted["source_b_rows"],
            self.extracted["source_a_sha256"],
            self.extracted["source_b_sha256"],
        )
        self.assertGreater(len(result.categories), 0)
        self.assertGreater(len(result.products), 0)
        self.assertGreater(len(result.shops), 0)

    def test_product_name_variant_minimum_1(self):
        """§20: product_name_variant_count >= 1."""
        from marketvoice.etl.transform import transform
        result = transform(
            self.extracted["source_a_rows"],
            self.extracted["source_b_rows"],
            self.extracted["source_a_sha256"],
            self.extracted["source_b_sha256"],
        )
        for prod in result.products:
            self.assertGreaterEqual(prod["product_name_variant_count"], 1)


class TestDatabaseSchema(unittest.TestCase):
    """Test DEL-08 DDL on test database."""

    @classmethod
    def setUpClass(cls):
        from marketvoice.database.connection import (
            DBSettings, connect, ensure_database_exists, get_marketvoice_env,
        )
        env = get_marketvoice_env()
        if env != "test":
            raise unittest.SkipTest(f"MARKETVOICE_ENV={env}, required=test")
        cls.settings = DBSettings.from_env()
        ensure_database_exists(cls.settings, dbname=cls.settings.test_dbname)
        cls.conn = connect(cls.settings, dbname_override=cls.settings.test_dbname)
        from marketvoice.database.schema import apply_ddl
        apply_ddl(cls.conn, reset_schema=True)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'conn'):
            cls.conn.close()

    def test_9_tables_exactly(self):
        """§24: Exactly 9 physical tables."""
        from marketvoice.database.schema import verify_9_tables_exactly
        ok, missing, extras = verify_9_tables_exactly(self.conn)
        self.assertTrue(ok, f"missing={missing}, extras={extras}")

    def test_seed_dim_source_2(self):
        from marketvoice.database.schema import verify_seed_counts
        counts = verify_seed_counts(self.conn)
        self.assertEqual(counts["dim_source"], 2)

    def test_seed_dim_rating_5(self):
        from marketvoice.database.schema import verify_seed_counts
        counts = verify_seed_counts(self.conn)
        self.assertEqual(counts["dim_rating"], 5)

    def test_server_encoding_utf8(self):
        """§21: server_encoding must be UTF8."""
        from marketvoice.database.schema import server_encoding
        enc = server_encoding(self.conn)
        self.assertEqual(enc, "UTF8")

    def test_safe_destructive_guard(self):
        """§22: Guard must pass in test env."""
        from marketvoice.database.connection import assert_safe_destructive
        # Should not raise
        assert_safe_destructive(self.conn, self.settings)


class TestFullPipeline(unittest.TestCase):
    """Integration test: full ETL pipeline on test DB."""

    @classmethod
    def setUpClass(cls):
        from marketvoice.database.connection import (
            DBSettings, get_marketvoice_env,
        )
        env = get_marketvoice_env()
        if env != "test":
            raise unittest.SkipTest(f"MARKETVOICE_ENV={env}, required=test")
        cls.settings = DBSettings.from_env()

    def test_full_pipeline_run(self):
        """Run complete pipeline and verify success."""
        from marketvoice.etl.pipeline import run_pipeline
        result = run_pipeline(
            project_root=_PROJECT_ROOT,
            target_db=self.settings.test_dbname,
            ensure_schema=True,
        )
        self.assertEqual(result.status, "SUCCESS", f"Pipeline failed: {result.errors}")
        self.assertFalse(result.raw_data_mutated, "§26: Raw data must not change")
        self.assertEqual(result.critical_fails, 0, "No critical DQ failures allowed")
        self.assertGreater(result.total_loaded, 0, "Must load at least 1 fact row")

    def test_idempotency(self):
        """§17: Run pipeline twice → same natural-key counts, 0 duplicate natural keys."""
        from marketvoice.etl.pipeline import run_pipeline
        from marketvoice.database.connection import connect
        from marketvoice.database.schema import SCHEMA

        # Run 1
        r1 = run_pipeline(
            project_root=_PROJECT_ROOT,
            target_db=self.settings.test_dbname,
            ensure_schema=True,
        )
        self.assertEqual(r1.status, "SUCCESS")

        # Run 2
        r2 = run_pipeline(
            project_root=_PROJECT_ROOT,
            target_db=self.settings.test_dbname,
            ensure_schema=True,
        )
        self.assertEqual(r2.status, "SUCCESS")

        # Same fact count
        self.assertEqual(r1.total_loaded, r2.total_loaded,
                         "§17: Same fact count after idempotent re-run")
        self.assertEqual(r1.dim_category_count, r2.dim_category_count)
        self.assertEqual(r1.dim_product_count, r2.dim_product_count)
        self.assertEqual(r1.dim_shop_count, r2.dim_shop_count)

        # No duplicate natural keys
        conn = connect(self.settings, dbname_override=self.settings.test_dbname)
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT COUNT(*) c FROM (
                    SELECT source_sk, source_native_row_hash, COUNT(*) cnt
                    FROM {SCHEMA}.fact_review
                    GROUP BY source_sk, source_native_row_hash
                    HAVING COUNT(*) > 1
                ) dups
            """)
            dups = cur.fetchone()["c"]
        conn.close()
        self.assertEqual(dups, 0, "§17: No duplicate natural keys after re-run")

    def test_post_load_checks(self):
        """Run post-load forensic checks after a successful pipeline."""
        from marketvoice.etl.pipeline import run_pipeline
        from marketvoice.database.connection import connect
        from marketvoice.quality.checks import run_post_load_checks

        result = run_pipeline(
            project_root=_PROJECT_ROOT,
            target_db=self.settings.test_dbname,
            ensure_schema=True,
        )
        self.assertEqual(result.status, "SUCCESS")

        conn = connect(self.settings, dbname_override=self.settings.test_dbname)
        post_checks = run_post_load_checks(conn, result.run_id)
        conn.close()

        critical_fails = [c for c in post_checks if not c["passed"] and c["severity"] == "CRITICAL"]
        self.assertEqual(len(critical_fails), 0,
                         f"Post-load critical failures: {critical_fails}")


if __name__ == "__main__":
    unittest.main()
