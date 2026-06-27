# Independent Gemini Review — Goals 4130–4131: RT-DBSCAN Warmed One-Shot Guidance

Date: 2026-06-09

Verdict: accept-with-boundary

## Purpose

This review evaluates Goal4130 (Tuned Direct-Status Warmed One-Shot Probe) and Goal4131 (Current Route Decision After Warmed One-Shot Probe). The primary objectives are to confirm that the one-shot probe fairly reuses the Goal4117 runner, that the one-shot total calculation is correctly specified and arithmetically exact against the raw JSON fields, that all nine speedup values are exactly supported by the pod artifacts, that all factor rows preserve the component-size signature, that the advisor update is advisory-only with no automatic behaviors, and that all claim boundaries are intact.

Prior context: Goal4117 factor-sweep runner, Goal4122 131k probe, Goal4126 262k probe, Goal4128 Claude review and Goal4129 Gemini review of Goals 4126–4127.

---

## Questions Answered

### 1. Does Goal4130 fairly reuse the Goal4117 factor-sweep runner for a warmed one-shot probe (`repeat=2`, `warmup=1`), and are the artifacts cleanly commit-pinned to `f9f1b82b` with dirty flag false?

**Answer: accept**

All three artifacts (`goal4130_tuned_direct_status_warm_one_shot_65k_pod.json`, `131k_pod.json`, `262k_pod.json`) carry `"schema": "rtdl.goal4117.partition_cell_factor_route_sweep.v1"`, the same schema used by the Goal4117, Goal4122, and Goal4126 pods. All three are commit-pinned to `"source_commit": "f9f1b82b022c2f2631aa4f5b70805660880debfd"` with `"source_tracked_worktree_dirty": false`. The `"goal": "Goal4117"` field is a schema-provenance identifier, not a measurement-goal label.

The probe uses `"repeat": 2, "warmup": 1`, in contrast to the prior sweep pods (`repeat: 4, warmup: 1`). This is the correct parameterization for a warmed one-shot probe: one warmup run is discarded, and one measured run provides both the replay timing and the single-replay cost against which prepare is charged. The tested factors remain `[0.25, 0.5]`.

The test `test_artifacts_are_clean_commit_pinned_and_non_authorizing` verifies the schema, commit prefix `f9f1b82b`, clean-worktree flag, correct `point_count` per scale, `repeat == 2`, `warmup == 1`, and all authorization flags as `false` for each of the three artifacts. ✓

---

### 2. Does the one-shot total calculation make sense for the stated boundary: `current_route_prepare_sec + current_route_replay_sec` versus `direct_status_prepare_sec + direct_status_replay_sec`?

**Answer: accept**

The one-shot total speedup calculation is:

```
one_shot_speedup = (current_route_prepare_sec + current_route_replay_sec)
                 / (best_replay_factor_prepare_sec + best_replay_factor_replay_sec)
```

This charges the current route's full prepare-plus-one-replay cost against the prepared direct-status route's full prepare-plus-one-replay cost, where the direct-status factor is the one with the best repeated-replay speedup. The methodology is conservative and internally consistent: the factor recommended for repeated use is evaluated on its one-shot cost as well, not selected post-hoc to maximize the one-shot claim.

The JSON's `current_route_amortized_sec` field equals `current_route_prepare_sec + current_route_replay_sec` exactly (e.g., 65k clustered3d: `1.098135` = `1.003352 + 0.094783`). The factor-row `amortized_sec` field equals `prepare_sec + replay_sec` (e.g., 65k clustered3d factor 0.25: `0.438231` = `0.406338 + 0.031893`). The one-shot total speedup in the report corresponds exactly to the JSON `amortized_over_current_speedup` field for the best-replay-factor row.

The `_one_shot_speedup` helper in the test file implements this calculation correctly. The boundary is clearly stated: the one-shot win does not make the route automatic, does not select a factor automatically, and does not claim a whole-app speedup. ✓

---

### 3. Are the reported one-shot total speedups exactly supported by the JSON artifacts?

**Answer: accept**

All nine reported speedup values are verified against the JSON raw fields and arithmetic cross-checks:

**65k pod:**
- `clustered3d`: factor `0.25`. `(1.003352 + 0.094783) / (0.406338 + 0.031893) = 1.098135 / 0.438231 = 2.5058x`. JSON `amortized_over_current_speedup`: `2.505839`. Report: `2.506x`. ✓
- `road3d`: factor `0.25`. `(0.125383 + 0.038714) / (0.041759 + 0.021128) = 0.164097 / 0.062887 = 2.6094x`. JSON: `2.609400`. Report: `2.609x`. ✓
- `ngsim_dense`: factor `0.5` (best replay). `(0.208602 + 0.015835) / (0.111794 + 0.011608) = 0.224437 / 0.123402 = 1.8187x`. JSON: `1.818747`. Report: `1.819x`. ✓

