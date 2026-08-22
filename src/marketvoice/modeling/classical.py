"""Classical sparse-text classification models (Level 1).

Implements TF-IDF + Logistic Regression and TF-IDF + LinearSVC
per experiment_protocol.md candidate sequence.

Fitting is done on TRAINING data only.  Vectoriser vocabulary
is frozen after fit; validation/test transforms use the frozen
vocabulary.

Uses the project canonical seed (42).
"""
from __future__ import annotations

import os
import sys
from typing import Any, Dict, Optional, Tuple

import numpy as np

_PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)
_PIPDEPS = os.path.join(_PROJECT_ROOT, ".pipdeps")
if os.path.isdir(_PIPDEPS) and _PIPDEPS not in sys.path:
    sys.path.insert(0, _PIPDEPS)

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV

from marketvoice.modeling.splitter import CANONICAL_SEED


def build_tfidf_vectorizer(
    max_features: int = 50_000,
    ngram_range_word: Tuple[int, int] = (1, 2),
    ngram_range_char: Tuple[int, int] = (3, 5),
    sublinear_tf: bool = True,
) -> TfidfVectorizer:
    """Build a TF-IDF vectoriser combining word and character n-grams.

    Character n-grams capture morphological variants and typos common
    in Indonesian marketplace text without requiring explicit stemming.
    """
    return TfidfVectorizer(
        analyzer="word",
        ngram_range=ngram_range_word,
        max_features=max_features,
        sublinear_tf=sublinear_tf,
        min_df=2,
        strip_accents="unicode",
    )


def build_tfidf_char_vectorizer(
    max_features: int = 50_000,
    ngram_range: Tuple[int, int] = (3, 5),
    sublinear_tf: bool = True,
) -> TfidfVectorizer:
    """Build a character-level TF-IDF vectoriser."""
    return TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=ngram_range,
        max_features=max_features,
        sublinear_tf=sublinear_tf,
        min_df=2,
    )


def train_logistic_regression(
    X_train,
    y_train,
    class_weight: Optional[str] = "balanced",
    max_iter: int = 1000,
    C: float = 1.0,
    seed: int = CANONICAL_SEED,
) -> LogisticRegression:
    """Train Logistic Regression with balanced class weights."""
    model = LogisticRegression(
        C=C,
        class_weight=class_weight,
        max_iter=max_iter,
        random_state=seed,
        solver="lbfgs",
        multi_class="multinomial",
        n_jobs=-1,
    )
    model.fit(X_train, y_train)
    return model


def train_linear_svc(
    X_train,
    y_train,
    class_weight: Optional[str] = "balanced",
    max_iter: int = 2000,
    C: float = 1.0,
    seed: int = CANONICAL_SEED,
) -> CalibratedClassifierCV:
    """Train LinearSVC wrapped with Platt calibration for probability output.

    LinearSVC does not natively support predict_proba; wrapping with
    CalibratedClassifierCV provides calibrated probabilities for
    downstream confidence analysis.
    """
    base_svc = LinearSVC(
        C=C,
        class_weight=class_weight,
        max_iter=max_iter,
        random_state=seed,
        dual="auto",
    )
    # Use 3-fold calibration on training data
    calibrated = CalibratedClassifierCV(base_svc, cv=3, method="sigmoid")
    calibrated.fit(X_train, y_train)
    return calibrated
