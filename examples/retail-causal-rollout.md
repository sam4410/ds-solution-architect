---
title: Personalised Offers Feature — Causal Impact & Rollout Decision — Data Science Solution Plan
client: National apparel retailer (name TBD)
industry: Retail
prepared_by: Data science solution architecture team
date: 2026-10-14
version: 0.1 (draft)
depth: Standard
classification: Confidential
---

# Personalised Offers Feature — Causal Impact & Rollout Decision — Data Science Solution Plan

## 1. Executive Summary
- **Decision:** Should the loyalty-app "personalised offers" feature be rolled out to all 220 stores, and can the CMO claim the feature "caused a 7-point lift"?
- **Plain-language problem:** Stores with the feature grew 12% year-on-year and stores without it grew 5%. The 7-point gap (12 − 5) is a *comparison*, not yet a *causal effect*. The 40 treated stores were chosen by regional managers and are mostly larger metro stores, so they may have been growing faster anyway. The gap mixes the feature's effect with the effect of *which stores were picked*.
- **Lens:** Causal (primary), with an Inferential component (uncertainty, practical significance). A predictive model is **not** the right tool for the causal question; a predictive/uplift component is optional later for targeting.
- **Recommended approach:**
  1. **Do not publish "caused a 7-point lift" now.** The defensible current statement is "treated stores grew 7 points faster than untreated stores; the share due to the feature is not yet established."
  2. **A1, retrospective analysis:** estimate the effect with a difference-in-differences / synthetic-control style design on weekly store-level data, using the pre-launch period to test whether treated and comparison stores were on parallel trends. Report an effect with confidence interval and sensitivity analysis, and state plainly if the data cannot support a causal claim.
  3. **A2, forward experiment (planned 26–52 weeks, about 36–66 weeks end to end):** because 180 stores are still untreated, run a randomised store-level rollout (cluster-randomised or stepped-wedge) so the rollout decision rests on randomised evidence. This is the only design that fully removes the selection problem.
  4. **Decision rule agreed in advance:** roll out if the lower confidence bound of net incremental margin per store-week (offer and running cost already deducted) is above zero and above the minimum worthwhile effect (`[TBD with client]`); the randomised pilot (A2) governs if it disagrees with the retrospective estimate.
- **What must be true:** weekly store-level sales (and ideally margin) for at least 2 years before launch are available; the launch dates and the store-selection process are documented; no other major initiative hit the treated stores at the same time; the client can randomise some of the 180 untreated stores.
- **Top risks:** selection bias (larger metro stores); co-occurring changes (regional campaigns, new store formats, price changes); spillover between stores sharing customers; novelty effect at six months; sales vs margin (offers may buy revenue with discounts).
- **Next steps:** see "Needed from the client next".

> **Needed from the client next:**
> 1. Weekly store × category sales, margin and discount data for ≥ 24 months pre-launch to now, plus the store master (size, format, metro/non-metro, region, opening date). *(Owner: BI / Finance.)*
> 2. Exactly how the 40 stores were chosen and the launch date per store (single date or staggered?). *(Owner: regional managers / CMO office.)*
> 3. A list of other initiatives, price changes, refits, openings or closures across the whole pre-period and since launch, for all 220 stores. *(Owner: Marketing & Operations.)*
> 4. Whether loyalty sales can be tracked separately from non-loyalty sales and whether app users existed before the feature. *(Owner: CRM / Loyalty product.)*
> 5. Whether randomising the next stores is acceptable, the earliest start date, and the cost per store of enabling the feature. *(Owner: CMO / COO.)*

### Scope of this plan
This plan covers two analyses: A1 (retrospective effect estimate for the 40 treated stores) and A2 (forward randomised rollout). The full causal and statistical design is in scope. Data needs are covered only to the extent the causal designs require. There is no deployed model, so model serving is limited to the decision rule and post-launch evaluation (§17). Validation is described as design windows (§12).

| Section | Status |
|---|---|
| §1–5 | Included |
| §6 Preprocessing | Included, short (causal panel preparation only) |
| §7 Feature & target design | Included, short (outcome and covariate definition) |
| §8–9 Baselines, algorithms | Omitted: no predictive model is the objective. A predictive/uplift model is deferred to a later phase (§20, D9). The comparators A1 must beat are in §10 |
| §11 Analysis cards | Included in place of an experiment matrix and tuning plan |
| §10 Metrics | Included (outcome metrics rather than model metrics) |
| §12 Validation | Included (design windows, not model splits) |
| §13 Leakage audit | Included, as bias/contamination audit |
| §14–15 | Included (core of this plan) |
| §16 Interpretability | Omitted: no model; uncertainty reporting is covered in §14 |
| §17–21 | Included |

