# Strategic Thesis & Competition Differentiation Blueprint
**Project:** Gradient Learnings — Data Analytics Hackathon 2026  
**Subject:** Olist Brazilian E-Commerce Ecosystem Diagnostic

---

## 1. The Core Strategic Thesis

> **Central Hypothesis:**  
> Customer dissatisfaction on Olist is not a uniform consequence of delivery delays, nor can it be solved by broad platform-wide mandates. Instead, dissatisfaction is heavily concentrated in specific operational intersections—where geographic logistics friction (long-haul corridors), seller handling delays, category characteristics (bulky/fragile goods), and freight pricing economics converge to produce disproportionate customer dissatisfaction.

This thesis remains a **HYPOTHESIS** until empirically tested against the Olist dataset. Every finding will strictly adhere to the data evidence hierarchy:
1. `HYPOTHESIS`: Untested assumption.
2. `OBSERVED`: Directly computed metric from the dataset.
3. `INFERENCE`: Contextualized statistical interpretation.
4. `RECOMMENDATION`: Actionable operational intervention.

---

## 2. Competitive Differentiation: Beyond Generic Olist EDA

Most public Olist Kaggle/GitHub projects produce the exact same descriptive summaries:
- A monthly sales line chart showing November 2017 Black Friday peak.
- A bar chart showing São Paulo (`SP`) has the most orders.
- A correlation saying "late orders have lower review scores."

To win this competition, we elevate the inquiry to an **executive decision-support framework**:

| Standard Competitor Analysis | Our Differentiated Strategic Approach |
| :--- | :--- |
| Binary "On-Time vs Late" classification | **Nonlinear Delay Severity Buckets** (quantifying exact threshold drops at 1-3d, 4-7d, >7d late) |
| Basic Seller Average Rating ranking | **Context-Adjusted Seller Benchmarking** (controlling for category difficulty and geographic origin) |
| Isolated Category or State ranking | **Multivariate Corridors** ($S_{\text{state}} \times C_{\text{state}}$ routes with severe delay concentration) |
| Raw shipping cost correlation | **Freight Efficiency Trade-off** (identifying expensive routes that fail to deliver faster service) |
| Simple correlation coefficient | **Multivariate Logistic Regression** (identifying true independent drivers of low reviews with Odds Ratios) |
| Descriptive percentages alone | **Quantified Business Exposure** (Share of Platform Revenue at Risk vs Share of Low Reviews) |
| Generic advice ("Improve delivery speed") | **Targeted Intervention Matrix** (P0/P1/P2 actionable playbooks with measurable SLAs) |

---

## 3. The 6 Core Competition Questions & Analytical Mapping

1. **Q1 — Marketplace Performance Over Time:** Trend volume, revenue, AOV, and review scores. Test for the "growth vs. quality divergence" phenomenon.
2. **Q2 — Delivery Performance & Satisfaction:** Map delay days against 1-5 star distributions, calculating inflection points and category/regional variance.
3. **Q3 — Seller & Geographic Patterns:** Quantify spatial distribution, Haversine distances, interstate corridors, and regional logistics bottlenecks.
4. **Q4 — Product Category Performance:** Benchmark categories on volume, price, freight burden, and customer sentiment.
5. **Q5 — Payment Behavior:** Relate payment methods, installment adoption, and basket sizes to fulfillment and customer sentiment.
6. **Q6 — Root Cause Analysis:** Implement a 2-layer statistical + segmentation diagnostic isolating primary vs secondary drivers of `review_score <= 2`.
