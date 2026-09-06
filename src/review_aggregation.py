"""
review_aggregation.py — Review Data Handling & Order-Level Selection
Project: Gradient Learnings Data Analytics Hackathon 2026 (Olist)

Implements a deterministic, auditable review aggregation and selection pipeline:
1. Preserves 100% of raw review records for granular review-level analysis.
2. Formulates an explicit, deterministic order-level customer-experience selection rule:
   `LATEST_VALID_REVIEW_PER_ORDER`:
   - Primary sort: review_answer_timestamp (descending)
   - Secondary sort: review_creation_date (descending)
   - Tie-breaker: review_id (descending)
3. Quantifies all duplication artifacts (duplicate review IDs, multiple reviews per order,
   score discrepancies, and temporal deltas).
4. Outputs comprehensive audit table to outputs/tables/review_aggregation_audit.csv.
"""

from pathlib import Path
from typing import Tuple, Dict, Any
import pandas as pd
import numpy as np


def analyze_review_structure(df_reviews: pd.DataFrame) -> Dict[str, Any]:
    """
    Performs a deep structural audit of the reviews dataset.
    Quantifies duplicate review IDs, multi-review orders, content variability,
    and temporal deltas.
    """
    total_raw_rows = len(df_reviews)
    unique_review_ids = df_reviews["review_id"].nunique()
    unique_orders_reviewed = df_reviews["order_id"].nunique()

    # Duplicate review_id analysis
    dup_review_id_mask = df_reviews.duplicated(subset=["review_id"], keep=False)
    dup_review_id_rows = int(dup_review_id_mask.sum())
    unique_dup_review_ids = int(df_reviews.loc[dup_review_id_mask, "review_id"].nunique())

    # Multi-review order_id analysis
    multi_order_mask = df_reviews.duplicated(subset=["order_id"], keep=False)
    multi_order_rows = int(multi_order_mask.sum())
    unique_multi_orders = int(df_reviews.loc[multi_order_mask, "order_id"].nunique())

    # Content consistency check on duplicate review_id
    content_cols = [
        "review_score", "review_comment_title", "review_comment_message",
        "review_creation_date", "review_answer_timestamp"
    ]
    dup_reviews_df = df_reviews[dup_review_id_mask]
    content_max_nunique = dup_reviews_df.groupby("review_id")[content_cols].apply(
        lambda g: g.nunique().max()
    ) if not dup_reviews_df.empty else pd.Series([1])
    is_content_identical_for_dup_ids = bool((content_max_nunique <= 1).all())

    # Score dynamics in multi-review orders
    multi_orders_df = df_reviews[multi_order_mask].copy()
    multi_orders_df["review_answer_timestamp"] = pd.to_datetime(multi_orders_df["review_answer_timestamp"])
    multi_orders_df["review_creation_date"] = pd.to_datetime(multi_orders_df["review_creation_date"])
    multi_orders_sorted = multi_orders_df.sort_values(["order_id", "review_answer_timestamp"])

    first_rev = multi_orders_sorted.groupby("order_id").first()
    latest_rev = multi_orders_sorted.groupby("order_id").last()
    score_delta = latest_rev["review_score"] - first_rev["review_score"]

    identical_score_count = int((score_delta == 0).sum())
    improved_score_count = int((score_delta > 0).sum())
    worsened_score_count = int((score_delta < 0).sum())

    # Temporal delta
    time_deltas = multi_orders_sorted.groupby("order_id")["review_answer_timestamp"].apply(
        lambda s: (s.max() - s.min()).total_seconds() / 86400.0
    )
    mean_time_delta_days = float(time_deltas.mean()) if not time_deltas.empty else 0.0
    median_time_delta_days = float(time_deltas.median()) if not time_deltas.empty else 0.0
    max_time_delta_days = float(time_deltas.max()) if not time_deltas.empty else 0.0

    return {
        "total_raw_rows": total_raw_rows,
        "unique_review_ids": unique_review_ids,
        "unique_orders_reviewed": unique_orders_reviewed,
        "duplicate_review_id_rows": dup_review_id_rows,
        "unique_duplicate_review_ids": unique_dup_review_ids,
        "multi_review_order_rows": multi_order_rows,
        "unique_multi_review_orders": unique_multi_orders,
        "is_content_identical_for_dup_ids": is_content_identical_for_dup_ids,
        "identical_score_count": identical_score_count,
        "improved_score_count": improved_score_count,
        "worsened_score_count": worsened_score_count,
        "mean_time_delta_days": round(mean_time_delta_days, 4),
        "median_time_delta_days": round(median_time_delta_days, 4),
        "max_time_delta_days": round(max_time_delta_days, 4),
    }


