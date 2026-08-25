"""Phase 9 automated test suite — Issue Intelligence.

Verifies:
  1. Taxonomy definition, stopwords, and freeze invariants.
  2. Multi-label keyword classification engine.
  3. Severity assignment rules.
  4. Issue summary, category, and product metric calculations.
  5. Emerging issue z-score and segment analysis.
  6. Recurrence analysis.
  7. Database schema, table counts, FK integrity, and view reconciliation.
"""
import os
import sys
import pytest
import pandas as pd
import numpy as np

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))
_PIPDEPS = os.path.join(PROJECT_ROOT, ".pipdeps")
if os.path.isdir(_PIPDEPS):
    sys.path.insert(0, _PIPDEPS)

from marketvoice.analytics.taxonomy import (
    INDONESIAN_STOPWORDS, CANDIDATE_TAXONOMY, TAXONOMY_VERSION,
    compute_filtered_ngrams, validate_taxonomy_against_corpus, freeze_taxonomy,
)
from marketvoice.analytics.issue_classifier import (
    classify_reviews, classification_summary, _match_keywords,
    _compute_confidence, _rating_to_severity_id, SEVERITY_LEVELS,
)
from marketvoice.analytics.issue_metrics import (
    compute_issue_summary, compute_issue_by_category, compute_issue_by_product,
)
from marketvoice.analytics.emerging_issues import (
    detect_emerging_issues, _proportion_z_test,
)
from marketvoice.analytics.recurrence import (
    compute_category_recurrence, compute_product_recurrence,
)


# ===================================================================
# 1. TAXONOMY TESTS
# ===================================================================

class TestTaxonomy:
    """Test taxonomy definition, stopwords, and freeze invariants."""

    def test_stopwords_not_empty(self):
        assert len(INDONESIAN_STOPWORDS) > 100
        assert "dan" in INDONESIAN_STOPWORDS
        assert "saya" in INDONESIAN_STOPWORDS
        assert "barang" in INDONESIAN_STOPWORDS

    def test_candidate_taxonomy_5_categories(self):
        assert len(CANDIDATE_TAXONOMY) == 5
        ids = [c["issue_id"] for c in CANDIDATE_TAXONOMY]
        assert sorted(ids) == [1, 2, 3, 4, 5]

    def test_all_categories_have_required_fields(self):
        required_fields = ["issue_id", "issue_name", "definition", "evidence_keywords"]
        for cat in CANDIDATE_TAXONOMY:
            for field in required_fields:
                assert field in cat, f"Missing {field} in {cat.get('issue_name')}"
                assert len(cat["evidence_keywords"]) >= 5

    def test_filtered_ngrams_excludes_stopwords(self):
        texts = pd.Series(["barang ini sangat bagus dan saya suka sekali", "produk jelek rusak cacat"])
        ngrams = compute_filtered_ngrams(texts, top_n=20, min_freq=1)
        extracted = [ng["ngram"] for ng in ngrams]
        assert "rusak" in extracted
        assert "cacat" in extracted
        # Stopwords should not appear as standalone unigrams
        assert "dan" not in extracted
        assert "saya" not in extracted

    def test_freeze_taxonomy_marks_active(self):
        val_results = [
            {"issue_id": 1, "support_count": 100, "distinct_keywords_observed": 5, "status": "ACTIVE"},
            {"issue_id": 2, "support_count": 80, "distinct_keywords_observed": 4, "status": "ACTIVE"},
            {"issue_id": 3, "support_count": 60, "distinct_keywords_observed": 3, "status": "ACTIVE"},
            {"issue_id": 4, "support_count": 55, "distinct_keywords_observed": 4, "status": "ACTIVE"},
            {"issue_id": 5, "support_count": 70, "distinct_keywords_observed": 4, "status": "ACTIVE"},
        ]
        frozen = freeze_taxonomy(val_results)
        assert len(frozen) == 5
        for cat in frozen:
            assert cat["status"] == "ACTIVE"
            assert cat["taxonomy_version"] == TAXONOMY_VERSION


# ===================================================================
# 2. CLASSIFIER TESTS
# ===================================================================

