"""
data_model.py -- Analytical Data Model Layer Definitions
Project: Gradient Learnings Data Analytics Hackathon 2026 (Olist)

Defines the layered analytical model architecture and the feature
engineering operations that transform the canonical order-grain base
into analysis-ready feature layers.

Architecture Layers:
    Layer A: Raw Sources          (data/raw/ -- 9 CSVs, untouched)
    Layer B: Pre-Aggregations     (items_agg, payments_agg, reviews_selected)
    Layer C: Reference Tables     (zip_centroids, category_translation)
    Layer D: Canonical Order Base (1 row = 1 order_id, 99,441 rows)
    Layer E: Missingness Flags    (explicit availability indicators)
    Layer F: Analytical Features  (derived flags, buckets, computed metrics)
    Layer G: Temporal Features    (date-derived dimensions for time-series analysis)
    Layer H: Final Validated Base (all layers merged, contract-validated)

Each downstream module (3+) consumes Layer H and never touches
raw sources or intermediate aggregations directly.
"""

from pathlib import Path
from typing import Dict, Tuple
import sys
import numpy as np
import pandas as pd

_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from src.join_validation import validate_order_grain, validate_row_count

# ------------------------------------------------------------------------------
# Layer E -- Missingness / Availability Flags
# ------------------------------------------------------------------------------

MISSINGNESS_FLAGS = {
    "has_items":               "item_count",
    "has_payment_record":      "payment_value_total",
    "has_review":              "review_score",
    "has_customer_coordinates": "customer_lat",
    "has_seller_coordinates":  "seller_lat",
    "has_product_category":    "dominant_category",
    "has_delivery_date":       "order_delivered_customer_date",
    "has_approval_date":       "order_approved_at",
    "has_carrier_date":        "order_delivered_carrier_date",
}


