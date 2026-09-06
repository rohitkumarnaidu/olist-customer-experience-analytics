# Scene-by-Scene Video Storyboard & Visual Presentation Plan

**Project:** Gradient Learnings Data Analytics Hackathon 2026 — Olist Customer Experience Analytics  
**Companion Script:** `reports/three_minute_video_script.md`  
**Target Duration:** Exactly 2:53 minutes (175 seconds)  
**Aspect Ratio:** 16:9 Landscape (1080p Full HD / 4K UHD Standard)  
**Total Scenes:** 9 Core Scenes  

---

## Storyboard Master Sequence Table

| Time | Scene | Spoken Message | On-Screen Headline | Visual | Numbers | Transition |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- |
| **0:00 – 0:20** | **1. Opening: Growth vs. Dissatisfaction** | Olist scaled rapidly to nearly 100,000 orders, but dissatisfaction is concentrated in a small set of operational patterns. Where is it coming from, and what should Olist fix first? | **OLIST SCALING STRAIN: DISSATISFACTION IS CONCENTRATED** | `outputs/figures/fig01_monthly_marketplace_growth_divergence.png` | • **+742% Order Growth**<br>• **99,441 Total Orders**<br>• **12.8% Low Reviews** | Fade in from black; red callout box highlighting the Nov 2017 rating dip. |
| **0:20 – 0:40** | **2. Analytical Approach & Architecture** | We combined 9 operational datasets into a validated order-level model of 99,441 orders, preserving 1 row per order, and localized risk into high-impact operational segments. | **DATA CONTRACTS & RIGOROUS ORDER-GRAIN ARCHITECTURE** | Analytical Architecture Diagram (9 CSVs $\to$ Canonical Base Table) | • **9 Source Datasets**<br>• **99,441 Orders**<br>• **1 Row = 1 Order**<br>• **195/195 Tests Passing** | Smooth push right; display the Zero-Trust Certification badge. |
| **0:40 – 1:05** | **3. Finding 1: Delivery Delay Dominance** | Delivery delay is the strongest operational predictor of low reviews. Scores break at 0.5 days late and collapse into an acute escalation zone past 3.5 days late. | **DELIVERY DELAY IS THE DOMINANT OPERATIONAL DRIVER** | `outputs/figures/fig20_delay_threshold_piecewise_spline_fit.png` + `outputs/figures/fig08_review_score_by_delay_bucket.png` | • **0.5d Structural Break**<br>• **~3.5d Escalation Zone**<br>• **72.7% Low Reviews**<br>• **Adjusted OR = 9.8x** | Wipe up; highlight the sharp downward inflection at $\tau = 0.5$d and the $>3.5$d drop. |
| **1:05 – 1:30** | **4. Finding 2: Carrier Transit Accountability** | The majority of fulfillment time sits in carrier transit, averaging 9.3 days versus 2.8 for merchants, with 3.16 times higher excess odds of dissatisfaction in our model. | **CARRIER LINEHAUL TRANSIT DOMINATES FULFILLMENT DURATION** | `outputs/figures/fig22_delivery_accountability_seller_vs_carrier.png` | • **76.9% Transit Share**<br>• **9.30d Carrier vs. 2.79d Seller**<br>• **Carrier OR = 2.20 vs 1.38**<br>• **3.16x Excess-Odds Ratio** | Cross-dissolve; side-by-side comparison of duration share and standardized odds ratios. |
| **1:30 – 1:50** | **5. Finding 3: Geographic Supply Concentration** | Seller supply is concentrated in São Paulo at 70.9%, forcing 64% interstate flow. The SP-to-RJ corridor combines high volume with elevated delay and dissatisfaction. | **GEOGRAPHIC SUPPLY CONCENTRATION CREATES CORRIDOR EXPOSURE** | `outputs/figures/fig23_geographic_corridor_risk_matrix.png` + `outputs/figures/fig12_geographic_flow_seller_to_customer_states.png` | • **70.9% São Paulo Sellers**<br>• **64.0% Interstate Flow**<br>• **SP $\to$ RJ: 8,065 Orders**<br>• **15.3% Late \| 1,625 Low Reviews** | Pan & zoom into the Southeast trunkline; highlight SP $\to$ RJ risk bubble. |
| **1:50 – 2:15** | **6. Finding 4: Pre-Delivery Survey Timing** | Our most distinctive finding: some customers are asked to review before delivery. Over 4,900 orders received pre-delivery surveys, showing 72.6% low reviews and 12.5x adjusted odds. | **SIGNATURE FINDING: PRE-DELIVERY SURVEY TIMING ASYNCHRONY** | `outputs/figures/fig21_survey_timing_adjusted_odds_comparison.png` | • **4,976 Pre-Delivery Surveys**<br>• **72.61% Low-Review Rate**<br>• **Adjusted OR = 12.50x**<br>• **26.09% Platform Low Reviews** | Dramatic red spotlight framing the pre-delivery odds bar; qualified hypothesis tag. |
| **2:15 – 2:30** | **7. Finding 5: Deduplicated Business Exposure** | After removing 51% overlap between interventions, these patterns cover 32,811 unique orders, R$ 5.59M GMV, and 7,005 observed low reviews—over half of all platform dissatisfaction. | **DEDUPLICATED BUSINESS FOOTPRINT: 57.1% OF DISSATISFACTION** | `outputs/figures/fig26_high_impact_segment_exposure_matrix.png` + Overlap Funnel | • **32,811 Unique Orders**<br>• **R$ 5.59M GMV Footprint**<br>• **7,005 Unique Low Reviews**<br>• **50.86% Overlap Removed** | Split slide showing Gross Exposure ($14,255$) shrinking to Unique Set Union ($7,005$). |
| **2:30 – 2:50** | **8. Recommendations: Prioritized P0 Pilots** | We recommend 3 immediate P0 pilots: delivery-gated survey timing, a 2-business-day promise adjustment for SP-to-RJ, and proactive delay messaging for severe delays. | **PRIORITIZED OPERATIONAL ROADMAP: THREE IMMEDIATE P0 PILOTS** | `outputs/figures/fig28_p0_p1_p2_opportunity_matrix.png` | • **INT-01: Survey Gating (A/B Test)**<br>• **INT-02: SP $\to$ RJ +2d SLA Buffer**<br>• **INT-03: Day 3.0 Delay Alerts**<br>• **P1/P2: Linehaul & Seller SLA** | Step-by-step card reveal: highlight P0 quadrant (high impact, immediate feasibility). |
| **2:50 – 3:00** | **9. Closing: Concentrated Operational Chain** | Olist does not need generic firefighting. Targeted experiments along this concentrated operational chain will deliver measurable improvement. That's where we would focus first. | **PRECISION OPERATIONAL GOVERNANCE REPLACES FIREFIGHTING** | `outputs/figures/fig30_executive_prioritization_scorecard.png` | • **Target Pre-Delivery = 0.0%**<br>• **Target SP $\to$ RJ Late < 7.5%**<br>• **Protect R$ 5.59M GMV** | Fade to executive scorecard summary card; closing team credentials and GitHub link. |

---

## On-Screen Text & Visual Curation Rules

1. **Strict Text Economy:** Every scene displays exactly **1 major headline** and **2 to 4 compact supporting bullet metrics**. No narrative paragraphs are permitted on slides.
2. **Chart Selection:** Uses exactly **8 curated, publication-quality figures** from `outputs/figures/`, ensuring complete visual consistency with the final report and submission notebook.
3. **Visual Branding:** Maintains a dark navy and slate palette with warm gold and crimson accents for risk highlights, identical to the hackathon project design guidelines.
4. **Presenter Eye Contact Rule:**
   - Scene 1 (Opening): 100% direct eye contact with camera.
   - Scenes 2–5 (Methodology & Core Findings): 50% screen reference, 50% camera.
   - Scene 6 (Signature Finding): 100% direct eye contact on qualification statement.
   - Scene 7–8 (Exposure & Recommendations): 50% screen reference, 50% camera.
   - Scene 9 (Closing): 100% direct eye contact with camera.
