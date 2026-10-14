---
name: ds-data-assessment
description: Assesses data sourcing, feasibility and preparation for a data science use case. Identifies candidate internal and external data sources (tagged Confirmed / Assumed / To investigate), grain and keys, point-in-time availability, label quality and delay, joins, missingness, bias, privacy and licensing; then produces a preprocessing and feature-engineering plan (missing values, outliers, encoding, scaling, imbalance, text/image/time-series prep, target construction) with rationale, risks and validation checks. Use when asked "what data do we need", "what preprocessing should we do", "is this feasible with our data", or when ds-solution-plan calls for data assessment.
---

# DS Data Assessment & Preprocessing

Decide what data the solution needs, whether it plausibly exists and can be used at the prediction point,
and how to prepare it without introducing leakage or bias.

## Load as needed
- `references/preprocessing-playbook.md`: methods, risks and checks for each preprocessing step. **Always read.**
- `references/leakage-checklist.md`: sections A, C, D and F apply directly to data preparation.
- `references/domain-healthcare.md` / `domain-bfsi.md` / `domain-retail.md`: typical internal and external sources, standards and traps for the client's industry.

## Workflow

1. **Start from the framing**: unit of analysis, prediction point, target, horizon. If these are missing, state the assumptions you are using.
2. **Build the data inventory.** For each candidate source record: business meaning, likely owner/system, grain
   and primary keys, history and refresh frequency, join strategy and duplicate risk, **availability at the
   prediction point (with latency)**, quality concerns, label quality/delay, privacy/consent/licensing, and a
   **status tag**:
   - **[Confirmed]**: the client said it exists, or it has been seen in the data
   - **[Assumed]**: likely to exist given the industry, but unverified
   - **[To investigate]**: desirable, existence or usability unknown
   Separate "must-have" from "nice-to-have" sources. Include external sources only when they plausibly add signal.
3. **Give a feasibility verdict**: Feasible / Feasible with conditions / Not yet feasible, listing the blocking dependencies.
4. **Target construction**: exact definition, maturity window, censoring, exclusions, label-definition stability, and
   selective labels (e.g., outcomes observed only for approved loans or investigated claims).
5. **Preprocessing plan**: one table row per applicable step (Step | Rationale | Method | Risks | Validation check).
   Only include steps relevant to this data. Mark every learned transform as "fit on training folds only".
6. **Feature design**: feature groups, each with its source, availability timestamp relative to the prediction point, and hypothesis for why it carries signal.
7. **Flag estimand distortion**: note where preprocessing changes the population or the estimand (playbook §11).
8. **Data quality checks to run first** (an EDA plan): row counts by period, target prevalence by period, missingness by feature, period and subgroup, duplicate rate, entity overlap, and distribution shifts.

## Output contract
```
### Data inventory            (pipe table incl. Status column)
### Feasibility verdict & blocking dependencies
### Target construction
### Preprocessing plan        (pipe table)
### Feature groups & availability
### Initial EDA / data-quality checks
### Facts / Assumptions / Open questions
### Decision rows             (pipe table: Decision | Rationale | Alternatives | Assumptions | Risk | Validation method)
```

## Guardrails
- Never claim that a table, column or system exists unless the user said so. Use the status tags.
- Never propose features that would not be available at the prediction point.
- Flag PHI/PII and say where processing must happen (client environment, de-identified extracts). Do not suggest sending client data to external services.
- If the user supplies actual data files, profile them. Report observed facts (rows, nulls, ranges) separately from interpretation.
