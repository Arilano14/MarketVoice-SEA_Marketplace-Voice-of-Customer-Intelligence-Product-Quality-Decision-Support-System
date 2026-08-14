#!/usr/bin/env python3
"""Check Source A schema."""

import pandas as pd

df_a = pd.read_csv('data/raw/prdect_id/PRDECT-ID Dataset.csv', nrows=3)
print("Source A columns and first 3 rows:")
print(df_a)
print()

# Check exact column names
print("Column mapping:")
for col in df_a.columns:
    print(f"  '{col}'")

# Check if rating-like column exists
print()
print("Checking rating-like columns:")
for col in df_a.columns:
    if 'rating' in col.lower() or 'rate' in col.lower():
        print(f"  Found: '{col}'")
        df_full = pd.read_csv('data/raw/prdect_id/PRDECT-ID Dataset.csv')
        vals = df_full[col].unique()
        print(f"    Unique values: {sorted(vals)}")
