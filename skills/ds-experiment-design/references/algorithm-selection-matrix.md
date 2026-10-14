# Algorithm Selection Matrix

Use to build a **prioritised** candidate list. Always list a baseline first, then the simplest
credible model, then more complex candidates *only if justified* by data scale, signal structure
or a demonstrated baseline gap. Never invent expected scores.

Legend — Interp.: interpretability (H/M/L). Data: data volume needed (S/M/L). Compute (L/M/H).

## 1. Baselines (mandatory — pick ≥1 per task)

| Task | Baseline | What it tells you |
|---|---|---|
| Forecasting | Naive (last value), seasonal-naive (same period last season), moving average, drift | Whether the model beats "do nothing clever"; MASE is scaled to naive |
| Regression | Mean / median predictor; simple linear model on 3–5 obvious features | Signal exists beyond central tendency |
| Classification | Prevalence / majority class; current business rule; logistic regression on few features | Lift over the rule the client already uses |
| Ranking / recsys | Popularity, recency, "bought together" co-occurrence | Personalisation value |
| Anomaly | Z-score / IQR rules, business thresholds | Whether ML adds over rules |
| NLP | Keyword/regex rules; TF-IDF + logistic regression; zero-shot LLM | Cost/benefit of heavier models |
| CV | Pretrained backbone + linear probe | Need for fine-tuning |
| Survival | Kaplan–Meier (no covariates); Cox with few covariates | Covariate value |
| Causal | Naive difference in means (explicitly flagged as biased) | Size of confounding adjustment |

## 2. Tabular classification & regression

| Algorithm | Plausible when | Assumptions / needs | Strengths | Weaknesses / failure modes | Interp. | Data | Compute | Key hyperparameters | Reject if |
|---|---|---|---|---|---|---|---|---|---|
| Linear / logistic regression (+L1/L2/elastic net) | Baseline; regulated settings; small n; need coefficients | Linearity in (transformed) features, low multicollinearity for interpretation, scaling for regularisation | Transparent, stable, calibrated (logistic), fast | Misses interactions/non-linearity unless engineered; sensitive to outliers | H | S | L | C/alpha, l1_ratio, class_weight | Large, persistent gap vs trees after feature engineering |
| GAM / EBM (explainable boosting) | Need non-linear but explainable effects (credit, clinical) | Additive effects (+ limited pairwise) | Near-GBM accuracy on many tabular tasks with shape-function interpretability | Slower training; limited interactions | H | M | M | n bins, interactions, learning rate | Strong high-order interactions dominate |
| Decision tree | Rule extraction, communication | — | Readable rules | High variance, overfits | H | S | L | max_depth, min_samples_leaf | Used as final model when accuracy matters |
| Random forest | Robust default, mixed features, moderate n | — | Little tuning, robust to outliers, OOB estimate | Larger models, poorer calibration, extrapolation impossible | M | M | M | n_estimators, max_features, min_samples_leaf, max_depth | GBM clearly better at equal validation |
| Gradient boosting (XGBoost / LightGBM / CatBoost) | Default strong learner for tabular data | Enough rows (typically thousands+); careful validation | State-of-the-art tabular accuracy, handles missing values, monotonic constraints (credit) | Overfits small data, needs tuning, poorer calibration, can memorise leakage | M (with SHAP) | M–L | M | learning_rate, n_estimators (early stopping), max_depth/num_leaves, min_child_weight/min_data_in_leaf, subsample, colsample, reg_lambda/alpha, scale_pos_weight | No gain over GAM/logistic → prefer simpler |
| CatBoost specifically | Many high-cardinality categoricals | — | Ordered target statistics reduce target-encoding leakage | Slower than LightGBM | M | M–L | M | depth, l2_leaf_reg, learning_rate, iterations | — |
| k-NN | Small, low-dim, similarity-driven | Meaningful distance, scaling | Simple | Curse of dimensionality, slow inference | M | S | L–M | k, metric, weights | High-dimensional data |
| SVM | Small–medium n, high-dim sparse (text) | Scaling | Strong margins | Scales poorly in n, no native probabilities | L | S–M | M–H | C, kernel, gamma | n > ~100k |
| Neural nets (MLP, TabNet, FT-Transformer) | Very large tabular data, multimodal fusion | Large n, careful regularisation | Can fuse text/image/tabular | Usually do not beat GBMs on mid-size tabular; costly; opaque | L | L | H | lr, depth, width, dropout, weight decay, batch size | Not beating tuned GBM on same splits |