**131k pod:**
- `clustered3d`: factor `0.25`. `(1.275888 + 0.345484) / (0.412559 + 0.108817) = 1.621372 / 0.521375 = 3.1098x`. JSON: `3.109800`. Report: `3.110x`. ✓
- `road3d`: factor `0.25`. `(0.330194 + 0.129121) / (0.092838 + 0.083442) = 0.459315 / 0.176280 = 2.6056x`. JSON: `2.605599`. Report: `2.606x`. ✓
- `ngsim_dense`: factor `0.25`. `(0.433236 + 0.047351) / (0.104727 + 0.036208) = 0.480587 / 0.140934 = 3.4100x`. JSON: `3.410003`. Report: `3.410x`. ✓

**262k pod:**
- `clustered3d`: factor `0.25`. `(1.681726 + 1.262912) / (0.511874 + 0.410653) = 2.944638 / 0.922526 = 3.1919x`. JSON: `3.191929`. Report: `3.192x`. ✓
- `road3d`: factor `0.25`. `(0.701955 + 0.471716) / (0.188074 + 0.328591) = 1.173671 / 0.516665 = 2.2716x`. JSON: `2.271629`. Report: `2.272x`. ✓
- `ngsim_dense`: factor `0.25`. `(0.799718 + 0.155041) / (0.229675 + 0.095144) = 0.954759 / 0.324819 = 2.9394x`. JSON: `2.939360`. Report: `2.939x`. ✓

The test `test_warmed_one_shot_total_wins_all_profiles_and_scales` asserts conservative lower bounds that are all satisfied. The test `test_report_documents_warmed_one_shot_boundary` confirms `"1.819x"` and `"3.410x"` appear in the report text. ✓

---

### 4. Do all factor rows preserve the current grouped-stream route's component-size signature?

**Answer: accept**

Every factor row across all three scales and all three profiles carries `"same_signature": true`, and the per-profile `"all_factors_match_current_signature": true` is present for all 18 factor-profile combinations. This includes both factor 0.25 and factor 0.5 rows at all three scales, including sub-parity rows (65k ngsim_dense factor 0.25 at 0.969x replay, 131k road3d factor 0.5 at 0.316x replay, 262k road3d factor 0.5 at 0.281x replay, 262k ngsim_dense factor 0.5 at 0.827x replay).

The test `test_warmed_one_shot_total_wins_all_profiles_and_scales` asserts `assertTrue(row["all_factors_match_current_signature"])` for every profile at every scale. ✓

Correctness and performance are confirmed independent: sub-parity factor rows are slower than the current route while still satisfying the component-size signature contract.

---

### 5. Does Goal4131 update the route advisor to expose prepared direct-status as an explicit user-selectable option for tested one-shot and repeated component-signature workloads without hidden dispatch, automatic route selection, automatic partner selection, or automatic factor selection?

**Answer: accept**

`explain_rt_dbscan_explicit_route_choice` (benchmark app lines 106–188) now includes `"one_shot_total_speedup_vs_current"` in each direct-status option entry, sourced from the `"one_shot_total_speedup"` field in `RT_DBSCAN_TESTED_DIRECT_STATUS_PARTITION_CELL_FACTOR_OPTIONS`. The `"when"` field distinguishes the one-shot case (`repeated_component_signature=False`) from the repeated case. All advisory enforcement flags remain:

- `"status": "advisory_only_no_dispatch"` ✓
- `"user_must_select_route": True` ✓
- `"automatic_dispatch_authorized": False` ✓
- `"automatic_partner_selection_authorized": False` ✓
- `"automatic_partition_cell_factor_selection_authorized": False` ✓
- `"hidden_dispatch_allowed": False` ✓

The function does not call `run_rt_dbscan_benchmark` or any route executor. The sorting of `tested_options` by nearest scale is purely informational.

`CurrentBenchmarkRouteDecision.__post_init__` (lines 87–99 of `current_benchmark_route_decisions.py`) enforces all nine authorization flags as `False` and `user_explicit_choice_required` as `True` at object-construction time, making it structurally impossible to serialize a registry entry with any prohibited flag set.

