# Claude External Review — Phoenix V3 Midterm Report And Next Plan

Date: 2026-06-24
Reviewer: Claude (independent external reviewer)
Packet under review: `docs/reviews/call_for_review_phoenix_v3_midterm_report_and_next_plan_2026-06-24.md`
Protocol: `docs/rebuild/v3/phoenix_v3_bounded_external_review_protocol_2026-06-22.md`
Companion: `phoenix_v3_revised_m72_plan_target_the_blocker_2026-06-24.md`

## Verdict

```text
verdict: accept_with_required_amendments
release_authorized: false
all_app_pod_spend_authorized: false
focused_pod_spend_authorized: false
major_version_mandate_overridden: false
```

The report is honest and the trunk-first direction is correct, but the next plan optimizes the families V3 already wins while under-addressing the regressions that actually block the scorecard. Continue, with the four amendments below applied before engineering resumes. Gate stays `redo_required`.

## Verified grounding

- The runner and helpers exist: `src/rtdsl/prepared_execution.py`, `src/rtdsl/partner_adapters.py` (`run_grouped_vector_sum_2d_prepared_session`, `run_radius_graph_component_union_3d_prepared_session`).
- M43 is real: in `phoenix_v3_m43_grouped_reduction_cupy_warp_prepared_runner_2026-06-23.md`, the Numba grouped-reduction variants were 0.62x / 0.68x (still CPU-slower); **only the CuPy RawKernel warp prepared-session route hit 3.45x** and cleared the original CPU-hot inversion. The win source is the CuPy partner continuation, not the V3 kernel.
- M28 froze the Set-A trunk family as `aggregate_tree_fused_vector_sum` (Barnes-Hut's structure). M43's grouped-vector-sum is the continuation that family consumes.

## Honesty assessment

High. The four-category separation (real runtime / focused evidence / process / waste) is the correct frame, applied to the report's own work without flinching. Calling `Ran 752 tests OK` "not progress," admitting M70/M71 displaced the trunk, and the Goal-Level Audit are genuine self-correction. Q1: **yes, honest.**

## Required amendments

### A1 — Win-families and blocker-families are disjoint (central flaw)
Trunk wins are M40 (component union) and M43 (grouped reduction). Scorecard blockers are barnes_hut Set-A 0.844x, librts Set-B 0.937x, RTNN not cleared, and a Set-A app-win shortfall (1/5). The bar is held down by **regressions in different families**, not by a shortage of wins. Set-A requires no severe regression <0.90x (barnes_hut violates) and Set-B no row <0.95x (librts violates). So the plan as written (prove the trunk on already-winning families) can succeed completely and still produce a blocked scorecard. **You cannot clear the bar by getting better at what you already win.**

### A2 — Retarget M72 at the Barnes-Hut / aggregate-tree blocker, reusing M43
M28 froze the Set-A trunk family as aggregate-tree-fused-vector-sum (Barnes-Hut); M43 already cleared the grouped-reduction inversion that feeds it. The highest-value next step is therefore **wiring M43's grouped-reduction runner into the Barnes-Hut / aggregate-tree front-door and measuring whether it moves the 0.844x blocker** — not a generic fixed-radius self-query family, which maps to RT-DBSCAN (not a current blocker). barnes_hut's 0.844x is a *regression* the report attributes to generic runtime overhead/materialization — exactly what the residency trunk removes — so there is a real chance routing it through the runner lifts it toward parity for free.

### A3 — Classify every trunk win by source
- M40 component union: runner vs legacy hot ≈ 0.994x (parity); win is wall-time from residency. Source = `residency_wall`.
- M43 grouped reduction: only CuPy hit 3.45x (Numba 0.62–0.68x). Source = `partner_continuation` (CuPy), not RT cores.

Both are legitimate V3 runtime-capability wins, but neither is "RT-core faster." Require a `win_source ∈ {residency_wall, partner_continuation, kernel}` field on every trunk evidence packet, so wins never blend into a misleading "V3 is faster" line (the v3.0 over-promotion failure) and so generality is predicted honestly.

### A4 — Make Goal B the gate; explicitly own the regression decision
Every trunk family must be tied to a named scorecard-controlling row **before** implementation; a family that moves no blocker is recorded and dropped. The plan must explicitly decide whether barnes_hut (0.844x) and librts (0.937x) are **trunk-fixable** (route through the runner) or need **severe-regression repair** (permitted as an exception). Right now they are named as blockers but no goal owns fixing them.

## Answers to the seven questions

1. Honest about state? Yes, unusually.
2. M40/M43 correctly classified as meaningful-but-bounded? Yes — add per-source classification (A3).
3. Partial Step-1/2 or reset Step 1? **Partial Step-1/2 — do not reset.** The trunk executes end to end with residency on two families. M72 is connection-to-front-door, not re-proving execution.
4. Is M72's family the right critical path? **No — retarget at the Barnes-Hut/aggregate-tree blocker (A2).** The recommended fixed-radius family maps to a non-blocker.
5. Too app-driven or runtime-driven? Overcorrected to **runtime-driven but blocker-blind.** Aim runtime work at the controlling rows (A1/A4), do not return to app tuning.
6. Resource estimates reasonable? Yes — concrete and modest. Budget one retry on M72 for residency/contract mismatches.
7. Remove/tighten/add? Add win-source classification and explicit regression ownership; tighten M72 to target the blocker; hold the line on no further process expansion.

## Conditions to upgrade to `accept_plan_continue`

Retarget M72 at a scorecard blocker (barnes_hut/aggregate-tree) using the existing M43 runner; add win-source classification; make Goal B the gate; own the barnes_hut/librts regression decision. See the companion revised plan.

## Non-authorization

Authorizes nothing: no release, no POD spend (focused or all-app), no public/broad V3-over-V2 wording, no RT-core/zero-copy wording, no V4/embedding/C-ABI. Gate remains `redo_required`. Major-version mandate not overridden.
