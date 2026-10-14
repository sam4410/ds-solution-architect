# Validation Strategy Catalog

**Principle:** the validation scheme must simulate deployment. Ask: *at the moment the model is
used, what data exists, which entities are new, and how far ahead are we predicting?* Then build
splits that reproduce exactly that situation.

## 1. Choose by data-generating process

| Data structure | Default strategy | Estimates | Never do |
|---|---|---|---|
| i.i.d. rows, stable over time | Stratified k-fold CV (k=5/10) + held-out test | Generalisation to similar new rows | — |
| Repeated rows per entity (customer, patient, store, device) | **Grouped k-fold** (GroupKFold / StratifiedGroupKFold) by entity | Performance on *new* entities | Random row split (entity leakage inflates scores) |
| Temporal ordering matters (anything deployed forward in time) | **Out-of-time** split: train ≤ T, validate (T, T+v], test (T+v, T+v+t] | Performance on future periods | Random split; shuffling |
| Time series forecasting | **Rolling-origin / walk-forward** (expanding or sliding window) | Performance per horizon across multiple forecast origins | Single split only; k-fold with shuffling |
| Temporal + entity | Out-of-time **and** grouped (new entities in future) — or report both "existing entity, future time" and "new entity" | Realistic mix at deployment | — |
| Spatial / multi-site (hospitals, branches, stores) | Leave-one-site-out / spatial block CV | Transfer to unseen sites | Mixing sites when deployment is to new sites |
| Small n with hyperparameter tuning | **Nested CV** (inner tune, outer evaluate) | Unbiased estimate including tuning | Tuning and reporting on same folds |
| Overlapping label windows (e.g., 30-day outcomes, rolling features) | Purged + embargoed time splits (gap ≥ label horizon) | Avoids leakage through overlapping windows | Adjacent train/test with overlapping outcome windows |
| External validation | Different hospital/region/time/vendor dataset | Transportability | Claiming generality from internal CV only |

## 2. Walk-forward design (forecasting & any temporal model)

Specify all of:
- **Forecast origin(s):** dates when forecasts are made (e.g., every Monday for the last 26 weeks).
- **Horizon(s):** h = 1…H in the deployment unit (weeks/days/months).
- **Training window:** expanding (all history) vs sliding (last W periods — use when regimes change).
- **Retraining cadence:** match deployment (e.g., retrain monthly, forecast weekly).
- **Gap / embargo:** periods between training end and forecast start if data arrives with latency
  (e.g., sales finalised with 3-day lag → gap of 1 week).
- **Number of folds/origins:** enough to cover seasonality (≥ one full seasonal cycle where possible).
- **Evaluation:** metric per horizon and per origin; aggregate with dispersion.
- **Data vintage:** use values *as known at the origin* (point-in-time), not later-corrected values.

```
Expanding window (H = 4, step = 4)
|== train ========|-gap-|.. test h1..h4 ..|
|== train ============|-gap-|.. test ..|
|== train ================|-gap-|.. test ..|
Sliding window
   |== train (W) ==|-gap-|.. test ..|
       |== train (W) ==|-gap-|.. test ..|
```

## 3. Split hygiene

- **Locked test set:** created once, touched once, at the end. Any decision taken after seeing test results invalidates it as a test.
- **Validation set** is for model selection, early stopping, threshold choice, calibration fitting.
- **All learned transforms** (imputers, scalers, encoders, feature selection, resampling like SMOTE, target encoding, PCA) are fit **inside** each training fold via a pipeline.
- **Resampling for imbalance** applied only to training folds — never to validation/test.
- **Stratify** on target (and important strata) for classification when i.i.d.
- **De-duplicate** before splitting; check near-duplicates (same patient different encounter IDs; same customer multiple accounts).
- **Record split definitions** (dates, group IDs, seeds) as versioned artefacts.

## 4. Additional robustness validations

| Check | What it reveals |
|---|---|
| Performance by time slice (month/quarter) | Drift and instability |
| Performance by subgroup / site / segment | Hidden failure modes, fairness |
| Train-vs-validation gap | Overfitting |
| Fold-to-fold variance | Reliability of the estimate; whether model differences are real |
| Adversarial validation (classifier to distinguish train vs test rows) | Covariate shift between periods/sites |
| Backtest under known shocks (COVID, policy change, promo calendar change) | Robustness to regime changes |
| Label-delay simulation (score only on matured labels) | Optimism from immature labels |
| Permutation of target (should collapse to chance) | Leakage or pipeline bug if it does not |

## 5. Statistical comparison of models

- Compare models on identical folds/windows; use paired comparisons (per-fold differences).
- Use corrected resampled t-test (Nadeau–Bengio) or bootstrap of paired differences; for classifiers on one test set, McNemar's test; for AUCs, DeLong's test; for forecasts, Diebold–Mariano.
- Pre-declare the minimum practically meaningful improvement.
