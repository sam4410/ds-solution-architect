# Domain Pack — BFSI (Banking, Financial Services, Insurance)

> Regulatory notes are orientation, not legal advice. Always confirm current regulations and the
> client's model risk policy with their compliance/risk teams.

## 1. Common use cases → formulation
| Use case | Lens | Formulation | Key pitfalls |
|---|---|---|---|
| Application scorecard / PD | Predictive | Binary classification (e.g., 90+ DPD within 12 months) → calibrated PD; often logistic + WoE for explainability, GBM as challenger | Reject inference (no outcomes for declined), vintage maturity, policy changes, explainability requirements |
| Behavioural scoring / early warning | Predictive | Classification / survival on monthly snapshots | Snapshot leakage, collections actions as leakage |
| LGD / EAD | Predictive | Regression (bounded, bimodal LGD → beta/two-stage/fractional models) | Workout period censoring, recoveries timing |
| IFRS 9 / ECL inputs | Predictive | Lifetime PD term structures, macro scenario conditioning | Macro forecasts, staging rules |
| Card/transaction fraud | Predictive / anomaly | Real-time classification; anomaly detection for new patterns | Extreme imbalance, chargeback label delay (weeks–months), adversarial drift, latency |
| AML / transaction monitoring | Anomaly + classification | Alert prioritisation, network analytics | Labels = SAR filings (biased), regulator expectations on explainability |
| Customer churn / attrition | Predictive (+ causal for retention offers) | Classification or survival; uplift for targeting | Defining churn for non-contractual products (dormancy), closures already initiated |
| Cross-sell / next best offer | Predictive / prescriptive | Propensity models, recommendation, uplift | Suitability rules; consent for marketing |
| Collections prioritisation | Prescriptive | Propensity-to-pay + uplift of contact strategy | Fair-practice codes on collections |
| Insurance claims fraud | Predictive / anomaly | Classification with investigator capacity | Investigated-only labels |
| Insurance pricing / underwriting | Predictive | GLMs (Poisson frequency × Gamma severity / Tweedie), GBM challengers | Rating-factor regulation, fairness, rate filing |
| Claims reserving / lapse | Predictive | Chain-ladder variants, survival/lapse models | Development-pattern changes |
| Cash / ATM / branch demand forecasting | Predictive | Forecasting | Salary days, festivals, month-end |
| Policy/product impact (limit increase, rate change) | Causal | Champion–challenger tests, RDD on score cutoffs, DiD | Selection by policy rules |
| Comparing approval rates across groups | Inferential | Proportion tests, regression with controls | Disparate impact; confounding by legitimate credit factors |

## 2. Typical data sources
Internal: core banking (accounts, balances, transactions), loan origination system (applications incl. declines),
loan management/collections, cards authorisation & clearing, CRM, digital channel clickstream, KYC, complaints,
policy admin & claims (insurance), GL/finance. External: credit bureau (CIBIL, Experian, Equifax, CRIF High Mark in India),
account aggregator data (consented, India), GST/ITR data (consented, SME lending), macroeconomic series (RBI, MOSPI, rates, inflation),
alternative data (only with consent and fairness review), sanctions/PEP lists.

## 3. Data & leakage traps specific to BFSI
- **Reject inference / selective labels:** performance is only observed for approved applicants.
- **Vintage maturity:** recent cohorts have not completed the outcome window — exclude or use survival.
- **Collections/recovery actions, write-off flags, restructuring flags** recorded after the prediction point.
- **Bureau pulls refreshed later** (use archived bureau snapshot at application date).
- **Policy cut-offs** create discontinuities and feedback loops.
- **Chargeback/fraud labels** arrive with long delay — evaluate only on matured windows.
- **Proxy discrimination:** pincode, language, device type can proxy protected attributes.

## 4. Metrics conventions
Gini/AUC, KS, PSI and CSI (stability), calibration by score band (Hosmer–Lemeshow / binomial tests per grade),
bad rate by decile, approval rate vs bad rate trade-off (strategy curves), expected loss (PD × LGD × EAD),
fraud: detection rate at fixed alert volume, value-detection rate (₹ saved), false positive ratio, latency;
insurance: Gini/lift on loss cost, loss ratio; fairness: adverse impact ratio, approval/bad-rate parity checks.

## 5. Regulatory & governance checklist (confirm applicability)
- **India:** RBI directions on model risk/credit risk management and IT governance; RBI's framework on responsible & ethical AI in the financial sector (FREE-AI, 2025) — verify current status; RBI digital lending guidelines; fair practices code; DPDP Act 2023 and Rules; Account Aggregator consent framework; IRDAI guidelines (insurance); SEBI (capital markets).
- **US:** SR 11-7 model risk management (validation, documentation, effective challenge); ECOA/Regulation B adverse action reason requirements; FCRA; fair lending (disparate impact); state insurance rating rules.
- **EU/UK:** EU AI Act (creditworthiness assessment and life/health insurance pricing listed as high-risk); GDPR (automated decision-making); EBA guidelines on loan origination; PRA SS1/23 model risk management (UK).
- **Global:** Basel IRB requirements for PD/LGD/EAD; IFRS 9; PCI DSS for card data.
- Expect: independent model validation, model documentation pack, champion–challenger governance, explainability (reason codes), monotonic constraints where business-intuitive, periodic monitoring with PSI thresholds.

## 6. Questions to ask the client
1. Exact bad/churn/fraud definition, observation & performance windows, exclusions.
2. Are declined applications and their bureau data available (reject inference)?
3. Regulatory explainability requirement — is a GBM acceptable, or must the champion be a scorecard?
4. Decision capacity (investigator alerts/day, call-centre capacity) and cost of FP/FN in ₹.
5. Policy changes in the history (cut-offs, products, COVID moratorium) that break comparability.
6. Model risk management process and validation team expectations.
