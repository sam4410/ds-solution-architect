---
title: Store-Level Weekly Demand Forecasting & Stock-out Reduction — Data Science Solution Plan
client: Client (mid-size Indian grocery & FMCG retail chain)
industry: Retail
prepared_by: Data Science Solution Architecture team
date: 2026-10-14
version: 0.1 (draft)
depth: Standard
classification: Confidential
---

# Store-Level Weekly Demand Forecasting & Stock-out Reduction — Data Science Solution Plan

## 1. Executive Summary

- **Decision supported:** how much of each SKU to order for each store (or for the DC serving it) every Monday, so stores stop running out of stock, especially around festivals, without carrying excess inventory.
- **Problem in plain language:** the current 4-week moving average of sales cannot see festivals coming, treats promotions as normal demand, and mistakes "we sold nothing because the shelf was empty" for "nobody wanted it". We will replace it with a probabilistic demand forecast per SKU × store, built for the Monday-order, 1–2-week lead-time process, plus a transparent rule that turns the forecast into a recommended order quantity.
- **Lenses:** *Predictive* (AN1: demand forecasting) is the core. *Prescriptive* (AN2: forecast → order quantity at a target service level) sits on top of it. *Causal* (AN3: "did the new process actually reduce stock-outs?") is answered by a controlled store pilot, **not** by forecast accuracy.
- **Recommended approach:**
  1. Reconstruct the current 4-week-average process as the official baseline and backtest it, so we do not rely on any quoted accuracy.
  2. Forecast *unconstrained demand* (correcting for stock-outs), as quantiles over the lead-time-plus-review window, not a single point.
  3. Test a global gradient-boosted model with festival, promotion and calendar features alongside intermittent-demand statistical models for slow SKUs and hierarchy reconciliation; adopt each only where it beats the baselines by the agreed margin. Deep-learning models are deferred unless they clear a demonstrated gap.
  4. Validate by rolling-origin (every-Monday) backtests, with dedicated festival-window backtests and a locked final test.
  5. Roll out as a weekly batch with planner override, a shadow run, then a matched-store pilot.
- **What must be true:** (a) stock-on-hand or stock-out information exists (or can be inferred reasonably); (b) the promotion calendar is known and frozen *before* each Monday order, and we can recover what the calendar said at each past order date; (c) festival dates and regional relevance can be mapped to stores; (d) planners will act on the recommendations.
- **Top risks:** demand censored by stock-outs; at most ~3 observations of each festival (if history is a full 3 years); promotion information leaking from the future; sparse SKU×store series; benefit proof requires a pilot, not just a good backtest.
- **First next steps:** run the data-readiness checks in §5/§6 (inventory availability, promo-calendar history, calendar of festivals), agree the metric/service-level targets with supply-chain leadership, and set up the baseline backtest harness.

> **Note:** The client was unavailable for questions. Every client-specific detail below that was not in the brief is labelled **[Assumed]** or **[To investigate]** and listed in §4. No accuracy, uplift or stock-out numbers are claimed anywhere in this plan.

### Scope of this plan
- **Included:** framing, data assessment, baselines, candidates, metrics, experiments, validation and leakage audit, a light statistical/causal plan for the pilot, robustness, deployment/monitoring, roadmap.
- **Omitted/light:** price-elasticity and promotion-effectiveness measurement (not requested; flagged as a possible later analysis); full inventory optimisation (multi-echelon, shelf-life, MOQ optimisation) is limited to a service-level order rule in this phase; classification-style calibration is replaced by quantile calibration.
- **Routing:** framing (full); data assessment (full); model selection (full); validation/leakage (full); experiment design (full); statistical inference (pilot design only, light); evaluation & deployment (full).
- **Depth mode:** Standard.

## 2. Business Problem & Decision Framing

| Element | Definition for this case | Status |
|---|---|---|
| Decision | Weekly replenishment quantity per SKU per store (or per DC allocation) | [Assumed] store-level orders; DC-level orders would change the grain (see Q3) |
| Decision owner | Supply-chain / category planners placing the Monday order | [Assumed] |
| Decision timing (prediction point) | Monday order cut-off; data available through the previous Sunday | [Confirmed] orders are placed every Monday; cut-off hour [To investigate] |
| Supplier lead time | 1–2 weeks | [Confirmed]; per-supplier/SKU lead times [To investigate] |
| Forecast target window | Cumulative demand over the protection interval = lead time + review period (1 week), i.e. roughly weeks +1 to +3 relative to the order Monday, depending on supplier | Derived from [Confirmed] facts; exact interval per SKU depends on lead-time data |
| Forecast horizons | h = 1, 2, 3 weeks ahead as standard; festival pre-build horizons up to ~8–10 weeks | [Assumed] longer horizons are needed for festival stocking |
| Unit of analysis | SKU × store × week (week definition [To investigate]: ISO vs retail calendar, Monday–Sunday) | [Assumed] |
| Population | ~9,000 active SKUs × ~180 stores across 6 states, plus new and delisted items | [Confirmed] approximate scale per brief (~180 stores, ~9,000 SKUs, 6 states); number of non-zero series [To investigate] |
| Outcome (target) | **Unconstrained weekly demand** in units (sales corrected for periods of unavailability) | Definition proposed; depends on availability data |
| Observed proxy | Weekly units sold from POS lines (net of returns) | [Confirmed] POS exists |
| Cost of errors | Under-forecast → lost sales, customer loss, festival revenue loss. Over-forecast → holding cost, wastage (perishables), markdowns, working capital. Asymmetric and differs by category | [TBD with client]; per-category target service levels needed |
| Current approach | 4-week moving average in Excel | [Confirmed] |
| Success criteria | Better forecast value-added vs the current process, lower stock-out rate with no unacceptable inventory increase, measured in a pilot | Thresholds [TBD with client] |
| Constraints | Monday batch; planner usability (Excel-like outputs); data residency and consumer-data rules (DPDP Act 2023 – confirm with compliance) | [Assumed] except Monday batch |

