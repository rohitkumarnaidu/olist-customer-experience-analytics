"""
test_module5_business_prioritization.py — Automated Test Suite for Module 5
Project: Gradient Learnings Data Analytics Hackathon 2026 (Olist Marketplace Diagnostic)

Validates:
1. Population denominators and zero double-counting across segments.
2. Mutually exclusive survey timing partitioning (sum == 95,824 orders).
3. Delay strata exposure and invariant sums (sum == 12,272 low reviews).
4. Minimum sample threshold compliance (N >= 100 sellers/corridors, N >= 200 categories).
5. Prioritization score mathematical determinism and P0/P1/P2 consistency.
6. Table persistence and schema integrity across all 11 Module 5 CSV tables.
7. Figure persistence, non-emptiness, and 300 DPI sizing (> 50 KB) across Figures 25–30.
"""

import os
from pathlib import Path
import pytest
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
TABLES_DIR = BASE_DIR / "outputs" / "tables"
FIGURES_DIR = BASE_DIR / "outputs" / "figures"


@pytest.fixture(scope="module")
def analytical_model():
    parquet_path = PROCESSED_DIR / "analytical_model.parquet"
    assert parquet_path.exists(), f"Missing analytical model: {parquet_path}"
    return pd.read_parquet(parquet_path)


# =============================================================================
# 1. POPULATION INVARIANTS & INTEGRITY
# =============================================================================
def test_population_e_denominators(analytical_model):
    """Verifies that Population E maintains exact certified count 95,824."""
    df = analytical_model
    is_pop_e = (
        (df['order_status'] == 'delivered') &
        df['order_delivered_customer_date'].notna() &
        df['review_score'].notna()
    )
    df_e = df[is_pop_e]
    assert len(df_e) == 95824, f"Expected Population E to be 95,824, got {len(df_e)}"
    low_reviews = (df_e['review_score'] <= 2).sum()
    assert low_reviews == 12272, f"Expected 12,272 low reviews in Pop E, got {low_reviews}"


def test_survey_timing_mutually_exclusive_partition(analytical_model):
    """Verifies that survey timing partition is strictly mutually exclusive and exhaustive."""
    df = analytical_model
    is_pop_e = (
        (df['order_status'] == 'delivered') &
        df['order_delivered_customer_date'].notna() &
        df['review_score'].notna()
    )
    df_e = df[is_pop_e].copy()

    t_deliv = pd.to_datetime(df_e['order_delivered_customer_date'])
    t_create = pd.to_datetime(df_e['review_creation_date'])

    strict_pre = (t_create.dt.date < t_deliv.dt.date).sum()
    same_day = (t_create.dt.date == t_deliv.dt.date).sum()
    strict_post = (t_create.dt.date > t_deliv.dt.date).sum()

    assert strict_pre == 4976, f"Expected 4,976 strict calendar pre-delivery, got {strict_pre}"
    assert same_day == 3164, f"Expected 3,164 same-day ambiguous, got {same_day}"
    assert strict_post == 87684, f"Expected 87,684 clearly post-delivery, got {strict_post}"
    assert (strict_pre + same_day + strict_post) == 95824, "Survey timing partitions do not sum to 95,824!"


def test_delay_strata_invariants():
    """Verifies that delay strata sum to 100% of Population E and 100% of low reviews."""
    delay_path = TABLES_DIR / "high_risk_delay_segments.csv"
    assert delay_path.exists()
    df = pd.read_csv(delay_path)

    assert df['orders'].sum() == 95824, f"Delay strata orders sum to {df['orders'].sum()}, expected 95,824"
    assert df['low_reviews'].sum() == 12272, f"Delay strata low reviews sum to {df['low_reviews'].sum()}, expected 12,272"
    assert np.isclose(df['dissatisfaction_share_pct'].sum(), 100.0, atol=0.01), "Dissatisfaction share does not sum to 100%"


# =============================================================================
# 2. SAMPLE THRESHOLD COMPLIANCE
# =============================================================================
def test_corridor_sample_threshold():
    """Verifies that all evaluated corridors strictly meet N >= 100 threshold."""
    corr_path = TABLES_DIR / "high_risk_geographic_segments.csv"
    assert corr_path.exists()
    df = pd.read_csv(corr_path)
    min_orders = df['orders'].min()
    assert min_orders >= 100, f"Found corridor with {min_orders} orders (< 100 threshold)"


