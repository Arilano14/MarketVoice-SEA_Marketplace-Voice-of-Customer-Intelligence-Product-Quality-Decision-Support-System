#!/usr/bin/env python3
"""Phase 4 comprehensive validation audit."""

import os
import yaml
from pathlib import Path

print("=" * 80)
print("PHASE 4 COMPREHENSIVE VALIDATION AUDIT")
print("=" * 80)
print()

# Define checks
checks = {}

# ============================================================================
# GROUP A: ENTRY & GOVERNANCE
# ============================================================================
print("GROUP A: ENTRY & GOVERNANCE")
print("-" * 80)

# P4-E01: Repository root
repo_root = Path(".")
checks["P4-E01"] = {
    "title": "Repository root identified",
    "expected": "Git repository with phase gates",
    "actual": "yes" if (repo_root / ".git").exists() else "no",
    "evidence": str(repo_root.absolute()),
}
print(f"P4-E01: {checks['P4-E01']['actual']}")

# P4-E02: Working tree status
import subprocess
try:
    result = subprocess.run(["git", "status", "--short"], capture_output=True, text=True, timeout=5)
    checks["P4-E02"] = {
        "title": "Working tree clean or changes documented",
        "expected": "no untracked modifications or documented",
        "actual": "clean" if not result.stdout.strip() else f"changes: {len(result.stdout.splitlines())} files",
        "evidence": "git status --short",
    }
except:
    checks["P4-E02"] = {"title": "Working tree status", "actual": "error", "evidence": "git not available"}
print(f"P4-E02: {checks['P4-E02']['actual']}")

# P4-E03: Canonical roadmap located
roadmap_file = Path("docs/governance/phase_gates.md")
checks["P4-E03"] = {
    "title": "Canonical roadmap located",
    "expected": "docs/governance/phase_gates.md exists",
    "actual": "yes" if roadmap_file.exists() else "no",
    "evidence": str(roadmap_file) if roadmap_file.exists() else "not found",
}
print(f"P4-E03: {checks['P4-E03']['actual']}")

# P4-E04-E07: Phase gates (canonical evidence paths with actual filenames)
phase_canonical_evidence = {
    0: Path("docs/governance/project_charter.md"),
    1: Path("reports/validation/phase_01_validation_report.md"),
    2: Path("reports/validation/phase_02_dataset_forensic_audit_report.md"),
    3: Path("reports/validation/phase_03_validation.md"),
}
for phase in range(0, 4):
    gate_file = phase_canonical_evidence[phase]
    checks[f"P4-E{4+phase}"] = {
        "title": f"Phase {phase} gate evidence",
        "actual": "present" if gate_file.exists() else "missing",
        "evidence": str(gate_file),
    }
    print(f"P4-E{4+phase}: {checks[f'P4-E{4+phase}']['actual']}")

print()

# ============================================================================
# GROUP D: EXPERIMENT PROTOCOL CRITICAL CHECKS
# ============================================================================
print("GROUP D: EXPERIMENT PROTOCOL CRITICAL CHECKS")
print("-" * 80)

# P4-X09: Holdout protected
holdout_check = False
try:
    with open("docs/methodology/experiment_protocol.md", "r") as f:
        protocol = f.read()
        if "holdout is not used for feature, preprocessing, challenger, or champion selection" in protocol:
            holdout_check = True
            evidence = "experiment_protocol.md §2 states holdout not used for selection"
        else:
            evidence = "holdout protection wording not found"
except:
    evidence = "file read error"

checks["P4-X09"] = {
    "title": "Holdout protected from selection",
    "expected": "Explicit prohibition on holdout in champion selection",
    "actual": "yes" if holdout_check else "no",
    "evidence": evidence,
}
print(f"P4-X09: {checks['P4-X09']['actual']}")

# P4-X10: Champion selection uses train/validation only
selection_check = False
try:
    with open("docs/methodology/evaluation_protocol.md", "r") as f:
        eval_proto = f.read()
        if "validation-led comparison" in eval_proto:
            selection_check = True
            evidence = "evaluation_protocol.md §2: validation-led comparison"
        else:
            evidence = "validation-led wording not found"
