"""
build_order_base.py — Canonical Order Analytics Base Builder & Join Pipeline
Project: Gradient Learnings Data Analytics Hackathon 2026 (Olist)

MODULE 2 — Data Model and Join Architecture

Orchestrates the creation of the canonical analytical order table:
`order_analytics_base` at exactly 1 row = 1 order_id (99,441 rows).

Layers:
    A-C: Raw loading, pre-aggregation, reference tables (delegated to sub-modules)
    D:   Canonical order base via validated joins
    E:   Missingness/availability flags
    F:   Analytical feature engineering
    G:   Temporal features
    H:   Final validated analytical model

Enforces:
1. Pure reproducibility directly from data/raw/ source CSVs.
2. Pre-aggregated joins that prevent relational fan-out.
3. Strict telemetry tracking via enhanced JoinTracker.
4. Preserves both customer_id and customer_unique_id.
5. Invariant delivery population flags.
6. Explicit financial definitions: GMV vs Settlement Value.
7. Emits:
   - data/processed/order_analytics_base.parquet    (Layer D — canonical order base)
   - data/processed/order_analytics_base.csv
   - data/processed/analytical_model.parquet         (Layer H — full analytical model)
   - data/processed/analytical_model.csv
   - outputs/tables/join_audit.csv                   (Enhanced join telemetry)
   - outputs/tables/order_analytics_data_dictionary.csv
"""

from pathlib import Path
from typing import Tuple
import sys
import pandas as pd
import numpy as np

# Ensure project root is in sys.path
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from src.category_translation import audit_category_translations
from src.geolocation import build_zip_centroids
from src.item_aggregation import aggregate_order_items
from src.payment_aggregation import aggregate_order_payments
from src.review_aggregation import run_review_aggregation
from src.financial_metrics import compute_order_financial_metrics
from src.join_validation import (
    JoinTracker, validate_order_grain, validate_row_count,
    validate_unique_key, validate_no_row_explosion
)
from src.data_contract import (
    ORDER_ANALYTICS_BASE_CONTRACT, validate_table_contract
)
from src.data_model import (
    build_analytical_model, generate_data_dictionary
)


