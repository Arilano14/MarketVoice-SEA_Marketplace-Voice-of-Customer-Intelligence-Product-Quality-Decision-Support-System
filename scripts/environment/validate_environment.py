"""
Environment validation script for MarketVoice SEA (Phase 1).
Verifies Python version, directory structure, pyproject.toml, and configuration files.
"""

import sys
from pathlib import Path


def check_python_version() -> bool:
    """Ensure Python version is >= 3.10."""
    major, minor = sys.version_info[:2]
    status = major >= 3 and minor >= 10
    print(f"[{'PASS' if status else 'FAIL'}] Python Version: {sys.version.split()[0]} (Required >= 3.10)")
    return status


def check_directories() -> bool:
    """Ensure required directory structure exists."""
    root = Path(__file__).resolve().parents[2]
    required_dirs = [
        "config",
        "data/raw",
        "data/interim",
        "data/processed",
        "data/metadata",
        "docs/governance",
        "docs/requirements",
        "docs/engineering",
        "scripts/environment",
        "scripts/data_acquisition",
        "src/marketvoice",
        "tests",
        "reports/validation",
    ]
    all_ok = True
    for relative_dir in required_dirs:
        dir_path = root / relative_dir
        exists = dir_path.exists() and dir_path.is_dir()
        if not exists:
            all_ok = False
        print(f"[{'PASS' if exists else 'FAIL'}] Directory: {relative_dir}")
    return all_ok


def check_files() -> bool:
    """Ensure mandatory project root files exist."""
    root = Path(__file__).resolve().parents[2]
    required_files = [
        "README.md",
        "LICENSE",
        "CITATION.cff",
        "CONTRIBUTING.md",
        "SECURITY.md",
        ".gitignore",
        ".env.example",
        "pyproject.toml",
        "config/project_settings.yaml",
        "config/data_sources.yaml",
        "data/metadata/source_manifest.csv",
    ]
    all_ok = True
    for relative_file in required_files:
        file_path = root / relative_file
        exists = file_path.exists() and file_path.is_file()
        if not exists:
            all_ok = False
        print(f"[{'PASS' if exists else 'FAIL'}] File: {relative_file}")
    return all_ok


def main():
    print("=" * 60)
    print("MARKETVOICE SEA — PHASE 1 ENVIRONMENT VALIDATION")
    print("=" * 60)

    v_ok = check_python_version()
    d_ok = check_directories()
    f_ok = check_files()

    print("=" * 60)
    if v_ok and d_ok and f_ok:
        print("OVERALL HEALTH STATUS: PASS — Environment is properly configured.")
        sys.exit(0)
    else:
        print("OVERALL HEALTH STATUS: FAIL — Environment setup incomplete.")
        sys.exit(1)


if __name__ == "__main__":
    main()
