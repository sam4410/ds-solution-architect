---
name: ds-experiment-design
description: Designs the model-development experiment plan for a data science project. Covers staged experiments (sanity checks, baselines, simple and advanced candidates, feature ablations, hyperparameter optimisation, robustness, calibration, locked-test evaluation), experiment cards with hypotheses, fixed conditions and stopping rules, hyperparameter priorities and search strategy (grid, random, Bayesian, Hyperband), reproducibility and experiment tracking. Use when asked "how do we set up experiments", "which hyperparameters matter", "tuning strategy", "experiment matrix", or when ds-solution-plan calls for experiment design.
---

# DS Experiment Design (Model Development)

Turn the model shortlist into a disciplined, reproducible sequence of experiments, where each one answers a
stated question and has a pre-declared stopping rule.

## Load as needed
- `references/experiment-design-playbook.md`: stages E0–E8, the experiment card, search strategies, hyperparameter priorities and tracking. **Always read.**
- `references/algorithm-selection-matrix.md`: hyperparameters per algorithm.
- `references/evaluation-metrics-catalog.md`: metric choice and comparison rules.

## Workflow

1. **Take as inputs** the baselines, candidates, metrics and split design. If any are missing, state the assumptions you are using.
2. **Lay out stages E0–E8**, adapted to the case. Drop stages that do not apply and say why (e.g., no calibration stage for pure forecasting point estimates).
3. **Write experiment cards** for the key experiments (5–12 for Standard depth, more for Full): ID, hypothesis,
   change tested, fixed conditions, dataset/split version, metrics, expected interpretation, stopping/acceptance rule.
   Include **feature-group ablations** that tell the client which data sources are worth acquiring.
4. **Tuning strategy**: choose grid, random or Bayesian (with pruning) by search-space size and compute budget;
   set the budget (trials or hours); list the top hyperparameters per shortlisted model in priority order; and say
   where tuning happens (validation folds or inner CV, **never the test set**).
5. **Reproducibility**: seeds, environment lockfile, data snapshot and hash, split-definition version, config files,
   code commit, an experiment tracker (MLflow or equivalent, or a versioned log if the client has none), and a model card.
6. **Model comparison protocol**: identical folds, paired comparison tests, a pre-declared minimum meaningful improvement, and a log of test-set access.

## Output contract
```
### Experiment stages          (pipe table: Stage | Purpose | Exit criterion)
### Experiment cards           (pipe table: ID | Hypothesis | Change | Fixed conditions | Split | Metrics | Stopping rule)
### Hyperparameter strategy    (search method, budget, priorities per model)
### Reproducibility & tracking
### Model comparison protocol
### Facts / Assumptions / Open questions
### Decision rows              (pipe table: Decision | Rationale | Alternatives | Assumptions | Risk | Validation method)
```

## Guardrails
- Never fabricate experiment results. Cards describe planned work only.
- Do not plan tuning for models that have not yet beaten the baseline.
- For pure inferential or causal analyses, skip this skill and use ds-statistical-inference instead.
