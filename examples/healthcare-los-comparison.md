---
title: Knee-Replacement Length of Stay, Hospital A vs Hospital B — Analysis Plan
client: Hospital group (Hospital A, Pune; Hospital B, Nagpur)
industry: Healthcare
prepared_by: Data Science Solution Architect toolkit
date: 2026-10-14
version: 0.1 (draft)
depth: Standard
classification: Confidential
---

# Knee-Replacement Length of Stay, Hospital A vs Hospital B — Analysis Plan

## 1. Executive Summary
- **Decision supported:** whether to launch a process-improvement program at Hospital B for elective knee replacement, and how to size it.
- **Problem in plain language:** management believes patients stay longer at B. We need to establish whether the gap is real (not noise), how large it is once patient mix is accounted for, and how much of the variation sits at hospital, surgeon and patient level (as association, not cause).
- **Lens:** **Inferential** (a population difference between two sites). It is not a prediction problem, so no prediction model is built. The follow-up question "why is B longer / will the program work" is **causal** and is explicitly *out of scope*; this plan only prepares the ground for it.
- **Recommended approach:**
  1. Define LOS and the population precisely, then profile and clean the data (Discovery and EDA).
  2. Report the **raw difference** with a confidence interval, using a surgeon-clustered bootstrap.
  3. Fit the **primary analysis**: a case-mix-adjusted model of LOS (hospital effect, adjusted for age, sex, comorbidity, ASA grade, with surgeon as a random effect, standardised to a marginal effect), reporting the adjusted ratio of means or difference in means with a 95% CI.
  4. Run **sensitivity analyses** (alternative LOS definitions, outlier handling, surgeon-level view, time slices) and a **variance decomposition** (how much of the gap sits between hospitals, between surgeons, and between patients).
  5. Report effect size in days and in bed-days per year associated with the gap, compared with a practically important threshold agreed with management.
- **What must be true:** LOS is defined the same way and recorded reliably at both sites; both hospitals perform comparable procedures (primary vs revision, unilateral vs bilateral); the recorded case-mix variables capture the main clinical drivers of stay.
- **Top risks:** unmeasured case-mix differences (home support, distance, rehabilitation protocol, payer/insurance type); different discharge conventions; surgeons working at only one site, so surgeon and hospital effects cannot be fully separated.
- **Honest limit:** this analysis can say whether B is *associated* with longer stay after adjustment, and by roughly how much. It cannot, on its own, say *why*, or that a program would shorten stay.

> **Needed from the client next** (blocking; answered by hospital data/IT teams and the clinical lead for orthopaedics)
> 1. Exact definition of admission and discharge timestamps at each site (date only or date-time; discharge order vs physical exit) and whether the definition is the same in A and B. Owner: HIS/IT leads at both sites.
> 2. Is the cohort limited to elective primary knee replacement? How are revisions, bilateral, and unicompartmental cases coded? Owner: orthopaedic lead.
> 3. Which surgeons operated at only one hospital and which at both? Owner: medical director's office.
> 4. Approval route for using patient-level data (ethics/IRB or institutional waiver, de-identification, data residency). Owner: compliance/ethics committee.
> 5. The smallest LOS difference that would justify a program (practical importance threshold) and the cost of a bed-day. Owner: hospital group management / finance.

### Scope of this plan
| Section | Included? | Reason |
|---|---|---|
| 2–3 Framing and classification | Yes | Core |
| 4 Assumptions and questions | Yes | Client unavailable; assumptions labelled |
| 5–6 Data and preprocessing | Yes | Needed for a valid comparison |
| 7 Outcome and covariate design | Yes | Outcome definition is central |
| 8–9 Baseline model, candidate algorithms | Omitted | No prediction task; the raw difference serves as the unadjusted comparator |
| 10 Metrics | Yes, as estimand and effect-size reporting | Inferential reporting |
| 11–12 Experiments, train/validation/test | Omitted | No model is being trained or tuned; no held-out test needed. Robustness is handled in §15 |
| 13 Leakage audit | Short form | Replaced by a bias and confounding audit |
| 14 Inference plan | Yes | Core |
| 15 Robustness | Yes | Core |
| 16 Interpretability and uncertainty | Merged into §14 | |
| 17 Deployment and monitoring | Omitted for a model; reporting handoff and optional post-program evaluation noted | |
| 18–20 Risks, roadmap, decisions | Yes | |
| 21 References | None consulted | |

