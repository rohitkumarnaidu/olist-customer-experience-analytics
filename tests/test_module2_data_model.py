"""
test_module2_data_model.py -- Module 2 Extended Test Suite
Project: Gradient Learnings Data Analytics Hackathon 2026 (Olist)

Tests the analytical model (Layer H), data model features,
join audit, reproducibility, and idempotency guarantees.
"""

from pathlib import Path
import sys
import pytest
import pandas as pd
import numpy as np

_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

DATA_DIR = _project_root / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
TABLES_DIR = _project_root / "outputs" / "tables"

ANALYTICAL_MODEL_PATH = PROCESSED_DIR / "analytical_model.parquet"
CANONICAL_BASE_PATH = PROCESSED_DIR / "order_analytics_base.parquet"
JOIN_AUDIT_PATH = TABLES_DIR / "join_audit.csv"
DATA_DICT_PATH = TABLES_DIR / "order_analytics_data_dictionary.csv"

EXPECTED_ORDER_COUNT = 99441


# ==============================================================================
# FIXTURES
# ==============================================================================

@pytest.fixture(scope="module")
def canonical_base():
    """Load the canonical order analytics base (Layer D)."""
    assert CANONICAL_BASE_PATH.exists(), f"Canonical base not found: {CANONICAL_BASE_PATH}"
    return pd.read_parquet(CANONICAL_BASE_PATH)


@pytest.fixture(scope="module")
def analytical_model():
    """Load the analytical model (Layer H)."""
    assert ANALYTICAL_MODEL_PATH.exists(), f"Analytical model not found: {ANALYTICAL_MODEL_PATH}"
    return pd.read_parquet(ANALYTICAL_MODEL_PATH)


@pytest.fixture(scope="module")
def join_audit():
    """Load the join audit log."""
    assert JOIN_AUDIT_PATH.exists(), f"Join audit not found: {JOIN_AUDIT_PATH}"
    return pd.read_csv(JOIN_AUDIT_PATH)


@pytest.fixture(scope="module")
def data_dict():
    """Load the data dictionary."""
    assert DATA_DICT_PATH.exists(), f"Data dictionary not found: {DATA_DICT_PATH}"
    return pd.read_csv(DATA_DICT_PATH)


# ==============================================================================
# 1. GRAIN INVARIANTS
# ==============================================================================

class TestGrainInvariants:
    """Tests that the fundamental 1 row = 1 order_id grain is preserved."""

    def test_canonical_base_row_count(self, canonical_base):
        assert len(canonical_base) == EXPECTED_ORDER_COUNT

    def test_canonical_base_order_uniqueness(self, canonical_base):
        assert canonical_base["order_id"].nunique() == EXPECTED_ORDER_COUNT

    def test_canonical_base_no_null_order_id(self, canonical_base):
        assert canonical_base["order_id"].isnull().sum() == 0

    def test_analytical_model_row_count(self, analytical_model):
        assert len(analytical_model) == EXPECTED_ORDER_COUNT

    def test_analytical_model_order_uniqueness(self, analytical_model):
        assert analytical_model["order_id"].nunique() == EXPECTED_ORDER_COUNT

    def test_analytical_model_no_null_order_id(self, analytical_model):
        assert analytical_model["order_id"].isnull().sum() == 0

    def test_grain_consistency_between_layers(self, canonical_base, analytical_model):
        """Layer D and Layer H must have the same set of order_ids."""
        base_ids = set(canonical_base["order_id"])
        model_ids = set(analytical_model["order_id"])
        assert base_ids == model_ids


# ==============================================================================
# 2. LAYER E -- MISSINGNESS FLAGS
# ==============================================================================

class TestMissingnessFlags:
    """Tests that missingness flags correctly reflect null presence."""

    MISSINGNESS_PAIRS = [
        ("has_items", "item_count"),
        ("has_payment_record", "payment_value_total"),
        ("has_review", "review_score"),
        ("has_customer_coordinates", "customer_lat"),
        ("has_seller_coordinates", "seller_lat"),
        ("has_product_category", "dominant_category"),
        ("has_delivery_date", "order_delivered_customer_date"),
        ("has_approval_date", "order_approved_at"),
        ("has_carrier_date", "order_delivered_carrier_date"),
    ]

    @pytest.mark.parametrize("flag_col,source_col", MISSINGNESS_PAIRS)
    def test_missingness_flag_exists(self, analytical_model, flag_col, source_col):
        assert flag_col in analytical_model.columns, f"Missing flag column: {flag_col}"

    @pytest.mark.parametrize("flag_col,source_col", MISSINGNESS_PAIRS)
    def test_missingness_flag_consistency(self, analytical_model, flag_col, source_col):
        """Flag should be True where source is not null, False where null."""
        expected = analytical_model[source_col].notnull()
        actual = analytical_model[flag_col]
        mismatches = (expected != actual).sum()
        assert mismatches == 0, (
            f"Missingness flag {flag_col} has {mismatches} mismatches with {source_col}"
        )


