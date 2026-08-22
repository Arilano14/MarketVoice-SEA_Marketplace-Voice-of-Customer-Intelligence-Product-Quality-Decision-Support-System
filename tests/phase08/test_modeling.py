"""Phase 8 automated tests — Preprocessor, Splitter, Evaluator, Baselines.

Tests are deterministic, run without database access where possible,
and verify core modelling invariants.
"""
import os
import sys
import hashlib
import numpy as np
import pandas as pd
import pytest

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))
_PIPDEPS = os.path.join(PROJECT_ROOT, ".pipdeps")
if os.path.isdir(_PIPDEPS):
    sys.path.insert(0, _PIPDEPS)

from marketvoice.modeling.preprocessor import preprocess, normalise_for_dedup
from marketvoice.modeling.splitter import (
    CANONICAL_SEED,
    assign_duplicate_groups,
    stratified_group_split,
    split_diagnostics,
)
from marketvoice.modeling.baselines import MajorityClassifier, StratifiedPriorClassifier
from marketvoice.modeling.evaluator import evaluate_classification, format_report


# ===================================================================
# PREPROCESSOR TESTS
# ===================================================================

class TestPreprocessor:
    """Tests for deterministic text preprocessing."""

    def test_basic_lowercasing(self):
        assert preprocess("HELLO WORLD") == "hello world"

    def test_unicode_nfc_normalization(self):
        # Composed vs decomposed accent
        result1 = preprocess("café")
        result2 = preprocess("café")  # decomposed
        assert result1 == result2

    def test_whitespace_collapse(self):
        assert preprocess("hello   world  \t test") == "hello world test"

    def test_null_sentinels(self):
        for val in ["NULL", "None", "nan", "N/A", "", "  "]:
            assert preprocess(val) == "", f"Expected empty for sentinel: {repr(val)}"

    def test_non_string_returns_empty(self):
        assert preprocess(None) == ""
        assert preprocess(123) == ""

    def test_determinism(self):
        text = "Barang bagus! Pengiriman cepat 😊"
        assert preprocess(text) == preprocess(text)

    def test_preserves_exclamation(self):
        result = preprocess("Bagus sekali!")
        assert "!" in result, "Exclamation mark should be preserved for sentiment"

    def test_preserves_emoji(self):
        result = preprocess("Bagus 😊")
        assert "😊" in result, "Emoji should be preserved for sentiment"


class TestNormaliseForDedup:
    """Tests for dedup normalisation."""

    def test_strips_punctuation(self):
        result = normalise_for_dedup("hello, world!")
        assert "," not in result
        assert "!" not in result

    def test_collapses_to_same(self):
        t1 = normalise_for_dedup("Bagus sekali!!!")
        t2 = normalise_for_dedup("bagus sekali")
        assert t1 == t2

    def test_different_texts_differ(self):
        t1 = normalise_for_dedup("produk bagus")
        t2 = normalise_for_dedup("produk jelek")
        assert t1 != t2


# ===================================================================
# SPLITTER TESTS
# ===================================================================

