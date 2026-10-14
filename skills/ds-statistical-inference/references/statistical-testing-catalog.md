# Statistical Testing & Inference Catalog

Workflow for every inferential question:
1. State the **estimand** (what population quantity) and the **sampling unit**.
2. State H₀ and H₁ (one- or two-sided, justified *before* seeing data).
3. Choose α (default 0.05; stricter for many tests or high-stakes), and the **minimum effect of practical importance**.
4. Check design: independence, clustering, pairing, sample size/power.
5. Pick the test or estimator; check assumptions; have a robust/nonparametric fallback.
6. Report **effect size + confidence interval** first; p-value second.
7. Adjust for multiple comparisons; state what was pre-registered vs exploratory.

## 1. Test selector

| Question | Data | Parametric | Assumptions | Robust / nonparametric alternative | Effect size |
|---|---|---|---|---|---|
| Two independent groups, mean | Continuous | Welch's t-test (default over Student's) | Approx. normal means (CLT for n≳30/group), independence | Mann–Whitney U (tests distribution shift, not mean); bootstrap CI of mean difference; permutation test | Mean diff + CI; Cohen's d / Hedges' g |
| Paired / before–after | Continuous | Paired t-test | Normal differences | Wilcoxon signed-rank; bootstrap | Mean of differences + CI |
| >2 groups | Continuous | One-way ANOVA (Welch ANOVA if unequal variances) | Normality of residuals, independence | Kruskal–Wallis; permutation | η², ω² |
| Multiple factors | Continuous | Factorial ANOVA / linear regression | Linear model assumptions | Robust regression; GLM | Coefficients + CI |
| Two proportions | Binary | Two-proportion z-test; χ² | Expected counts ≥5 | Fisher's exact (small n) | Risk difference, risk ratio, odds ratio + CI |
| Paired binary | Binary | McNemar's test | — | Exact McNemar | — |
| Association of categoricals | Counts | χ² test of independence | Expected counts ≥5 | Fisher/Monte Carlo exact | Cramér's V |
| Correlation | Continuous | Pearson | Linearity, bivariate normal for inference | Spearman / Kendall | r with CI |
| Rates / counts | Counts with exposure | Poisson regression; rate ratio test | Equidispersion | Negative binomial; quasi-Poisson | Rate ratio + CI |
| Time to event | Survival | Log-rank test; Cox model | Proportional hazards | RMST difference; Wilcoxon (Breslow) | Hazard ratio, RMST diff |
| Clustered / repeated measures | Any | Mixed-effects models; GEE; cluster-robust SEs | Correct cluster structure | Cluster bootstrap | Model coefficients |
| Distribution comparison | Continuous | — | — | Kolmogorov–Smirnov; Anderson–Darling | KS D |
| Equivalence / non-inferiority | Any | TOST | Pre-specified margin | — | CI vs margin |
| Ratio metrics (revenue/user, CTR) | Ratio | Delta method | Large samples | Bootstrap at randomisation unit | Relative lift + CI |

## 2. Assumption checks
- Independence: the most violated assumption — repeated customers, patients within hospitals, transactions within accounts → cluster-robust methods.
- Normality: Q-Q plots of residuals; formal tests (Shapiro) are over-sensitive with large n — rely on CLT and plots.
- Equal variances: default to Welch.
- Heavy tails / skewed revenue: trimmed means, log-transform (changes estimand), bootstrap, or CUPED-style variance reduction for experiments.

## 3. Power & sample size
Inputs: α, power (1−β, default 0.8), baseline rate/variance, **minimum detectable effect (MDE)**, allocation ratio,
intra-cluster correlation (design effect = 1 + (m−1)·ICC for cluster randomisation).
Approximation for two proportions per group: n ≈ (z₁₋α/₂ + z₁₋β)² · [p₁(1−p₁)+p₂(1−p₂)] / (p₁−p₂)².
Report the MDE achievable with available sample if n is fixed. Underpowered studies → "absence of evidence ≠ evidence of absence".

## 4. Multiple testing
- Family-wise error (few confirmatory tests, high stakes): Bonferroni, Holm.
- False discovery rate (many exploratory tests, e.g., many segments/features): Benjamini–Hochberg.
- Pre-register primary hypothesis and metric; label all others exploratory.
- Sequential monitoring of A/B tests (peeking) inflates false positives → use group-sequential designs (alpha spending) or always-valid inference.

## 5. Practical vs statistical significance
With large n (BFSI transactions, retail baskets), tiny effects become "significant". Compare CI to the
pre-declared practically meaningful effect. Translate effects into business units (₹, readmissions avoided, units sold).

## 6. Alternatives
- **Bootstrap:** CIs for medians, ratios, complex metrics; resample the independent unit (cluster bootstrap).
- **Permutation tests:** exact under exchangeability; good for small/odd distributions.
- **Bayesian:** posterior of effect, probability of exceeding a business threshold; useful for decision-making, small samples with priors, and continuous monitoring; state priors explicitly.

## 7. A/B test & experiment design checklist
Randomisation unit (user, account, store, region — must match interference structure) · analysis unit = randomisation unit (or cluster-robust) ·
primary metric + guardrail metrics · MDE & power · duration ≥ full business cycle (weekly seasonality) · sample-ratio-mismatch check ·
pre-period balance check · novelty effects · spillovers/interference (store-level for retail, network effects) · CUPED/covariate adjustment ·
stopping rule · ethical/regulatory approvals (IRB/ethics committee for healthcare; fair-treatment obligations for BFSI).

## 8. Reporting template
> **Estimand:** … **Design:** … **Test/estimator:** … **Assumptions & checks:** … **Estimate:** effect = X (95% CI [a, b]) ·
> **p-value:** … · **Practical significance:** compare to threshold … · **Multiple-testing adjustment:** … ·
> **Limitations:** … · **What this does NOT show:** (e.g., causality, generalisation to other regions).
