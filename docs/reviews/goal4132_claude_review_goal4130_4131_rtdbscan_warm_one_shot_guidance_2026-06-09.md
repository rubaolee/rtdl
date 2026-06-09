# Claude Review — Goals 4130–4131: RT-DBSCAN Warmed One-Shot Guidance

**Date:** 2026-06-09
**Reviewer:** Claude Sonnet 4.6 (external read-only review)
**Verdict:** `accept-with-boundary`

---

## Scope

- Goal4130: warmed one-shot probe using the Goal4117 factor-sweep runner at 65k, 131k, and 262k; three JSON pod artifacts; report; test
- Goal4131: `current_benchmark_route_decisions.py` refresh to expose warmed one-shot evidence; advisor update; report; test

Prior context reviewed: Goal4128 Claude review and Goal4129 Gemini review of Goals 4126–4127 (262k scale guidance); Goal4117 factor-sweep runner; Goal4122 131k probe; Goal4126 262k probe.

No source files were edited. No tests were run. All findings are based on reading source, test, artifact, and report files.

---

## Question 1 — Does Goal4130 fairly reuse the Goal4117 factor-sweep runner for a warmed one-shot probe, and are the artifacts cleanly commit-pinned to `f9f1b82b` with dirty flag false?

**Yes on both counts.**

All three pods carry `"schema": "rtdl.goal4117.partition_cell_factor_route_sweep.v1"`, matching the schema used by the Goal4117, Goal4122, and Goal4126 pods. The probe introduces `repeat=2, warmup=1` (one warmup run discarded, one measured run). This is the only change from prior sweep protocols (which used `repeat=4, warmup=1` for replay-only pods) — justified by the goal of charging prepare once in the one-shot total.

All three artifacts are commit-pinned to `"source_commit": "f9f1b82b022c2f2631aa4f5b70805660880debfd"` with `"source_tracked_worktree_dirty": false`. The test `test_artifacts_are_clean_commit_pinned_and_non_authorizing` verifies the commit prefix `f9f1b82b`, the clean-worktree flag, the correct `point_count` per scale, `repeat == 2`, `warmup == 1`, and all authorization flags as `false`. ✓

The `"goal": "Goal4117"` field in the JSON is the schema-provenance field, not the measurement goal. It is not an error.

---

## Question 2 — Does the one-shot total calculation make sense for the stated boundary?

**Yes. The calculation is correct and the boundary is clearly scoped.**

The one-shot total speedup compares two total costs, each equal to the sum of a single prepare plus a single replay:

```
one_shot_speedup = (current_route_prepare_sec + current_route_replay_sec)
                 / (direct_status_prepare_sec + direct_status_replay_sec)
```

where `direct_status_prepare_sec` and `direct_status_replay_sec` are taken from the best-replay-factor row. This is internally consistent: the factor selected is the one that wins on repeated-replay timing, and the one-shot speedup is then reported for the same factor. The `current_route_amortized_sec` field in the JSON equals `current_route_prepare_sec + current_route_replay_sec` exactly (verified), confirming the JSON's own amortization convention.

The boundary is that this does not make the route automatic, does not declare a universal best factor, and does not claim a whole-app speedup. These limits are restated in both the report and the registry. ✓

---

## Question 3 — Are the reported one-shot total speedups exactly supported by the JSON artifacts?

**Yes. All nine values verify exactly against the raw JSON fields and arithmetic cross-checks.**

