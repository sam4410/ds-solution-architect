# Domain Pack — Retail & Consumer (store, e-commerce, omnichannel, CPG)

> Regulatory notes are orientation, not legal advice; confirm with the client's legal/compliance team.

## 1. Common use cases → formulation
| Use case | Lens | Formulation | Key pitfalls |
|---|---|---|---|
| Demand forecasting (SKU×store×week/day) | Predictive | Global forecasting (GBM with lags) + local statistical models; hierarchical reconciliation; intermittent-demand methods | **Stock-outs censor demand**, promotions known/unknown at origin, new products (cold start), cannibalisation |
| Replenishment / inventory optimisation | Prescriptive | Probabilistic forecast → inventory policy (service level, safety stock) | Optimising forecast error instead of cost/service; lead-time variability |
| Price elasticity / markdown optimisation | Causal + prescriptive | Elasticity models (log-log, hierarchical Bayesian), experiments, optimisation | Price endogeneity (prices set in response to demand), cross-price effects |
| Promotion effectiveness | Causal | Incremental lift via experiments, DiD, synthetic control, baseline forecasts | Pull-forward, halo, cannibalisation, stockpiling |
| Customer churn / lapse (non-contractual) | Predictive | Classification on inactivity definition; BTYD models (Pareto/NBD, BG/NBD) | Churn definition arbitrary; seasonal shoppers |
| Customer lifetime value | Predictive | BTYD + Gamma-Gamma; regression/GBM | Horizon definition, returns |
| Segmentation | Exploratory | RFM, clustering, mission-based segmentation | Actionability, stability |
| Recommendation / personalisation | Predictive | Popularity → CF → sequential models; LTR | Offline-online gap; requires A/B tests |
| Market basket analysis | Exploratory | Association rules (support, confidence, lift) | Spurious rules from popular items |
| Store/site performance comparison | Inferential | Mixed models with controls; matched comparisons | Store size, location, catchment confounding |
| New store site selection | Predictive | Regression with geo features, analogue stores | Few examples, spatial autocorrelation → spatial CV |
| Returns / fraud (e-com) | Predictive | Classification | Label delay (return windows) |
| Shelf/planogram compliance, product recognition | CV | Detection/classification | Store lighting/camera shift |
| Review/feedback analytics | NLP | Sentiment/topic/aspect extraction | Multilingual and code-mixed text (Hinglish) |
| Workforce/footfall forecasting | Predictive | Forecasting hourly/daily | Events, weather |

## 2. Typical data sources
Internal: POS transactions (line-level), e-commerce orders & clickstream, inventory/stock positions (on-hand, in-transit),
stock-out logs, purchase orders & lead times, price history, promotion calendar & mechanics, markdowns, product master/hierarchy,
store master (size, format, cluster), loyalty/CRM, returns, supply chain/DC data, planograms, footfall counters, marketing spend.
External: holidays & festival calendars (national and regional — Diwali, Eid, Onam, Pongal, Christmas, sale events), weather,
competitor prices (scraped — check terms & legality), macro (CPI, consumer sentiment), local events, mobility/footfall
panels, syndicated market data (NielsenIQ/Circana-type), census/catchment demographics.

## 3. Data & leakage traps specific to retail
- **Sales ≠ demand** during stock-outs — use availability flags; exclude/impute censored periods.
- **Future promotions/prices** included as features when not finalised at forecast origin (check promo calendar lock dates).
- **Restated sales** (returns netted later).
- **New/discontinued items** — cold start and survivorship (only items that survived appear in history).
- **Calendar alignment** — retail 4-4-5 calendar vs ISO weeks; moving festivals (lunar calendars).
- **Store openings/closures/refits** — structural breaks.
- **Cannibalisation & halo** — item-level models miss cross-effects.

## 4. Metrics conventions
WAPE (volume-weighted), MASE/RMSSE (scale-free across SKUs), bias (systematic over/under), forecast value added (FVA) vs naive and vs current planner forecast,
horizon-specific accuracy, quantile loss for safety stock, service level / fill rate, stock-out rate, inventory days/turns,
lost sales, markdown cost; marketing: incremental revenue/margin, ROI, uplift; recsys: CTR, conversion, AOV, revenue/session.

## 5. Governance checklist (confirm applicability)
Consumer data protection (India DPDP Act 2023 and Rules; GDPR/UK GDPR; CCPA/CPRA), marketing consent and do-not-disturb rules,
PCI DSS for payment data, price discrimination and consumer-protection rules for personalised pricing,
competition-law limits on sharing competitor price data, terms of service for scraped data, fairness in personalisation.

## 6. Questions to ask the client
1. Forecast grain, horizon, frequency and the downstream decision (ordering, allocation, staffing)?
2. Are stock-out/availability data recorded? Is the promotion calendar known in advance, and how far?
3. Current forecasting method and its accuracy (benchmark for FVA)?
4. Lead times, review periods, MOQ, shelf-life constraints?
5. New products/stores frequency?
6. Can we run store- or customer-level experiments?