def build_order_analytics_base(
    data_dir: Path,
    output_dir: Path,
    tables_dir: Path,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Main builder function for the canonical order analytics base table
    and the full analytical model.

    Returns:
        (order_analytics_base_df, analytical_model_df, join_audit_df)
    """
    tracker = JoinTracker(primary_key="order_id")

    # Paths
    raw_dir = data_dir / "raw"
    orders_p = raw_dir / "olist_orders_dataset.csv"
    custs_p = raw_dir / "olist_customers_dataset.csv"
    items_p = raw_dir / "olist_order_items_dataset.csv"
    pmts_p = raw_dir / "olist_order_payments_dataset.csv"
    revs_p = raw_dir / "olist_order_reviews_dataset.csv"
    prods_p = raw_dir / "olist_products_dataset.csv"
    sellers_p = raw_dir / "olist_sellers_dataset.csv"
    geo_p = raw_dir / "olist_geolocation_dataset.csv"
    trans_p = raw_dir / "product_category_name_translation.csv"

    # ----------------------------------------------------------------------
    # Layer A: Load Raw Sources
    # ----------------------------------------------------------------------
    print("  [A] Loading raw sources...")
    df_orders = pd.read_csv(orders_p)
    validate_order_grain(df_orders, "order_id", "Raw Orders")
    validate_row_count(df_orders, 99441, "Raw Orders")

    # ----------------------------------------------------------------------
    # Layer B: Build Pre-Aggregated Components
    # ----------------------------------------------------------------------
    print("  [B] Building pre-aggregated components...")
    items_agg, _ = aggregate_order_items(
        items_p, prods_p, trans_p, tables_dir / "item_aggregation_audit.csv"
    )
    pmts_agg, _ = aggregate_order_payments(
        pmts_p, tables_dir / "payment_aggregation_audit.csv"
    )
    revs_selected, _ = run_review_aggregation(
        revs_p, tables_dir / "review_aggregation_audit.csv"
    )

    # ----------------------------------------------------------------------
    # Layer C: Build Reference Tables
    # ----------------------------------------------------------------------
    print("  [C] Building reference tables...")
    zip_centroids, _ = build_zip_centroids(
        geo_p, tables_dir / "geolocation_aggregation_audit.csv"
    )
    _, _ = compute_order_financial_metrics(
        items_p, pmts_p, orders_p, tables_dir / "financial_metrics_audit.csv"
    )
    audit_category_translations(
        prods_p, trans_p, tables_dir / "category_translation_audit.csv"
    )

    # ----------------------------------------------------------------------
    # Layer D: Validated Joins → Canonical Order Base
    # ----------------------------------------------------------------------
    print("  [D] Executing validated join pipeline...")
    base_df = df_orders.copy()

    # Step D.1: Join Customers (1:1 on customer_id)
    df_custs = pd.read_csv(custs_p)
    validate_unique_key(df_custs, "customer_id", "Raw Customers")
    next_df = base_df.merge(df_custs, on="customer_id", how="left")
    tracker.record_join(
        "D.1 Join Customers", base_df, next_df, "customer_id",
        source_table="orders", right_table="customers",
        join_type="left", cardinality_expected="1:1",
    )
    base_df = next_df

    # Step D.2: Join Customer Geolocation Centroids (M:1 on zip prefix)
    cust_geo = zip_centroids[["zip_code_prefix", "centroid_lat", "centroid_lng"]].rename(
        columns={
            "zip_code_prefix": "customer_zip_code_prefix",
            "centroid_lat": "customer_lat",
            "centroid_lng": "customer_lng",
        }
    )
    next_df = base_df.merge(cust_geo, on="customer_zip_code_prefix", how="left")
    tracker.record_join(
        "D.2 Join Customer Centroids", base_df, next_df, "customer_zip_code_prefix",
        source_table="orders+customers", right_table="zip_centroids",
        join_type="left", cardinality_expected="M:1",
    )
    base_df = next_df

    # Step D.3: Join Aggregated Items (1:1 on order_id, Left Join)
    next_df = base_df.merge(items_agg, on="order_id", how="left")
    tracker.record_join(
        "D.3 Join Aggregated Items", base_df, next_df, "order_id",
        source_table="orders+customers+geo", right_table="items_aggregated",
        join_type="left", cardinality_expected="1:1",
    )
    base_df = next_df

    # Step D.4: Join Dominant Seller Information & Geolocation
    df_sellers = pd.read_csv(sellers_p)
    seller_geo = zip_centroids[["zip_code_prefix", "centroid_lat", "centroid_lng"]].rename(
        columns={
            "zip_code_prefix": "seller_zip_code_prefix",
            "centroid_lat": "seller_lat",
            "centroid_lng": "seller_lng",
        }
    )
    sellers_enriched = df_sellers.merge(seller_geo, on="seller_zip_code_prefix", how="left")
    sellers_enriched = sellers_enriched.rename(columns={"seller_id": "dominant_seller"})

    next_df = base_df.merge(sellers_enriched, on="dominant_seller", how="left")
    tracker.record_join(
        "D.4 Join Dominant Seller & Centroids", base_df, next_df, "dominant_seller",
        source_table="orders+items", right_table="sellers+zip_centroids",
        join_type="left", cardinality_expected="M:1",
    )
    base_df = next_df

    # Step D.5: Join Aggregated Payments (1:1 on order_id, Left Join)
    next_df = base_df.merge(pmts_agg, on="order_id", how="left")
    tracker.record_join(
        "D.5 Join Aggregated Payments", base_df, next_df, "order_id",
        source_table="orders+items+sellers", right_table="payments_aggregated",
        join_type="left", cardinality_expected="1:1",
    )
    base_df = next_df

    # Step D.6: Join Selected Review (1:1 on order_id, Left Join)
    rev_cols = [
        "order_id", "review_id", "review_score", "review_comment_title",
        "review_comment_message", "review_creation_date", "review_answer_timestamp",
        "review_count_for_order", "multi_review_flag"
    ]
    next_df = base_df.merge(revs_selected[rev_cols], on="order_id", how="left")
    tracker.record_join(
        "D.6 Join Selected Review", base_df, next_df, "order_id",
        source_table="orders+items+sellers+payments", right_table="reviews_selected",
        join_type="left", cardinality_expected="1:1",
    )
    base_df = next_df

    # -- Layer D Population Flags & Financial Diagnostics --
    base_df["is_delivered"] = base_df["order_status"] == "delivered"
    base_df["has_delivery_date"] = base_df["order_delivered_customer_date"].notnull()
    base_df["eligible_for_delivery_analysis"] = base_df["is_delivered"] & base_df["has_delivery_date"]

    # Financial Diagnostics (Layer D scope — raw difference)
    gmv_filled = base_df["order_gmv"].fillna(0.0)
    pmt_filled = base_df["payment_value_total"].fillna(0.0)
    base_df["financial_diff"] = gmv_filled - pmt_filled
    base_df["financial_abs_diff"] = base_df["financial_diff"].abs()
    base_df["financial_reconciled_flag"] = base_df["financial_abs_diff"] < 0.01

    # -- Layer D: Final Grain Invariant Assertions --
    validate_order_grain(base_df, "order_id", "Layer D: Canonical Order Base")
    validate_row_count(base_df, 99441, "Layer D: Canonical Order Base")

    # Validate against formal contract
    contract_check = validate_table_contract(base_df, ORDER_ANALYTICS_BASE_CONTRACT, "order_analytics_base")
    if not contract_check["is_valid"]:
        raise ValueError(f"Contract violation on order_analytics_base: {contract_check}")

    # ----------------------------------------------------------------------
    # Save Layer D (Canonical Order Base)
    # ----------------------------------------------------------------------
    output_dir.mkdir(parents=True, exist_ok=True)
    parquet_d = output_dir / "order_analytics_base.parquet"
    csv_d = output_dir / "order_analytics_base.csv"
    base_df.to_parquet(parquet_d, index=False)
    base_df.to_csv(csv_d, index=False)
    print(f"  [D] Saved canonical base: {base_df.shape} -> {parquet_d.name}")

    # ----------------------------------------------------------------------
    # Layers E/F/G -> Layer H: Full Analytical Model
    # ----------------------------------------------------------------------
    print("  [E/F/G] Building analytical model layers...")
    model_df = build_analytical_model(base_df.copy())

    parquet_h = output_dir / "analytical_model.parquet"
    csv_h = output_dir / "analytical_model.csv"
    model_df.to_parquet(parquet_h, index=False)
    model_df.to_csv(csv_h, index=False)
    print(f"  [H] Saved analytical model: {model_df.shape} -> {parquet_h.name}")

    # ----------------------------------------------------------------------
    # Save Join Audit Telemetry & Data Dictionary
    # ----------------------------------------------------------------------
    tables_dir.mkdir(parents=True, exist_ok=True)
    validation_df = tracker.to_dataframe()
    audit_path = tables_dir / "join_audit.csv"
    validation_df.to_csv(audit_path, index=False)
    print(f"  [Audit] Join telemetry: {len(validation_df)} steps -> {audit_path.name}")

    # Also save the legacy validation file for backward compatibility
    validation_df.to_csv(tables_dir / "order_base_validation.csv", index=False)

    # Data Dictionary
    dd_path = tables_dir / "order_analytics_data_dictionary.csv"
    generate_data_dictionary(model_df, dd_path)
    print(f"  [Dict] Data dictionary: {len(model_df.columns)} columns -> {dd_path.name}")

    return base_df, model_df, validation_df


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent
    data_dir = base_dir / "data"
    proc_dir = data_dir / "processed"
    tables_dir = base_dir / "outputs" / "tables"

    print("=" * 70)
    print("MODULE 2 — Building Canonical Order Analytics Base & Analytical Model")
    print("=" * 70)
    df_base, df_model, df_val = build_order_analytics_base(data_dir, proc_dir, tables_dir)
    print("=" * 70)
    print("BUILD COMPLETE")
    print(f"  Layer D (Canonical Base): {df_base.shape[0]:,} rows × {df_base.shape[1]} cols")
    print(f"  Layer H (Analytical Model): {df_model.shape[0]:,} rows × {df_model.shape[1]} cols")
    print(f"  Order ID unique count: {df_base['order_id'].nunique():,}")
    print(f"  Join Steps: {len(df_val)}")
    print("\n  Join Telemetry Summary:")
    for _, row in df_val.iterrows():
        print(f"    {row['step']:45s} | {row['status']:6s} | match_rate={row['match_rate_pct']:.1f}%")
    print("=" * 70)