| Scale | Profile | Best factor | JSON prepare (direct) | JSON replay (direct) | JSON prepare+replay (current) | JSON amortized_speedup | Report | Verified |
|---|---|---|---|---|---|---|---|---|
| 65k | clustered3d | 0.25 | 0.406338 | 0.031893 | 1.098135 | 2.505839 | 2.506x | ✓ |
| 65k | road3d | 0.25 | 0.041759 | 0.021128 | 0.164097 | 2.609400 | 2.609x | ✓ |
| 65k | ngsim_dense | 0.5 | 0.111794 | 0.011608 | 0.224437 | 1.818747 | 1.819x | ✓ |
| 131k | clustered3d | 0.25 | 0.412559 | 0.108817 | 1.621372 | 3.109800 | 3.110x | ✓ |
| 131k | road3d | 0.25 | 0.092838 | 0.083442 | 0.459315 | 2.605599 | 2.606x | ✓ |
| 131k | ngsim_dense | 0.25 | 0.104727 | 0.036208 | 0.480587 | 3.410003 | 3.410x | ✓ |
| 262k | clustered3d | 0.25 | 0.511874 | 0.410653 | 2.944638 | 3.191929 | 3.192x | ✓ |
| 262k | road3d | 0.25 | 0.188074 | 0.328591 | 1.173671 | 2.271629 | 2.272x | ✓ |
| 262k | ngsim_dense | 0.25 | 0.229675 | 0.095144 | 0.954759 | 2.939360 | 2.939x | ✓ |

All values match to three decimal places. The JSON `amortized_over_current_speedup` field for the best-replay-factor row corresponds exactly to the report's "One-shot total speedup" column.

The replay speedup figures in the report table also verify:
- 65k clustered3d: 0.094783 / 0.031893 = 2.972x (JSON `best_replay_over_current_speedup` = 2.9719) ✓
- 131k ngsim_dense: 0.047351 / 0.036208 = 1.308x (JSON = 1.3078) ✓
- 262k road3d: 0.471716 / 0.328591 = 1.436x (JSON = 1.4356) ✓

---

## Question 4 — Do all factor rows preserve the current grouped-stream route's component-size signature?

**Yes. Every factor row across all three scales and all three profiles carries `"same_signature": true`, and the per-profile `"all_factors_match_current_signature": true` is set throughout.**

The test `test_warmed_one_shot_total_wins_all_profiles_and_scales` asserts `assertTrue(row["all_factors_match_current_signature"])` for every profile at every scale. ✓

This holds for both factor 0.25 and factor 0.5 at all nine (scale, profile) combinations, including the two sub-parity rows (65k ngsim_dense factor 0.25 at 0.969x replay, 262k road3d factor 0.5 at 0.281x replay). Sub-parity rows still match the signature even though they are slower — the correctness contract and the performance story are independent. ✓

---

## Question 5 — Does Goal4131 update the route advisor to expose prepared direct-status as an explicit user-selectable option for tested one-shot and repeated component-signature workloads, without hidden dispatch, automatic route selection, automatic partner selection, or automatic factor selection?

**Yes, on every required dimension.**

`explain_rt_dbscan_explicit_route_choice` (app lines 106–188) now includes `one_shot_total_speedup_vs_current` in each direct-status option entry (line 143). The `when` field distinguishes repeated and one-shot workloads (line 145–149). All advisory enforcement flags remain:

- `"status": "advisory_only_no_dispatch"` ✓
- `"user_must_select_route": True` ✓
- `"automatic_dispatch_authorized": False` ✓
- `"automatic_partner_selection_authorized": False` ✓
- `"automatic_partition_cell_factor_selection_authorized": False` ✓
- `"hidden_dispatch_allowed": False` ✓

The function still does not call `run_rt_dbscan_benchmark` or any route executor. The only dispatch-adjacent action is sorting `tested_options` by `abs(int(row["point_count"]) - resolved_point_count)`, which is informational and changes no runtime behavior.

The test `test_advisor_exposes_one_shot_direct_status_without_dispatch` verifies that for `ngsim_dense`, `point_count=262144`, `repeated_component_signature=False`:
- `first["mode"] == RT_DBSCAN_DIRECT_STATUS_APP_MODE` ✓
- `first["partner"] == "cupy"` ✓
- `first["partition_cell_factor"] == 0.25` ✓
- `first["tested_point_count"] == 262144` ✓
- `first["one_shot_total_speedup_vs_current"] > 2.9` (actual: 2.939x) ✓
- `"Goal4130" in first["evidence_refs"]` ✓
- `"one-shot" in first["when"]` ✓
- All three automatic-selection flags `False` ✓

---

## Question 6 — Is it correct that `plan_rt_dbscan_execution` remains a separate older planning surface and is not silently changed into an auto-dispatcher?

**Yes, confirmed.**