## 3. Analytical Problem Classification

**Separate analyses**

| ID | Question | Lens | Formulation |
|---|---|---|---|
| AN1 | How much will each store sell of each SKU over the protection interval? | Predictive | Probabilistic multi-horizon time-series forecasting on a hierarchy (SKU × store × week) |
| AN2 | What quantity should we order to hit a target service level? | Prescriptive | Order-up-to level = forecast quantile for the protection interval minus on-hand and in-transit; per-category service levels |
| AN3 | Does the new process reduce stock-outs vs the current one? | Causal (programme evaluation) | Matched-store pilot / staggered rollout with difference-in-differences |
| AN4 (later, optional) | What incremental lift do promotions generate? | Causal | Not in scope; the forecasting model's promotion coefficients must **not** be read as lift |

**Rationale.** The ordering decision needs a distribution of demand over a window, not a weekly point value, because the stock-out cost is asymmetric. "Forecasting weekly demand" is therefore delivered as quantile forecasts aggregated over the lead-time-plus-review window.

**Alternatives considered**
- *Point forecast + fixed safety-stock %:* simpler to explain; adopt as the fallback if quantile models do not beat it.
- *Direct "will this SKU stock out next week" classification:* useful as a diagnostic or alert layer, but it is label-contaminated by past replenishment behaviour; consider later.
- *Daily forecasting:* better for fast movers and weekend peaks, but ordering is weekly; revisit if replenishment frequency increases.
- *Aggregated (category × store or SKU × cluster) forecasts:* fall-back for the sparse tail.

**Red flags**
- Sales ≠ demand during stock-outs (censoring), which would make a naive model reproduce past stock-outs.
- Festival signal is thin (at most ~3 occurrences per festival if history is a full 3 years) and festival dates move on lunar calendars.
- Promotion calendar may be revised after the order date; if we train on the final calendar we leak.
- A good backtest does not prove fewer stock-outs; this needs a pilot (AN3).

## 4. Assumptions, Unknowns & Client Clarification Questions

| ID | Statement | Type | Impact if wrong | Owner | Needed by |
|---|---|---|---|---|---|
| Q1 | Stock-on-hand (daily or weekly), in-transit and stock-out/availability flags exist at SKU×store | Open question (top priority) | If absent, demand must be inferred from zero-sales runs; accuracy of unconstrained demand and of stock-out KPIs drops; may need a data-capture workstream | Client IT / supply chain | Discovery week 1–2 |
| Q2 | The promotion calendar is final before the Monday order, and past versions (as known at each order date) are retrievable; it includes mechanic, depth, SKU/store scope | Open question (top priority) | If only the final executed calendar exists, features must be restricted or lag-simulated; promo effect on backtests will be overstated | Category team | Week 1–2 |
| Q3 | Orders are placed per store (not only per DC); the order grain and allocation logic are known | Open question | Changes target grain, hierarchy and what is "the decision" | Supply chain | Week 1 |
| Q4 | Lead time per supplier/SKU (and its variability), MOQ, case-pack, shelf-life, DC cut-off | Open question | Determines protection interval, safety stock and perishable handling | Procurement | Week 2 |
| Q5 | Which festivals matter per state/store, and which categories/SKUs are festival-driven | Open question | Wrong mapping dilutes festival features | Category team | Week 2 |
| A1 | POS history is ~3 years (per brief), complete and consistent, with SKU, store, timestamp, quantity, net value and bill ID fields | Assumption [Assumed] for completeness and fields | Missing months or store migrations create structural breaks | Client IT | Week 1 |
| A2 | Loyalty/customer identifiers on POS lines are not needed and will be excluded | Assumption | Reduces privacy scope; if wrongly included, adds DPDP obligations | DS lead | Week 1 |
| A3 | The planners will review and may override recommendations | Assumption | If fully automated ordering is expected, governance needs change | Business sponsor | Week 4 |
| A4 | No known data from before the last 3 years is usable | Assumption | Would help festival learning if older data exists | Client IT | Week 1 |
| A5 | Current accuracy is **not** known; we will reconstruct it by backtest | Open question (not in the brief) | None | DS team | Week 3 |
| A6 | Festival calendar for the autumn season is imminent (Diwali 2026 date to be verified); a full model cannot be live before it | Assumption [To investigate] | Set expectations: use an interim festival uplift rule for this season | Business sponsor | Immediately |
| Q6 | Targets: acceptable stock-out rate, inventory increase and service level by category | Open question | Needed to define pass/fail | Leadership | Week 3 |
| Q7 | Compute/stack in client environment (cloud vs on-prem, Python allowed, scheduler) | Open question | Affects deployment and roadmap effort | Client IT | Week 2 |

> **Open question:** Q1 and Q2 are the two answers that most change the plan; if either is "no", the Discovery phase gains a data-capture/reconstruction work package and the timeline in §19 extends.

## 5. Data Inventory & Feasibility Assessment

