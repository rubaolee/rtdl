# Independent Gemini Review — Goals 4126–4127: RT-DBSCAN 262k Scale Guidance

Date: 2026-06-09

Verdict: accept-with-boundary

## Purpose

This review evaluates Goal4126 (Tuned Direct-Status 262k Scale Probe) and Goal4127 (Current Route Decision After 262k Direct-Status Probe). The primary objectives are to confirm that the 262k probe fairly extends the Goal4117/Goal4122 evidence chain, that the speedup values are exactly supported by the pod artifact, that the route registry update remains advisory-only with no automatic behaviors, and that all claim boundaries are intact.

Prior context: Goal4117 factor-sweep, Goal4122 131k scale probe, Goal4124 Claude review and Goal4125 Gemini review of Goals 4121–4123.

---

## Questions Answered

### 1. Does Goal4126 fairly reuse the Goal4117 factor-sweep runner for the 262,144-point probe, and is the pod artifact cleanly commit-pinned?

**Answer: accept**

Goal4126 reuses the Goal4117 runner without modification. The artifact `goal4126_tuned_direct_status_262k_scale_probe_pod.json` carries `"schema": "rtdl.goal4117.partition_cell_factor_route_sweep.v1"`, which is the same schema used by the Goal4122 pod. The measurement protocol is consistent: `"repeat": 4`, `"warmup": 1`, `"partition_cell_factors": [0.25, 0.5]`. The probe extends the scale series from 65k → 131k → 262k without changing any runner parameters.

The artifact is commit-pinned to `"source_commit": "5ddd50cd1ebfecbffbe078af696bd1544ab78b36"` with `"source_tracked_worktree_dirty": false`. The test `test_artifact_is_clean_commit_pinned_and_non_authorizing` verifies the commit prefix `5ddd50cd`, the clean-worktree flag, and `point_count == 262144`. The schema field is also verified. All nine authorization flags (`release_authorized`, `public_speedup_claim_authorized`, `rt_core_speedup_claim_authorized`, `automatic_partner_selection_authorized`, `native_abi_added`, `app_specific_engine_logic_allowed`, `partition_convergence_hybrid_promoted`, `true_zero_copy_claim_authorized`, `whole_app_speedup_claim_authorized`) are verified as `false`. ✓

---

### 2. Are the reported 262k results exactly supported by the JSON artifact?

**Answer: accept**

All three reported speedup values are verified against the raw JSON fields:

- `clustered3d`: reported factor `0.25`, speedup `3.118x`. JSON: `best_replay_partition_cell_factor: 0.25`, `best_replay_over_current_speedup: 3.118326850231395`. Report rounds to `3.118x`. Cross-check: `current_route_replay_sec (1.2654860615730286) / replay_sec (0.40582213550806046) = 3.118x`. ✓
- `road3d`: reported factor `0.25`, speedup `1.428x`. JSON: `best_replay_partition_cell_factor: 0.25`, `best_replay_over_current_speedup: 1.4283644989770918`. Report rounds to `1.428x`. Cross-check: `0.471896156668663 / 0.33037516474723816 = 1.428x`. ✓
- `ngsim_dense`: reported factor `0.25`, speedup `1.642x`. JSON: `best_replay_partition_cell_factor: 0.25`, `best_replay_over_current_speedup: 1.6424382994393592`. Report rounds to `1.642x`. Cross-check: `0.1563163697719574 / 0.09517335891723633 = 1.642x`. ✓

The factor-detail table in the report is also verified: partition counts (5652, 1117, 5122, 1015, 43742, 6526) and max_neighbor_offset values (5 for factor 0.25, 3 for factor 0.5) match the JSON exactly across all six factor-profile combinations.

The test `test_report_documents_262k_boundary` confirms all three speedup strings appear in the report text. The test `test_tuned_direct_status_wins_all_262k_profiles` asserts factor 0.25 is best for all three profiles and checks conservative lower bounds (`> 3.0`, `> 1.4`, `> 1.6`) that are satisfied by the measured values. ✓

---

### 3. Do all factor rows preserve the current grouped-stream route's component-size signature?

**Answer: accept**

Every factor row in the JSON artifact carries `"same_signature": true`, and the per-profile top-level field `"all_factors_match_current_signature": true` is present for all three profiles (`clustered3d`, `road3d`, `ngsim_dense`). This covers both the `0.25` and `0.5` factor rows at 262k scale.

The test `test_tuned_direct_status_wins_all_262k_profiles` asserts `assertTrue(row["all_factors_match_current_signature"])` for every row. ✓

This confirms the prepared direct-status route satisfies the repeated-component-signature contract at 262k scale, with no correctness regressions observed for either tested factor.

---

