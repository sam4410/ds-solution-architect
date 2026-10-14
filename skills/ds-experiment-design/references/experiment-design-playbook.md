# Experiment Design & Hyperparameter Playbook (model development)

## 1. Staged experiment plan

| Stage | Purpose | Exit criterion |
|---|---|---|
| E0 Data & target sanity | Row counts, target prevalence by period, leakage quick-checks, split integrity | Data contract signed off; leakage checks pass |
| E1 Baseline(s) | Establish the bar | Baseline metrics recorded on locked splits |
| E2 Simple candidates | Linear/logistic/GAM, ETS — with core features | Gap vs baseline quantified with fold dispersion |
| E3 Advanced candidates (if justified) | GBM, global forecasting, deep models | Beats E2 by ≥ pre-declared margin, else stop |
| E4 Feature-group ablations | Value of each data source (worth acquiring?) | Feature groups kept only if gain > noise and cost justified |
| E5 Hyperparameter optimisation | Tune shortlisted 1–2 models | Budget exhausted or plateau |
| E6 Robustness & subgroup | Time slices, sites, segments, fairness, stress tests | No unacceptable subgroup failure |
| E7 Calibration & threshold | Probability calibration (Platt/isotonic on validation), decision threshold | Calibration within tolerance; threshold frozen |
| E8 Locked test evaluation | One-shot final estimate | Report; no further tuning |

## 2. Experiment card (one per experiment)

| Field | Content |
|---|---|
| ID / name | E4.2 — add promo calendar features |
| Hypothesis | Promo features reduce WAPE at h=1–2 for promoted SKUs |
| Change tested | +promo_flag, promo_depth, days_to_promo |
| Fixed conditions | Model LightGBM v-config-07, same walk-forward origins, same seeds |
| Data / split | Splits v1.2 (origins 2025-W01…W26) |
| Metrics | Primary WAPE; secondary bias, MASE; by horizon & promo vs non-promo |
| Expected interpretation | Gain concentrated in promo weeks; no degradation elsewhere |
| Stopping rule | Accept if mean WAPE gain > fold sd and no segment worsens > 1pt |
| Result / decision | (filled after run) |

## 3. Hyperparameter search strategy

| Situation | Strategy |
|---|---|
| ≤3 important params, cheap model | Grid search (coarse → fine) |
| Many params, moderate budget | Random search (better coverage than grid for same budget) |
| Expensive model, ≤20 params | Bayesian optimisation (TPE e.g. Optuna; Gaussian processes) with early stopping / pruning (Hyperband/ASHA) |
| Deep learning | LR range test + schedule; then Bayesian/ASHA on few key params |
| Time series | Tune on walk-forward validation origins, never on test origins |

Budget: define trials or wall-clock up front. Small data → nested CV to avoid optimistic estimates.

## 4. Hyperparameter priorities (highest impact first)

| Model | Priority 1 | Priority 2 | Priority 3 |
|---|---|---|---|
| Logistic / linear | Regularisation strength (C/alpha) | Penalty type, l1_ratio | class_weight |
| Random forest | max_features, min_samples_leaf | n_estimators (more = more stable) | max_depth |
| XGBoost/LightGBM | learning_rate + n_estimators (early stopping), max_depth / num_leaves | min_child_weight / min_data_in_leaf, subsample, colsample_bytree | reg_lambda/alpha, scale_pos_weight, monotone constraints |
| CatBoost | depth, learning_rate | l2_leaf_reg | border_count, one_hot_max_size |
| SVM | C, gamma | kernel | — |
| k-NN | k | distance metric/weights | — |
| ETS / ARIMA | model form (information criteria within training) | seasonal period | damping |
| Neural nets | learning rate & schedule | width/depth, dropout, weight decay | batch size, optimiser |
| Global forecasting DL | lookback length, learning rate | hidden size, dropout | loss (quantile) |
| Clustering | k / min_cluster_size | distance, scaling | init |

## 5. Reproducibility & tracking
- Seeds (numpy, framework, CV split), package versions (lockfile), hardware notes.
- Data version (snapshot date + hash), split definition version, feature set version.
- Config files (YAML) per experiment; code commit hash.
- Experiment tracker (e.g., MLflow, Weights & Biases, or a versioned spreadsheet if nothing else): params, metrics per fold, artefacts (plots, models), notes.
- Model card for the selected model.

## 6. Model comparison rules
- Same folds/windows, same metric code, same population.
- Paired statistical comparison (see validation catalog §5).
- Prefer the simpler model if within noise band.
- Log every test-set touch.
