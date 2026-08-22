"""Unsupervised aspect/issue taxonomy discovery from review text.

Phase 8 scope: discovery and candidate taxonomy formulation ONLY.
No supervised aspect classifier is trained in Phase 8.
Final aspect taxonomy is Phase 9 scope.
"""
from __future__ import annotations

import re
from collections import Counter
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


def extract_negative_reviews(
    df: pd.DataFrame,
    rating_col: str = "rating_value",
    text_col: str = "review_text_preprocessed",
    max_rating: int = 2,
) -> pd.DataFrame:
    """Filter reviews with rating <= max_rating (negative reviews)."""
    return df[df[rating_col] <= max_rating].copy()


def compute_ngram_frequencies(
    texts: pd.Series,
    ngram_range: Tuple[int, int] = (1, 3),
    top_n: int = 100,
    min_freq: int = 5,
) -> List[Dict]:
    """Compute n-gram frequency distribution over a text corpus.

    Parameters
    ----------
    texts : pd.Series of str
        Preprocessed review texts.
    ngram_range : tuple
        (min_n, max_n) for n-gram extraction.
    top_n : int
        Return top N most frequent n-grams.
    min_freq : int
        Minimum frequency threshold.

    Returns
    -------
    list of dict
        Each dict: {ngram, frequency, rank}.
    """
    counter = Counter()

    for text in texts.dropna():
        words = text.split()
        for n in range(ngram_range[0], ngram_range[1] + 1):
            for i in range(len(words) - n + 1):
                gram = " ".join(words[i : i + n])
                if len(gram) > 2:  # skip trivially short grams
                    counter[gram] += 1

    # Filter by min frequency
    filtered = [(gram, freq) for gram, freq in counter.most_common() if freq >= min_freq]

    results = []
    for rank, (gram, freq) in enumerate(filtered[:top_n], 1):
        results.append({"ngram": gram, "frequency": freq, "rank": rank})

    return results


def propose_candidate_taxonomy(
    ngram_results: List[Dict],
    source_label: str,
) -> List[Dict]:
    """Propose a candidate issue taxonomy based on observed keyword evidence.

    This is a CANDIDATE taxonomy for Phase 9 review and refinement.
    It is NOT a final supervised classifier.

    Returns
    -------
    list of dict
        Each dict: {category, definition, evidence_keywords, ambiguity_notes, status}.
    """
    # Common Indonesian complaint vocabulary clusters observed in marketplace reviews
    taxonomy_candidates = [
        {
            "category": "Product Defect / Quality",
            "definition": "Review indicates the received product has a physical defect, does not function as expected, or quality is below description.",
            "evidence_keywords": ["rusak", "cacat", "pecah", "patah", "jelek", "murahan",
                                  "tidak berfungsi", "mati", "error", "gagal", "palsu"],
            "ambiguity_notes": "May overlap with 'Order Inaccuracy' when wrong product is described as defective.",
            "status": "CANDIDATE_FOR_PHASE_9",
        },
        {
            "category": "Packaging / Shipping Damage",
            "definition": "Review indicates the packaging was damaged, insufficient, or the product was damaged during shipping.",
            "evidence_keywords": ["packing", "kemasan", "buble", "bubble", "kardus",
                                  "lecek", "penyok", "remuk", "hancur", "bocor"],
            "ambiguity_notes": "Distinguish packaging quality from product defect.",
            "status": "CANDIDATE_FOR_PHASE_9",
        },
        {
            "category": "Order Inaccuracy / Missing Items",
            "definition": "Review indicates the wrong product, wrong variant, wrong colour/size, or missing items were received.",
            "evidence_keywords": ["salah", "beda", "tidak sesuai", "kurang", "hilang",
                                  "ga sesuai", "gak sesuai", "warna beda", "ukuran salah"],
            "ambiguity_notes": "Distinguish from 'Product Defect' — wrong item vs defective correct item.",
            "status": "CANDIDATE_FOR_PHASE_9",
        },
        {
            "category": "Delivery / Shipping Delay",
            "definition": "Review indicates the delivery took significantly longer than expected or the order was delayed.",
            "evidence_keywords": ["lama", "lambat", "telat", "terlambat", "pengiriman lama",
                                  "belum sampai", "ga sampai"],
            "ambiguity_notes": "Delivery delay vs seller processing delay may require context.",
            "status": "CANDIDATE_FOR_PHASE_9",
        },
        {
            "category": "Customer Service / Seller Responsiveness",
            "definition": "Review indicates poor seller communication, unresponsive customer service, or complaint handling failure.",
            "evidence_keywords": ["respon", "slow respon", "slow response", "tidak merespon",
                                  "ga bales", "chat", "komplain", "retur"],
            "ambiguity_notes": "Distinguish seller responsiveness from marketplace platform issues.",
            "status": "CANDIDATE_FOR_PHASE_9",
        },
    ]

    # Match evidence keywords against actual ngram results
    observed_ngrams = {r["ngram"]: r["frequency"] for r in ngram_results}
    for cat in taxonomy_candidates:
        matched = []
        for kw in cat["evidence_keywords"]:
            for ngram, freq in observed_ngrams.items():
                if kw in ngram:
                    matched.append({"keyword": kw, "ngram_match": ngram, "frequency": freq})
                    break
        cat["matched_evidence"] = matched
        cat["evidence_coverage"] = len(matched)

    return taxonomy_candidates
