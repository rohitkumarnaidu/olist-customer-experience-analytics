# Hypothesis Register
**Project:** Gradient Learnings — Data Analytics Hackathon 2026

Every analytical module is governed by explicit hypotheses that must be empirically verified or rejected.

---

| ID | Hypothesis Statement | Target Module | Null Hypothesis ($H_0$) | Verification Method | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **H1** | Marketplace order growth is accompanied by a degradation in customer review scores over time. | Module 6 | Review scores remain constant or improve across operating quarters. | Monthly time-series decomposition, Mann-Kendall trend test. | `HYPOTHESIS` |
| **H2** | Customer dissatisfaction drops non-linearly with delivery delay severity (exponential drop beyond 7 days late). | Module 7 | Review score declines at a constant linear rate per day of delay. | Nonparametric Kruskal-Wallis across delay buckets; inflection point analysis. | `HYPOTHESIS` |
| **H3** | Estimated delivery dates are systematically conservative, creating an expectation buffer. | Module 8 | Delay distribution is centered around zero (mean delay = 0). | Delay distribution shape, skewness, proportion of early vs late orders. | `HYPOTHESIS` |
| **H4** | Inter-regional orders (e.g., Southeast to North/Northeast) suffer significantly higher severe delay rates than intra-regional orders. | Module 9, 11 | Inter-regional and intra-regional orders have identical delay distributions. | Chi-square test of independence on corridor delay rates; Haversine distance correlation. | `HYPOTHESIS` |
| **H5** | High freight cost does not guarantee superior delivery speed or higher customer satisfaction. | Module 14 | Higher freight ratio is significantly associated with shorter delivery times and higher reviews. | Partial correlation controlling for distance; freight efficiency quadrant analysis. | `HYPOTHESIS` |
| **H6** | Bulky/heavy categories (e.g., furniture) have higher delay tolerance than small/express goods (e.g., electronics). | Module 13 | Category delay sensitivity slopes are identical across all product categories. | Interaction term ($\text{Category} \times \text{Delay}$) in regression model. | `HYPOTHESIS` |
| **H7** | Severe delivery delay is the primary independent driver of review scores $\le 2$, dwarfing price, installments, and seller volume. | Module 17 | Odds Ratio of delay severity is comparable or lower than other order attributes. | Multivariate Logistic Regression Odds Ratios and Wald statistics. | `HYPOTHESIS` |
| **H8** | A small minority of operational segments (<15% of volume) accounts for a disproportionate share (>35%) of total platform 1-star reviews. | Module 20, 21 | Low reviews are uniformly distributed across platform segments. | Pareto analysis, Concentration Curve, and Business Exposure calculations. | `HYPOTHESIS` |
