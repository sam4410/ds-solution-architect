# Evaluations

| Scenario | Tests |
|---|---|
| 01 Retail demand forecasting | Time-dependent data, walk-forward validation, censored demand, promo leakage |
| 02 BFSI churn | Class imbalance, capacity-based metrics, grouped out-of-time split, prediction vs drivers vs causal offer effect |
| 03 Healthcare LOS comparison | Pure inferential analysis: no ML padding, case-mix adjustment, effect sizes and CIs |
| 04 Retail causal rollout | Selection bias in a non-random rollout; DiD, synthetic control, randomised extension |
| 05 Ambiguous brief (BFSI) | Insufficient information gives a Quick triage, not a fabricated blueprint |

Run: `bash evals/run_evals.sh` (all) or `bash evals/run_evals.sh "02*"`.
Each result folder contains `transcript.jsonl` (full tool trace), `solution-plans/` (.md + .docx) and `review.md`
(an independent grader's scores on checks G1–G8 plus PASS/PARTIAL/FAIL against the scenario's expected behaviours).

**Pass bar:** every check ≥ 4, no fabrication findings, and no FAIL on the expected behaviours.
Results are git-ignored. Summaries of notable runs are recorded in `evals/results/README.md`.
