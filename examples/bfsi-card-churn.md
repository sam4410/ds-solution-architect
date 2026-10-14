---
title: Credit-Card Attrition — Data Science Solution Plan
client: Client (private-sector bank, credit-card business)
industry: BFSI
prepared_by: Data Science Solution Architecture team
date: 2026-10-14
version: 0.1 (draft)
depth: Standard
classification: Confidential
---

# Credit-Card Attrition — Data Science Solution Plan

## 1. Executive Summary

- **Decision supported:** each month, which ~20,000 card customers the retention team should call, and which offer (fee waiver or reward points) to make, so as to retain the most profitable customers per call and per rupee of offer cost.
- **The request contains three different questions, and one model cannot answer all three:**
  - **A1 (Predictive):** who is likely to close their card voluntarily in the next 3 months?
  - **A2 (Inferential / exploratory):** what is associated with churn?
  - **A3 (Causal):** do the fee-waiver and reward-point offers reduce churn?
- **Why this matters:** a churn-risk model finds customers who are likely to leave. It does not show that a call or offer changes the outcome. Customers with the highest risk may have already decided to leave, or may stay anyway. "Drivers" from a churn model are associations, not levers. "Do offers work" can only be answered credibly with a randomised experiment.
- **Recommended approach:**
  1. Build a calibrated 3-month churn-risk model on monthly customer snapshots. Start with a simple baseline and a regularised logistic model, then a gradient-boosted model if it earns its place. Validate strictly out-of-time with a 3-month embargo.
  2. Answer "what drives churn" with interpretable associational analysis (survival or logistic models, SHAP). Label all of it as association. Test actionable levers causally where a natural experiment exists, such as the annual-fee billing event.
  3. Answer "do offers work" with a **randomised retention experiment built into the monthly campaign**: a no-call control, a fee-waiver arm and a reward-points arm, randomised inside the high-risk pool. This sets the offer-effect estimate, the incremental ROI and the training data for an **uplift model**, so that later waves call the customers who are *persuadable* rather than just *at risk*.
  4. Deploy as a monthly batch score feeding the CRM call list, with suppression rules, reason codes for agents, a rule-based fallback and a permanent small holdout for ongoing measurement.
- **Capacity arithmetic from the figures given (derived, assuming uniform hazard):**
  - 1.5% monthly attrition on ~2.4M cards is about 36,000 closures per month.
  - Over 3 months that is about 4.4% of the base, or about 106,000 customers.
  - A random list has about 4.4% precision, so the 20,000-call list is the first thing to beat.
  - A single list can contain at most ~19% of the customers who will close in the next 3 months. Success should therefore be judged by **precision/lift at 20,000 and by incremental retained margin**, not by AUC or recall.
- **What must be true:**
  - A clear definition of "voluntary closure" exists and closure dates are reliable in the data.
  - About 36 months of monthly history (minimum 30) is available (to be confirmed).
  - The bank's compliance and business owners approve randomising offers and holding out a control group.
  - Point-in-time feature snapshots can be rebuilt from the source systems.
- **Top risks:**
  - Call-centre "closure request" records leak the label.
  - Past retention calls and offers contaminate the labels and features.
  - Offers are selected by agents for customers who ask to leave, which makes observational comparisons misleading.
  - Silent attrition (stop using but never close) is not captured by a closure label.
  - Fee-waiver benefits may only delay churn by a year.
- **First next steps:** confirm the churn definition and the data extracts (§4 questions Q1–Q5); run the EDA and label-maturity audit; get approval for the randomised pilot while the baseline model is built.

### Scope of this plan

| Section | Status | Reason |
|---|---|---|
| 2–13 | Included | Predictive analysis A1 needs framing, data, baselines, metrics, experiments, validation and leakage audit. |
| 14 | Included in full | A2 (drivers) and A3 (offer effectiveness) are inferential and causal questions. |
| 15–17 | Included | Segment robustness, fairness, explainability, deployment and monitoring matter for a customer-facing regulated bank. |
| 18–21 | Included | Risks, roadmap, decision log and references. |
| Hyperparameter detail | Condensed | Detailed tuning applies only to A1 and the later uplift model. |
| Healthcare/retail packs | Not used | BFSI domain pack applied. |

**Plain-language glossary.** *Precision@K / lift:* of the K customers called, the share who would have left (lift = that share divided by the overall rate). *Embargo:* a deliberate time gap so training labels never overlap the evaluation period. *ITT (intention-to-treat):* compare customers by what they were assigned, whether or not the call connected. *Uplift:* how much a call changes the chance of leaving for a given customer. *PSI:* a score showing how far today's data has drifted from the data the model was built on. *WoE:* a way of binning variables for transparent scorecard-style models.

Depth: **Standard**. The brief has an identifiable decision, but the client was unavailable, so key definitions are labelled assumptions in §4.

## 2. Business Problem & Decision Framing

**Plain-language restatement.** The bank loses a small share of its card customers each month. It can phone about 20,000 customers a month with an offer. It wants to know who is about to leave, why they leave, and whether the offers keep them.

| Element | Definition for this case | Status |
|---|---|---|
| Decision | Monthly choice of whom to call (≤20,000) and which offer to make | [Confirmed] |
| Decision owner | Retention / portfolio marketing team | [Assumed] |
| Prediction point (t0) | Month-end snapshot of each active card. Calls happen during the following month, so the earliest call is about t0 + L days (L = list-to-call lead time, Q7). | [Assumed] |
| Action space | Call with fee waiver, call with reward points, or no call | [Confirmed] |
| Capacity | ~20,000 calls per month | [Confirmed] |
| Unit of analysis | Customer-card snapshot (customer–month). Customer is the resampling unit for confidence intervals. | [Assumed], see Q3 |
| Population | Active, in-good-standing cards at t0. Excludes cards already closed, bank-initiated closures, deceased, fraud-blocked, charged-off and 90+ DPD cases. | [Assumed] |
| Outcome (A1) | Customer-initiated (voluntary) card closure within 3 months after t0 | [Confirmed horizon]; exact definition [To investigate] |
| Base rate | ~1.5% monthly, so ≈4.4% over 3 months (derived) | [Confirmed monthly]; 3-month figure derived |
| Estimands | A2: associations. A3: ITT effect and per-reached effect of each offer vs no call on 90-day voluntary closure. | Defined here |
| Cost of errors | False positive: a wasted call plus a possible unneeded offer cost. False negative: lost card margin. Both [TBD with client]. | [TBD] |
| Success criteria | Precision/lift at 20,000 beats the agreed baseline. Experiment shows incremental retention with positive net value. All values [TBD with client]. | [TBD] |
| Constraints | RBI and DPDP data and consent rules, telemarketing and do-not-call rules, fair-treatment of customers, model risk governance (confirm with compliance) | [Assumed] |

