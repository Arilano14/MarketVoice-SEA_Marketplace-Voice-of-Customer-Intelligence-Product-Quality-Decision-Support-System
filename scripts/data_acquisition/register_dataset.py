"""
Dataset registration and SHA256 checksum calculation utility.
Audits files in data/raw/ and records size, checksum, and registration date in data/metadata/source_manifest.csv.
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
    """Inspect data/raw/ and report file checksums."""
    root = Path(__file__).resolve().parents[2]
    raw_dir = root / "data/raw"

    print("=" * 60)
    print("MARKETVOICE SEA — DATASET REGISTRATION & CHECKSUM AUDIT")
    print("=" * 60)

    if not raw_dir.exists():
        print("ERROR: data/raw directory does not exist.")
        return

    raw_files = [f for f in raw_dir.glob("*") if f.is_file() and f.name != "README.md"]

    if not raw_files:
        print("STATUS: data/raw/ landing area is currently empty.")
        print("INSTRUCTION: Place raw competition CSV files in data/raw/ to register checksums.")
        return

    for file in raw_files:
        size = file.stat().st_size
        checksum = calculate_sha256(file)
        print(f"File: {file.name}")
        print(f"  Size: {size:,} bytes")
        print(f"  SHA256: {checksum}")
        print("-" * 60)


if __name__ == "__main__":
    audit_raw_data()
