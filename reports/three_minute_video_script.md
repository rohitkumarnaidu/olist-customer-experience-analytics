# FINAL 3-MINUTE VIDEO SCRIPT

**Project:** Gradient Learnings Data Analytics Hackathon 2026 — Olist Customer Experience Analytics  
**Title:** Olist Customer Experience & Delivery Risk Diagnostic  
**Target Duration:** 2:45 – 3:00 minutes (Estimated: ~2:53 minutes)  
**Speaking Rate:** 140 – 145 words per minute  
**Total Spoken Word Count:** 418 words  
**Audit Standard:** Final End-to-End Zero-Trust Certified  

---

## Opening

Olist scaled rapidly to nearly one hundred thousand orders, but the data shows that customer dissatisfaction isn't evenly distributed. It is concentrated in a small set of operational patterns. Where is dissatisfaction coming from, how large is the exposure, and what should Olist fix first?

*Performance Note:* Look directly into the camera lens. Maintain an authoritative, measured executive tone. Do not rush the opening question; pause briefly (1 second) before transitioning to the methodology.

---

## Analytical Approach

We combined nine operational datasets into a validated order-level model covering 99,441 orders. We preserved one row per order, explored marketplace behavior, tested delivery and satisfaction statistically, and then localized the risk into high-impact operational segments.

*Performance Note:* Gesture toward the analytical architecture slide on screen. Speak with crisp, confident articulation. Emphasize the data integrity milestone (1 row = 1 order, 99,441 orders).

---

## Finding 1

Delivery delay is the strongest operational predictor of low reviews in our certified model. Customer review scores exhibit an econometric structural breakpoint at 0.5 days late, before entering an acute operational escalation zone past 3.5 days late, where low ratings reach 72.7%. Dissatisfaction becomes operationally acute beyond roughly three and a half days late.

*Performance Note:* Shift visual attention to the piecewise spline curve and predicted probability chart. Emphasize the distinction between the 0.5-day statistical inflection and the 3.5-day acute escalation zone.

---

## Finding 2

The majority of fulfillment time sits in carrier transit. Carrier linehaul accounts for 76.9% of fulfillment duration, averaging 9.3 days versus 2.8 days for merchant handling. In our standardized model, carrier transit shows approximately 3.16 times higher excess odds of dissatisfaction per standard deviation than merchant handling.

*Performance Note:* Point to the split-screen fulfillment duration and standardized odds ratio bars. Deliver the standardized comparison calmly and objectively; avoid any phrasing that implies carriers are single-handedly at fault.

---

## Finding 3

Seller supply is highly concentrated in São Paulo at 70.9%, so 64% of orders travel across state borders. The São Paulo to Rio de Janeiro corridor is especially important because it combines high volume with elevated delay and dissatisfaction exposure, generating 1,625 low reviews across 8,065 orders.

*Performance Note:* Focus attention on the inter-state flow sankey and the corridor risk matrix. Highlight the strategic exposure created by São Paulo merchant concentration feeding the Rio de Janeiro trunkline.

---

## Signature Finding

Our most distinctive finding is that some customers are asked to review before their package is recorded as delivered. Over 4,900 orders received surveys strictly before delivery, showing a 72.6% low-review rate and an adjusted odds ratio of 12.5 times. This is a strong adjusted association and a high-priority intervention hypothesis—not proof that survey timing itself causes the rating.

*Performance Note:* Turn your head and look directly back into the camera. Slow down slightly. Deliver the explicit qualification with utmost professional rigor and calm conviction. Let the 12.5x adjusted odds ratio register clearly.

---

## Exposure

After removing 51% overlap between interventions, these operating patterns cover 32,811 unique orders, 5.59 million Reais in GMV, and 7,005 observed low reviews—over half of all delivered dissatisfaction ever recorded on Olist.

*Performance Note:* Display the deduplication funnel on screen. Emphasize the rigor of avoiding double-counting, demonstrating that addressing these four failure modes targets over half of all platform dissatisfaction.

---

## Recommendations

We recommend three immediate P0 pilots: first, test delivery-gated survey timing; second, test a two-business-day promise adjustment on the São Paulo to Rio route; and third, test proactive in-transit notifications for severe delays. Longer term, Olist should diversify peak-season linehaul capacity and strengthen merchant dispatch governance.

*Performance Note:* Present the P0/P1/P2 opportunity matrix. Step through each recommendation with a solution-oriented, energetic cadence. Ensure +2 days and delay incentives are clearly communicated as pilot test parameters.

---

## Closing

The key lesson is simple: Olist does not need a generic marketplace-wide fix. The data points to a concentrated operational chain where targeted experiments can replace broad firefighting with measurable improvement. That's where we would focus first.

*Performance Note:* Return full eye contact to the camera lens. Deliver the closing punchline with warm executive confidence and conviction. Hold your gaze for two seconds as the final executive scorecard fades out.

---

## Video Timing & Word Count Breakdown

| Section | Target Timestamp | Target Duration | Spoken Word Count | Cadence (WPM) | Visual / Focus Asset |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Opening** | 0:00 – 0:20 | 20s | 43 words | 129 wpm | Title Slide & Growth Decoupling Callout |
| **Analytical Approach** | 0:20 – 0:40 | 20s | 45 words | 135 wpm | Analytical Architecture & Invariants |
| **Finding 1 (Delivery Delay)** | 0:40 – 1:05 | 25s | 55 words | 132 wpm | Piecewise Spline & Escalation Zone |
| **Finding 2 (Carrier Transit)** | 1:05 – 1:30 | 25s | 55 words | 132 wpm | Fulfillment Duration & Accountability Decomposition |
| **Finding 3 (Geographic Exposure)** | 1:30 – 1:50 | 20s | 45 words | 135 wpm | Inter-State Flows & SP $\to$ RJ Risk Matrix |
| **Signature Finding (Survey Timing)** | 1:50 – 2:15 | 25s | 62 words | 148 wpm | Pre-Delivery Adjusted Odds Ratio Comparison |
| **Exposure (Deduplication)** | 2:15 – 2:30 | 15s | 36 words | 144 wpm | Deduplication Funnel & Exposure Matrix |
| **Recommendations (P0 Pilots)** | 2:30 – 2:50 | 20s | 50 words | 150 wpm | Prioritized P0/P1/P2 Opportunity Matrix |
| **Closing** | 2:50 – 3:00 | 10s | 27 words | 162 wpm | Executive Governance Scorecard & Call to Action |
| **TOTALS** | **0:00 – 2:55** | **175s (~2:53)** | **418 words** | **~143 wpm** | **8 Curated Visual Assets** |

---

## Presenter Technical & Recording Guidance

### 1. Camera & Framing
- Position webcam/camera at eye level.
- Frame subject from mid-chest up (medium close-up).
- Maintain direct eye contact with the camera during the Opening, Signature Finding, and Closing.
- For data-heavy sections (Approach, Findings 1–3, Exposure, Recommendations), look toward the presentation screen while maintaining expressive energy.

### 2. Audio & Environment
- Use a dedicated cardioid condenser or directional lavalier microphone positioned 6–8 inches from mouth.
- Record in a quiet, treated interior space with minimal acoustic reverberation.
- Ensure audio input levels peak between -12 dB and -6 dB without digital clipping.

### 3. Screen & Visual Resolution
- Present in 16:9 widescreen format (1920x1080 Full HD or 3840x2160 4K).
- Ensure all charts from `outputs/figures/` are displayed at native sharp DPI without blurriness.
- Use clean slide cuts or gentle 0.3s cross-dissolve transitions; avoid distracting animated slide effects.