`plan_rt_dbscan_execution` (app lines 77–103) is unchanged. It routes `ngsim_dense` to `"partner_cupy_prepared_grid_components_3d"` based on Goal2425 evidence, routes `road3d` and `clustered3d` per scale-based conditions from the same evidence, and returns a packet with `"not_hidden_dispatcher": True`, `"release_claim_authorized": False`. It does not call `explain_rt_dbscan_explicit_route_choice` and does not reference Goal4130 evidence.

The two functions serve different surfaces: `plan_rt_dbscan_execution` is an older one-shot planning function used by the `"planned_rt_dbscan"` benchmark mode (app lines 1111–1145); `explain_rt_dbscan_explicit_route_choice` is the advisory-only route explainer introduced in Goal4121. They are structurally independent and not in conflict. ✓

---

## Question 7 — Are all claim boundaries intact?

**Yes. All prohibited claims are `False` throughout all surfaces.**

| Claim | JSON pods | Advisor packet | Registry row | Structural guard |
|---|---|---|---|---|
| Release authorized | `false` top-level, per-profile, per-factor-row | `False` | `False` via `__post_init__` | `validate_current_benchmark_route_decisions()` returns `accept`, `errors == ()` ✓ |
| Public speedup claim | `false` everywhere | `False` | `False` | ✓ |
| Broad RT-core claim | `rt_core_speedup_claim_authorized: false` | `broad_rt_core_claim_authorized: False` | `broad_rt_core_claim_authorized: False` | ✓ |
| Whole-app speedup | `whole_app_speedup_claim_authorized: false` | `False` | `False` | ✓ |
| Paper reproduction | not in pod schema | not in advisor | `paper_reproduction_claim_authorized: False` | ✓ |
| True zero-copy | `true_zero_copy_claim_authorized: false` | `true_zero_copy_claim_authorized: False` | `true_zero_copy_claim_authorized: False` | ✓ |
| Hidden dispatch | not applicable | `hidden_dispatch_allowed: False` | — | ✓ |
| Automatic partner selection | `automatic_partner_selection_authorized: false` | `False` | `False` | ✓ |
| Automatic factor selection | `automatic_partner_selection_authorized: false` | `automatic_partition_cell_factor_selection_authorized: False` | listed in `rejected_or_unpromoted_candidates` | ✓ |
| Native ABI added | `native_abi_added: false` | `native_dbscan_abi_added: False` | `app_specific_native_engine_logic_allowed: False` | ✓ |
| App-specific engine logic | `app_specific_engine_logic_allowed: false` | `app_specific_engine_logic_allowed: False` | `app_specific_native_engine_logic_allowed: False` | ✓ |
| AMD performance claim | not in pod schema | not in advisor | `amd_performance_claim_authorized: False` | ✓ |
| Automatic one-shot route promotion | — | — | explicitly listed in `rejected_or_unpromoted_candidates` | ✓ |

The `CURRENT_BENCHMARK_ROUTE_DECISION_VERSION` is now `"rtdl.v2_10.current_benchmark_route_decisions.goal4131.v1"`, correctly advancing from the Goal4127 version. The `CURRENT_BENCHMARK_ROUTE_DECISION_CLAIM_BOUNDARY` string now enumerates "a warmed one-shot route probe" in the evidence chain. ✓

---

## Question 8 — Are there correctness, determinism, scale-sensitivity, app-agnostic, or performance-risk issues that should block the next RT-DBSCAN engineering step?

**No blocking issues found.** Four non-blocking observations follow.

### Non-blocking: 65k ngsim_dense factor asymmetry between one-shot and replay guidance

At 65k, the `ngsim_dense` best-replay factor is 0.5 (replay speedup 1.364x), giving a one-shot total speedup of 1.819x. However, factor 0.25 gives a substantially better one-shot amortized speedup of 3.679x (from `best_amortized_over_current_speedup = 3.679` in the JSON), while losing on repeated replay (0.969x < 1.0). The report correctly uses the best-replay factor for both the replay and one-shot claims, which is a conservative and internally consistent choice. However, a user primarily interested in one-shot performance at 65k ngsim_dense would be better served by factor 0.25 than factor 0.5. This trade-off is visible in the JSON but not made explicit in the report or advisory guidance text. It should be flagged for future guidance wording when the factor recommendation table is extended to distinguish replay-optimized vs. one-shot-optimized selections.

