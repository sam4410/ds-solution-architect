# Quality Gates & Scoring Rubric

Score each gate 1–5. A plan is client-ready only if **every gate ≥ 4** and there are **zero
fabrication findings**.

| # | Gate | 5 = Excellent | 3 = Partial | 1 = Fail |
|---|---|---|---|---|
| G1 | **Problem fit** | Lens(es) explicit; prediction vs inference vs causal separated; decision, prediction point, unit, horizon, estimand defined | Lens stated but decision/prediction point vague | Treats everything as model-building; causal question answered with a predictive model |
| G2 | **Data feasibility** | Every source tagged Confirmed/Assumed/To investigate; grain, point-in-time availability, label delay, privacy addressed | Sources listed without status or timing | Assumes data exists; invents tables/columns |
| G3 | **Baseline discipline** | Meaningful baseline(s) incl. current business rule; bar to beat defined | Baseline mentioned generically | No baseline / jumps to complex models |
| G4 | **Validation integrity** | Split mirrors deployment (temporal/grouped/site); walk-forward fully specified where temporal; locked test | Right family but under-specified | Random split for temporal/grouped data without justification |
| G5 | **Leakage awareness** | Target timing, feature availability, entity overlap, preprocessing-in-fold, label maturity, selective labels each assessed for this case | Generic checklist pasted | Not addressed |
| G6 | **Statistical rigour** | Uncertainty, assumptions, effect sizes + CIs, power/MDE, multiple testing, practical significance (where relevant) | Some elements | p-values only, or claims without uncertainty |
| G7 | **Reproducibility** | Experiment cards with hypotheses, fixed conditions, stopping rules; tracking & versioning; acceptance criteria | Staged plan without criteria | No experiment plan |
| G8 | **Client communication** | Plain-language summary; trade-offs, alternatives, limitations, dependencies; business rationale; domain/regulatory controls | Technical but understandable | Jargon dump or generic |

## Fabrication checks (any hit = must fix)
- [ ] Numeric performance/baseline values stated without client data.
- [ ] Worked numeric examples built on invented inputs (σ, ICC, base rates), even when labelled "illustrative" or "placeholder".
- [ ] Arithmetic that does not match its own stated formula or the brief's figures (recompute it).
- [ ] Data sources, tables or columns asserted as existing without client confirmation.
- [ ] Citations/regulations that cannot be verified or are misattributed.
- [ ] Causal language for associational evidence ("drives", "causes", "impact of" from observational/predictive results).
- [ ] Irrelevant sections included mechanically (e.g., hyperparameter tuning for a pure inferential question).

## Additional checks for Healthcare / BFSI
- [ ] PHI/PII handling, consent, data residency stated.
- [ ] Explainability and human oversight requirements addressed.
- [ ] Subgroup/fairness evaluation planned.
- [ ] Relevant regulatory frameworks named with "confirm with compliance".