## 2. Business Problem & Decision Framing

| Element | Definition for this case | Status |
|---|---|---|
| Decision | (a) What can be publicly/internally claimed about the feature's impact; (b) roll out to all 220 stores or not (or in what order) | [Confirmed] |
| Decision owner | CMO | [Confirmed] |
| Timing | Rollout decision pending; launch was about 6 months ago | [Confirmed] |
| Action space | Roll out to all / roll out in waves / stop / continue current 40 only / redesign | [Assumed] |
| Capacity | Cost and effort of enabling a store, and number of stores per wave | [TBD with client] |
| Unit of analysis | Store × week (panel) | [Assumed] |
| Population | 220 stores: 40 treated, 180 untreated | [Confirmed] |
| Outcome (primary) | Weekly sales; **incremental gross margin after offer cost** is preferred for the decision | Sales [Confirmed]; margin [To investigate] |
| Observation window | Pre-launch ≥ 24 months, post-launch about 26 weeks | [Assumed] |
| Estimand (A1) | ATT: average effect of the feature on weekly net margin (and secondarily sales) in the 40 treated stores over the post period | [Assumed] |
| Estimand (A2) | ATE: average effect of enabling the feature in a typical store among the 180 not yet treated | [Assumed] |
| Cost of errors | False "yes" → rolling out a feature that costs money/discounts with no real lift and public claim that cannot be defended. False "no" → forgoing a real gain | [Assumed] |
| Success criteria | Net margin effect CI lower bound above zero **and** above the minimum worthwhile effect `[TBD with client]` | [TBD with client] |
| Constraints | Consumer-data and marketing-consent rules (DPDP Act 2023 and Rules, if India; confirm jurisdiction); fairness of personalised offers | [To investigate] |

## 3. Analytical Problem Classification
- **A1, retrospective causal effect on the 40 treated stores.** Causal lens, observational data with non-random assignment. Formulation: difference-in-differences (DiD), with synthetic control / matched comparison as cross-checks.
- **A2, forward rollout decision.** Causal lens, experimental. Formulation: store-level cluster-randomised trial or stepped-wedge rollout among the 180 untreated stores.
- **A3 (optional, deferred), who benefits.** Heterogeneous effect / uplift analysis, run only on randomised data from A2.
- **Alternatives considered:** (i) the raw 12% vs 5% comparison (rejected: ignores selection); (ii) regression adjusting for store size and region (kept only as a secondary estimate: it relies on no unmeasured confounding); (iii) a predictive model of sales with "treated" as a feature (rejected: feature importance is not a causal effect); (iv) customer-level randomisation inside stores (better statistical power, but app-level randomisation may be possible and is worth checking, see Q8 below, because store-level randomisation has few units).

> **Note:** "7-point lift" arithmetic: 12 − 5 = 7 percentage points. This is derived only from the brief and is the *naive difference*; relative growth ratio 1.12 / 1.05 − 1 ≈ 6.7%. Neither is a causal estimate.

## 4. Assumptions, Unknowns & Client Clarification Questions

| ID | Statement | Type | Impact if wrong | Owner | Needed by |
|---|---|---|---|---|---|
| F1 | 40 of 220 stores have the feature; ~6 months live | Fact | — | CMO office | — |
| F2 | Treated stores were chosen by regional managers, mostly larger metro stores | Fact | Selection bias is the central threat | CMO office | — |
| F3 | Treated +12% YoY vs untreated +5% YoY | Fact (as reported) | Definition of "sales" (like-for-like? gross? net of returns?) changes the number | BI | Week 1 |
| AS1 | Sales means net sales of comparable (like-for-like) stores | Assumption | If new/closed stores are included, growth rates are distorted | BI | Week 1 |
| AS2 | The feature launched on one date in all 40 stores | Assumption | Staggered launch requires staggered-DiD estimators | Loyalty product | Week 1 |
| AS3 | Weekly store-level data with ≥ 24 months pre-launch exist | Assumption | Fewer pre-periods weaken the parallel-trends test | BI | Week 2 |
| AS4 | No other store-specific initiative coincided with the launch | Assumption | Effect would be mis-attributed | Marketing / Ops | Week 2 |
| AS5 | Untreated stores did not receive the offers (no contamination) | Assumption | Bias toward zero | Loyalty product | Week 2 |
| AS6 | Randomising some of the 180 untreated stores is operationally acceptable | Assumption | Fall back to quasi-experimental rollout design | CMO / COO | Week 2 |
| Q1 | How were the 40 stores chosen (criteria, e.g., "most digitally active", "best managers")? | Open (blocking) | Determines how credible the comparison is | Regional managers | Week 1 |
| Q2 | Are margin, discount cost and offer cost recorded per store-week? | Open (blocking) | Sales lift without margin may be a loss. Fallback if unavailable: sales effect × an agreed margin rate and cost per store, labelled as an approximation | Finance | Week 2 |
| Q3 | Other initiatives, price changes, refits, openings/closures over the whole pre-period (≥ 24 months) to now? | Open (blocking) | See AS4 | Marketing / Ops | Week 2 |
| Q4 | Can loyalty / app-user sales be separated from other sales; how many app users per store before the launch? | Open (blocking) | Allows mechanism checks and a better-targeted outcome | CRM | Week 2 |
| Q5 | Acceptable pilot size/duration (a full seasonal cycle is preferred, see §14.4), cost per store, earliest start | Open (blocking) | Sets design and power | CMO / COO | Week 2 |
| Q6 | (Blocking) What is the minimum effect (in currency units of margin per store per week) that justifies rollout, and is the running cost per store a weekly or one-off amount? | Open (blocking) | Defines practical significance | CMO / Finance | Week 2 |
| Q7 | Are stores geographically close enough that customers visit both a treated and an untreated store? | Open | Spillover / interference | Operations | Week 2 |
| Q8 | Can the app randomise offers at customer level within a store (holdout of personalisation)? | Open | Offers a higher-power design | Loyalty product | Week 2 |

