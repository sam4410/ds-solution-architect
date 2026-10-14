# Routing Matrix: which specialists to invoke

Framing (`ds-problem-framing`) and data assessment (`ds-data-assessment`) **always** run (except in Quick
triage, where data assessment is abbreviated). Route the rest by lens. A mixed request is split into
analyses A1, A2, … and each is routed separately.

| Lens / question type | model-selection | experiment-design | validation-leakage | statistical-inference | evaluation-deployment |
|---|---|---|---|---|---|
| Exploratory / descriptive / segmentation | Light (clustering/EDA methods only) | Skip | Light (stability of segments) | If hypotheses will be tested | Light (actionability metrics; no serving unless segments are operationalised) |
| Predictive (classification, regression, forecasting, ranking, anomaly, NLP, CV, survival) | **Full** | **Full** | **Full** | Only for model comparison tests | **Full** |
| Inferential (population differences, relationships) | Skip (unless adjustment models are needed) | Skip | Skip (or light: assumptions about independence) | **Full** | Light (reporting, no deployment) |
| Causal / intervention / "impact of X" | Only for uplift or HTE targeting | Experiment design is inside statistical-inference | Light (pre-period and holdout design) | **Full** (causal designs) | Light (decision rule, post-launch evaluation) |
| Prescriptive / optimisation | Predictive inputs: Full | Full | Full | If action effects are needed: Full | Full + decision simulation |
| Insufficient info / ambiguous target | Skip | Skip | Skip | Skip | Skip, produce **Quick triage** |

## Depth modes
| Mode | When | Sections |
|---|---|---|
| Quick triage | Thin information, ambiguous target, or the user asks for a quick view | 1, 2, 3, 4, 5 (short), 18, 19 (discovery phase only) |
| Standard (default) | Normal brief with an identifiable decision and target | All applicable sections with concise tables |
| Full blueprint | User asks for "detailed", "full" or "comprehensive", or high-stakes regulated work | All applicable sections with expanded experiment cards, full leakage audit and detailed roadmap |

## Industry detection
- Healthcare: patients, hospital, clinical, EHR, claims (payer), readmission, diagnosis, pharma, ICD, LOS.
- BFSI: loan, credit, default, card, fraud, bank, NBFC, insurance, premium, claims (insurer), AML, collections, KYC.
- Retail: SKU, store, POS, basket, promotion, inventory, e-commerce, footfall, assortment, markdown.
Load the matching `domain-*.md` file. If several match (e.g., health insurance claims), load both.