Routing: framing, data assessment and statistical inference ran in full. Model selection, experiment design and validation design were skipped (inferential lens). Evaluation and deployment ran in light form only (reporting).

## 2. Business Problem & Decision Framing
| Element | Definition for this case | Status |
|---|---|---|
| Decision | Launch (or not) and size a process-improvement program at Hospital B | [Confirmed] from brief |
| Decision owner | Hospital group management | [Assumed] |
| Timing | Before program launch | [Confirmed] |
| Action space | Launch / defer / investigate further | [Assumed] |
| Unit of analysis | One elective knee-replacement admission (the encounter) | [Assumed] |
| Population | Adults with elective knee replacement admitted to A or B (the 2-financial-year period is [Confirmed] from the brief); exclusions (revisions, bilateral, emergency, trauma, deaths in hospital, transfers out) to be confirmed | Population [Assumed], period [Confirmed], exclusions [To investigate] |
| Outcome | Length of stay in days: discharge date minus admission date, with the definition to be confirmed (see §7) | [Assumed] |
| Estimand | Difference in mean LOS (B minus A) in comparable patients; also expressed as a ratio of means | [Assumed] |
| Practical importance threshold | [TBD with client] | Open |
| Cost of errors | Falsely concluding B is longer wastes program effort; missing a real gap leaves bed-days unused | [Assumed] |
| Constraints | Patient-level health data: consent, de-identification, data residency | [To investigate] |

## 3. Analytical Problem Classification
- **A1 (in scope): Inferential.** Is mean LOS for elective knee replacement different between B and A, after accounting for patient mix, and by how much?
- **A2 (out of scope, flagged): Causal.** "What would reduce LOS at B / what is the effect of the program?" A cross-hospital comparison cannot answer this. If management wants it, a separate design is needed (for example a before/after with a comparison site, or a staged roll-out across wards or surgeons). The toolkit's causal-design guidance would apply.
- **A3 (optional, exploratory): Diagnostic.** Where in the pathway does B's time go? This needs timestamps beyond admission and discharge (theatre date, mobilisation, discharge order) which are not in the stated data.
- **Alternatives considered:** a predictive LOS model would be appropriate for bed planning, but it does not answer "is B different". A risk-adjusted comparison via indirect standardisation (expected LOS from a pooled model, then observed/expected by site) is a presentation option for the same analysis.

## 4. Assumptions, Unknowns & Client Clarification Questions
| ID | Statement | Type | Impact if wrong | Owner | Needed by |
|---|---|---|---|---|---|
| Q1 | Admission and discharge definitions are identical at A and B | Open question | A definitional gap could create or hide the difference | HIS/IT leads | Discovery |
| Q2 | Cohort is elective primary knee replacement only | Open question | Mixing in revisions or bilaterals inflates LOS and may differ by site | Orthopaedic lead | Discovery |
| Q3 | Surgeon overlap between sites | Open question | If no surgeon works at both sites, hospital and surgeon effects cannot be separated | Medical director | Discovery |
| Q4 | Ethics/data-protection approval route | Open question | Blocks access to data | Compliance | Discovery |
| Q5 | Practical importance threshold and bed-day cost | Open question | Cannot judge significance in business terms | Management | Discovery |
| A1 | Data are complete for all consecutive eligible admissions (no selection into extract) | Assumption | Selection bias | Data team | Data profiling |
| A2 | The two financial years are the same at both sites, with no major policy change mid-period | Assumption | Time confounding | Client | Discovery |
| A3 | Comorbidities are available as a coded list or index (not free text) | Assumption | Weaker adjustment | Data team | Data profiling |
| A4 | In-hospital deaths and transfers out are rare enough to handle by exclusion with a sensitivity check | Assumption | Informative censoring of LOS | Data team | Data profiling |
| A5 | Payer or insurance type, discharge destination, and day-of-week are *not* in the stated data; we ask for them but proceed without if absent | Assumption | Residual confounding | Data team | Discovery |
| F1 | About 1,100 admissions at A, about 800 at B, last 2 financial years, with age, sex, comorbidities, ASA grade, surgeon, admission and discharge dates | Fact (from brief) | | | |