## 5. Data Inventory & Feasibility Assessment

| Source | Business meaning | Grain / keys | Point-in-time? | Quality risks | Status |
|---|---|---|---|---|---|
| Store sales (POS) | Net sales per store | Store × day/week | Yes | Returns restated; calendar alignment (retail calendar vs ISO weeks, moving festivals) | Sales totals [Confirmed]; weekly history [Assumed] |
| Margin and discount data | Profitability after offers | Store × week (or line-level) | Yes | May not capture offer cost | [To investigate] |
| Store master | Size, format, metro flag, region, opening date, refits | Store | Static + change log | Refits and openings are structural breaks | [Assumed] |
| Loyalty-app data | App users, offer issue and redemption | Customer × event | Yes | Self-selection of app users; privacy and consent | [To investigate] |
| Store-selection record | Why/when each treated store was chosen and launched | Store | Yes | May be informal | [To investigate] |
| Initiative / promotion calendar | Other campaigns, price changes, events | Store/region × date | Yes | Incomplete | [To investigate] |
| External | Holidays and festivals (national and regional), weather, local events, catchment demographics | Date × region | Yes | Moving-festival alignment | [To investigate] |

**Privacy, owners and refresh:** Each source needs a named data owner and refresh cadence (to be filled in Discovery). Loyalty-app and offer data are personal data: confirm consent basis, purpose limitation, data residency and who approves access (Legal / DPO). Store-level aggregates are preferred so that customer-level data need not leave its environment.

**Feasibility verdict:** A1 is feasible **only if** weekly pre-launch store data and launch dates exist (Q1–Q4); even then the credibility depends on the parallel-trends diagnostics, which could fail. A2 is feasible if the client accepts randomisation (AS6). **Blocking dependencies:** Q1, Q2, Q3, Q4, Q5, Q6. A blocking question may be closed only by an answer or by a labelled assumption signed off by the CMO office.

## 6. Data Quality & Preprocessing Plan

| Step | Rationale | Method | Risk | Validation check |
|---|---|---|---|---|
| Build like-for-like store × week panel | Growth rates are distorted by openings, closures, refits | Exclude or flag stores with structural breaks; use the same calendar for all stores | Excluding stores changes the population | Compare included vs excluded store profile |
| Align to retail calendar and festivals | YoY and seasonality comparisons need matched weeks | Map each week to its festival/event flags | Misalignment of moving festivals | Spot-check festival weeks in both years |
| Remove stock-out distortion | Sales ≠ demand when out of stock | Use availability flags where available; sensitivity analysis excluding stock-out weeks | Missing availability data | Compare effect with and without flagged weeks |
| Define outcome scale | Level differences between large and small stores | Use log sales or sales indexed to each store's own pre-period mean | Index base choice | Re-run with both specifications |
| Missingness and outliers | Single weeks can dominate | Document; winsorise only as a pre-declared sensitivity check | Hiding genuine effects | Report results with and without |

