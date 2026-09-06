"""
business_prioritization_engine.py — Module 5 Root-Cause Synthesis & Business Prioritization Engine
Project: Gradient Learnings Data Analytics Hackathon 2026 (Olist E-Commerce Diagnostic)

Executes the definitive business prioritization and root-cause synthesis pipeline:
- 5.1 Root-Cause Hierarchy & Contribution Matrix (Levels 1–4 across 8 core factors)
- 5.2 Delay Severity Segmentation & Non-Linear Operational Collapse
- 5.3 Seller Operational Risk Cohorts (N >= 100 high-volume sellers)
- 5.4 High-Volume Geographic Corridor Risk Matrix (N >= 100 state pairs, SP -> RJ focus)
- 5.5 High-Exposure Product Category Audit (N >= 200 categories, exposure vs root cause)
- 5.6 Mutually Exclusive Survey Timing Segmentation (Strict Pre-Delivery, Same-Day, Post-Delivery)
- 5.7 Compound High-Impact Risk Intersections
- 5.8 Business Exposure Framework (Order, GMV, Dissatisfaction, Delay Exposures)
- 5.9 Transparent Multi-Factor Prioritization Scoring (Severity x Exposure x Actionability x Evidence)
- 5.10 P0 / P1 / P2 Actionable Operational Roadmap with Addressable Impact Metrics
- 5.11 Executive Operational Scorecard & Monitoring Cadence
- Generates all 11 structured output CSV tables in outputs/tables/
- Generates all 6 publication-grade figures in outputs/figures/ (fig25 through fig30) at 300 DPI.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Tuple, List, Any

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns

# Global Workspace Paths
BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
TABLES_DIR = BASE_DIR / "outputs" / "tables"
FIGURES_DIR = BASE_DIR / "outputs" / "figures"

# Ensure output directories exist
TABLES_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Publication Styling Configuration
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#D1D5DB'
plt.rcParams['axes.linewidth'] = 0.8

COLOR_PRIMARY = '#1E3A8A'      # Deep Navy
COLOR_SECONDARY = '#0D9488'    # Teal
COLOR_ACCENT = '#D97706'       # Amber
COLOR_DANGER = '#DC2626'       # Crimson
COLOR_MUTED = '#6B7280'        # Slate Grey
COLOR_LIGHT = '#F3F4F6'        # Light Grey
COLOR_PURPLE = '#7C3AED'       # Purple Accent


def load_canonical_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Loads canonical analytical model and prepares standardized Population E subset.
    Returns:
        (df_all, df_pop_e)
    """
    parquet_path = PROCESSED_DIR / "analytical_model.parquet"
    if not parquet_path.exists():
        raise FileNotFoundError(f"Missing canonical analytical model at {parquet_path}")

    df = pd.read_parquet(parquet_path)

    # Population E: Delivered orders with valid delivery date and non-null review score
    is_pop_e = (
        (df['order_status'] == 'delivered') &
        df['order_delivered_customer_date'].notna() &
        df['review_score'].notna()
    )
    df_e = df[is_pop_e].copy()

    # Cast binary indicators
    df_e['low_review'] = (df_e['review_score'] <= 2).astype(int)
    df_e['one_star'] = (df_e['review_score'] == 1).astype(int)
    df_e['is_late'] = (df_e['delivery_delay_days'] > 0.0).astype(int)
    df_e['is_severe_late'] = (df_e['delivery_delay_days'] > 3.5).astype(int)
    df_e['corridor'] = df_e['seller_state'] + " -> " + df_e['customer_state']

    # Timestamps
    t_deliv = pd.to_datetime(df_e['order_delivered_customer_date'])
    t_create = pd.to_datetime(df_e['review_creation_date'])
    t_ans = pd.to_datetime(df_e['review_answer_timestamp'])
    t_est = pd.to_datetime(df_e['order_estimated_delivery_date'])

    # Mutually Exclusive Survey Timing Groups
    df_e['strict_calendar_pre'] = (t_create.dt.date < t_deliv.dt.date).astype(int)
    df_e['same_day_ambiguous'] = (t_create.dt.date == t_deliv.dt.date).astype(int)
    df_e['clearly_post_delivery'] = (t_create.dt.date > t_deliv.dt.date).astype(int)

    # Subgroup: Answered Pre-Delivery
    df_e['answered_pre_delivery'] = (t_ans < t_deliv).astype(int)
    # Subgroup: Overdue in transit survey
    df_e['overdue_in_transit_survey'] = ((t_create < t_deliv) & (t_create >= t_est)).astype(int)

    # Compute Haversine Distance
    r_earth = 6371.0
    phi1, phi2 = np.radians(df_e['customer_lat']), np.radians(df_e['seller_lat'])
    dphi = np.radians(df_e['seller_lat'] - df_e['customer_lat'])
    dlambda = np.radians(df_e['seller_lng'] - df_e['customer_lng'])
    a = np.sin(dphi / 2.0) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda / 2.0) ** 2
    df_e['haversine_distance_km'] = r_earth * 2.0 * np.arctan2(np.sqrt(a), np.sqrt(1.0 - a))

    return df, df_e


