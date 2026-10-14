---
name: ds-statistical-inference
description: Plans statistical inference and causal analysis for data science questions. Defines estimands, null and alternative hypotheses, test or estimator choice with assumption checks (t-tests, ANOVA, chi-square, nonparametric, regression, mixed models, survival tests, bootstrap, permutation, Bayesian), effect sizes and confidence intervals, power and minimum detectable effect, multiple-testing control, A/B test design, and causal designs (randomised experiments, difference-in-differences, synthetic control, regression discontinuity, instrumental variables, propensity weighting, uplift), with explicit statements of what can and cannot be identified. Use when asked "is this difference significant", "hypothesis test", "A/B test design", "what is the impact of X", "does X cause Y", "correlation vs causation", or when ds-solution-plan detects inferential or causal questions.
---

# DS Statistical Inference & Causal Reasoning

Answer "is it real, how big is it, and did our action cause it?" with designs whose assumptions are
stated and checked. Never let predictive accuracy or feature importance stand in for causal evidence.

## Load as needed
- `references/statistical-testing-catalog.md`: test selector, assumptions, power, multiple testing, A/B checklist and reporting template. **Always read for inferential questions.**
- `references/causal-inference-designs.md`: estimands, DAGs, design selector, sensitivity analyses and domain notes. **Always read for causal questions.**

## Workflow

### For inferential questions (population differences or relationships)
1. Define the **estimand**, population, sampling unit and comparison.
2. State H₀ and H₁ (and sidedness, with justification), α, and the **minimum practically important effect**.
3. Check the design: independence or clustering, pairing, confounders that make a raw comparison unfair (case-mix, store size).
4. Choose the primary test or estimator, an assumption-check plan, and a robust fallback.
5. Do a power/MDE calculation, or report the MDE achievable with the available n. Show the inputs and mark them as assumptions.
6. Plan multiple-testing control (Holm or BH), and label confirmatory vs exploratory analyses.
7. Specify the reporting format: effect size + CI first, then p-value, then practical significance, then limitations.

### For causal or intervention questions
1. Define the treatment, outcome, population and estimand (ATE / ATT / CATE / LATE).
2. Sketch the **DAG** in text (confounders, mediators, colliders) and list the threats: confounding, selection,
   reverse causality, immortal time, regression to the mean, interference.
3. **Ask whether randomisation is feasible first.** If it is, design the experiment: randomisation unit, stratification,
   power/MDE, duration, guardrail metrics, SRM check, analysis plan, and ethics/regulatory approvals.
4. If not, choose a quasi-experimental design from the selector. State its identifying assumptions, how each will be
   probed (pre-trends, balance or SMD, overlap, density tests, first-stage F, placebo tests) and the sensitivity analysis (E-value, etc.).
5. State **what the design can and cannot identify**.

## Output contract
```
### Inferential / causal questions & estimands
### Hypotheses & decision thresholds
### Design & test/estimator      (pipe table: Question | Design/Test | Key assumptions | Checks | Fallback)
### Power / MDE
### Multiple testing & pre-registration
### Causal diagram (text) & threats      (causal only)
### What this can and cannot show
### Facts / Assumptions / Open questions
### Decision rows                (pipe table: Decision | Rationale | Alternatives | Assumptions | Risk | Validation method)
```

## Guardrails
- Report effect sizes with CIs. Never rely on p-values alone.
- Use "associated with" for observational adjusted estimates unless identification has been defended.
- Do not invent baseline rates or variances for power calculations. Use placeholders or illustrative inputs clearly labelled as such.
- In healthcare and BFSI, note ethics, regulatory and fair-treatment constraints on experiments.
