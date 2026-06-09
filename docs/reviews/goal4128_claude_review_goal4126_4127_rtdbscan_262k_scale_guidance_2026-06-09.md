# Claude Review — Goals 4126–4127: RT-DBSCAN 262k Scale Guidance

**Date:** 2026-06-09
**Reviewer:** Claude Sonnet 4.6 (external read-only review)
**Verdict:** `accept-with-boundary`

---

## Scope

- Goal4126: 262,144-point tuned direct-status scale probe, pod artifact, report, and test
- Goal4127: `current_benchmark_route_decisions.py` refresh to 262k-aware guidance, `explain_rt_dbscan_explicit_route_choice` update, report, and test

Prior context reviewed: Goal4117 factor-sweep report and pod, Goal4122 131k scale probe report, Goal4124 Claude review and Goal4125 Gemini review of Goals 4121–4123.

No source files were edited. No tests were run. All findings are based on reading source, test, artifact, and report files.

---

## Question 1 — Does Goal4126 fairly reuse the Goal4117 factor-sweep runner, and is the pod artifact cleanly commit-pinned?

**Yes on both counts.**

The JSON artifact carries `"schema": "rtdl.goal4117.partition_cell_factor_route_sweep.v1"`, which is the same schema used by the Goal4117 and Goal4122 pods. The measurement protocol is identical: `repeat: 4`, `warmup: 1`, factors `[0.25, 0.5]`. The artifact is commit-pinned to `5ddd50cd1ebfecbffbe078af696bd1544ab78b36` (`5ddd50cd` — the Goal4123 scale-aware-advisor-review commit that appears in the recent git log) with `source_tracked_worktree_dirty: false`.

The test `test_artifact_is_clean_commit_pinned_and_non_authorizing` verifies the commit prefix, clean-worktree flag, `point_count == 262144`, and all nine authorization flags set to `false`. ✓

The scale sequence (65k → 131k → 262k) is a clean halving/doubling series. No structural deviation from the Goal4117/Goal4122 runner protocol was observed.

---

## Question 2 — Are the reported 262k results exactly supported by the JSON artifact?

**Yes. All three speedup values verify exactly against the raw JSON fields.**

| Profile | Report states | JSON raw value | Cross-check arithmetic | Verified |
|---|---|---|---|---|
| `clustered3d` | factor `0.25`, `3.118x` | `best_replay_over_current_speedup: 3.118326850231395` | 1.265486 / 0.405822 = 3.118x | ✓ |
| `road3d` | factor `0.25`, `1.428x` | `best_replay_over_current_speedup: 1.4283644989770918` | 0.471896 / 0.330375 = 1.428x | ✓ |
| `ngsim_dense` | factor `0.25`, `1.642x` | `best_replay_over_current_speedup: 1.6424382994393592` | 0.156316 / 0.095173 = 1.642x | ✓ |

The factor-detail table in the report is also verified:

| Profile | Factor | Report replay (s) | JSON replay_sec | Report speedup | JSON speedup | Partitions | Max offset |
|---|---|---|---|---|---|---|---|
| `clustered3d` | 0.25 | 0.405822 | 0.40582213... | 3.118x | 3.118326... | 5652 | 5 |
| `clustered3d` | 0.5 | 1.511232 | 1.51123191... | 0.837x | 0.837387... | 1117 | 3 |
| `road3d` | 0.25 | 0.330375 | 0.33037516... | 1.428x | 1.428364... | 5122 | 5 |
| `road3d` | 0.5 | 1.619231 | 1.61923077... | 0.291x | 0.291432... | 1015 | 3 |
| `ngsim_dense` | 0.25 | 0.095173 | 0.09517335... | 1.642x | 1.642438... | 43742 | 5 |
| `ngsim_dense` | 0.5 | 0.187640 | 0.18764030... | 0.833x | 0.833063... | 6526 | 3 |