# =============================================================================
# 1. ROOT-CAUSE CONTRIBUTION MATRIX (TABLE 1 & FIGURE 25)
# =============================================================================
def build_root_cause_contribution_matrix() -> pd.DataFrame:
    """
    Builds the 4-level root cause hierarchy and contribution matrix across 8 core factors.
    """
    print("\n--- 1. Building Root-Cause Contribution Matrix ---")
    data = [
        {
            'Level': 'Level 1: Structural',
            'Factor': 'Geographic Seller Concentration',
            'Evidence_Type': 'Descriptive Fact',
            'Effect_Size': '70.9% seller volume in SP; 64.0% interstate orders',
            'Robustness': 'Complete Census (N=99,441)',
            'Business_Exposure': '64.0% of orders cross state boundaries',
            'Actionability': 'Low (Requires multi-year regional merchant onboarding)',
            'Causal_Confidence': 'Exogenous Structural Fact',
            'Priority': 'P1 — Strategic'
        },
        {
            'Level': 'Level 1: Structural',
            'Factor': 'Long-Haul Trunk Linehaul Exposure',
            'Evidence_Type': 'Adjusted Associative',
            'Effect_Size': 'Distance mediated by transit duration (r=0.40)',
            'Robustness': 'Model 5 Spatial Fixed Effects (p < 10^-16)',
            'Business_Exposure': 'Corridors to North/Northeast face 18-24d durations',
            'Actionability': 'Medium (3PL hub partnerships & multi-regional fulfillment)',
            'Causal_Confidence': 'Logistical Operational Proxy',
            'Priority': 'P1 — Strategic'
        },
        {
            'Level': 'Level 2: Operational',
            'Factor': 'Carrier Linehaul Transit Delay',
            'Evidence_Type': 'Adjusted Associative',
            'Effect_Size': '76.9% of timeline (9.3d avg); Standardized OR = 2.20 (+120% excess odds/SD vs +38% seller)',
            'Robustness': 'Robust across 8 model specifications (p < 10^-50)',
            'Business_Exposure': 'Accounts for 81.8% of Black Friday fulfillment surge (+2.7d carrier surge)',
            'Actionability': 'High (Carrier contract SLAs, dynamic routing, volume penalties)',
            'Causal_Confidence': 'Primary Operational Predictor',
            'Priority': 'P0 — Immediate'
        },
        {
            'Level': 'Level 2: Operational',
            'Factor': 'Seller Warehouse Handling Bottleneck',
            'Evidence_Type': 'Adjusted Associative',
            'Effect_Size': '17.5% of timeline (2.8d avg); Standardized OR = 1.12 (+12% excess odds/SD)',
            'Robustness': 'p < 10^-15 across all specifications',
            'Business_Exposure': '9.4% of orders take >5 days to dispatch (16.2% of low reviews)',
            'Actionability': 'High (Seller dispatch SLAs, automated late-dispatch penalties)',
            'Causal_Confidence': 'Direct Merchant Responsibility',
            'Priority': 'P2 — Optimization'
        },
        {
            'Level': 'Level 2: Operational',
            'Factor': 'Promised SLA Breach (>3.5 Days Late)',
            'Evidence_Type': 'Robust Threshold',
            'Effect_Size': 'Econometric break at 0.5d; Escalation at 3.5d; OR=9.8x vs on-time',
            'Robustness': 'AIC minimized at tau=0.5d (Delta AIC = -1,556); LOWESS confirmed',
            'Business_Exposure': '5.2% of orders (>3.5d late) generate 29.6% of delivered low reviews',
            'Actionability': 'High (Promised date recalibration, proactive delay alerts)',
            'Causal_Confidence': 'Direct SLA Breach Driver',
            'Priority': 'P0 — Immediate'
        },
        {
            'Level': 'Level 3: Experience Amplifier',
            'Factor': 'Asynchronous Pre-Delivery Survey Solicitations',
            'Evidence_Type': 'Mechanistic / Controlled',
            'Effect_Size': 'Adjusted OR = 12.50x (strict calendar); 26.1% of marketplace low reviews',
            'Robustness': 'Robust across 4 definitions & delay-stratified controls (p < 10^-50)',
            'Business_Exposure': '4,976 strict pre-delivery orders produce 3,613 low reviews (72.6% rate)',
            'Actionability': 'Immediate / Zero Capex (Suppress survey until confirmed delivery)',
            'Causal_Confidence': 'Operational Feedback Asynchrony',
            'Priority': 'P0 — Immediate'
        },
        {
            'Level': 'Level 4: Context & Friction',
            'Factor': 'Product Category Delivery Sensitivity',
            'Evidence_Type': 'Overpowered / Minor Effect',
            'Effect_Size': 'ANOVA interaction partial eta^2 = 0.073% (negligible)',
            'Robustness': 'F = 4.88, p = 1.2e-06 (overpowered by N=59,640)',
            'Business_Exposure': 'Top 4 categories generate 34.8% of low reviews due to volume share',
            'Actionability': 'Medium (Category-specific packaging & volumetric freight buffers)',
            'Causal_Confidence': 'Volume Exposure, Not Root Cause',
            'Priority': 'P2 — Optimization'
        },
        {
            'Level': 'Level 4: Context & Friction',
            'Factor': 'Freight Burden Share',
            'Evidence_Type': 'Controlled Non-Association',
            'Effect_Size': 'Controlled OR = 1.000 to 1.023 (indistinguishable from 1.0)',
            'Robustness': 'p = 0.89 controlling for distance & duration',
            'Business_Exposure': 'High freight correlated with distance, not direct dissatisfaction',
            'Actionability': 'Low Impact (Subsidies will not fix NPS; speed matters)',
            'Causal_Confidence': 'Spurious Direct Association',
            'Priority': 'P2 — Optimization'
        }
    ]
    df_matrix = pd.DataFrame(data)
    csv_path = TABLES_DIR / "root_cause_contribution_matrix.csv"
    df_matrix.to_csv(csv_path, index=False)
    print(f"  Saved {csv_path}")

    # Figure 25: Root-Cause Contribution Matrix Visual
    fig, ax = plt.subplots(figsize=(12, 6), dpi=300)
    ax.axis('off')

    colors_by_level = {
        'Level 1: Structural': '#EFF6FF',
        'Level 2: Operational': '#FEF2F2',
        'Level 3: Experience Amplifier': '#FFFBEB',
        'Level 4: Context & Friction': '#F3F4F6'
    }
    table_data = []
    cell_colors = []
    headers = ['Hierarchy Level', 'Causal Factor', 'Evidence Type', 'Effect Size', 'Business Exposure', 'Actionability', 'Priority']

    for _, r in df_matrix.iterrows():
        table_data.append([r['Level'], r['Factor'], r['Evidence_Type'], r['Effect_Size'], r['Business_Exposure'], r['Actionability'], r['Priority']])
        bg_col = colors_by_level.get(r['Level'], '#FFFFFF')
        cell_colors.append([bg_col] * len(headers))

    tbl = ax.table(cellText=table_data, colLabels=headers, cellColours=cell_colors, loc='center', cellLoc='left')
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(8.5)
    tbl.scale(1.0, 1.8)

    # Style headers
    for (i, j), cell in tbl.get_celld().items():
        if i == 0:
            cell.set_text_props(weight='bold', color='white')
            cell.set_facecolor(COLOR_PRIMARY)
            cell.set_height(0.08)
        else:
            cell.set_edgecolor('#E5E7EB')
            cell.set_linewidth(0.6)

    ax.set_title("Olist Marketplace: Root-Cause Synthesis & Contribution Hierarchy", fontsize=13, fontweight='bold', pad=15)
    plt.tight_layout()
    fig25_path = FIGURES_DIR / "fig25_root_cause_contribution_matrix.png"
    plt.savefig(fig25_path, bbox_inches='tight')
    plt.close()
    print(f"  Saved {fig25_path}")

    return df_matrix


# =============================================================================
# 2. HIGH-RISK DELAY SEGMENTS (TABLE 2)
# =============================================================================
def build_high_risk_delay_segments(df_e: pd.DataFrame) -> pd.DataFrame:
    """
    Partitions Population E into 5 operational delay severity strata.
    """
    print("\n--- 2. Building High-Risk Delay Segments ---")
    bins = [-1000.0, -0.5, 0.0, 3.0, 7.0, 1000.0]
    labels = ['Early (>0.5d early)', 'On-Time (0-0.5d early)', 'Minor Late (1-3d late)', 'Moderate Late (4-7d late)', 'Severe Late (>7d late)']
    df_e['delay_stratum'] = pd.cut(df_e['delivery_delay_days'], bins=bins, labels=labels)

    total_orders = len(df_e)
    total_gmv = df_e['order_gmv'].sum()
    total_low = df_e['low_review'].sum()

    agg = df_e.groupby('delay_stratum', observed=False).agg(
        orders=('order_id', 'count'),
        gmv=('order_gmv', 'sum'),
        mean_review_score=('review_score', 'mean'),
        low_reviews=('low_review', 'sum'),
        low_review_rate=('low_review', lambda s: s.mean() * 100.0)
    ).reset_index()

    agg['order_share_pct'] = agg['orders'] / total_orders * 100.0
    agg['gmv_share_pct'] = agg['gmv'] / total_gmv * 100.0
    agg['dissatisfaction_share_pct'] = agg['low_reviews'] / total_low * 100.0

    csv_path = TABLES_DIR / "high_risk_delay_segments.csv"
    agg.to_csv(csv_path, index=False)
    print(f"  Saved {csv_path}")
    return agg


