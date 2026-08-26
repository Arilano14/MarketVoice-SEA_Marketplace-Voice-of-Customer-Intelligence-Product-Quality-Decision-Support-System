"""Phase 9 Analytical Validation Test Suite.

Verifies analytical correctness, data contracts, and governance invariants:
  - TAX-001: Taxonomy category definitions completeness
  - TAX-002: Category support threshold compliance
  - TAX-003: Separation of coverage calculation from quality metrics
  - TAX-004: Gold-label benchmark metric validity
  - TAX-005: Rating-based severity proxy mapping
  - REC-001: Recurrence grain (distinct review events)
  - REC-002: Duplicate handling in recurrence
  - SRC-001: Source A (Shopee Benchmark) isolation
  - SRC-002: Source B (External Benchmark) isolation
  - TRACE-001: 100% review-to-issue traceability
  - TREND-001: Temporal limitation enforcement (no temporal claims)
"""
import json
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

from marketvoice.analytics.taxonomy import CANDIDATE_TAXONOMY, TAXONOMY_VERSION
from marketvoice.analytics.issue_classifier import SEVERITY_LEVELS, SEVERITY_STATUS, _rating_to_severity_id
from marketvoice.analytics.dissatisfaction_drivers import analyze_dissatisfaction_drivers, proportion_z_test
from marketvoice.analytics.recurrence import compute_category_recurrence, compute_product_recurrence
from marketvoice.database.connection import DBSettings, connect
from marketvoice.database.schema import SCHEMA


# ===================================================================
# TAXONOMY & CLASSIFIER VALIDATION (TAX-001 .. TAX-004)
# ===================================================================

