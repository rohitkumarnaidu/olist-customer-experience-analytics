"""
test_data_contracts.py — Automated Test Suite for Data Contracts & Integrity
Project: Gradient Learnings Data Analytics Hackathon 2026 (Olist)

Automated test suite using pytest covering:
1. Raw CSV file presence, row counts, and schema contracts
2. Composite-key uniqueness (items, payments, reviews)
3. Geolocation reference table integrity and territorial coordinate validity
4. Pre-aggregated table grain invariants (1 row per order_id)
5. Canonical order_analytics_base table grain and contract invariants
"""

from pathlib import Path
import pytest
import pandas as pd
import numpy as np

import sys
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from src.data_contract import (
    RAW_OFFICIAL_ROW_COUNTS, RAW_DATASET_KEYS, RAW_EXPECTED_COLUMNS,
    AGGREGATED_TABLE_CONTRACTS, GEOLOCATION_REFERENCE_CONTRACT,
    ORDER_ANALYTICS_BASE_CONTRACT, validate_table_contract
)
from src.geolocation import (
    BRAZIL_LAT_MIN, BRAZIL_LAT_MAX, BRAZIL_LNG_MIN, BRAZIL_LNG_MAX,
    build_zip_centroids
)
from src.review_aggregation import select_order_level_reviews
from src.item_aggregation import aggregate_order_items
from src.payment_aggregation import aggregate_order_payments

RAW_DIR = _root / "data" / "raw"
PROCESSED_DIR = _root / "data" / "processed"


# 1. Raw Files Inventory Tests
@pytest.mark.parametrize("filename,expected_rows", RAW_OFFICIAL_ROW_COUNTS.items())
def test_raw_file_presence_and_row_count(filename, expected_rows):
    filepath = RAW_DIR / filename
    assert filepath.exists(), f"Raw file {filename} does not exist!"
    df = pd.read_csv(filepath)
    assert len(df) == expected_rows, f"Row count mismatch in {filename}: expected {expected_rows}, got {len(df)}"


# 2. Raw Files Schema Tests
@pytest.mark.parametrize("filename,expected_cols", RAW_EXPECTED_COLUMNS.items())
def test_raw_file_columns(filename, expected_cols):
    filepath = RAW_DIR / filename
    df = pd.read_csv(filepath, nrows=5)
    for col in expected_cols:
        assert col in df.columns, f"Expected column '{col}' missing from {filename}"


# 3. Composite Key Integrity Tests
def test_order_items_composite_key():
    df = pd.read_csv(RAW_DIR / "olist_order_items_dataset.csv")
    assert df.duplicated(subset=["order_id", "order_item_id"]).sum() == 0, "order_items composite key is not unique!"


def test_order_payments_composite_key():
    df = pd.read_csv(RAW_DIR / "olist_order_payments_dataset.csv")
    assert df.duplicated(subset=["order_id", "payment_sequential"]).sum() == 0, "order_payments composite key is not unique!"


def test_orders_primary_key():
    df = pd.read_csv(RAW_DIR / "olist_orders_dataset.csv")
    assert df["order_id"].nunique() == len(df) == 99441, "orders primary key order_id is not unique!"


def test_customers_primary_key():
    df = pd.read_csv(RAW_DIR / "olist_customers_dataset.csv")
    assert df["customer_id"].nunique() == len(df) == 99441, "customers primary key customer_id is not unique!"


def test_sellers_primary_key():
    df = pd.read_csv(RAW_DIR / "olist_sellers_dataset.csv")
    assert df["seller_id"].nunique() == len(df) == 3095, "sellers primary key seller_id is not unique!"


def test_products_primary_key():
    df = pd.read_csv(RAW_DIR / "olist_products_dataset.csv")
    assert df["product_id"].nunique() == len(df) == 32951, "products primary key product_id is not unique!"