## 3. Analytical Problem Classification

| Analysis | Lens | ML / statistical formulation | Why |
|---|---|---|---|
| **A1** Who will close within 3 months? | Predictive | Binary classification on monthly snapshots with a 3-month label window and calibrated probabilities. Ranking at top-K = 20,000. | Capacity-constrained ranking decision |
| **A2** What drives churn? | Inferential (associational), with exploratory descriptive work | Survival / discrete-time hazard or logistic model with adjustment, plus SHAP on the GBM. Reported as "associated with". | Interpretation, not prediction |
| **A3** Do the offers work? | Causal | Randomised controlled experiment (ITT, plus CACE via instrument). Later, uplift modelling on the randomised data. | Only randomisation is credible; offers were not assigned at random historically |
| **A4** Whom to offer what (follow-on) | Prescriptive | Uplift / CATE model, then a value-based targeting policy | Depends on A3 data |

**Alternatives considered.**

- **Survival / discrete-time hazard instead of 3-month binary classification:** better if follow-up varies or if the team wants a risk curve over time. Kept as a challenger because it gives horizon-specific risk and handles censoring of recent snapshots.
- **Predicting inactivity or dormancy instead of closure:** better if most real attrition is silent. Kept as a secondary target to compare (Q2).
- **Ranking by expected value** (risk × margin) rather than risk alone: preferred once margin data is available. Starts as a sensitivity analysis.

> **Note:** A churn model's top-risk list is *not* the same as the list of customers who should be offered something. This plan separates the two on purpose.

## 4. Assumptions, Unknowns & Client Clarification Questions

The client was not available. The assumptions below are used to proceed. The first five questions would change the plan most if answered differently.