## 5. Data Inventory & Feasibility Assessment
| Source | Business meaning | Owner | Grain/keys | Coverage | Point-in-time? | Quality risks | Privacy | Status |
|---|---|---|---|---|---|---|---|---|
| Admission-level knee-replacement extract | Core analysis table | Each hospital's records/IT team (system to be confirmed) | One row per admission | 2 financial years, A ~1,100 and B ~800 | Not relevant (retrospective) | Possible differences in systems and coding between sites, possibly date-only timestamps, possible missing comorbidity fields [all To investigate] | Patient-level health data; confirm DPDP Act 2023 obligations and institutional rules with compliance | [Confirmed] it exists per brief; field detail [To investigate] |
| Procedure and diagnosis codes (to define cohort) | Identify elective primary TKR vs revision/bilateral | Medical records / IT | Admission | Same | n/a | Local coding differences | As above | [To investigate] |
| Surgeon identifier | Cluster variable | Hospital records | Admission | Same | n/a | Same surgeon may be spelled differently; consultants vs assistants | Pseudonymise | [Confirmed] per brief |
| Payer/insurance type, discharge destination, theatre date, rehab/physio timestamps | Additional drivers of stay | Billing, ward systems | Admission | Unknown | n/a | May not exist | As above | [To investigate]; would materially strengthen the analysis |

**Feasibility verdict:** feasible for the core question given the stated fields, provided Q1 and Q2 are resolved. The key limitation is that the stated variables may not capture all drivers of stay (social support, distance from home, insurance pre-authorisation delays, physiotherapy availability). **Blocking dependencies:** data access approval (Q4), definition alignment (Q1, Q2).

## 6. Data Quality & Preprocessing Plan
| Step | Rationale | Method | Risks | Validation check |
|---|---|---|---|---|
| Pseudonymise and keep data in the client environment | Privacy | Hash IDs; analysis runs on client infrastructure | None | Access log |
| Reconcile definitions across sites | Different systems | Data dictionary comparison; side-by-side field profiles | Silent definitional differences | Compare timestamp precision and discharge-event meaning at each site |
| Apply cohort definition | Comparable populations | Rule-based filter on codes; log exclusions by site | Exclusion rules applied unequally | Exclusion counts by site and reason reported |
| Compute LOS | Outcome | Discharge date minus admission date; check for negatives, zeros, and extreme values | Same-day or date-only rounding | Distribution plots by site; manual review of extremes against source records |
| Duplicates and readmissions | Independence | Check repeat patients and bilateral staged procedures | Non-independent rows | Count of patients with multiple rows |
| Missing data | Adjustment variables | Report missingness by site; if modest, multiple imputation with site as a predictor; complete-case as sensitivity | Missingness differs by site | Compare imputed vs complete-case estimates |
| Comorbidity summary | Case-mix | Use a standard index if codes allow (for example Charlson or Elixhauser), otherwise individual flags | Coding intensity differs by site, so sicker-looking patients may simply be better documented | Compare comorbidity counts per patient by site and by surgeon |
| Do not drop long stays silently | Long stays are the signal | Keep all; handle by robust methods or sensitivity | Outliers dominate the mean | Report results with and without top percentile |