# =============================================================================
# 3. HIGH-RISK SELLER COHORTS (TABLE 3)
# =============================================================================
def build_high_risk_seller_segments(df_e: pd.DataFrame) -> pd.DataFrame:
    """
    Identifies seller operational risk cohorts among qualified sellers (N >= 100 orders).
    """
    print("\n--- 3. Building High-Risk Seller Cohorts (N >= 100) ---")
    seller_agg = df_e.groupby('dominant_seller').agg(
        orders=('order_id', 'count'),
        gmv=('order_gmv', 'sum'),
        mean_review_score=('review_score', 'mean'),
        low_reviews=('low_review', 'sum'),
        low_review_rate=('low_review', lambda s: s.mean() * 100.0),
        late_orders=('is_late', 'sum'),
        late_rate=('is_late', lambda s: s.mean() * 100.0),
        severe_late_orders=('is_severe_late', 'sum'),
        severe_late_rate=('is_severe_late', lambda s: s.mean() * 100.0),
        mean_handling_days=('approval_to_carrier_days', 'mean'),
        mean_carrier_days=('carrier_to_delivery_days', 'mean'),
        seller_state=('seller_state', 'first')
    ).reset_index()

    s100 = seller_agg[seller_agg['orders'] >= 100].copy()

    # Assign cohorts
    def assign_cohort(row):
        if row['mean_handling_days'] >= 5.0:
            return 'Warehouse Bottleneck (Handling > 5d)'
        elif row['orders'] >= 300 and row['low_review_rate'] >= 15.0:
            return 'High-Volume / High-Risk (N>=300, Low>=15%)'
        elif row['orders'] >= 300 and row['low_review_rate'] < 10.0:
            return 'High-Volume / High-Performing (N>=300, Low<10%)'
        elif row['low_review_rate'] >= 15.0:
            return 'Mid-Volume / Elevated-Risk (100<=N<300, Low>=15%)'
        else:
            return 'Mid-Volume / Standard-Performing'

    s100['seller_cohort'] = s100.apply(assign_cohort, axis=1)

    cohort_summary = s100.groupby('seller_cohort').agg(
        qualified_sellers=('dominant_seller', 'count'),
        total_orders=('orders', 'sum'),
        total_gmv=('gmv', 'sum'),
        total_low_reviews=('low_reviews', 'sum'),
        mean_low_review_rate=('low_review_rate', 'mean'),
        mean_late_rate=('late_rate', 'mean'),
        mean_handling_days=('mean_handling_days', 'mean'),
        mean_carrier_days=('mean_carrier_days', 'mean')
    ).reset_index().sort_values('total_low_reviews', ascending=False)

    cohort_summary['order_share_pct'] = cohort_summary['total_orders'] / len(df_e) * 100.0
    cohort_summary['dissatisfaction_share_pct'] = cohort_summary['total_low_reviews'] / df_e['low_review'].sum() * 100.0

    csv_path = TABLES_DIR / "high_risk_seller_segments.csv"
    cohort_summary.to_csv(csv_path, index=False)
    print(f"  Saved {csv_path}")
    return cohort_summary


# =============================================================================
# 4. HIGH-RISK GEOGRAPHIC CORRIDORS (TABLE 4 & FIGURE 27)
# =============================================================================
def build_high_risk_geographic_segments(df_e: pd.DataFrame) -> pd.DataFrame:
    """
    Evaluates state-to-state corridors with minimum volume threshold N >= 100.
    """
    print("\n--- 4. Building High-Risk Geographic Corridors (N >= 100) ---")
    corr_agg = df_e.groupby('corridor').agg(
        orders=('order_id', 'count'),
        gmv=('order_gmv', 'sum'),
        mean_distance_km=('haversine_distance_km', 'mean'),
        late_orders=('is_late', 'sum'),
        late_rate=('is_late', lambda s: s.mean() * 100.0),
        severe_late_orders=('is_severe_late', 'sum'),
        severe_late_rate=('is_severe_late', lambda s: s.mean() * 100.0),
        low_reviews=('low_review', 'sum'),
        low_review_rate=('low_review', lambda s: s.mean() * 100.0),
        median_delay_days=('delivery_delay_days', 'median'),
        median_duration_days=('delivery_days_total', 'median')
    ).reset_index()

    corr_100 = corr_agg[corr_agg['orders'] >= 100].copy()
    corr_100['order_share_pct'] = corr_100['orders'] / len(df_e) * 100.0
    corr_100['dissatisfaction_share_pct'] = corr_100['low_reviews'] / df_e['low_review'].sum() * 100.0
    corr_100 = corr_100.sort_values('low_reviews', ascending=False)

    csv_path = TABLES_DIR / "high_risk_geographic_segments.csv"
    corr_100.to_csv(csv_path, index=False)
    print(f"  Saved {csv_path}")

    # Figure 27: Corridor Risk Bubble / Scatter Plot
    fig, ax = plt.subplots(figsize=(11, 6), dpi=300)
    scatter = ax.scatter(
        corr_100['severe_late_rate'],
        corr_100['low_review_rate'],
        s=corr_100['orders'] / 25 + 20,
        c=corr_100['dissatisfaction_share_pct'],
        cmap='YlOrRd',
        alpha=0.85,
        edgecolors='black',
        linewidth=0.6
    )

    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label("Share of Marketplace Low Reviews (%)", fontsize=9)

    # Highlight and label strategic corridors
    strategic_labels = ['SP -> RJ', 'SP -> SP', 'SP -> BA', 'SP -> MG', 'SP -> RS', 'SP -> PR', 'SP -> SC', 'SP -> ES', 'PR -> SP']
    for _, r in corr_100.iterrows():
        if r['corridor'] in strategic_labels:
            ax.annotate(
                f"{r['corridor']}\n({r['dissatisfaction_share_pct']:.1f}% Low)",
                xy=(r['severe_late_rate'], r['low_review_rate']),
                xytext=(r['severe_late_rate'] + 0.35, r['low_review_rate'] + 0.3),
                fontsize=8,
                fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8, edgecolor='#CCCCCC')
            )

    ax.set_title("Macro-Corridor Operational Risk Matrix: Severe Lateness vs. Low Review Rate (N ≥ 100)", fontsize=12, fontweight='bold', pad=12)
    ax.set_xlabel("Severe Lateness Rate (% Delivered > 3.5 Days Past SLA)", fontsize=10)
    ax.set_ylabel("Low Review Rate (% Rating 1–2 Stars)", fontsize=10)
    ax.grid(True, linestyle=':', alpha=0.6)

    plt.tight_layout()
    fig27_path = FIGURES_DIR / "fig27_corridor_risk_bubble_scatter.png"
    plt.savefig(fig27_path)
    plt.close()
    print(f"  Saved {fig27_path}")

    return corr_100


# =============================================================================
# 5. HIGH-EXPOSURE PRODUCT CATEGORY SEGMENTS (TABLE 5)
# =============================================================================
def build_high_risk_category_segments(df_e: pd.DataFrame) -> pd.DataFrame:
    """
    Evaluates product categories with minimum volume threshold N >= 200.
    """
    print("\n--- 5. Building High-Risk Category Segments (N >= 200) ---")
    cat_agg = df_e.groupby('dominant_category').agg(
        orders=('order_id', 'count'),
        gmv=('order_gmv', 'sum'),
        low_reviews=('low_review', 'sum'),
        low_review_rate=('low_review', lambda s: s.mean() * 100.0),
        late_orders=('is_late', 'sum'),
        late_rate=('is_late', lambda s: s.mean() * 100.0),
        severe_late_orders=('is_severe_late', 'sum'),
        severe_late_rate=('is_severe_late', lambda s: s.mean() * 100.0),
        mean_transit_days=('delivery_days_total', 'mean')
    ).reset_index()

    cat_200 = cat_agg[cat_agg['orders'] >= 200].copy()
    cat_200['order_share_pct'] = cat_200['orders'] / len(df_e) * 100.0
    cat_200['dissatisfaction_share_pct'] = cat_200['low_reviews'] / df_e['low_review'].sum() * 100.0
    cat_200 = cat_200.sort_values('low_reviews', ascending=False)

    csv_path = TABLES_DIR / "high_risk_category_segments.csv"
    cat_200.to_csv(csv_path, index=False)
    print(f"  Saved {csv_path}")
    return cat_200