All values match to three significant figures. The test `test_report_documents_262k_boundary` checks for exact string fragments `"3.118x"`, `"1.428x"`, `"1.642x"` in the report text. ✓

---

## Question 3 — Do all factor rows preserve the current grouped-stream route's component-size signature?

**Yes. Every factor row for every profile reports `same_signature: true`, and the per-profile top-level field `all_factors_match_current_signature: true` is set for all three profiles.**

The test `test_tuned_direct_status_wins_all_262k_profiles` asserts `assertTrue(row["all_factors_match_current_signature"])` for every row in the artifact. ✓

This means the prepared direct-status route (factor 0.25 and factor 0.5) produces component-size outputs that agree with the current grouped-stream Numba route at 262k scale for all three profiles, satisfying the repeated-component-signature contract.

One detail worth noting: the `ngsim_dense` factor `0.5` row at 262k yields `replay_over_current_speedup: 0.833x` — i.e., it is slower than the current route — while still matching the signature. This is consistent with the interpretation that `0.5` is not viable at the 262k scale for dense profiles, reinforcing the scale-dependent factor guidance.

---

## Question 4 — Does Goal4127 update the advisor and current route registry in an advisory-only way, without hidden dispatch, automatic partner selection, or automatic factor selection?

**Yes, on every required dimension.**

`explain_rt_dbscan_explicit_route_choice` (app lines 106–183) returns a packet with:
- `status: "advisory_only_no_dispatch"` ✓
- `user_must_select_route: True` ✓
- `automatic_dispatch_authorized: False` ✓
- `automatic_partner_selection_authorized: False` ✓
- `automatic_partition_cell_factor_selection_authorized: False` ✓
- `hidden_dispatch_allowed: False` ✓

The function's only dispatch-adjacent action is sorting the options tuple by `abs(tested_point_count - resolved_point_count)`. This reordering is purely informational and does not call any route executor. The 262k entry for all three profiles now appears first in the tuple when `point_count=262144` is supplied.

`CurrentBenchmarkRouteDecision.__post_init__` (lines 87–99 of `current_benchmark_route_decisions.py`) raises `ValueError` at object-construction time if any of the nine authorization flags deviates from `False` or if `user_explicit_choice_required` deviates from `True`. This is a structural build-time guard that makes it impossible for the registry to be serialized with any prohibited flag set.

The test `test_advisor_ranks_nearest_262k_scale_first` confirms:
- `first["partition_cell_factor"] == 0.25` and `first["tested_point_count"] == 262144` ✓
- `"Goal4126" in first["evidence_refs"]` ✓
- `second["tested_point_count"] == 131072` ✓
- `automatic_partition_cell_factor_selection_authorized == False` ✓
- `automatic_dispatch_authorized == False` ✓

The route-registry test `test_route_registry_records_262k_scale_evidence` asserts the version is `goal4127.v1`, `decision_kind == "mixed_explicit"`, `partner_policy == "mixed_explicit_user_choice"`, and confirms `"Goal4126"`, `"3.118x"`, `"1.428x"`, `"1.642x"`, and `"131k/262k"` appear in the text fields. ✓

The `validate_current_benchmark_route_decisions()` path returns `status="accept"` with `errors == ()` (tested in `test_registry_summary_and_report_stay_non_authorizing`). ✓

---

## Question 5 — Does the new guidance avoid claiming a universal dense-profile factor, while correctly stating that `ngsim_dense` used `0.5` at 65k and `0.25` at 131k/262k?

**Yes. The claim is correctly scoped and the scale history is accurately stated.**

`RT_DBSCAN_TESTED_DIRECT_STATUS_PARTITION_CELL_FACTOR_OPTIONS` (app lines 33–48) now reads:

```python
"ngsim_dense": (
    {"point_count": 65536,  "factor": 0.5,  "replay_speedup": 1.312, "evidence_refs": ("Goal4117",)},
    {"point_count": 131072, "factor": 0.25, "replay_speedup": 1.399, "evidence_refs": ("Goal4122",)},
    {"point_count": 262144, "factor": 0.25, "replay_speedup": 1.642, "evidence_refs": ("Goal4126",)},
),
```

