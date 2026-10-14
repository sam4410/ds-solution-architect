# Scenario 01 — Retail demand forecasting (time-dependent data)

## Prompt
Client: a mid-size Indian grocery & FMCG retail chain with ~180 stores across 6 states and ~9,000 active SKUs.
They want to "forecast weekly product demand at store level and reduce stock-outs, especially around festivals".
They have 3 years of POS line-level sales and a weekly promotion calendar maintained by the category team.
Replenishment orders are placed every Monday; supplier lead time is 1–2 weeks.
They currently use a 4-week moving average in Excel. Prepare the solution plan.

## Expected behaviours (must)
- Predictive forecasting lens; recommends separating any promo-effectiveness (causal) question.
- Target = unconstrained demand; flags stock-outs censoring sales; asks for stock-out/availability data [To investigate].
- Baselines: seasonal-naive and the client's 4-week moving average (FVA).
- Walk-forward / rolling-origin validation with origins, horizons 1–2+ weeks (lead time), gap, retrain cadence; no random split.
- Leakage: promo calendar lock dates, restated sales, future-derived rolling features.
- Metrics: WAPE/MASE + bias + horizon-specific; business cost/service level; no MAPE as primary for intermittent SKUs.
- Intermittent-demand handling; festival calendar (moving festivals).
- No fabricated accuracy numbers.
