"""
test_module3_eda.py — Automated Verification Suite for Module 3 EDA
Project: Gradient Learnings Data Analytics Hackathon 2026 (Olist)
Module: 3 — Exploratory Data Analysis (EDA)

Verifies all 11 output CSV tables, all 18 visualization artifacts,
KPI baseline invariants, monotonic delivery delay inflections,
the survey trigger mechanism, and notebook structural integrity.
"""

import os
import json
import pytest
import pandas as pd
import numpy as np

# Base paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLES_DIR = os.path.join(PROJECT_ROOT, 'outputs', 'tables')
FIGURES_DIR = os.path.join(PROJECT_ROOT, 'outputs', 'figures')
NOTEBOOKS_DIR = os.path.join(PROJECT_ROOT, 'notebooks')


# ==============================================================================
# 1. TABLE PRESENCE & SCHEMA TESTS
# ==============================================================================

REQUIRED_TABLES = [
    'eda_kpi_baseline.csv',
    'eda_time_series.csv',
    'eda_delivery_distribution.csv',
    'eda_review_distribution.csv',
    'eda_category_summary.csv',
    'eda_seller_summary.csv',
    'eda_geography_summary.csv',
    'eda_payment_summary.csv',
    'eda_interaction_candidates.csv',
    'eda_anomaly_register.csv',
    'eda_finding_register.csv'
]

@pytest.mark.parametrize('table_name', REQUIRED_TABLES)
def test_eda_table_exists_and_non_empty(table_name):
    """Confirm all 11 required EDA CSV tables exist and contain records."""
    path = os.path.join(TABLES_DIR, table_name)
    assert os.path.exists(path), f"Missing required table: {path}"
    df = pd.read_csv(path)
    assert len(df) > 0, f"Table {table_name} is empty!"


# ==============================================================================
# 2. FIGURE PRESENCE & SIZE TESTS (18 CORE VISUALS)
# ==============================================================================

REQUIRED_FIGURES = [
    'fig01_monthly_marketplace_growth_divergence.png',
    'fig02_order_status_composition.png',
    'fig03_seller_concentration_pareto.png',
    'fig04_category_volume_vs_revenue_share.png',
    'fig05_delivery_duration_distribution.png',
    'fig06_delivery_delay_distribution_and_buffer.png',
    'fig07_review_score_distribution_polarization.png',
    'fig08_review_score_by_delay_bucket.png',
    'fig09_survey_trigger_pre_vs_post_delivery.png',
    'fig10_payment_type_share_and_aov.png',
    'fig11_installments_vs_ticket_value.png',
    'fig12_geographic_flow_seller_to_customer_states.png',
    'fig13_haversine_distance_vs_delivery_duration.png',
    'fig14_regional_corridor_delay_heatmap.png',
    'fig15_category_delay_vs_review_sensitivity.png',
    'fig16_freight_share_vs_satisfaction.png',
    'fig17_repeat_vs_onetime_customer_experience.png',
    'fig18_executive_exploratory_dashboard.png'
]

@pytest.mark.parametrize('fig_name', REQUIRED_FIGURES)
def test_eda_figure_exists_and_valid_size(fig_name):
    """Confirm all 18 publication-grade visualization PNGs exist and exceed 50 KB."""
    path = os.path.join(FIGURES_DIR, fig_name)
    assert os.path.exists(path), f"Missing required figure: {path}"
    file_size = os.path.getsize(path)
    assert file_size > 50_000, f"Figure {fig_name} is abnormally small ({file_size} bytes)!"


# ==============================================================================
# 3. KPI BASELINE INVARIANT TESTS
# ==============================================================================

@pytest.fixture(scope='module')
def kpi_dict():
    path = os.path.join(TABLES_DIR, 'eda_kpi_baseline.csv')
    df = pd.read_csv(path)
    return dict(zip(df['kpi_name'], df['value']))

def test_kpi_order_volume_invariants(kpi_dict):
    """Verify order volume baseline invariants."""
    assert kpi_dict['Total Orders'] == '99,441'
    assert kpi_dict['Delivered Orders'] == '96,478'
    assert kpi_dict['Non-Delivered Orders'] == '2,963'
    assert kpi_dict['Delivered Rate'] == '97.02%'

def test_kpi_financial_invariants(kpi_dict):
    """Verify GMV vs settlement reconciliation values."""
    assert '15,843,553.24' in kpi_dict['Total GMV (Price + Freight)']
    assert '16,008,872.12' in kpi_dict['Total Settlement Value']
    assert '160.58' in kpi_dict['Average Order Value (AOV)']