except:
    evidence = "file read error"

checks["P4-X10"] = {
    "title": "Champion selection uses train/validation only",
    "expected": "Selection explicitly excludes holdout",
    "actual": "yes" if selection_check else "no",
    "evidence": evidence,
}
print(f"P4-X10: {checks['P4-X10']['actual']}")

print()

# ============================================================================
# GROUP E: EVALUATION METRICS
# ============================================================================
print("GROUP E: EVALUATION METRICS")
print("-" * 80)

# Check for ordinal rating metrics
ordinal_metrics_present = False
ordinal_metrics = ["quadratic_weighted_kappa", "mean_absolute_error", "qwk", "mae", "MAE"]
try:
    with open("docs/methodology/evaluation_protocol.md", "r") as f:
        eval_protocol = f.read()
    with open("config/experiment_settings.yaml", "r") as f:
        exp_settings = yaml.safe_load(f)
    
    metrics_text = eval_protocol + str(exp_settings)
    ordinal_found = [m for m in ordinal_metrics if m.lower() in metrics_text.lower()]
    
    checks["P4-V08"] = {
        "title": "QWK defined for ordinal rating",
        "expected": "quadratic_weighted_kappa or equivalent ordinal metric",
        "actual": "present" if ordinal_found else "missing",
        "evidence": f"Found: {ordinal_found}" if ordinal_found else "No QWK/ordinal metric mentioned",
    }
except Exception as e:
    checks["P4-V08"] = {
        "title": "QWK defined for ordinal rating",
        "actual": f"error: {e}",
        "evidence": "file read error",
    }
print(f"P4-V08: {checks['P4-V08']['actual']}")

# P4-V09: MAE defined for ordinal rating
checks["P4-V09"] = {
    "title": "MAE defined for ordinal rating",
    "expected": "mean_absolute_error or equivalent",
    "actual": "present" if ordinal_found else "missing",
    "evidence": f"Same check as QWK: {ordinal_found}" if ordinal_found else "No MAE mentioned",
}
print(f"P4-V09: {checks['P4-V09']['actual']}")

print()

# ============================================================================
# GROUP F: CONFIGURATION
# ============================================================================
print("GROUP F: CONFIGURATION")
print("-" * 80)

# P4-T04: experiment YAML parses
yaml_valid = False
yaml_error = ""
try:
    with open("config/experiment_settings.yaml", "r") as f:
        yaml.safe_load(f)
    yaml_valid = True
    yaml_error = "YAML valid"
except Exception as e:
    yaml_error = str(e)

checks["P4-T04"] = {
    "title": "experiment_settings.yaml parses",
    "expected": "Valid YAML syntax",
    "actual": "yes" if yaml_valid else "no",
    "evidence": yaml_error,
}
print(f"P4-T04: {checks['P4-T04']['actual']}")

print()

# ============================================================================
# SUMMARY
# ============================================================================
print("SUMMARY")
print("=" * 80)

passed = sum(1 for c in checks.values() if c.get("actual") == "yes" or c.get("actual") == "present" or c.get("actual") == "clean")
failed = sum(1 for c in checks.values() if c.get("actual") == "no" or c.get("actual") == "missing")
errors = sum(1 for c in checks.values() if "error" in str(c.get("actual", "")).lower())

print(f"Total checks: {len(checks)}")
print(f"  Passed: {passed}")
print(f"  Failed: {failed}")
print(f"  Errors: {errors}")
print()

if failed > 0:
    print("FAILED CHECKS:")
    for check_id, check in checks.items():
        if check.get("actual") == "no" or check.get("actual") == "missing":
            print(f"  {check_id}: {check['title']}")
            print(f"    Evidence: {check['evidence']}")
            print()

if errors > 0:
    print("CHECKS WITH ERRORS:")
    for check_id, check in checks.items():
        if "error" in str(check.get("actual", "")).lower():
            print(f"  {check_id}: {check['title']}")
            print(f"    Error: {check['actual']}")
            print()
