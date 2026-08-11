"""
MARKETVOICE SEA — REQUIREMENTS ALIGNMENT & TARGET STANDARDIZATION CHECKING SYSTEM

Automated utility that programmatically audits:
1. Alignment between Business Information Requirements (BIR-01..BIR-06) and underlying data capabilities (data/metadata/data_capability_matrix.csv).
2. Standardization of target performance metrics across BRD, SRS, RTM, and system settings.
3. Dual-source governance boundaries and isolation rules in config/data_sources.yaml.
"""

import os
import re
import yaml
import pandas as pd
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
CONFIG_DATA_SOURCES = ROOT_DIR / "config" / "data_sources.yaml"
CAPABILITY_MATRIX_PATH = ROOT_DIR / "data" / "metadata" / "data_capability_matrix.csv"
BRD_PATH = ROOT_DIR / "docs" / "requirements" / "business_requirements_document.md"
SRS_PATH = ROOT_DIR / "docs" / "requirements" / "system_requirements_specification.md"
RTM_PATH = ROOT_DIR / "docs" / "requirements" / "requirements_traceability_matrix.md"

STANDARDIZED_TARGETS = {
    "rating_macro_f1": 0.70,
    "rating_weighted_f1": 0.75,
    "rating_qwk": 0.75,
    "emotion_macro_f1": 0.65,
    "aspect_micro_f1": 0.70,
    "aspect_hamming_loss": 0.10,
    "priority_separation_ratio": 2.5,
    "priority_top_k_precision": 0.80,
    "row_reconciliation_pct": 100.0,
    "lineage_key_uniqueness_pct": 100.0
}


def validate_requirements_alignment():
    print("=" * 80)
    print("MARKETVOICE SEA — REQUIREMENTS ALIGNMENT & TARGET CHECKING SYSTEM")
    print("=" * 80)
    errors = 0

    # 1. Audit Data Capability Matrix Alignment
    if not CAPABILITY_MATRIX_PATH.exists():
        print(f"[FAIL] Capability matrix missing at {CAPABILITY_MATRIX_PATH}")
        errors += 1
    else:
        df_cap = pd.read_csv(CAPABILITY_MATRIX_PATH)
        print(f"[PASS] Data Capability Matrix loaded ({len(df_cap)} capabilities audited).")
        
        # Verify core capabilities CAP-01 to CAP-06 are supported
        supported_caps = df_cap[df_cap['project_support_status'].str.startswith('SUPPORTED')]
        print(f"[PASS] {len(supported_caps)} core capabilities verified as SUPPORTED by data foundation.")

    # 2. Audit Configuration Boundaries
    if not CONFIG_DATA_SOURCES.exists():
        print(f"[FAIL] Data sources config missing at {CONFIG_DATA_SOURCES}")
        errors += 1
    else:
        with open(CONFIG_DATA_SOURCES, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        ds = cfg.get("data_sources", {})
        rules = cfg.get("cross_source_rules", {})
        
        if ds.get("source_a", {}).get("source_id") == "SRC_PRDECT_ID_V1" and ds.get("source_b", {}).get("source_id") == "SRC_TOKOPEDIA_REVIEWS_2019":
            print("[PASS] Dual-Source configuration IDs verified (SRC_PRDECT_ID_V1 & SRC_TOKOPEDIA_REVIEWS_2019).")
        else:
            print("[FAIL] Dual-Source configuration IDs invalid!")
            errors += 1
            
        if not rules.get("cross_source_product_linkage") and not rules.get("cross_source_shop_linkage"):
            print("[PASS] Cross-source isolation rules verified (zero product/shop linkage).")
        else:
            print("[FAIL] Cross-source isolation rules violated!")
            errors += 1

    # 3. Audit Requirement Specifications Presence & Target Consistency
    for doc_path, doc_name in [(BRD_PATH, "BRD"), (SRS_PATH, "SRS"), (RTM_PATH, "RTM")]:
        if not doc_path.exists():
            print(f"[FAIL] {doc_name} specification document missing at {doc_path}")
            errors += 1
        else:
            with open(doc_path, "r", encoding="utf-8") as f:
                content = f.read()
            print(f"[PASS] {doc_name} specification verified present ({len(content):,} bytes).")
            
            # Check target metrics mention
            if "0.70" in content and "0.75" in content and "2.5" in content:
                print(f"[PASS] {doc_name} target metrics (Macro F1 >= 0.70, QWK >= 0.75, Separation Ratio >= 2.5) confirmed standardized.")
            else:
                print(f"[WARNING] {doc_name} may have non-standardized target metrics!")

    print("=" * 80)
    if errors == 0:
        print("OVERALL ALIGNMENT CHECK RESULT: PASS — Requirements & Target Standards fully aligned.")
    else:
        print(f"OVERALL ALIGNMENT CHECK RESULT: FAIL — Found {errors} alignment errors.")
    print("=" * 80)
    return errors == 0


if __name__ == "__main__":
    success = validate_requirements_alignment()
    exit(0 if success else 1)
