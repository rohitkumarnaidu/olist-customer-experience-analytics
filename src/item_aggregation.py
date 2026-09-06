"""
item_aggregation.py — Item Pre-Aggregation Contract & Dominant Feature Selection
Project: Gradient Learnings Data Analytics Hackathon 2026 (Olist)

Creates a validated order-grain aggregation from olist_order_items_dataset.csv:
1. Calculates core commercial totals:
   - item_count (count of order_item_id)
   - item_price_total (sum of price)
   - freight_total (sum of freight_value)
   - order_gmv (sum of price + freight_value)
2. Calculates diversity/multiplicity metrics:
   - distinct_products (nunique of product_id)
   - distinct_sellers (nunique of seller_id)
   - distinct_categories (nunique of translated category)
   - multi_seller_flag (distinct_sellers > 1)
   - multi_category_flag (distinct_categories > 1)
3. Implements transparent, deterministic "Dominant" entity selection rules:
   - dominant_category: category with highest cumulative item spend (price) in the order;
     tie-breaker is alphabetical ascending. Missing categories are assigned 'unknown'.
   - dominant_seller: seller with highest cumulative item spend (price) in the order;
     tie-breaker is alphabetical ascending by seller_id.
4. Output is guaranteed to be exactly 1 row = 1 order_id (98,666 rows).
"""

from pathlib import Path
from typing import Tuple, Dict, Any
import pandas as pd
import numpy as np

import sys

# Ensure project root is in sys.path
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from src.category_translation import load_category_mapping, translate_category


def aggregate_order_items(
    items_path: Path,
    products_path: Path,
    translation_path: Path,
    output_audit_path: Path = None,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Aggregates raw order items into an order-grain DataFrame with dominant attributes.
    Returns:
        (order_items_aggregated_df, audit_summary_df)
    """
    df_items = pd.read_csv(items_path)
    df_products = pd.read_csv(products_path)
    cat_map = load_category_mapping(translation_path)

    # Translate product categories with explicit fallback
    df_products["product_category_name_english"] = df_products["product_category_name"].apply(
        lambda c: translate_category(c, cat_map)
    )

    # Join product category to items
    items_enriched = df_items.merge(
        df_products[["product_id", "product_category_name_english"]],
        on="product_id",
        how="left",
    )
    items_enriched["product_category_name_english"] = items_enriched["product_category_name_english"].fillna("unknown")

    # Basic aggregations
    order_base = items_enriched.groupby("order_id").agg(
        item_count=("order_item_id", "count"),
        item_price_total=("price", "sum"),
        freight_total=("freight_value", "sum"),
        distinct_products=("product_id", "nunique"),
        distinct_sellers=("seller_id", "nunique"),
        distinct_categories=("product_category_name_english", "nunique"),
    )

    order_base["order_gmv"] = order_base["item_price_total"] + order_base["freight_total"]
    order_base["multi_seller_flag"] = order_base["distinct_sellers"] > 1
    order_base["multi_category_flag"] = order_base["distinct_categories"] > 1

    # Dominant Category Rule:
    # 1. Group by order_id + category, sum price
    # 2. Sort by price DESC, category ASC
    # 3. Drop duplicates keeping first
    cat_spend = items_enriched.groupby(["order_id", "product_category_name_english"])["price"].sum().reset_index()
    cat_spend = cat_spend.sort_values(
        by=["order_id", "price", "product_category_name_english"],
        ascending=[True, False, True]
    )
    dom_cat = cat_spend.drop_duplicates(subset=["order_id"], keep="first").set_index("order_id")["product_category_name_english"]
    order_base["dominant_category"] = dom_cat

    # Dominant Seller Rule:
    # 1. Group by order_id + seller_id, sum price
    # 2. Sort by price DESC, seller_id ASC
    # 3. Drop duplicates keeping first
    seller_spend = items_enriched.groupby(["order_id", "seller_id"])["price"].sum().reset_index()
    seller_spend = seller_spend.sort_values(
        by=["order_id", "price", "seller_id"],
        ascending=[True, False, True]
    )
    dom_seller = seller_spend.drop_duplicates(subset=["order_id"], keep="first").set_index("order_id")["seller_id"]
    order_base["dominant_seller"] = dom_seller

    order_items_agg = order_base.reset_index()

    # Integrity verification
    assert len(order_items_agg) == order_items_agg["order_id"].nunique(), "Order items aggregation grain violated!"
    assert len(order_items_agg) == 98666, f"Expected 98,666 orders in items, got {len(order_items_agg)}"

    # Audit summary
    total_raw_items = len(df_items)
    multi_seller_orders = int(order_items_agg["multi_seller_flag"].sum())
    multi_category_orders = int(order_items_agg["multi_category_flag"].sum())
    multi_item_orders = int((order_items_agg["item_count"] > 1).sum())

    audit_data = [
        {"metric": "total_raw_item_rows", "value": total_raw_items},
        {"metric": "total_orders_in_items", "value": len(order_items_agg)},
        {"metric": "multi_item_orders_count", "value": multi_item_orders},
        {"metric": "multi_item_orders_pct", "value": round(multi_item_orders / len(order_items_agg) * 100.0, 4)},
        {"metric": "multi_seller_orders_count", "value": multi_seller_orders},
        {"metric": "multi_seller_orders_pct", "value": round(multi_seller_orders / len(order_items_agg) * 100.0, 4)},
        {"metric": "multi_category_orders_count", "value": multi_category_orders},
        {"metric": "multi_category_orders_pct", "value": round(multi_category_orders / len(order_items_agg) * 100.0, 4)},
        {"metric": "total_item_price_brl", "value": round(float(order_items_agg["item_price_total"].sum()), 2)},
        {"metric": "total_freight_value_brl", "value": round(float(order_items_agg["freight_total"].sum()), 2)},
        {"metric": "total_order_gmv_brl", "value": round(float(order_items_agg["order_gmv"].sum()), 2)},
        {"metric": "dominant_category_rule", "value": "Max cumulative item spend per order, tie-break alphabetical ASC"},
        {"metric": "dominant_seller_rule", "value": "Max cumulative item spend per order, tie-break seller_id ASC"},
    ]
    audit_df = pd.DataFrame(audit_data)

    if output_audit_path is not None:
        output_audit_path.parent.mkdir(parents=True, exist_ok=True)
        audit_df.to_csv(output_audit_path, index=False)

    return order_items_agg, audit_df


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent
    items_p = base_dir / "data" / "raw" / "olist_order_items_dataset.csv"
    prods_p = base_dir / "data" / "raw" / "olist_products_dataset.csv"
    trans_p = base_dir / "data" / "raw" / "product_category_name_translation.csv"
    audit_p = base_dir / "outputs" / "tables" / "item_aggregation_audit.csv"

    items_agg, audit_df = aggregate_order_items(items_p, prods_p, trans_p, audit_p)
    print("Item aggregation complete.")
    print(f"Aggregated items: {len(items_agg)} orders.")
    print(audit_df.to_string())
