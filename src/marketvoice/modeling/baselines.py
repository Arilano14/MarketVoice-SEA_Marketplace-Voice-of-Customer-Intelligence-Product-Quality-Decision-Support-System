"""Naive baseline classifiers for lower-bound reference.

Implements Level 0 baselines per experiment_protocol.md:
  - Majority-class classifier
  - Stratified-prior random classifier
"""
from __future__ import annotations

from typing import List, Optional

import numpy as np

from marketvoice.modeling.splitter import CANONICAL_SEED


class MajorityClassifier:
    """Predicts the most frequent training label for every sample."""

    def __init__(self):
        self.majority_label = None

    def fit(self, y_train: np.ndarray) -> "MajorityClassifier":
        values, counts = np.unique(y_train, return_counts=True)
        self.majority_label = values[np.argmax(counts)]
        return self

    def predict(self, n: int) -> np.ndarray:
        return np.full(n, self.majority_label)

    def __repr__(self):
        return f"MajorityClassifier(majority_label={self.majority_label})"


class StratifiedPriorClassifier:
    """Predicts by randomly sampling from the training class distribution."""

    def __init__(self, seed: int = CANONICAL_SEED):
        self.class_probs = None
        self.classes = None
        self.seed = seed

    def fit(self, y_train: np.ndarray) -> "StratifiedPriorClassifier":
        values, counts = np.unique(y_train, return_counts=True)
        self.classes = values
        self.class_probs = counts / counts.sum()
        return self

    def predict(self, n: int) -> np.ndarray:
        rng = np.random.RandomState(self.seed)
        return rng.choice(self.classes, size=n, p=self.class_probs)

    def __repr__(self):
        return f"StratifiedPriorClassifier(classes={list(self.classes)})"
