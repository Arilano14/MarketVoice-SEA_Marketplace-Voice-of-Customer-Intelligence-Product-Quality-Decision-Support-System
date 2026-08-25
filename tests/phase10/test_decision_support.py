"""Phase 10 Automated Test Suite — Decision Support System & Priority Scoring.

Verifies:
  1. Deterministic priority scoring and bounding [0, 100].
  2. Feature normalization scaling transforms.
  3. Reason code deterministic attribution.
  4. Decision queue generation across isolated grains (Product, Category, Source).
  5. Baseline policy benchmarking engine.
  6. Monte Carlo sensitivity analysis & rank stability.
  7. Database schema, table counts, foreign keys, and analytical mart views.
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

from marketvoice.decision.priority_score import (
    DEFAULT_WEIGHTS,
    CALCULATION_VERSION,
    normalize_feature,
    compute_priority_score,
)
from marketvoice.decision.reason_codes import (
    REASON_CODES,
    generate_reason_codes,
    format_decision_explanation,
)
from marketvoice.decision.decision_queue import (
    PRIORITY_TIERS,
    score_to_tier,
    generate_decision_queue_product,
    generate_decision_queue_category,
    generate_decision_queue_source,
)
from marketvoice.decision.benchmarking import evaluate_policy_benchmarks
from marketvoice.decision.sensitivity_analysis import run_monte_carlo_sensitivity
from marketvoice.database.connection import DBSettings, connect
from marketvoice.database.schema import SCHEMA


# ===================================================================
# 1. PRIORITY SCORING ENGINE TESTS
# ===================================================================

class TestPriorityScoringEngine:
    """Test priority scoring mathematical invariants."""

    def test_weights_sum_to_one(self):
        total = sum(DEFAULT_WEIGHTS.values())
        assert pytest.approx(total, rel=1e-4) == 1.0

    def test_normalization_bounds(self):
        # Severity
        assert normalize_feature(0.0, "severity") == 0.0
        assert normalize_feature(1.0, "severity") == 1.0
        assert normalize_feature(1.5, "severity") == 1.0  # clipped

        # Dissatisfaction
        assert normalize_feature(1.0, "dissatisfaction") == 0.0
        assert normalize_feature(4.0, "dissatisfaction") == 1.0
        assert normalize_feature(6.0, "dissatisfaction") == 1.0  # clipped

        # Recurrence
        assert normalize_feature(0, "recurrence") == 0.0
        assert 0.0 < normalize_feature(10, "recurrence") < 1.0

        # Volume
        assert normalize_feature(0, "volume") == 0.0
        assert 0.0 < normalize_feature(100, "volume") < 1.0

        # Confidence
        assert normalize_feature(0.3333, "confidence") == pytest.approx(0.0, abs=1e-3)
        assert normalize_feature(1.0, "confidence") == 1.0

    def test_deterministic_score_calculation(self):
        scores = compute_priority_score(
            severity_ratio=0.60,
            dissatisfaction_ratio=3.0,
            recurrence_count=10,
            volume=50,
            confidence=0.80,
        )
        assert 0.0 <= scores["priority_score"] <= 100.0
        assert 0.0 <= scores["severity_impact_score"] <= 100.0
        assert 0.0 <= scores["dissatisfaction_score"] <= 100.0
        assert 0.0 <= scores["recurrence_score"] <= 100.0
        assert 0.0 <= scores["volume_score"] <= 100.0
        assert 0.0 <= scores["confidence_score"] <= 100.0

    def test_score_monotonicity(self):
        low = compute_priority_score(0.1, 1.0, 1, 5, 0.4)
        high = compute_priority_score(0.9, 4.0, 50, 500, 0.9)
        assert high["priority_score"] > low["priority_score"]


# ===================================================================
# 2. REASON CODES TESTS
# ===================================================================

class TestReasonCodesEngine:
    """Test explainable reason code generation."""

    def test_reason_codes_registry(self):
        assert len(REASON_CODES) >= 6
        assert "RC_CRITICAL_SEVERITY_DOMINANCE" in REASON_CODES
        assert "RC_HIGH_DISSATISFACTION_DRIVER" in REASON_CODES

    def test_reason_code_triggers(self):
        rcs = generate_reason_codes(
            severity_ratio=0.75,
            dissatisfaction_ratio=3.5,
            recurrence_count=12,
            volume=150,
            confidence=0.85,
            z_score=5.2,
        )
        assert "RC_CRITICAL_SEVERITY_DOMINANCE" in rcs
        assert "RC_HIGH_DISSATISFACTION_DRIVER" in rcs
        assert "RC_CHRONIC_EVENT_RECURRENCE" in rcs
        assert "RC_BROAD_EVIDENCE_SUPPORT" in rcs
        assert "RC_HIGH_CONFIDENCE_SIGNAL" in rcs

    def test_small_sample_trigger(self):
        rcs = generate_reason_codes(0.2, 1.0, 1, 2, 0.4)
        assert "RC_SMALL_SAMPLE_CAUTION" in rcs

    def test_explanation_formatter(self):
        explanation = format_decision_explanation(
            "HP Cartridge", "Product Defect", "P1_CRITICAL", 82.5,
            ["RC_CRITICAL_SEVERITY_DOMINANCE", "RC_CHRONIC_EVENT_RECURRENCE"]
        )
        assert "HP Cartridge" in explanation
        assert "P1_CRITICAL" in explanation
        assert "Critical Severity Dominance" in explanation


# ===================================================================
# 3. BENCHMARKING & SENSITIVITY TESTS
# ===================================================================

class TestBenchmarkingAndSensitivity:
    """Test policy comparisons and Monte Carlo sensitivity."""

    @pytest.fixture
    def sample_queue(self):
        np.random.seed(42)
        n = 100
        sev = np.random.uniform(0, 100, n)
        dis = np.random.uniform(0, 100, n)
        rec = np.random.uniform(0, 100, n)
        vol = np.random.uniform(0, 100, n)
        cnf = np.random.uniform(0, 100, n)

        prs = (
            DEFAULT_WEIGHTS["severity"] * sev
            + DEFAULT_WEIGHTS["dissatisfaction"] * dis
            + DEFAULT_WEIGHTS["recurrence"] * rec
            + DEFAULT_WEIGHTS["volume"] * vol
            + DEFAULT_WEIGHTS["confidence"] * cnf
        )

        return pd.DataFrame({
            "product_sk": list(range(1, n + 1)),
            "issue_id": [1] * n,
            "priority_score": prs,
            "evidence_support": np.random.randint(1, 200, n),
            "distinct_review_events": np.random.randint(1, 50, n),
            "critical_severity_count": np.random.randint(0, 30, n),
            "severity_impact_score": sev,
            "dissatisfaction_score": dis,
            "recurrence_score": rec,
            "volume_score": vol,
            "confidence_score": cnf,
        })

    def test_policy_benchmarking(self, sample_queue):
        res = evaluate_policy_benchmarks(sample_queue)
        assert res["evaluation_type"] == "SIMULATED_DECISION_EVALUATION"
        assert "policy_metrics" in res
        assert "Proposed_MultiFactor_DSS" in res["policy_metrics"]
        assert "Baseline_Volume_Only" in res["policy_metrics"]
        assert "Baseline_Severity_Only" in res["policy_metrics"]
        assert "Baseline_FIFO_Default" in res["policy_metrics"]

    def test_monte_carlo_sensitivity(self, sample_queue):
        sens = run_monte_carlo_sensitivity(sample_queue, n_simulations=100, seed=42)
        assert sens["mean_kendall_tau"] > 0.70
        assert sens["mean_spearman_rho"] > 0.85
        assert sens["stability_classification"] in ["HIGH", "MODERATE"]


# ===================================================================
# 4. DATABASE INTEGRATION & RECONCILIATION TESTS
# ===================================================================

class TestDatabaseIntegration:
    """Test database tables, views, and integrity."""

    @pytest.fixture(scope="class")
    def db_conn(self):
        settings = DBSettings.from_env()
        conn = connect(settings, dbname_override=settings.dev_dbname)
        yield conn
        conn.close()

    def test_fact_review_unchanged(self, db_conn):
        with db_conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS cnt FROM marketvoice_warehouse.fact_review")
            assert cur.fetchone()["cnt"] == 46007

    def test_fact_review_issue_unchanged(self, db_conn):
        with db_conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS cnt FROM marketvoice_warehouse.fact_review_issue")
            assert cur.fetchone()["cnt"] == 18863

    def test_fact_decision_queue_populated(self, db_conn):
        with db_conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS cnt FROM marketvoice_warehouse.fact_decision_queue")
            cnt = cur.fetchone()["cnt"]
            assert cnt == 5090, f"Expected 5090 decision cases, got {cnt}"

    def test_grain_counts(self, db_conn):
        with db_conn.cursor() as cur:
            cur.execute("""
                SELECT grain_type, COUNT(*) AS cnt
                FROM marketvoice_warehouse.fact_decision_queue
                GROUP BY grain_type
            """)
            grains = {r["grain_type"]: r["cnt"] for r in cur.fetchall()}
            assert grains["PRODUCT_X_ISSUE"] == 4913
            assert grains["CATEGORY_X_ISSUE"] == 167
            assert grains["SOURCE_X_ISSUE"] == 10

    def test_zero_orphans(self, db_conn):
        with db_conn.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) AS cnt FROM marketvoice_warehouse.fact_decision_queue fdq
                LEFT JOIN marketvoice_warehouse.dim_product dp ON dp.product_sk = fdq.product_sk
                WHERE fdq.product_sk IS NOT NULL AND dp.product_sk IS NULL
            """)
            assert cur.fetchone()["cnt"] == 0

    def test_scores_in_bounds(self, db_conn):
        with db_conn.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) AS cnt FROM marketvoice_warehouse.fact_decision_queue
                WHERE priority_score < 0.0 OR priority_score > 100.0
            """)
            assert cur.fetchone()["cnt"] == 0

    def test_mv_priority_product_queue_view(self, db_conn):
        with db_conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS cnt FROM marketvoice_warehouse.mv_priority_product_queue")
            assert cur.fetchone()["cnt"] == 4913

    def test_mv_priority_category_queue_view(self, db_conn):
        with db_conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS cnt FROM marketvoice_warehouse.mv_priority_category_queue")
            assert cur.fetchone()["cnt"] == 167

    def test_mv_product_risk_index_view(self, db_conn):
        with db_conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS cnt FROM marketvoice_warehouse.mv_product_risk_index")
            cnt = cur.fetchone()["cnt"]
            assert cnt > 1000
