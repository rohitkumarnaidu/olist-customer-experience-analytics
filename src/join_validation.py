"""
join_validation.py -- Reusable Join Validation & Telemetry Framework
Project: Gradient Learnings Data Analytics Hackathon 2026 (Olist)

Enforces strict relational join integrity across the analytical pipeline.
Guarantees that joins do not silently cause row multiplication, key duplication,
or unexpected null introduction.

Minimum required validation functions:
- validate_row_count()
- validate_unique_key()
- validate_order_grain()
- validate_no_row_explosion()
- validate_join_completeness()
- validate_expected_cardinality()

Tracks join telemetry:
- rows_before
- rows_after
- unique_orders_before
- unique_orders_after
- duplicate_orders_after
- new_null_keys
"""

from typing import Dict, Any, List, Optional
import pandas as pd


class JoinIntegrityError(AssertionError):
    """Raised when a join operation violates data contracts or cardinality constraints."""
    pass


def validate_row_count(
    df: pd.DataFrame,
    expected_count: int,
    label: str = "DataFrame",
) -> None:
    """Asserts that the row count matches exactly."""
    actual_count = len(df)
    if actual_count != expected_count:
        raise JoinIntegrityError(
            f"[{label}] Row count mismatch! Expected {expected_count}, got {actual_count}."
        )


def validate_unique_key(
    df: pd.DataFrame,
    key_col: str,
    label: str = "DataFrame",
) -> None:
    """Asserts that key_col has 0 nulls and 0 duplicate values."""
    if key_col not in df.columns:
        raise JoinIntegrityError(f"[{label}] Key column '{key_col}' missing from DataFrame!")
    null_count = int(df[key_col].isnull().sum())
    dup_count = int(df[key_col].duplicated().sum())
    if null_count > 0 or dup_count > 0:
        raise JoinIntegrityError(
            f"[{label}] Key integrity violated on '{key_col}'! "
            f"Nulls: {null_count}, Duplicates: {dup_count}."
        )


def validate_order_grain(
    df: pd.DataFrame,
    order_col: str = "order_id",
    label: str = "DataFrame",
) -> None:
    """Asserts that exactly 1 row = 1 order_id."""
    validate_unique_key(df, order_col, label)
    if len(df) != df[order_col].nunique():
        raise JoinIntegrityError(
            f"[{label}] Order grain violated! Total rows ({len(df)}) != unique orders ({df[order_col].nunique()})."
        )


def validate_no_row_explosion(
    df_before: pd.DataFrame,
    df_after: pd.DataFrame,
    label: str = "Join Operation",
) -> None:
    """Asserts that the join did not multiply rows beyond df_before."""
    if len(df_after) > len(df_before):
        raise JoinIntegrityError(
            f"[{label}] Row explosion detected! Rows before: {len(df_before)}, rows after: {len(df_after)}."
        )


def validate_join_completeness(
    df: pd.DataFrame,
    key_col: str,
    expected_keys: set,
    label: str = "Join Operation",
) -> None:
    """Asserts that all expected keys are retained."""
    actual_keys = set(df[key_col].dropna())
    missing_keys = expected_keys - actual_keys
    if missing_keys:
        raise JoinIntegrityError(
            f"[{label}] Join dropped expected keys! Missing {len(missing_keys)} keys out of {len(expected_keys)}."
        )


def validate_expected_cardinality(
    df_left: pd.DataFrame,
    df_right: pd.DataFrame,
    df_joined: pd.DataFrame,
    join_type: str = "left",
    label: str = "Join Operation",
) -> None:
    """Asserts cardinality invariants according to join type."""
    if join_type == "left":
        if len(df_joined) != len(df_left):
            raise JoinIntegrityError(
                f"[{label}] Left join changed row count! Left rows: {len(df_left)}, joined rows: {len(df_joined)}."
            )
    elif join_type == "inner":
        if len(df_joined) > min(len(df_left), len(df_right)):
            raise JoinIntegrityError(
                f"[{label}] Inner join exploded! Left: {len(df_left)}, Right: {len(df_right)}, Joined: {len(df_joined)}."
            )


class JoinTracker:
    """
    Records telemetry across sequential join steps to produce an auditable join log.

    Enhanced for Module 2 with:
    - source_table and right_table tracking
    - join_type and cardinality_expected
    - matched / unmatched / match_rate metrics
    - columns_added tracking
    """
    def __init__(self, primary_key: str = "order_id"):
        self.primary_key = primary_key
        self.telemetry: List[Dict[str, Any]] = []

    def record_join(
        self,
        step_name: str,
        df_before: pd.DataFrame,
        df_after: pd.DataFrame,
        join_key: str,
        *,
        source_table: str = "",
        right_table: str = "",
        join_type: str = "left",
        cardinality_expected: str = "1:1",
    ) -> Dict[str, Any]:
        """Validates the join, records telemetry, and raises on grain breach."""
        rows_before = len(df_before)
        rows_after = len(df_after)
        unique_orders_before = df_before[self.primary_key].nunique() if self.primary_key in df_before.columns else 0
        unique_orders_after = df_after[self.primary_key].nunique() if self.primary_key in df_after.columns else 0
        duplicate_orders_after = rows_after - unique_orders_after

        # Count newly introduced nulls on the join key
        nulls_before = df_before[join_key].isnull().sum() if join_key in df_before.columns else 0
        nulls_after = df_after[join_key].isnull().sum() if join_key in df_after.columns else 0
        new_null_keys = max(0, int(nulls_after - nulls_before))

        # Columns added by this join
        cols_before = set(df_before.columns)
        cols_after = set(df_after.columns)
        columns_added = sorted(cols_after - cols_before)

        # Match / unmatched rate (check for new nulls on a newly added column)
        matched = rows_before  # left join preserves all left rows
        unmatched = 0
        if columns_added:
            sample_col = columns_added[0]
            unmatched = int(df_after[sample_col].isnull().sum())
            matched = rows_after - unmatched
        match_rate = round(matched / rows_after * 100, 4) if rows_after > 0 else 0

        # Enforce no row explosion & strict order grain
        validate_no_row_explosion(df_before, df_after, step_name)
        validate_order_grain(df_after, self.primary_key, step_name)

        record = {
            "step": step_name,
            "source_table": source_table,
            "right_table": right_table,
            "join_key": join_key,
            "join_type": join_type,
            "cardinality_expected": cardinality_expected,
            "rows_before": rows_before,
            "rows_after": rows_after,
            "unique_orders_before": unique_orders_before,
            "unique_orders_after": unique_orders_after,
            "duplicate_orders_after": duplicate_orders_after,
            "matched": matched,
            "unmatched": unmatched,
            "match_rate_pct": match_rate,
            "new_null_keys": new_null_keys,
            "columns_added_count": len(columns_added),
            "columns_added": "; ".join(columns_added) if columns_added else "",
            "status": "PASSED",
        }
        self.telemetry.append(record)
        return record

    def to_dataframe(self) -> pd.DataFrame:
        """Returns recorded join telemetry as a DataFrame."""
        return pd.DataFrame(self.telemetry)