## 7. Feature & Target Design
- **Primary outcome (A1 and A2): incremental gross margin per store-week, net of offer and running cost**, in currency units, estimated on the level scale (margin can be negative, so no log transform). [To investigate: Q2.] If margin is unavailable, the fallback primary is the sales effect converted with an agreed margin rate (labelled as an approximation).
- **Secondary outcomes:** log weekly net sales (reported as a % effect), transactions, average basket value, loyalty-member share of sales, discount depth, and return rate.
- **Guardrails:** margin rate, return rate, and sales in neighbouring untreated stores (spillover).
- **Covariates (all measured before launch):** store size, metro flag, region, format [Assumed available]; catchment demographics, stock availability flags, pre-period app-user share [To investigate]; pre-period sales level and trend [Assumed]. No post-launch variable is used as a control (post-treatment variables may be mediators).

## 10. Metrics & Decision Criteria

| Tier | Metric | Definition | Why | Caveat |
|---|---|---|---|---|
| Primary | Incremental margin per store-week net of offer and running cost (A1: ATT; A2: ATE) | Difference in change of margin (level scale), treated vs comparison, with CI | The decision-relevant quantity | Needs margin and cost data (Q2); fallback in §7 |
| Secondary | Log weekly net sales | Difference in change of log sales, with CI | Comparable across store sizes; % effect for communication (convert to currency using store baseline sales) | Relative estimand |
| Secondary | Transactions, basket value, loyalty share | As named | Mechanism | Exploratory unless pre-registered |
| Comparator | Naive difference and covariate-adjusted regression | 12 − 5 = 7 points; regression with pre-launch covariates | A1 must be shown next to these so the size of the selection bias is visible | Neither is causal |
| Diagnostic | Pre-trend (event-study) coefficients; standardized mean differences (SMD); sample-ratio mismatch (SRM) | See §14 | Tests of design validity | A failed test invalidates the causal reading, not the data. Pass thresholds are conventions to be agreed in Discovery (§11 gate) |
| Business | Rollout payback | Cost to enable all remaining stores vs lower CI bound of incremental margin | Go/no-go | Thresholds `[TBD with client]` |

**Decision rule (proposed, to be agreed with the CMO before analysis):** The rollout decision is driven by A2 (randomised, applies to the stores not yet treated); A1 supports statements about the 40 treated stores. If A1 and A2 disagree, A2 governs and the gap is reported as an estimate of selection bias. The primary margin already includes offer and running cost, so: roll out broadly if the 95% CI lower bound of incremental margin per store-week is above zero and above the minimum worthwhile effect from Q6 `[TBD with client]`; roll out in waves with continued measurement if the CI includes both beneficial and break-even values; do not roll out if the CI's upper bound is below the minimum worthwhile effect. **Fallback if A2 is not approved or fails:** the decision uses A1 only if its diagnostics pass, as a staged rollout in waves with continued measurement; otherwise it is labelled a judgement call with no causal evidence.

## 11. Analysis Cards & Reproducibility
No hyperparameter tuning is planned. The analyses are specified as cards so they can be run and audited.

| ID | Hypothesis | Specification | Fixed conditions | Window / split | Metrics | Stopping / pass rule |
|---|---|---|---|---|---|---|
| C1 (A1) | Treated stores' margin changed differently from comparison stores after launch | Primary: DiD on the level-scale margin with store and week effects, store-clustered SEs | Covariates, store exclusions and outcome definition frozen in the analysis plan | Pre-period split into fit (earlier) and held-out (last N weeks, N agreed in Discovery); post-period effect window | Primary margin effect with CI; log-sales effect | Diagnostics pass rule: event-study pre-launch coefficients jointly consistent with zero and held-out fit error within a tolerance agreed in Discovery. If it fails, report A1 as descriptive only |
| C2 (A1) | Same, with better-matched comparison | Fallback ladder in order: synthetic control, then matched DiD, then store-specific trends, then weighting | Same as C1; ladder order fixed before looking at post-launch results | Same | Same | Stop at the first rung whose diagnostics pass; report all rungs |
| C3 (A2) | Enabling the feature changes margin per store-week | Stepped-wedge (or parallel-arm) with stratified randomisation; store and week effects, cluster-robust inference | Randomisation seed and strata recorded; primary outcome and decision rule pre-registered | Pilot of 26–52 weeks planned (§14.4); interim read at 26 weeks | Primary margin effect with CI; guardrails | Interim looks only under a group-sequential alpha-spending plan fixed at design (boundaries from the design software, not set here); stop early for guardrail breach |

**Reproducibility:** freeze a versioned data snapshot per run, keep analysis code in version control with the commit hash recorded in each report, store the pre-registered plan with a time stamp, fix random seeds, and log every specification tried.