def add_missingness_flags(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds boolean availability flags for every source that may be null.
    Convention: True = data is present, False = data is missing.
    Does NOT fill missing values -- downstream analysis must respect these flags.
    """
    for flag_col, source_col in MISSINGNESS_FLAGS.items():
        if source_col in df.columns:
            df[flag_col] = df[source_col].notnull()
        else:
            df[flag_col] = False
    return df


# ------------------------------------------------------------------------------
# Layer F -- Analytical Feature Engineering
# ------------------------------------------------------------------------------

def add_review_features(df: pd.DataFrame) -> pd.DataFrame:
    """Adds review-derived analytical flags."""
    # Low review indicator (score <= 2)
    df["low_review_flag"] = False
    mask = df["review_score"].notnull()
    df.loc[mask, "low_review_flag"] = df.loc[mask, "review_score"] <= 2

    # High review indicator (score >= 4)
    df["high_review_flag"] = False
    df.loc[mask, "high_review_flag"] = df.loc[mask, "review_score"] >= 4

    # Review text availability
    df["review_text_available"] = df["review_comment_message"].notnull()
    df["review_title_available"] = df["review_comment_title"].notnull()

    return df


def add_item_features(df: pd.DataFrame) -> pd.DataFrame:
    """Adds item-derived analytical flags."""
    # Multi-item order boolean (distinct from item_count)
    df["multi_item_order"] = False
    mask = df["item_count"].notnull()
    df.loc[mask, "multi_item_order"] = df.loc[mask, "item_count"] > 1

    # Freight share of GMV
    df["freight_share_pct"] = np.nan
    gmv_mask = df["order_gmv"].notnull() & (df["order_gmv"] > 0)
    df.loc[gmv_mask, "freight_share_pct"] = (
        df.loc[gmv_mask, "freight_total"] / df.loc[gmv_mask, "order_gmv"] * 100
    ).round(4)

    return df


def add_financial_features(df: pd.DataFrame) -> pd.DataFrame:
    """Adds financial discrepancy buckets for reconciliation analysis."""
    # Discrepancy buckets
    conditions = [
        df["financial_abs_diff"] < 0.01,
        df["financial_abs_diff"] < 1.00,
        df["financial_abs_diff"] < 10.00,
        df["financial_abs_diff"] < 100.00,
        df["financial_abs_diff"] >= 100.00,
    ]
    choices = [
        "exact_match",
        "minor_<1",
        "small_<10",
        "medium_<100",
        "large_>=100",
    ]
    df["discrepancy_bucket"] = np.select(conditions, choices, default="no_data")

    # Mark orders with no items AND no payments as truly empty
    no_data = df["order_gmv"].isnull() & df["payment_value_total"].isnull()
    df.loc[no_data, "discrepancy_bucket"] = "no_data"

    return df


# ------------------------------------------------------------------------------
# Layer G -- Temporal Features
# ------------------------------------------------------------------------------

def add_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds date-derived dimensions from order_purchase_timestamp.
    These enable time-series analysis without repeated date parsing downstream.
    """
    ts_col = "order_purchase_timestamp"
    if ts_col not in df.columns:
        return df

    ts = pd.to_datetime(df[ts_col], errors="coerce")

    df["purchase_year"] = ts.dt.year.astype("Int64")
    df["purchase_month"] = ts.dt.month.astype("Int64")
    df["purchase_year_month"] = ts.dt.to_period("M").astype(str)
    df["purchase_quarter"] = ts.dt.quarter.astype("Int64")
    df["purchase_day_of_week"] = ts.dt.dayofweek.astype("Int64")  # 0=Monday
    df["purchase_day_name"] = ts.dt.day_name()
    df["purchase_hour"] = ts.dt.hour.astype("Int64")

    # Weekend flag
    df["is_weekend_purchase"] = df["purchase_day_of_week"].isin([5, 6])

    # Delivery time features (only for delivered orders)
    delivered_mask = df["order_delivered_customer_date"].notnull()
    purchase_ts = ts
    delivery_ts = pd.to_datetime(df["order_delivered_customer_date"], errors="coerce")
    estimated_ts = pd.to_datetime(df["order_estimated_delivery_date"], errors="coerce")
    carrier_ts = pd.to_datetime(df["order_delivered_carrier_date"], errors="coerce")
    approved_ts = pd.to_datetime(df["order_approved_at"], errors="coerce")

    # Total delivery time (purchase to delivery)
    df["delivery_days_total"] = np.nan
    diff = (delivery_ts - purchase_ts).dt.total_seconds() / 86400
    df.loc[delivered_mask, "delivery_days_total"] = diff[delivered_mask].round(2)

    # On-time flag: actual delivery <= estimated delivery
    df["delivered_on_time"] = pd.array([pd.NA] * len(df), dtype="boolean")
    on_time_mask = delivered_mask & estimated_ts.notnull()
    df.loc[on_time_mask, "delivered_on_time"] = (
        delivery_ts[on_time_mask] <= estimated_ts[on_time_mask]
    )

    # Delivery delay days (positive = late, negative = early)
    df["delivery_delay_days"] = np.nan
    delay = (delivery_ts - estimated_ts).dt.total_seconds() / 86400
    df.loc[on_time_mask, "delivery_delay_days"] = delay[on_time_mask].round(2)

    # Approval to carrier handoff time
    df["approval_to_carrier_days"] = np.nan
    a2c_mask = approved_ts.notnull() & carrier_ts.notnull()
    a2c = (carrier_ts - approved_ts).dt.total_seconds() / 86400
    df.loc[a2c_mask, "approval_to_carrier_days"] = a2c[a2c_mask].round(2)

    # Carrier to customer delivery time
    df["carrier_to_delivery_days"] = np.nan
    c2d_mask = carrier_ts.notnull() & delivered_mask
    c2d = (delivery_ts - carrier_ts).dt.total_seconds() / 86400
    df.loc[c2d_mask, "carrier_to_delivery_days"] = c2d[c2d_mask].round(2)

    return df


# ------------------------------------------------------------------------------
# Layer H -- Full Analytical Model Assembly
# ------------------------------------------------------------------------------

def build_analytical_model(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies all feature layers (E, F, G) to the canonical order base (Layer D).
    Returns the complete Layer H analytical model.

    Pre-condition: df must be the validated order_analytics_base (99,441 rows, 1:1 order_id).
    Post-condition: same grain, enriched with ~30 additional analytical columns.
    """
    n_before = len(df)

    # Layer E: Missingness
    df = add_missingness_flags(df)
    assert len(df) == n_before, "Layer E changed row count!"

    # Layer F: Analytical features
    df = add_review_features(df)
    df = add_item_features(df)
    df = add_financial_features(df)
    assert len(df) == n_before, "Layer F changed row count!"

    # Layer G: Temporal features
    df = add_temporal_features(df)
    assert len(df) == n_before, "Layer G changed row count!"

    # Final grain assertion
    validate_order_grain(df, "order_id", "Layer H: Final Analytical Model")
    validate_row_count(df, 99441, "Layer H: Final Analytical Model")

    return df


# ------------------------------------------------------------------------------
# Data Dictionary Generator
# ------------------------------------------------------------------------------

COLUMN_DESCRIPTIONS: Dict[str, Tuple[str, str]] = {
    # (layer, description)
    "order_id": ("D", "Unique order identifier (primary key)"),
    "customer_id": ("D", "Customer identifier (FK to customers table)"),
    "order_status": ("D", "Current order status (delivered, shipped, canceled, etc.)"),
    "order_purchase_timestamp": ("D", "Timestamp when customer placed the order"),
    "order_approved_at": ("D", "Timestamp when payment was approved"),
    "order_delivered_carrier_date": ("D", "Timestamp when order was handed to carrier"),
    "order_delivered_customer_date": ("D", "Timestamp when customer received the order"),
    "order_estimated_delivery_date": ("D", "Estimated delivery date shown to customer"),
    "customer_unique_id": ("D", "Deduplicated customer identifier across orders"),
    "customer_zip_code_prefix": ("D", "Customer 5-digit zip code prefix"),
    "customer_city": ("D", "Customer city name"),
    "customer_state": ("D", "Customer state code (2-letter, e.g. SP, RJ)"),
    "customer_lat": ("C", "Customer latitude (zip centroid)"),
    "customer_lng": ("C", "Customer longitude (zip centroid)"),
    "item_count": ("B", "Number of items in the order"),
    "item_price_total": ("B", "Sum of item prices in BRL"),
    "freight_total": ("B", "Sum of freight charges in BRL"),
    "order_gmv": ("B", "Gross Merchandise Value: item_price_total + freight_total"),
    "distinct_products": ("B", "Number of distinct product IDs in the order"),
    "distinct_sellers": ("B", "Number of distinct seller IDs in the order"),
    "distinct_categories": ("B", "Number of distinct product categories in the order"),
    "dominant_category": ("B", "Product category with highest cumulative spend"),
    "dominant_seller": ("B", "Seller with highest cumulative spend in the order"),
    "multi_seller_flag": ("B", "True if order has multiple distinct sellers"),
    "multi_category_flag": ("B", "True if order has multiple distinct categories"),
    "seller_zip_code_prefix": ("D", "Dominant seller 5-digit zip code prefix"),
    "seller_city": ("D", "Dominant seller city name"),
    "seller_state": ("D", "Dominant seller state code"),
    "seller_lat": ("C", "Dominant seller latitude (zip centroid)"),
    "seller_lng": ("C", "Dominant seller longitude (zip centroid)"),
    "payment_value_total": ("B", "Settlement Value: sum of payment_value in BRL"),
    "payment_line_count": ("B", "Number of payment line items for the order"),
    "payment_type_count": ("B", "Number of distinct payment types used"),
    "payment_installments_max": ("B", "Maximum installment count across payment lines"),
    "payment_installments_min": ("B", "Minimum installment count across payment lines"),
    "payment_installments_mean": ("B", "Mean installment count across payment lines"),
    "multi_payment_flag": ("B", "True if order used multiple payment lines"),
    "dominant_payment_type": ("B", "Payment type with the highest total payment value"),
    "review_id": ("B", "Selected review identifier (latest valid per order)"),
    "review_score": ("B", "Selected review score (1-5)"),
    "review_comment_title": ("B", "Selected review title text (nullable)"),
    "review_comment_message": ("B", "Selected review message text (nullable)"),
    "review_creation_date": ("B", "Timestamp when selected review was created"),
    "review_answer_timestamp": ("B", "Timestamp when selected review was answered"),
    "review_count_for_order": ("B", "Total number of reviews submitted for this order"),
    "multi_review_flag": ("B", "True if order has multiple review submissions"),
    "is_delivered": ("D", "True if order_status == 'delivered'"),
    "has_delivery_date": ("E", "True if order_delivered_customer_date is not null"),
    "eligible_for_delivery_analysis": ("D", "True if is_delivered AND has_delivery_date"),
    "financial_diff": ("F", "GMV minus Settlement Value (BRL)"),
    "financial_abs_diff": ("F", "Absolute value of financial_diff"),
    "financial_reconciled_flag": ("F", "True if |financial_diff| < 0.01 BRL"),
    # Layer E -- Missingness
    "has_items": ("E", "True if item_count is not null (order has item records)"),
    "has_payment_record": ("E", "True if payment_value_total is not null"),
    "has_review": ("E", "True if review_score is not null"),
    "has_customer_coordinates": ("E", "True if customer_lat is not null"),
    "has_seller_coordinates": ("E", "True if seller_lat is not null"),
    "has_product_category": ("E", "True if dominant_category is not null"),
    "has_approval_date": ("E", "True if order_approved_at is not null"),
    "has_carrier_date": ("E", "True if order_delivered_carrier_date is not null"),
    # Layer F -- Analytical
    "low_review_flag": ("F", "True if review_score <= 2"),
    "high_review_flag": ("F", "True if review_score >= 4"),
    "review_text_available": ("F", "True if review_comment_message is not null"),
    "review_title_available": ("F", "True if review_comment_title is not null"),
    "multi_item_order": ("F", "True if item_count > 1"),
    "freight_share_pct": ("F", "Freight as percentage of GMV (0-100)"),
    "discrepancy_bucket": ("F", "Financial diff bucket: exact_match, minor_<1, small_<10, medium_<100, large_>=100, no_data"),
    # Layer G -- Temporal
    "purchase_year": ("G", "Year extracted from order_purchase_timestamp"),
    "purchase_month": ("G", "Month (1-12) extracted from order_purchase_timestamp"),
    "purchase_year_month": ("G", "Year-month period string (e.g. 2017-01)"),
    "purchase_quarter": ("G", "Quarter (1-4) extracted from order_purchase_timestamp"),
    "purchase_day_of_week": ("G", "Day of week (0=Monday, 6=Sunday)"),
    "purchase_day_name": ("G", "Day name (e.g. Monday, Tuesday)"),
    "purchase_hour": ("G", "Hour of day (0-23) from order_purchase_timestamp"),
    "is_weekend_purchase": ("G", "True if purchase_day_of_week is Saturday or Sunday"),
    "delivery_days_total": ("G", "Days from purchase to delivery (purchase to actual delivery)"),
    "delivered_on_time": ("G", "True if actual delivery <= estimated delivery date"),
    "delivery_delay_days": ("G", "Days beyond estimated delivery (positive = late, negative = early)"),
    "approval_to_carrier_days": ("G", "Days from payment approval to carrier handoff"),
    "carrier_to_delivery_days": ("G", "Days from carrier handoff to customer delivery"),
}


def generate_data_dictionary(df: pd.DataFrame, output_path: Path) -> pd.DataFrame:
    """
    Generates a comprehensive data dictionary CSV for the analytical model.
    """
    records = []
    for col in df.columns:
        desc_info = COLUMN_DESCRIPTIONS.get(col, ("?", "No description available"))
        layer, description = desc_info

        dtype = str(df[col].dtype)
        null_count = int(df[col].isnull().sum())
        null_pct = round(null_count / len(df) * 100, 4)
        non_null = len(df) - null_count
        unique_count = int(df[col].nunique())

        records.append({
            "column_name": col,
            "layer": layer,
            "dtype": dtype,
            "non_null_count": non_null,
            "null_count": null_count,
            "null_pct": null_pct,
            "unique_count": unique_count,
            "description": description,
        })

    dict_df = pd.DataFrame(records)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    dict_df.to_csv(output_path, index=False)
    return dict_df


if __name__ == "__main__":
    from src.data_loader import load_canonical_base, TABLES_DIR

    print("Loading canonical base...")
    base = load_canonical_base()
    print(f"  Base shape: {base.shape}")

    print("Building analytical model (Layers E/F/G)...")
    model = build_analytical_model(base)
    print(f"  Model shape: {model.shape}")

    dd_path = TABLES_DIR / "order_analytics_data_dictionary.csv"
    dd = generate_data_dictionary(model, dd_path)
    print(f"\n  Data dictionary: {len(dd)} columns documented -> {dd_path}")
    print("\nDone.")
