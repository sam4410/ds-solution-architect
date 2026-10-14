# Robustness, Deployment & Monitoring Playbook

## 1. Pre-deployment robustness
| Check | Method |
|---|---|
| Subgroup performance | Metric + calibration by segment, site, channel, protected attribute |
| Sensitivity analysis | Perturb inputs (noise, missingness), vary assumptions (costs, thresholds) |
| Stress / scenario tests | Simulate shocks (price rise, pandemic-like demand break, rate hikes) |
| Uncertainty | Prediction intervals (quantile models, conformal prediction), bootstrap CIs on metrics |
| Calibration | Reliability curve on recent out-of-time data; recalibrate if needed |
| Stability | Score/PSI stability across months; feature-importance stability across folds |
| Explainability | Global (permutation importance, SHAP summary, partial dependence) and local (SHAP, reason codes) — clearly labelled as model behaviour, not causation |

## 2. Deployment options
| Pattern | When |
|---|---|
| Batch scoring (daily/weekly) | Most planning decisions: forecasts, risk lists, campaign targeting |
| Real-time API | Fraud at authorisation, credit decision at application, clinical alerts at point of care |
| Embedded in workflow tool (EHR, LOS, CRM) | Adoption depends on in-workflow delivery |
| Human-in-the-loop | High stakes (clinical, credit decline), low-confidence cases, regulatory requirement |
| Shadow mode → champion–challenger → full rollout | Default safe rollout path |

Define: latency SLA, throughput, feature store / point-in-time serving parity (training-serving skew), fallback rule if model unavailable.

## 3. Monitoring
| Layer | Metrics | Trigger examples |
|---|---|---|
| Data quality | Schema, null rates, ranges, volumes, freshness | Null rate +x pp; late feed |
| Input drift | PSI / KS / Jensen–Shannon per feature (PSI > 0.1 watch, > 0.25 act — common BFSI convention) | PSI > 0.25 on key features |
| Prediction drift | Score distribution, positive rate | Alert rate doubles |
| Performance (when labels mature) | Primary metric, calibration, by segment | Below agreed floor for 2 consecutive periods |
| Business KPIs | Readmissions, losses, stock-outs, conversions | Deviation from expected value |
| Fairness | Subgroup metric gaps | Gap exceeds tolerance |
| Operational | Latency, errors, uptime | SLA breach |

Account for **label delay**: use proxy/early indicators and drift while waiting for outcomes.

## 4. Retraining & lifecycle
- Retraining cadence (scheduled) + triggers (drift, performance floor breach).
- Re-validation on walk-forward before promotion; approval gate (model risk / clinical governance).
- Rollback criteria and procedure; version registry.
- Post-deployment evaluation: did the business outcome move? (ideally via experiment / holdout group).
- Feedback loops: model-driven actions change future labels (e.g., interventions prevent readmissions → model appears worse). Keep a random holdout where ethical.

## 5. Governance & controls
Privacy (minimisation, de-identification, consent, data residency), security (access control, secrets management),
fairness assessment, auditability (lineage, decisions log, model cards), documentation for regulators,
incident response. See domain packs for sector-specific controls.