**Protecting the plan from what is already known:** the headline growth figures (12% and 5%) have already been seen. The specification, covariates and fallback order are therefore fixed from the pre-period and design considerations only, and the weekly post-launch outcome series are not examined until the analysis plan is signed off. This limits, but does not eliminate, the risk of a specification chosen to fit the result.

## 12. Train / Validation / Test Design (design windows)
No predictive model is fitted, so there is no train/test split. The analogous windows are:
- **Pre-period:** from 24 months before launch up to the launch date; the earlier part is used for parallel-trends testing and for fitting synthetic-control weights, and the last N weeks (N agreed in Discovery) are held out to check that the fitted comparison tracks the treated stores out of sample. Do not use post-launch data to choose donors, controls or specifications.
- **Post-period:** launch date to data cut-off; the effect window. Report effect by month (event study) to separate novelty from steady state.
- **Placebo windows:** fake launch dates inside the pre-period to show the method returns about zero when nothing happened.
- **Pilot (A2):** a pre-registered analysis plan, frozen before randomisation.

## 13. Bias & Contamination Audit

| Risk | Applies? | Where it could occur | Mitigation | Owner |
|---|---|---|---|---|
| Selection bias (non-random store choice) | **Yes, high** | Regional managers picked mostly large metro stores; may also have picked stores already improving | Pre-trend tests, matching/synthetic control, randomised A2 | DS |
| Confounding by co-occurring initiatives | Likely | Regional campaigns, refits, price moves | Initiative calendar (Q3); exclude affected stores; sensitivity | Marketing / DS |
| Regression to the mean | Possible | If stores were chosen after a weak/strong period | Use long pre-period; check selection timing | DS |
| Different growth drivers in metro vs non-metro | Likely | Metro recovery, footfall, tourism | Compare within metro / size strata; include store-specific trends | DS |
| Spillover (SUTVA violation) | Possible | Customers using both treated and untreated stores; app users switching stores | Distance-based exclusion buffers; guardrail on neighbouring stores | DS |
| Contamination of controls | Possible | App features available to all users regardless of store | Verify with Loyalty product (AS5) | Loyalty product |
| Post-treatment control variables | Avoid | Using post-launch traffic or app use as a control | Controls limited to pre-launch values | DS |
| Novelty effect | Possible | Six-month window | Event-study by month; extend the pilot | DS |
| Anticipation | Possible | Stores prepared, staff briefed or customers messaged before the official launch date | Get the first-activity date per store; drop or model the ramp-up weeks | Loyalty product |
| A2 pilot contaminating A1 controls | Yes if overlapping | Both use the 180 untreated stores | Complete A1 or freeze its control set before pilot randomisation; document which stores are in which role | DS |
| Researcher degrees of freedom | Yes | Many specifications | Pre-register the primary specification; report all | DS lead |
| Calendar and YoY artefacts | Yes | Base-year anomalies (e.g., festival timing, base-year disruption) | Use week-matched panel; compare against 2 prior years | BI |

## 14. Statistical Inference & Causal Analysis Plan

### 14.1 Estimands and hypotheses
- **A1 estimand:** ATT on weekly net margin (and, secondarily, log sales) among the 40 treated stores, post-launch window.
- **A2 estimand:** ATE on weekly net margin of enabling the feature among comparable currently untreated stores, over a pilot window of at least one full business cycle.
- **Hypotheses:** H₀: the effect on net margin is zero. H₁: it is non-zero (two-sided, because harm through discounting is plausible). α = 0.05 for the primary outcome. Because the decision is about exceeding a minimum worthwhile effect δ (Q6), the primary decision uses the 95% CI of the effect against δ (equivalently a test of H₀: effect ≤ δ), not the zero-effect test alone.
- **Scale:** the primary effect is in currency units of margin per store-week. Relative (log sales) effects are converted to currency using each store's baseline sales for communication.

### 14.2 Causal diagram (text) and threats
- Store size / metro status / regional economy / manager quality → (a) *selection into treatment* and (b) *sales growth*. This is the main confounding path and it is open in the raw comparison.
- Feature → offers redeemed → basket and visit frequency → sales (mediators; not adjusted for when estimating the total effect).
- Other initiatives → sales (a confounder if correlated with treatment).
- Neighbouring-store customers → spillover (interference).

### 14.3 A1 design and estimator