| Source | Business meaning | Owner | Grain/keys | Coverage & refresh | Point-in-time available? | Quality risks | Privacy/licensing | Status |
|---|---|---|---|---|---|---|---|---|
| POS line-level sales | What was sold, where, when | Client IT / retail ops | Bill line: store, SKU, timestamp, qty, value, discount [Assumed field list] | 3 years per brief; refresh [To investigate] | Yes, through Sunday for the Monday run (latency [To investigate]) | Returns netting, duplicates, store migrations, back-dated bills | May contain loyalty ID; drop/hash | [Confirmed] that line-level POS exists (per brief); field list [Assumed] |
| Weekly promotion calendar | Planned promotions by the category team | Category team | Week × SKU (or category) × store group; mechanic and depth | Weekly | Only if frozen before Monday; versions history needed | Late edits, execution mismatch, SKU/store scope ambiguity | Internal | [Confirmed] weekly calendar is maintained (per brief); content, lock date and version history [To investigate] |
| Product master & hierarchy | Category, brand, pack size, price band, shelf life | Merchandising | SKU | Current + changes | Yes | Delisting, re-coding, pack changes; surviving-item bias | Internal | [Assumed] |
| Store master | Format, size, state, city, opening/closing, cluster | Operations | Store | Current | Yes | Refits, closures create breaks | Internal | [Assumed] |
| Inventory on-hand / stock-out log | Availability by SKU×store | Supply chain | SKU×store×day/week | Unknown | Yes if snapshots are kept | May be only current (no history) | Internal | [To investigate] (critical) |
| Purchase orders, receipts, lead times | What was ordered/arrived/when | Procurement | PO line | Unknown | Yes | Partial deliveries, substitutions | Internal | [Assumed] |
| Price/MRP history | Shelf price, discounts | Pricing | SKU×store×date | Unknown | Yes if scheduled | Price in POS may stand in | Internal | [Assumed] (derivable from POS) |
| Festival & holiday calendar (national + state) | Festival timing, relevance by region | DS team to build + category team | Date × state | Public | Known well in advance | Lunar dates vary; regional relevance | Public | [To investigate] source verification |
| Weather (rain, heat) | Beverage, seasonal categories | External | District × day | Public APIs | Forecast only; use observed lag or a forecast snapshot | Matching to stores | Licence check | [To investigate], nice-to-have |

**Feasibility verdict: Feasible with conditions.** POS history plus the promo calendar is sufficient for a first model and a defensible baseline comparison. Blocking dependencies: (1) availability information (Q1) for an honest unconstrained-demand target and stock-out KPI; (2) historical versions of the promo calendar (Q2); (3) a signed-off festival-to-store mapping (Q5). Without (1) the pilot cannot measure stock-out reduction.

## 6. Data Quality & Preprocessing Plan

| Step | Rationale | Method | Risks | Validation check |
|---|---|---|---|---|
| Aggregate POS lines to SKU×store×week | Forecast grain | Net of returns using the bill date; consistent week definition (Mon–Sun) | Returns restated later; wrong calendar | Reconcile weekly totals to finance sales; compare to 4-4-5 vs ISO |
| Build a complete panel | Missing rows ≠ zero demand for open, in-range stores | Zero-fill only between SKU first-sale/listing date and delist date, and only on open store-days | Zero-filling pre-listing weeks inflates intermittency | Row counts by week; share of zeros by SKU age |
| Flag availability / stock-outs | Sales are censored when stock is zero | Use stock snapshots if available; otherwise flag runs of zero sales much longer than the SKU's typical inter-sale gap (heuristic, calibrated per velocity class) | Heuristic flags false positives for slow SKUs | Compare flags to the stock log on the subset where both exist |
| Unconstrained-demand reconstruction | Train on what customers wanted | (a) Exclude censored weeks from the loss (preferred first step); (b) impute from similar weeks or a censored-likelihood model as an experiment | Imputation can add bias or circularity | Compare backtest in-stock weeks only vs all weeks; card EX6 |
| Outlier/anomaly handling | Bulk buys, data errors, one-off events | Winsorise at a high quantile within SKU×store history; keep festival peaks (do not clip them as outliers) | Clipping real festival spikes | Check clipped weeks against festival calendar |
| Structural-break tagging | Store opening/closing/refit, SKU relaunch, pack change | Event flags; start history at break for new-store models | Unlabelled breaks cause persistent bias | Residual diagnostics around known events |
| Promotion features as-of order date | Avoid future leakage | Reconstruct promo state as known at each Monday cut-off using calendar versions; if unavailable, use only promos flagged ≥ N weeks ahead (N from lead-time/lock policy) | Overstated promo effect in backtest | Backtest with 'lagged-known' vs 'final' promo; large gap = leakage signal |
| Calendar/festival features | Moving festival dates | Days-to-festival, festival-week position, state-specific festival flags, pay-day/month-end, school calendar | Mis-assigned regional relevance | Event study: average weekly demand index around each festival by state |
| Hierarchy and clustering | Sparse series need pooling | Product hierarchy (SKU→brand→category), store clusters (format/state/volume) | Cluster definitions drifting | Stability across years |
| Velocity classification | Different models for different series | ADI/CV² (smooth, erratic, intermittent, lumpy) and ABC on volume, computed on training data only | Class leakage if calculated on full history | Recompute per fold |
| Scaling/encoding | Model needs | Target scaling per series (training window only); high-cardinality IDs as embeddings/categoricals; no leakage from target encoding (out-of-fold) | Target-encoding leakage | Fit inside each fold |
| Privacy | POS lines may carry customer IDs | Drop or irreversibly hash at extract; no customer-level modelling needed | Re-identification | Data-protection review |

**Target.** `demand[s,i,w]` = units that would have sold in week *w* with adequate availability. Phase-1 proxy: sales in non-censored weeks, with censored weeks masked from the loss. Evaluation uses *sales in in-stock weeks* for the accuracy metrics and the separate stock-out KPI for service. Exclusions: store-weeks closed, SKU weeks before listing, bulk B2B bills if separately identifiable [To investigate].

**Estimand distortion note:** masking censored weeks removes the weeks with the highest demand pressure (stock-outs plausibly cluster in high-demand weeks; to be checked in EDA), which biases forecasts down if not handled; this is why the unconstrained-demand experiment (stage E4, card EX6) is mandatory.

## 7. Feature & Target Design

| Feature group | Examples | Availability relative to the Monday order | Hypothesis |
|---|---|---|---|
| Own history | Lags (1,2,3,4,8,13,52 weeks), rolling means/std, zero-run length, weeks since last sale | Through previous Sunday | Level and trend |
| Seasonality/calendar | Week of year, month, month-end/pay cycle, school terms | Always known | Recurring patterns |
| Festivals | Days to/from festival, in-week fraction, festival type, state relevance, last-year same-festival uplift (computed from past years only) | Known in advance | Pre-festival ramp-up and post-festival drop |
| Promotions | Promo flag, depth, mechanic, display, prior-week promo, days since last promo; **as known at cut-off** | Only if frozen before order (Q2) | Promotion volume lift and post-promo dip (association, not causal lift) |
| Price | Shelf price, relative price vs category, discount depth | Planned prices known ahead; actuals not | Price association (not causal elasticity) |
| Availability | Past stock-out frequency, recent in-stock rate | Past only | Understanding censoring |
| Hierarchy/entity | SKU/brand/category, pack size, store cluster/state/format, shelf life | Static | Cross-series learning, cold start |
| External (optional) | Weather observed lag, local events | Per source | Category-specific |