def test_category_sample_threshold():
    """Verifies that all evaluated categories strictly meet N >= 200 threshold."""
    cat_path = TABLES_DIR / "high_risk_category_segments.csv"
    assert cat_path.exists()
    df = pd.read_csv(cat_path)
    min_orders = df['orders'].min()
    assert min_orders >= 200, f"Found category with {min_orders} orders (< 200 threshold)"


# =============================================================================
# 3. PRIORITIZATION SCORE MATHEMATICAL INTEGRITY
# =============================================================================
def test_prioritization_score_math():
    """Verifies that Priority Score exactly equals product of its 4 component scores."""
    p_path = TABLES_DIR / "prioritization_score.csv"
    assert p_path.exists()
    df = pd.read_csv(p_path)

    for _, r in df.iterrows():
        expected_score = r['Severity_Score'] * r['Exposure_Score'] * r['Actionability_Score'] * r['Evidence_Score']
        assert r['Priority_Score'] == expected_score, f"Prioritization score math mismatch for {r['Intervention_ID']}"
        assert 1 <= r['Severity_Score'] <= 5
        assert 1 <= r['Exposure_Score'] <= 5
        assert 1 <= r['Actionability_Score'] <= 5
        assert 1 <= r['Evidence_Score'] <= 5

    # Verify P0 rankings have top priority scores
    p0_items = df[df['P_Rank'] == 'P0 — Immediate']
    assert len(p0_items) >= 2, "Expected at least 2 P0 immediate interventions"
    assert (p0_items['Priority_Score'] >= 300).all(), "P0 items should have priority scores >= 300"


# =============================================================================
# 4. TABLE PERSISTENCE & SCHEMA AUDIT
# =============================================================================
REQUIRED_M5_TABLES = [
    ("root_cause_contribution_matrix.csv", ["Level", "Factor", "Evidence_Type", "Effect_Size", "Actionability", "Priority"]),
    ("high_risk_delay_segments.csv", ["delay_stratum", "orders", "gmv", "low_reviews", "dissatisfaction_share_pct"]),
    ("high_risk_seller_segments.csv", ["seller_cohort", "qualified_sellers", "total_orders", "total_low_reviews"]),
    ("high_risk_geographic_segments.csv", ["corridor", "orders", "late_rate", "severe_late_rate", "low_review_rate"]),
    ("high_risk_category_segments.csv", ["dominant_category", "orders", "low_reviews", "dissatisfaction_share_pct"]),
    ("survey_timing_segments.csv", ["survey_timing_partition", "orders", "low_reviews", "low_review_rate"]),
    ("high_impact_combinations.csv", ["Combination_ID", "Combination_Name", "Order_Count", "Low_Reviews", "Dissatisfaction_Share_Pct"]),
    ("business_exposure_segments.csv", ["Segment_Category", "Segment_Name", "Order_Count", "Order_Exposure_Pct", "Dissatisfaction_Exposure_Pct"]),
    ("prioritization_score.csv", ["Intervention_ID", "Intervention_Name", "Priority_Score", "P_Rank", "Owner"]),
    ("executive_scorecard.csv", ["KPI_Code", "Metric_Name", "Current_Value", "Target_Benchmark", "Priority_Tier"]),
    ("module5_finding_register.csv", ["Finding", "Metric", "Evidence", "Exposure", "Mechanism", "Action", "Priority"])
]


@pytest.mark.parametrize("filename,expected_cols", REQUIRED_M5_TABLES)
def test_required_table_existence_and_schema(filename, expected_cols):
    """Verifies that every required Module 5 table exists, is non-empty, and contains expected columns."""
    filepath = TABLES_DIR / filename
    assert filepath.exists(), f"Missing required table: {filepath}"
    df = pd.read_csv(filepath)
    assert len(df) > 0, f"Table {filename} is empty!"
    for col in expected_cols:
        assert col in df.columns, f"Missing column '{col}' in {filename}. Available: {df.columns.tolist()}"