| Question | Design / estimator | Key assumptions | Checks | Fallback |
|---|---|---|---|---|
| Effect on the 40 treated stores | Two-way fixed-effects DiD on store × week log sales, store-clustered SEs. If launches are staggered, use a heterogeneity-robust estimator (Callaway–Sant'Anna or Sun–Abraham type) | Parallel trends conditional on covariates; no anticipation; no interference | Event-study plot with pre-launch coefficients near zero; placebo launch dates; placebo outcome (a category or channel unlikely to be affected) | Add store-specific linear trends, or restrict to a matched comparison set |
| Same, with a more credible comparison | Synthetic control / synthetic DiD: weighted untreated stores that reproduce each treated store's (or the treated group's) pre-launch trajectory | Good pre-period fit; donors unaffected | Pre-period fit (RMSPE), placebo-in-space (apply the method to untreated stores), leave-one-donor-out | Matched DiD on size, region, pre-trend |
| Observational adjustment | Propensity weighting / doubly robust estimation with pre-launch covariates | No unmeasured confounding; overlap | Standardized mean differences after weighting below a conventional threshold such as 0.1 (to be agreed); overlap plots; trimming | Report as "associated with" only |
| Robustness | Restrict to metro-only (treated vs untreated metro); restrict to size-matched stores | Overlap exists within the stratum | Compare estimates across strata | — |

**Sensitivity analysis:** report a bound on how far parallel trends could be violated before the conclusion changes (Rambachan–Roth style, if supported by the software), the effect under store-specific trends, and the placebo-in-space distribution. An E-value is not used because it is defined for risk and odds ratios, and the mapping to a DiD margin effect is not straightforward. Previously mentioned: a Rambachan–Roth style "how much would parallel trends need to be violated" bound if event-study software supports it.

**Inference:** cluster standard errors at the store level; with 40 treated stores, use wild-cluster bootstrap or randomisation inference as a check; compare to a permutation distribution built from placebo assignments among the 180 untreated stores.

### 14.4 A2 design (forward experiment)

| Option | Description | Pros | Cons |
|---|---|---|---|
| **Stepped-wedge (recommended if rollout to all is the intent)** | Randomise the order in which the 180 untreated stores receive the feature across several waves; stratify by metro/non-metro, size band and region | Everyone eventually gets the feature; every store is its own control pre-switch; supports ATE | Needs a time-trend model; effects confounded by time if misspecified; longer to finish |
| **Parallel-arm cluster randomisation** | Randomly assign k of the 180 stores to treatment and the rest to control for the pilot window | Simplest to analyse | Control stores wait; fewer treated stores |
| Customer-level holdout (if Q8 yes) | Randomise customers within store to receive personalised vs generic offers | Much higher power; captures offer effect directly | Measures within-store effect only; spillover within the store; may not capture store-level traffic effect |

Design elements: randomisation unit = store (or customer if Q8); analysis unit = store-week with cluster-robust inference; stratified (blocked) randomisation on metro flag, size band, region and pre-period sales trend; pre-registered primary outcome, guardrails, planned duration 26–52 weeks (the minimum is set by the simulation in §14.5): an interim read at 26 weeks under the alpha-spending plan, and a full-year read to cover seasonality and show novelty decay, with the final length fixed at design; sample-ratio and balance checks; no peeking without a group-sequential or alpha-spending plan; pre-period covariate adjustment (CUPED-type) to reduce variance.

### 14.5 Power / MDE
Power in a store-randomised design is driven by the **number of stores** (units), not the number of transactions. The relevant inputs are: α, power, the between-store variance of the outcome change, the weekly autocorrelation of store sales, the number of waves/weeks, and the proportion of variance explained by pre-period covariates. With a fixed number of clusters, the approximate relation is

MDE ≈ (z₁₋α/₂ + z₁₋β) · SE(θ̂), where SE(θ̂) is estimated from the pre-period data by simulation.

**No numeric σ, ICC or MDE is stated here.** Plan: a simulation-based power analysis using the actual 24-month pre-period panel (re-assigning placebo treatment to stores, injecting a range of effect sizes, and recording rejection rates) to report the MDE for candidate pilot sizes among the 180 untreated stores. The sample is bounded by the numbers in the brief: 40 treated and 180 untreated stores (40/220 ≈ 18.2% treated). If the achievable MDE is larger than the effect worth detecting (Q6), the plan will state "pilot is under-powered" and consider the customer-level design (Q8), longer duration, or more waves.

### 14.6 Multiple testing and pre-registration
One primary outcome (margin; sales as co-primary only if the CMO insists, with Holm adjustment across the two). Secondary outcomes and subgroup effects (metro vs non-metro, size bands, regions) are exploratory and use Benjamini–Hochberg control. The analysis plan (specification, covariates, exclusions, decision rule) is written and time-stamped before looking at post-launch outcomes in A1 and before randomisation in A2.