# ==============================================================================
# 3. LAYER F -- ANALYTICAL FEATURES
# ==============================================================================

class TestAnalyticalFeatures:
    """Tests review, item, and financial feature engineering."""

    def test_low_review_flag_values(self, analytical_model):
        """low_review_flag should only be True where review_score <= 2."""
        has_review = analytical_model["review_score"].notnull()
        low = analytical_model.loc[has_review, "low_review_flag"]
        score = analytical_model.loc[has_review, "review_score"]
        assert (low == (score <= 2)).all()

    def test_high_review_flag_values(self, analytical_model):
        """high_review_flag should only be True where review_score >= 4."""
        has_review = analytical_model["review_score"].notnull()
        high = analytical_model.loc[has_review, "high_review_flag"]
        score = analytical_model.loc[has_review, "review_score"]
        assert (high == (score >= 4)).all()

    def test_review_text_available_consistency(self, analytical_model):
        expected = analytical_model["review_comment_message"].notnull()
        assert (analytical_model["review_text_available"] == expected).all()

    def test_multi_item_order_consistency(self, analytical_model):
        """multi_item_order should be True where item_count > 1."""
        has_items = analytical_model["item_count"].notnull()
        actual = analytical_model.loc[has_items, "multi_item_order"]
        expected = analytical_model.loc[has_items, "item_count"] > 1
        assert (actual == expected).all()

    def test_freight_share_pct_range(self, analytical_model):
        """freight_share_pct should be 0-100 where present."""
        valid = analytical_model["freight_share_pct"].dropna()
        assert (valid >= 0).all()
        assert (valid <= 100).all()

    def test_discrepancy_bucket_values(self, analytical_model):
        valid_buckets = {"exact_match", "minor_<1", "small_<10", "medium_<100", "large_>=100", "no_data"}
        actual_buckets = set(analytical_model["discrepancy_bucket"].unique())
        assert actual_buckets.issubset(valid_buckets), f"Unexpected buckets: {actual_buckets - valid_buckets}"


# ==============================================================================
# 4. LAYER G -- TEMPORAL FEATURES
# ==============================================================================

class TestTemporalFeatures:
    """Tests date-derived dimensions."""

    TEMPORAL_COLUMNS = [
        "purchase_year", "purchase_month", "purchase_year_month",
        "purchase_quarter", "purchase_day_of_week", "purchase_day_name",
        "purchase_hour", "is_weekend_purchase",
        "delivery_days_total", "delivered_on_time", "delivery_delay_days",
        "approval_to_carrier_days", "carrier_to_delivery_days",
    ]

    @pytest.mark.parametrize("col", TEMPORAL_COLUMNS)
    def test_temporal_column_exists(self, analytical_model, col):
        assert col in analytical_model.columns, f"Missing temporal column: {col}"

    def test_purchase_year_range(self, analytical_model):
        years = analytical_model["purchase_year"].dropna()
        assert years.min() >= 2016
        assert years.max() <= 2018

    def test_purchase_month_range(self, analytical_model):
        months = analytical_model["purchase_month"].dropna()
        assert months.min() >= 1
        assert months.max() <= 12

    def test_purchase_quarter_range(self, analytical_model):
        quarters = analytical_model["purchase_quarter"].dropna()
        assert quarters.min() >= 1
        assert quarters.max() <= 4

    def test_purchase_day_of_week_range(self, analytical_model):
        days = analytical_model["purchase_day_of_week"].dropna()
        assert days.min() >= 0
        assert days.max() <= 6

    def test_purchase_hour_range(self, analytical_model):
        hours = analytical_model["purchase_hour"].dropna()
        assert hours.min() >= 0
        assert hours.max() <= 23

    def test_weekend_flag_consistency(self, analytical_model):
        """is_weekend_purchase should be True only for Saturday (5) and Sunday (6)."""
        valid = analytical_model["purchase_day_of_week"].notnull()
        weekend = analytical_model.loc[valid, "is_weekend_purchase"]
        dow = analytical_model.loc[valid, "purchase_day_of_week"]
        expected = dow.isin([5, 6])
        assert (weekend == expected).all()

    def test_delivery_days_non_negative(self, analytical_model):
        """Total delivery days should be non-negative for valid entries."""
        valid = analytical_model["delivery_days_total"].dropna()
        # Allow very small negative values from timestamp precision
        assert (valid >= -0.1).all()


# ==============================================================================
# 5. JOIN AUDIT
# ==============================================================================