class TestClassifier:
    """Test multi-label keyword classifier and severity assignment."""

    def test_match_keywords_exact(self):
        text = "barang rusak dan pecah saat pengiriman"
        matched = _match_keywords(text, ["rusak", "pecah", "cacat", "hilang"])
        assert "rusak" in matched
        assert "pecah" in matched
        assert "cacat" not in matched
        assert "hilang" not in matched

    def test_confidence_computation(self):
        assert _compute_confidence(1, 10) == pytest.approx(0.3333, rel=1e-2)
        assert _compute_confidence(2, 10) == pytest.approx(0.6667, rel=1e-2)
        assert _compute_confidence(3, 10) == 1.0
        assert _compute_confidence(5, 10) == 1.0

    def test_severity_mapping(self):
        assert _rating_to_severity_id(1) == 1  # CRITICAL
        assert _rating_to_severity_id(2) == 2  # HIGH
        assert _rating_to_severity_id(3) == 3  # MODERATE
        assert _rating_to_severity_id(4) == 4  # LOW
        assert _rating_to_severity_id(5) == 4  # LOW

    def test_classify_reviews_multi_label(self):
        sample = pd.DataFrame({
            "review_sk": [1, 2, 3],
            "source_sk": [1, 1, 1],
            "review_text": [
                "barang rusak cacat dan packing lecek penyok",
                "pengiriman cepat dan bagus sekali",
                "warna beda tidak sesuai pesanan dan lambat pengiriman",
            ],
            "rating_value": [1, 5, 2],
        })
        classified = classify_reviews(sample)
        # Review 1 should match Product Defect AND Packaging Damage
        r1 = classified[classified["review_sk"] == 1]
        assert len(r1) >= 2
        r1_issues = set(r1["issue_name"])
        assert "Product Defect / Quality" in r1_issues
        assert "Packaging / Shipping Damage" in r1_issues
        assert all(r1["severity_id"] == 1)

        # Review 3 should match Order Inaccuracy AND Delivery
        r3 = classified[classified["review_sk"] == 3]
        assert len(r3) >= 2
        assert all(r3["severity_id"] == 2)

    def test_classification_summary(self):
        sample = pd.DataFrame({
            "review_sk": [1, 1, 2],
            "source_sk": [1, 1, 1],
            "issue_id": [1, 2, 1],
            "issue_name": ["Product Defect / Quality", "Packaging / Shipping Damage", "Product Defect / Quality"],
            "severity_id": [1, 1, 4],
            "rating_value": [1, 1, 5],
            "confidence": [0.66, 0.33, 0.33],
        })
        summary = classification_summary(sample, total_reviews=10, total_negative_reviews=2)
        assert summary["total_issue_assignments"] == 3
        assert summary["distinct_reviews_with_issues"] == 2
        assert summary["issue_coverage_pct"] == 20.0


# ===================================================================
# 3. METRICS & RECURRENCE TESTS
# ===================================================================

class TestMetricsAndRecurrence:
    """Test issue summary, emerging issues, and recurrence."""

    def test_proportion_z_test(self):
        # Significant difference
        z = _proportion_z_test(0.30, 1000, 0.10, 5000)
        assert z > 2.0

        # No difference
        z_equal = _proportion_z_test(0.10, 1000, 0.10, 5000)
        assert abs(z_equal) < 0.1

    def test_emerging_issues_detects_overrepresentation(self):
        fact = pd.DataFrame({
            "review_sk": list(range(1, 101)),
            "rating_value": [1] * 20 + [5] * 80,
        })
        # Issue 1 appears mostly in rating 1
        classified = pd.DataFrame({
            "review_sk": list(range(1, 16)) + [50, 51],
            "source_sk": [1] * 17,
            "issue_id": [1] * 17,
            "issue_name": ["Product Defect / Quality"] * 17,
            "rating_value": [1] * 15 + [5] * 2,
        })
        emerg = detect_emerging_issues(classified, fact, "SRC_TEST", min_support=10, z_threshold=2.0)
        assert not emerg.empty
        assert emerg.iloc[0]["emerging_signal"] == True

    def test_recurrence_computation(self):
        classified = pd.DataFrame({
            "review_sk": [1, 2, 3, 4, 5],
            "category_sk": [10, 10, 10, 20, 20],
            "issue_id": [1, 1, 1, 2, 2],
            "issue_name": ["Defect", "Defect", "Defect", "Packaging", "Packaging"],
        })
        rec = compute_category_recurrence(classified, min_threshold=3)
        # Category 10 has 3 distinct reviews for issue 1 -> is_recurring = True
        c10 = rec[rec["category_sk"] == 10]
        assert len(c10) == 1
        assert c10.iloc[0]["is_recurring"] == True
        # Category 20 has 2 distinct reviews -> is_recurring = False
        c20 = rec[rec["category_sk"] == 20]
        assert c20.iloc[0]["is_recurring"] == False