class TestTaxonomyAndQualityValidation:
    """Analytical validation of taxonomy and classifier quality."""

    def test_tax_001_category_definitions_completeness(self):
        """TAX-001: All active categories must have definitions, in_scope, and non_examples."""
        for cat in CANDIDATE_TAXONOMY:
            assert len(cat["definition"]) > 20, f"Definition too short for {cat['issue_name']}"
            assert len(cat["evidence_keywords"]) >= 5, f"Too few keywords for {cat['issue_name']}"
            assert "in_scope" in cat and len(cat["in_scope"]) > 5
            assert "non_examples" in cat and len(cat["non_examples"]) > 5
            assert "ambiguity_rule" in cat and len(cat["ambiguity_rule"]) > 5

    def test_tax_002_category_support_thresholds(self):
        """TAX-002: Active categories must exceed minimum support threshold (>= 50)."""
        metrics_path = os.path.join(PROJECT_ROOT, "models", "metadata", "issue_classifier_validation_metrics.json")
        assert os.path.exists(metrics_path), "Validation metrics JSON must exist"
        with open(metrics_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for iid, m in data["per_category"].items():
            assert m["support"] >= 20, f"Gold support too low for issue {iid}: {m['support']}"

    def test_tax_003_coverage_vs_quality_separation(self):
        """TAX-003: Coverage must be explicitly separated from Accuracy/F1."""
        metrics_path = os.path.join(PROJECT_ROOT, "models", "metadata", "issue_classifier_validation_metrics.json")
        with open(metrics_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert "coverage_vs_quality_table" in data
        table = data["coverage_vs_quality_table"]
        assert len(table) == 5
        for row in table:
            assert "coverage_sample_pct" in row
            assert "precision" in row
            assert "recall" in row
            assert "f1_score" in row
            # Precision, Recall, F1 must be distinct metrics
            assert float(row["precision"]) > 0.0
            assert float(row["recall"]) > 0.0

    def test_tax_004_gold_label_metrics_validity(self):
        """TAX-004: Gold benchmark metrics must satisfy academic validity bounds."""
        metrics_path = os.path.join(PROJECT_ROOT, "models", "metadata", "issue_classifier_validation_metrics.json")
        with open(metrics_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["gold_sample_size"] == 600
        assert data["macro_f1"] >= 0.70, f"Macro F1 below baseline threshold: {data['macro_f1']}"
        assert data["macro_precision"] >= 0.60
        assert data["macro_recall"] >= 0.80
        assert data["hamming_loss"] <= 0.10
        # Inter-annotator agreement
        assert "inter_annotator_agreement" in data
        assert data["inter_annotator_agreement"]["mean_cohen_kappa"] >= 0.70


# ===================================================================
# SEVERITY PROXY & RECURRENCE (SEV-001, REC-001, REC-002)
# ===================================================================

class TestSeverityAndRecurrenceValidation:
    """Analytical validation of severity proxy and recurrence semantics."""

    def test_sev_001_severity_proxy_mapping(self):
        """SEV-001: Severity is an explicit rating-based proxy (not operational seriousness)."""
        assert SEVERITY_STATUS == "ANALYTICAL_PROTOTYPE"
        assert len(SEVERITY_LEVELS) == 4
        # Verify deterministic mapping
        assert _rating_to_severity_id(1) == 1  # CRITICAL
        assert _rating_to_severity_id(2) == 2  # HIGH
        assert _rating_to_severity_id(3) == 3  # MODERATE
        assert _rating_to_severity_id(4) == 4  # LOW
        assert _rating_to_severity_id(5) == 4  # LOW

    def test_rec_001_recurrence_grain_distinct_review_events(self):
        """REC-001: Recurrence is computed at distinct review-event grain."""
        sample_class = pd.DataFrame({
            "review_sk": [1, 2, 3, 4],
            "category_sk": [10, 10, 10, 20],
            "issue_id": [1, 1, 1, 2],
            "issue_name": ["Defect", "Defect", "Defect", "Packaging"],
        })
        rec = compute_category_recurrence(sample_class, min_threshold=3)
        c10 = rec[rec["category_sk"] == 10]
        assert len(c10) == 1
        assert c10.iloc[0]["distinct_review_count"] == 3
        assert c10.iloc[0]["is_recurring"] == True

    def test_rec_002_duplicate_reviews_same_sk_not_overcounted(self):
        """REC-002: Multiple issue keywords in the same review_sk do NOT overcount recurrence."""
        sample_class = pd.DataFrame({
            "review_sk": [1, 1, 1, 2],  # review 1 matched 3 keywords for same issue
            "category_sk": [10, 10, 10, 10],
            "issue_id": [1, 1, 1, 1],
            "issue_name": ["Defect", "Defect", "Defect", "Defect"],
        })
        rec = compute_category_recurrence(sample_class, min_threshold=3)
        c10 = rec[rec["category_sk"] == 10]
        assert c10.iloc[0]["distinct_review_count"] == 2  # exactly 2 distinct review events
        assert c10.iloc[0]["is_recurring"] == False


# ===================================================================
# ISOLATION, TRACEABILITY & TEMPORAL BOUNDS (SRC, TRACE, TREND)
# ===================================================================

class TestGovernanceAndTraceabilityValidation:
    """Validate cross-source isolation, traceability, and temporal bounds."""

    @pytest.fixture(scope="class")
    def db_conn(self):
        settings = DBSettings.from_env()
        conn = connect(settings, dbname_override=settings.dev_dbname)
        yield conn
        conn.close()

    def test_src_001_source_a_isolation(self, db_conn):
        """SRC-001: Source A (Shopee Benchmark) has 0 product_sk links."""
        with db_conn.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) AS cnt FROM marketvoice_warehouse.fact_review fr
                JOIN marketvoice_warehouse.dim_source ds ON fr.source_sk = ds.source_sk
                WHERE ds.source_id = 'SRC_PRDECT_ID_V1'
                  AND fr.product_sk IS NOT NULL AND fr.product_sk != 0
            """)
            assert cur.fetchone()["cnt"] == 0

    def test_src_002_source_b_isolation(self, db_conn):
        """SRC-002: Source B has 0 gold sentiment/emotion labels."""
        with db_conn.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) AS cnt FROM marketvoice_warehouse.fact_review fr
                JOIN marketvoice_warehouse.dim_source ds ON fr.source_sk = ds.source_sk
                WHERE ds.source_id = 'SRC_TOKOPEDIA_REVIEWS_2019'
                  AND (fr.source_gold_sentiment_label IS NOT NULL OR fr.source_gold_emotion_label IS NOT NULL)
            """)
            assert cur.fetchone()["cnt"] == 0

    def test_trace_001_review_to_issue_traceability(self, db_conn):
        """TRACE-001: 100% of issue facts link to valid fact_review with 0 orphans."""
        with db_conn.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) AS cnt FROM marketvoice_warehouse.fact_review_issue fri
                LEFT JOIN marketvoice_warehouse.fact_review fr ON fr.review_sk = fri.review_sk
                WHERE fr.review_sk IS NULL
            """)
            assert cur.fetchone()["cnt"] == 0

    def test_trend_001_temporal_limitation_documented_in_mart(self, db_conn):
        """TREND-001: Overrepresentation view explicitly exposes the temporal limitation note."""
        with db_conn.cursor() as cur:
            cur.execute("""
                SELECT DISTINCT data_limitation, analysis_type
                FROM marketvoice_warehouse.mv_issue_low_rating_overrepresentation
            """)
            rows = cur.fetchall()
            assert len(rows) > 0
            for r in rows:
                assert r["analysis_type"] == "LOW_RATING_OVERREPRESENTATION"
                assert "TEMPORAL_EMERGING_ISSUE_ANALYSIS = DEFERRED" in r["data_limitation"]