def select_order_level_reviews(
    df_reviews: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Applies the LATEST_VALID_REVIEW_PER_ORDER rule to extract exactly
    1 review per reviewed order, while computing order-level review metadata.

    Returns:
        (order_level_reviews_df, audit_summary_df)
    """
    df = df_reviews.copy()
    df["review_answer_timestamp_dt"] = pd.to_datetime(df["review_answer_timestamp"])
    df["review_creation_date_dt"] = pd.to_datetime(df["review_creation_date"])

    # Count reviews per order before deduplication
    review_counts = df.groupby("order_id")["review_id"].count().rename("review_count_for_order")

    # Sort deterministically: latest answer timestamp, latest creation date, highest review_id
    df_sorted = df.sort_values(
        by=["order_id", "review_answer_timestamp_dt", "review_creation_date_dt", "review_id"],
        ascending=[True, False, False, False],
    )

    order_level = df_sorted.drop_duplicates(subset=["order_id"], keep="first").copy()
    order_level = order_level.merge(review_counts, on="order_id", how="left")
    order_level["multi_review_flag"] = order_level["review_count_for_order"] > 1

    # Drop temporary datetime sorting columns
    order_level = order_level.drop(columns=["review_answer_timestamp_dt", "review_creation_date_dt"])

    # Build audit summary
    metrics = analyze_review_structure(df_reviews)
    audit_data = [
        {"metric": "total_raw_reviews", "value": metrics["total_raw_rows"]},
        {"metric": "unique_orders_reviewed", "value": metrics["unique_orders_reviewed"]},
        {"metric": "orders_with_multiple_reviews", "value": metrics["unique_multi_review_orders"]},
        {"metric": "multi_review_order_rows", "value": metrics["multi_review_order_rows"]},
        {"metric": "duplicate_review_id_rows", "value": metrics["duplicate_review_id_rows"]},
        {"metric": "unique_duplicate_review_ids", "value": metrics["unique_duplicate_review_ids"]},
        {"metric": "duplicate_id_content_identical", "value": metrics["is_content_identical_for_dup_ids"]},
        {"metric": "multi_review_score_identical_count", "value": metrics["identical_score_count"]},
        {"metric": "multi_review_score_improved_count", "value": metrics["improved_score_count"]},
        {"metric": "multi_review_score_worsened_count", "value": metrics["worsened_score_count"]},
        {"metric": "multi_review_median_time_delta_days", "value": metrics["median_time_delta_days"]},
        {"metric": "multi_review_mean_time_delta_days", "value": metrics["mean_time_delta_days"]},
        {"metric": "raw_rows_retained", "value": metrics["total_raw_rows"]},
        {"metric": "rows_selected_for_order_level_layer", "value": len(order_level)},
        {"metric": "selection_rule", "value": "LATEST_VALID_REVIEW_PER_ORDER (descending answer_timestamp, creation_date, review_id tie-breaker)"},
    ]
    audit_df = pd.DataFrame(audit_data)

    return order_level, audit_df


def run_review_aggregation(
    raw_reviews_path: Path,
    output_audit_path: Path,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Pipeline runner for review aggregation and auditing."""
    df_raw = pd.read_csv(raw_reviews_path)
    order_level_reviews, audit_df = select_order_level_reviews(df_raw)

    output_audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_df.to_csv(output_audit_path, index=False)
    return order_level_reviews, audit_df


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent
    reviews_path = base_dir / "data" / "raw" / "olist_order_reviews_dataset.csv"
    audit_out = base_dir / "outputs" / "tables" / "review_aggregation_audit.csv"

    order_level_df, audit_df = run_review_aggregation(reviews_path, audit_out)
    print("Review aggregation & order-level selection complete.")
    print(f"Raw reviews: 99,224 -> Order-level selected: {len(order_level_df)}")
    print(f"Unique order_id check: {order_level_df['order_id'].nunique()} == {len(order_level_df)}")
    print(f"Audit written to: {audit_out}")