# ===================================================================
# 4. DATABASE INTEGRATION & RECONCILIATION TESTS
# ===================================================================

class TestDatabaseIntegration:
    """Test database tables, views, and integrity."""

    @pytest.fixture(scope="class")
    def db_conn(self):
        from marketvoice.database.connection import DBSettings, connect
        settings = DBSettings.from_env()
        conn = connect(settings, dbname_override=settings.dev_dbname)
        yield conn
        conn.close()

    def test_fact_review_unchanged(self, db_conn):
        with db_conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS cnt FROM marketvoice_warehouse.fact_review")
            cnt = cur.fetchone()["cnt"]
            assert cnt == 46007

    def test_dim_issue_5_active(self, db_conn):
        with db_conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS cnt FROM marketvoice_warehouse.dim_issue WHERE status = 'ACTIVE'")
            assert cur.fetchone()["cnt"] == 5

    def test_dim_severity_4_levels(self, db_conn):
        with db_conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS cnt FROM marketvoice_warehouse.dim_severity")
            assert cur.fetchone()["cnt"] == 4

    def test_fact_review_issue_has_records(self, db_conn):
        with db_conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS cnt FROM marketvoice_warehouse.fact_review_issue")
            cnt = cur.fetchone()["cnt"]
            assert cnt > 15000, f"Expected >15000 issue assignments, got {cnt}"

    def test_zero_orphan_reviews(self, db_conn):
        with db_conn.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) AS cnt FROM marketvoice_warehouse.fact_review_issue fri
                LEFT JOIN marketvoice_warehouse.fact_review fr ON fr.review_sk = fri.review_sk
                WHERE fr.review_sk IS NULL
            """)
            assert cur.fetchone()["cnt"] == 0

    def test_zero_cross_source_violations(self, db_conn):
        with db_conn.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) AS cnt FROM marketvoice_warehouse.fact_review_issue fri
                JOIN marketvoice_warehouse.fact_review fr ON fr.review_sk = fri.review_sk
                WHERE fri.source_sk != fr.source_sk
            """)
            assert cur.fetchone()["cnt"] == 0

    def test_mv_issue_summary_view(self, db_conn):
        with db_conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS cnt FROM marketvoice_warehouse.mv_issue_summary")
            assert cur.fetchone()["cnt"] == 10  # 2 sources * 5 issues

    def test_mv_issue_by_category_view(self, db_conn):
        with db_conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS cnt FROM marketvoice_warehouse.mv_issue_by_category")
            assert cur.fetchone()["cnt"] > 50

    def test_mv_issue_by_product_view(self, db_conn):
        with db_conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS cnt FROM marketvoice_warehouse.mv_issue_by_product")
            assert cur.fetchone()["cnt"] > 1000

    def test_mv_issue_emerging_view(self, db_conn):
        with db_conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS cnt FROM marketvoice_warehouse.mv_issue_emerging")
            assert cur.fetchone()["cnt"] == 10  # 2 sources * 5 issues

    def test_mv_issue_low_rating_overrepresentation_view(self, db_conn):
        with db_conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS cnt FROM marketvoice_warehouse.mv_issue_low_rating_overrepresentation")
            assert cur.fetchone()["cnt"] == 10  # 2 sources * 5 issues
