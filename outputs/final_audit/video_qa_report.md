# Video Presentation QA & Certification Report

**Project:** Gradient Learnings Data Analytics Hackathon 2026 — Olist Customer Experience Analytics  
**Document Evaluated:** `reports/three_minute_video_script.md`  
**Storyboard Evaluated:** `reports/video_storyboard.md`  
**Claim Traceability Registry:** `outputs/final_audit/video_claim_traceability.csv`  
**Evaluation Date:** 2026-09-06  
**Audit Standard:** Final End-to-End Zero-Trust Certified  

---

## 1. Word Count

- **Total Spoken Words:** **407 spoken words**
- **Section Breakdown:**
  - **Opening (0:00 – 0:20):** 46 words
  - **Analytical Approach (0:20 – 0:40):** 36 words
  - **Finding 1 — Delivery Delay (0:40 – 1:05):** 54 words
  - **Finding 2 — Carrier Transit (1:05 – 1:30):** 47 words
  - **Finding 3 — Geographic Exposure (1:30 – 1:50):** 47 words
  - **Signature Finding — Survey Timing (1:50 – 2:15):** 60 words
  - **Finding 5 — Business Exposure (2:15 – 2:30):** 33 words
  - **Recommendations (2:30 – 2:50):** 46 words
  - **Closing (2:50 – 3:00):** 38 words
- **Word Economy Rating:** **EXCELLENT** (Within ideal range of 390–420 words).

---

## 2. Estimated Duration

- **Speaking Cadence:** 140 – 145 words per minute (natural, executive conversational pace)
- **Duration at 140 WPM:** **2 minutes 54 seconds (174.4s)**
- **Duration at 142 WPM:** **2 minutes 52 seconds (172.0s) [PREFERRED TARGET]**
- **Duration at 145 WPM:** **2 minutes 48 seconds (168.4s)**
- **Maximum Envelope:** 3 minutes 00 seconds (180.0s)
- **Duration Status:** **PASS** (Zero risk of exceeding the 3-minute hard ceiling).

---

## 3. Claim Traceability

Every single quantitative figure and analytical finding in the spoken script traces 100% to certified claims in `outputs/final_audit/final_claim_registry.csv` and `outputs/final_audit/population_registry.csv`:
- **Total Orders (99,441):** `POP-A` (Census Verified)
- **Delivered Low-Review Rate (12.8%):** `POP-E` (Census Verified)
- **Delivery Delay Primary Predictor (Adjusted OR = 9.8x):** `CLAIM-01` (p < 10^-50 Verified)
- **Structural Breakpoint ($\tau = 0.5$d late):** `CLAIM-02` ($\Delta\text{AIC} = -1,556$ Verified)
- **Operational Escalation Zone ($\tau = 3.5$d late, 72.7% low reviews):** `CLAIM-02` (Verified)
- **Carrier Fulfillment Share (76.9%, 9.30d vs 2.79d):** `CLAIM-03` (Verified)
- **Carrier vs Seller Excess-Odds Ratio (3.16x, OR 2.20 vs 1.38):** `CLAIM-03` (Model D Verified)
- **São Paulo Origin Share (70.9%) & Interstate Share (64.0%):** `CLAIM-06` (Census Verified)
- **SP $\to$ RJ Corridor (8,065 orders, 15.31% late, 1,625 low reviews):** `CLAIM-07` (Segment Fact Verified)
- **Strict Pre-Delivery Surveys (4,976 orders, 72.61% rate, Adjusted OR = 12.50x):** `CLAIM-04` (Controlled Association Verified)
- **Overdue-in-Transit Accounting Share (26.09%):** `CLAIM-05` (Census Fact Verified)
- **Intervention Overlap Rate (50.86%):** `CLAIM-11` (Set Union Accounting Verified)
- **Deduplicated Unique Exposure (32,811 orders, R$ 5.59M GMV, 7,005 low reviews):** `CLAIM-11` (57.08% Platform Footprint Verified)

*Traceability Verdict:* **100% TRACEABLE (20 of 20 elements mapped in `video_claim_traceability.csv`).**

---

## 4. Recommendation Traceability

All recommended actions map directly to `outputs/final_audit/final_recommendation_registry.csv`:
- **INT-01:** Feedback Timing Guardrail (Delivery-Gated Survey A/B Test) $\to$ **P0 (Rank 1, Score 625)**
- **INT-02:** Dynamic SLA Buffer Recalibration (+2 business days SP $\to$ RJ) $\to$ **P0 (Rank 3, Score 320)**
- **INT-03:** Proactive Delay Messaging & Calibrated Service Recovery (Day 3.0 late) $\to$ **P0 (Rank 2, Score 400)**
- **INT-04 / INT-05:** Long-Haul Capacity Reservation & 3PL Carrier Diversification $\to$ **P1 (Ranks 4 & 5)**
- **INT-06:** Merchant Dispatch SLA Governance (>5-day slow dispatch coaching) $\to$ **P2 (Rank 6)**

*Recommendation Verdict:* **100% REGISTRY ALIGNED.**

---

## 5. Visual Count & Presentation Alignment

