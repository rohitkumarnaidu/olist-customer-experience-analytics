"""
data_contract.py — Comprehensive Data Contract & Schema Specifications
Project: Gradient Learnings Data Analytics Hackathon 2026 (Olist)

Defines expectations, schemas, primary keys, and reusable validation functions
for all layers of the analytical pipeline:
1. Raw Source Tables (9 official CSVs)
2. Pre-Aggregated Order-Level Tables (items, payments, reviews)
3. Geolocation Centroid Reference Table (zip_to_centroid)
4. Canonical Order Analytics Base Table (order_analytics_base)
5. Financial Metric Definitions (GMV vs Settlement Value)
"""

from pathlib import Path
from typing import Dict, List, Any, Tuple
import pandas as pd

# ==============================================================================
# 1. RAW SOURCE TABLE CONTRACTS
# ==============================================================================

RAW_OFFICIAL_ROW_COUNTS: Dict[str, int] = {
    "olist_orders_dataset.csv": 99441,
    "olist_order_items_dataset.csv": 112650,
    "olist_order_payments_dataset.csv": 103886,
    "olist_order_reviews_dataset.csv": 99224,  # Empirically verified parsed rows
    "olist_customers_dataset.csv": 99441,
    "olist_products_dataset.csv": 32951,
    "olist_sellers_dataset.csv": 3095,
    "olist_geolocation_dataset.csv": 1000163,
    "product_category_name_translation.csv": 71,
}

RAW_DATASET_KEYS: Dict[str, List[str]] = {
    "olist_orders_dataset.csv": ["order_id"],
    "olist_order_items_dataset.csv": ["order_id", "order_item_id"],
    "olist_order_payments_dataset.csv": ["order_id", "payment_sequential"],
    "olist_order_reviews_dataset.csv": ["review_id", "order_id"],  # Empirically composite
    "olist_customers_dataset.csv": ["customer_id"],
    "olist_products_dataset.csv": ["product_id"],
    "olist_sellers_dataset.csv": ["seller_id"],
    "olist_geolocation_dataset.csv": [],  # Non-unique table by design
    "product_category_name_translation.csv": ["product_category_name"],
}