| ID | Statement | Type | Impact if wrong | Owner | Needed by |
|---|---|---|---|---|---|
| Q1 | "Churn" means customer-initiated card closure. Bank-initiated closures, dormant-but-open cards and product migrations/upgrades are excluded from the target. | Assumption | Changes target, population and value. Needs exact closure reason codes. | Client business + data owner | Week 1 |
| Q2 | Silent attrition (spend stops, card stays open) is not counted as churn in the primary target but is analysed as a secondary outcome. | Open question | If silent attrition is a large share of lost value, the closure model misses it. | Client business | Week 1 |
| Q3 | Unit is the customer–card snapshot, with customer ID as the grouping key. Whether a customer who closes one card but keeps another counts as churn is not known. | Open question | Changes label, leakage grouping and cross-sell interactions. | Client | Week 1 |
| Q4 | Past retention calls and offers are logged (who, when, offer, outcome). | Open question | If not logged, history is contaminated with unknown treatment and the observational analysis of offers is infeasible. | Retention team | Week 1 |
| Q5 | The bank approves randomising offers within the risk pool and keeping a control group that receives no call. | Open question | Without it, A3 cannot be answered causally and only an observational, hypothesis-generating analysis is possible. | Business head, compliance | Week 2 |
| S1 | At least 36 months of monthly history exist (minimum 30; see §12). | Assumption | If shorter, seasonality and out-of-time validation weaken or become infeasible. | Data owner | Week 1 |
| S2 | Margin / profitability per card is available or can be approximated (interchange, interest, fees, minus rewards cost). | Assumption | Targeting stays risk-based, not value-based. | Finance | Week 3 |
| S3 | Data stays in the bank's environment. No client data goes to external services. | Assumption | Tooling choices change. | Security | Week 1 |
| S4 | Currency is INR and the regulator is the RBI. | Assumption | Regulatory checklist changes if not. | Client | Week 1 |
| S5 | Call outcomes (reached, accepted, declined) are logged. | Assumption | Without them, per-reached effects cannot be estimated. | Retention team | Week 2 |
| Q6 | The current approach (rules, agent judgement, existing score) is not described. | Open question | The baseline to beat is unknown. | Retention team | Week 1 |
| Q7 | How soon before closure can a call still help? Closures in the first days after t0 may be unsavable. | Open question | May justify excluding very imminent closures from the target or adding a minimum lead time. | Retention team | Week 2 |
| Q9 | Closure-posting latency (days between the customer's request and the closure date in the data) is unknown. | Open question | Sets label maturity and the earliest usable date for pending-request flags. | Cards ops | Week 1 |
| Q8 | Reward points and fee waivers have a cost and an expiry; their terms are not known. | Open question | Needed to compute net value and to define the follow-up window. | Finance, product | Week 3 |

## 5. Data Inventory & Feasibility Assessment

| Source | Business meaning | Owner | Grain / keys | Coverage & refresh | Point-in-time? | Quality risks | Privacy | Status |
|---|---|---|---|---|---|---|---|---|
| Card transactions | Spend, merchant category, channel, location, reversals | Cards ops | Transaction; card ID, customer ID | History depth and refresh to be confirmed | Yes, timestamped | Reversals, duplicates, MCC coding | PII; keep in bank environment | [Confirmed] exists; depth [To investigate] |
| Statements | Billing cycle balance, payments, interest, fees, limit | Cards ops | Card–cycle | Monthly | Yes, by statement date | Cycle dates differ from calendar months | PII | [Confirmed] exists |
| Customer demographics | Age, income band, city, tenure, relationship | CRM | Customer | Slowly changing | Only if history is kept (SCD) | Overwritten current values leak the future | PII; sensitive attributes | [Confirmed]; history [To investigate] |
| Complaints | Complaint type, date, status, resolution | Service | Complaint; customer ID | Event | Yes if open/close dates are kept | Resolution status updated later | PII | [Confirmed] |
| Call-centre logs | Call reason codes, notes, agent actions | Contact centre | Interaction | Event | Yes if timestamped | **Closure-request tags are near-label**; free text has PII | PII; redact text | [Confirmed]; fields [To investigate] |
| Bureau score at onboarding | Credit score at origination | Risk | Customer | One-off, so stale for old customers | Yes for early lifecycle | Stale for long-tenure customers | Bureau terms of use | [Confirmed] |
| Closure / account-status table | Closure date, initiator, reason code | Cards ops | Card | Event | Yes | Reason codes may be inconsistent | PII | [To investigate]; essential for the label |
| Retention campaign history | Who was called, offered what, outcome | Retention | Customer–campaign | Event | Yes | Selection by agent judgement | PII | [To investigate]; critical for A3 |
| Offer / reward cost terms | Fee-waiver value, points cost | Finance / product | Product | Static | n/a | n/a | n/a | [To investigate] |
| Marketing consent / DND flags | Contactability | Compliance | Customer | Event | Yes | Staleness | Regulatory | [To investigate] |
| External macro / competitor offers | Interest-rate and competitor effects | Public | Month | Monthly | Yes | Weak, aggregated | None | [To investigate], nice-to-have |

**Feasibility verdict: Feasible with conditions.** Blocking dependencies:

1. A reliable voluntary-closure label with reason codes and closure dates (Q1).
2. Point-in-time reconstruction of features at each month-end, including history of demographics and limits.
3. Retention-call history, to avoid contaminated features and labels and to support the observational part of A3 (Q4).
4. Approval to run the randomised pilot (Q5).

## 6. Data Quality & Preprocessing Plan

| Step | Rationale | Method | Risks | Validation check |
|---|---|---|---|---|
| Build monthly snapshot table | Match the decision timing | One row per active card per month-end; features from data ≤ t0 only; label from (t0, t0+3m] | Using current-state tables leaks the future | Re-run a past snapshot and compare with archived values |
| Entity resolution | Customers may hold several cards | Map card to customer; define churn per Q3 | Counting product migrations as churn | Reconcile closures against new-card issuance |
| Exclusions | Remove cases the call cannot influence or that are not voluntary | Drop bank-initiated closures, fraud, deceased, delinquent/charge-off, and cards closed at t0 | Alters the population and the estimand (state it) | Counts and rates by exclusion reason |
| Handle pending closure requests | A request already logged is nearly the label | Exclude from the ordinary model population at t0 or route to a "save desk" list | Leakage; wasted capacity | Compare model quality with and without these rows |
| Deduplicate and reconcile transactions | Duplicates and reversals distort spend | Net reversals; dedupe by transaction ID | Signal loss from over-cleaning | Totals reconcile to statements |
| Missing values | Missingness may be informative (no complaints vs not recorded) | Explicit missing indicators; zero-fill only where "none" is true; tree-native handling | Imputation fit on full data leaks | Fit imputers in training folds only |
| Outliers | Spend and balance are heavy-tailed | Winsorise or log-transform for linear models; leave for trees | Removing high-value customers | Compare metrics by value tier |
| Encoding | MCC, city, product are high-cardinality | Frequency or target encoding fitted in folds; grouped rare levels | Target encoding leakage | Encoding inside the CV pipeline |
| Scaling | Needed for linear / regularised models only | Fit on training folds | None material for trees | Pipeline test |
| Class imbalance (~4–5% positives) | Imbalance is moderate, not extreme | Do **not** resample by default; use class weights as an experiment; if negatives are down-sampled for compute, re-weight and recalibrate | Resampling distorts probabilities and the top-K cut | Calibration plot and precision at 20,000 on the unaltered validation set |
| Text from complaints and call notes | May carry signal | Phase 2 only: redact PII in place, then structured categories first, then simple text features | PII exposure; leakage from "close card" phrases | Ablation (E4) and a keyword leakage scan |
| Treatment-history features | Past calls change future behaviour | Include contact/offer history as explicit features only if they are available at t0 and the deployment policy would still see them | The model learns "called = safe" and suppresses calls on at-risk customers | Compare with and without; check in the experiment |
| Time alignment | Statement cycles vs calendar months | Use statement-cycle date or calendar month-end consistently | Misaligned windows | Spot-check |

## 7. Feature & Target Design

### Target (A1)

- **Label = 1** if the card is closed by the customer (or at the customer's request) within 3 months after t0; otherwise 0. This is the requested target and is used for model development.
- **Actionable-window sensitivity.** Closures before the earliest feasible call date (t0 + L) cannot be saved. Evaluate a variant label counting closures only in (t0 + L, t0 + 3m]. The A3 experiment outcome is 90 days from assignment, so the two windows differ by design (Q7).
- **Selection effect of exclusions.** Excluding bank-initiated closures, fraud, delinquency and pending requests means the model describes the voluntary-churn risk of otherwise healthy cards. Report the size of each exclusion and check whether excluded groups differ in profile.
- **Maturity.** A snapshot is labelled only once t0 + 3 months + closure-posting latency has passed. Recent snapshots are excluded from training and evaluation.
- **Exclusions** as in §6. Cards closed for bank-initiated reasons within the window are removed from the labelled set (competing event); the survival challenger (X7) treats them as censored.
- **Label stability.** Check whether reason codes, closure procedures or policy changed over time; if so, restrict training windows or add period indicators.
- **Secondary targets:** 1-month hazard, silent attrition (e.g., no spend for N months, N to be agreed), and customer-level relationship attrition.

### Feature groups (all measured at or before t0)

| Group | Examples | Availability | Hypothesis |
|---|---|---|---|
| Spend dynamics | Recent vs prior 3/6/12-month spend, transaction counts, category mix, share of online/international | Month-end | Hypothesis: falling engagement precedes closure |
| Balance and payment behaviour | Utilisation, revolve vs full pay, minimum-due behaviour, late payments | Statement date | Hypothesis: financial strain or a switch to another card |
| Fees and charges | Annual fee posted or upcoming, interest and late-fee charges, fee reversals | Statement date | Hypothesis: fee events prompt customers to reconsider |
| Rewards | Points earned/redeemed, expiring points, reward-to-spend ratio | Month-end | Hypothesis: low perceived reward value |
| Tenure and lifecycle | Months on book, card age, time since last limit change, card product | Static or SCD | Hypothesis to test: risk varies with card age and anniversaries |
| Service interactions | Complaints in last 30/90/180 days, unresolved complaints, call counts, call reason categories, dispute counts | Event-timed | Hypothesis: poor service experience is associated with closure |
| Retention history | Prior calls, offers accepted, offer expiry dates | Event-timed | Prior offers may suppress or defer churn |
| Demographics | Age band, income band, city tier | Must be historical | Context only; check fairness |
| Bureau at onboarding | Score at origination | Static | Weak, stale; keep, but test its contribution |
| Cross-product | Other products held with the bank, salary account | If available | Hypothesis: deeper relationships are associated with lower churn |

## 8. Baseline Model Specification

| Baseline | Inputs | Protocol | Limitation | Role |
|---|---|---|---|---|
| B0 Random list | None | Same out-of-time test, same K | Sanity floor only (precision ≈ base rate) | Floor |
| B1 Current business rule / score | Whatever the team uses today [TBD] | Same test and K | Unknown until Q6 is answered | **The bar that matters** |
| B2 Simple heuristic | Spend decline over 3 months, recent complaint, annual-fee month | Same test and K | Hand-built | Shows value of ML over rules |
| B3 Regularised logistic regression | A small, interpretable feature set | Same test and K | Limited non-linearity | Reference model and explainable champion candidate |

**Bar to beat.** A candidate must beat B1 (or B2 if B1 is missing) on precision@20,000 and on lift by an agreed margin [TBD with client] across all rolling out-of-time folds. Proposed rule for the margin: the lower 95% paired-bootstrap bound (resampling customers) of the precision@K gain over B1 must exceed the smallest gain that covers the extra operating cost, to be agreed in Phase 1. No numeric baseline value is stated here because none has been supplied.

## 9. Candidate Algorithms & Prioritisation

| Priority | Algorithm | Why plausible | Needs | Strengths | Weaknesses | Interpretability | Key hyperparameters | Reject if |
|---|---|---|---|---|---|---|---|---|
| 1 | Regularised logistic (WoE/binned) | Transparent, stable, easy to validate | Binning, monotone features | Calibrated, explainable, reason codes | Misses interactions | High | C, binning, penalty | Never rejected; stays as the reference |
| 2 | Gradient-boosted trees (LightGBM / XGBoost / sklearn HistGB) | Tabular data with many mixed features and interactions | Millions of rows are fine; careful time splits | Strong ranking quality, handles missing values | Needs calibration; less transparent | Medium (SHAP, monotone constraints) | learning rate, trees, depth/leaves, min child samples, subsample, regularisation, scale_pos_weight | Fails to beat logistic beyond the noise band on precision@20,000 or fails stability by period |
| 3 | Discrete-time survival (GBM on person-period rows) | Horizon-specific risk and censoring handling | Person-period table | Risk curves; uses recent snapshots | Larger data, complexity | Medium | Same as GBM plus time-bin encoding | Adds no value over the binary classifier |
| 4 (A4, later) | Uplift models (two-model / X-learner / causal forest) | Targets persuadables | **Randomised campaign data** | Optimises incremental retention | Needs volume; noisy | Medium | Base-learner settings, propensity known by design | Qini / uplift curve not better than risk ranking on held-out randomised data |

**Deferred.** Deep sequence models on transactions are not justified yet. Reconsider only if tabular aggregates plateau and an ablation shows raw-sequence signal.

**Selection rule.** Prefer the simpler model when the difference is within the cross-fold noise band. Otherwise rank by: precision@20,000 (primary), then calibration, stability across periods and segments, explainability, and serving cost.

## 10. Metrics & Decision Criteria

| Tier | Metric | Definition | Why | Caveat |
|---|---|---|---|---|
| Primary | Precision@K and lift@K (K = 20,000, or the equivalent top fraction scaled to a snapshot) | Share of the top K that close voluntarily within 3 months; divided by base rate for lift | Matches the monthly capacity | Does not show whether a call changes the outcome |
| Secondary | PR-AUC | Area under precision–recall | Threshold-free, suited to ~4% positives | Hard to interpret for executives |
| Secondary | Recall@K | Share of all 3-month churners captured in the top K | Context for coverage | Capped by capacity (≈19% ceiling under uniform hazard) |
| Secondary | Calibration (reliability curve, Brier, calibration slope) | Predicted vs observed rates | Needed for expected-value targeting | Resampling breaks calibration |
| Diagnostic | ROC-AUC / Gini, KS | Rank separation | Familiar to risk teams | Dominated by the large non-churn mass; do not use as a primary metric |
| Diagnostic | PSI / CSI | Distribution shift | Monitoring | Not a performance measure |
| Stability | Metric by month and segment | Same metric across folds and segments | Detect fragile models | Small segments are noisy |
| Business | Incremental retained cards and net margin per ₹ of offer cost | From the randomised experiment | The real objective | Needs margin and cost inputs [TBD] |

**Rejected metrics.** Accuracy (a model predicting "no churn" scores ~96%). Using AUC alone as the selection criterion.

**Decision rule.** Take the top K = capacity by risk score (A1). In later waves, rank by expected incremental margin = predicted uplift × margin − offer cost. K is set by call capacity, not by a probability cut-off. Any probability threshold used for tiering is chosen on validation data and frozen before the locked test.

## 11. Experiment Matrix & Tuning Strategy

### Stages

| Stage | Purpose | Exit criterion |
|---|---|---|
| E0 Data audit and sanity | Row counts, label maturity, prevalence by month, as-of timestamp audit, keyword scan of features for near-label content | Data passes checks; label definition signed off; no near-label feature remains |
| E1 Baselines | Run B0–B3 on the final split | Bar to beat fixed |
| E2 Candidate models | GBM and hazard model vs B3 | Gain above noise band or stop |
| E3 Feature-group ablations | Which data sources earn their cost | Contribution per group reported |
| E4 Text features | Complaint and call-note signal | Include only if gain above noise band and no leakage |
| E5 Tuning | Tune only models that beat baseline | Budget exhausted or no gain |
| E6 Calibration | Isotonic / Platt on a held-out calibration window | Calibration slope in agreed range |
| E7 Robustness, fairness, stability | Segments and time slices; target-shuffle test (performance must collapse to base rate); adversarial validation (train vs latest period) | Acceptance criteria met; shuffle and adversarial checks pass |
| E8 Locked test | One evaluation of the frozen pipeline | Report, no further tuning |

### Experiment cards

| ID | Hypothesis | Change | Fixed conditions | Split | Metrics | Stopping rule |
|---|---|---|---|---|---|---|
| X1 | A ranked model beats the current rule | B1 vs B3 | Same snapshots and K | Rolling out-of-time folds | Precision@K, lift | Run all folds; proceed to X2 only if B3 beats B1 by the minimum meaningful improvement, else revisit features |
| X2 | Boosted trees beat logistic | B3 vs GBM | Same features and folds | Same | Precision@K, PR-AUC | Stop if difference is within noise |
| X3 | Class weights or negative down-sampling help | Weights vs none | Best model of X2 | Same | Precision@K, calibration | Reject if the precision@K interval includes zero or the calibration slope leaves the agreed band |
| X4 | Service-interaction features add signal | Ablate complaints / call data | Best model | Same | Precision@K | Keep if gain exceeds noise band |
| X5 | Fee-event and rewards features add signal | Ablate groups | Best model | Same | Precision@K | Same |
| X6 | Retention-history features inflate performance | With vs without | Best model | Same | Precision@K; behaviour on never-contacted customers | Drop if gain comes from contact status only |
| X7 | Survival formulation improves recent-snapshot use | Hazard vs binary | Same features | Same | Precision@K | Keep only if better |
| X8 | Calibration is stable | Isotonic vs Platt | Frozen model | Calibration window | Slope, Brier | Choose the more stable |
| X9 | Value-weighted ranking changes the list | Risk vs risk × margin | Frozen model | Same | Margin captured at K | Report; adopt only with client agreement |
| X11 | Offers reduce 90-day closure vs no call (A3) | Randomised arms (§14) | Same pool rules, scripts and suppression | Randomised waves | Closure-rate difference with 95% CI; net value | Stop only at the pre-registered interim look (§14) |
| X12 | Uplift ranking beats risk ranking (A4) | Uplift model vs risk score | Held-out randomised wave | Held-out wave | Qini, incremental retained margin at K | Adopt if the interval for the gain excludes zero and exceeds the minimum meaningful improvement |
| X10 | Silent-attrition model | Alternative target | Same features | Same | PR-AUC | Exploratory |

**Tuning strategy.** Random search first, then Bayesian optimisation with early stopping for the winning family. Use rolling time-based folds. Budget: ~100–200 trials for the GBM, to be set against compute. Priority order: learning rate and number of trees, leaves/depth, min samples per leaf, feature/row subsampling, L1/L2 regularisation, class weight. Tuning happens only on validation folds, never on the locked test.

**Reproducibility.** Fixed seeds; environment lockfile; versioned and hashed data snapshots; versioned split definitions; configs in version control; an experiment tracker (MLflow or equivalent); a model card; and a log of every test-set access.

**Operational definitions.** *Noise band* = the 95% paired-bootstrap interval (by customer) of the metric difference across validation folds; a difference counts as real only if its interval excludes zero **and** exceeds the minimum meaningful improvement. *Minimum meaningful improvement* = [TBD with client]; proposed default: the precision@K gain that yields positive net value after the extra operating cost. **Tuning protocol:** hyperparameters are tuned on inner rolling folds inside the training period; model-family comparisons (X1–X10) use outer folds that tuning never touches, and the number of comparisons is logged and reported.

**Comparison protocol.** Identical folds, paired comparison with bootstrap intervals (resampling customers, not rows), and a pre-declared minimum meaningful improvement [TBD with client].

## 12. Train / Validation / Test Design

**Deployment scenario.** At each month-end the bank scores all eligible active cards using data up to that date, then calls the top K over the following weeks. Most customers are returning (the same customer appears in many snapshots), and the label needs 3 further months to mature.

**Strategy.** Out-of-time rolling-origin validation on monthly snapshots, with a **3-month embargo** between training labels and the evaluation period, and embargo and customer-level bootstrap. This estimates performance on a future month-end for a mostly known customer base.

> **Assumption:** about 36 months of history (minimum 30; S1). Feasibility arithmetic: ~12 months minimum training + 3 months embargo + 3 rolling validation origins + a 3-month calibration block + a 3-month locked test + 3 months for test labels to mature. With 30 months this allows only 2 validation origins and a shorter initial training window. With fewer than 24 months the full design is not feasible and the plan must be re-scoped (fewer folds, no seasonal-cycle coverage).

```
Month index (36 months of history; label data complete through m36):
m1 ........ m12 | m13-m15 | m16 .... m24 | m25-m27 | m28-m30 | m31-m33     | m34-m36
 expanding train  embargo    validation     calib.    embargo   LOCKED TEST   labels mature
Validation: 3 origins (train through m12 / m15 / m18, each + 3-month embargo), scoring the next 3 snapshots
Calibration: held-out block after the last validation fold, never used to fit the model
Locked test: snapshots m31-m33, labelled through m36; touched once
Retrain cadence: quarterly in production; monthly re-scoring
```

Customers recur across snapshots **by design**: in production the model scores customers it has already seen. The temporal split plus embargo is the primary protection. Customer grouping is used only for bootstrap resampling of intervals and for any non-temporal diagnostic cross-validation, not for the main split.

**Hygiene rules.**

- Deduplicate before splitting.
- Fit all transforms inside training folds.
- Resample only inside training folds, and always evaluate on the untouched natural distribution.
- The embargo ensures no training label window overlaps the evaluation period.
- Use the point-in-time data vintage.
- Version the split definitions.
- Never tune thresholds or early stopping on the test.

**Why not random k-fold.** A random split would mix snapshots from the same customers and from the future, inflate performance and ignore drift.

## 13. Leakage Audit Checklist

| Risk | Applies? | Where it could occur in this case | Mitigation | Owner |
|---|---|---|---|---|
| Target leakage | Yes | Closure-request call tags, "balance transfer out", closure-related complaint categories, final-statement flags | Remove or time-bound; scan features for near-label signals; exclude pending closure requests | DS + contact centre |
| Temporal leakage | Yes | Current-state demographic or limit tables; statements finalised after t0 | Rebuild features with as-of dates; use archived snapshots | Data eng |
| Label delay / immature labels | Yes | Closures posted late; last 3 months unlabelled | Maturity filter; evaluate on matured windows | DS |
| Entity overlap | Yes | Same customer across train and test; multiple cards | Time-based split plus embargo; customer overlap across time is intended; group by customer only for bootstrap and non-temporal diagnostics | DS |
| Preprocessing outside folds | Yes | Imputers, encoders, scalers | Pipelines fit in-fold | DS |
| Selective labels / treatment contamination | Yes | Past retention calls and offers suppress churn for treated customers; agents choose whom to call | Include contact history as a feature only with care; analyse never-contacted separately; rely on the randomised experiment for effects | DS + retention |
| Policy changes / regime shifts | Yes | Fee or reward devaluations, product changes, closure process changes | Period indicators; stability tests; restrict windows if needed | Business |
| Test-set reuse | Yes | Repeated looks at the test | Locked test, access log | DS lead |
| Resampling leakage | Yes | Over/under-sampling before splitting | Resample inside training folds only | DS |
| Aggregation leakage | Yes | Windows crossing t0 | Window end ≤ t0 | Data eng |
| Proxy discrimination | Possible | Pincode, language, device | Fairness review; drop or constrain | Risk |

## 14. Statistical Inference & Causal Analysis Plan

### A2 — What is associated with churn?

- **Estimand.** Adjusted association between each driver group and 3-month voluntary closure. Not an effect.
- **Methods.** Discrete-time hazard or logistic model with standardised features and pre-specified groups; SHAP and grouped permutation importance on the GBM; partial dependence for key variables. Report effect sizes with 95% confidence intervals (bootstrap by customer).
- **Language.** Always "associated with". Importance scores say what the model uses, not what causes closure.
- **Multiple testing.** Pre-specify confirmatory driver groups; control the rest with BH false-discovery-rate control and label them exploratory.
- **Pitfalls.** Correlated features split importance; reverse causality (complaints follow disengagement); variables recorded after the decision to leave.
- **Moving from association to levers.** For levers that can be changed, use a design that supports causal claims:
  - *Annual-fee posting:* event-study or difference-in-differences around billing timing, if billing dates vary across customers for administrative reasons. Check that timing is not self-selected.
  - *Reward changes or fee changes:* difference-in-differences with a comparison group if rollout varied by product. Test pre-trends.
  - *Complaint resolution speed:* observational and confounded; report as association only.

### A3 — Do the retention offers work?

**Estimand.** For eligible high-risk customers, the effect of being assigned to (a) a call with a fee waiver or (b) a call with reward points, versus no call, on voluntary closure within 90 days (intention-to-treat, ITT). Secondary: effect among customers actually reached (complier effect, using assignment as instrument), with the caveat that it applies to reachable customers.

**Why not use history.** If past offers went to customers who phoned to cancel, or were chosen by agents, a naive comparison will make offers look ineffective or harmful (confounding by indication). A propensity-weighted or doubly robust analysis of past campaigns is allowed **only as exploratory input** for sizing the pilot, and carries the assumption of no unmeasured confounding.

**Design (preferred): randomised controlled experiment embedded in the monthly campaign.**

| Item | Specification |
|---|---|
| Eligible pool | Top-ranked customers by the A1 model (pool size ≈ capacity plus control, set with the client) after suppression rules |
| Randomisation unit | Customer, stratified by risk decile, tenure band and product |
| Arms | Control (no call); call + fee waiver; call + reward points. Optional: call without an offer, to separate call effect from offer effect |
| Enrolment | **Once per customer within a 90-day outcome window**: a customer enrolled in one wave is ineligible for later waves until their 90-day outcome is observed, so waves do not overlap and the contact cap (§17) is respected. |
| Allocation | Illustrative only: a pool of ~25,000 per month with ~10,000 per offer arm and ~5,000 control, so calls stay within the 20,000 capacity. Final sizes follow from the power grid below and the client's tolerance for an uncalled control. |
| Exploration | A small random slice (e.g., ~5% of calls) from lower-risk bands to learn uplift across the risk range, subject to client agreement |
| Primary outcome | Voluntary closure within 90 days of assignment |
| Secondary outcomes | 180- and 365-day closure (for delayed churn when a waiver expires), spend, revolving balance, margin, offer cost, offer take-up |
| Guardrails | Complaints, opt-outs, customer-experience scores, offer-cost overrun, contactability |
| Integrity checks | Sample-ratio mismatch check, covariate balance table, call-log compliance (agents calling control customers), contamination |
| Interim looks and stopping | Pre-registered: one interim look after wave 2 outcomes using a conservative alpha-spending boundary (O'Brien–Fleming type). Stop an arm early for harm if a guardrail (complaints, opt-outs, cost per retained card) breaches its agreed limit. No other early stopping. |
| Analysis | ITT difference in closure rates with 95% CI; risk ratio; adjusted estimate (pre-specified covariates) as precision gain; per-reached effect via assignment as instrument; net value per customer |
| Heterogeneity | Pre-specified subgroups (risk tier, tenure, spend, revolver vs transactor), then uplift modelling on the pooled data |
| Pre-registration | Written analysis plan, hypotheses and stopping rule before launch |
| Multiplicity | Two primary comparisons (each offer vs control) with Holm correction; offer-vs-offer and subgroups are secondary or exploratory |
| Duration | Three monthly waves, each followed for 90 days (primary) and up to 12 months (secondary). Primary readout about 6 months after launch; full follow-up about 15 months. |
| Ongoing | After the pilot, keep a permanent random holdout (small, e.g., 2–5%, size set with the client) to track incremental impact |

**Power / minimum detectable effect (ILLUSTRATIVE; every input is an assumption, not client data).**

Formula for a two-proportion comparison: MDE ≈ (z₁₋α/₂ + z₁₋β) × √(p(1−p)(1/n_arm + 1/n_ctrl)), with 80% power and α = 0.025 per comparison after Holm (z ≈ 2.24 + 0.84). Two unknown inputs drive the result: the control closure rate p in the pool, and the **contact rate c** (the share of assigned customers actually reached). The ITT effect is diluted by c, so the smallest detectable effect among reached customers is the ITT MDE divided by c.

Sensitivity grid for three pooled waves (30,000 per offer arm, 15,000 control; a single wave has an MDE about 1.7 times larger):

| Control closure rate p | ITT MDE (pp) | Smallest detectable effect among reached customers, c = 60% (pp) | c = 40% (pp) |
|---|---|---|---|
| 8% | ≈ 0.8 | ≈ 1.3 | ≈ 1.9 |
| 15% | ≈ 1.1 | ≈ 1.8 | ≈ 2.7 |
| 25% | ≈ 1.4 | ≈ 2.3 | ≈ 3.5 |

Recompute with the real p and c once known. Compare the MDE with the smallest effect that makes the offer profitable (offer cost and margin, Q8). If the profitable effect is below the MDE, the pilot will be inconclusive for that arm and the design should be revised before launch (more waves, fewer arms, or a larger pool). Analyses are clustered by customer as a safeguard.

**Threats and what this design can and cannot identify.**

- Identifies the average effect of the *assigned* offers in the *high-risk pool*, in the *tested period and call script*. Does not identify the effect for low-risk customers (except the exploration slice), the effect of other offers, long-run effects beyond follow-up, or the effect when scaled to different capacity.
- Control customers are at risk and receive no call, so there is a commercial and customer-fairness cost to the control group. Size it as small as power allows, and get approval (Q5).
- Spillover is limited because customers are independent, but household members and social effects may exist.
- Fee waivers can postpone rather than prevent churn; hence the 12-month follow-up.
- If randomisation is refused, fall back to a regression-discontinuity design only if a risk-score cut-off already drives who is called (check for manipulation and continuity), or to an observational AIPW analysis with sensitivity analysis (E-value) and the label "exploratory — association".

**Uplift modelling (follow-on).** Train on the pooled randomised data. Evaluate on held-out randomised data using Qini / uplift-by-decile curves. Adopt for targeting only if it beats risk-ranking on incremental retained margin in a second randomised wave.

## 15. Robustness & Sensitivity Tests

- **Time slices.** Performance by month and quarter, including seasonal peaks and any policy-change period.
- **Segments.** Product, tenure band, spend tier, city tier, channel, and new vs mature customers.
- **Label sensitivity.** Different closure definitions (including or excluding product migrations), 2- and 4-month horizons, and minimum lead time (Q7).
- **Feature-availability stress.** Delay key feeds by one cycle to simulate late data.
- **Label-maturity simulation.** Evaluate as if only the labels available at deployment time were known.
- **Target-shuffle and adversarial validation.** Check for leakage and for shift between train and the latest period.
- **Experiment sensitivity.** Re-estimate A3 with and without covariate adjustment, trimmed outliers, and per-protocol vs ITT.

## 16. Interpretability & Uncertainty

- **Global.** Coefficients of the logistic reference model; SHAP summary and grouped importance for the GBM. Describe as model behaviour and association.
- **Local.** Top 3–5 contributing factors per customer as agent-facing "reason codes" in plain language (e.g., spend decline, unresolved complaint, annual fee due). Reasons are cues for a conversation, not stated causes.
- **Constraints.** Monotonic constraints where the business logic is clear; review any non-monotone behaviour with the business.
- **Uncertainty.** Calibrated probabilities with bootstrap intervals for metrics. Report effect sizes with confidence intervals everywhere. For the experiment, show intervals on net value, not just closure rates.
- **Communication.** Agents see a priority tier and reasons, not raw probabilities. Executives see lift, incremental retention and net value with intervals.

## 17. Deployment & Monitoring Strategy

**Serving pattern.** Monthly batch scoring on the month-end snapshot (weekly or event-triggered refresh is a later option), writing a ranked list to the CRM or dialler with offer assignment. No real-time requirement is assumed.

**Pipeline and parity.** Same feature code in training and scoring, with a versioned feature store or table. Score-time data checks before release.

**Business rules wrapped around the model.**

- Suppress customers who are on do-not-call or lack marketing consent, have an open complaint, are in collections, or have been called within N days (N set with client).
- Cap repeated contact so the same customer is not re-called every month.
- Apply offer-eligibility rules from product and finance.

**Human in the loop.** Agents may override with a logged reason. Scripts must follow fair-practice and mis-selling rules. Overrides are analysed.

**Rollout.** Shadow scoring against the existing list → randomised pilot (A3) → champion–challenger on call lists → full rollout, with the rule-based list as fallback.

### Monitoring plan

| Layer | Metric | Threshold (initial, to be agreed) | Action | Owner |
|---|---|---|---|---|
| Data | Feed completeness, schema, null rates | Any breach of agreed limits | Block scoring, alert data eng | Data eng |
| Drift | PSI/CSI on score and key features | PSI > 0.1 watch, > 0.25 investigate | Investigate, consider retrain | DS |
| Calibration | Predicted vs observed by decile once labels mature | Slope outside agreed band | Recalibrate | DS |
| Performance | Precision@K on matured cohorts (3-month lag); 30-day closure-request rate as an early proxy | Drop beyond noise band | Retrain / review | DS |
| Business | Incremental retention in permanent holdout; offer cost per retained card; net margin | Below plan | Revisit offers and targeting | Business |
| Fairness | Contact and offer rates, retention by protected-proxy segments | Parity limits agreed with risk | Review features and rules | Risk |
| Operations | Calls completed, contact rate, override rate | Agreed limits | Process fix | Retention |

**Retraining.** Quarterly by default, or sooner on a drift trigger or a policy change. Every candidate goes through the same validation and an approval gate. Rollback to the previous model or the rule-based list if monitoring breaches thresholds.

**Governance (all items: confirm with client compliance and model-risk teams; instruments are named for orientation and their current text must be verified).**

- **RBI directions on credit-card and debit-card issuance and conduct**, including the handling of card-closure requests. Closure requests must be honoured within the regulatory timeline, and retention outreach must not obstruct or delay a customer's closure. This constrains the "save desk" idea for pending closure requests (§6, D9): do not use it for customers who have already asked to close unless compliance approves the exact process.
- **RBI guidance on model risk, IT governance and outsourcing**, and the RBI framework on responsible and ethical AI in financial services (FREE-AI, 2025; verify current status).
- **Digital Personal Data Protection Act 2023 and Rules:** consent and purpose limitation for using transaction, complaint and call-note data for marketing.
- **Telecom commercial-communication / do-not-call rules** for outbound retention calls, and the bank's own contact-consent flags.
- **Fair-treatment expectations:** offers are applied by documented policy, not agent discretion. Randomised offers need business and compliance sign-off, and compliance should confirm that a no-call control group is acceptable.
- **Bank model-risk policy:** independent validation, documentation pack, change control and periodic review.
- **Data handling:** PII stays inside the bank's environment; free text is redacted; role-based access and audit logs.

**Fairness plan.** Evaluate precision@K, call-list selection rate, offer rate and (from the experiment) retention effect across age band, gender where held, city tier, income band, tenure band and product. Sensitive attributes and plausible proxies (pincode, language) are not model inputs unless risk approves; they are used for testing. Metrics: the ratio of selection rates (flag outside a band set by risk and compliance) and gaps in precision@K. Owner: risk with DS. Results go in the validation report.

## 18. Risks, Mitigations, Dependencies & Open Decisions

| Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|
| Label definition is wrong or unstable (migrations, bank-initiated) | Medium | High | Q1 sign-off; reason-code audit; sensitivity tests | Client + DS |
| Closure-request call tags leak the label | High | High | Time-bound features; exclude pending requests; leakage scan | DS |
| Past campaigns contaminate labels and features | High | High | Treatment-history audit; randomised pilot | DS + retention |
| Control group not approved, or its cost is too high (about 20% of the pilot pool goes uncalled in the illustrative allocation) | Medium | High (A3 not answerable causally; foregone retention in control) | Early stakeholder alignment; smaller control; fallback designs labelled exploratory | Business |
| Experiment underpowered | Medium | Medium | Recompute MDE with real rates; pool waves; reduce arms | DS |
| Fee waivers delay rather than prevent churn | Medium | Medium | 12-month follow-up | DS |
| High-risk customers are not persuadable | Medium | High | Uplift modelling on randomised data | DS |
| Insufficient history for out-of-time validation | Medium | Medium | Check early; shorten folds; flag limits | Data eng |
| Policy shifts (fees, rewards, competitor offers) break stationarity | Medium | Medium | Monitoring, period indicators, quarterly retraining | DS |
| Silent attrition missed | Medium | Medium | Secondary target (Q2) | DS |
| Fairness or proxy discrimination in offers | Low–Medium | High | Fairness testing; feature review | Risk |
| Agents ignore or override list | Medium | Medium | Training, override logging, feedback loop | Retention |
| Privacy breach from call text | Low | High | In-environment processing; redaction | Security |

## 19. Phased Implementation Roadmap

All effort ranges are **provisional**, since team size, infrastructure and data readiness are unknown.

| Phase | Work package | Dependencies | Deliverables | Acceptance criteria | Indicative effort (provisional) |
|---|---|---|---|---|---|
| 1 Discovery | Confirm definitions (Q1–Q8), stakeholders, success metrics, governance path | Client access | Signed-off target definition, success criteria, experiment approval path | Q1–Q7 and Q9 answered in writing, including the current baseline process (Q6) and the lead time (Q7) | 2–3 weeks |
| 2 Data engineering | Point-in-time monthly snapshot table, label table, campaign history, quality checks | Data access, Q4 | Versioned snapshot and label tables; data dictionary | Reproducible rebuild of a past month; reconciliation passes | 4–8 weeks |
| 3 Analysis / EDA | Prevalence by month, missingness, label maturity, segment profiles, A2 descriptive findings | Phase 2 | EDA report; refined plan | Findings reviewed with client | 2–3 weeks |
| 4 Modelling | Baselines, candidates, ablations, calibration (E1–E6) | Phases 2–3 | Experiment log, candidate models | Beats agreed bar on validation folds | 4–6 weeks |
| 5 Validation | Robustness, fairness, locked test, model documentation, independent validation | Phase 4 | Validation report, model card | Passes acceptance criteria; sign-off | 3–4 weeks |
| 5b Randomised pilot (parallel) | Design, approval, launch three monthly waves, 90-day outcomes | Q5, Phase 4 first model or baseline list | Pre-registered analysis plan, experiment results | Integrity checks pass; effect with CI reported | ~6 months to the primary readout; ~15 months to full 12-month follow-up (parallel with phases 6–7) |
| 6 Deployment | Batch pipeline, CRM integration, suppression rules, fallback | Phase 5 | Production pipeline, runbook | Shadow run matches offline | 4–6 weeks |
| 7 Monitoring and uplift | Monitoring, quarterly retrain, uplift model from pilot data, second validation wave | Pilot data | Dashboards, retrain schedule, uplift evaluation | Thresholds live; uplift beats risk ranking or is dropped | Ongoing |

## 20. Decision Log

| # | Decision / Recommendation | Rationale | Alternatives considered | Key assumptions | Risk | Validation method |
|---|---|---|---|---|---|---|
| D1 | Split the request into A1 predict, A2 drivers, A3 offer effect | Each needs a different method and evidence | One churn model for everything | Client wants decision value | Client expects the model to answer "drivers" and "offers" | Review framing with client |
| D2 | Target = 3-month voluntary closure on month-end snapshots | Matches decision and horizon | Survival; dormancy target | Q1, Q3 | Wrong label | Reason-code audit |
| D3 | Select models by precision/lift@20,000; judge the programme by net value from the experiment | Capacity-constrained ranking; imbalance | AUC, accuracy | K = 20,000 | Ignores uplift | Compare to baselines; experiment |
| D4 | No default resampling; calibrate after any weighting | ~4% positives is moderate; keep probabilities honest | SMOTE / under-sampling | — | Weak ranking | X3 |
| D5 | Out-of-time rolling validation with 3-month embargo | Mirrors deployment, overlapping label windows | Random k-fold | About 36 months of data (minimum 30) | Short history | Fold diagnostics |
| D6 | Start with logistic, then GBM; survival as challenger | Simple first; complexity must earn its place | Deep learning | — | Over-engineering | X1–X2, X7 |
| D7 | Randomised experiment for offers | Only credible way to separate offer effect from selection | Observational AIPW; RDD | Q5 approved | Underpowered or refused | Power check; integrity checks |
| D8 | Drivers reported as associations, with causal follow-up for actionable levers | Prevents over-claiming | SHAP as causes | — | Misinterpretation | Language review |
| D9 | Exclude or route pending closure requests | They are near-label | Include | Contact-centre tags exist | Lost recall | X ablation |
| D10 | Uplift model after pilot data exists | Targets persuadables | Keep risk ranking | Randomised data | Noisy uplift | Qini on held-out randomised wave |
| D11 | Monthly batch with suppression rules, fallback and permanent holdout | Operationally simple; supports measurement | Real-time | Monthly cadence suffices | Slow reaction | Shadow run |

## 21. References

No external sources were consulted for this draft. Regulatory references named in §17 are for orientation and are **to be verified** with the client's compliance and model-risk teams before being relied on.
