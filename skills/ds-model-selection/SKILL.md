---
name: ds-model-selection
description: Selects and prioritises modelling approaches for a framed data science problem. Defines meaningful baselines first, then a ranked sequence of candidate algorithms (simple to complex) for tabular regression and classification, time-series forecasting, survival, anomaly and fraud detection, clustering, recommendation, NLP and computer vision, with assumptions, strengths, weaknesses, interpretability, data and compute needs, key hyperparameters and explicit rejection criteria. Use when asked "which algorithm should we start with", "baseline model", "trade-offs between models", or when ds-solution-plan calls for model selection.
---

# DS Model Selection & Baselines

Recommend a defensible, prioritised modelling path. Complexity has to earn its place by beating simpler
options on proper out-of-sample validation.

## Load as needed
- `references/algorithm-selection-matrix.md`: baselines and per-algorithm trade-offs. **Always read.**
- `references/problem-taxonomy.md` §4: formulation alternatives.

## Workflow

1. **Confirm the formulation** (from framing): target type, data structure (i.i.d., grouped, temporal, spatial),
   scale (rows, entities, series), feature types, interpretability and latency constraints, and the regulatory context.
2. **Specify baseline(s)**, at least one and ideally including the client's *current* rule or process. For each,
   give inputs, assumptions, evaluation protocol and limitations, and define **the bar candidates must beat**
   (e.g., "beat seasonal-naive WAPE by an agreed margin on all walk-forward windows"). Do **not** invent baseline scores.
3. **Shortlist 2–4 candidates** in priority order (simple → complex). For each give: why it is plausible here,
   assumptions and data needs, strengths, weaknesses and failure modes on *this* data, interpretability,
   compute, sensitivity to noise, imbalance and drift, key hyperparameters, and **reject-if** criteria.
4. **Justify any complex model** (deep learning, large ensembles, LLMs) with a concrete reason such as data scale,
   modality or a demonstrated gap. Otherwise defer it to a "consider later" note.
5. **Note regulatory and explainability fit** (e.g., scorecard or monotonic GBM for credit; clinician-facing explanations).
6. **Say how the final model will be chosen**: the decision rule that combines primary metric, stability, calibration, interpretability, cost and latency.

## Output contract
```
### Baseline specification     (pipe table: Baseline | Inputs | Protocol | Limitation | Role)
### Candidate algorithms       (pipe table: Priority | Algorithm | Why plausible | Needs | Strengths | Weaknesses | Interpretability | Key hyperparameters | Reject if)
### Trade-off narrative
### Model selection decision rule
### Facts / Assumptions / Open questions
### Decision rows             (pipe table: Decision | Rationale | Alternatives | Assumptions | Risk | Validation method)
```

## Guardrails
- Never state expected accuracy or scores.
- Prefer the simpler model when its performance is within the cross-fold noise band.
- For causal questions, do not propose predictive models as the answer. Point to ds-statistical-inference.
- Keep algorithm lists short and specific to the case rather than encyclopaedic.
