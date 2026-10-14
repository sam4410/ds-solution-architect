# Causal Inference Designs

**Hierarchy of evidence:** randomised experiment > strong quasi-experiment with testable
assumptions > adjustment for observed confounders > naive comparison. Prediction models and feature
importance **never** establish causation.

## 1. Before choosing a design
1. Define treatment (what exactly, dose, timing), outcome, population, and estimand:
   - **ATE** (average effect in population), **ATT** (effect on those treated), **CATE** (effect by subgroup / individual — uplift), **LATE** (compliers, IV).
2. Draw a **DAG** (causal diagram) with the client's domain experts: treatment, outcome, confounders (common causes), mediators (on the path — do not adjust if you want total effect), colliders (common effects — never adjust).
3. Identify biases: confounding by indication (sicker patients get treatment), selection bias, reverse causality, survivorship, collider bias, immortal time bias (healthcare), regression to the mean (targeting "worst" units then measuring improvement).
4. Ask: **Can we randomise?** If yes, design an experiment — it is almost always cheaper than defending a quasi-experiment.

## 2. Design selector

| Design | Use when | Key assumption(s) | Diagnostics | Example |
|---|---|---|---|---|
| **Randomised controlled experiment / A/B test** | Treatment assignment controllable | Randomisation integrity, no interference (SUTVA) | SRM check, balance table | Retention offer randomised among at-risk customers |
| **Cluster-randomised / switchback** | Interference between units; operational treatments | Clusters independent; enough clusters | ICC, design effect | Store-level pricing test; hospital-ward protocol |
| **Stepped-wedge** | Rollout to all sites eventually; staggered | No time-treatment confounding beyond modelled trends | Secular trend modelling | Clinical pathway rollout across hospitals |
| **Difference-in-differences (DiD)** | Policy/intervention hit some units at known time; pre/post data for both groups | **Parallel trends** (no differential trend absent treatment) | Pre-trend plots/event study; placebo periods | New branch policy in some states; promo in some regions |
| **Staggered DiD** | Treatment at different times | As above; avoid naive TWFE bias with heterogeneous effects | Use Callaway–Sant'Anna / Sun–Abraham style estimators | Phased product launch |
| **Synthetic control** | One/few treated units (a region, a store), long pre-period | Weighted donors reproduce pre-period trajectory | Pre-period fit, placebo-in-space tests | Effect of a flagship store remodel |
| **Regression discontinuity (RDD)** | Treatment assigned by threshold on a running variable | No manipulation at cutoff; continuity of potential outcomes | Density test (McCrary), covariate continuity, bandwidth sensitivity | Credit limit given at score ≥ 700; care program for risk score ≥ 0.3 |
| **Instrumental variables (IV)** | Unobserved confounding, valid instrument exists | Relevance (strong first stage, F > 10 rule-of-thumb), exclusion restriction, monotonicity | First-stage F, over-identification tests where possible | Distance to facility as instrument for treatment choice (assumptions often contested) |
| **Propensity score matching / weighting (IPW), doubly robust (AIPW)** | Observational data, rich measured confounders | **No unmeasured confounding**, positivity/overlap | SMD < 0.1 after weighting, overlap plots, trimming | Effect of a loyalty programme membership on spend |
| **Regression adjustment / G-computation** | As above | Correct model + no unmeasured confounding | Sensitivity analysis | — |
| **Interrupted time series** | Single series, intervention at known time, no control group | No co-occurring changes; stable pre-trend | Segmented regression residuals; autocorrelation | Hospital-wide hand-hygiene protocol |
| **Uplift / heterogeneous treatment effect models** | Targeting: who benefits from the action? | Randomised (preferred) or identified data | Qini/AUUC on held-out randomised data | Whom to send a retention offer |
| **Double ML / causal forests** | High-dimensional confounders | No unmeasured confounding; overlap | Cross-fitting; sensitivity | — |

## 3. Sensitivity & robustness
- E-value: how strong an unmeasured confounder must be to explain away the effect.
- Rosenbaum bounds (matching).
- Negative-control outcomes/exposures (should show no effect).
- Placebo treatment dates/units.
- Alternative specifications, bandwidths, donor pools.

## 4. Language rules for the plan
- "X is **associated** with Y" for observational adjusted estimates unless identification is defended.
- "Under assumptions A, B, C, the estimated effect of X on Y is …" for quasi-experiments.
- State explicitly **what the design cannot identify** (e.g., long-term effects, effects outside the threshold neighbourhood for RDD, effects on non-compliers for IV).

## 5. Domain notes
- **Healthcare:** confounding by indication and immortal time bias are pervasive; target-trial emulation framing is recommended for observational EHR studies; ethics approval for interventions.
- **BFSI:** selective labels (outcomes only for approved applicants) and policy feedback loops; champion–challenger tests are the standard experimental vehicle; fair-treatment rules limit randomisation of credit terms.
- **Retail:** spillovers (cannibalisation, halo, store-to-store), seasonality and promotion calendars; geo/store-level experiments and synthetic control are common.
