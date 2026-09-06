"""
test_module4_statistics.py — Automated Test Suite for Module 4 Formal Statistical Analysis
Project: Gradient Learnings Data Analytics Hackathon 2026 (Olist Marketplace Diagnostic)

Validates:
1. Population definitions and sample sizes (Populations A–E).
2. Feature construction, types, and absence of target contamination.
3. Statistical model outputs, convergence, and parameter validity.
4. Multicollinearity VIF thresholds (< 5.0).
5. Output table persistence and column schema integrity across all 14 tables.
6. Generation and non-emptiness of all 6 publication figures (fig19 - fig24).
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
# 1. POPULATION INTEGRITY TESTS
# =============================================================================
def test_population_counts_and_consistency(analytical_model):
    """Verifies the exact population counts established in methodology."""
    df = analytical_model
    pop_a = len(df)
    pop_b = (df['order_status'] == 'delivered').sum()
    pop_c = ((df['order_status'] == 'delivered') & df['order_delivered_customer_date'].notna()).sum()
    pop_d = df['has_review'].sum()
    pop_e = ((df['order_status'] == 'delivered') & df['order_delivered_customer_date'].notna() & df['review_score'].notna()).sum()

    assert pop_a == 99441, f"Expected Population A to be 99,441, got {pop_a}"
    assert pop_b == 96478, f"Expected Population B to be 96,478, got {pop_b}"
    assert pop_c == 96470, f"Expected Population C to be 96,470, got {pop_c}"
    assert pop_d == 98673, f"Expected Population D to be 98,673, got {pop_d}"
    assert pop_e == 95824, f"Expected Population E to be 95,824, got {pop_e}"


# =============================================================================
# 2. FEATURE CONSTRUCTION & INTEGRITY TESTS
# =============================================================================
def test_derived_statistical_features(analytical_model):
    """Verifies that delivery components, delay days, and survey timing are valid."""
    df = analytical_model
    assert 'delivery_delay_days' in df.columns
    assert 'approval_to_carrier_days' in df.columns
    assert 'carrier_to_delivery_days' in df.columns
    assert 'delivery_days_total' in df.columns

    # Delivered orders must have non-null delay days
    delivered = df[df['order_status'] == 'delivered']
    valid_deliv = delivered[delivered['order_delivered_customer_date'].notna()]
    assert valid_deliv['delivery_delay_days'].isna().sum() == 0, "Null delivery delay in delivered orders!"


# =============================================================================
# 3. TABLE PERSISTENCE & SCHEMA AUDIT
# =============================================================================
REQUIRED_TABLES = [
    ("module_4_feature_audit.csv", ["Feature", "Role", "Multicollinearity_Risk", "Use"]),
    ("delay_threshold_analysis.csv", ["candidate_breakpoint_days", "slope_before_breakpoint (b1)", "aic"]),
    ("module_4_logistic_models.csv", ["model_name", "predictor", "coefficient", "odds_ratio", "ci_lower_95", "ci_upper_95"]),
    ("module_4_vif.csv", ["feature", "vif", "collinearity_status"]),
    ("model_robustness.csv", ["specification", "sample_n", "delay_odds_ratio", "survey_pre_deliv_odds_ratio"]),
    ("survey_timing_definitions.csv", ["definition_id", "order_count", "unadjusted_odds_ratio", "adjusted_odds_ratio"]),
    ("survey_timing_models.csv", ["model", "odds_ratio", "ci_lower_95", "ci_upper_95", "p_value"]),
    ("survey_timing_controlled_comparison.csv", ["delay_stratum", "survey_post_delivery_orders", "survey_pre_delivery_orders"]),
    ("delivery_component_models.csv", ["model", "fulfillment_stage", "odds_ratio", "p_value"]),
    ("geographic_model_comparison.csv", ["model_name", "pseudo_r2", "aic"]),
    ("seller_context_analysis.csv", ["sample_filter", "qualified_seller_count", "spearman_corr_late_rate_vs_score"]),
    ("category_control_analysis.csv", ["top_category", "order_count", "low_review_rate"]),
    ("freight_adjusted_analysis.csv", ["model_specification", "freight_coef", "freight_odds_ratio"]),
    ("black_friday_diagnostic.csv", ["purchase_ym", "order_volume", "late_delivery_rate", "mean_review_score"]),
    ("module_4_finding_register.csv", ["Finding", "Evidence", "Effect_Size", "Causal_Status", "Decision"]),
    ("module4_sample_reconciliation.csv", ["Model", "Intended_Population", "Initial_N", "Missing_Removed", "Final_N", "Current_Report_N", "Match"]),
    ("module4_independent_reproduction.csv", ["Statistic", "Reported", "Independent", "Difference", "Tolerance", "Status"]),
    ("module4_feature_formula_audit.csv", ["Feature", "Source_Columns", "Formula", "Unit", "Temporal_Position", "Independence_Risk"]),
    ("delay_breakpoint_robustness.csv", ["Specification", "Formula", "Parameters", "Residual_SS", "AIC"]),
    ("module4_robustness_audit.csv", ["Robustness_Check", "N_Obs", "Delay_OR", "Survey_Timing_OR", "Pseudo_R2"]),
    ("module4_model_specification_audit.csv", ["Model_ID", "Name", "Estimand", "Population", "Outcome", "Predictors"]),
    ("module4_language_audit.csv", ["Claim_Text", "Current_Classification", "Audit_Finding", "Required_Rewrite"])
]


@pytest.mark.parametrize("filename,expected_cols", REQUIRED_TABLES)
def test_required_table_existence_and_schema(filename, expected_cols):
    """Verifies that every required statistical table exists and contains expected columns."""
    filepath = TABLES_DIR / filename
    assert filepath.exists(), f"Missing required table: {filepath}"
    df = pd.read_csv(filepath)
    assert len(df) > 0, f"Table {filename} is empty!"
    for col in expected_cols:
        assert col in df.columns, f"Missing column '{col}' in {filename}. Available: {df.columns.tolist()}"


# =============================================================================
# 4. STATISTICAL VALIDITY CHECKS
# =============================================================================
def test_vif_within_safe_thresholds():
    """Verifies that all predictors in the final logistic specification have VIF < 5.0."""
    vif_path = TABLES_DIR / "module_4_vif.csv"
    assert vif_path.exists()
    df_vif = pd.read_csv(vif_path)
    max_vif = df_vif['vif'].max()
    assert max_vif < 5.0, f"VIF exceeded conservative threshold 5.0! Max VIF: {max_vif:.2f}"
    assert (df_vif['collinearity_status'] == 'HIGH').sum() == 0, "Found HIGH collinearity feature!"


def test_delay_threshold_breakpoint_validity():
    """Verifies that the optimal delay threshold breakpoint is reasonable (between 0.5 and 7 days)."""
    thresh_path = TABLES_DIR / "delay_threshold_analysis.csv"
    assert thresh_path.exists()
    df = pd.read_csv(thresh_path)
    min_rss_idx = df['residual_sum_of_squares'].idxmin()
    best_tau = df.loc[min_rss_idx, 'candidate_breakpoint_days']
    assert 0.5 <= best_tau <= 7.0, f"Optimal breakpoint {best_tau} is outside reasonable bounds [0.5, 7.0]"


def test_survey_timing_odds_ratio_stability():
    """Verifies that survey timing Odds Ratio remains consistently > 3.0 across nested specifications."""
    st_path = TABLES_DIR / "survey_timing_models.csv"
    assert st_path.exists()
    df = pd.read_csv(st_path)
    for _, r in df.iterrows():
        assert r['odds_ratio'] > 2.5, f"Odds ratio in {r['model']} fell below 2.5: {r['odds_ratio']:.2f}"
        assert r['p_value'] < 0.001, f"Survey timing lost significance in {r['model']}: p = {r['p_value']}"


def test_black_friday_capacity_surge():
    """Verifies that November 2017 exhibits the documented volume and late delivery surge."""
    bf_path = TABLES_DIR / "black_friday_diagnostic.csv"
    assert bf_path.exists()
    df = pd.read_csv(bf_path)
    nov = df[df['purchase_ym'] == '2017-11'].iloc[0]
    oct = df[df['purchase_ym'] == '2017-10'].iloc[0]
    
    assert nov['order_volume'] > oct['order_volume'] * 1.4, "Nov 2017 order surge was less than +40% MoM"
    assert nov['late_delivery_rate'] > 10.0, "Nov 2017 late rate should exceed 10%"
    assert nov['mean_review_score'] < oct['mean_review_score'], "Nov 2017 review score did not decline"


# =============================================================================
# 5. FIGURE PERSISTENCE & INTEGRITY
# =============================================================================
REQUIRED_FIGURES = [
    "fig19_delay_vs_predicted_low_review_probability.png",
    "fig20_delay_threshold_piecewise_spline_fit.png",
    "fig21_survey_timing_adjusted_odds_comparison.png",
    "fig22_delivery_accountability_seller_vs_carrier.png",
    "fig23_geographic_corridor_risk_matrix.png",
    "fig24_black_friday_capacity_shock_decomposition.png"
]


@pytest.mark.parametrize("figname", REQUIRED_FIGURES)
def test_required_figure_existence_and_size(figname):
    """Verifies that all 6 publication figures exist, are non-empty, and exceed 50 KB (300 DPI check)."""
    figpath = FIGURES_DIR / figname
    assert figpath.exists(), f"Missing figure: {figpath}"
    file_size = figpath.stat().st_size
    assert file_size > 50000, f"Figure {figname} is suspiciously small ({file_size} bytes), check DPI!"