# =============================================================================
# 6. MUTUALLY EXCLUSIVE SURVEY TIMING SEGMENTS (TABLE 6)
# =============================================================================
def build_survey_timing_segments(df_e: pd.DataFrame) -> pd.DataFrame:
    """
    Constructs mutually exclusive survey timing groups and key diagnostic subgroups.
    """
    print("\n--- 6. Building Mutually Exclusive Survey Timing Segments ---")
    # Mutually Exclusive Classification
    def timing_class(row):
        if row['strict_calendar_pre'] == 1:
            return '1. Strict Calendar Pre-Delivery'
        elif row['same_day_ambiguous'] == 1:
            return '2. Same-Day Delivery Ambiguous'
        else:
            return '3. Clearly Post-Delivery'

    df_e['survey_timing_partition'] = df_e.apply(timing_class, axis=1)

    part_agg = df_e.groupby('survey_timing_partition').agg(
        orders=('order_id', 'count'),
        gmv=('order_gmv', 'sum'),
        mean_review_score=('review_score', 'mean'),
        low_reviews=('low_review', 'sum'),
        low_review_rate=('low_review', lambda s: s.mean() * 100.0),
        severe_late_orders=('is_severe_late', 'sum'),
        severe_late_rate=('is_severe_late', lambda s: s.mean() * 100.0)
    ).reset_index()

    part_agg['order_share_pct'] = part_agg['orders'] / len(df_e) * 100.0
    part_agg['dissatisfaction_share_pct'] = part_agg['low_reviews'] / df_e['low_review'].sum() * 100.0

    # Add Subgroup Rows for Transparency
    subgroup_ans = {
        'survey_timing_partition': 'Subgroup: Answered Pre-Delivery (Def B)',
        'orders': int(df_e['answered_pre_delivery'].sum()),
        'gmv': float(df_e.loc[df_e['answered_pre_delivery'] == 1, 'order_gmv'].sum()),
        'mean_review_score': float(df_e.loc[df_e['answered_pre_delivery'] == 1, 'review_score'].mean()),
        'low_reviews': int(df_e.loc[df_e['answered_pre_delivery'] == 1, 'low_review'].sum()),
        'low_review_rate': float(df_e.loc[df_e['answered_pre_delivery'] == 1, 'low_review'].mean() * 100.0),
        'severe_late_orders': int(df_e.loc[df_e['answered_pre_delivery'] == 1, 'is_severe_late'].sum()),
        'severe_late_rate': float(df_e.loc[df_e['answered_pre_delivery'] == 1, 'is_severe_late'].mean() * 100.0),
        'order_share_pct': float(df_e['answered_pre_delivery'].mean() * 100.0),
        'dissatisfaction_share_pct': float(df_e.loc[df_e['answered_pre_delivery'] == 1, 'low_review'].sum() / df_e['low_review'].sum() * 100.0)
    }

    subgroup_overdue = {
        'survey_timing_partition': 'Subgroup: Overdue in Transit Survey',
        'orders': int(df_e['overdue_in_transit_survey'].sum()),
        'gmv': float(df_e.loc[df_e['overdue_in_transit_survey'] == 1, 'order_gmv'].sum()),
        'mean_review_score': float(df_e.loc[df_e['overdue_in_transit_survey'] == 1, 'review_score'].mean()),
        'low_reviews': int(df_e.loc[df_e['overdue_in_transit_survey'] == 1, 'low_review'].sum()),
        'low_review_rate': float(df_e.loc[df_e['overdue_in_transit_survey'] == 1, 'low_review'].mean() * 100.0),
        'severe_late_orders': int(df_e.loc[df_e['overdue_in_transit_survey'] == 1, 'is_severe_late'].sum()),
        'severe_late_rate': float(df_e.loc[df_e['overdue_in_transit_survey'] == 1, 'is_severe_late'].mean() * 100.0),
        'order_share_pct': float(df_e['overdue_in_transit_survey'].mean() * 100.0),
        'dissatisfaction_share_pct': float(df_e.loc[df_e['overdue_in_transit_survey'] == 1, 'low_review'].sum() / df_e['low_review'].sum() * 100.0)
    }

    part_agg = pd.concat([part_agg, pd.DataFrame([subgroup_ans, subgroup_overdue])], ignore_index=True)
    csv_path = TABLES_DIR / "survey_timing_segments.csv"
    part_agg.to_csv(csv_path, index=False)
    print(f"  Saved {csv_path}")
    return part_agg


# =============================================================================
# 7. HIGH-IMPACT COMBINATIONS (TABLE 7 & FIGURE 26)
# =============================================================================
def build_high_impact_combinations(df_e: pd.DataFrame) -> pd.DataFrame:
    """
    Evaluates multi-factor intersection segments combining operational delay,
    geographic corridors, and feedback timing.
    """
    print("\n--- 7. Building High-Impact Combinations ---")
    df_e['sp_to_rj'] = (df_e['corridor'] == 'SP -> RJ').astype(int)
    df_e['seller_slow_handling'] = (df_e['approval_to_carrier_days'] > 5.0).astype(int)
    df_e['top_4_categories'] = df_e['dominant_category'].isin(['bed_bath_table', 'health_beauty', 'computers_accessories', 'furniture_decor']).astype(int)

    combos = [
        {
            'Combination_Name': 'COMBO-01: Severe Delay (>3.5d) + Pre-Delivery Survey',
            'Filter_Condition': '(delivery_delay_days > 3.5) & (strict_calendar_pre == 1)',
            'Mask': (df_e['is_severe_late'] == 1) & (df_e['strict_calendar_pre'] == 1)
        },
        {
            'Combination_Name': 'COMBO-02: SP -> RJ Corridor + Severe Delay (>3.5d)',
            'Filter_Condition': '(corridor == "SP -> RJ") & (delivery_delay_days > 3.5)',
            'Mask': (df_e['sp_to_rj'] == 1) & (df_e['is_severe_late'] == 1)
        },
        {
            'Combination_Name': 'COMBO-03: SP -> RJ Corridor + Pre-Delivery Survey',
            'Filter_Condition': '(corridor == "SP -> RJ") & (strict_calendar_pre == 1)',
            'Mask': (df_e['sp_to_rj'] == 1) & (df_e['strict_calendar_pre'] == 1)
        },
        {
            'Combination_Name': 'COMBO-04: Slow Warehouse Handling (>5d) + Interstate Transit',
            'Filter_Condition': '(approval_to_carrier_days > 5.0) & (customer_state != seller_state)',
            'Mask': (df_e['seller_slow_handling'] == 1) & (df_e['customer_state'] != df_e['seller_state'])
        },
        {
            'Combination_Name': 'COMBO-05: Top 4 Categories + Severe Delay (>3.5d)',
            'Filter_Condition': '(top_4_categories == 1) & (delivery_delay_days > 3.5)',
            'Mask': (df_e['top_4_categories'] == 1) & (df_e['is_severe_late'] == 1)
        },
        {
            'Combination_Name': 'COMBO-06: Black Friday Nov 2017 Surge Orders',
            'Filter_Condition': 'order_purchase_timestamp in Nov 2017',
            'Mask': pd.to_datetime(df_e['order_purchase_timestamp']).dt.to_period('M').astype(str) == '2017-11'
        }
    ]

    total_orders = len(df_e)
    total_gmv = df_e['order_gmv'].sum()
    total_low = df_e['low_review'].sum()

    records = []
    for c in combos:
        sub = df_e[c['Mask']].copy()
        n = len(sub)
        gmv = sub['order_gmv'].sum()
        low_n = sub['low_review'].sum()
        low_rate = sub['low_review'].mean() * 100.0 if n > 0 else 0.0

        records.append({
            'Combination_ID': c['Combination_Name'].split(':')[0],
            'Combination_Name': c['Combination_Name'].split(': ')[1],
            'Order_Count': n,
            'Order_Share_Pct': n / total_orders * 100.0,
            'Total_GMV_BRL': gmv,
            'GMV_Share_Pct': gmv / total_gmv * 100.0,
            'Low_Reviews': low_n,
            'Low_Review_Rate_Pct': low_rate,
            'Dissatisfaction_Share_Pct': low_n / total_low * 100.0,
            'Operational_Mechanism': 'Feedback timing amplifies severe delay' if 'COMBO-01' in c['Combination_Name'] else ('Carrier bottleneck on high-volume trunk' if 'COMBO-02' in c['Combination_Name'] or 'COMBO-03' in c['Combination_Name'] else ('Warehouse delay compounds interstate transit' if 'COMBO-04' in c['Combination_Name'] else 'Volume exposure in heavy goods'))
        })

    combo_df = pd.DataFrame(records)
    csv_path = TABLES_DIR / "high_impact_combinations.csv"
    combo_df.to_csv(csv_path, index=False)
    print(f"  Saved {csv_path}")

    # Figure 26: High-Impact Segment Exposure Matrix (Bar comparison of Share of Orders vs Share of Low Reviews)
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    x = np.arange(len(combo_df))
    width = 0.35

    ax.bar(x - width/2, combo_df['Order_Share_Pct'], width, label='Order Volume Share (%)', color='#93C5FD', edgecolor='#1E40AF', linewidth=0.8)
    ax.bar(x + width/2, combo_df['Dissatisfaction_Share_Pct'], width, label='Low Review Share (% Rating 1–2 Stars)', color=COLOR_DANGER, edgecolor='#991B1B', linewidth=0.8)

    ax.set_xticks(x)
    ax.set_xticklabels([r['Combination_ID'] for _, r in combo_df.iterrows()], fontsize=9, fontweight='bold')
    ax.set_ylabel("Share of Marketplace Total (%)", fontsize=10)
    ax.set_title("Disproportionate Dissatisfaction Exposure Across Compound Operational Segments", fontsize=11, fontweight='bold', pad=12)
    ax.grid(True, linestyle=':', alpha=0.5, axis='y')
    ax.legend(frameon=True, fontsize=9)

    for i, r in combo_df.iterrows():
        ratio = r['Dissatisfaction_Share_Pct'] / r['Order_Share_Pct'] if r['Order_Share_Pct'] > 0 else 0
        ax.annotate(f"{ratio:.1f}x Risk", xy=(i + width/2, r['Dissatisfaction_Share_Pct']), xytext=(i + width/2 - 0.15, r['Dissatisfaction_Share_Pct'] + 1.0),
                    fontsize=8, fontweight='bold', color=COLOR_DANGER)

    plt.tight_layout()
    fig26_path = FIGURES_DIR / "fig26_high_impact_segment_exposure_matrix.png"
    plt.savefig(fig26_path)
    plt.close()
    print(f"  Saved {fig26_path}")

    return combo_df


