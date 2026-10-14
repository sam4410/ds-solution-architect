# Solution Plan Template

Write the plan in Markdown following this skeleton, then convert to Word with
`scripts/md_to_docx.py`. Rules for the Markdown so it converts cleanly:
- Start with a YAML-like metadata block exactly as shown (between `---` lines).
- Use `#` for the document title only once; `##` for numbered sections; `###` / `####` for subsections.
- Use pipe tables (header row + separator row). Keep cells short; no line breaks inside cells.
- Use `- ` bullets and `1. ` numbered lists. `**bold**`, `*italic*`, `` `code` `` are supported.
- Use blockquotes starting with `> **Assumption:**`, `> **Risk:**`, `> **Open question:**`, `> **Note:**` for callouts.
- **Omit sections that do not apply** and state why in one line under "Scope of this plan" (e.g., "No causal question was raised; §14 omitted"). Never pad.
- Never state numeric results, baselines or performance targets as facts unless provided by the client — write them as targets to be agreed or as `[TBD with client]`.
- Tag every data source and key statement: **[Confirmed]**, **[Assumed]**, **[To investigate]**.

---

```
---
title: <Use-case name> — Data Science Solution Plan
client: <Client name or "Client">
industry: <Healthcare | BFSI | Retail | Other>
prepared_by: <Name / team>
date: <YYYY-MM-DD>
version: 0.1 (draft)
depth: <Quick triage | Standard | Full blueprint>
classification: Confidential
---

# <Use-case name> — Data Science Solution Plan

## 1. Executive Summary
- The decision this work supports (one sentence).
- Problem in plain language and the analytical lens(es): Exploratory / Predictive / Inferential / Causal.
- Recommended approach (3–5 bullets).
- What must be true for this to work (top assumptions/dependencies).
- Top risks and first next steps.

### Scope of this plan
Sections included/omitted and why.

## 2. Business Problem & Decision Framing
Framing table: decision, owner, timing (prediction point), action space, capacity, unit of analysis,
population, outcome, horizon, observation window, cost of errors, success criteria, constraints.

## 3. Analytical Problem Classification
- Lens(es) and ML formulation with rationale.
- Alternative formulations considered and when they would be better.
- Separate analyses (if the question is mixed) with their own estimand.

## 4. Assumptions, Unknowns & Client Clarification Questions
Table: ID · Statement · Type (Fact/Assumption/Open question) · Impact if wrong · Owner · Needed by.

## 5. Data Inventory & Feasibility Assessment
Table: Source · Business meaning · Owner · Grain/keys · Coverage & refresh · Point-in-time available? · Quality risks · Privacy/licensing · Status [Confirmed/Assumed/To investigate].
Feasibility verdict and blocking dependencies.

## 6. Data Quality & Preprocessing Plan
Table: Step · Rationale · Method · Risks (leakage/bias/signal loss) · Validation check.

## 7. Feature & Target Design
- Target definition (exact), maturity/label delay, censoring, exclusions.
- Feature groups with availability timestamp relative to prediction point.

## 8. Baseline Model Specification
Baseline(s), inputs, evaluation protocol, and the bar candidates must beat (margin agreed with client).

## 9. Candidate Algorithms & Prioritisation
Table: Priority · Algorithm · Why plausible · Assumptions/needs · Strengths · Weaknesses · Interpretability · Key hyperparameters · Reject if.

## 10. Metrics & Decision Criteria
Table: Tier (Primary/Secondary/Diagnostic/Business) · Metric · Definition · Why · Caveat.
Threshold/decision rule and how it is chosen.

## 11. Experiment Matrix & Tuning Strategy
Staged plan E0–E8; experiment cards table: ID · Hypothesis · Change · Fixed conditions · Split · Metrics · Stopping rule.
Tuning strategy, budget, hyperparameter priorities, reproducibility & tracking.

## 12. Train / Validation / Test Design
Split strategy and why it mirrors deployment; diagram/description of windows; walk-forward specifics
(origin, horizon, window, retrain cadence, gap/embargo) where temporal.

## 13. Leakage Audit Checklist
Table: Risk · Applies? · Evidence/where it could occur · Mitigation · Owner.

## 14. Statistical Inference & Causal Analysis Plan
Estimand, hypotheses, design/test, assumptions & checks, power/MDE, multiple testing, effect sizes & CIs,
what the design can and cannot identify.

## 15. Robustness & Sensitivity Tests
Subgroups, time slices, stress scenarios, sensitivity to assumptions.

## 16. Interpretability & Uncertainty
Global/local explanation approach (labelled as association), prediction intervals / calibration, communication to users.

## 17. Deployment & Monitoring Strategy
Serving pattern, integration, human-in-the-loop, monitoring metrics & thresholds, retraining triggers, rollback,
post-deployment evaluation, governance & regulatory controls.

## 18. Risks, Mitigations, Dependencies & Open Decisions
Table: Risk · Likelihood · Impact · Mitigation · Owner.

## 19. Phased Implementation Roadmap
Table: Phase · Work package · Dependencies · Deliverables · Acceptance criteria · Indicative effort (provisional) .
Phases: Discovery → Data engineering → Analysis/EDA → Modelling → Validation → Deployment → Monitoring.

## 20. Decision Log
Table: # · Decision/Recommendation · Rationale · Alternatives considered · Key assumptions · Risk · Validation method.

## 21. References
Authoritative sources supporting non-obvious technical claims (only real, verifiable references; none if none were consulted).
```
