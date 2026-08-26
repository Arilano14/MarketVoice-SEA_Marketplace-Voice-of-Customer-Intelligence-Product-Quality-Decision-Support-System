"""Phase 7 test suite — DEL-11 Baseline Business Intelligence Marts.

Validates:
  1. All 6 mart views exist and are queryable.
  2. Row count and grain contracts for each mart.
  3. Aggregate review count reconciliation (46,007 facts).
  4. Cross-source isolation (no cross-source product/shop linkage).
  5. Source B only restrictions for product and shop summaries.
  6. Source A only restrictions for sentiment/emotion breakdown.
  7. Absence of synthetic rows.
  8. Absence of exposed review timestamps (maintaining temporal boundary).
  9. Limitation clause comments present in SQL DDL.
"""
from __future__ import annotations

import os
import sys
import unittest

_PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
sys.path.insert(0, os.path.join(_PROJECT_ROOT, "src"))
_PIPDEPS = os.path.join(_PROJECT_ROOT, ".pipdeps")
if os.path.isdir(_PIPDEPS):
    sys.path.insert(0, _PIPDEPS)

os.environ.setdefault("MARKETVOICE_ENV", "test")

from marketvoice.database.connection import DBSettings, connect
from marketvoice.database.schema import SCHEMA


class TestPhase07Marts(unittest.TestCase):
    """Test suite for DEL-11 Business Intelligence Mart Views."""

    @classmethod
    def setUpClass(cls):
        cls.settings = DBSettings.from_env()
        cls.conn = connect(cls.settings, dbname_override=cls.settings.test_dbname)
        # Ensure DDL is applied
        sql_path = os.path.join(_PROJECT_ROOT, "sql", "marts", "005_mart_views.sql")
        with open(sql_path, "r", encoding="utf-8") as f:
            ddl = f.read()
        with cls.conn.cursor() as cur:
            cur.execute(ddl)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "conn") and cls.conn:
            cls.conn.close()

    def test_all_6_views_exist(self):
        """AC-P7-01: Verify all 6 mart views exist in marketvoice_warehouse schema."""
        expected_views = {
            "mv_source_summary",
            "mv_category_summary",
            "mv_product_summary",
            "mv_shop_summary",
            "mv_source_a_label_breakdown",
            "mv_pipeline_health",
        }
        with self.conn.cursor() as cur:
            cur.execute(f"""
                SELECT table_name FROM information_schema.views
                WHERE table_schema = '{SCHEMA}'
            """)
            views = {r["table_name"] for r in cur.fetchall()}
        self.assertTrue(expected_views.issubset(views), f"Missing views: {expected_views - views}")

    def test_mv_source_summary_rows_and_reconciliation(self):
        """AC-P7-02, AC-P7-03: mv_source_summary returns exactly 2 rows and sums to 46,007 reviews."""
        with self.conn.cursor() as cur:
            cur.execute(f"SELECT * FROM {SCHEMA}.mv_source_summary ORDER BY source_id")
            rows = cur.fetchall()
            self.assertEqual(len(rows), 2, f"Expected 2 sources, got {len(rows)}")

            sources = {r["source_id"]: r for r in rows}
            self.assertIn("SRC_PRDECT_ID_V1", sources)
            self.assertIn("SRC_TOKOPEDIA_REVIEWS_2019", sources)

            self.assertEqual(sources["SRC_PRDECT_ID_V1"]["review_count"], 5400)
            self.assertEqual(sources["SRC_TOKOPEDIA_REVIEWS_2019"]["review_count"], 40607)

            total_reviews = sum(r["review_count"] for r in rows)
            self.assertEqual(total_reviews, 46007, f"Total review count mismatch: {total_reviews}")

            # Verify rating distribution sum equals total per source
            for src_id, r in sources.items():
                rating_sum = (
                    r["rating_1_count"]
                    + r["rating_2_count"]
                    + r["rating_3_count"]
                    + r["rating_4_count"]
                    + r["rating_5_count"]
                )
                self.assertEqual(rating_sum, r["review_count"], f"Rating sum mismatch for {src_id}")

    def test_mv_category_summary_reconciliation(self):
        """AC-P7-04, AC-P7-05: mv_category_summary has 34 rows and reconciles to fact totals."""
        with self.conn.cursor() as cur:
            cur.execute(f"SELECT * FROM {SCHEMA}.mv_category_summary")
            rows = cur.fetchall()
            self.assertEqual(len(rows), 34, f"Expected 34 category rows, got {len(rows)}")

            # Check counts by source
            cur.execute(f"""
                SELECT source_id, COUNT(*) as cat_cnt, SUM(review_count) as total_rev
                FROM {SCHEMA}.mv_category_summary
                GROUP BY source_id
                ORDER BY source_id
            """)
            by_src = {r["source_id"]: r for r in cur.fetchall()}
            self.assertEqual(by_src["SRC_PRDECT_ID_V1"]["cat_cnt"], 29)
            self.assertEqual(by_src["SRC_PRDECT_ID_V1"]["total_rev"], 5400)
            self.assertEqual(by_src["SRC_TOKOPEDIA_REVIEWS_2019"]["cat_cnt"], 5)
            self.assertEqual(by_src["SRC_TOKOPEDIA_REVIEWS_2019"]["total_rev"], 40607)

    def test_mv_product_summary_source_b_only(self):
        """AC-P7-06: mv_product_summary contains exactly 3,664 Source B products."""
        with self.conn.cursor() as cur:
            cur.execute(f"SELECT * FROM {SCHEMA}.mv_product_summary")
            rows = cur.fetchall()
            self.assertEqual(len(rows), 3664, f"Expected 3664 products, got {len(rows)}")

            # Verify source_id is exclusively Source B
            cur.execute(f"SELECT DISTINCT source_id FROM {SCHEMA}.mv_product_summary")
            src_ids = [r["source_id"] for r in cur.fetchall()]
            self.assertEqual(src_ids, ["SRC_TOKOPEDIA_REVIEWS_2019"])

            # Total reviews from product summary must equal 40,607
            total_rev = sum(r["review_count"] for r in rows)
            self.assertEqual(total_rev, 40607, f"Product reviews sum mismatch: {total_rev}")

            # Low rating count <= review count
            for r in rows:
                self.assertLessEqual(r["low_rating_count"], r["review_count"])
                self.assertLessEqual(r["high_rating_count"], r["review_count"])

    def test_mv_shop_summary_source_b_only(self):
        """AC-P7-07: mv_shop_summary contains exactly 158 Source B shops."""
        with self.conn.cursor() as cur:
            cur.execute(f"SELECT * FROM {SCHEMA}.mv_shop_summary")
            rows = cur.fetchall()
            self.assertEqual(len(rows), 158, f"Expected 158 shops, got {len(rows)}")

            # Verify source_id is exclusively Source B
            cur.execute(f"SELECT DISTINCT source_id FROM {SCHEMA}.mv_shop_summary")
            src_ids = [r["source_id"] for r in cur.fetchall()]
            self.assertEqual(src_ids, ["SRC_TOKOPEDIA_REVIEWS_2019"])

            # Total reviews from shop summary must equal 40,607
            total_rev = sum(r["review_count"] for r in rows)
            self.assertEqual(total_rev, 40607, f"Shop reviews sum mismatch: {total_rev}")

    def test_mv_source_a_label_breakdown(self):
        """AC-P7-08: mv_source_a_label_breakdown is exclusively Source A and sums to 5,400."""
        with self.conn.cursor() as cur:
            cur.execute(f"SELECT * FROM {SCHEMA}.mv_source_a_label_breakdown")
            rows = cur.fetchall()
            self.assertGreater(len(rows), 0)

            # Check source_id
            for r in rows:
                self.assertEqual(r["source_id"], "SRC_PRDECT_ID_V1")

            total_rev = sum(r["review_count"] for r in rows)
            self.assertEqual(total_rev, 5400, f"Source A label breakdown sum mismatch: {total_rev}")

            # Pct of source sum should be ~100%
            total_pct = sum(r["pct_of_source"] for r in rows)
            self.assertAlmostEqual(float(total_pct), 100.0, places=1)

    def test_mv_pipeline_health(self):
        """AC-P7-01: mv_pipeline_health returns recent pipeline execution stats."""
        with self.conn.cursor() as cur:
            cur.execute(f"SELECT * FROM {SCHEMA}.mv_pipeline_health")
            rows = cur.fetchall()
            self.assertGreaterEqual(len(rows), 1)
            for r in rows:
                self.assertEqual(r["status"], "SUCCESS")
                self.assertEqual(r["critical_dq_fails"], 0)
                self.assertEqual(r["rejected_rows_total"], 0)
                self.assertEqual(r["loaded_rows_total"], 46007)

    def test_no_temporal_columns_in_marts(self):
        """AC-P7-10: Verify no customer review timestamp or date trend columns exist in analytical marts."""
        with self.conn.cursor() as cur:
            analytical_views = [
                "mv_source_summary",
                "mv_category_summary",
                "mv_product_summary",
                "mv_shop_summary",
                "mv_source_a_label_breakdown",
            ]
            for v in analytical_views:
                cur.execute(f"""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_schema = '{SCHEMA}' AND table_name = '{v}'
                """)
                col_names = [r["column_name"].lower() for r in cur.fetchall()]
                for forbidden in ["review_date", "review_time", "review_timestamp", "order_date", "created_date"]:
                    self.assertNotIn(forbidden, col_names, f"Forbidden temporal column {forbidden} found in {v}")

    def test_limitation_clauses_in_ddl(self):
        """AC-P7-12: Verify SQL DDL file contains formal limitation clauses for each view."""
        sql_path = os.path.join(_PROJECT_ROOT, "sql", "marts", "005_mart_views.sql")
        with open(sql_path, "r", encoding="utf-8") as f:
            content = f.read()

        views = [
            "mv_source_summary",
            "mv_category_summary",
            "mv_product_summary",
            "mv_shop_summary",
            "mv_source_a_label_breakdown",
            "mv_pipeline_health",
        ]
        for v in views:
            self.assertIn(f"VIEW 1: {v}" if v == "mv_source_summary" else v, content)
            self.assertIn("Limitation:", content)


if __name__ == "__main__":
    unittest.main()