The test `test_advisor_exposes_one_shot_direct_status_without_dispatch` verifies that for `ngsim_dense`, `point_count=262144`, `repeated_component_signature=False`:
- `first["mode"] == RT_DBSCAN_DIRECT_STATUS_APP_MODE` ✓
- `first["partner"] == "cupy"` ✓
- `first["partition_cell_factor"] == 0.25` ✓
- `first["tested_point_count"] == 262144` ✓
- `first["one_shot_total_speedup_vs_current"] > 2.9` (actual 2.939x) ✓
- `"Goal4130" in first["evidence_refs"]` ✓
- `"one-shot" in first["when"]` ✓
- All three automatic-selection flags `False` ✓

The test `test_route_registry_records_one_shot_evidence_without_auto_promotion` confirms version `"goal4131.v1"`, `decision_kind == "mixed_explicit"`, `partner_policy == "mixed_explicit_user_choice"`, that `"Goal4130"`, `"one-shot"`, `"1.819x"`, `"3.410x"`, and `"Do not auto-select"` appear in text fields, and that `"automatic one-shot route promotion"` is present in `rejected_or_unpromoted_candidates`. ✓

---

### 6. Is it correct that `plan_rt_dbscan_execution` remains a separate older planning surface and is not silently changed into an auto-dispatcher?

**Answer: accept**

`plan_rt_dbscan_execution` (benchmark app lines 77–103) is unchanged. It routes by dataset and scale using Goal2425 evidence and returns a packet with `"not_hidden_dispatcher": True`, `"release_claim_authorized": False`, `"paper_reproduction_claim_authorized": False`. It does not reference Goal4130, `RT_DBSCAN_TESTED_DIRECT_STATUS_PARTITION_CELL_FACTOR_OPTIONS`, or `explain_rt_dbscan_explicit_route_choice`.

The two planning surfaces are structurally independent:
- `plan_rt_dbscan_execution`: older one-shot planning function; routes `ngsim_dense` to `partner_cupy_prepared_grid_components_3d` based on Goal2425; used by the `"planned_rt_dbscan"` benchmark CLI mode.
- `explain_rt_dbscan_explicit_route_choice`: advisory-only route explainer from Goal4121; returns an options tuple without executing anything.

Neither function is a hidden dispatcher, and their structural separation is intact. ✓

---

### 7. Are all claim boundaries intact: no release, public speedup, broad RT-core, whole-app, paper reproduction, true-zero-copy, hidden dispatch, automatic partner selection, automatic factor selection, native ABI, app-specific engine logic, or AMD performance claims?

**Answer: accept**

All prohibited claim flags are `False` across all surfaces.

In all three JSON pods: `release_authorized`, `public_speedup_claim_authorized`, `rt_core_speedup_claim_authorized`, `whole_app_speedup_claim_authorized`, `automatic_partner_selection_authorized`, `native_abi_added`, `app_specific_engine_logic_allowed`, `partition_convergence_hybrid_promoted`, and `true_zero_copy_claim_authorized` are `false` at the top level and in every per-profile and per-factor-row entry.

In the advisor packet: `release_authorized`, `public_speedup_claim_authorized`, `broad_rt_core_claim_authorized`, `whole_app_speedup_claim_authorized`, `true_zero_copy_claim_authorized`, `native_dbscan_abi_added`, `app_specific_engine_logic_allowed`, `automatic_dispatch_authorized`, `automatic_partner_selection_authorized`, `automatic_partition_cell_factor_selection_authorized`, and `hidden_dispatch_allowed` are all `False`.

In the route registry: the `CurrentBenchmarkRouteDecision` dataclass enforces all nine authorization flags at construction time. `validate_current_benchmark_route_decisions()` returns `status="accept"` with `errors == ()` (verified in `test_registry_summary_and_report_stay_non_authorizing`). The `CURRENT_BENCHMARK_ROUTE_DECISION_CLAIM_BOUNDARY` string enumerates "a warmed one-shot route probe" in the evidence chain and lists all prohibited actions. The `rt_dbscan` registry entry explicitly lists `"automatic one-shot route promotion after Goal4130 warmed one-shot evidence"` in `rejected_or_unpromoted_candidates`. ✓

---

### 8. Are there correctness, determinism, scale-sensitivity, app-agnostic, or performance-risk issues that should block the next RT-DBSCAN engineering step?

**Answer: accept — no blocking issues identified.**

The following non-blocking observations are noted for the engineering record.