def test_kpi_sentiment_and_retention(kpi_dict):
    """Verify review sentiment and repeat customer benchmarks."""
    assert float(kpi_dict['Average Review Score']) >= 4.08
    assert '3.12%' in kpi_dict['Repeat Customer Rate (Unique Cust)']
    assert '6.38%' in kpi_dict['Repeat Customer Order Share']


# ==============================================================================
# 4. DELIVERY DELAY NON-LINEAR INFLECTION TESTS
# ==============================================================================

def test_delivery_delay_monotonic_degradation():
    """Verify that average review score monotonically degrades across delay buckets."""
    path = os.path.join(TABLES_DIR, 'eda_delivery_distribution.csv')
    df = pd.read_csv(path)
    scores = df['mean_review_score'].tolist()
    low_rates = df['low_review_rate_pct'].tolist()
    
    # Assert strict monotonic decrease of review scores across delay buckets
    assert scores[0] > scores[1] > scores[2] > scores[3] > scores[4]
    
    # Assert on-time is high (> 4.1 stars)
    assert scores[0] > 4.2
    assert scores[1] > 4.1
    
    # Assert severe collapse on moderate (4-7d) and severe (>7d) delay
    assert scores[3] < 2.5
    assert scores[4] < 2.0
    
    # Assert strict monotonic increase in low-review rate from early to severe delay
    assert low_rates[0] < low_rates[1] < low_rates[2] < low_rates[3] < low_rates[4]
    assert low_rates[4] > 75.0  # >75% negative reviews for severe delays (>7d)


# ==============================================================================
# 5. THE SURVEY TRIGGER DEFECT TEST (SIGNATURE FINDING)
# ==============================================================================

def test_survey_trigger_defect_quantification():
    """Verify the empirical quantification of the survey trigger mechanism."""
    path = os.path.join(TABLES_DIR, 'eda_review_distribution.csv')
    df = pd.read_csv(path)
    
    post_deliv = df[df['timing_segment'].str.contains('Survey >= Delivered')].iloc[0]
    overdue_in_transit = df[df['timing_segment'].str.contains('Estimate Elapsed')].iloc[0]
    
    # Normal post-delivery reviews average > 4.2 stars with < 11% low reviews
    assert post_deliv['mean_review_score'] > 4.2
    assert post_deliv['low_review_rate_pct'] < 11.0
    
    # In-transit overdue surveys collapse to < 2.2 stars with > 65% low reviews
    assert overdue_in_transit['mean_review_score'] < 2.2
    assert overdue_in_transit['low_review_rate_pct'] > 65.0
    assert overdue_in_transit['order_count'] > 5000  # Exactly 5,335 orders


# ==============================================================================
# 6. GEOGRAPHY & CORRIDOR CONCENTRATION TESTS
# ==============================================================================

def test_geography_sao_paulo_hegemony():
    """Verify São Paulo's supply dominance across Brazil."""
    path = os.path.join(TABLES_DIR, 'eda_geography_summary.csv')
    df = pd.read_csv(path)
    sp_row = df[df['customer_state'] == 'SP'].iloc[0]
    
    # SP represents over 40% of customer orders
    assert sp_row['order_share_pct'] > 40.0
    assert sp_row['order_count'] > 40_000
    
    # SP has faster delivery (< 10 days) and lower delay rate (< 7%)
    assert sp_row['mean_delivery_duration'] < 10.0
    assert sp_row['late_delivery_rate_pct'] < 7.0


# ==============================================================================
# 7. NOTEBOOK STRUCTURAL INTEGRITY
# ==============================================================================

def test_eda_notebook_structural_integrity():
    """Verify that notebooks/03_exploratory_data_analysis.ipynb exists and is valid nbformat v4."""
    path = os.path.join(NOTEBOOKS_DIR, '03_exploratory_data_analysis.ipynb')
    assert os.path.exists(path), f"Missing notebook: {path}"
    
    with open(path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
        
    assert nb['nbformat'] == 4
    assert len(nb['cells']) >= 40
    
    # Verify presence of code and markdown cells
    code_cells = [c for c in nb['cells'] if c['cell_type'] == 'code']
    md_cells = [c for c in nb['cells'] if c['cell_type'] == 'markdown']
    assert len(code_cells) >= 12
    assert len(md_cells) >= 20