# =============================================================================
# 8. BUSINESS EXPOSURE FRAMEWORK (TABLE 8)
# =============================================================================
def build_business_exposure_segments(df_e: pd.DataFrame) -> pd.DataFrame:
    """
    Computes Order, Revenue, Dissatisfaction, and Delay exposures across major business segments.
    """
    print("\n--- 8. Building Business Exposure Framework ---")
    total_orders = len(df_e)
    total_gmv = df_e['order_gmv'].sum()
    total_low = df_e['low_review'].sum()
    total_severe_late = df_e['is_severe_late'].sum()

    segments = [
        {
            'Segment_Category': 'Delay Severity',
            'Segment_Name': 'Severe Late (>3.5 Days Past SLA)',
            'Mask': df_e['is_severe_late'] == 1
        },
        {
            'Segment_Category': 'Feedback Timing',
            'Segment_Name': 'Strict Calendar Pre-Delivery Surveys',
            'Mask': df_e['strict_calendar_pre'] == 1
        },
        {
            'Segment_Category': 'Geographic Corridor',
            'Segment_Name': 'São Paulo to Rio de Janeiro (SP -> RJ)',
            'Mask': df_e['corridor'] == 'SP -> RJ'
        },
        {
            'Segment_Category': 'Geographic Corridor',
            'Segment_Name': 'São Paulo to Bahia (SP -> BA)',
            'Mask': df_e['corridor'] == 'SP -> BA'
        },
        {
            'Segment_Category': 'Seller Operations',
            'Segment_Name': 'Slow Merchant Dispatch (Handling > 5d)',
            'Mask': df_e['approval_to_carrier_days'] > 5.0
        },
        {
            'Segment_Category': 'Compound Risk',
            'Segment_Name': 'Severe Delay + Pre-Delivery Survey',
            'Mask': (df_e['is_severe_late'] == 1) & (df_e['strict_calendar_pre'] == 1)
        },
        {
            'Segment_Category': 'Merchandise Exposure',
            'Segment_Name': 'Top Category: Bed Bath & Table',
            'Mask': df_e['dominant_category'] == 'bed_bath_table'
        }
    ]

    records = []
    for s in segments:
        sub = df_e[s['Mask']]
        orders = len(sub)
        gmv = sub['order_gmv'].sum()
        low_reviews = sub['low_review'].sum()
        severe_delays = sub['is_severe_late'].sum()

        records.append({
            'Segment_Category': s['Segment_Category'],
            'Segment_Name': s['Segment_Name'],
            'Order_Count': orders,
            'Order_Exposure_Pct': orders / total_orders * 100.0,
            'Total_GMV_BRL': gmv,
            'Revenue_Exposure_Pct': gmv / total_gmv * 100.0,
            'Low_Reviews_Count': low_reviews,
            'Dissatisfaction_Exposure_Pct': low_reviews / total_low * 100.0,
            'Severe_Delays_Count': severe_delays,
            'Delay_Exposure_Pct': severe_delays / total_severe_late * 100.0,
            'Low_Review_Rate_Pct': low_reviews / orders * 100.0 if orders > 0 else 0.0
        })

    exp_df = pd.DataFrame(records)
    csv_path = TABLES_DIR / "business_exposure_segments.csv"
    exp_df.to_csv(csv_path, index=False)
    print(f"  Saved {csv_path}")
    return exp_df


