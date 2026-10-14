---
title: Branch Performance with AI/ML — Data Science Solution Plan (Quick Triage)
client: Cooperative bank (name not provided)
industry: BFSI
prepared_by: Data Science team
date: 2026-10-14
version: 0.1 (draft)
depth: Quick triage
classification: Confidential
---

# Branch Performance with AI/ML — Data Science Solution Plan (Quick Triage)

## 1. Executive Summary
- **Brief received:** the MD said "We want to use AI and machine learning to improve our branch performance. We have lots of data." That is the whole brief. **[Confirmed]**
- **Why this is not a full plan:** the brief names no decision, no definition of "performance", and no data source. A modelling plan written now would rest on guesses. This document is a triage: it sets out the plausible framings, what each needs, the questions that decide between them, and a short discovery phase.
- **Working recommendation [Assumed]:** start with a descriptive, peer-adjusted branch performance diagnostic (Exploratory lens). It needs only data the bank probably has, and it settles what "performance" means. Move to a predictive model only once the discovery questions have answers.
- **What must be true:** (1) the MD or a delegate names the performance measures that matter, (2) branch-level data for at least 24 months can be extracted, (3) a named owner can act on the findings (for example regional heads).
- **Top risks:** optimising a metric that is not the one the MD means; a small number of branches (a guess; the count is unknown) limiting any branch-level model; findings that are correlational but read as causal; data-protection and cooperative-banking regulatory obligations.
- **Next step:** a 4–5 week discovery phase (§19; some tasks overlap), starting with a 60-minute stakeholder session on Q1, Q2 and Q5 (Q2 is a Week 1 gate because the data audit scope depends on the KPIs). Q3 and Q4 go to IT and Operations in Week 1.

### Scope of this plan
Quick triage sections only: 1, 2, 3, 4, 5 (short), 18 and 19 (discovery phase only). Sections 6–17, 20 and 21 are omitted because there is no target, data inventory or decision to design them against. Writing them now would be fabrication. No references were consulted, so §21 is omitted.

## 2. Business Problem & Decision Framing
Plain-language restatement: the bank wants its branches to do better and believes its data can show how. "Better" is not defined.

| Element | Definition for this case | Status |
|---|---|---|
| Decision and owner | Unknown. Candidates: branch-manager targets, resource allocation (staff, ATMs), branch network changes, product pushes | **[Open question]** |
| Prediction point / timing | Unknown | **[TBD with client]** |
| Unit of analysis | Branch (probably branch-month) | **[Assumed]** |
| Outcome / "performance" | Unknown. Candidates: deposit growth, loan growth, NPA/overdue rate, cost-to-income, customer attrition, service quality | **[TBD with client]** |
| Capacity to act | Unknown | **[TBD with client]** |
| Cost of errors | Unknown | **[TBD with client]** |
| Success criteria | None stated. Any improvement target is `[TBD with client]` | **[TBD with client]** |
| Constraints | Cooperative bank: likely regulated by RBI and state cooperative authorities. Data protection (DPDP Act 2023) applies. Details unverified | **[To investigate]** |

## 3. Analytical Problem Classification
The request fits several lenses. Each candidate framing below is a separate analysis.

| ID | Candidate framing | Lens | ML formulation | Needs | Best if the MD means… |
|---|---|---|---|---|---|
| A1 | Peer-adjusted performance diagnostic: which branches under- or over-perform given their market and size, and why | Exploratory (descriptive) | Regression or ranking of branch KPIs against context; benchmarking with peer groups; clustering | Branch KPIs, branch attributes, catchment/market data | "Show us where we are weak" |
| A2 | Forecasting branch KPIs (deposits, loans, cash demand, footfall) | Predictive | Time-series forecasting | 2+ years of monthly history per branch | "Plan ahead" or "set realistic targets" |
| A3 | Early warning of branch deterioration (for example rising overdue loans or deposit outflow) | Predictive | Classification or survival on branch-month, or loan/customer-level risk | Defined event, history of events, enough branches | "Catch problems early" |
| A4 | Customer-level models (churn, cross-sell, credit risk) aggregated to branch uplift | Predictive (+ causal for offers) | Propensity or uplift models | Customer/account data, consent, campaign history | "Grow business per branch" |
| A5 | "What would improve performance?" (staffing, hours, closing or opening branches, incentives) | Causal / Prescriptive | Quasi-experiment, DiD, synthetic control, or pilot | Intervention history or willingness to run pilots | "Tell us what to change" |

> **Note:** A5 is the question the MD is probably asking, but a predictive or diagnostic model cannot answer it. Associations between branch features and performance will not show that changing a feature changes performance. The plan must keep this distinction in front of the client.

**Baseline and validation (to be fixed after Q2/Q4):** the bar to beat for A1 is today's branch ranking or scorecard, or a naive peer-group median. Any later model is validated with temporal or branch-grouped splits and a locked test period. Experiment cards and tracking come with the full plan.

**Recommended sequence [Assumed]:** A1 first (cheap, builds data foundations, defines "performance"). Then A2 or A3 depending on the answers in §4. A5 only through pilots with comparison branches.

**Red flags:**
- Leakage and label maturity for A2–A4: event definitions and campaign history must be dated at the prediction point; recent periods may not have matured outcomes.
- No named decision or owner.
- A vague, possibly multi-dimensional target.
- Small branch count, so overfitting is likely at branch level.
- A "lots of data" claim not yet backed by any specific source.
- Causal expectation attached to a descriptive or predictive tool.

