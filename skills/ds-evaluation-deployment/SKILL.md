---
name: ds-evaluation-deployment
description: Selects business-aligned evaluation metrics and plans robustness, deployment and monitoring for data science solutions. Defines primary, secondary, diagnostic and business metrics with formulas and caveats (regression, classification, imbalanced data, forecasting, ranking, survival, clustering, NLP/CV, causal, fairness), decision thresholds from cost and capacity, calibration, uncertainty, explainability, serving patterns, human-in-the-loop, drift and performance monitoring, retraining triggers, rollback and governance controls for healthcare, BFSI and retail. Use when asked "which metrics should we use", "how to choose a threshold", "how to deploy and monitor the model", "model monitoring", or when ds-solution-plan calls for evaluation and deployment.
---

# DS Evaluation, Robustness & Deployment

Make sure the model is judged by what matters to the business and that it stays trustworthy once in production.

## Load as needed
- `references/evaluation-metrics-catalog.md`: metrics by task, threshold selection, fairness and comparison rules. **Always read.**
- `references/deployment-monitoring-playbook.md`: robustness checks, serving patterns, monitoring and governance. **Always read.**
- `references/domain-healthcare.md` / `domain-bfsi.md` / `domain-retail.md`: industry metric conventions and regulatory controls.

## Workflow

1. **Metric tiers**: one **primary** metric (drives selection), secondary metrics (guard against gaming the
   primary), diagnostic metrics (explain behaviour) and **business** metrics (value). For each give the definition or formula, why it fits this case, and when it would mislead.
   Explicitly reject unsuitable metrics (e.g., accuracy for 2% prevalence; MAPE for intermittent demand).
2. **Decision threshold or rule**: derive it from the cost matrix and action capacity (top-k), choose it on validation data, and freeze it before the test.
3. **Calibration and uncertainty**: say whether probabilities are used directly (if so, plan calibration), and give the prediction-interval approach (quantile or conformal).
4. **Robustness and fairness**: subgroups, time slices, stress scenarios, and fairness metrics (mandatory for healthcare and BFSI decisions about people).
5. **Interpretability**: the global and local explanation approach, labelled as model behaviour rather than causation. Add regulatory reason codes where needed.
6. **Deployment**: serving pattern (batch, real-time or embedded), integration point, latency, training-serving parity, a fallback rule, human-in-the-loop, and rollout path (shadow → champion–challenger → full).
7. **Monitoring**: data-quality, drift, prediction, performance (allowing for label delay), business and fairness metrics, each with **thresholds and owners**.
8. **Lifecycle**: retraining cadence and triggers, re-validation and approval gate, rollback criteria, post-deployment impact evaluation (holdout or experiment), and feedback-loop risks.
9. **Governance**: privacy, security, auditability and model documentation, plus the regulatory frameworks to confirm with the client's compliance team.

## Output contract
```
### Metrics                      (pipe table: Tier | Metric | Definition | Why | Caveat)
### Decision threshold / rule
### Calibration & uncertainty
### Robustness, subgroup & fairness tests
### Interpretability plan
### Deployment design
### Monitoring plan              (pipe table: Layer | Metric | Threshold | Action | Owner)
### Retraining, rollback & post-deployment evaluation
### Governance & regulatory controls
### Facts / Assumptions / Open questions
### Decision rows                (pipe table: Decision | Rationale | Alternatives | Assumptions | Risk | Validation method)
```

## Guardrails
- Never compare metrics across different populations, windows or label definitions.
- Never state target metric values as achievable. Write them as acceptance criteria to be agreed.
- Regulatory items are orientation only and must be marked "confirm with client compliance".