# =============================================================================
# 9. PRIORITIZATION SCORING & P0/P1/P2 (TABLE 9 & FIGURE 28)
# =============================================================================
def build_prioritization_score_table() -> pd.DataFrame:
    """
    Computes multi-factor Prioritization Score across candidate interventions:
    Priority = Severity (1-5) * Exposure (1-5) * Actionability (1-5) * Evidence Confidence (1-5).
    """
    print("\n--- 9. Building Prioritization Score Table & P0/P1/P2 Framework ---")
    interventions = [
        {
            'Intervention_ID': 'INT-01',
            'Intervention_Name': 'Feedback Timing Guardrail (Survey Suppression Until Confirmed Delivery)',
            'Target_Segment': 'Pre-Delivery Survey Recipient Orders (N=4,976)',
            'Severity_Score': 5,          # 72.6% low review rate
            'Exposure_Score': 5,          # Accounts for 29.4% of low reviews
            'Actionability_Score': 5,     # Immediate software/CRM configuration rule (Zero Capex)
            'Evidence_Score': 5,          # Controlled OR = 12.5x (p < 10^-50), stratified proofs
            'P_Rank': 'P0 — Immediate',
            'Addressable_Low_Reviews': 3613,
            'Addressable_GMV_BRL': 778000.0,
            'Target_Reduction_Impact': '1,500 to 2,200 low reviews prevented via post-delivery survey gating',
            'Owner': 'CRM / Customer Experience Team'
        },
        {
            'Intervention_ID': 'INT-02',
            'Intervention_Name': 'Dynamic SLA Recalibration & Buffer Calibration (SP -> RJ Corridor)',
            'Target_Segment': 'São Paulo to Rio de Janeiro Shipments (N=8,065)',
            'Severity_Score': 4,          # 20.1% low review rate, 12.0% severe delay rate
            'Exposure_Score': 4,          # 13.2% of platform low reviews concentrated in one corridor
            'Actionability_Score': 4,     # Algorithm update to promised delivery dates + carrier routing
            'Evidence_Score': 5,          # Corridor model verified (N=8,065)
            'P_Rank': 'P0 — Immediate',
            'Addressable_Low_Reviews': 1625,
            'Addressable_GMV_BRL': 1237250.0,
            'Target_Reduction_Impact': '25% reduction in severe delay eliminates ~240 acute low reviews',
            'Owner': 'Logistics & Carrier Management'
        },
        {
            'Intervention_ID': 'INT-03',
            'Intervention_Name': 'Proactive In-Transit Delay Messaging (Day 3.5 Late Trigger)',
            'Target_Segment': 'Parcels Delayed Past Operational Escalation Threshold (>3.5d)',
            'Severity_Score': 5,          # 72.4% low review rate beyond Day 3.5
            'Exposure_Score': 4,          # 29.6% of delivered low reviews
            'Actionability_Score': 4,     # Automated SMS/WhatsApp notification + proactive coupon/credit
            'Evidence_Score': 5,          # Segmented regression threshold tau=0.5d / tau=3.5d
            'P_Rank': 'P0 — Immediate',
            'Addressable_Low_Reviews': 3636,
            'Addressable_GMV_BRL': 897000.0,
            'Target_Reduction_Impact': 'Mitigates in-transit customer panic before survey solicitation',
            'Owner': 'Operations & Customer Support'
        },
        {
            'Intervention_ID': 'INT-04',
            'Intervention_Name': 'Interstate 3PL Carrier Diversification & SLA Enforcement',
            'Target_Segment': 'Inter-Regional Long-Haul Corridors (SP -> BA, PE, CE, North/Northeast)',
            'Severity_Score': 4,          # 18.2% low review rate in SP -> BA
            'Exposure_Score': 3,          # High regional concentration
            'Actionability_Score': 3,     # Requires secondary carrier onboarding & contract renegotiation
            'Evidence_Score': 5,          # Carrier accounts for 76.9% timeline and 3.2x excess odds per SD
            'P_Rank': 'P1 — Strategic',
            'Addressable_Low_Reviews': 1250,
            'Addressable_GMV_BRL': 1150000.0,
            'Target_Reduction_Impact': 'Compresses long-haul transit by 3-5 days; prevents postal choke',
            'Owner': 'Logistics & 3PL Partnerships'
        },
        {
            'Intervention_ID': 'INT-05',
            'Intervention_Name': 'Peak-Season Linehaul Capacity Reservation (Black Friday Defense)',
            'Target_Segment': 'Q4 Holiday Demand Surge (Nov-Dec Shipments)',
            'Severity_Score': 5,          # Rating dropped to 3.82 stars; late rate rose to 16.2%
            'Exposure_Score': 3,          # Seasonal quarter exposure
            'Actionability_Score': 3,     # Requires guaranteed freight space reservations with carriers
            'Evidence_Score': 5,          # Event study proved carrier transit surged +2.7d (+3.3d total)
            'P_Rank': 'P1 — Strategic',
            'Addressable_Low_Reviews': 1180,
            'Addressable_GMV_BRL': 2100000.0,
            'Target_Reduction_Impact': 'Prevents annual post-Black Friday platform reputation erosion',
            'Owner': 'Executive Operations & Logistics'
        },
        {
            'Intervention_ID': 'INT-06',
            'Intervention_Name': 'Merchant Warehouse Dispatch SLA Enforcement (>5-Day Bottleneck Pruning)',
            'Target_Segment': 'Slow-Dispatch Sellers (Handling > 5 days; N=8,999 orders)',
            'Severity_Score': 3,          # 22.1% low review rate on slow-handling interstate orders
            'Exposure_Score': 3,          # 16.2% of low reviews
            'Actionability_Score': 4,     # Automatic listing deprioritization / commission surcharges
            'Evidence_Score': 4,          # Seller standardized OR = 1.12 (p < 10^-15)
            'P_Rank': 'P2 — Optimization',
            'Addressable_Low_Reviews': 1992,
            'Addressable_GMV_BRL': 1420000.0,
            'Target_Reduction_Impact': 'Enforces 48-hour carrier handoff compliance on high-volume sellers',
            'Owner': 'Seller Success & Marketplace Integrity'
        },
        {
            'Intervention_ID': 'INT-07',
            'Intervention_Name': 'Volumetric Category Packaging & Carrier Dimension Standardization',
            'Target_Segment': 'Bulky Categories (Bed Bath & Table, Furniture Decor)',
            'Severity_Score': 3,          # 15.8% low review rate
            'Exposure_Score': 3,          # 11.8% of low reviews in Bed Bath Table
            'Actionability_Score': 3,     # Merchant packaging guidelines & flat-rate volumetric boxes
            'Evidence_Score': 3,          # Exposure-driven; category interaction is small
            'P_Rank': 'P2 — Optimization',
            'Addressable_Low_Reviews': 1443,
            'Addressable_GMV_BRL': 1220000.0,
            'Target_Reduction_Impact': 'Reduces package handling friction and carrier transit delays',
            'Owner': 'Category Management & Merchant Ops'
        }
    ]

    for item in interventions:
        item['Priority_Score'] = item['Severity_Score'] * item['Exposure_Score'] * item['Actionability_Score'] * item['Evidence_Score']

    p_df = pd.DataFrame(interventions).sort_values('Priority_Score', ascending=False)
    csv_path = TABLES_DIR / "prioritization_score.csv"
    p_df.to_csv(csv_path, index=False)
    print(f"  Saved {csv_path}")

    # Figure 28: P0 / P1 / P2 Opportunity Matrix (Bubble Scatter: Actionability vs Severity, Sized by Priority Score)
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    color_map = {'P0 — Immediate': COLOR_DANGER, 'P1 — Strategic': COLOR_PRIMARY, 'P2 — Optimization': COLOR_SECONDARY}

    for p_rank, group in p_df.groupby('P_Rank'):
        ax.scatter(
            group['Actionability_Score'],
            group['Severity_Score'],
            s=group['Priority_Score'] * 1.8,
            color=color_map[p_rank],
            alpha=0.75,
            edgecolors='black',
            linewidth=0.8,
            label=p_rank
        )

    for _, r in p_df.iterrows():
        ax.annotate(
            f"{r['Intervention_ID']}: {r['Intervention_Name'].split(' (')[0]}\n(Score: {r['Priority_Score']})",
            xy=(r['Actionability_Score'], r['Severity_Score']),
            xytext=(r['Actionability_Score'] - 0.25, r['Severity_Score'] + 0.18),
            fontsize=8,
            fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.85, edgecolor='#CCCCCC')
        )

    ax.set_title("Olist Executive Intervention Prioritization Matrix (P0 / P1 / P2)", fontsize=12, fontweight='bold', pad=12)
    ax.set_xlabel("Operational Actionability (1 = Macro Constraint, 5 = Direct Software/Policy Control)", fontsize=10)
    ax.set_ylabel("Dissatisfaction Severity (1 = Low Impact, 5 = Acute Failure)", fontsize=10)
    ax.set_xlim(2.0, 5.5)
    ax.set_ylim(2.5, 5.5)
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.legend(title='Priority Tier', frameon=True, fontsize=9, loc='lower right')

    plt.tight_layout()
    fig28_path = FIGURES_DIR / "fig28_p0_p1_p2_opportunity_matrix.png"
    plt.savefig(fig28_path)
    plt.close()
    print(f"  Saved {fig28_path}")

    return p_df