New SKUs and stores: forecast with attribute-based analogues (same category/pack/price band; store cluster) until ≥ N weeks of history exist (N [TBD]).

## 8. Baseline Model Specification

| Baseline | Inputs | Protocol | Limitation | Role |
|---|---|---|---|---|
| B0 Current process: 4-week moving average of sales, scaled to protection interval | Last 4 weeks of sales at SKU×store | Re-implemented exactly as the planners do it (confirm any manual adjustments); evaluated in the same walk-forward backtest | May hide manual overrides not in the data | **Primary bar to beat** (forecast value added) |
| B1 Seasonal naive (same week last year) plus level adjustment | 52-week lag, recent level | Same protocol | Only 2 usable years; fails on moving festivals | Checks whether seasonality is worth modelling |
| B2 Moving average + festival/promo uplift factors by category | 4-wk average × category-level historic ratios | Same | Ratios estimated from few occurrences | Simple, explainable improvement that candidates must beat |
| B3 Tuned statistical per-series (ETS/TSB/Croston by velocity class) | Own history | Same | No cross-series learning | Strong classical benchmark |

**Bar for candidates (to be agreed with the client):** beat B0 on WAPE and bias over the protection interval, and beat B2/B3, across all rolling-origin windows and in the festival windows, by a pre-declared minimum margin [TBD with client], without worsening bias in the high-volume A-class items. No baseline numbers are assumed; they will be measured in E0/E1.

## 9. Candidate Algorithms & Prioritisation

| Priority | Algorithm | Why plausible | Assumptions/needs | Strengths | Weaknesses | Interpretability | Key hyperparameters | Reject if |
|---|---|---|---|---|---|---|---|---|
| 1 | Global gradient boosting (LightGBM-class), direct multi-horizon, quantile or Tweedie/Poisson-type objective | Large panel with rich covariates; handles promo/festival features; fast | Lags built point-in-time; feature panel | Learns across series; handles non-linearity; scalable to large panels | Quantile crossing; needs good lag features; weak for ultra-sparse series | Feature importance/SHAP (associative) | learning rate, num_leaves, min_data_in_leaf, feature/bagging fraction, regularisation, number of trees, quantile levels | Does not beat B2/B3 in the pre-declared windows or is unstable across folds |
| 2 | Statistical per-series: ETS/ARIMA for smooth items; Croston-SBA/TSB for intermittent | Strong, cheap benchmark; good for slow movers | Enough history per series | Robust, simple | No covariates (or limited); per-series noise | High | smoothing parameters, intermittency method | Used as a benchmark; kept for classes where it wins |
| 3 | Count/negative-binomial or hierarchical Bayesian model for sparse SKUs | Natural for low counts and uncertainty; pooling | Count data | Proper predictive distribution | Slower; harder to scale | Medium-high | priors, pooling levels | No gain over TSB/GBM on intermittent classes |
| 4 | Hierarchical reconciliation (MinT-style or top-down) over category/store/SKU | Coherent forecasts between levels, helps the sparse tail | Hierarchy defined | Reduces noise at SKU×store | Added complexity | Medium | reconciliation method, covariance estimator | No improvement on accuracy or coherence |
| Later | Deep global models (e.g. DeepAR/TFT-style) | Only if GBM plateaus and compute is available | GPU, tuning effort | Native probabilistic outputs | Hard to tune; data-hungry | Low | – | Not considered until Priority 1–4 are complete and a clear gap exists |

**Trade-off narrative.** With ~1.6M potential series and sparse tails, a global GBM paired with strong statistical models for slow movers is the most defensible starting point; it is also easy to deploy with Excel-like outputs. Deep models are costly and carry no guaranteed gain over a well-featured GBM on 3 years of weekly data.

**Model selection decision rule.** Choose per velocity class (not globally) the simplest model whose WAPE/pinball loss is better than B0/B2 by the pre-declared margin on paired rolling-origin comparison; prefer the simpler model when the difference is within the fold-to-fold noise band; require no worse bias in A-class items and no deterioration in festival windows; weight the final choice by operational cost (run time before Monday) and explainability for planners.

## 10. Metrics & Decision Criteria

| Tier | Metric | Definition | Why | Caveat |
|---|---|---|---|---|
| Primary | WAPE on the protection-interval demand | Σ\|forecast − actual\| / Σ actual, aggregated by class and across the portfolio | Volume-weighted; fits ordering | Dominated by large SKUs; report by ABC class and festival/non-festival |
| Primary (probabilistic) | Weighted pinball (quantile) loss at service-level quantiles | Mean of quantile loss at target quantiles (e.g. those implied by category service levels) | Orders use upper quantiles | Needs calibrated quantiles |
| Secondary | Bias (signed error %) | Σ(forecast − actual)/Σ actual | Systematic under/over | Can hide offsetting errors |
| Secondary | Forecast value added (FVA) | Error reduction vs B0 and vs B2 | Directly answers "better than what we do today" | Measure on identical windows |
| Secondary | Quantile calibration / coverage | Share of actuals below each predicted quantile | Trust in safety stock | Coverage shifts in festival weeks |
| Diagnostic | MASE/RMSSE | Scale-free across SKUs | Cross-SKU comparison | Unstable for ultra-sparse series |
| Diagnostic | Error by horizon, class, state, category, festival vs normal, promo vs non-promo, new SKUs | Slice analysis | Finds where it fails | Multiple slices → exploratory only |
| Business (pilot) | Stock-out rate / in-stock rate / fill rate (unit-level lost-sales proxy) | Stock-out SKU-store-days ÷ SKU-store-days on range | The stated goal | Needs Q1 data; definition must be fixed before pilot |
| Business (pilot) | Inventory days (weeks of cover), wastage/markdown on perishables | Stock ÷ demand rate | Guard against over-ordering | Compare at equal service |
| Rejected | MAPE / sMAPE | – | Unstable with zeros and intermittent demand | Do not use for SKU×store |
| Rejected | Accuracy at the SKU×store×week level alone | – | The decision is made over the protection interval | Report as diagnostic only |