The `user_choice_guidance` field in `current_benchmark_route_decisions.py` (lines 228–231) states:
> "For dense NGSIM-like profiles, use the route advisor or scale-specific evidence: 0.5 at 65k and 0.25 at 131k/262k. Do not auto-select the factor."

This correctly records the factor flip (`0.5` → `0.25`) at 131k and confirms that `0.25` remains best at 262k. It does not claim `0.5` or `0.25` as a universal dense-profile default. The Goal4126 report also states directly: "Dense NGSIM-like profiles are not globally tied to one factor."

The test `test_half_cell_factor_is_not_a_universal_dense_default` checks:
- `ngsim[0.25]["replay_over_current_speedup"] > 1.6` ✓ (actual: 1.642x)
- `ngsim[0.5]["replay_over_current_speedup"] < 1.0` ✓ (actual: 0.833x)
- `ngsim[0.25] > ngsim[0.5]` ✓

The report fragment test `test_report_documents_262k_boundary` checks for `"0.5\` was best at 65k"` and `` "`0.25` wins at 131k and 262k" `` in the report text. ✓

---

## Question 6 — Are all claim boundaries intact?

**Yes. All prohibited claims are `False` throughout.**

| Claim | Status |
|---|---|
| Release authorized | `False` in JSON top-level, per-profile, per-factor-row, advisor packet, registry row ✓ |
| Public speedup claim | `False` everywhere ✓ |
| Broad RT-core claim | `rt_core_speedup_claim_authorized: false` in JSON; `broad_rt_core_claim_authorized: False` in registry ✓ |
| Whole-app speedup claim | `whole_app_speedup_claim_authorized: false` in JSON; `False` in registry ✓ |
| Paper reproduction claim | `False` in registry (`paper_reproduction_claim_authorized`) ✓ |
| True zero-copy claim | `true_zero_copy_claim_authorized: false` in advisor and registry ✓ |
| Hidden dispatch | `hidden_dispatch_allowed: False` in advisor packet ✓ |
| Automatic partner selection | `automatic_partner_selection_authorized: false` in all surfaces ✓ |
| Automatic factor selection | `automatic_partition_cell_factor_selection_authorized: False` in advisor; "automatic partition-cell-factor tuning" in `rejected_or_unpromoted_candidates` ✓ |
| Native ABI added | `native_abi_added: false` in JSON at top-level and per-factor-row ✓ |
| App-specific engine logic | `app_specific_engine_logic_allowed: false` in JSON; `app_specific_native_engine_logic_allowed: False` in registry ✓ |
| `partition_convergence_hybrid` promoted | `partition_convergence_hybrid_promoted: false` in JSON; listed in `rejected_or_unpromoted_candidates` ✓ |
| AMD performance claim | `amd_performance_claim_authorized: False` in registry ✓ |

The per-factor-row `claim_boundary` strings in the JSON are consistent with the top-level artifact boundary and the advisor packet. The `CURRENT_BENCHMARK_ROUTE_DECISION_CLAIM_BOUNDARY` string (lines 11–24 of `current_benchmark_route_decisions.py`) enumerates all prohibited claims, now extended with "131k plus 262k scale probes." ✓

---

## Question 7 — Are there correctness, determinism, scale-sensitivity, app-agnostic, or performance-risk issues that should block the next RT-DBSCAN engineering step?

**No blocking issues found.** Five non-blocking observations follow.

### Non-blocking: `plan_rt_dbscan_execution` remains on Goal2425 evidence, not direct-status

`plan_rt_dbscan_execution` (app lines 77–103) still routes `ngsim_dense` to `partner_cupy_prepared_grid_components_3d` based on Goal2425 evidence. This function serves a different planning surface (one-shot default plan) than `explain_rt_dbscan_explicit_route_choice` (repeated component-signature advisory). They are structurally separate and not in conflict. This observation is flagged only to confirm the two planners serve different surfaces, not to suggest a fix.