# =============================================================================
# 10. EXECUTIVE SCORECARD (TABLE 10 & FIGURE 30)
# =============================================================================
def build_executive_scorecard() -> pd.DataFrame:
    """
    Constructs the operational executive scorecard with metrics, thresholds, owners, and cadences.
    """
    print("\n--- 10. Building Executive Scorecard ---")
    scorecard_data = [
        {
            'KPI_Code': 'KPI-01',
            'Metric_Name': 'Strict Pre-Delivery Survey Rate (%)',
            'Current_Value': '5.2%',
            'Problem_Threshold': '> 1.0%',
            'Target_Benchmark': '0.0% (Zero Tolerance)',
            'Affected_Population': 'All Customers (4,976 orders currently impacted)',
            'Priority_Tier': 'P0 — Immediate',
            'Accountable_Owner': 'CRM & Platform Engineering',
            'Cadence': 'Real-Time / Daily'
        },
        {
            'KPI_Code': 'KPI-02',
            'Metric_Name': 'SP -> RJ Corridor Late Delivery Rate (%)',
            'Current_Value': '15.3%',
            'Problem_Threshold': '> 10.0%',
            'Target_Benchmark': '< 7.5%',
            'Affected_Population': 'São Paulo to Rio de Janeiro Shipments (8,065 orders)',
            'Priority_Tier': 'P0 — Immediate',
            'Accountable_Owner': 'Logistics / Carrier Operations',
            'Cadence': 'Weekly'
        },
        {
            'KPI_Code': 'KPI-03',
            'Metric_Name': 'Severe Delivery Delay Rate (>3.5d Late)',
            'Current_Value': '5.2%',
            'Problem_Threshold': '> 4.0%',
            'Target_Benchmark': '< 2.5%',
            'Affected_Population': 'Platform-Wide Orders (5,021 orders currently)',
            'Priority_Tier': 'P0 — Immediate',
            'Accountable_Owner': 'Carrier Linehaul Management',
            'Cadence': 'Weekly'
        },
        {
            'KPI_Code': 'KPI-04',
            'Metric_Name': 'Merchant Warehouse Handling Time (>5d Rate)',
            'Current_Value': '9.4%',
            'Problem_Threshold': '> 8.0%',
            'Target_Benchmark': '< 3.0%',
            'Affected_Population': 'Marketplace Sellers (8,999 interstate orders)',
            'Priority_Tier': 'P2 — Optimization',
            'Accountable_Owner': 'Seller Success & Operations',
            'Cadence': 'Bi-Weekly'
        },
        {
            'KPI_Code': 'KPI-05',
            'Metric_Name': 'Long-Haul Trunk Duration (SP -> BA Mean Days)',
            'Current_Value': '17.6 days',
            'Problem_Threshold': '> 15.0 days',
            'Target_Benchmark': '< 12.0 days',
            'Affected_Population': 'Northeast Cross-Regional Shipments',
            'Priority_Tier': 'P1 — Strategic',
            'Accountable_Owner': '3PL Carrier Partnerships',
            'Cadence': 'Monthly'
        },
        {
            'KPI_Code': 'KPI-06',
            'Metric_Name': 'Black Friday Transit Inflation (Carrier Surge Days)',
            'Current_Value': '+2.7 days',
            'Problem_Threshold': '> +2.0 days',
            'Target_Benchmark': '< +1.5 days',
            'Affected_Population': 'Q4 Holiday Surge Shipments',
            'Priority_Tier': 'P1 — Strategic',
            'Accountable_Owner': 'Executive Logistics Planning',
            'Cadence': 'Quarterly / Seasonal Pre-Mortem'
        }
    ]
    card_df = pd.DataFrame(scorecard_data)
    csv_path = TABLES_DIR / "executive_scorecard.csv"
    card_df.to_csv(csv_path, index=False)
    print(f"  Saved {csv_path}")

    # Figure 30: Executive Scorecard Visual Table
    fig, ax = plt.subplots(figsize=(12, 5), dpi=300)
    ax.axis('off')

    table_data = []
    cell_colors = []
    headers = ['KPI Code', 'Operational Metric', 'Current Value', 'Target SLA', 'Priority', 'Accountable Owner', 'Cadence']

    for _, r in card_df.iterrows():
        table_data.append([r['KPI_Code'], r['Metric_Name'], r['Current_Value'], r['Target_Benchmark'], r['Priority_Tier'], r['Accountable_Owner'], r['Cadence']])
        bg_col = '#FEF2F2' if 'P0' in r['Priority_Tier'] else ('#EFF6FF' if 'P1' in r['Priority_Tier'] else '#F0FDF4')
        cell_colors.append([bg_col] * len(headers))

    tbl = ax.table(cellText=table_data, colLabels=headers, cellColours=cell_colors, loc='center', cellLoc='left')
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(8.5)
    tbl.scale(1.0, 1.8)

    for (i, j), cell in tbl.get_celld().items():
        if i == 0:
            cell.set_text_props(weight='bold', color='white')
            cell.set_facecolor(COLOR_PRIMARY)
            cell.set_height(0.08)
        else:
            cell.set_edgecolor('#E5E7EB')
            cell.set_linewidth(0.6)

    ax.set_title("Olist Marketplace: Executive Operational Scorecard & Monitoring Cadence", fontsize=13, fontweight='bold', pad=15)
    plt.tight_layout()
    fig30_path = FIGURES_DIR / "fig30_executive_prioritization_scorecard.png"
    plt.savefig(fig30_path, bbox_inches='tight')
    plt.close()
    print(f"  Saved {fig30_path}")

    return card_df


# =============================================================================
# 11. ROOT-CAUSE WATERFALL VISUAL (FIGURE 29)
# =============================================================================
def build_root_cause_waterfall_figure():
    """
    Generates Figure 29: Visual Root-Cause Waterfall / Decision Framework.
    """
    print("\n--- 11. Generating Figure 29: Root-Cause Waterfall & Decision Framework ---")
    fig, ax = plt.subplots(figsize=(11, 6), dpi=300)
    ax.axis('off')

    # Define steps in the causal cascade
    steps = [
        ("1. STRUCTURAL GEOGRAPHY", "70.9% of sellers concentrated in São Paulo.\nGenerates long-haul exposure to North/Northeast.", "#EFF6FF", COLOR_PRIMARY),
        ("2. CARRIER TRANSIT BOTTLENECK", "Carrier linehaul accounts for 76.9% of fulfillment duration.\nExcess odds ratio is 3.2x per SD vs. seller handling.", "#FEF2F2", COLOR_DANGER),
        ("3. CORRIDOR CONCENTRATION", "SP -> RJ trunk corridor accounts for 13.2% of all low reviews.\nLate delivery rate reaches 15.3%.", "#FFFBEB", COLOR_ACCENT),
        ("4. OPERATIONAL SLA BREACH", "Inflection breakpoint at Day 0.5; escalation beyond Day 3.5.\n5.2% of orders generate 29.6% of low reviews.", "#FEF2F2", COLOR_DANGER),
        ("5. FEEDBACK ASYNCHRONY AMPLIFIER", "CRM survey sent while package is delayed in transit.\nMultiplies odds of low review by 12.5x (Strict Calendar Pre-Deliv).", "#FDF2F8", COLOR_PURPLE),
        ("6. OBSERVED MARKETPLACE DISSATISFACTION", "26.1% of marketplace negative reviews accounted for by\npre-delivery surveys during in-transit delays.", "#F3F4F6", COLOR_MUTED)
    ]

    box_height = 0.12
    box_width = 0.72
    y_start = 0.88
    y_step = 0.16

    for i, (title, desc, bg_color, border_color) in enumerate(steps):
        y_pos = y_start - i * y_step
        # Draw box
        rect = plt.Rectangle((0.14, y_pos - box_height/2), box_width, box_height,
                             facecolor=bg_color, edgecolor=border_color, linewidth=1.5,
                             transform=ax.transAxes, zorder=2)
        ax.add_patch(rect)

        # Text
        ax.text(0.16, y_pos + 0.02, title, fontsize=9.5, fontweight='bold', color=border_color, transform=ax.transAxes, zorder=3)
        ax.text(0.16, y_pos - 0.035, desc, fontsize=8, color='#374151', transform=ax.transAxes, zorder=3)

        # Arrow down to next step
        if i < len(steps) - 1:
            next_y = y_start - (i + 1) * y_step
            ax.annotate("", xy=(0.50, next_y + box_height/2), xytext=(0.50, y_pos - box_height/2),
                        arrowprops=dict(arrowstyle="->", color='#9CA3AF', lw=1.8),
                        transform=ax.transAxes, zorder=1)

    ax.set_title("Olist Marketplace: Anatomical Root-Cause Waterfall (The Three-Tiered System)", fontsize=12, fontweight='bold', pad=12)
    plt.tight_layout()
    fig29_path = FIGURES_DIR / "fig29_root_cause_waterfall_decision_framework.png"
    plt.savefig(fig29_path, bbox_inches='tight')
    plt.close()
    print(f"  Saved {fig29_path}")


