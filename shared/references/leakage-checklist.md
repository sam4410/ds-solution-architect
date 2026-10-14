# Leakage Audit Checklist

Run for **every** predictive plan. For each item record: *Applies? (Y/N/Unknown) · Evidence · Mitigation · Owner*.
Suspiciously good results (e.g., AUC > 0.95 on a hard human problem, or a single feature with
dominant importance) are a leakage alarm until proven otherwise.

## A. Target leakage (post-outcome information)
- [ ] Every feature has a documented **availability timestamp** ≤ prediction point.
- [ ] No feature is a consequence/proxy of the outcome (e.g., "collections call made" for default; "discharge disposition = hospice" for mortality; "refund issued" for fraud; "account closed date" for churn).
- [ ] Aggregates (counts, averages, rolling windows) are computed only from data before the prediction point.
- [ ] Status fields are point-in-time (snapshot/as-of tables or SCD Type-2), not current values overwritten later. Watch for
      **resolution/status updates** on complaints, tickets, claims, disputes and cases: a record resolved *after* the prediction point must appear as open.
- [ ] Codes assigned after the fact (final diagnosis codes, billing codes, chargeback reasons) are excluded or time-gated.

## B. Train/test contamination
- [ ] Same entity (patient, customer, account, household, device, store) does not appear in both train and test when deployment targets new entities.
- [ ] Exact and near-duplicate records removed before splitting.
- [ ] Augmented samples (images, text paraphrases) of one original are in the same fold.
- [ ] Linked entities (family, joint accounts, same merchant) considered for grouping.

## C. Temporal leakage
- [ ] Splits respect time; no shuffling across time for temporal deployment.
- [ ] Future-derived features excluded (e.g., centred moving averages, full-period normalisation, future promotions not known at origin).
- [ ] Gap/embargo ≥ label horizon when outcome windows overlap.
- [ ] Data vintage: features use values as recorded at the time, not later corrections/restatements.

## D. Preprocessing leakage
- [ ] Imputation, scaling, encoding, feature selection, dimensionality reduction, target encoding, resampling (SMOTE) all fit within training folds only (pipeline).
- [ ] Vocabulary/tokenisers/embeddings fine-tuned only on training data (NLP).
- [ ] Outlier thresholds and binning computed on training data only.

## E. Evaluation leakage
- [ ] Test set untouched until final evaluation; not used for tuning, threshold choice, early stopping, feature selection.
- [ ] Number of test evaluations is logged; repeated peeking is disclosed.
- [ ] Hyperparameter search budget and selection criteria fixed in advance.

## F. Label issues
- [ ] Label delay understood (chargebacks 30–120 days; default definitions 90+ DPD over 12 months; readmission 30 days); immature labels excluded from training and evaluation windows.
- [ ] Censoring handled (survival methods, or exclude units without full follow-up — and report the selection effect).
- [ ] Label definition stable over time (coding changes, policy changes).
- [ ] Selective labels: outcomes only observed for treated/approved units (e.g., default only for approved loans → reject inference problem; fraud labels only for investigated cases).

## G. Population & deployment mismatch
- [ ] Training population = deployment population (inclusion/exclusion logic identical).
- [ ] Policy/feedback loops: past model or rule decisions influenced who got which outcome.
- [ ] Site/geography/channel shift assessed.

## H. Causal vs correlation guardrails
- [ ] Feature importances / SHAP described as **associations used by the model**, not causes.
- [ ] Any "driver" analysis intended for intervention is routed to the causal-inference workflow.
- [ ] Proxy variables for protected attributes identified (pincode/zip → ethnicity/income).

## Quick automated checks (when data is available)
1. Single-feature models: any feature alone giving near-perfect score → investigate.
2. Timestamp audit: `feature_time > prediction_time` count per feature (should be 0).
3. Entity overlap count between train and test.
4. Target-shuffle test: model on shuffled labels must score ≈ chance.
5. Adversarial validation between train and test periods.
