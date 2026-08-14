#!/usr/bin/env python3
"""Validate YAML configuration files."""

import yaml
import sys

files = [
    'config/experiment_settings.yaml',
]

errors = False
for fpath in files:
    try:
        with open(fpath, 'r') as f:
            yaml.safe_load(f)
        print(f"✓ {fpath}: Valid YAML")
    except Exception as e:
        print(f"✗ {fpath}: {e}")
        errors = True

sys.exit(1 if errors else 0)