## 4. Assumptions, Unknowns & Client Clarification Questions

| ID | Statement | Type | Impact if wrong | Owner | Needed by |
|---|---|---|---|---|---|
| Q1 | **Which decision should the output change, and who takes it?** (branch targets, staffing, network, products) | Open question | Determines the whole plan | MD | Before discovery ends |
| Q2 | **What does "branch performance" mean?** Which 3–5 KPIs, and how are branches judged today? Blocks A1–A3 (target and baseline) | Open question | Wrong target, wasted modelling | MD / Head of Operations | Week 1 gate |
| Q3 | **What data exists?** Core banking, loan system, CRM, HR/staffing, branch costs; history length; can it be extracted at branch-month grain? | Open question | Feasibility | IT / Head of Data | Week 1 |
| Q4 | **How many branches does the bank have, and how much history per branch?** | Open question | Rule of thumb, unsourced: with few branches (say under ~50), branch-level models are weak and simple benchmarking or pilots are preferable | Operations | Week 1 |
| Q5 | **Has the bank made interventions in some branches (new managers, hours, renovations, incentive schemes)?** Is it willing to pilot? | Open question | Whether any causal claim is possible | MD | Before discovery ends |
| A-1 | Unit of analysis is branch-month | Assumption | Grain of all datasets | DS team | Week 1 |
| A-2 | Data lives in a core banking system with monthly extracts possible | Assumption | Effort and timeline | IT | Week 1 |
| A-3 | The bank is India-based and falls under RBI and state cooperative regulation | Assumption | Compliance controls | Compliance | Week 1 |
| A-4 | No existing branch analytics or scorecard is in use | Assumption | Baseline to beat | Operations | Week 1 |
| F-1 | Client's statement: "use AI and ML to improve branch performance; we have lots of data" | Fact | n/a | n/a | n/a |

## 5. Data Inventory & Feasibility Assessment (short)
No data source has been confirmed. All entries are candidates to check in discovery.

| Candidate source | Why useful | Grain | Status |
|---|---|---|---|
| Core banking: deposits, loans, balances, transactions | Core KPIs | Account / day, aggregable to branch-month | **[Assumed]** |
| Loan management / collections | Overdue and NPA measures | Loan / month | **[Assumed]** |
| Branch master (location, size, age, staff count, type) | Peer groups and context | Branch | **[To investigate]** |
| HR / staffing and cost data | Productivity, cost-to-income | Branch-month | **[To investigate]** |
| CRM / complaints / service data | Quality of service | Customer / event | **[To investigate]** |
| External: local demographics, competitor branches, economic indicators | Market adjustment | District / pin code | **[To investigate]** |

For each source, discovery records history length and as-of (point-in-time) availability. The first pass uses branch-level aggregates only; customer-level data (A4) is out of scope until consent and governance are confirmed.

**Feasibility verdict:** unknown. "Lots of data" often means many transactions but few branches and little structured branch context. That is a risk, not a finding. Sensitive customer data should stay in the bank's environment, with branch-level aggregates used wherever possible.

## 18. Risks, Mitigations, Dependencies & Open Decisions

| Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|
| Target ambiguity: optimising the wrong KPI | High | High | Settle KPIs in discovery (Q2); agree on a scorecard | MD / DS lead |
| Few branches, so models overfit | Medium (unknown) | High | Peer benchmarking, simple regularised models, report uncertainty | DS lead |
| Correlation presented as cause | High | High | Label findings as associations; use pilots for A5 | DS lead |
| Data fragmented or low quality across systems | Medium | High | Data audit in discovery before commitments | IT / DS |
| Branch rankings used punitively, harming staff or gaming behaviour | Medium | Medium | Adjust for market context; governance on use of scores | MD / HR |
| Regulatory and data protection (RBI, state cooperative rules and the DPDP Act are named from general knowledge; confirm with compliance): PII, consent, residency | Medium | High | Compliance review before data access; aggregate data; keep data in the bank's environment | Compliance |
| Unfair or opaque branch rankings (explainability, human oversight, subgroup effects such as rural/urban or branch type) | Medium | High | Peer-adjusted, explainable scorecards; human review before any staff-facing use; subgroup checks | MD / HR / DS lead |
| Statistical: ranking noise, multiple comparisons, underpowered pilots | High | Medium | Uncertainty bands on rankings; multiple-comparison caveat; power/MDE check before any A5 pilot | DS lead |
| Dependence on key stakeholders | Medium | Medium | Name a single sponsor and a data owner | MD |

## 19. Phased Implementation Roadmap (discovery phase only)
Effort ranges are **provisional**: team, infrastructure and data are unknown.

| Phase | Work package | Dependencies | Deliverables | Acceptance criteria | Indicative effort (provisional) |
|---|---|---|---|---|---|
| Discovery | Stakeholder session on Q1, Q2, Q5 | MD availability | Written decision and KPI definitions | MD signs off on 3–5 KPIs and a named decision owner | 1 week |
| Discovery | Data audit: list systems, owners, history, grain, quality | IT access (Q3, Q4) | Data inventory with statuses upgraded to Confirmed or ruled out | Every candidate source marked | 1–2 weeks |
| Discovery | Baseline: current branch reporting and any scorecard | Operations | Description of today's measure of performance | Documented | 1 week |
| Discovery | Recommendation and full plan | All above | Full solution plan covering the chosen framing(s) (A1–A5) | Client sponsor approves scope | 1 week |

Later phases (data engineering, EDA, modelling, validation, deployment, monitoring) are deliberately not planned until discovery completes.