### 14.7 What this can and cannot show
- **A1 can show** (under the stated assumptions and if diagnostics pass) an estimate of the feature's effect on the treated stores, with a CI. **It cannot** prove causality: if pre-trends diverge or an unmeasured co-occurring change exists, the design fails, and the report must say so. It does **not** show the effect in the stores not yet treated (if, as assumed [Assumed], the untreated stores are on average smaller and less metro, effects may differ).
- **A2 can show** the effect in typical untreated stores with randomisation protection, for the pilot window. It cannot show long-run effects beyond the window, effects of design changes to the feature, or national spillovers beyond the measured buffer.
- **Neither** identifies which customers benefit (needs A3 on randomised data).

## 15. Robustness & Sensitivity Tests
- Alternative outcome scales (log, indexed, level); with/without stock-out weeks; with/without festival weeks.
- Metro-only and size-matched subsets; leave-one-region-out.
- Placebo dates (pre-period) and placebo outcomes.
- Exclude stores with other initiatives (Q3).
- Time slices: effect by month since launch (novelty/decay).
- Spillover buffers: exclude untreated stores within a distance `[TBD with client]` of a treated store.
- Compare A1 (quasi-experimental) with A2 (randomised) estimates once available to calibrate how much to trust observational estimates in future.

## 17. Deployment & Monitoring Strategy
No model is deployed. The "deployment" is the rollout decision and its measurement:
- **Decision rule:** as in §10, agreed before analysis.
- **Rollout:** staged waves with randomised order (A2) so every wave remains evaluable.
- **Post-launch monitoring:** weekly dashboard of treated vs not-yet-treated stores (effect estimate with CI, margin, discount depth, return rate, redemption share). Alert if the margin effect's CI turns negative or if discount depth rises beyond a limit `[TBD with client]`.
- **Rollback:** the feature can be disabled per store; criteria agreed upfront.
- **Governance:** confirm consent for personalised marketing, data-protection obligations (DPDP Act 2023 and Rules if applicable), and fairness of offers across customer groups. *To be verified with the client's legal team.*
- **Communication:** until A1 diagnostics pass or A2 reports, wording for internal and external statements is "stores with the feature grew faster" rather than "the feature caused".

## 18. Risks, Mitigations, Dependencies & Open Decisions

| Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|
| Pre-launch data too short or missing, so parallel trends cannot be tested | Medium | High | Early data audit (Discovery); if unavailable, A1 is reported as descriptive only | BI / DS |
| Treated stores were trending up before launch | Medium–High | High | Event-study and synthetic control; report honestly if A1 fails | DS |
| CMO or stakeholders pressure for a headline number before analysis | High | High | Agree wording and decision rule now; share the "what we can say today" statement | Engagement lead |
| Randomisation rejected for operational or political reasons | Medium | High | Stepped-wedge with regional constraints; or quasi-random rollout using a documented ranking | CMO / COO |
| Pilot under-powered | Medium | Medium | Simulation-based power analysis before commit; consider customer-level design | DS |
| Sales lift achieved through discounts that erode margin | Medium | High | Margin as primary outcome | Finance |
| Spillover between nearby stores | Medium | Medium | Buffers, guardrail analysis | DS |
| Co-occurring initiatives (confounding) | Medium | High | Initiative calendar (Q3); exclusions; sensitivity | Marketing / DS |
| Novelty effect inflates the six-month result | Medium | Medium | Monthly event study; 26–52 week pilot | DS |
| Time confounding in the stepped-wedge | Medium | Medium | Stratified waves; secular-trend model; compare with a parallel-arm check | DS |
| A2 pilot contaminates A1 controls | Medium | Medium | Sequence A1 first or freeze its control set | DS |
| Privacy and marketing-consent compliance | Low–Medium | High | Legal review | Legal |

## 19. Phased Implementation Roadmap (provisional effort)