class TestSplitter:
    """Tests for atomic duplicate-safe stratified splitting."""

    @pytest.fixture
    def sample_df(self):
        """Create a sample DataFrame with some duplicates."""
        np.random.seed(CANONICAL_SEED)
        texts = [f"review text {i}" for i in range(100)]
        # Add some duplicates
        texts[10] = texts[0]
        texts[20] = texts[0]
        texts[30] = texts[1]
        df = pd.DataFrame({
            "review_text_norm": texts,
            "rating_value": np.random.choice([1, 2, 3, 4, 5], size=100),
        })
        return assign_duplicate_groups(df, text_col="review_text_norm")

    def test_canonical_seed_is_42(self):
        assert CANONICAL_SEED == 42

    def test_no_split_overlap(self, sample_df):
        train, val, test = stratified_group_split(
            sample_df, target_col="rating_value", seed=CANONICAL_SEED
        )
        train_groups = set(train["duplicate_group_id"])
        val_groups = set(val["duplicate_group_id"])
        test_groups = set(test["duplicate_group_id"])
        assert len(train_groups & val_groups) == 0, "Train/Val groups overlap!"
        assert len(train_groups & test_groups) == 0, "Train/Test groups overlap!"
        assert len(val_groups & test_groups) == 0, "Val/Test groups overlap!"

    def test_all_rows_assigned(self, sample_df):
        train, val, test = stratified_group_split(
            sample_df, target_col="rating_value", seed=CANONICAL_SEED
        )
        assert len(train) + len(val) + len(test) == len(sample_df)

    def test_duplicate_texts_same_split(self, sample_df):
        train, val, test = stratified_group_split(
            sample_df, target_col="rating_value", seed=CANONICAL_SEED
        )
        combined = pd.concat([train, val, test])
        for gid, group in combined.groupby("duplicate_group_id"):
            splits = group["split"].unique()
            assert len(splits) == 1, f"Group {gid} appears in {splits}"

    def test_split_proportions_approximate(self, sample_df):
        train, val, test = stratified_group_split(
            sample_df, target_col="rating_value", seed=CANONICAL_SEED
        )
        total = len(train) + len(val) + len(test)
        assert 0.60 <= len(train) / total <= 0.80
        assert 0.08 <= len(val) / total <= 0.22
        assert 0.08 <= len(test) / total <= 0.22

    def test_reproducibility(self, sample_df):
        t1, v1, te1 = stratified_group_split(
            sample_df, target_col="rating_value", seed=CANONICAL_SEED
        )
        t2, v2, te2 = stratified_group_split(
            sample_df, target_col="rating_value", seed=CANONICAL_SEED
        )
        assert list(t1["review_text_norm"]) == list(t2["review_text_norm"])

    def test_diagnostics_no_text_overlap(self, sample_df):
        train, val, test = stratified_group_split(
            sample_df, target_col="rating_value", seed=CANONICAL_SEED
        )
        diag = split_diagnostics(train, val, test, "rating_value")
        assert diag["train_test_text_overlap"] == 0


# ===================================================================
# BASELINE TESTS
# ===================================================================

class TestBaselines:
    """Tests for Level 0 naive baselines."""

    def test_majority_predicts_most_frequent(self):
        y = np.array([1, 1, 1, 2, 2, 3])
        clf = MajorityClassifier().fit(y)
        preds = clf.predict(5)
        assert all(p == 1 for p in preds)

    def test_stratified_distribution(self):
        y = np.array([1] * 50 + [2] * 30 + [3] * 20)
        clf = StratifiedPriorClassifier(seed=42).fit(y)
        preds = clf.predict(10000)
        # Check proportions are approximately correct
        counts = pd.Series(preds).value_counts(normalize=True)
        assert abs(counts.get(1, 0) - 0.5) < 0.05
        assert abs(counts.get(2, 0) - 0.3) < 0.05
        assert abs(counts.get(3, 0) - 0.2) < 0.05

    def test_stratified_reproducibility(self):
        y = np.array([1, 2, 3, 1, 2, 3])
        clf = StratifiedPriorClassifier(seed=42).fit(y)
        p1 = clf.predict(100)
        p2 = clf.predict(100)
        assert list(p1) == list(p2)


# ===================================================================
# EVALUATOR TESTS
# ===================================================================

class TestEvaluator:
    """Tests for multi-metric evaluation engine."""

    def test_perfect_predictions(self):
        y = np.array([1, 2, 3, 4, 5])
        metrics = evaluate_classification(y, y, labels=[1, 2, 3, 4, 5])
        assert metrics["accuracy"] == 1.0
        assert metrics["macro_f1"] == 1.0

    def test_ordinal_metrics_included(self):
        y_true = np.array([1, 2, 3, 4, 5])
        y_pred = np.array([1, 2, 3, 4, 5])
        metrics = evaluate_classification(y_true, y_pred, task_type="ordinal")
        assert "qwk" in metrics
        assert "mae" in metrics
        assert metrics["qwk"] == 1.0
        assert metrics["mae"] == 0.0

    def test_confusion_matrix_shape(self):
        y_true = np.array([1, 2, 3, 1, 2])
        y_pred = np.array([1, 2, 3, 2, 1])
        metrics = evaluate_classification(y_true, y_pred, labels=[1, 2, 3])
        cm = metrics["confusion_matrix"]
        assert len(cm) == 3
        assert len(cm[0]) == 3

    def test_per_class_keys(self):
        y_true = np.array([1, 2, 3])
        y_pred = np.array([1, 2, 2])
        metrics = evaluate_classification(y_true, y_pred, labels=[1, 2, 3])
        assert "1" in metrics["per_class"]
        assert "2" in metrics["per_class"]
        assert "3" in metrics["per_class"]

    def test_format_report_not_empty(self):
        y = np.array([1, 2, 1, 2])
        metrics = evaluate_classification(y, y)
        report = format_report(metrics, "Test")
        assert len(report) > 0
        assert "Test" in report