## 7. Feature & Target Design
- **Outcome:** LOS in days, defined as discharge date minus admission date. Admission date means hospital admission, not surgery date; whether pre-operative days are included matters if A admits the day before surgery and B admits the same day. **Primary recommendation:** also compute **post-operative LOS** (surgery date to discharge) if the surgery date is available [To investigate], since it removes admission-practice differences.
- **Distribution:** LOS is a count of days and typically right-skewed [Assumed]; modelling choices in §14 reflect that.
- **Exposure:** hospital (B vs A). This is a site label, not a manipulable treatment.
- **Adjustment covariates (all known before or at admission):** age, sex, comorbidity (index or flags), ASA grade. Admission month/quarter and financial year are added as time controls.
- **Cluster:** surgeon (nested within hospital unless surgeons operate at both).
- **Do not adjust for** anything that occurs after admission and may be affected by the hospital's process (complications, ICU stay, discharge destination), since that would adjust away part of the effect we are trying to measure. Report these as descriptive.
- **Exclusions to confirm:** in-hospital deaths, transfers out, revisions, bilaterals, emergency or trauma cases.

## 10. Metrics & Decision Criteria
| Tier | Metric | Definition | Why | Caveat |
|---|---|---|---|---|
| Primary | Adjusted difference in mean LOS (B minus A), days, with 95% CI | From the primary model, averaged over the pooled case-mix | Directly answers "how large" | Observational; association only |
| Primary | Adjusted ratio of means with 95% CI | Exponentiated hospital coefficient in a log-link model | Relative gap is easier to compare across procedures | |
| Secondary | Raw difference in mean and median LOS with CI | Unadjusted | Shows what management sees today | Confounded by case-mix |
| Secondary | Standardised effect size | Difference in means divided by pooled SD | Comparability | Not a substitute for days |
| Diagnostic | Proportion with LOS above a clinically agreed cut-off (for example "prolonged stay") | Defined with clinicians | Tail may drive the mean | Cut-off [TBD with client] |
| Diagnostic | Between-surgeon variance | Random-effect variance component | Shows how much variation sits at surgeon level | Unreliable with few surgeons |
| Business | Bed-days per year associated with the gap | Adjusted difference × annual case volume at B | Translates to capacity and cost; not a counterfactual saving | Volume from the data; cost of a bed-day [TBD with client] |

**Decision rule (to agree before looking at results; exhaustive).** Let T be the practical importance threshold and [L, U] the 95% CI of the adjusted difference (B minus A). (1) L > T: real and material. (2) 0 < L ≤ T < U: real, but whether it is material is uncertain. (3) 0 < L and U ≤ T: real but small. (4) L ≤ 0 ≤ U with U ≥ T: inconclusive, since both no gap and a material gap are compatible. (5) L ≤ 0 ≤ U with U < T: no material gap (any gap is below T). (6) U < 0: B shorter. T is [TBD with client] and **must be fixed before the Discovery phase exits**.

## 13. Bias and Confounding Audit (replaces the predictive leakage checklist)
| Risk | Applies? | Where it could occur | Mitigation | Owner |
|---|---|---|---|---|
| Hospital label confounded with all site-level factors | Yes | With two sites, the hospital effect bundles staffing, physiotherapy availability, referral base, systems and local practice; it cannot be split into those parts | State this explicitly in the report; do not attribute the gap to any one factor | Analyst |
| Case-mix confounding | Yes | B may treat older or sicker patients (tertiary referral) | Adjust for age, sex, comorbidity, ASA | Analyst |
| Definitional difference in LOS | Yes | Different admission/discharge conventions | Reconcile (Q1); use post-operative LOS | HIS/IT |
| Coding intensity difference | Possible | Comorbidities documented more at one site | Compare coding density; sensitivity without comorbidity index | Analyst |
| Surgeon–hospital confounding | Yes | Surgeons tied to one site (nested vs crossed structure depends on Q3) | Surgeon random effect; report overlap; say what cannot be separated | Analyst |
| Selection into hospital | Possible | Patients may choose hospitals by insurance, region or complexity | Describe; sensitivity analysis for unmeasured confounding | Analyst |
| Time effects | Possible | A policy change or staffing change in one period | Adjust for period; time-sliced estimates | Analyst |
| Mediators wrongly adjusted | Avoid | Post-admission variables | Pre-specify covariates | Analyst |
| Informative exclusion (deaths, transfers) | Possible | Excluding them biases LOS downward | Report counts by site; sensitivity analysis | Analyst |
| Multiple looks | Avoid | Fishing across subgroups | Pre-specify (see §14) | Analyst |

