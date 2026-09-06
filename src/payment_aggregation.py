"""
payment_aggregation.py — Payment Pre-Aggregation Contract & Dominant Payment Selection
Project: Gradient Learnings Data Analytics Hackathon 2026 (Olist)

Creates a validated order-grain aggregation from olist_order_payments_dataset.csv:
1. Calculates core settlement metrics:
   - payment_value_total (sum of payment_value)
   - payment_line_count (count of payment records per order)
   - payment_type_count (nunique of payment_type)
   - payment_installments_max (max installments)
   - payment_installments_min (min installments)
   - payment_installments_mean (mean installments)
   - multi_payment_flag (payment_line_count > 1)
2. Implements transparent dominant payment type selection rule:
   - dominant_payment_type: payment_type with highest cumulative payment_value for that order;
     tie-breaker is alphabetical ascending.
3. Output is guaranteed to be exactly 1 row = 1 order_id (99,440 rows).
4. Emits audit summary to outputs/tables/payment_aggregation_audit.csv.
"""

from pathlib import Path
from typing import Tuple, Dict, Any
import pandas as pd
import numpy as np


def aggregate_order_payments(
    payments_path: Path,
    output_audit_path: Path = None,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Aggregates raw order payments into an order-grain DataFrame with dominant payment type.
    Returns:
        (order_payments_aggregated_df, audit_summary_df)
    """
    df_payments = pd.read_csv(payments_path)

    # Basic aggregations per order
    order_base = df_payments.groupby("order_id").agg(
        payment_value_total=("payment_value", "sum"),
        payment_line_count=("payment_sequential", "count"),
        payment_type_count=("payment_type", "nunique"),
        payment_installments_max=("payment_installments", "max"),
        payment_installments_min=("payment_installments", "min"),
        payment_installments_mean=("payment_installments", "mean"),
    )

    order_base["multi_payment_flag"] = order_base["payment_line_count"] > 1

    # Dominant Payment Type Rule:
    # 1. Group by order_id + payment_type, sum payment_value
    # 2. Sort by payment_value DESC, payment_type ASC
    # 3. Drop duplicates keeping first
    type_spend = df_payments.groupby(["order_id", "payment_type"])["payment_value"].sum().reset_index()
    type_spend = type_spend.sort_values(
        by=["order_id", "payment_value", "payment_type"],
        ascending=[True, False, True]
    )
    dom_type = type_spend.drop_duplicates(subset=["order_id"], keep="first").set_index("order_id")["payment_type"]
    order_base["dominant_payment_type"] = dom_type

    order_pmt_agg = order_base.reset_index()

    # Integrity verification
    assert len(order_pmt_agg) == order_pmt_agg["order_id"].nunique(), "Payment aggregation grain violated!"
    assert len(order_pmt_agg) == 99440, f"Expected 99,440 orders in payments, got {len(order_pmt_agg)}"

    # Audit metrics
    total_raw_rows = len(df_payments)
    multi_pmt_orders = int(order_pmt_agg["multi_payment_flag"].sum())
    total_settlement = float(order_pmt_agg["payment_value_total"].sum())

    audit_data = [
        {"metric": "total_raw_payment_rows", "value": total_raw_rows},
        {"metric": "total_orders_in_payments", "value": len(order_pmt_agg)},
        {"metric": "multi_payment_orders_count", "value": multi_pmt_orders},
        {"metric": "multi_payment_orders_pct", "value": round(multi_pmt_orders / len(order_pmt_agg) * 100.0, 4)},
        {"metric": "total_settlement_value_brl", "value": round(total_settlement, 2)},
        {"metric": "dominant_payment_type_rule", "value": "Max cumulative payment value per order, tie-break alphabetical ASC"},
    ]
    audit_df = pd.DataFrame(audit_data)

    if output_audit_path is not None:
        output_audit_path.parent.mkdir(parents=True, exist_ok=True)
        audit_df.to_csv(output_audit_path, index=False)

    return order_pmt_agg, audit_df


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent
    pmts_p = base_dir / "data" / "raw" / "olist_order_payments_dataset.csv"
    audit_p = base_dir / "outputs" / "tables" / "payment_aggregation_audit.csv"

    pmt_agg, audit_df = aggregate_order_payments(pmts_p, audit_p)
    print("Payment aggregation complete.")
    print(f"Aggregated payments: {len(pmt_agg)} orders.")
    print(audit_df.to_string())