### Non-blocking: road3d one-shot speedup declines at 262k relative to prior scales

Road3d one-shot total speedups: 65k 2.609x → 131k 2.606x → 262k 2.272x. The 262k decline is more pronounced than in the replay-only series (1.866x → 1.545x → 1.428x replay), where the decline was monotonic across all three scales. Both trend lines suggest that road3d's advantage over the current route is eroding at larger scales. At 2.272x the 262k case is still strongly positive, but road3d should be an explicit priority when a 524k probe is added.

### Non-blocking: Tie-break semantics (carry-forward from Goal4124/Goal4125/Goal4128/Goal4129 reviews)

The advisor sorts by `abs(tested_point_count - resolved_point_count)`. With the current three-point spacing (65k, 131k, 262k), no equidistant query is possible within the tested range. A fourth evidence point at the geometric mean of two adjacent entries could create a tie that resolves by insertion order. This is a latent determinism gap — low priority now but should be addressed before the evidence table grows beyond four entries.

### Non-blocking: `plan_rt_dbscan_execution` remains on Goal2425 evidence

This one-shot planning function still routes `ngsim_dense` to `"partner_cupy_prepared_grid_components_3d"` based on Goal2425 evidence, not the direct-status guidance. This is structurally intentional: the two functions serve different surfaces. This observation is included only to confirm the separation remains intact, not to request a change.

---

## Summary

| Goal | Finding |
|---|---|
| 4130 runner reuse | Confirmed: schema `rtdl.goal4117.partition_cell_factor_route_sweep.v1`, `repeat=2`, `warmup=1`, commit `f9f1b82b`, clean worktree. |
| 4130 one-shot calculation | Correct: `current_prepare + current_replay` vs. `best_replay_factor_prepare + best_replay_factor_replay`. Consistent with JSON `amortized_sec` convention. |
| 4130 speedup values | All nine values (`2.506x`, `2.609x`, `1.819x`, `3.110x`, `2.606x`, `3.410x`, `3.192x`, `2.272x`, `2.939x`) verified exactly against JSON raw fields and arithmetic cross-checks. |
| 4130 signature preservation | `same_signature: true` and `all_factors_match_current_signature: true` on all 18 factor-profile rows across all three scales. |
| 4131 advisor update | `one_shot_total_speedup_vs_current` field added; `when` field distinguishes one-shot vs. repeated; all advisory flags intact; no dispatch surface added. |
| 4131 route registry | Version advanced to `goal4131.v1`; `rejected_or_unpromoted_candidates` extended with automatic one-shot promotion; `validate_current_benchmark_route_decisions()` returns `accept` with `errors == ()`. |
| `plan_rt_dbscan_execution` separation | Confirmed: structurally unchanged, separate surface, Goal2425 evidence only. |
| Claim boundaries | All prohibited flags are `False` across JSON pods, advisor packet, and registry. Structural `__post_init__` guard and validator both pass. |

**Verdict: `accept-with-boundary`**

Goals 4130–4131 form a clean extension of the Goal4117/Goal4122/Goal4126 evidence chain. The one-shot probe fairly reuses the Goal4117 runner with `repeat=2, warmup=1`, the three pods are commit-pinned to `f9f1b82b` with clean worktrees, and all nine one-shot total speedup values are exactly supported by the JSON artifacts. The advisor update exposes prepared direct-status as an explicit user-selectable option for both tested one-shot and repeated component-signature workloads without any hidden dispatch, automatic route selection, automatic partner selection, or automatic factor selection. The `plan_rt_dbscan_execution` surface remains structurally separate. All claim boundaries are intact across JSON pods, advisor packet, and registry, with structural enforcement via `__post_init__` and the validator returning `accept` with zero errors.

This review does not authorize release, public speedup wording, broad RT-core wording, whole-app benchmark claims, paper-reproduction claims, hidden dispatch, automatic partner selection, automatic factor selection, native ABI additions, AMD performance claims, or true-zero-copy claims.