## 14. Statistical Inference & Causal Analysis Plan
**Estimand.** The **marginal** (population-averaged) difference and ratio in mean LOS between B and A, standardised to the pooled case-mix of both hospitals. It is obtained from the fitted model by standardisation (g-computation: predict LOS for every patient as if treated at A and as if at B, average, then contrast), with CIs from a surgeon-clustered bootstrap. The OLS-with-cluster-robust-SE fallback targets the same estimand; the log(LOS) fallback targets a geometric-mean ratio (a different estimand) and quantile regression targets a median difference, so both are reported only as sensitivity results. Associational wording applies throughout, because the hospital label is not a manipulable treatment. in the population of elective knee-replacement patients treated at these two hospitals during the study period.

**Hypotheses.** H₀: adjusted mean LOS at B equals that at A. H₁: they differ (two-sided; management's belief is directional, but a two-sided test is the conservative choice and allows the possibility that B is shorter). α = 0.05.

| Question | Design / test | Key assumptions | Checks | Fallback |
|---|---|---|---|---|
| Raw difference | Welch's t-test; bootstrap CI for the mean difference | Independence (violated by surgeon clustering) | Distribution plots | Make the surgeon-clustered bootstrap the primary raw CI (Welch shown for reference); Mann–Whitney as a shift-in-distribution complement |
| Adjusted difference (primary) | Generalised linear mixed model, hospital as fixed effect, surgeon as random intercept (nested in hospital; crossed if Q3 shows surgeons at both sites), log link. **Family selection rule:** if LOS is whole days with many small values, start with negative binomial; if recorded as continuous or date-time, start with gamma; choose by dispersion, residual checks and AIC, and report the other as a sensitivity | Correct mean–variance structure; random effects approximately normal | Residual and Q-Q plots; dispersion; compare negative binomial and gamma fits (Poisson only as a dispersion check); influence diagnostics | Linear regression on log(LOS) (changes the estimand to a geometric mean ratio); OLS with cluster-robust SEs by surgeon; quantile regression for the median |
| Case-mix balance | Standardised mean differences between sites on all covariates | Overlap | SMD plots; check covariate overlap | Restrict to the region of overlap; propensity weighting as a sensitivity method |
| Where variation sits | Between-surgeon variance within the model, and a descriptive per-surgeon table. With only two hospitals, a between-hospital variance component is **not** estimable; the hospital contrast is a single fixed effect | Enough surgeons | **Minimum rule:** if fewer than about 8–10 surgeons per site [Assumed rule of thumb, to confirm with a statistician], drop the random effect and use surgeon-clustered robust SEs plus the descriptive table | Descriptive per-surgeon table with CIs |
| Distribution tail | Compare share of prolonged stays and quantiles (median, 75th, 90th percentile) | | | Quantile regression |
| Unmeasured confounding | Bias analysis: E-value applied to the ratio of means (approximate, treating it as a risk-ratio-scale quantity, with the approximation stated), or a simple benchmark against the strongest observed covariate | | | State the strength of hidden confounder required to erase the gap |

**Effect sizes and CIs.** Report in days, as a ratio, and as a standardised effect, each with a 95% CI, before any p-value. Convert to bed-days per year associated with the gap at B.

**Power / MDE.** The sample sizes are fixed (n₁ ≈ 1,100 and n₂ ≈ 800, total 1,900). For a two-group comparison of means with α = 0.05 and 80% power, MDE ≈ 2.8·σ·√(1/n₁ + 1/n₂). With the stated sample sizes this evaluates to **about 0.13 standard deviations of LOS** (computed with a script from the brief's counts; ignores surgeon clustering and covariate adjustment). Clustering by surgeon enlarges this by the design effect 1 + (m − 1)·ICC, where m is mean cases per surgeon and ICC is the intra-surgeon correlation; neither is known yet. Covariate adjustment reduces it. Convert to days once σ is observed in the data. Because the question is "how large", the analysis is judged by CI width more than by power. Plan a simulation on the real data structure once surgeon counts are known.

**Multiple testing and pre-registration.** One primary hypothesis (adjusted difference, all eligible cases). All subgroup analyses (by ASA grade, age band, sex, surgeon, year) are **exploratory**, reported with Benjamini–Hochberg control and labelled as such. Write the analysis plan and covariate list into a dated protocol before outcome data are examined.

**What this can and cannot show.**
- *Can show:* whether, after adjustment for recorded patient characteristics and surgeon clustering, B's mean LOS is higher than A's, the size with uncertainty, and how much variation sits at surgeon level vs hospital level.
- *Cannot show:* that the hospital's processes *cause* the gap (it could be unmeasured patient factors, referral patterns or social circumstances), which processes matter, or that a program would close it. It also cannot generalise beyond these two hospitals and years.
- *Language:* use "is associated with", "adjusted difference", never "B causes longer stay".

**Causal diagram (text), used only to choose adjustment variables:** age, sex, comorbidity and ASA → LOS; the same variables are associated with hospital (referral and case-mix); unmeasured home support, insurance and distance → hospital choice and LOS; hospital process/staffing → complications, physiotherapy timing, discharge destination → LOS (mediators, **not** adjusted); surgeon → LOS and surgeon ⊂ hospital.

**Plain-language glossary for management.** *Adjusted* means comparing like with like (similar age, health and ASA grade). *Confidence interval* is the range of gaps consistent with the data. *Mixed model* allows each surgeon to have their own typical stay. *E-value* says how strong a hidden factor would have to be to explain the gap away. *BH correction* guards against finding false patterns when many subgroups are examined.

## 15. Robustness & Sensitivity Tests
| Test | Purpose |
|---|---|
| Post-operative LOS instead of admission-to-discharge | Removes admission-timing practice differences |
| Exclude or winsorise the longest stays; also analyse log(LOS) | Check that a few outliers do not drive the mean |
| Complete-case vs multiple-imputation | Missing-data sensitivity |
| Drop comorbidity index; use individual flags | Coding-intensity sensitivity |
| Leave-one-surgeon-out; surgeons present at both sites only (if any) | Surgeon influence; identification of hospital vs surgeon |
| Year 1 vs year 2 estimates | Stability over time |
| Add or remove deaths and transfers | Informative exclusion |
| Propensity-weighted or matched comparison | Alternative adjustment strategy |
| E-value for unmeasured confounding | How strong a hidden factor would need to be |
| Subgroup estimates (age band, sex, ASA grade; payer type and urban/rural residence if available) | Exploratory; check for effect modification and equity patterns, interpreted cautiously |

## 17. Reporting Handoff (no model deployment)
- Deliverable: a short written report with a one-page management summary, a forest-style chart of raw and adjusted differences, the sensitivity table, and a data and methods appendix.
- Reproducibility: version-controlled analysis code, fixed random seeds for bootstrap, a data dictionary, and a log of exclusions. Run inside the client environment.
- **If a program is launched:** the follow-up evaluation should be designed *before* launch (see §3 A2). Recommended options are a before/after design with Hospital A as a comparison site (difference-in-differences) or a staged roll-out. This requires a separate causal plan and ethics review.
- Human oversight: the orthopaedic lead and management review the findings together before any decision, and the report states its limits so that results are not used to judge individual surgeons.
- Environment: pin software and package versions (lockfile), and store the dated protocol in the group's version-control repository, locked before outcome analysis.
- Governance: confirm data-protection obligations (India's Digital Personal Data Protection Act 2023 and any institutional ethics requirements) with the client's compliance team; no patient-level data leaves the client environment.

## 18. Risks, Mitigations, Dependencies & Open Decisions
| Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|
| LOS defined differently at each site | Medium | High | Resolve in Discovery; use post-operative LOS | HIS/IT |
| Unmeasured case-mix drivers explain the gap | Medium | High | Request additional fields; E-value; wording of conclusions | Analyst |
| Surgeons do not overlap across sites | Medium | Medium | Report as a limitation; do not claim to separate | Analyst |
| Data access delayed by approvals | Medium | Medium | Start Q4 in week 1 | Compliance |
| Management reads the result as causal | Medium | High | Explicit "can and cannot show" page | Lead |
| Few surgeons make variance estimates unstable | Medium | Low | Descriptive per-surgeon table | Analyst |

## 19. Phased Implementation Roadmap
Efforts are **provisional**, since team, data readiness and approvals are unknown.

| Phase | Work package | Dependencies | Deliverables | Acceptance criteria | Indicative effort (provisional) |
|---|---|---|---|---|---|
| Discovery | Resolve Q1–Q5; confirm data fields; obtain approvals; agree decision rule and threshold | Client contacts | Signed-off protocol, data dictionary | Blocking questions closed; threshold T fixed; protocol dated before outcome analysis | 1–2 weeks of effort; elapsed time depends on approvals [provisional] |
| Data engineering | Extract, pseudonymise, harmonise both sites; apply cohort rules | Access approval | Analysis dataset, exclusion log | Counts reconcile with the stated ~1,100 and ~800 | 1 week |
| Analysis / EDA | Profile data; raw comparison; balance table; missingness | Clean dataset | EDA report | Covariate balance and distributions reviewed | 1 week |
| Modelling (inference) | Primary mixed model; variance decomposition; fallbacks | EDA | Estimates with CIs | Assumption checks passed or fallback applied | 1 week |
| Validation (robustness) | Sensitivity analyses in §15; E-value | Primary model | Sensitivity table | Conclusion stated as stable or fragile | 1 week |
| Reporting | Management report and read-out | All above | Report and presentation | Reviewed by clinical lead and management | 1 week |
| Monitoring | Optional: define post-program evaluation design | Management decision | Causal design note | Agreed before launch | Separate scope |

## 20. Decision Log
| # | Decision | Rationale | Alternatives | Key assumptions | Risk | Validation method |
|---|---|---|---|---|---|---|
| 1 | Treat as inferential, not predictive | The question is whether a difference is real and how large | LOS prediction model | Management wants a population-level answer | None material | Client confirms |
| 2 | Primary estimator: mixed GLM with surgeon random effect | Handles skew, count outcome, clustering, case-mix | OLS on log LOS; Welch alone | Adequate surgeon count | Model misfit | Residual checks; compare fallbacks |
| 3 | Report raw and adjusted estimates side by side | Shows how much case-mix explains | Adjusted only | | None | Balance table |
| 4 | Two-sided α = 0.05 | Conservative; allows B to be shorter | One-sided | | None | Pre-specified in protocol |
| 5 | Subgroups exploratory with BH control | Avoid false discoveries | Confirmatory subgroups | | Low power | Labelling |
| 6 | Do not adjust for post-admission variables | Avoid adjusting away the effect | Adjust for complications | | Residual confounding | DAG review |
| 7 | Causal question separated and deferred | Cross-site comparison cannot identify program effect | Fold into this analysis | | Misinterpretation | "Can and cannot show" section |
| 8 | Practical-importance threshold set by management before results | Prevents post-hoc judgement | Decide after seeing results | Management will commit | Delay | Q5 |

## 21. References
None consulted. Regulatory references (for example the Digital Personal Data Protection Act 2023 and applicable ICMR ethical guidelines) are to be verified with the client's compliance team.