### 4. Does Goal4127 update the advisor and current route registry in an advisory-only way, without hidden dispatch, automatic partner selection, or automatic factor selection?

**Answer: accept**

The `explain_rt_dbscan_explicit_route_choice` function (benchmark app lines 106–183) returns a packet explicitly marked as advisory. Key fields:
- `"status": "advisory_only_no_dispatch"` ✓
- `"user_must_select_route": True` ✓
- `"automatic_dispatch_authorized": False` ✓
- `"automatic_partner_selection_authorized": False` ✓
- `"automatic_partition_cell_factor_selection_authorized": False` ✓
- `"hidden_dispatch_allowed": False` ✓

The function does not call `run_rt_dbscan_benchmark` or any route executor. The 262k entry is added to the informational sorted options tuple, not to any dispatch table. Sorting by `abs(tested_point_count - resolved_point_count)` ranks the most scale-relevant evidence first, without selecting or executing anything.

`CurrentBenchmarkRouteDecision.__post_init__` (lines 87–99 of `current_benchmark_route_decisions.py`) enforces all nine authorization flags as `False` and `user_explicit_choice_required` as `True` at object-construction time, making it structurally impossible to serialize a registry entry with any prohibited flag set.

The test `test_advisor_ranks_nearest_262k_scale_first` verifies:
- `first["partition_cell_factor"] == 0.25` and `first["tested_point_count"] == 262144` ✓
- `"Goal4126" in first["evidence_refs"]` ✓
- `second["tested_point_count"] == 131072` ✓
- `automatic_partition_cell_factor_selection_authorized == False` ✓
- `automatic_dispatch_authorized == False` ✓

The test `test_route_registry_records_262k_scale_evidence` confirms `version == "rtdl.v2_10.current_benchmark_route_decisions.goal4127.v1"`, `decision_kind == "mixed_explicit"`, `partner_policy == "mixed_explicit_user_choice"`, and that all three 262k speedup strings plus `"131k/262k"` appear in the text fields. ✓

---

### 5. Does the new guidance avoid claiming a universal dense-profile factor, while correctly stating that `ngsim_dense` used `0.5` at 65k and `0.25` at 131k/262k?

**Answer: accept**

The `RT_DBSCAN_TESTED_DIRECT_STATUS_PARTITION_CELL_FACTOR_OPTIONS["ngsim_dense"]` entry (benchmark app lines 44–48) now records three scale points:
- 65k: factor `0.5`, speedup `1.312x`, evidence `Goal4117`
- 131k: factor `0.25`, speedup `1.399x`, evidence `Goal4122`
- 262k: factor `0.25`, speedup `1.642x`, evidence `Goal4126`

The `user_choice_guidance` field in the route registry explicitly states: `"For dense NGSIM-like profiles, use the route advisor or scale-specific evidence: 0.5 at 65k and 0.25 at 131k/262k. Do not auto-select the factor."` This correctly captures the factor flip and avoids any universal factor claim.

The Goal4126 report states: "Dense NGSIM-like profiles are not globally tied to one factor: `0.5` was best at 65k, but `0.25` wins at 131k and 262k." The test `test_half_cell_factor_is_not_a_universal_dense_default` confirms factor `0.5` at 262k is below 1.0x speedup (`0.833x`), while factor `0.25` exceeds `1.6x`. The report fragment test verifies the strings `` "`0.5` was best at 65k" `` and `` "`0.25` wins at 131k and 262k" `` appear in the report. ✓

No claim is made that `0.25` will remain optimal at all future scales for dense profiles.

---

### 6. Are all claim boundaries intact: no release, public speedup, broad RT-core, whole-app, paper reproduction, true-zero-copy, hidden dispatch, automatic partner selection, automatic factor selection, native ABI, app-specific engine logic, or AMD performance claims?

**Answer: accept**

All claim boundaries are intact and consistently enforced across all surfaces.

In the JSON artifact: `release_authorized`, `public_speedup_claim_authorized`, `rt_core_speedup_claim_authorized`, `automatic_partner_selection_authorized`, `native_abi_added`, `app_specific_engine_logic_allowed`, `partition_convergence_hybrid_promoted`, `true_zero_copy_claim_authorized`, and `whole_app_speedup_claim_authorized` are all `false` at the top level and in every per-profile and per-factor-row entry.

In the advisor packet: `release_authorized`, `public_speedup_claim_authorized`, `broad_rt_core_claim_authorized`, `whole_app_speedup_claim_authorized`, `true_zero_copy_claim_authorized`, `native_dbscan_abi_added`, `app_specific_engine_logic_allowed`, `automatic_dispatch_authorized`, `automatic_partner_selection_authorized`, `automatic_partition_cell_factor_selection_authorized`, and `hidden_dispatch_allowed` are all `False`.

