"""
financial_metrics.py — Financial Metric Disambiguation & Discrepancy Audit
Project: Gradient Learnings Data Analytics Hackathon 2026 (Olist)

Defines explicit, rigorous financial accounting contracts:
1. GMV (Gross Merchandise Value): sum(item price + item freight) at order grain.
   Measures merchant marketplace commercial value.
2. Settlement Value: sum(payment_value) at order grain.
   Measures cash tender collected via payment gateways.
3. Quantifies discrepancies, distributions, and root causes without forcing artificial
   reconciliation, documenting distinct commercial vs settlement concepts.
4. Outputs comprehensive audit table to outputs/tables/financial_metrics_audit.csv.
"""

from pathlib import Path
from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np


def compute_order_financial_metrics(
    items_path: Path,
    payments_path: Path,
    orders_path: Path,
    output_audit_path: Path = None,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Computes order-level GMV and Settlement Value, comparing them across all orders.
    Returns:
        (order_financials_df, audit_summary_df)
    """
    df_items = pd.read_csv(items_path)
    df_payments = pd.read_csv(payments_path)
    df_orders = pd.read_csv(orders_path)

    # Calculate item-level GMV at order grain
    df_items["item_total"] = df_items["price"] + df_items["freight_value"]
    gmv_by_order = df_items.groupby("order_id").agg(
        item_price_total=("price", "sum"),
        freight_total=("freight_value", "sum"),
        order_gmv=("item_total", "sum")
    ).reset_index()

    # Calculate payment settlement at order grain
    pmt_by_order = df_payments.groupby("order_id").agg(
        payment_value_total=("payment_value", "sum")
    ).reset_index()

    # Merge against complete order universe (99,441 orders)
    fin_df = df_orders[["order_id", "order_status"]].merge(gmv_by_order, on="order_id", how="left")
    fin_df = fin_df.merge(pmt_by_order, on="order_id", how="left")

    # Preserve raw presence flags before fillna
    fin_df["has_items_record"] = fin_df["order_gmv"].notnull()
    fin_df["has_payments_record"] = fin_df["payment_value_total"].notnull()

    # Null handling for differential arithmetic
    fin_df["order_gmv_filled"] = fin_df["order_gmv"].fillna(0.0)
    fin_df["payment_value_total_filled"] = fin_df["payment_value_total"].fillna(0.0)

    # Discrepancy metrics
    fin_df["financial_diff"] = fin_df["order_gmv_filled"] - fin_df["payment_value_total_filled"]
    fin_df["financial_abs_diff"] = fin_df["financial_diff"].abs()
    fin_df["financial_reconciled_flag"] = fin_df["financial_abs_diff"] < 0.01

    # Statistical summary
    total_orders = len(fin_df)
    total_gmv = float(fin_df["order_gmv_filled"].sum())
    total_payment_value = float(fin_df["payment_value_total_filled"].sum())
    net_difference = total_gmv - total_payment_value

    exact_matches = int((fin_df["financial_abs_diff"] < 0.001).sum())
    rounding_diffs = int(((fin_df["financial_abs_diff"] >= 0.001) & (fin_df["financial_abs_diff"] <= 0.10)).sum())
    material_diffs = int((fin_df["financial_abs_diff"] > 0.10).sum())
    orders_with_diff = int((fin_df["financial_abs_diff"] >= 0.01).sum())

    # Orders with missing records
    orders_payments_no_items = int((~fin_df["has_items_record"] & fin_df["has_payments_record"]).sum())
    orders_items_no_payments = int((fin_df["has_items_record"] & ~fin_df["has_payments_record"]).sum())

    # Percentiles of diff for orders that have both records
    both_records = fin_df[fin_df["has_items_record"] & fin_df["has_payments_record"]]
    quantiles = both_records["financial_diff"].quantile([0.01, 0.05, 0.25, 0.50, 0.75, 0.95, 0.99]).to_dict()

    audit_metrics = [
        {"metric": "total_orders_evaluated", "value": total_orders},
        {"metric": "total_gmv_brl", "value": round(total_gmv, 2)},
        {"metric": "total_settlement_value_brl", "value": round(total_payment_value, 2)},
        {"metric": "net_difference_brl", "value": round(net_difference, 2)},
        {"metric": "exact_match_count", "value": exact_matches},
        {"metric": "exact_match_pct", "value": round(exact_matches / total_orders * 100.0, 4)},
        {"metric": "rounding_diff_count_le_0_10", "value": rounding_diffs},
        {"metric": "material_diff_count_gt_0_10", "value": material_diffs},
        {"metric": "orders_with_diff_ge_0_01", "value": orders_with_diff},
        {"metric": "max_absolute_difference_brl", "value": round(float(fin_df["financial_abs_diff"].max()), 2)},
        {"metric": "orders_payment_recorded_no_items", "value": orders_payments_no_items},
        {"metric": "orders_items_recorded_no_payment", "value": orders_items_no_payments},
        {"metric": "diff_q01_brl", "value": round(float(quantiles[0.01]), 4)},
        {"metric": "diff_q05_brl", "value": round(float(quantiles[0.05]), 4)},
        {"metric": "diff_q25_brl", "value": round(float(quantiles[0.25]), 4)},
        {"metric": "diff_q50_brl", "value": round(float(quantiles[0.50]), 4)},
        {"metric": "diff_q75_brl", "value": round(float(quantiles[0.75]), 4)},
        {"metric": "diff_q95_brl", "value": round(float(quantiles[0.95]), 4)},
        {"metric": "diff_q99_brl", "value": round(float(quantiles[0.99]), 4)},
    ]
    audit_df = pd.DataFrame(audit_metrics)

    if output_audit_path is not None:
        output_audit_path.parent.mkdir(parents=True, exist_ok=True)
        audit_df.to_csv(output_audit_path, index=False)

    return fin_df, audit_df


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent
    items_p = base_dir / "data" / "raw" / "olist_order_items_dataset.csv"
    pmts_p = base_dir / "data" / "raw" / "olist_order_payments_dataset.csv"
    orders_p = base_dir / "data" / "raw" / "olist_orders_dataset.csv"
    audit_p = base_dir / "outputs" / "tables" / "financial_metrics_audit.csv"

    fin_df, audit_df = compute_order_financial_metrics(items_p, pmts_p, orders_p, audit_p)
    print("Financial metrics audit complete.")
    print(audit_df.to_string())
