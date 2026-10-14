# Evaluation Metrics Catalog

Pick metrics in four tiers: **primary** (one; drives model selection), **secondary** (guards
against gaming the primary), **diagnostic** (explain behaviour), **business** (value to the client).
Always compute every metric on the *same* validation population and windows, and report fold
dispersion (mean ± sd or interval), not just a point.

## 1. Regression

| Metric | Formula | Use when | Avoid / caveat |
|---|---|---|---|
| MAE | mean(|y − ŷ|) | Errors cost linearly; robust to outliers; median-optimal | Scale-dependent; not comparable across targets |
| RMSE | sqrt(mean((y − ŷ)²)) | Large errors disproportionately costly; mean-optimal | Dominated by outliers |
| MAPE | mean(|y − ŷ| / |y|) | Stakeholders want %; y far from 0 | Undefined/explodes near 0; asymmetric; **avoid for intermittent demand** |
| sMAPE | mean(2|y − ŷ| / (|y|+|ŷ|)) | Symmetric % | Still unstable near 0; contested interpretation |
| R² | 1 − SSE/SST | Explained variance communication | Not an error metric; can be high with useless predictions on trending data |
| Quantile (pinball) loss | Σ max(τ(y−q), (τ−1)(y−q)) | Decisions depend on a quantile (safety stock, capacity) | Need one per quantile |
| RMSLE | RMSE on log1p | Multiplicative errors, right-skewed targets | Under-penalises under-prediction of large values |

## 2. Classification

| Metric | Definition | Use when | Caveat |
|---|---|---|---|
| Confusion matrix + cost matrix | TP/FP/FN/TN × business costs | **Always** — the basis of threshold choice | Requires cost estimates from client |
| Precision | TP/(TP+FP) | Cost of acting on FP is high (manual review, false fraud alerts) | Depends on prevalence |
| Recall (sensitivity) | TP/(TP+FN) | Missing a positive is costly (sepsis, default, fraud) | Trivially 1 if you flag all |
| Specificity | TN/(TN+FP) | Clinical tests | — |
| F1 / Fβ | Harmonic mean; β>1 weights recall | Single threshold summary when costs unknown | Ignores TN; threshold-dependent; **prefer explicit costs** |
| ROC-AUC | P(score+ > score−) | Ranking quality, balanced-ish classes | Optimistic under heavy imbalance; insensitive to calibration |
| PR-AUC / Average Precision | Area under precision–recall | **Imbalanced data** (fraud, rare disease) | Baseline equals prevalence — always report prevalence alongside |
| Precision/Recall@k, lift@k | Metrics in top-k scored | **Capacity-constrained actions** (k calls/day, k investigations) | Choose k from real capacity |
| Log loss | −mean(y log p + (1−y) log(1−p)) | Probabilities used directly (pricing, expected loss) | Punishes over-confidence heavily |
| Brier score | mean((p − y)²) | Probability accuracy, decomposable | Low values easy with rare events — compare to prevalence Brier |
| Calibration (reliability curve, ECE, calibration slope/intercept) | Predicted vs observed rates by bin | Any use of probabilities; clinical risk; PD | Bins sensitive; use slope/intercept too |
| KS statistic, Gini (=2·AUC−1) | Max separation of cumulative distributions | **BFSI scorecard convention** | Report with AUC for comparability |
| Balanced accuracy, MCC | — | Imbalance, single-number summary | Less interpretable to business |
| Accuracy | (TP+TN)/N | Only balanced classes with symmetric cost | **Misleading under imbalance** — never primary for churn/fraud/rare disease |

Threshold selection: choose threshold by maximising expected value
`EV = TP·benefit − FP·cost_fp − FN·cost_fn` subject to capacity, on the **validation** set; freeze it
before test. Report metrics at the chosen threshold plus threshold-free metrics.

## 3. Forecasting

| Metric | Formula / description | Use when | Caveat |
|---|---|---|---|
| MAE / RMSE per horizon | As above, by horizon h | Always report by horizon | Aggregate hides degradation with h |
| WAPE (wMAPE) | Σ|y − ŷ| / Σ|y| | Retail/supply aggregates; volume-weighted | Dominated by high-volume items; report alongside item-level |
| MASE | MAE / MAE of (seasonal) naive in-sample | **Cross-series comparison**; intermittent demand-safe | Interpretation: <1 beats naive |
| RMSSE | Scaled RMSE (M5 competition style) | Many series with different scales | — |
| Bias (mean error, tracking signal) | Σ(ŷ − y)/Σy | Inventory: systematic over/under-forecast drives stock-outs/overstock | Low MAE can hide strong bias |
| Pinball loss / CRPS | Probabilistic accuracy | Quantile/probabilistic forecasts | — |
| Interval coverage & width | % actuals within PI; mean width | Planning with uncertainty | Coverage without width is gameable |
| Business: service level, stock-out rate, inventory cost, lost sales | Simulated from forecasts + policy | The real objective | Needs inventory policy simulation |

**Censored demand warning:** during stock-outs, sales ≠ demand. Exclude, flag or impute unconstrained demand before scoring.

## 4. Ranking & recommendation

| Metric | Use | Caveat |
|---|---|---|
| NDCG@k | Graded relevance, position-aware | Needs relevance labels |
| MAP@k, MRR | Binary relevance; first relevant hit | — |
| Hit rate / Recall@k | Coverage of relevant items | — |
| Coverage, diversity, novelty | Avoid popularity collapse | — |
| Online: CTR, conversion, revenue per session | True value | Requires A/B test; offline-online gap is common |

## 5. Survival

Harrell's / Uno's C-index (discrimination with censoring), time-dependent AUC at clinically
relevant t, integrated Brier score, calibration at fixed horizons. Report horizon-specific metrics.

## 6. Clustering / segmentation

Silhouette, Davies–Bouldin, Calinski–Harabasz (internal); **stability** across bootstrap
resamples (ARI between runs); business actionability (segment size, distinctiveness on
business KPIs, ability to target). Internal indices alone never justify a segmentation.

## 7. NLP / CV

Classification metrics as above (macro vs micro averaging stated explicitly); NER/extraction:
entity-level precision/recall/F1 (exact vs partial match stated); detection: mAP@IoU; segmentation:
IoU/Dice; generation/summaries: human evaluation rubric + task-specific checks (faithfulness), not
BLEU/ROUGE alone.

## 8. Causal & inferential

Point estimate of the estimand (ATE/ATT/CATE/DiD effect) with confidence interval; covariate
balance (standardised mean difference < 0.1 after weighting/matching); overlap/positivity diagnostics
(propensity distributions); placebo/negative-control outcomes; pre-trend tests for DiD; first-stage F
for IV; sensitivity analysis (E-value, Rosenbaum bounds). For uplift: Qini/AUUC.

## 9. Fairness & subgroup metrics (mandatory in Healthcare and BFSI)

Report primary metric and calibration by protected/relevant subgroup (age band, sex, region,
income band, channel). Consider: demographic parity difference, equal opportunity (TPR) difference,
equalised odds, calibration within groups, adverse impact ratio (four-fifths rule, BFSI). Note that
fairness criteria can be mutually incompatible — choose with client/compliance and document.

## 10. Rules

- Never compare metrics computed on different populations, windows or label definitions without qualification.
- Never report accuracy alone for imbalanced problems.
- Always report the baseline on the same metric and windows.
- Report uncertainty across folds/windows (or bootstrap CIs).
- State the metric the model was **optimised** on vs. the metric it is **selected** on vs. the metric the **business** cares about.
