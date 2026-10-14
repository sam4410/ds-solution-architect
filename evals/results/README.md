# Evaluation log

Raw run folders (`<run-id>/`) are git-ignored. Notable runs are summarised here.

## Run 2026-10-14 (v0.1.0): all 5 scenarios
Graded by an independent reviewer pass (ds-plan-review plus the scenario's expected behaviours).

| Scenario | Specialists routed | Gates (G1–G8) | Expected behaviours | Fabrication |
|---|---|---|---|---|
| 01 Retail forecasting | framing, data, model-selection, validation, experiment, evaluation + reviewer agent | 5,4,4,4,5,4,5,4 | 6 PASS, 2 PARTIAL | None |
| 02 BFSI churn | framing, data, inference, model-selection, validation, experiment, evaluation + reviewer agent | 5,4,5,4,4,4,5,4 | 6 PASS, 2 PARTIAL | None |
| 03 Healthcare LOS (inferential) | framing, inference, data + reviewer agent (no ML sections) | 5,4,4,4,4,4,4,4 | 5 PASS, 1 PARTIAL | 1 (worked example from a placeholder σ) |
| 04 Retail causal rollout | framing, inference + reviewer agent | 5,4,4,4,5,4,4,5 | 5 PASS, 1 PARTIAL | None |
| 05 Ambiguous brief | framing only, giving a Quick triage | 5,4,4,4,4,4,4,4 | 5 PASS | None |

**Changes made in response:**
- Banned worked numeric examples built on invented inputs; required arithmetic to be computed with code.
- Added a consistency pass and a "Needed from the client next" box to the orchestrator.
- Required the pure canonical baseline (e.g., pure seasonal-naive) in model selection.
- Added an entity-disjoint sensitivity fold and an explicit gap rule for overlapping windows to validation.
- Added status/resolution as-of leakage to the leakage checklist.
- Made horizon-specific error and an offline cost-weighted metric headline metrics for forecasting.
- Added cluster-randomised power guidance.

## Re-run 2026-10-14 (after fixes): scenarios 03 and 04
| Scenario | Gates | Expected behaviours | Fabrication |
|---|---|---|---|
| 03 Healthcare LOS | 5,4,4,4,4,4,4,5 | **6/6 PASS** | None (MDE expressed in SD units using the brief's n only) |
| 04 Retail causal rollout | 5,4,4,4,5,4,4,4 | **6/6 PASS** | None (arithmetic independently recomputed and matched) |

The remaining reviewer notes are minor internal-consistency edits (a cross-reference, the wording of one sentence).