class TestJoinAudit:
    """Tests the join audit telemetry."""

    def test_join_audit_exists(self, join_audit):
        assert len(join_audit) == 6, f"Expected 6 join steps, got {len(join_audit)}"

    def test_all_joins_passed(self, join_audit):
        assert (join_audit["status"] == "PASSED").all()

    def test_no_row_explosion(self, join_audit):
        for _, row in join_audit.iterrows():
            assert row["rows_after"] == row["rows_before"], (
                f"Row explosion at step {row['step']}: "
                f"{row['rows_before']} -> {row['rows_after']}"
            )

    def test_join_audit_has_required_fields(self, join_audit):
        required = [
            "step", "source_table", "right_table", "join_key",
            "join_type", "cardinality_expected", "rows_before", "rows_after",
            "matched", "unmatched", "match_rate_pct", "status",
        ]
        for field in required:
            assert field in join_audit.columns, f"Missing audit field: {field}"


# ==============================================================================
# 6. DATA DICTIONARY
# ==============================================================================

class TestDataDictionary:
    """Tests the data dictionary completeness."""

    def test_data_dict_exists(self, data_dict):
        assert len(data_dict) > 0

    def test_data_dict_covers_all_columns(self, analytical_model, data_dict):
        model_cols = set(analytical_model.columns)
        dict_cols = set(data_dict["column_name"])
        missing = model_cols - dict_cols
        assert len(missing) == 0, f"Data dictionary missing columns: {missing}"

    def test_data_dict_has_required_fields(self, data_dict):
        required = ["column_name", "layer", "dtype", "null_count", "description"]
        for field in required:
            assert field in data_dict.columns, f"Missing dict field: {field}"


# ==============================================================================
# 7. IDEMPOTENCY & REPRODUCIBILITY
# ==============================================================================

class TestIdempotency:
    """Tests that the pipeline produces consistent results."""

    def test_canonical_base_parquet_and_csv_match(self):
        """Parquet and CSV representations should have the same row count."""
        base_pq = pd.read_parquet(CANONICAL_BASE_PATH)
        base_csv = pd.read_csv(PROCESSED_DIR / "order_analytics_base.csv", low_memory=False)
        assert len(base_pq) == len(base_csv)
        assert set(base_pq.columns) == set(base_csv.columns)

    def test_analytical_model_parquet_and_csv_match(self):
        """Parquet and CSV representations should have the same row count."""
        model_pq = pd.read_parquet(ANALYTICAL_MODEL_PATH)
        model_csv = pd.read_csv(PROCESSED_DIR / "analytical_model.csv", low_memory=False)
        assert len(model_pq) == len(model_csv)
        assert set(model_pq.columns) == set(model_csv.columns)


# ==============================================================================
# 8. FINANCIAL INTEGRITY
# ==============================================================================

class TestFinancialIntegrity:
    """Tests financial metric consistency."""

    def test_gmv_equals_price_plus_freight(self, analytical_model):
        """order_gmv should equal item_price_total + freight_total."""
        has_items = analytical_model["item_count"].notnull()
        gmv = analytical_model.loc[has_items, "order_gmv"]
        price = analytical_model.loc[has_items, "item_price_total"]
        freight = analytical_model.loc[has_items, "freight_total"]
        diff = (gmv - (price + freight)).abs()
        assert (diff < 0.01).all(), f"GMV != price + freight for {(diff >= 0.01).sum()} rows"

    def test_financial_diff_computation(self, analytical_model):
        """financial_diff should equal GMV - payment_value_total (where both exist)."""
        both = analytical_model["order_gmv"].notnull() & analytical_model["payment_value_total"].notnull()
        gmv = analytical_model.loc[both, "order_gmv"]
        pmt = analytical_model.loc[both, "payment_value_total"]
        expected = gmv - pmt
        actual = analytical_model.loc[both, "financial_diff"]
        diff = (expected - actual).abs()
        assert (diff < 0.01).all()

    def test_reconciled_flag_consistency(self, analytical_model):
        """financial_reconciled_flag should be True where |diff| < 0.01."""
        flag = analytical_model["financial_reconciled_flag"]
        abs_diff = analytical_model["financial_abs_diff"]
        expected = abs_diff < 0.01
        assert (flag == expected).all()


# ==============================================================================
# 9. DELIVERY ANALYSIS POPULATION
# ==============================================================================

class TestDeliveryPopulation:
    """Tests delivery population flags."""

    def test_is_delivered_consistency(self, analytical_model):
        expected = analytical_model["order_status"] == "delivered"
        assert (analytical_model["is_delivered"] == expected).all()

    def test_eligible_for_delivery_analysis(self, analytical_model):
        expected = analytical_model["is_delivered"] & analytical_model["has_delivery_date"]
        assert (analytical_model["eligible_for_delivery_analysis"] == expected).all()