# =============================================================================
# 5. FIGURE PERSISTENCE & 300 DPI SIZE AUDIT
# =============================================================================
REQUIRED_M5_FIGURES = [
    "fig25_root_cause_contribution_matrix.png",
    "fig26_high_impact_segment_exposure_matrix.png",
    "fig27_corridor_risk_bubble_scatter.png",
    "fig28_p0_p1_p2_opportunity_matrix.png",
    "fig29_root_cause_waterfall_decision_framework.png",
    "fig30_executive_prioritization_scorecard.png"
]


@pytest.mark.parametrize("figname", REQUIRED_M5_FIGURES)
def test_required_figure_existence_and_size(figname):
    """Verifies that all 6 Module 5 publication figures exist, are non-empty, and exceed 50 KB (300 DPI check)."""
    figpath = FIGURES_DIR / figname
    assert figpath.exists(), f"Missing figure: {figpath}"
    file_size = figpath.stat().st_size
    assert file_size > 50000, f"Figure {figname} is suspiciously small ({file_size} bytes), check DPI!"


# =============================================================================
# 6. ZERO-TRUST AUDIT TABLES & DEDUPLICATION VERIFICATION
# =============================================================================
REQUIRED_AUDIT_TABLES = [
    ("module5_root_cause_language_audit.csv", ["Factor", "Current_Label", "Approved_Zero_Trust_Label"]),
    ("module5_intervention_overlap.csv", ["Intervention", "Target_Orders", "Observed_Low_Reviews"]),
    ("prioritization_sensitivity.csv", ["ID", "Original_Score", "Rank_Original", "Rank_Equal", "Rank_Exposure", "Rank_Evidence", "Rank_Actionability"]),
    ("intervention_counterfactual_audit.csv", ["Claim_ID", "Original_Phrasing", "Audit_Classification", "Approved_Correction"]),
    ("target_threshold_audit.csv", ["KPI_Code", "Metric", "Proposed_Target", "Classification"]),
    ("recommendation_evidence_chain.csv", ["Intervention_ID", "Observed_Problem", "Empirical_Evidence", "Recommended_Pilot", "Success_KPI"]),
    ("module5_final_findings.csv", ["Finding_ID", "Title", "Empirical_Fact", "Priority_Tier"])
]


@pytest.mark.parametrize("filename,expected_cols", REQUIRED_AUDIT_TABLES)
def test_zero_trust_audit_tables_exist_and_valid(filename, expected_cols):
    """Verifies that all 7 Zero-Trust Audit tables exist, are populated, and have expected schemas."""
    filepath = TABLES_DIR / filename
    assert filepath.exists(), f"Missing audit table: {filepath}"
    df = pd.read_csv(filepath)
    assert len(df) > 0, f"Audit table {filename} is empty!"
    for col in expected_cols:
        assert col in df.columns, f"Missing column '{col}' in {filename}"


def test_intervention_overlap_deduplication_accounting():
    """Verifies that inter-intervention overlap is correctly quantified and deduplicated."""
    overlap_path = TABLES_DIR / "module5_intervention_overlap.csv"
    assert overlap_path.exists()
    df = pd.read_csv(overlap_path)

    unique_row = df[df['Intervention'].str.contains('UNIQUE TOTAL')]
    gross_row = df[df['Intervention'].str.contains('GROSS TOTAL')]
    overlap_row = df[df['Intervention'].str.contains('OVERLAP')]

    assert len(unique_row) == 1, "Missing UNIQUE TOTAL row in overlap table"
    assert len(gross_row) == 1, "Missing GROSS TOTAL row in overlap table"
    assert len(overlap_row) == 1, "Missing OVERLAP row in overlap table"

    unique_low = unique_row['Observed_Low_Reviews'].iloc[0]
    gross_low = gross_row['Observed_Low_Reviews'].iloc[0]

    # Verify that unique low reviews is strictly 7,005 and less than gross sum 14,255
    assert unique_low == 7005, f"Expected 7,005 unique low reviews, got {unique_low}"
    assert gross_low == 14255, f"Expected 14,255 gross low reviews, got {gross_low}"
    assert unique_low < 12272, "Unique low reviews must not exceed total delivered low reviews (12,272)"

    # Verify overlap percentage is ~50.86%
    overlap_rate = (gross_low - unique_low) / gross_low * 100.0
    assert 50.0 <= overlap_rate <= 52.0, f"Overlap rate {overlap_rate}% outside expected 50-52% range"

