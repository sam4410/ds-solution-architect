# Client Intake Questionnaire

Extract answers from whatever the user provided (brief, email, RFP, notes). Ask the user only the
**essential** questions whose answers would change the plan materially (max 5, prioritised). For everything
else, proceed with labelled assumptions.

## A. Essential (ask if missing and not inferable)
1. **Decision:** What decision or action will the output change, and who takes it?
2. **Target/outcome:** What exactly is the outcome (definition, window)?
3. **Timing:** When is the output needed relative to the event (prediction point / horizon)?
4. **Data:** What data exists today (systems, history length, grain)? Are labels recorded?
5. **Constraints:** Regulatory/explainability/latency/data-residency constraints?

## B. Important (assume and label if missing)
6. Industry and sub-domain; geography (drives regulation).
7. Scale: number of entities/series, rows per period.
8. Current approach/benchmark (rule, planner forecast, vendor model) and its performance if known.
9. Capacity to act (calls/day, investigations/day, budget).
10. Cost of errors (FP vs FN), in money or harm.
11. Can we run experiments / randomise?
12. Deployment target (batch report, API, embedded tool) and users.
13. Timeline and team (for roadmap effort ranges).

## C. Depth mode
- **Quick triage** (1–3 pages): lens, formulation, data needs, top risks, clarifying questions, next step.
  Use when information is thin or the user asks for a quick view.
- **Standard** (default): all applicable sections, concise tables.
- **Full blueprint**: all applicable sections expanded with experiment cards, full leakage audit, detailed roadmap.

## D. Insufficient-information rule
If the target is ambiguous, the decision is unknown, or no data source is identifiable, **do not produce a full
plan**. Produce a Quick triage with: candidate framings (2–3), what each would need, the questions that decide
between them, and a discovery-phase plan.
