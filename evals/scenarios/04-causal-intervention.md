# Scenario 04 — Causal question involving an intervention (Retail)

## Prompt
Client: a national apparel retailer. Six months ago they rolled out a new loyalty-app "personalised offers" feature to
40 of their 220 stores (stores chosen by the regional managers, mostly larger metro stores). Sales in those 40 stores
are up 12% year-on-year versus 5% in the other stores. The CMO wants to claim the feature "caused a 7-point lift" and
decide whether to roll it out to all stores. Prepare the solution plan to answer this properly.

## Expected behaviours (must)
- Causal lens; explicitly rejects the naive 12% vs 5% comparison (selection bias: managers chose larger metro stores).
- Defines estimand (ATT on store sales/margin), unit = store-week, interference/cannibalisation considerations.
- Proposes DiD with pre-trend/event-study checks and/or synthetic control; matching on pre-period trends; staggered rollout estimators if applicable.
- Recommends a randomised (cluster/store-level or stepped) rollout for remaining stores as the stronger design, with power considerations given ~180 stores.
- Sensitivity/placebo tests; states what cannot be identified.
- Does not treat the 7-point gap as the effect; no fabricated estimates.