**What is scored.** WAPE, bias and FVA use the P50 forecast of protection-interval demand; service quantiles (P-τ) are scored by pinball loss and coverage. B0–B3 are point forecasts, so for pinball comparison each gets an empirical-residual quantile band estimated on training windows only. Protection intervals that overlap stock-outs are scored with censored weeks masked at the weekly level, and the share of masked intervals is reported with every result; results on in-stock-only weeks are labelled as biased towards lower demand.

**Offline policy simulation (AN2).** Before the pilot, replay past weeks with the recommended order rule vs the B0-based rule, sampling lead-time variability from receipts (Q4) and using observed demand where uncensored, to estimate service level and inventory days with intervals. Results are model-based and are not proof of benefit.

**Decision rule / order recommendation.** Recommended order = max(0, Q_τ(protection-interval demand) − on-hand − in-transit), rounded to case-pack/MOQ, where τ = target service level for the category (e.g. higher for festival staples, lower for slow, perishable items). τ values are **[TBD with client]** and chosen using cost of a stock-out vs holding/wastage cost, then frozen before the pilot. Without on-hand data, the recommendation is a forecast quantile only.

## 11. Experiment Matrix & Tuning Strategy

| Stage | Purpose | Exit criterion |
|---|---|---|
| E0 Sanity | Data reconciliation, panel completeness, split harness, shuffle/leak tests | Totals reconcile; harness reproduces B0 |
| E1 Baselines | Measure B0–B3 on all windows | Baseline table stored; bar defined with client |
| E2 Simple candidates | Global GBM with core features; statistical models by class | Beats B0 on pre-declared margin or stop |
| E3 Feature ablation | Which data sources are worth it | Report with intervals |
| E4 Censoring treatment | Masking vs imputation vs censored loss | Choose on in-stock-week error and stock-out proxy |
| E5 Probabilistic/quantile | Calibrated service-level quantiles | Coverage within agreed tolerance |
| E6 Hierarchy/sparse tail | Reconciliation, pooling, cold-start | Gains on sparse classes |
| E7 Tuning | Hyperparameter search on survivors only | Gain beyond noise band |
| E8 Locked test + shadow | One-time test on held-out period; live shadow | Meets acceptance criteria |

| ID | Hypothesis | Change | Fixed conditions | Split | Metrics | Stopping rule |
|---|---|---|---|---|---|---|
| EX1 | The Excel process is replicable; our B0 matches planner behaviour | Implement B0 | Same data and windows | Rolling origin | WAPE, bias | Stop when B0 reproduces historical planner orders within a tolerance agreed in Discovery; if it cannot, document the gap and use the data-only B0 |
| EX2 | Seasonality and festival/promo uplift add value over B0 | B1, B2 | Same | Rolling origin + festival windows | FVA vs B0 | If B2 is within noise of B0, festival uplift is weak or mis-specified; investigate |
| EX3 | A global GBM beats B0/B2/B3 | LightGBM-class with core features | Same folds | Rolling origin | WAPE, pinball, bias | Stop if not better than B2/B3 by margin in ≥ agreed share of windows |
| EX4 | Festival features improve festival-window error | Add festival group | Same model, same folds | Festival-window backtests | WAPE in festival windows | Keep if gain exceeds noise band and non-festival error is not worse |
| EX5 | Promo information at order-time adds value; using final calendar overstates it | Promo (as-of cut-off) vs promo (final) | Same model | Rolling origin | WAPE promo weeks | Large gap = leakage warning; use as-of version only |
| EX6 | Masking censored weeks beats naive training; imputation may beat masking | Three censoring treatments | Same model | Rolling origin | In-stock WAPE; bias; stock-out proxy | Stop after the three treatments are compared on identical folds; adopt masking unless imputation reduces bias on high-demand weeks by more than the noise band, in which case adopt imputation |
| EX7 | Velocity-class routing beats a single model | Route intermittent to TSB/NB | Same | Rolling origin | WAPE and pinball by class | Keep if better on slow movers without hurting A-class |
| EX8 | Quantile forecasts achieve target coverage | Quantile objective or conformal calibration | Same | Rolling + festival windows | Coverage, pinball | Tolerance band [TBD]; recalibrate otherwise |
| EX9 | Reconciliation improves sparse series | Reconciliation on/off | Same | Rolling origin | WAPE on tail | Keep if gain > noise |
| EX10 | External weather/events add value for selected categories | Add features by category | Same | Rolling origin | Category WAPE | Drop if no gain; record cost of acquiring |

**Tuning.** Random search with early stopping first (cheap, wide), then Bayesian (e.g. Optuna-style with pruning) on survivors only; budget [TBD, e.g. a fixed number of trials/hours agreed after E2]. Priorities for GBM: learning rate × number of trees, leaf count/min data in leaf, regularisation, feature fraction; then quantile levels and loss-power for Tweedie. Tuning is done on the validation folds only (never on the locked test); tune once per velocity class.

**Reproducibility & tracking.** Fixed seeds, environment lockfile, immutable data snapshot with hash, versioned split definitions and feature code, config-driven runs, experiment tracker (MLflow or an equivalent versioned log), model card for each released version, test-set access log.

**Comparison protocol.** Identical folds and windows for every model; paired comparisons (block bootstrap over weeks, or Diebold–Mariano-type tests with HAC variance to handle overlapping multi-week windows) with a pre-declared minimum meaningful improvement; results reported with intervals, not just means.

## 12. Train / Validation / Test Design

