#!/usr/bin/env python3
"""Validate YAML configuration files."""

import yaml
import sys

files = [
    'config/project_settings.yaml',
    'config/data_sources.yaml',
    'config/experiment_settings.yaml',
]

errors = False
for fpath in files:
    try:
        with open(fpath, 'r') as f:
            yaml.safe_load(f)
        print(f"[PASS] {fpath}: Valid YAML")
    except Exception as e:
        print(f"[FAIL] {fpath}: {e}")
        errors = True

sys.exit(1 if errors else 0)