### Non-blocking: `ngsim_dense` factor 0.5 is now below 1.0x at 262k

The `ngsim_dense` factor `0.5` row at 262k yields `0.833x` replay speedup — slower than the current route. The guidance already correctly excludes factor `0.5` from the top-ranked 262k recommendation. This data point strengthens the case that the dense-profile factor is genuinely scale-sensitive, not merely noisy.

### Non-blocking: Carry-forward tie-break semantics (from Goal4124 review)

The advisor sorts by `abs(tested_point_count - resolved_point_count)`. At the current three-point spacing (65k, 131k, 262k), no equidistant query is possible within the tested range. However, once a 524k or other intermediate scale is added, a query at the geometric mean of two adjacent evidence points would tie-break by tuple insertion order. This is a latent determinism gap. The fix (prefer smaller tested scale, or document tie-break semantics) remains low-priority but should be addressed before the evidence table grows beyond four entries.

### Non-blocking: `road3d` replay speedup trends downward across scales

At 65k: `1.866x`. At 131k: `1.545x`. At 262k: `1.428x`. The speedup declines monotonically as scale grows, while `clustered3d` and `ngsim_dense` both show higher speedup at 262k than at 131k. This suggests the direct-status advantage for road-like profiles is shrinking at larger scales. This is not alarming at 1.428x (still clearly positive), but road3d should be an explicit priority in any next larger-scale packet.

### Non-blocking: The 262k `ngsim_dense` prepare time is visible in amortized speedup

The amortized speedup for `ngsim_dense` factor 0.25 is `2.550x` while the replay speedup is only `1.642x`. The prepare step (`0.219s`) is substantial relative to the replay (`0.095s`). For short repeated workloads the prepare amortization assumption may be fragile. The guidance correctly scopes this to "explicit repeated component-signature route over reused point/partition columns" and makes no whole-app or amortized claims. ✓

---

## Summary

| Goal | Finding |
|---|---|
| 4126 runner reuse | Confirmed: same schema (`rtdl.goal4117.partition_cell_factor_route_sweep.v1`), same protocol (repeat 4, warmup 1). Commit-pinned to `5ddd50cd`, clean worktree. |
| 4126 speedup values | All three values (`3.118x`, `1.428x`, `1.642x`) verified exactly against JSON raw fields and cross-check arithmetic. |
| 4126 factor table | All six factor-profile rows verify exactly. Partitions and max-neighbor-offset match. |
| 4126 signature preservation | `same_signature: true` and `all_factors_match_current_signature: true` on all rows. ✓ |
| 4127 advisory enforcement | No dispatch, no automatic selection, no hidden path. Structural enforcement via `__post_init__`. Validation returns `accept` with zero errors. |
| 4127 ngsim scale history | Correctly states 0.5 at 65k and 0.25 at 131k/262k. No universal factor claim. |
| Claim boundaries | All prohibited flags are `False` throughout all surfaces (JSON, advisor, registry). |

**Verdict: `accept-with-boundary`**

Goals 4126–4127 form a clean, internally consistent extension of the 131k chain from Goals 4121–4123. The 262k probe fairly reuses the Goal4117 runner, the pod is commit-pinned to a clean worktree, and all three speedup values are exactly supported by the JSON artifact. The advisor and route registry update is advisory-only with no dispatch surface, and the structural `__post_init__` guard enforces all claim boundaries at construction time. The scale-aware `ngsim_dense` guidance is correctly stated: factor `0.5` at 65k, factor `0.25` at 131k and 262k, with no universal-factor claim. All claim boundaries are intact.

This review does not authorize release, public speedup wording, broad RT-core wording, whole-app benchmark claims, paper-reproduction claims, hidden dispatch, automatic partner selection, automatic factor selection, native ABI additions, AMD performance claims, or true-zero-copy claims.