| Phase | Work package | Dependencies | Deliverables | Acceptance criteria | Indicative effort (provisional) |
|---|---|---|---|---|---|
| Discovery | Resolve Q1–Q8 (all needed by Week 2); agree decision rule and wording; data audit | Client access to owners | Signed-off analysis plan; data request | All blocking questions (Q1–Q6) answered or closed by a labelled assumption signed off by the CMO office | 1–2 weeks |
| Data engineering | Build store × week panel, initiative calendar, margin join | Discovery | Validated panel and data-quality report | Reconciles to reported 12% and 5% figures within an agreed tolerance | 2–3 weeks |
| Analysis / EDA (A1) | Pre-trend diagnostics; DiD, synthetic control; sensitivity | Data engineering | A1 report with effect, CI, diagnostics, verdict | Diagnostics reported; claim wording matches evidence | 3–4 weeks |
| Pilot design (A2) | Simulation-based power; randomisation scheme; pre-registration | Analysis/EDA findings, Q5 | Pilot protocol and randomised store list | Simulated MDE no larger than the minimum worthwhile effect δ (Q6), or the shortfall is accepted in writing; SMD balance within the agreed threshold; client approval | 2–3 weeks |
| Pilot run and monitoring (A2) | Staged rollout and weekly monitoring | Protocol approval | Dashboard; interim checks under alpha-spending plan | SRM passes; baseline covariate balance within the agreed SMD threshold; guardrails within limits | 26–52 weeks |
| Validation / readout | Final A2 analysis; compare with A1; rollout recommendation | Pilot complete | Decision memo to CMO | Decision rule applied as pre-agreed | 2 weeks |
| Deployment and monitoring | Staged rollout to remaining stores in randomised order; weekly monitoring per §17 | Decision memo | Rollout plan; monitoring dashboard | Guardrails within limits; effect CI tracked | Ongoing, outside the totals below; owner: CMO / Operations |

**Totals (sum of the six phases above, run sequentially, excluding the ongoing rollout phase):** 36–66 weeks, computed as 1+2+3+2+26+2 = 36 and 2+3+4+3+52+2 = 66. Pilot design could overlap with the A1 analysis, which would shorten the lower bound. Effort ranges are provisional placeholders: they depend on team size, data readiness, and approvals, none of which are known. A1 results are available about 6–9 weeks from the start (1+2+3 and 2+3+4), well before the pilot ends.

## 20. Decision Log

| # | Decision / recommendation | Rationale | Alternatives considered | Key assumptions | Risk | Validation method |
|---|---|---|---|---|---|---|
| D1 | Do not state "caused a 7-point lift" yet | The gap is confounded by non-random store selection | Publish the naive figure | F2 | Reputational; wrong rollout | A1 diagnostics, A2 |
| D2 | Treat as a causal problem, not a predictive one | Question is about the effect of an action | Predictive model with a treated flag | — | — | Framing review |
| D3 | A1 with DiD + synthetic control | Treatment at known date, pre/post data, many comparison stores | Naive comparison, regression only, interrupted time series | AS3, AS4, AS5 | Parallel trends fail | Event study, placebos |
| D4 | Margin net of offer cost as the primary decision outcome, level scale | Sales can be bought with discounts; margin can be negative | Sales only; log margin | Q2 | Data not available (fallback: sales × agreed margin rate) | Data audit |
| D5 | Randomise rollout among the 180 untreated stores (A2) | Removes selection bias | Further observational analysis only | AS6 | Operational resistance | Balance, SRM |
| D6 | Stepped-wedge preferred when full rollout is intended; parallel-arm as alternative | Everyone gets the feature eventually | Parallel arm | Time-trend model is credible | Time confounding | Simulation, secular-trend checks |
| D7 | Power via simulation on real pre-period data | No invented variance inputs | Closed-form with assumed ICC | AS3 | Under-powered | Simulation |
| D8 | Pre-register analysis and decision rule | Limits researcher degrees of freedom | Ad hoc analysis | — | Rigidity | Plan sign-off |
| D9 | Defer uplift/targeting model until randomised data exist | Needs causal labels | Train on the 40 stores now | — | Biased targeting | Qini/AUUC on randomised holdout |

## 21. References
No external sources were consulted in this run. Method names (difference-in-differences, synthetic control, stepped-wedge, Callaway–Sant'Anna, Sun–Abraham, Rambachan–Roth, wild-cluster bootstrap) refer to standard published methods; **full citations are still to be added and verified** before client release. Regulatory references (DPDP Act 2023) are to be verified with the client's legal team.

## Glossary
- **ATT / ATE:** average effect on the stores that got the feature / average effect across a typical store.
- **DiD (difference-in-differences):** compares the change over time in treated stores with the change in comparison stores.
- **Parallel trends:** treated and comparison stores would have moved together had the feature not been launched.
- **Synthetic control:** a weighted blend of untreated stores built to mimic a treated store's history.
- **SUTVA / spillover:** one store's treatment must not change another store's sales; spillover breaks this.
- **SRM:** sample-ratio mismatch, a check that the randomised split came out as planned.
- **SMD:** standardized mean difference, a measure of how well-balanced two groups are.
- **CUPED:** variance reduction using pre-period data.
- **RMSPE:** error between a synthetic control and the real store before launch.
- **Holm / Benjamini–Hochberg:** methods that adjust for testing many outcomes at once.
- **Alpha-spending:** a pre-set budget for false-positive risk across interim looks.