In the route registry: the `CurrentBenchmarkRouteDecision` dataclass enforces all nine authorization flags at construction time. The `validate_current_benchmark_route_decisions()` function returns `status="accept"` with `errors == ()` (verified in `test_registry_summary_and_report_stay_non_authorizing`). The `CURRENT_BENCHMARK_ROUTE_DECISION_CLAIM_BOUNDARY` string explicitly enumerates all prohibited claims.

The `rejected_or_unpromoted_candidates` tuple for `rt_dbscan` continues to list "automatic partition-cell-factor tuning after Goal4117 explicit factor sweep." ✓

---

### 7. Are there correctness, determinism, scale-sensitivity, app-agnostic, or performance-risk issues that should block the next RT-DBSCAN engineering step?

**Answer: accept**

No blocking issues were identified. The following non-blocking observations are noted for the engineering record.

**Non-blocking: `ngsim_dense` factor 0.5 is below 1.0x at 262k.** The JSON records `replay_over_current_speedup: 0.833x` for `ngsim_dense` factor `0.5` at 262k — slower than the current route while still signature-matching. The guidance already excludes this factor from the top recommendation at 262k. This data point confirms the factor-performance relationship is genuinely scale-sensitive for dense profiles, not just noisy variance.

**Non-blocking: `road3d` replay speedup declines monotonically across scales.** 65k: `1.866x`. 131k: `1.545x`. 262k: `1.428x`. In contrast, `clustered3d` improved (2.961x → 3.211x → 3.118x, stable-to-improving) and `ngsim_dense` improved from 131k to 262k (1.399x → 1.642x). The `road3d` decline is modest and the profile remains clearly positive at 1.428x. However, road3d should be an explicit priority in the next larger-scale packet to determine whether the trend continues.

**Non-blocking: Tie-break semantics for equidistant queries (carry-forward from Goal4124/Goal4125 reviews).** The advisor sorts by `abs(tested_point_count - resolved_point_count)`. With the current three-point spacing (65k, 131k, 262k) no equidistant query exists within the tested range. Adding a fourth evidence point at certain scales could create a tie that resolves by insertion order. This should be addressed before the evidence table grows beyond four entries.

**Non-blocking: `plan_rt_dbscan_execution` remains on Goal2425 evidence.** This one-shot planning function routes `ngsim_dense` to `partner_cupy_prepared_grid_components_3d` regardless of the new direct-status guidance. It serves a different planning surface (one-shot default plan) than the `explain_rt_dbscan_explicit_route_choice` advisor (repeated component-signature advisory). The two functions are structurally separate and not in conflict. No change is required.

---

## Summary

| Goal | Finding |
|---|---|
| 4126 runner reuse | Confirmed: same schema `rtdl.goal4117.partition_cell_factor_route_sweep.v1`, same protocol (repeat 4, warmup 1). Commit-pinned to `5ddd50cd`, clean worktree. |
| 4126 speedup values | All three values (`3.118x`, `1.428x`, `1.642x`) verified exactly against JSON raw fields and arithmetic cross-checks. |
| 4126 factor table | All six factor-profile rows verified. Partition counts and max-neighbor-offset match. |
| 4126 signature preservation | `same_signature: true` and `all_factors_match_current_signature: true` on all rows. ✓ |
| 4127 advisory enforcement | No dispatch, no automatic selection, no hidden path. Structural `__post_init__` guard. Validation returns `accept` with zero errors. |
| 4127 ngsim scale history | Correctly states `0.5` at 65k and `0.25` at 131k/262k. No universal factor claim. |
| Claim boundaries | All prohibited flags are `False` across JSON, advisor, and registry. Structural enforcement intact. |

**Verdict: accept-with-boundary**

Goals 4126–4127 cleanly extend the 131k scale chain. The 262k probe fairly reuses the Goal4117 runner, the artifact is commit-pinned to a clean worktree, and all speedup values are exactly supported by the JSON artifact. The advisor and registry update is advisory-only with no dispatch surface, and the structural `__post_init__` guard enforces all claim boundaries at construction time. The scale-aware ngsim_dense guidance is correctly stated without any universal-factor claim. The four non-blocking observations (ngsim 0.5 sub-parity at 262k, road3d declining trend, tie-break semantics, plan_rt_dbscan_execution surface separation) are manageable by the stated next action of broader profile coverage and a larger-scale packet.

This review does not authorize release, public speedup wording, broad RT-core wording, whole-app benchmark claims, paper-reproduction claims, hidden dispatch, automatic partner selection, automatic factor selection, native ABI additions, AMD performance claims, or true-zero-copy claims.