- **Total Curated Visuals:** 8 high-resolution figures from `outputs/figures/`
- **Visual Schedule:**
  1. `fig01_monthly_marketplace_growth_divergence.png` (Scene 1: Scaling Paradox)
  2. Data Architecture Diagram (Scene 2: Methodology & Data Contracts)
  3. `fig20_delay_threshold_piecewise_spline_fit.png` + `fig08_review_score_by_delay_bucket.png` (Scene 3: Breakpoint & Escalation)
  4. `fig22_delivery_accountability_seller_vs_carrier.png` (Scene 4: Fulfillment Accountability)
  5. `fig23_geographic_corridor_risk_matrix.png` + `fig12_geographic_flow_seller_to_customer_states.png` (Scene 5: Geographic Supply Concentration)
  6. `fig21_survey_timing_adjusted_odds_comparison.png` (Scene 6: Signature Pre-Delivery Survey Finding)
  7. `fig26_high_impact_segment_exposure_matrix.png` (Scene 7: Deduplicated Business Exposure)
  8. `fig28_p0_p1_p2_opportunity_matrix.png` + `fig30_executive_prioritization_scorecard.png` (Scenes 8 & 9: P0 Pilots & Executive Governance)
- **On-Screen Text Rule Adherence:** Every slide restricted to 1 headline and 2–4 concise bullet metrics. Zero dense paragraphs.

*Visual Plan Verdict:* **PASS.**

---

## 6. Causal Language Audit

An automated regex scan tested the script against all prohibited and unsupported causal terms:
- `caused`: **0 occurrences** (PASS)
- `causes`: **1 occurrence** (Explicitly required qualification: *"not proof that survey timing itself causes the rating"*) (PASS)
- `proved`: **0 occurrences** (PASS)
- `proves`: **0 occurrences** (PASS)
- `eliminated`: **0 occurrences** (PASS)
- `guaranteed`: **0 occurrences** (PASS)
- `responsible for`: **0 occurrences** (PASS)
- `will reduce`: **0 occurrences** (PASS)
- `will improve`: **0 occurrences** (PASS)
- `fixed`: **0 occurrences** (PASS)

*Language Audit Verdict:* **100% PASS — Flawless causal discipline maintained.**

---

## 7. Numerical Consistency

Every numerical fact cited verbally was audited against the final certified master table:
- Total Orders: $99,441$ $\to$ Verified.
- Carrier Transit Share: $76.9\%$ ($9.30$d vs. $2.79$d) $\to$ Verified.
- Breakpoint / Escalation: $0.5$d late / $3.5$d late $\to$ Verified.
- Severe Delay Low-Review Rate: $72.7\%$ $\to$ Verified.
- Standardized ORs: $2.20$ vs. $1.38$ ($3.16\times$ excess-odds) $\to$ Verified.
- SP Seller Share: $70.9\%$ $\to$ Verified.
- Interstate Flow: $64.0\%$ $\to$ Verified.
- SP $\to$ RJ Corridor: $8,065$ orders, $15.31\%$ late, $1,625$ low reviews $\to$ Verified.
- Strict Pre-Delivery: $4,976$ orders, $72.61\%$ rate, Adjusted $\text{OR} = 12.50\times$ $\to$ Verified.
- Overdue-in-Transit Share: $26.09\%$ $\to$ Verified.
- Deduplication Overlap: $50.86\%$ $\to$ Verified.
- Unique Business Footprint: $32,811$ orders, $\text{R}\$ 5.59\text{M}$ GMV, $7,005$ low reviews $\to$ Verified.

*Numerical Consistency Verdict:* **100% CONSISTENT.**

---

## 8. Report & Artifact Consistency

The script, storyboard, and visual assets are 100% synchronized with:
- `reports/final_competition_report.md`
- `reports/final_report_appendix.md`
- `notebooks/FINAL_Olist_Analytics_Submission.ipynb`
- `outputs/final_end_to_end_zero_trust_audit.md`

Terminology, segment definitions (SEG-1 to SEG-5), intervention codes (INT-01 to INT-07), and statistical parameters match across all deliverables.

---

## 9. Story Quality & Executive Impact

The narrative follows the optimal executive problem-solving arc:
$$\text{BUSINESS PROBLEM} \to \text{EVIDENCE} \to \text{INSIGHT} \to \text{EXPOSURE} \to \text{ACTION}$$
- Eliminates technical trivia and software package names.
- Focuses on business risk, financial exposure, operational accountability, and pilot experimental designs.
- Provides immediate clarity on where leadership should deploy resources first.

---

## 10. Judge Simulation & Stress Test Answers

### Judge Question 1: "What is your single biggest analytical insight?"
> *"Customer dissatisfaction on Olist is not random noise. It concentrates in an observable operational chain—from São Paulo supply concentration to carrier linehaul transit to delivery delay, amplified by premature survey timing. Pre-delivery feedback timing exhibits an adjusted odds ratio of 12.5 times and accounts for over a quarter of platform-wide low reviews."*

### Judge Question 2: "What should Olist do tomorrow?"
> *"Execute three low-capex P0 randomized pilots: First, gate satisfaction surveys behind confirmed carrier delivery scan +24 hours. Second, add a candidate two-business-day buffer to checkout promises on the São Paulo to Rio de Janeiro corridor. Third, deploy automated proactive tracking notifications at Day 3.0 late to recover customer sentiment before negative reviews are submitted."*

### Judge Question 3: "What makes your analysis superior to standard EDA?"
> *"We preserved strict order grain across 99,441 orders, decomposed fulfillment duration and standardized odds between merchants and carriers, isolated structural breakpoints from operational escalation zones, and rigorously deduplicated a 51% multi-segment overlap to isolate a true unique footprint of 7,005 low reviews and R$ 5.59M in GMV."*

---

## 11. Final Verdict

# PASS — READY TO RECORD

The 3-minute video presentation package (`reports/three_minute_video_script.md` and `reports/video_storyboard.md`) is fully certified for video recording and final hackathon submission.