**Deployment scenario.** Every Monday morning the system has POS data through the previous Sunday (latency [To investigate]), promotions as frozen by the cut-off, and known future festival calendar; it must output quantile forecasts for the protection interval for all active SKU×store series. Stores and SKUs are mostly returning; a minority are new. Hence the validation design is **temporal**, with some **grouped** checks for cold-start.

**Strategy**
- **Rolling-origin (walk-forward) backtest with weekly Monday origins** — estimates routine weekly performance, one origin per order Monday.
- **Festival-window backtests** — origins placed 1–10 weeks ahead of each past major festival, estimating performance exactly when stock-outs matter. Each is a separate stratum; results are reported per festival and not averaged with ordinary weeks.
- **Cold-start (grouped) check** — hold out a set of new SKUs and new stores (all history after listing) to evaluate analogue-based forecasts. Estimates behaviour for items with no history.
- **Locked final test** — the most recent block, containing at least one festival period if history allows, touched once, after the model and decision rule are frozen.

**Window specification (rules relative to the data end date, which is [To investigate])**

| Item | Specification |
|---|---|
| Forecast origins | Every Monday in the validation/test range |
| Horizons | h = 1–3 weeks (cumulative protection interval); 4–10 weeks for festival pre-build (aligned with §17) |
| Training window | Expanding for GBM (all history up to origin); sliding option tested for drift (E-series) |
| Retraining cadence tested | Weekly refit vs monthly vs quarterly (cost/benefit) |
| Gap/embargo | No gap needed for features built from data ≤ Sunday; target windows may overlap origins, so evaluation uses the window after the origin only; features are never computed with data after the origin |
| Data vintage | Point-in-time: promo calendar version as-of order date; POS as-of Sunday (late bills/returns handled as the system would have seen them) |
| Seasonal coverage | Validation must cover all months at least once; festival strata evaluated separately |
| Locked test | Latest ~13–26 weeks [TBD once data end date and festival positions are known], reserved before modelling; a shorter test leaves more training data for festival learning; at least one major festival should fall in validation or test |

```
time ->
|<------------- training (expanding) ------------->|<-- val origins (weekly) -->|<-- LOCKED TEST -->|
 start of history ...................................   ~26 wks             ~26 wks   (sizes provisional)
Festival backtests: origins 1–10 weeks before festival F(y-1), F(y-2)  [trained only on data before origin]
Cold-start check: new SKUs/stores held out as groups from first listing
```

**Promotion endogeneity:** promotions are chosen by the category team in anticipation of demand, so promo coefficients are associations; no lift claims are made (AN4 would need its own design).

**Known limitation:** with ~3 years, a backtest on a given festival is trained on 0–2 earlier occurrences of it (the earliest festival cannot be backtested). Results for festival windows are therefore high-variance; we report them with intervals and by festival, and rely on cross-SKU/store pooling and category-level festival indices to stabilise estimates.

**Split hygiene.** No random splits; all transformers (scaling, encoders, velocity classes, imputation, festival indices) fitted on training windows only; one frozen test; test-set access log; split definitions versioned; duplicates in POS removed before aggregation; no tuning on test.

## 13. Leakage Audit Checklist

| Risk | Applies? | Where it could occur in this case | Mitigation | Owner |
|---|---|---|---|---|
| Future promotions/prices as features | **Yes (high)** | Final or revised promo calendar used for past orders | As-of-cutoff promo versions; EX5 'final vs as-of' leak test | DS + category team |
| Target leakage via post-order information | Yes | Features using sales/stock after the Monday order (e.g. same-week sales) | Strict origin-based feature builder; unit tests on timestamps | DS |
| Preprocessing outside folds | Yes | Velocity class, scaling, festival indices, imputation computed on full history | Fit in-fold; recompute per origin | DS |
| Censoring / selective labels | Yes | Demand observed only when stocked; past recommendations influence stock | Availability flags; X6; monitor feedback loop | DS + supply chain |
| Last-year same-festival features | Yes | 'Last year uplift' computed using future years when backtesting | Compute only from years before the origin | DS |
| Retail-calendar misalignment | Yes | Moving festivals; 4-4-5 vs ISO weeks | Single calendar table; date-level tests | DS |
| Restated sales / returns | Yes | Returns netted after the fact change past targets | Use as-of snapshots or fixed lag for 'settled' sales | Client IT |
| New/discontinued item survivorship | Yes | Only items alive today appear in the master | Reconstruct SKU listing history; include delisted SKUs | DS + merchandising |
| Entity overlap across splits | Partly | Same SKU/store appears in train and test (expected for returning series) | Intended; cold-start check covers new groups | DS |
| Hierarchy reconciliation using future data | Possible | Reconciliation weights estimated with test residuals | Estimate from training residuals only | DS |
| Test-set reuse / tuning on test | Possible | Repeated looks at final block | Lock once; access log | DS lead |
| Store attributes updated after the fact (size, cluster) | Possible | Current store master applied to history | Use dated attributes | Client IT |
| Weather: observed vs forecast | If used | Using observed weather for the future week | Use forecast snapshot or lagged observed | DS |

**Robustness validations.** Time-slice stability; error by state, category, store cluster and velocity class; festival vs non-festival; promo vs non-promo; new vs established SKUs; target-shuffle sanity test; adversarial validation between training and latest period (drift); sensitivity to censoring treatment and to lead-time variation.

## 14. Statistical Inference & Causal Analysis Plan

Only the pilot (AN3) requires inference; this section is deliberately short.

