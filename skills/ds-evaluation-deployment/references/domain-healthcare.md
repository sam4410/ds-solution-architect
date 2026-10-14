# Domain Pack — Healthcare (providers, payers, pharma/life sciences, health-tech)

> Regulatory notes are orientation, not legal advice. Always confirm the current regulatory position
> and the client's own policies with their compliance/legal team; regulations change.

## 1. Common use cases → formulation
| Use case | Lens | Formulation | Key pitfalls |
|---|---|---|---|
| 30-day readmission risk | Predictive (+ causal for interventions) | Binary classification or discrete-time survival at discharge | Planned readmissions, deaths as competing risk, transfers, readmission to other hospitals unobserved |
| Length-of-stay prediction | Predictive | Regression (skewed → log/quantile) or survival | Prediction point (admission vs day 2), censoring for in-house patients |
| Sepsis / deterioration early warning | Predictive | Classification on rolling windows / survival | Label timing (onset definitions), alert fatigue, documentation-driven leakage (antibiotic orders, lactate ordered *because* of suspicion) |
| Bed/ED/OPD demand forecasting | Predictive | Time-series forecasting (hourly/daily, multiple seasonality) | Holidays, epidemics, policy changes |
| No-show prediction | Predictive | Classification | Fairness (transport, income proxies); action = reminder/overbooking |
| Claims fraud, waste & abuse (payers/TPAs) | Predictive / anomaly | Anomaly detection → supervised as labels mature | Investigated-only labels, provider-level grouping |
| Claims denial prediction / coding assistance | Predictive / NLP | Classification, NLP extraction | Payer rule changes |
| Medical imaging triage | Predictive (CV) | Classification/detection/segmentation | Site/scanner shift, label noise, regulatory classification as a medical device |
| Clinical notes extraction | NLP | NER / extraction / LLM with schema | PHI handling, abbreviations, negation ("no fever") |
| Treatment / program effectiveness | Causal | Trial, target-trial emulation, DiD, RDD on risk-score cutoffs | Confounding by indication, immortal time bias |
| Comparing outcomes between hospitals/wards | Inferential | Risk-adjusted comparison (mixed models), funnel plots | Case-mix, small-volume noise, multiple comparisons |
| Drug demand / pharmacy inventory | Predictive | Forecasting (intermittent demand) | Stock-outs censor demand, expiry |
| Patient segmentation | Exploratory | Clustering on utilisation/conditions | Actionability, stability |

## 2. Typical data sources (label confirmed / assumed / to investigate)
Internal: EHR/EMR (encounters, diagnoses ICD-10, procedures, medications, vitals, labs, notes), HIS/ADT feeds,
LIS/RIS/PACS (imaging), pharmacy, billing/claims, scheduling, bed management, staffing rosters, CRM/call centre.
External: census/demographics, deprivation indices, weather, air quality, epidemic surveillance, public holiday
calendars, claims/insurance data (payers), drug master data, government health-program data (where permitted).
Standards: ICD-10, SNOMED CT, LOINC, HL7/FHIR, DICOM.

## 3. Data & leakage traps specific to healthcare
- **Documentation leakage:** orders/tests/notes created *because* clinicians suspected the outcome.
- **Discharge-time information** (final diagnosis codes, discharge disposition) used for admission-time predictions.
- **Patient overlap:** split by patient, not encounter.
- **Coding changes** (ICD version, local code updates) alter label definitions over time.
- **Death as competing risk** for readmission/LOS.
- **Missing-not-at-random labs.**
- **Site effects:** device/vendor/hospital differences — use leave-site-out validation for multi-site deployment.

## 4. Metrics conventions
Sensitivity/specificity, PPV/NPV at operational thresholds, alerts per day / per bed, number needed to evaluate,
AUROC + AUPRC, calibration (slope/intercept), decision-curve analysis (net benefit), subgroup performance
(age, sex, ethnicity where recorded, payer type, site). Survival: C-index, time-dependent AUC.

## 5. Regulatory & governance checklist (confirm applicability)
- **India:** Digital Personal Data Protection Act 2023 and its Rules (health data as personal data; consent, purpose limitation, data fiduciary obligations); ABDM health data management policy where integrating with ABDM; ICMR ethical guidelines for AI in biomedical research and healthcare; CDSCO rules where software qualifies as a medical device.
- **US:** HIPAA Privacy & Security Rules (PHI, de-identification via Safe Harbor or Expert Determination, BAAs with vendors); FDA guidance for AI-enabled software as a medical device and clinical decision support; ONC algorithm transparency requirements for certified health IT.
- **EU/UK:** GDPR (health data = special category), EU AI Act (many medical AI systems are high-risk), MDR for software as a medical device.
- Ethics/IRB approval for research and prospective studies; clinical safety case; human oversight (clinician remains decision-maker); model cards; reporting guidelines (TRIPOD+AI for prediction models, CONSORT-AI/SPIRIT-AI for trials).
- PHI must not leave approved environments (including to external LLM/APIs) without explicit authorisation and contracts.

## 6. Questions to ask the client
1. What clinical/operational action follows a high-risk flag, and what is the daily capacity?
2. Exact outcome definition and exclusions (planned readmissions? transfers? deaths?)
3. At what moment is the prediction needed, and which data are available in the system at that moment (and with what latency)?
4. Single site or multi-site deployment? Same EHR vendor?
5. Data residency, de-identification requirements, ethics approval status.
6. Who is clinically accountable for the model's use?