**Non-blocking: 65k ngsim_dense factor asymmetry between one-shot and replay guidance.** At 65k, `ngsim_dense` factor 0.5 is the best-replay choice (1.364x replay) and gives 1.819x one-shot total speedup. However, factor 0.25 gives 3.679x one-shot amortized speedup (`best_amortized_over_current_speedup = 3.679` in the JSON) while losing on repeated replay (0.969x). The report correctly uses the best-replay factor for both replay and one-shot claims, which is conservative and internally consistent. A user whose primary workload is genuinely one-shot at 65k ngsim_dense would benefit from knowing factor 0.25 is available and faster for that use case. This trade-off is visible in the JSON but not surfaced in the advisory guidance text. It should be addressed before the guidance is used at 65k ngsim_dense scale.

**Non-blocking: road3d one-shot total speedup declines at 262k.** One-shot total speedups for road3d: 65k 2.609x → 131k 2.606x → 262k 2.272x. Both the one-shot and replay series are monotonically declining for road3d. At 2.272x the 262k case is still strongly positive, but road3d should be an explicit priority in any next larger-scale packet.

**Non-blocking: Tie-break semantics for equidistant queries (carry-forward from Goal4124/Goal4125/Goal4128/Goal4129 reviews).** The advisor sorts by `abs(tested_point_count - resolved_point_count)`. With the current three-point spacing (65k, 131k, 262k), no equidistant query exists within the tested range. A fourth evidence point at certain scales could create a tie that resolves by insertion order. This should be addressed before the evidence table grows beyond four entries.

**Non-blocking: `plan_rt_dbscan_execution` remains on Goal2425 evidence.** Confirmed unchanged. This one-shot planning function does not reflect the Goal4130 one-shot evidence. The two surfaces are structurally separate, so no fix is required, but the divergence should be noted if future guidance consolidation is attempted.

---

## Summary

| Goal | Finding |
|---|---|
| 4130 runner reuse | Confirmed: schema `rtdl.goal4117.partition_cell_factor_route_sweep.v1`, `repeat=2`, `warmup=1`, commit `f9f1b82b`, clean worktree, all three scale pods. |
| 4130 one-shot calculation | Correct: `current_prepare + current_replay` vs. `best_replay_factor_prepare + best_replay_factor_replay`. Consistent with JSON `amortized_sec` convention. |
| 4130 speedup values | All nine values (`2.506x`, `2.609x`, `1.819x`, `3.110x`, `2.606x`, `3.410x`, `3.192x`, `2.272x`, `2.939x`) verified exactly against JSON raw fields and arithmetic cross-checks. |
| 4130 signature preservation | `same_signature: true` and `all_factors_match_current_signature: true` on all 18 factor-profile rows across all three scales, including sub-parity rows. |
| 4131 advisor update | `one_shot_total_speedup_vs_current` field added; `when` field distinguishes one-shot vs. repeated; all advisory enforcement flags intact; no dispatch surface added. |
| 4131 route registry | Version advanced to `goal4131.v1`; `rejected_or_unpromoted_candidates` extended with automatic one-shot promotion; `validate_current_benchmark_route_decisions()` returns `accept`, `errors == ()`. |
| `plan_rt_dbscan_execution` separation | Confirmed unchanged; structurally separate from the advisor; Goal2425 evidence only. |
| Claim boundaries | All prohibited flags are `False` across all three JSON pods, advisor packet, and registry. Structural `__post_init__` guard and validator both pass. |

**Verdict: `accept-with-boundary`**

Goals 4130–4131 cleanly extend the Goal4117/Goal4122/Goal4126 replay-evidence chain into the one-shot prepare-charged domain. The one-shot probe fairly reuses the Goal4117 runner with `repeat=2, warmup=1`, the three pod artifacts are commit-pinned to `f9f1b82b` with clean worktrees, and all nine one-shot total speedup values are exactly supported by the JSON artifacts. The advisor and registry update exposes prepared direct-status as an explicit user-selectable option for both one-shot and repeated component-signature workloads without any hidden dispatch, automatic route selection, automatic partner selection, or automatic factor selection. The `plan_rt_dbscan_execution` surface remains structurally separate. All claim boundaries are intact across all surfaces, with structural enforcement via `__post_init__` and the validator returning `accept` with zero errors. The four non-blocking observations (65k ngsim_dense factor asymmetry, road3d declining one-shot trend, tie-break semantics, plan_rt_dbscan_execution divergence) are manageable by the stated next actions of prepare-cost reduction or broader profile coverage.

This review does not authorize release, public speedup wording, broad RT-core wording, whole-app benchmark claims, paper-reproduction claims, hidden dispatch, automatic partner selection, automatic factor selection, native ABI additions, AMD performance claims, or true-zero-copy claims.