- **Estimand:** the change in stock-out rate (and in inventory days) at pilot stores caused by using the new recommendations instead of the current process, over the pilot period.
- **Design:** matched-store (or staggered) pilot. Select treated stores and matched control stores by format, state, volume and pre-period stock-out trend; a randomised assignment across matched pairs is preferred if operations allow it; otherwise difference-in-differences with pre-period parallel-trend checks. Festival periods should be included for both arms.
- **Metrics (declared before launch):** primary = stock-out rate (SKU-store-days out of stock on range); guardrails = inventory days, wastage/markdown, sales value.
- **Analysis:** DiD/mixed-effects model with store and week effects; clustered standard errors by store; effect sizes with confidence intervals; practical-significance threshold [TBD with client].
- **Contamination/spillover:** treated and control stores sharing a DC or transferring stock can contaminate each other; pick controls on different DC routes where possible, record transfers, and run a sensitivity analysis excluding shared-DC pairs.
- **Power/MDE:** cannot be calculated without historic variance of the stock-out rate; compute from the pre-period data in Discovery and size the pilot (number of stores × weeks) to reach the agreed minimum detectable effect. Agreeing the improvement margin and MDE is an exit criterion of Phase 1.
- **Multiple testing:** one primary metric; guardrails reported descriptively or with correction; category-level slices exploratory.
- **What this can and cannot show:** it can show whether the new process reduced stock-outs in comparable stores. It cannot attribute effects to individual features, and the forecasting model's promotion coefficients cannot be read as promotion lift (that would need a separate design, AN4).

## 15. Robustness & Sensitivity Tests

- **Subgroups:** state, store format/size, category, ABC and velocity class, perishable vs shelf-stable.
- **Time slices:** each month; festival vs non-festival; pre/post major disruptions (price changes, store refits).
- **Stress scenarios:** supplier lead time increases by one week; promotion cancelled/added after the cut-off; a festival moving by a week; a supply shock to a key SKU; sudden new store.
- **Sensitivity:** to censoring treatment, to the service-level τ, to the lead-time assumption, to missing promo information (drop promo features and measure the loss).

## 16. Interpretability & Uncertainty

- **Explanations:** per-SKU forecast decomposition (baseline level, festival, promo, trend) for planners, from the model's feature contributions; labelled as *associations in the model*, not causes.
- **Uncertainty:** deliver P10/P50/P90 (and the ordering quantile) per series for the protection interval; calibrate quantiles on validation windows (conformal or empirical calibration), separately for festival weeks.
- **Communication:** a planner view with the current process value, the new forecast, the interval and a short associative note on which inputs were active (e.g. 'festival week and promo flagged in the inputs'; not a causal attribution), with colour flags for unusually wide intervals or low-confidence cold-start items.

## 17. Deployment & Monitoring Strategy

**Serving pattern.** Weekly batch scheduled after Sunday close: data refresh → feature build (point-in-time) → forecast → recommended order file/dashboard ready before the Monday cut-off, with a time buffer. Integration through the existing Excel/ERP ordering process initially (CSV/Excel + dashboard), automation later. Compute location: the client's environment [Assumed]; client data stays there.

**Human in the loop.** Planners may override; overrides require a reason code and are logged, so FVA (human vs model) can be measured. A rule-based fallback to B0 or B2 runs automatically if data checks fail or forecasts are missing.

**Rollout path.** (1) Shadow mode: forecasts produced alongside actual orders with no use; (2) pilot in matched stores/categories (A3); (3) staged scale-up by state/category; (4) full rollout. Festival seasons get a dedicated pre-festival review (category team reviews festival forecasts 8–10 weeks ahead with the DS team).

| Layer | Metric | Threshold | Action | Owner |
|---|---|---|---|---|
| Data quality | POS completeness by store, late files, duplicate rate | [TBD] | Block run, fallback to B0 | Data engineering |
| Data drift | Feature and target distribution shift (PSI or similar); new SKUs/stores share | [TBD] | Investigate; retrain trigger | DS |
| Prediction | Forecast distribution vs history; quantile crossing | [TBD] | Auto-correct/alert | DS |
| Accuracy | Weekly WAPE, bias, FVA vs B0 by class and category (actuals arrive within 1–3 weeks) | [TBD] | Alert; review; retrain | DS + planners |
| Calibration | Coverage of P90/service quantile | Tolerance [TBD] | Recalibrate | DS |
| Business | Stock-out rate, inventory days, wastage | [TBD] | Review settings (τ, rules) | Supply chain |
| Process | Override rate and FVA of overrides | [TBD] | Planner feedback; tune UI | Supply chain |

**Retraining, rollback and post-deployment evaluation.** Refit weekly or monthly depending on E-series results; full retrain/review quarterly and before each festival season; triggers include persistent bias, coverage failure, drift alerts, structural events (new states, store clusters). A new version is promoted only after champion–challenger shadow comparison and approval; rollback to the previous version or B0 if accuracy worsens beyond tolerance. Post-launch impact is evaluated through the pilot design (§14), then through retained control stores or holdout categories.

**Governance.** Data stays in client environment; remove customer identifiers from modelling data; access controls and audit logs; model documentation and a model card per version. Regulatory orientation (confirm with client compliance/legal): India's DPDP Act 2023 for any personal data. Aggregate store-level forecasting itself carries low personal-data exposure.

## 18. Risks, Mitigations, Dependencies & Open Decisions

| Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|
| No usable availability/stock data (Q1) | Medium | High | Zero-run heuristic; start capturing snapshots now; limit claims about stock-out reduction | Client IT / DS |
| Historic promo versions missing (Q2) | Medium | High | Use only promos known ≥N weeks ahead; run leak test EX5; request versioning going forward | Category team |
| Only 2–3 occurrences per festival | High | High | Pooling across SKUs/stores/festivals; category festival indices; planner judgement overlay for festival peaks; report intervals | DS |
| Forecast gains don't translate to fewer stock-outs (supplier constraints, shelf execution, store ordering behaviour) | Medium | High | Pilot with business metrics; track fill rate from suppliers; separate forecast error from execution | Supply chain |
| Planner adoption low | Medium | High | Co-design, explainable outputs, measure FVA of overrides | Sponsor |
| Compute/time window before Monday cut-off | Medium | Medium | Class-based modelling, incremental refresh, fallback to B0 | Data engineering |
| Cold-start items/stores (new launches) | High | Medium | Analogue forecasts; planner input for launches | DS |
| Cannibalisation/halo between SKUs and substitution when out of stock | Medium | Medium | Category-level reconciliation; treat as limitation; consider later | DS |
| Data privacy/regulatory | Low | Medium | Drop customer identifiers; compliance review | Client legal |
| Time-sensitivity: the autumn festival season may arrive before the model is ready | High | High | Interim rule (B2-style festival uplift by category using last years' ratios, reviewed by category managers) in a quick-win track | DS + category team |

**Open decisions:** target service levels by category; order grain (store vs DC); override policy; pilot store selection; tools/platform.

## 19. Phased Implementation Roadmap

*Effort ranges are provisional; they assume a small team (1 DS lead, 1–2 DS/ML engineers, 1 data engineer, part-time planner/category SME) and an unknown client stack.*

| Phase | Work package | Dependencies | Deliverables | Acceptance criteria | Indicative effort (provisional) |
|---|---|---|---|---|---|
| 0 Quick win | Interim festival rule for the imminent season (fast POS extract by category×state×week; category-head review) | Read access to POS history in week 1; sanity backtest on prior festivals | Category-level festival uplift table and process note | Reviewed and approved by category heads; limitations documented | 1–2 weeks |
| 1 Discovery | Resolve Q1–Q7; data profiling; metric & service-level agreement; reconstruct B0; pilot design | Access to data and stakeholders | Data readiness report; agreed KPI/targets; baseline definition | Q1/Q2 answered or contingency chosen; B0 reproducible; improvement margin and pilot MDE agreed | 3–4 weeks |
| 1b Contingency (if Q1 or Q2 is 'no') | Start daily stock-snapshot and promo-version capture immediately; build zero-run availability proxy; restrict promo features; label proxy-based stock-out KPI as uncalibrated | Phase 1 findings | Capture jobs; proxy validation on any overlapping stock data | Capture running before modelling starts; limitations documented | 2–4 weeks in parallel; capture needs time to accumulate |
| 2 Data engineering | Panel, calendars, festival mapping, availability flags, point-in-time promo store, feature pipeline | Phase 1 | Versioned datasets and pipeline | Reconciliation to finance totals; timestamp unit tests pass | 5–8 weeks |
| 3 Analysis/EDA | Quality checks, event studies, velocity classes, festival indices | Phase 2 | EDA report and data-quality log | Issues triaged; assumptions updated | 2–3 weeks (overlaps Phase 2) |
| 4 Modelling | E1–E7 experiments | Phases 2–3 | Experiment log, candidate model(s), decision rule | Pre-declared margin over B0/B2/B3 or documented stop | 6–10 weeks |
| 5 Validation | Locked test; festival backtests; robustness; shadow run | Phase 4 | Validation report; model card | Acceptance criteria agreed in Phase 1 met | 3–4 weeks |
| 6 Deployment & pilot | Batch pipeline, planner UI/file, overrides, pilot in matched stores; the earliest pilot window likely misses the autumn festival season, so aim to cover the next major festival | Phase 5 | Production pipeline; pilot results | Run completes before cut-off; pilot readout with CIs | 8–12 weeks |
| 7 Monitoring | Dashboards, alerts, retraining runbook, quarterly review | Phase 6 | Monitoring and governance pack | Thresholds agreed; owners named | Ongoing |

## 20. Decision Log

| # | Decision/Recommendation | Rationale | Alternatives considered | Key assumptions | Risk | Validation method |
|---|---|---|---|---|---|---|
| D1 | Forecast unconstrained demand, not sales | Sales understate demand in stock-outs | Forecast sales as-is | Availability data or reliable proxy | Imputation bias | E4 / EX6 |
| D2 | Probabilistic forecast over protection interval | Ordering depends on tail and window | Point forecast + fixed safety stock | Lead-time data | Calibration | EX8; coverage |
| D3 | Baseline = reproduced 4-week MA (B0), plus B1–B3 | Meaningful bar; client's own process | Quoted accuracy figures | Replicable from data | Manual overrides invisible | EX1 |
| D4 | Global GBM first, statistical models by velocity class | Scale and sparse tail | Deep learning first | Feature panel feasible | Overfit | Rolling-origin comparison |
| D5 | Weekly-origin rolling backtest + festival strata + locked test | Mirrors Monday process | Random k-fold | Dates reliable | Few festival repeats | Variance reporting |
| D6 | Promo features only as known at cut-off | Avoid future leakage | Use final calendar | Versions retrievable | Weaker features | EX5 |
| D7 | WAPE/pinball/bias/FVA; reject MAPE | Intermittent, volume-weighted | MAPE, accuracy at row level | – | Metric gaming | Class slices |
| D8 | Stock-out benefit proven via pilot (DiD/matched stores) | Backtest ≠ business impact | Before/after comparison | Pilot feasible | Contamination | §14 |
| D9 | Planner-in-the-loop with fallback | Adoption, safety | Full automation | Planners available | Over-trust/under-trust | Override FVA |
| D10 | Interim festival rule while model is built | Season timing | Wait for model | Category input | Rule inaccuracy | Compare vs actual after season |

## Glossary and value framing

- **WAPE:** weighted absolute percentage error (total absolute error ÷ total actual demand).
- **FVA:** forecast value added: how much better the new forecast is than the current process.
- **Pinball loss:** error measure for quantile (percentile) forecasts.
- **Protection interval:** lead time + review period, the time one order has to cover.
- **ADI/CV²:** statistics classifying demand as smooth, erratic, intermittent or lumpy.
- **TSB/Croston:** methods for products that sell sporadically.
- **MinT/reconciliation:** adjusts forecasts so SKU, store and category totals agree.
- **PSI:** population stability index, a drift measure.
- **DiD:** difference-in-differences, comparing changes in pilot vs control stores.

**Value framing.** Value is avoided lost sales and wastage net of holding cost, to be estimated from category margins and measured in the pilot; no value estimate is made here.

## 21. References

None consulted for this draft; no external sources were relied on. Festival dates for the upcoming season and any regulatory references (DPDP Act 2023 requirements) are **to be verified** before client release.
