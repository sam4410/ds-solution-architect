# Preprocessing & Feature Engineering Playbook

Every step in the plan must be written as a row:
**Step · Rationale · Applies when · Proposed method · Risks (bias/leakage/signal loss) · Validation check**.
Every learned step is fit on training folds only (inside a pipeline).

## 1. Missing values

| Situation | Method | Risks | Validation check |
|---|---|---|---|
| Missingness informative (e.g., lab not ordered = clinician judged low risk; income missing = self-employed) | Keep indicator flag + simple impute | Indicator may encode process/policy that changes at deployment | Compare model with/without indicators; check missingness rate stability over time |
| MCAR/MAR, low rate (<5%) | Median/mode impute (train-only) | Shrinks variance | Distribution before/after |
| Moderate MAR | Iterative / KNN imputation; model-based | Complexity; leakage if fit on all data | Fit inside CV |
| Tree-based models | Native missing handling (XGBoost/LightGBM) | — | — |
| Inference / causal analysis | Multiple imputation (MICE) with Rubin's rules; sensitivity analysis | Complete-case analysis biases estimates unless MCAR | Compare complete-case vs MI estimates |
| Time series gaps | Distinguish true zero vs not recorded; forward-fill only for state variables | Forward-filling outcomes fabricates data | Gap audit |
| >40–60% missing | Consider dropping or using only indicator | Loss of signal | Business review |

Always report missingness by feature, over time, and by subgroup — differential missingness is a bias source (e.g., fewer labs recorded at rural sites).

## 2. Outliers & invalid values
- Separate **invalid** (impossible: age 250, negative quantity not a return) → fix/remove with rule log; from **extreme but valid** (high-value customer, super-spreader SKU) → keep; use robust losses, winsorise (train-derived percentiles), or log-transform.
- Never drop outliers in the target for evaluation data — that inflates scores.
- In fraud/anomaly tasks, outliers *are* the signal.

## 3. Duplicates & entity resolution
- Exact duplicates (system re-sends), near-duplicates (same transaction with different IDs), entity duplicates (same customer multiple IDs → master data / fuzzy matching).
- Define entity keys before splitting; group splits depend on them.

## 4. Data types, encoding & scaling

| Feature type | Method | Notes |
|---|---|---|
| Low-cardinality categorical | One-hot | Handle unseen categories ("other") |
| High-cardinality categorical (merchant, SKU, ICD code, pincode) | Target encoding with out-of-fold + smoothing; CatBoost ordered encoding; frequency encoding; hierarchical grouping (ICD chapter, category level) | **Target encoding leaks if not out-of-fold** |
| Ordinal | Integer mapping with order | — |
| Numeric for linear/distance/NN models | Standardise / robust scale (train stats) | Trees don't need scaling |
| Skewed positive (amounts, counts) | log1p, Box-Cox/Yeo-Johnson | Interpret back-transformed predictions carefully (bias correction for log targets) |
| Dates | Extract calendar parts, time-since-event, tenure, recency | Use reference = prediction point |
| Geography | Hierarchical levels, distance features | Proxy discrimination risk (BFSI) |

## 5. Class imbalance & rare outcomes
Order of preference: (1) choose correct metric (PR-AUC, recall@k, cost); (2) class weights / `scale_pos_weight`;
(3) threshold tuning on validation; (4) resampling (undersampling majority, SMOTE) **only in training folds** —
and recalibrate probabilities afterwards because resampling distorts them. Report prevalence in every split.

## 6. Feature engineering patterns
- **Temporal aggregates:** counts/sums/means over lookback windows (7/30/90/365 days) ending at prediction point; recency, frequency, monetary (RFM); trends (slope), volatility.
- **Ratios & domain features:** utilisation (balance/limit), DTI, LOS vs expected LOS, price relative to category average, promo depth.
- **Time-series features:** lags (≥ horizon for direct strategy), rolling stats on lagged series, calendar/holiday/festival flags (Diwali, Eid, Christmas, regional festivals), price/promo, weather.
- **Interaction features** only where hypothesised; trees learn many automatically.
- **Text:** cleaning, de-identification (PHI/PII), tokenisation, TF-IDF or embeddings; domain vocabularies (clinical abbreviations).
- **Images:** resizing, normalisation using pretrained model stats, augmentation (train only), DICOM handling, site/device metadata.

## 7. Feature selection
Filter (variance, correlation, mutual info) → embedded (L1, tree importance) → wrapper (RFE) — all inside CV.
Prefer domain-driven feature groups and **ablation by group** over automated selection on small data.
BFSI scorecards: IV/WoE binning with monotonicity constraints is the established convention.

## 8. Target construction
- Precise definition, window and exclusions (e.g., 90+ DPD within 12 months on book; readmission excluding planned).
- Label delay & maturity: only use cohorts whose outcome window has fully elapsed.
- Censoring: survival methods or explicit exclusion with reported effect.
- **Sales ≠ demand** during stock-outs; returns and cancellations netting rules.
- Verify label definition stability across years/systems.

## 9. Aggregation, alignment & resampling
- Align all sources to the analytical grain; document aggregation functions.
- Time zones, fiscal vs calendar periods, week definitions (ISO vs retail 4-4-5 calendar).
- Point-in-time joins (as-of joins) for slowly changing attributes.

## 10. Lineage & reproducibility
Versioned raw extracts (hash/date), transformation code in pipelines, data dictionary, feature
definitions with availability timestamps, random seeds, environment versions.

## 11. When preprocessing distorts the estimand
- Excluding hard-to-measure units changes the population (survivorship/selection).
- Winsorising the outcome changes the estimand from mean to trimmed mean.
- Log-transforming the outcome changes effects from additive to multiplicative.
- Imputing the outcome then testing on it inflates certainty.
- Deduplicating at the wrong grain changes the unit of analysis.
State such changes explicitly in the plan.
