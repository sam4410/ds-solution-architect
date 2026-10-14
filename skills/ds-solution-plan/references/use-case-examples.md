# Worked Use-Case Examples (condensed)

These are **illustrations of reasoning and output shape**, not recommendations for any real
client dataset. No numbers here are results.

---

## Example 1 — Retail: weekly SKU×store demand forecasting to reduce stock-outs

**Lens:** Predictive (forecasting) feeding a prescriptive decision (order quantities). Causal sub-question
("do promotions increase sales?") is **separate**.

| Dimension | Plan |
|---|---|
| Decision | Weekly replenishment orders per SKU×store, placed Monday for delivery in 1–2 weeks |
| Unit / horizon | SKU×store×week; h = 1–4 weeks (lead time + review period) |
| Data | POS sales [Confirmed], stock-on-hand & stock-out flags [To investigate], promo calendar with lock dates [Assumed], price history [Confirmed], festival calendar (external) [Confirmed], lead times [To investigate] |
| Target | Unconstrained demand: sales with stock-out weeks flagged and excluded/imputed |
| Baselines | Seasonal-naive (same week last year), 4-week moving average, current planner forecast (FVA benchmark) |
| Candidates | ETS per series (few, long series); global LightGBM with lags ≥ horizon, rolling stats, price/promo/calendar features; Croston/TSB for intermittent SKUs |
| Metrics | Primary WAPE at h=1–2 on SKU×store; secondary bias & MASE; business: simulated stock-out rate & inventory cost under order policy |
| Validation | Expanding-window walk-forward, weekly origins over ≥ 52 weeks, horizons 1–4, 1-week gap for data latency, point-in-time promo data |
| Leakage risks | Future promos not locked at origin; restated sales; using sales during stock-outs as demand; rolling features including current week |
| Experiments | E1 baselines → E2 ETS → E3 global GBM → E4 ablations (promo, price, weather) → E5 tuning → E6 by category/store cluster/new items |
| Decision rule | Select by out-of-sample WAPE + bias + simulated cost, not training fit |

---

## Example 2 — BFSI: credit-card customer attrition (churn) with class imbalance

**Lens:** Predictive (who will attrite) + causal (does the retention offer work, and for whom → uplift).

| Dimension | Plan |
|---|---|
| Decision | Monthly list of top-k customers for retention calls (capacity k/month) |
| Target | Voluntary closure or ≥ N months inactivity within 3 months after snapshot [definition to confirm] |
| Unit | Customer-month snapshot; **group split by customer** |
| Baselines | Prevalence; current rule (e.g., spend drop > X%); logistic regression on RFM features |
| Candidates | Logistic (L2) → LightGBM with monotonic constraints where intuitive → survival (time to attrition) if timing matters |
| Imbalance | Class weights; PR-AUC & recall@k primary; calibrate after weighting |
| Metrics | Primary: precision/recall@k (k = call capacity); secondary PR-AUC, calibration; business: expected retained revenue |
| Validation | Out-of-time: train on snapshots ≤ T−6m, validate next 3 months, test last 3 months; customers grouped |
| Leakage | Closure request logged before snapshot; retention-team contact flags; fees reversed after complaint |
| Causal | Randomised holdout within top-k to estimate offer effect; uplift model only after randomised data exists |

---

## Example 3 — Healthcare (inferential): do two hospitals differ in average length of stay?

**Lens:** Inferential. No predictive model needed.

| Dimension | Plan |
|---|---|
| Estimand | Difference in mean LOS for comparable patients (case-mix adjusted) between Hospital A and B in FY |
| Design | Regression of log(LOS) or Gamma GLM with hospital indicator + case-mix covariates (age, DRG/diagnosis group, comorbidity index, admission type); robust SEs |
| Assumptions | Independence across admissions (cluster by patient for repeat admissions), correct case-mix model, comparable coding |
| Tests | Welch t-test on raw LOS only as descriptive; adjusted estimate primary; bootstrap CI; sensitivity excluding outliers & deaths |
| Reporting | Adjusted ratio of mean LOS with 95% CI; practical threshold (e.g., ≥ 0.5 day) agreed with client |
| Cannot identify | That hospital practices *cause* the difference (residual case-mix confounding) |

---

## Example 4 — Healthcare/BFSI/Retail (causal): effect of an intervention

*Healthcare:* post-discharge follow-up call program on 30-day readmission, rolled out to some wards first.
**Design options:** (1) randomise eligible discharges (preferred; ethics approval), (2) stepped-wedge rollout across wards,
(3) DiD using staggered rollout with event-study pre-trends, (4) RDD if enrolment used a risk-score cutoff.
**Estimand:** ATT on 30-day unplanned readmission among eligible discharges. Report risk difference + CI,
NNT, sensitivity (E-value), and what is not identified (long-term effects, ineligible patients).

---

## Example 5 — Insufficient data / ambiguous target

Client: "Use AI to improve our branch performance."
**Response:** Quick triage only — candidate framings: (a) forecasting branch footfall/transactions for staffing,
(b) explaining performance differences (inferential, risk-adjusted), (c) evaluating a past intervention (causal).
List what each needs, ask: *Which decision? Which KPI defines performance? What data exists per branch and for how long?*
Propose a 2–3 week discovery phase with data audit and KPI definition workshop. **Do not** recommend algorithms yet.
