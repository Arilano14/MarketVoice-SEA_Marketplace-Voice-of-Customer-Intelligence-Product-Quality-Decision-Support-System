#!/usr/bin/env python3
"""Quick data audit for Phase 4 verification."""

import pandas as pd

print("=" * 70)
print("DATA REALITY AUDIT")
print("=" * 70)
print()

# Source A
try:
    df_a = pd.read_csv('data/raw/prdect_id/PRDECT-ID Dataset.csv')
    print(f'Source A (PRDECT-ID): {len(df_a)} rows, {len(df_a.columns)} columns')
    print(f'  Columns: {list(df_a.columns)}')
    rating_a = sorted(df_a['rating'].unique())
    print(f'  Rating domain: {rating_a}')
    if 'sentiment' in df_a.columns:
        sentiment_vals = df_a["sentiment"].unique()
        print(f'  Sentiment values: {sentiment_vals}')
    if 'emotion' in df_a.columns:
        emotion_vals = df_a["emotion"].unique()
        print(f'  Emotion values: {emotion_vals}')
    print(f'  Has product_id: {"product_id" in df_a.columns}')
    print(f'  Has shop_id: {"shop_id" in df_a.columns}')
except Exception as e:
    print(f'Source A error: {e}')

print()

# Source B
try:
    df_b = pd.read_csv('data/raw/tokopedia_product_reviews_2019/tokopedia-product-reviews-2019.csv')
    print(f'Source B (Tokopedia): {len(df_b)} rows, {len(df_b.columns)} columns')
    print(f'  Columns: {list(df_b.columns)}')
    rating_b = sorted(df_b['rating'].unique())
    print(f'  Rating domain: {rating_b}')
    print(f'  Unique product_ids: {df_b["product_id"].nunique()}')
    print(f'  Unique shop_ids: {df_b["shop_id"].nunique()}')
    print(f'  Has sentiment: {"sentiment" in df_b.columns}')
    print(f'  Has emotion: {"emotion" in df_b.columns}')
except Exception as e:
    print(f'Source B error: {e}')

print()
print("=" * 70)