## 3. Time-series forecasting

| Algorithm | Plausible when | Strengths | Weaknesses | Key hyperparameters |
|---|---|---|---|---|
| ETS (exponential smoothing, Holt-Winters) | Few series, clear level/trend/seasonality | Fast, robust, prediction intervals | Limited exogenous variables; one model per series | error/trend/seasonal type, damping |
| ARIMA / SARIMA(X) | Autocorrelation structure, few exogenous drivers | Interpretable, intervals | Stationarity assumptions, manual identification, slow at scale | (p,d,q)(P,D,Q,s), exogenous set |
| Theta / TBATS / MSTL | Multiple seasonalities (hourly/daily/weekly) | Handles complex seasonality | Exogenous limited | seasonal periods |
| Prophet-style additive models | Business series with holidays, changepoints; communication | Easy holiday handling | Often beaten by ETS/GBM; changepoint overfitting | changepoint prior scale, seasonality modes |
| Croston / SBA / TSB | Intermittent demand (many zeros) | Designed for sparse demand | Point forecasts only | smoothing alpha |
| Global GBM with lag/rolling/calendar features (LightGBM) | Many related series (SKU×store), rich exogenous drivers (price, promo) | Cross-learning, scalable, handles covariates | Needs careful lag construction (leakage!), recursive vs direct strategy choice | as GBM + lag set, horizon strategy |
| Global deep models (N-BEATS, N-HiTS, TFT, DeepAR) | Thousands of series, long history, probabilistic needs | Probabilistic forecasts, multi-horizon | Data hungry, costly, harder to debug | lookback, horizon, hidden size, dropout, lr |
| Foundation time-series models (zero-shot) | Cold-start, quick benchmark | No training | Unknown behaviour on domain specifics; verify licence and data residency | context length |
| Hierarchical reconciliation (MinT, bottom-up, top-down) | Forecasts needed at several aggregation levels | Coherent forecasts | Added complexity | reconciliation method |

Horizon strategy: recursive (one model, feed predictions) vs direct (one model per horizon) vs multi-output — choose by horizon length and error accumulation.

## 4. Other domains

| Domain | Candidate sequence (simple → complex) | Notes |
|---|---|---|
| Survival | Kaplan–Meier → Cox PH (check proportional hazards) → AFT models → random survival forest / gradient-boosted survival → DeepSurv | Handle censoring properly; never drop censored rows |
| Anomaly / fraud | Rules → isolation forest / LOF / robust z-scores → autoencoders → supervised GBM once labels mature | Label delay (chargebacks) is large; evaluate at fixed alert capacity |
| Clustering | k-means (scaled) → GMM → hierarchical → DBSCAN/HDBSCAN | Validate with stability and business usefulness, not only silhouette |
| Recommendation | Popularity → item-item CF / co-occurrence → matrix factorisation (ALS) → two-tower / sequential models → LTR re-ranker | Offline metrics are weak proxies; plan online test |
| NLP classification | Rules → TF-IDF + linear → fine-tuned small transformer → LLM (zero/few-shot or fine-tuned) | Compare cost/latency/privacy; PHI/PII cannot leave approved boundary |
| Information extraction | Regex/dictionary → CRF/spaCy NER → transformer NER → LLM extraction with schema validation | Measure field-level precision/recall |
| Computer vision | Pretrained CNN/ViT linear probe → fine-tune → detection/segmentation models | Site/device shift is a major risk (medical imaging) |
| Uplift / heterogeneous effects | Two-model (T-learner) → S/X-learner → causal forests / DR-learner | Requires randomised or well-identified data |
| Optimisation | Rule + ranking with capacity cut-off → integer/linear programming → stochastic optimisation | Optimise expected business value, not model metric |

## 5. Trade-off narrative template

For each shortlisted algorithm, write:
> **Why plausible:** … **Needs:** … **Main risk on this data:** … **We will reject it if:** (e.g., does not beat
> baseline by the agreed margin on the locked walk-forward windows, or calibration error exceeds X, or
> explanations unacceptable to risk/compliance).

Prefer simpler model when the performance gap is within the **noise band across folds**
(e.g., overlapping fold-wise intervals) — complexity must buy something measurable.