RAW_EXPECTED_COLUMNS: Dict[str, List[str]] = {
    "olist_orders_dataset.csv": [
        "order_id", "customer_id", "order_status",
        "order_purchase_timestamp", "order_approved_at",
        "order_delivered_carrier_date", "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ],
    "olist_order_items_dataset.csv": [
        "order_id", "order_item_id", "product_id",
        "seller_id", "shipping_limit_date", "price", "freight_value"
    ],
    "olist_order_payments_dataset.csv": [
        "order_id", "payment_sequential", "payment_type",
        "payment_installments", "payment_value"
    ],
    "olist_order_reviews_dataset.csv": [
        "review_id", "order_id", "review_score",
        "review_comment_title", "review_comment_message",
        "review_creation_date", "review_answer_timestamp"
    ],
    "olist_customers_dataset.csv": [
        "customer_id", "customer_unique_id",
        "customer_zip_code_prefix", "customer_city", "customer_state"
    ],
    "olist_products_dataset.csv": [
        "product_id", "product_category_name", "product_name_lenght",
        "product_description_lenght", "product_photos_qty",
        "product_weight_g", "product_length_cm",
        "product_height_cm", "product_width_cm"
    ],
    "olist_sellers_dataset.csv": [
        "seller_id", "seller_zip_code_prefix",
        "seller_city", "seller_state"
    ],
    "olist_geolocation_dataset.csv": [
        "geolocation_zip_code_prefix", "geolocation_lat",
        "geolocation_lng", "geolocation_city", "geolocation_state"
    ],
    "product_category_name_translation.csv": [
        "product_category_name", "product_category_name_english"
    ],
}

# ==============================================================================
# 2. AGGREGATED ORDER-LEVEL CONTRACTS
# ==============================================================================

AGGREGATED_TABLE_CONTRACTS: Dict[str, Dict[str, Any]] = {
    "items_aggregated": {
        "expected_grain": "1 row per order_id",
        "expected_key": "order_id",
        "allowed_multiplicity": 1,
        "expected_row_count": 98666,
        "critical_columns": [
            "order_id", "item_count", "item_price_total", "freight_total",
            "order_gmv", "distinct_products", "distinct_sellers",
            "distinct_categories", "dominant_category", "dominant_seller",
            "multi_seller_flag", "multi_category_flag"
        ],
    },
    "payments_aggregated": {
        "expected_grain": "1 row per order_id",
        "expected_key": "order_id",
        "allowed_multiplicity": 1,
        "expected_row_count": 99440,
        "critical_columns": [
            "order_id", "payment_value_total", "payment_line_count",
            "payment_type_count", "payment_installments_max",
            "payment_installments_min", "payment_installments_mean",
            "multi_payment_flag", "dominant_payment_type"
        ],
    },
    "reviews_selected": {
        "expected_grain": "1 row per order_id",
        "expected_key": "order_id",
        "allowed_multiplicity": 1,
        "expected_row_count": 98673,
        "critical_columns": [
            "order_id", "review_id", "review_score",
            "review_comment_title", "review_comment_message",
            "review_creation_date", "review_answer_timestamp",
            "review_count_for_order", "multi_review_flag"
        ],
    },
}

# ==============================================================================
# 3. GEOLOCATION REFERENCE CONTRACT
# ==============================================================================

GEOLOCATION_REFERENCE_CONTRACT: Dict[str, Any] = {
    "expected_grain": "1 row per zip_code_prefix",
    "expected_key": "zip_code_prefix",
    "allowed_multiplicity": 1,
    "expected_row_count": 19015,
    "critical_columns": [
        "zip_code_prefix", "raw_row_count", "valid_coord_count",
        "invalid_coord_count", "centroid_lat", "centroid_lng",
        "canonical_city", "canonical_state"
    ],
}

# ==============================================================================
# 4. CANONICAL ORDER ANALYTICS BASE CONTRACT
# ==============================================================================

ORDER_ANALYTICS_BASE_CONTRACT: Dict[str, Any] = {
    "expected_grain": "1 row per order_id",
    "expected_key": "order_id",
    "allowed_multiplicity": 1,
    "expected_row_count": 99441,
    "critical_columns": [
        # Order Core
        "order_id", "customer_id", "order_status",
        "order_purchase_timestamp", "order_approved_at",
        "order_delivered_carrier_date", "order_delivered_customer_date",
        "order_estimated_delivery_date",
        # Customer Identifiers & Location
        "customer_unique_id", "customer_zip_code_prefix",
        "customer_city", "customer_state",
        "customer_lat", "customer_lng",
        # Aggregated Items
        "item_count", "item_price_total", "freight_total", "order_gmv",
        "distinct_products", "distinct_sellers", "distinct_categories",
        "dominant_category", "dominant_seller",
        "multi_seller_flag", "multi_category_flag",
        # Seller Location (Dominant Seller)
        "seller_zip_code_prefix", "seller_city", "seller_state",
        "seller_lat", "seller_lng",
        # Aggregated Payments
        "payment_value_total", "payment_line_count", "payment_type_count",
        "payment_installments_max", "payment_installments_min", "payment_installments_mean",
        "multi_payment_flag", "dominant_payment_type",
        # Selected Review
        "review_id", "review_score", "review_creation_date", "review_answer_timestamp",
        "review_count_for_order", "multi_review_flag",
        # Delivery Population Flags
        "is_delivered", "has_delivery_date", "eligible_for_delivery_analysis",
        # Financial Comparison Flags
        "financial_diff", "financial_reconciled_flag"
    ],
}

# ==============================================================================
# 5. FINANCIAL CONTRACT
# ==============================================================================

FINANCIAL_CONTRACT: Dict[str, str] = {
    "GMV": "sum(price + freight_value) at order grain (merchant commercial value)",
    "Settlement_Value": "sum(payment_value) at order grain (customer cash tender)",
    "Discrepancy_Tolerance": "0.01 BRL (orders with abs_diff < 0.01 marked reconciled)",
}


# ==============================================================================
# 6. VALIDATION UTILITY FUNCTIONS
# ==============================================================================

def validate_table_contract(df: pd.DataFrame, contract: Dict[str, Any], table_name: str) -> Dict[str, Any]:
    """Validates a DataFrame against a defined contract dictionary."""
    expected_key = contract.get("expected_key")
    expected_rows = contract.get("expected_row_count")
    critical_cols = contract.get("critical_columns", [])

    actual_rows = len(df)
    missing_cols = [col for col in critical_cols if col not in df.columns]

    null_keys = 0
    duplicate_keys = 0
    is_key_unique = True
    if expected_key and expected_key in df.columns:
        null_keys = int(df[expected_key].isnull().sum())
        duplicate_keys = int(df[expected_key].duplicated().sum())
        is_key_unique = (null_keys == 0) and (duplicate_keys == 0)

    is_row_count_exact = (actual_rows == expected_rows) if expected_rows else True
    is_valid = is_key_unique and is_row_count_exact and (len(missing_cols) == 0)

    return {
        "table_name": table_name,
        "is_valid": is_valid,
        "actual_rows": actual_rows,
        "expected_rows": expected_rows,
        "is_row_count_exact": is_row_count_exact,
        "expected_key": expected_key,
        "null_keys": null_keys,
        "duplicate_keys": duplicate_keys,
        "is_key_unique": is_key_unique,
        "missing_columns": missing_cols,
    }
