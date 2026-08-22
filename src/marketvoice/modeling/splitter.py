"""Atomic-duplicate-safe stratified train/validation/test splitter.

Key invariant:
    All reviews sharing the same normalised text are assigned atomically
    to exactly ONE split partition.  Zero duplicate text leaks across
    train and test.

Uses the project canonical seed from config/project_settings.yaml (default_seed: 42).
"""
from __future__ import annotations

import hashlib
from typing import Dict, Tuple

import numpy as np
import pandas as pd


# Project canonical seed (from config/project_settings.yaml)
CANONICAL_SEED = 42

# Default split proportions
TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15


def _hash_text(text: str) -> str:
    """SHA-256 hash of normalised text for duplicate grouping."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def assign_duplicate_groups(
    df: pd.DataFrame,
    text_col: str = "review_text_norm",
) -> pd.DataFrame:
    """Assign a duplicate_group_id based on normalised review text.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain the *normalised* text column.
    text_col : str
        Column name holding normalised text.

    Returns
    -------
    pd.DataFrame
        Original frame with ``duplicate_group_id`` column added.
    """
    df = df.copy()
    df["duplicate_group_id"] = df[text_col].apply(_hash_text)
    return df


def stratified_group_split(
    df: pd.DataFrame,
    target_col: str,
    group_col: str = "duplicate_group_id",
    train_ratio: float = TRAIN_RATIO,
    val_ratio: float = VAL_RATIO,
    test_ratio: float = TEST_RATIO,
    seed: int = CANONICAL_SEED,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Split data into train / val / test with atomic duplicate grouping.

    Algorithm
    ---------
    1. For each duplicate group, determine the majority target label.
    2. Shuffle groups deterministically using the canonical seed.
    3. Assign entire groups to partitions in order, stratifying by the
       majority label, targeting the requested ratios.

    Parameters
    ----------
    df : pd.DataFrame
        Dataset with ``group_col`` and ``target_col``.
    target_col : str
        Column name of the classification target.
    group_col : str
        Column name of the duplicate group identifier.
    train_ratio, val_ratio, test_ratio : float
        Target proportions (must sum to 1.0).
    seed : int
        Random seed for reproducibility.

    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]
        (train_df, val_df, test_df) — each a subset of `df` with a
        ``split`` column added.
    """
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6, \
        "Split ratios must sum to 1.0"

    rng = np.random.RandomState(seed)

    # Step 1: Build group-level summary
    group_info = (
        df.groupby(group_col)
        .agg(
            group_size=(target_col, "size"),
            majority_label=(target_col, lambda x: x.mode().iloc[0]),
        )
        .reset_index()
    )

    # Step 2: Within each majority-label stratum, shuffle and assign groups
    train_groups, val_groups, test_groups = [], [], []

    for label, stratum in group_info.groupby("majority_label"):
        stratum = stratum.sample(frac=1.0, random_state=rng).reset_index(drop=True)
        n = len(stratum)
        n_train = int(round(n * train_ratio))
        n_val = int(round(n * val_ratio))
        # n_test = remainder

        train_groups.append(stratum.iloc[:n_train])
        val_groups.append(stratum.iloc[n_train : n_train + n_val])
        test_groups.append(stratum.iloc[n_train + n_val :])

    train_gids = set(pd.concat(train_groups)[group_col])
    val_gids = set(pd.concat(val_groups)[group_col])
    test_gids = set(pd.concat(test_groups)[group_col])

    # Verify no overlap
    assert len(train_gids & val_gids) == 0, "Train/Val group overlap detected!"
    assert len(train_gids & test_gids) == 0, "Train/Test group overlap detected!"
    assert len(val_gids & test_gids) == 0, "Val/Test group overlap detected!"

    # Step 3: Assign rows
    df = df.copy()
    df["split"] = "unassigned"
    df.loc[df[group_col].isin(train_gids), "split"] = "train"
    df.loc[df[group_col].isin(val_gids), "split"] = "val"
    df.loc[df[group_col].isin(test_gids), "split"] = "test"

    assert (df["split"] == "unassigned").sum() == 0, "Some rows were not assigned!"

    train_df = df[df["split"] == "train"].copy()
    val_df = df[df["split"] == "val"].copy()
    test_df = df[df["split"] == "test"].copy()

    return train_df, val_df, test_df


def split_diagnostics(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    test_df: pd.DataFrame,
    target_col: str,
) -> Dict:
    """Compute split diagnostic statistics.

    Returns
    -------
    dict
        Contains row counts, proportions, and per-class distributions.
    """
    total = len(train_df) + len(val_df) + len(test_df)
    diag = {
        "total_rows": total,
        "train_rows": len(train_df),
        "val_rows": len(val_df),
        "test_rows": len(test_df),
        "train_pct": round(len(train_df) / total * 100, 2),
        "val_pct": round(len(val_df) / total * 100, 2),
        "test_pct": round(len(test_df) / total * 100, 2),
        "train_class_dist": train_df[target_col].value_counts().to_dict(),
        "val_class_dist": val_df[target_col].value_counts().to_dict(),
        "test_class_dist": test_df[target_col].value_counts().to_dict(),
    }

    # Check for duplicate text leakage across train and test
    if "review_text_norm" in train_df.columns:
        train_texts = set(train_df["review_text_norm"])
        test_texts = set(test_df["review_text_norm"])
        diag["train_test_text_overlap"] = len(train_texts & test_texts)
    else:
        diag["train_test_text_overlap"] = "NOT_CHECKED"

    return diag
