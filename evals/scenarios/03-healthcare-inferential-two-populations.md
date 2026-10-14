# Scenario 03 — Inferential comparison of two populations (Healthcare)

## Prompt
Client: a hospital group with two tertiary hospitals (Hospital A in Pune, Hospital B in Nagpur). Management believes
Hospital B has a longer average length of stay (LOS) for elective knee-replacement surgery and wants to know whether
the difference is real and how large it is, before launching a process-improvement program. They can provide
admission-level data for the last 2 financial years (~1,100 knee replacements at A, ~800 at B) with age, sex,
comorbidities, ASA grade, surgeon, admission and discharge dates. Prepare the analysis plan.

## Expected behaviours (must)
- Inferential lens; no predictive ML model / hyperparameter tuning / deployment sections (or explicitly omitted).
- Estimand: case-mix-adjusted difference (or ratio) in mean LOS; unit = admission; clustering by surgeon/patient considered.
- Skewed LOS handled (log/Gamma GLM, bootstrap, robust SEs); Welch over Student t for raw comparison.
- Effect size + CI primary; practical significance threshold agreed with client; power/MDE commentary given sample sizes.
- Confounding/case-mix, coding differences, outliers/deaths, discharge practices; does NOT claim causation for hospital practices.
- Healthcare data governance (DPDP, ethics as needed).
