---
name: ds-validation-leakage
description: Designs train/validation/test strategy and leakage controls that mirror deployment. Chooses between stratified k-fold, grouped splits, out-of-time splits, rolling-origin / expanding- and sliding-window walk-forward backtests, purged and embargoed splits, leave-site-out, nested CV and external validation; fully specifies forecast origins, horizons, windows, retraining cadence and gaps; and runs a case-specific leakage audit (target leakage, entity overlap, temporal leakage, preprocessing outside folds, label delay, selective labels, test-set reuse) plus correlation-vs-causation guardrails. Use when asked about "train-test split", "walk-forward test", "backtesting", "out-of-sample validation", "data leakage", or when ds-solution-plan calls for validation.
---

# DS Validation Design & Leakage Audit

The validation scheme must reproduce the situation in which the model will be used: what data exists
at that moment, which entities are new, and how far ahead the prediction is made.

## Load as needed
- `references/validation-strategy-catalog.md`: strategy by data structure, walk-forward specification, split hygiene, robustness checks and model comparison tests. **Always read.**
- `references/leakage-checklist.md`: the full audit. **Always read.**

## Workflow

1. **Describe the deployment scenario** in one paragraph: when scoring happens, what data is available (and its latency), whether entities are new or returning, and whether sites or regions are new.
2. **Identify the data structure**: i.i.d., repeated entities, temporal, spatial or multi-site, overlapping label windows, small n with tuning.
3. **Choose the split strategy** from the catalog and justify it against the deployment scenario. If combining
   (e.g., temporal plus grouped), say what each part estimates. **Never** use random splits for temporal or grouped
   data without a written justification.
4. **Specify the windows concretely**:
   - Temporal: train/validation/test date boundaries, or rules relative to the data end date.
   - Walk-forward: forecast origins (count and spacing), horizons, expanding vs sliding window, retraining cadence,
     gap or embargo (≥ label horizon or data latency), point-in-time data vintage, and coverage of seasonal cycles.
     Include a small ASCII timeline.
   - Grouped: the grouping key(s) and any linked entities.
   - Repeated-entity snapshot designs (customer-month, patient-encounter) evaluated out-of-time: also add an
     **entity-disjoint sensitivity fold** (entities unseen in training) to estimate performance on new entities. Report both.
   - Overlapping outcome windows across consecutive origins: state the gap rule explicitly (e.g., the last training origin's
     target must be fully observed before the evaluation origin).
5. **Split hygiene**: a locked test set, pipelines that fit transforms in-fold, resampling only in training folds, deduplication before splitting, stratification, and versioned split definitions.
6. **Leakage audit**: walk through checklist sections A–H. For each item that plausibly applies **to this case**, name the specific
   field or process at risk (e.g., "discharge disposition", "collections flag", "promo plan updated after origin") and the mitigation.
   Mark items that do not apply as N/A briefly, and don't pad.
7. **Robustness validations**: choose the relevant ones (time slices, subgroups, adversarial validation, target-shuffle test, label-maturity simulation).
8. **Causation guardrail**: state that feature importances and SHAP values are associations, and route any "drivers" question to ds-statistical-inference.

## Output contract
```
### Deployment scenario
### Split strategy & rationale
### Window specification        (table and ASCII timeline)
### Split hygiene rules
### Leakage audit               (pipe table: Risk | Applies? | Where it could occur in this case | Mitigation | Owner)
### Robustness validations
### Facts / Assumptions / Open questions
### Decision rows               (pipe table: Decision | Rationale | Alternatives | Assumptions | Risk | Validation method)
```

## Guardrails
- Each validation strategy must state which deployment situation it estimates.
- If data timestamps or availability are unknown, make "obtain feature availability timestamps" a blocking open question.
- Never allow tuning, threshold selection or early stopping on the test set.
