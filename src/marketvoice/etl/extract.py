"""Extract module — CSV read with strict UTF-8 (§21) and SHA256 verify (§26).

Never uses errors='replace'. Decode failure → CRITICAL BLOCK_LOAD.
"""
from __future__ import annotations

import csv
import hashlib
import os
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class SourceFile:
    """Registered source file with manifest reference."""
    source_id: str
    file_path: str
    expected_sha256: str
    expected_row_count: int
    expected_column_count: int


# ─── Manifest-registered sources ──────────────────────────────────
SOURCE_A = SourceFile(
    source_id="SRC_PRDECT_ID_V1",
    file_path=os.path.join("data", "raw", "prdect_id", "PRDECT-ID Dataset.csv"),
    expected_sha256="1dfdde6bb169ad57aab4211ecf45a75a4111b774ab43932f6d39c349bfd92bde",
    expected_row_count=5400,
    expected_column_count=11,
)

SOURCE_B = SourceFile(
    source_id="SRC_TOKOPEDIA_REVIEWS_2019",
    file_path=os.path.join("data", "raw", "tokopedia_product_reviews_2019",
                           "tokopedia-product-reviews-2019.csv"),
    expected_sha256="dbffc29078db1894e60884c526fe4d0ccbc592f33fe95d2e5ac2d8f96336b7ed",
    expected_row_count=40607,
    expected_column_count=8,
)

# Source A columns (index order)
_A_COLS = [
    "Category", "Product Name", "Location", "Price", "Overall Rating",
    "Number Sold", "Total Review", "Customer Rating", "Customer Review",
    "Sentiment", "Emotion",
]

# Source B columns (index order)
_B_COLS = [
    "text", "rating", "category", "product_name", "product_id",
    "sold", "shop_id", "product_url",
]


class SHA256Mismatch(Exception):
    """§26 Raw data integrity failure. CRITICAL → STOP."""


class DecodeError(Exception):
    """§21 UTF-8 decode failure. CRITICAL → BLOCK_LOAD."""


def compute_sha256(filepath: str) -> str:
    """Compute SHA256 hex digest for a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def verify_sha256(source: SourceFile, project_root: str) -> str:
    """§26 Compare SHA256 against manifest. Raises SHA256Mismatch on failure.

    Returns: actual SHA256 hex string.
    """
    abs_path = os.path.join(project_root, source.file_path)
    actual = compute_sha256(abs_path)
    if actual != source.expected_sha256:
        raise SHA256Mismatch(
            f"§26 CRITICAL: {source.source_id} SHA256 mismatch. "
            f"expected={source.expected_sha256} actual={actual}"
        )
    return actual


def read_csv_strict(source: SourceFile, project_root: str) -> tuple[list[str], list[dict]]:
    """Read CSV with strict UTF-8 (§21). No errors='replace'.

    Returns: (header_list, list_of_row_dicts_with_added_meta)
    Each row dict has:
      - all original columns (by name)
      - _source_row_number: 1-indexed stable row number (data rows only; header=0)
      - _source_id: source identifier
    """
    abs_path = os.path.join(project_root, source.file_path)

    # §21 strict decode — no errors='replace'
    try:
        with open(abs_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)

            # Validate column count
            if len(header) != source.expected_column_count:
                raise ValueError(
                    f"Column count mismatch for {source.source_id}: "
                    f"expected={source.expected_column_count} got={len(header)}"
                )

            rows = []
            for row_num_0, values in enumerate(reader, start=1):
                row_dict = {}
                for i, col_name in enumerate(header):
                    row_dict[col_name] = values[i] if i < len(values) else None
                row_dict["_source_row_number"] = row_num_0
                row_dict["_source_id"] = source.source_id
                rows.append(row_dict)

    except UnicodeDecodeError as exc:
        raise DecodeError(
            f"§21 CRITICAL BLOCK_LOAD: UTF-8 decode error in {source.source_id}: {exc}"
        ) from exc

    return header, rows


def extract_all(project_root: str) -> dict:
    """Extract both sources with SHA256 pre-verification.

    Returns dict with keys:
      source_a_sha256, source_b_sha256,
      source_a_header, source_b_header,
      source_a_rows, source_b_rows,
      source_a_row_count, source_b_row_count
    """
    # §26 SHA256 pre-ETL verification
    sha_a = verify_sha256(SOURCE_A, project_root)
    sha_b = verify_sha256(SOURCE_B, project_root)

    header_a, rows_a = read_csv_strict(SOURCE_A, project_root)
    header_b, rows_b = read_csv_strict(SOURCE_B, project_root)

    return {
        "source_a_sha256": sha_a,
        "source_b_sha256": sha_b,
        "source_a_header": header_a,
        "source_b_header": header_b,
        "source_a_rows": rows_a,
        "source_b_rows": rows_b,
        "source_a_row_count": len(rows_a),
        "source_b_row_count": len(rows_b),
    }


__all__ = [
    "SourceFile", "SOURCE_A", "SOURCE_B",
    "SHA256Mismatch", "DecodeError",
    "compute_sha256", "verify_sha256",
    "read_csv_strict", "extract_all",
]
