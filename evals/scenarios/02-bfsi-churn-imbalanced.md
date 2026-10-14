# Scenario 02 — BFSI customer churn with class imbalance

## Prompt
Client: a private-sector bank's credit-card business (~2.4M active cards). Monthly voluntary attrition is roughly 1.5%.
The retention team can call about 20,000 customers per month and can offer fee waivers or reward points.
They want a model to identify which customers will close their card in the next 3 months, and also want to know
"what drives churn" and "whether the retention offers actually work". Data: card transactions, statements,
customer demographics, complaints and call-centre logs, bureau score at onboarding. Prepare the solution plan.

## Expected behaviours (must)
- Splits into predictive (attrition risk), exploratory/associational drivers, and causal (offer effectiveness) analyses.
- Imbalance handled via metrics (PR-AUC, precision/recall@k with k≈capacity), class weights; no accuracy as primary; calibration after reweighting.
- Out-of-time validation with customers grouped; snapshot design; label window maturity.
- Leakage: closure requests, retention-team contact flags, post-snapshot complaint resolutions.
- Drivers framed as associations (SHAP ≠ causation).
- Offer effectiveness via randomised holdout / champion–challenger; uplift only after randomised data.
- BFSI governance: model risk management, explainability, fairness, DPDP; "confirm with compliance".
- No fabricated performance numbers.
