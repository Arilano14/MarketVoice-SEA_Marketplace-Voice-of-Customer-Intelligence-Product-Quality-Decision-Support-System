"""
Dataset registration and SHA256 checksum calculation utility.
Audits raw datasets in data/raw/ and records size, checksum, and registration status.
"""

import hashlib
from pathlib import Path


def calculate_sha256(file_path: Path) -> str:
    """Compute SHA256 hash of a target file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def audit_raw_data():
    """Inspect data/raw subdirectories and report file checksums."""
    root = Path(__file__).resolve().parents[2]
    raw_dir = root / "data/raw"

    print("=" * 70)
    print("MARKETVOICE SEA — DUAL-SOURCE DATASET REGISTRATION AUDIT")
    print("=" * 70)

    if not raw_dir.exists():
        print("ERROR: data/raw directory does not exist.")
        return

    raw_files = [f for f in raw_dir.glob("**/*") if f.is_file() and f.name != "README.md"]

    if not raw_files:
        print("STATUS: data/raw/ landing areas are currently empty.")
        print("INSTRUCTION: Place raw CSV files in data/raw/prdect_id/ and data/raw/tokopedia_product_reviews_2019/.")
        return

    for file in sorted(raw_files):
        rel_path = file.relative_to(root)
        size = file.stat().st_size
        checksum = calculate_sha256(file)
        print(f"File: {rel_path}")
        print(f"  Size: {size:,} bytes")
        print(f"  SHA256: {checksum}")
        print("-" * 70)


if __name__ == "__main__":
    audit_raw_data()