# ===================================================================
# DATA INTEGRITY TESTS (require database)
# ===================================================================

class TestDataIntegrity:
    """Integration tests verifying data loading from warehouse."""

    @pytest.fixture(scope="class")
    def source_a_df(self):
        from marketvoice.modeling.data_loader import load_reviews, SOURCE_A
        return load_reviews(SOURCE_A)

    @pytest.fixture(scope="class")
    def source_b_df(self):
        from marketvoice.modeling.data_loader import load_reviews, SOURCE_B
        return load_reviews(SOURCE_B)

    def test_source_a_row_count(self, source_a_df):
        assert len(source_a_df) == 5400

    def test_source_b_row_count(self, source_b_df):
        assert len(source_b_df) == 40607

    def test_source_a_no_null_text(self, source_a_df):
        null_count = source_a_df["review_text"].isna().sum()
        empty_count = (source_a_df["review_text"] == "").sum()
        assert null_count == 0
        assert empty_count == 0

    def test_source_a_gold_labels_complete(self, source_a_df):
        assert source_a_df["source_gold_sentiment_label"].isna().sum() == 0
        assert source_a_df["source_gold_emotion_label"].isna().sum() == 0

    def test_source_b_no_gold_labels(self, source_b_df):
        # Source B should NOT have gold sentiment/emotion labels
        null_sent = source_b_df["source_gold_sentiment_label"].isna().sum()
        null_emo = source_b_df["source_gold_emotion_label"].isna().sum()
        assert null_sent == len(source_b_df)

    def test_no_cross_source_contamination(self, source_a_df, source_b_df):
        a_ids = set(source_a_df["review_sk"])
        b_ids = set(source_b_df["review_sk"])
        assert len(a_ids & b_ids) == 0, "review_sk overlap between sources!"

    def test_distinct_texts_exist(self, source_a_df):
        unique_texts = source_a_df["review_text"].nunique()
        assert unique_texts > 100, f"Too few unique texts: {unique_texts}"


# ===================================================================
# MODEL RESULTS VALIDATION (post-experiment)
# ===================================================================

class TestModelResults:
    """Validate that model card files and results JSON exist and are valid."""

    @pytest.fixture(scope="class")
    def results(self):
        results_path = os.path.join(PROJECT_ROOT, "models", "metadata", "phase8_experiment_results.json")
        if not os.path.exists(results_path):
            pytest.skip("Experiment results not yet generated")
        import json
        with open(results_path) as f:
            return json.load(f)

    def test_results_file_exists(self, results):
        assert results is not None

    def test_rating_source_a_champion_beats_majority(self, results):
        maj_f1 = results["rating_source_a"]["models"]["majority_baseline"]["val_metrics"]["macro_f1"]
        champ_f1 = results["rating_source_a"]["champion_val_metrics"]["macro_f1"]
        assert champ_f1 > maj_f1, "Champion must beat majority baseline!"

    def test_rating_source_b_champion_beats_majority(self, results):
        maj_f1 = results["rating_source_b"]["models"]["majority_baseline"]["val_metrics"]["macro_f1"]
        champ_f1 = results["rating_source_b"]["champion_val_metrics"]["macro_f1"]
        assert champ_f1 > maj_f1, "Champion must beat majority baseline!"

    def test_sentiment_holdout_accuracy_above_90(self, results):
        acc = results["sentiment_benchmark"]["holdout_metrics"]["accuracy"]
        assert acc >= 0.90, f"Sentiment accuracy {acc} below 90% threshold"

    def test_zero_train_test_text_overlap_source_a(self, results):
        overlap = results["rating_source_a"]["split_diagnostics"]["train_test_text_overlap"]
        assert overlap == 0

    def test_zero_train_test_text_overlap_source_b(self, results):
        overlap = results["rating_source_b"]["split_diagnostics"]["train_test_text_overlap"]
        assert overlap == 0

    def test_aspect_discovery_generated(self, results):
        assert results["aspect_discovery_a"]["status"] == "CANDIDATE_TAXONOMY_GENERATED"
        assert results["aspect_discovery_b"]["status"] == "CANDIDATE_TAXONOMY_GENERATED"

    def test_model_cards_exist(self):
        metadata_dir = os.path.join(PROJECT_ROOT, "models", "metadata")
        json_files = [f for f in os.listdir(metadata_dir) if f.endswith(".json") and f != "phase8_experiment_results.json"]
        assert len(json_files) >= 4, f"Expected >= 4 model cards, found {len(json_files)}"