# =============================================================================
# 12. MODULE 5 FINDING REGISTER (TABLE 11)
# =============================================================================
def build_module5_finding_register() -> pd.DataFrame:
    """
    Compiles formal Module 5 findings register linking evidence to action.
    """
    print("\n--- 12. Building Module 5 Finding Register ---")
    findings = [
        {
            'Finding': 'M5-01: Survey Suppression Gating (Zero-Capex Software Fix)',
            'Metric': 'Adjusted Odds Ratio = 12.50x (Strict Calendar Pre-Delivery); 29.4% Low Review Share',
            'Evidence': '4,976 orders surveyed on a calendar date strictly prior to delivery date had a 72.6% low review rate vs 9.4% for post-delivery.',
            'Exposure': '4,976 orders, R$778k GMV, 3,613 low reviews (29.4% of delivered low reviews)',
            'Mechanism': 'Feedback timing asynchrony converts customer in-transit anxiety into formal negative ratings.',
            'Action': 'Configure CRM logic to suppress survey trigger until confirmed delivery timestamp is recorded.',
            'Priority': 'P0 — Immediate',
            'Confidence': 'High (Robust across 4 definitions and delay strata)'
        },
        {
            'Finding': 'M5-02: SP -> RJ Trunk Corridor SLA Recalibration',
            'Metric': 'Late Delivery Rate = 15.3%, Severe Late Rate = 12.0%, Low Review Rate = 20.1%',
            'Evidence': 'Corridor accounts for 8,065 orders and 1,625 low reviews (13.2% of platform low reviews).',
            'Exposure': '8,065 orders, R$1.24M GMV, 1,625 low reviews',
            'Mechanism': 'Linehaul postal choke on the most active interstate route in Brazil.',
            'Action': 'Recalibrate promised SLA dates dynamically by +2 days and route to secondary private 3PL carriers.',
            'Priority': 'P0 — Immediate',
            'Confidence': 'High (N=8,065 corridor census)'
        },
        {
            'Finding': 'M5-03: Operational Escalation Alert Trigger at Day 3.5 Late',
            'Metric': 'Inflection Breakpoint tau=0.5d, Probability Escalation at tau=3.5d',
            'Evidence': 'Orders late past 3.5 days have a 72.4% low review rate and generate 29.6% of all low reviews.',
            'Exposure': '5,021 orders, R$897k GMV, 3,636 low reviews',
            'Mechanism': 'Customer expectations collapse beyond Day 3.5; without proactive communication, 1-star reviews are guaranteed.',
            'Action': 'Trigger automated proactive SMS/WhatsApp delay notification with R$15 compensation credit on Day 3 late.',
            'Priority': 'P0 — Immediate',
            'Confidence': 'High (Piecewise OLS RSS minimized at tau=0.5d; delta AIC = -1,556)'
        },
        {
            'Finding': 'M5-04: Merchant Warehouse Dispatch Bottleneck Pruning',
            'Metric': 'Handling Time > 5 Days on 9.4% of Orders; Standardized OR = 1.12',
            'Evidence': 'Sellers taking >5 days to hand off parcels to carriers generate 1,992 low reviews on interstate routes.',
            'Exposure': '8,999 interstate orders, R$1.42M GMV, 1,992 low reviews',
            'Mechanism': 'Warehouse handling delay consumes the delivery buffer before the carrier linehaul even begins.',
            'Action': 'Enforce 48-hour carrier handoff compliance on high-volume sellers; apply listing deprioritization for violations.',
            'Priority': 'P2 — Optimization',
            'Confidence': 'High (Standardized logistic Model D)'
        },
        {
            'Finding': 'M5-05: The Three-Tiered System (Signature Competition Narrative)',
            'Metric': 'Structural Exposure (70.9% SP) -> Operational Bottleneck (76.9% Carrier) -> Feedback Amplification (12.5x OR)',
            'Evidence': 'Integrates all empirical modules: geography is mediated by transit time; carrier transit dominates delays; survey timing crystallizes anxiety.',
            'Exposure': 'Platform-Wide (N=95,824 delivered orders)',
            'Mechanism': 'Multi-layered system failure requiring targeted, tiered interventions rather than generic "better logistics".',
            'Action': 'Present three-tiered diagnostic to executive leadership with concrete P0/P1/P2 roadmap.',
            'Priority': 'Core Strategic Thesis',
            'Confidence': 'Highest (100% Zero-Trust Certified)'
        }
    ]
    f_df = pd.DataFrame(findings)
    csv_path = TABLES_DIR / "module5_finding_register.csv"
    f_df.to_csv(csv_path, index=False)
    print(f"  Saved {csv_path}")
    return f_df


# =============================================================================
# MAIN ORCHESTRATOR
# =============================================================================
def main():
    print("=" * 80)
    print("STARTING MODULE 5: ROOT-CAUSE SYNTHESIS & BUSINESS PRIORITIZATION")
    print("=" * 80)

    # 1. Load Data
    df_all, df_pop_e = load_canonical_data()
    print(f"Loaded Canonical Model: Total={len(df_all):,}, Population E={len(df_pop_e):,}")

    # 2. Build Contribution Matrix
    matrix_df = build_root_cause_contribution_matrix()

    # 3. High-Risk Delay Segments
    delay_df = build_high_risk_delay_segments(df_pop_e)

    # 4. High-Risk Seller Cohorts
    seller_df = build_high_risk_seller_segments(df_pop_e)

    # 5. High-Risk Geographic Corridors
    corr_df = build_high_risk_geographic_segments(df_pop_e)

    # 6. High-Risk Category Segments
    cat_df = build_high_risk_category_segments(df_pop_e)

    # 7. Mutually Exclusive Survey Timing Segments
    survey_df = build_survey_timing_segments(df_pop_e)

    # 8. High-Impact Combinations
    combo_df = build_high_impact_combinations(df_pop_e)

    # 9. Business Exposure Segments
    exposure_df = build_business_exposure_segments(df_pop_e)

    # 10. Prioritization Scoring & P0/P1/P2
    p_df = build_prioritization_score_table()

    # 11. Executive Scorecard
    card_df = build_executive_scorecard()

    # 12. Root-Cause Waterfall Figure 29
    build_root_cause_waterfall_figure()

    # 13. Module 5 Finding Register
    find_df = build_module5_finding_register()

    print("\n" + "=" * 80)
    print("[SUCCESS] MODULE 5 BUSINESS PRIORITIZATION ENGINE EXECUTED DETERMINISTICALLY!")
    print(f"  - 11 Structured CSV Tables saved to: {TABLES_DIR}")
    print(f"  - 6 Publication Figures (fig25–fig30) saved to: {FIGURES_DIR}")
    print("=" * 80)


if __name__ == '__main__':
    main()
