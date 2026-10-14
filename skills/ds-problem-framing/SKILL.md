---
name: ds-problem-framing
description: Frames a client business problem as a precise data science problem. Classifies it with the simple lens (Exploratory / Predictive / Inferential / Causal), maps it to an ML domain (forecasting, regression, classification, NLP, computer vision, survival, recommendation, anomaly detection, clustering, causal, optimisation), and defines the decision, prediction point, unit of analysis, target, horizon, estimand, cost of errors and success criteria. Use when the user shares a client use case, brief or RFP and asks "how should we think about this problem", "what type of ML problem is this", "is this predictive or causal", or when the ds-solution-plan skill calls for framing.
---

# DS Problem Framing

Turn a loosely worded client request into an unambiguous analytical problem statement. Framing errors
propagate into every later decision, so be precise and explicit about what is known vs assumed.

## Load as needed
- `references/problem-taxonomy.md`: lens definitions, the framing checklist, ML-domain mapping, red flags. **Always read.**
- `references/intake-questionnaire.md`: which questions are essential to ask.
- `references/domain-healthcare.md`, `references/domain-bfsi.md`, `references/domain-retail.md`: read the one that matches the client's industry, for typical use cases, pitfalls and client questions.

## Workflow

1. **Restate the problem in plain language** (2–3 sentences a non-technical executive would agree with).
2. **Identify the decision**: who acts, what action, when (this is the prediction point), and the capacity to act.
   If no decision can be named, say so and flag it as the top open question.
3. **Apply the simple lens.** Classify each part of the request as Exploratory, Predictive, Inferential or
   Causal/Prescriptive. If the request mixes lenses, **split it into separate analyses** (A1, A2, …) and give
   each its own target/estimand. Explicitly flag any causal question that the client expects a predictive model to answer.
4. **Fill the framing checklist** (taxonomy §3) for each analysis: unit of analysis, population, outcome/target
   (exact definition), horizon, observation window, estimand (for inferential/causal), cost of errors, success
   criteria, constraints. Write `[TBD with client]` rather than inventing values.
5. **Map to ML formulation(s)** using taxonomy §4. Give the chosen formulation, the rationale, and 1–2
   alternative formulations with the conditions under which they would be better (e.g., survival instead of
   binary classification when follow-up varies).
6. **Check red flags** (taxonomy §5) and list any that apply.
7. **Separate knowledge states**: Confirmed facts / Working assumptions (each with impact if wrong) / Open questions
   (prioritised; mark the ≤5 that would materially change the plan).

## Output contract
Return Markdown with these headings so the orchestrator can merge them:

```
### Problem statement (plain language)
### Analytical lens & separate analyses
### Framing table            (pipe table: Element | Definition for this case | Status)
### ML formulation & alternatives
### Red flags
### Facts / Assumptions / Open questions
### Decision rows            (pipe table: Decision | Rationale | Alternatives | Assumptions | Risk | Validation method)
```

## Guardrails
- Do not choose algorithms here; that is ds-model-selection's job.
- Never assume a target definition, horizon or success threshold is known unless the client stated it.
- Never let a predictive formulation answer a causal question. Route causal questions to ds-statistical-inference.
- Adapt depth: one framing table per separate analysis, with no padding.
