# Problem Taxonomy — From Business Question to Analytical Formulation

Use this file to classify a client question before any method is chosen. Most failed projects
are mis-framed, not mis-modelled.

## 1. The simple lens (always start here)

Every client question collapses into one (or more) of four intents. State them in plain language
before using any technical vocabulary.

| Lens | The client is really asking… | Output is… | Success is judged by… | Typical trap |
|---|---|---|---|---|
| **Exploratory / Descriptive** | "What is going on? What does the data look like?" | Summaries, segments, patterns, hypotheses | Insight that changes a decision or generates testable hypotheses | Reporting patterns as if they were causes |
| **Predictive** | "What will happen / which one is it?" for a *new, unseen* case | A score, label, forecast or ranking per unit | Out-of-sample accuracy *at the decision point*, business value of acting on it | Building a model nobody can act on; leakage |
| **Inferential** | "Is this difference/relationship real, and how big is it, in the population?" | Estimates with uncertainty (CI), tests | Valid assumptions, effect size, power, practical significance | p-hacking, ignoring dependence, confusing significance with importance |
| **Causal / Prescriptive** | "What happens *if we do X*? Which action is best?" | Treatment-effect estimate, policy, optimised decision | Credible identification strategy; experiment or defensible quasi-experiment | Using a predictive model's feature importances as causal effects |

Rules of thumb:
- If the client will **act on individual units** (customers, patients, SKUs) → predictive component.
- If the client wants to **know whether something works or matters** → inferential/causal component.
- If the client will **change something** (price, policy, campaign, treatment) and wants the effect → causal. Prediction alone cannot answer it.
- Mixed questions are common (e.g., "predict churn **and** tell us why customers churn **and** whether the retention offer works"). Split them into **separate analyses**, each with its own estimand, data window and validation. Never let one model answer all three.

## 2. Extended objective types (for the detailed plan)

| Objective | Question form | Example (Healthcare / BFSI / Retail) |
|---|---|---|
| Descriptive | What happened? | ED visit volumes by hour / NPA ratio by branch / sales by category |
| Diagnostic | Why did it happen (associational drill-down)? | Which wards drive readmission rise? / Which segments drive delinquency jump? / Which stores drove margin drop? |
| Predictive | What will happen for unit *i*? | 30-day readmission risk / probability of default / next-month SKU demand |
| Inferential | Is the population-level difference real? | Do two hospitals differ in LOS? / Do two branches differ in approval rates? / Do two regions differ in basket size? |
| Causal | What is the effect of intervention X? | Effect of discharge-call program / effect of limit increase on spend / effect of a promotion on incremental sales |
| Prescriptive | What should we do? | Which patients to enrol in care management / which customers get a retention offer / optimal reorder quantity |
| Experimental | How do we test X rigorously? | Pragmatic trial / champion–challenger credit strategy / store-level A/B test |

## 3. Framing checklist (fill every row; mark unknowns)

| Element | Definition | Example |
|---|---|---|
| Business decision | The concrete action that changes based on the output | "Allocate care-coordinator calls to the top-k riskiest discharges each day" |
| Decision owner / user | Who consumes the output | Care manager, credit officer, category planner |
| Decision timing | When the decision is taken (this is the **prediction point**) | At discharge; at application; every Monday 06:00 for next 4 weeks |
| Action space | What can actually be done | Call / no call; approve / decline / refer; order quantity |
| Capacity constraints | How many actions are feasible | 40 calls/day; manual review of ≤5% applications |
| Unit of analysis | Row grain of the analytical dataset | Discharge episode; application; SKU×store×week |
| Population | Who is in scope (inclusion/exclusion) | Adult inpatients excluding planned readmissions |
| Outcome / target | Precise, measurable definition | Unplanned readmission within 30 days of discharge |
| Prediction horizon | Gap between prediction point and outcome | 30 days; 12-month PD; 1–4 weeks ahead |
| Observation window | Lookback period for features | 12 months prior to discharge |
| Estimand (inference/causal) | The exact quantity to estimate | ATE of the call program on 30-day readmission among eligible discharges |
| Cost of errors | Consequence of FP vs FN | Missed high-risk patient (FN) ≫ unnecessary call (FP) |
| Success criteria | Measurable acceptance threshold agreed with client | Recall@top-40/day ≥ X% above current rule; ≥Y readmissions avoided |
| Constraints | Regulatory, latency, interpretability, data residency | Explainable adverse-action reasons; on-prem only |

Always separate:
- **Confirmed facts** (stated by client or verified in data)
- **Working assumptions** (we proceed as if true; must be validated, owner + date)
- **Open questions** (block or materially change the plan)

## 4. ML problem-domain mapping

| Target / structure | Formulation | When an alternative is better |
|---|---|---|
| Continuous value, i.i.d. rows | Regression | Quantile regression when decisions depend on tails (stock, capacity); classification if only threshold crossing matters |
| Continuous value indexed by time | Time-series forecasting (local or global models) | Regression with lag features when many exogenous drivers and many series; hierarchical forecasting when aggregation levels must reconcile |
| Binary event within fixed window | Binary classification | **Survival analysis** when follow-up varies, censoring exists, or *when* matters (churn, default timing, readmission timing) |
| Multiple exclusive categories | Multiclass classification | Hierarchical classification for taxonomies; ordinal regression for ordered classes (risk grades) |
| Multiple non-exclusive labels | Multilabel classification | — |
| Order of items for a user/query | Learning-to-rank / recommendation | Simple popularity/co-occurrence baseline first; classification if only "buy/not buy" matters |
| No label; find groups | Clustering / segmentation | Supervised segmentation if a business outcome exists to segment on |
| Rare unusual events, few labels | Anomaly detection (unsupervised/semi-supervised) | Supervised classification once enough confirmed labels exist (fraud) |
| Free text | NLP: classification, NER/extraction, topic modelling, summarisation, semantic search | Rules/regex baseline; LLM zero/few-shot as baseline vs fine-tuned model |
| Images / scans | Computer vision: classification, detection, segmentation | Transfer learning from pretrained backbones; human-in-the-loop for clinical use |
| Time to event with censoring | Survival / time-to-event | Discrete-time hazard classification for simpler deployment |
| Effect of an action | Causal inference / uplift modelling | A/B test if randomisation is feasible — always preferred |
| Choose best action under constraints | Optimisation / decision analysis (often on top of predictions) | Simple ranking + capacity cut-off is often enough |
| High-dimensional features | Dimensionality reduction / representation learning | Feature selection when interpretability matters |

## 5. Red flags that mean "go back to framing"

- The target cannot be observed at scale, or is defined differently across systems.
- No one can name the decision the output will change.
- The question is causal ("does X drive Y?") but only observational data with obvious confounding exists and no design is defensible.
- The prediction point is undefined, so feature availability cannot be checked.
- The success metric is purely technical (AUC) with no link to business value or capacity.
- The population at deployment differs from the population in the history (new product, new geography, policy change).