# 4. Review Selection Tests
def test_review_order_selection_grain():
    df_reviews = pd.read_csv(RAW_DIR / "olist_order_reviews_dataset.csv")
    order_reviews, _ = select_order_level_reviews(df_reviews)
    assert len(order_reviews) == 98673, f"Expected 98,673 selected order reviews, got {len(order_reviews)}"
    assert order_reviews["order_id"].nunique() == len(order_reviews), "Order reviews grain is not 1 row per order_id!"


# 5. Geolocation Reference Tests
def test_geolocation_reference_grain_and_bounds():
    zip_centroids, _ = build_zip_centroids(RAW_DIR / "olist_geolocation_dataset.csv")
    assert len(zip_centroids) == 19015, f"Expected 19,015 zip centroids, got {len(zip_centroids)}"
    assert zip_centroids["zip_code_prefix"].nunique() == len(zip_centroids), "Zip centroids grain violated!"
    
    # Valid coordinates check
    valid_coords = zip_centroids.dropna(subset=["centroid_lat", "centroid_lng"])
    assert (valid_coords["centroid_lat"] >= BRAZIL_LAT_MIN).all(), "Centroid latitude below min bound!"
    assert (valid_coords["centroid_lat"] <= BRAZIL_LAT_MAX).all(), "Centroid latitude above max bound!"
    assert (valid_coords["centroid_lng"] >= BRAZIL_LNG_MIN).all(), "Centroid longitude below min bound!"
    assert (valid_coords["centroid_lng"] <= BRAZIL_LNG_MAX).all(), "Centroid longitude above max bound!"


# 6. Pre-Aggregated Items Tests
def test_item_aggregation_contract():
    items_agg, _ = aggregate_order_items(
        RAW_DIR / "olist_order_items_dataset.csv",
        RAW_DIR / "olist_products_dataset.csv",
        RAW_DIR / "product_category_name_translation.csv",
    )
    assert len(items_agg) == 98666, f"Expected 98,666 orders in items_agg, got {len(items_agg)}"
    assert items_agg["order_id"].nunique() == len(items_agg), "Order items agg grain violated!"
    for col in AGGREGATED_TABLE_CONTRACTS["items_aggregated"]["critical_columns"]:
        assert col in items_agg.columns, f"Missing critical column {col} in items_agg"


# 7. Pre-Aggregated Payments Tests
def test_payment_aggregation_contract():
    pmts_agg, _ = aggregate_order_payments(RAW_DIR / "olist_order_payments_dataset.csv")
    assert len(pmts_agg) == 99440, f"Expected 99,440 orders in pmts_agg, got {len(pmts_agg)}"
    assert pmts_agg["order_id"].nunique() == len(pmts_agg), "Order payments agg grain violated!"
    for col in AGGREGATED_TABLE_CONTRACTS["payments_aggregated"]["critical_columns"]:
        assert col in pmts_agg.columns, f"Missing critical column {col} in pmts_agg"


# 8. Canonical Order Analytics Base Invariant Tests
def test_order_analytics_base_invariants():
    parquet_path = PROCESSED_DIR / "order_analytics_base.parquet"
    if not parquet_path.exists():
        pytest.skip("order_analytics_base.parquet not built yet; build_order_base must run first.")
    
    df_base = pd.read_parquet(parquet_path)
    assert len(df_base) == 99441, f"Expected 99,441 rows in order_analytics_base, got {len(df_base)}"
    assert df_base["order_id"].nunique() == 99441, "Duplicate order_id found in order_analytics_base!"
    
    # Contract validation
    check = validate_table_contract(df_base, ORDER_ANALYTICS_BASE_CONTRACT, "order_analytics_base")
    assert check["is_valid"], f"order_analytics_base failed contract check: {check['missing_columns']}"
    
    # Check customer ID preservation
    assert "customer_id" in df_base.columns
    assert "customer_unique_id" in df_base.columns
    assert df_base["customer_id"].nunique() == 99441
    assert df_base["customer_unique_id"].nunique() == 96096
    
    # Delivery population flags check
    assert "is_delivered" in df_base.columns
    assert "eligible_for_delivery_analysis" in df_base.columns
    assert df_base["is_delivered"].sum() == 96478
    assert df_base["eligible_for_delivery_analysis"].sum() == 96470
