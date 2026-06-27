# Claude Review — Goals 4134–4135: RT-DBSCAN 524k Factor-0.25 Extension

**Date:** 2026-06-09
**Reviewer:** Claude Sonnet 4.6 (external read-only review)
**Verdict:** `accept-with-boundary`

---

## Scope

- Goal4134: bounded 524,288-point extension probe using only `partition_cell_factor=0.25`; JSON pod artifact; report; test
- Goal4135: `current_benchmark_route_decisions.py` refresh after the 524k probe; advisor update; report; test

Prior context reviewed: Goal4132 Claude review and Goal4133 Gemini review of Goals 4130–4131 (warmed one-shot guidance); Goal4117 factor-sweep runner; Goal4122 131k probe; Goal4126 262k probe; Goal4130 one-shot probe.

No source files were edited. No tests were run. All findings are based on reading source, test, artifact, and report files.

---

## Question 1 — Does Goal4134 fairly run a bounded 524,288-point extension probe with only `partition_cell_factor=0.25`, and is the artifact cleanly commit-pinned to `93c52cb1` with dirty flag false?

**Yes on all counts.**

The JSON artifact carries `"schema": "rtdl.goal4117.partition_cell_factor_route_sweep.v1"`, matching the schema used by all prior pods in this chain (Goal4117, Goal4122, Goal4126, Goal4130). The `"partition_cell_factors"` array contains `[0.25]` only — no other factor is present, correctly scoping this as a bounded single-factor extension rather than a full sweep.

The artifact is commit-pinned to `"source_commit": "93c52cb1e316dd30046cf3cd393102edad479a95"` with `"source_tracked_worktree_dirty": false`. `"point_count": 524288`, `"repeat": 2`, `"warmup": 1` — the same `repeat=2, warmup=1` protocol introduced in Goal4130 for one-shot-compatible measurements.

The test `test_artifact_is_clean_commit_pinned_and_non_authorizing` verifies the schema, commit prefix `93c52cb1`, clean-worktree flag, `point_count == 524288`, `partition_cell_factors == [0.25]`, and all authorization flags as `false`. ✓

Note: the `"goal": "Goal4117"` field is a schema-provenance identifier, not a measurement-goal label. This is the established convention for this pod family. ✓

---

## Question 2 — Are the reported 524k replay and one-shot total speedups exactly supported by the JSON artifact?

**Yes. All six values verify exactly against the raw JSON fields and arithmetic cross-checks.**

The one-shot total speedup is computed as:

```
one_shot_speedup = current_route_amortized_sec / direct_amortized_sec
                 = (current_prepare + current_replay) / (direct_prepare + direct_replay)
```

where `current_route_amortized_sec` equals `current_route_prepare_sec + current_route_replay_sec` exactly in all three profile rows (verified below).

| Profile | current prepare (s) | current replay (s) | current total (s) | direct prepare (s) | direct replay (s) | direct total (s) |
|---|---:|---:|---:|---:|---:|---:|
| clustered3d | 2.455740 | 5.063083 | 7.518823 | 0.774792 | 1.538509 | 2.313301 |
| road3d | 1.468695 | 1.834984 | 3.303679 | 0.388058 | 1.342011 | 1.730070 |
| ngsim_dense | 1.404089 | 0.596999 | 2.001089 | 0.466359 | 0.337514 | 0.803873 |

**Arithmetic verification:**

- clustered3d prepare sum: 2.455740 + 5.063083 = 7.518823 ✓ (JSON `current_route_amortized_sec` = 7.518822893500328 ✓)
- clustered3d replay speedup: 5.063083 / 1.538509 = **3.2909** → report `3.291x` ✓ (JSON `best_replay_over_current_speedup` = 3.2909032826276006 ✓)
- clustered3d one-shot speedup: 7.518823 / 2.313301 = **3.2503** → report `3.250x` ✓ (JSON `amortized_over_current_speedup` = 3.2502570478176627 ✓)

- road3d prepare sum: 1.468695 + 1.834984 = 3.303679 ✓
- road3d replay speedup: 1.834984 / 1.342011 = **1.3673** → report `1.367x` ✓ (JSON = 1.367338734685153 ✓)
- road3d one-shot speedup: 3.303679 / 1.730070 = **1.9096** → report `1.910x` ✓ (JSON = 1.909563978798569 ✓)

- ngsim_dense prepare sum: 1.404089 + 0.596999 = 2.001089 ✓
- ngsim_dense replay speedup: 0.596999 / 0.337514 = **1.7688** → report `1.769x` ✓ (JSON = 1.7688146747096347 ✓)
- ngsim_dense one-shot speedup: 2.001089 / 0.803873 = **2.4893** → report `2.489x` ✓ (JSON = 2.489309162393376 ✓)

All six values match the JSON raw fields and arithmetic cross-checks to three decimal places. ✓

---

## Question 3 — Do all factor rows preserve the current grouped-stream route's component-size signature?

**Yes.**

All three profile rows in the JSON carry `"same_signature": true` on their single factor-row entry, and all three carry `"all_factors_match_current_signature": true` at the per-profile level. Since only `partition_cell_factor=0.25` was tested, there are three factor-rows in total (one per profile) and all three match.

The test `test_factor025_stays_positive_at_524k` asserts `assertTrue(factor["same_signature"])` and `assertTrue(row["all_factors_match_current_signature"])` for all three profiles. ✓

Correctness and performance continue to be treated as independent: even a sub-parity factor row (none are sub-parity here, as all three are above 1.0x replay) would still satisfy the signature contract.

---

## Question 4 — Does Goal4135 correctly state that the 524k packet is a factor-0.25 extension, not a full 524k factor sweep or universal factor claim?

**Yes, clearly and consistently.**

The Goal4135 report states: "The 524k packet does not run a full factor sweep. It only confirms that factor `0.25` remains above parity at the larger scale for the three tested profiles."

The `rejected_or_unpromoted_candidates` tuple in the route registry (`current_benchmark_route_decisions.py`) explicitly includes:

```
"universal factor sweep claim after Goal4134 factor-0.25-only 524k extension"
```

The `user_choice_guidance` field clarifies that the 524k evidence only extends the factor-0.25 advisory evidence column, not a universal factor recommendation. The Goal4134 report's boundary statement also reads: "Because this probe tests only factor `0.25`, it does not authorize a full 524k factor ranking or a universal factor claim." ✓

---

## Question 5 — Does the advisor correctly distinguish repeated replay ranking from one-shot total ranking, especially the 65k `ngsim_dense` asymmetry?

**Yes.**

In `explain_rt_dbscan_explicit_route_choice` (benchmark app lines 134–144), the sort key is:

```python
metric_key = "replay_speedup" if repeated else "one_shot_total_speedup"
tested_options.sort(key=lambda row: (
    abs(int(row["point_count"]) - resolved_point_count),
    -float(row[metric_key]),
    float(row["factor"]),
))
```

For `ngsim_dense` at `point_count=65536`, two entries exist with equal distance (0):
- factor `0.25`: `replay_speedup=0.969`, `one_shot_total_speedup=3.679`
- factor `0.5`: `replay_speedup=1.312`, `one_shot_total_speedup=1.819`

When `repeated=False` (one-shot), the sort uses `-one_shot_total_speedup`: factor `0.25` scores `−3.679` vs. factor `0.5` at `−1.819`, so `0.25` ranks first. ✓
When `repeated=True` (replay), the sort uses `-replay_speedup`: factor `0.5` scores `−1.312` vs. factor `0.25` at `−0.969`, so `0.5` ranks first. ✓

The asymmetry is explicitly stated in `user_choice_guidance`: "For dense NGSIM-like profiles, use the route advisor because the 65k best factor depends on intent: one-shot total timing ranks 0.25 first, while repeated replay ranks 0.5 first; 131k/262k/524k rank 0.25 first for the tested evidence."

The sort is deterministic at 65k because the speedup values differ. The carry-forward tie-break concern from prior reviews (equidistant entries with identical metric values) does not apply here. ✓

The 524k ngsim_dense entry has only one factor (0.25), so there is no ambiguity at the new scale. ✓

---

## Question 6 — Does the current route registry remain advisory-only, with no hidden dispatch, automatic route selection, automatic partner selection, or automatic factor selection?

**Yes, on every required dimension.**

`explain_rt_dbscan_explicit_route_choice` (benchmark app lines 110–199) returns:

- `"status": "advisory_only_no_dispatch"` ✓
- `"user_must_select_route": True` ✓
- `"automatic_dispatch_authorized": False` ✓
- `"automatic_partner_selection_authorized": False` ✓
- `"automatic_partition_cell_factor_selection_authorized": False` ✓
- `"hidden_dispatch_allowed": False` ✓

The function does not call `run_rt_dbscan_benchmark` or any route executor. Sorting `tested_options` by nearest scale and metric is purely informational and changes no runtime behavior.

The `CurrentBenchmarkRouteDecision.__post_init__` (registry lines 67–100) enforces all nine authorization flags as `False` and `user_explicit_choice_required` as `True` at object-construction time, making it structurally impossible to create a registry entry with any prohibited flag set.

`validate_current_benchmark_route_decisions()` returns `status="accept"` with `errors == ()` (asserted in `test_registry_summary_and_report_stay_non_authorizing`). ✓

`plan_rt_dbscan_execution` (benchmark app lines 81–107) remains unchanged from prior reviews — it routes by dataset and scale using Goal2425 evidence and returns `"not_hidden_dispatcher": True`. It does not reference Goal4134 or the 524k extension data. The two surfaces remain structurally separate. ✓

---

## Question 7 — Are all claim boundaries intact?

**Yes. All prohibited claims are `False` throughout all surfaces.**

| Claim | JSON pod (top/per-profile/per-row) | Advisor packet | Registry / `__post_init__` |
|---|---|---|---|
| Release authorized | `false` all levels | `False` | Enforced, `False` |
| Public speedup claim | `false` all levels | `False` | Enforced, `False` |
| Broad RT-core claim | `rt_core_speedup_claim_authorized: false` | `broad_rt_core_claim_authorized: False` | Enforced, `False` |
| Whole-app speedup | `whole_app_speedup_claim_authorized: false` | `False` | Enforced, `False` |
| Paper reproduction | not in pod schema | not in advisor | `paper_reproduction_claim_authorized: False` enforced |
| True zero-copy | `true_zero_copy_claim_authorized: false` | `False` | Enforced, `False` |
| Hidden dispatch | not applicable | `hidden_dispatch_allowed: False` | — |
| Automatic partner selection | `automatic_partner_selection_authorized: false` | `False` | Enforced, `False` |
| Automatic factor selection | `automatic_partner_selection_authorized: false` | `automatic_partition_cell_factor_selection_authorized: False` | Listed in `rejected_or_unpromoted_candidates` |
| Native ABI added | `native_abi_added: false` | `native_dbscan_abi_added: False` | `app_specific_native_engine_logic_allowed: False` enforced |
| App-specific engine logic | `app_specific_engine_logic_allowed: false` | `False` | Enforced, `False` |
| AMD performance claim | not in pod schema | not in advisor | `amd_performance_claim_authorized: False` enforced |
| Partition convergence promoted | `partition_convergence_hybrid_promoted: false` | — | Listed in rejected candidates |
| Universal factor sweep | not applicable | not applicable | `"universal factor sweep claim after Goal4134 factor-0.25-only 524k extension"` in `rejected_or_unpromoted_candidates` ✓ |

The `CURRENT_BENCHMARK_ROUTE_DECISION_VERSION` is now `"rtdl.v2_10.current_benchmark_route_decisions.goal4135.v1"`, correctly advancing from the Goal4131 version. The `CURRENT_BENCHMARK_ROUTE_DECISION_CLAIM_BOUNDARY` string now enumerates "a 524k factor-0.25 extension probe" in the evidence chain. ✓

---

## Question 8 — Are there correctness, determinism, scale-sensitivity, app-agnostic, or performance-risk issues that should block the next RT-DBSCAN engineering step?

**No blocking issues found.** Three non-blocking observations follow.

### Non-blocking: road3d replay speedup continues monotonic decline at 524k

road3d replay speedups across the evidence chain: 65k 1.866x → 131k 1.545x → 262k 1.428x → 524k 1.367x. The one-shot total trend: 65k 2.609x → 131k 2.606x → 262k 2.272x → 524k 1.910x. Both series are monotonically declining. At 1.367x replay and 1.910x one-shot total, the 524k case is still clearly positive, but road3d's advantage over the current route continues to erode at larger scales. This was flagged in the Goal4132/4133 reviews and remains a non-blocking monitoring item. If a 1M-point probe is added, road3d should be an explicit priority.

### Non-blocking: Tie-break semantics carry-forward (from Goal4124/4125/4128/4129/4132/4133 reviews)

The advisor sorts by `(abs(point_count - resolved_point_count), -metric_key, factor)`. With the current four-point spacing for clustered3d and road3d (65k, 131k, 262k, 524k) and five-point spacing for ngsim_dense (65k×2, 131k, 262k, 524k), no equidistant query is possible for clustered3d/road3d within the tested range, and the two 65k ngsim_dense entries are correctly distinguished by the metric key. This is a carry-forward observation confirmed resolved for the current table configuration.

### Non-blocking: `plan_rt_dbscan_execution` remains on Goal2425 evidence

This one-shot planning function still routes by dataset/scale using Goal2425 evidence and does not reference Goal4134. The two surfaces remain structurally separate, which is intentional. This observation is included only to confirm the separation remains intact after the Goal4135 update.

---

## Summary

| Goal | Finding |
|---|---|
| 4134 runner scope | Confirmed: single factor `[0.25]`, 524,288 points, `repeat=2`, `warmup=1`, schema `rtdl.goal4117.partition_cell_factor_route_sweep.v1`, commit `93c52cb1`, clean worktree. |
| 4134 speedup values | All six values (`3.291x`, `3.250x`, `1.367x`, `1.910x`, `1.769x`, `2.489x`) verified exactly against JSON raw fields and arithmetic cross-checks. |
| 4134 signature preservation | `same_signature: true` and `all_factors_match_current_signature: true` on all three factor-profile rows. |
| 4135 extension framing | Correctly framed as factor-0.25-only extension; "universal factor sweep claim" listed in `rejected_or_unpromoted_candidates`. |
| 4135 advisor asymmetry handling | `metric_key` correctly surfaces factor `0.5` for repeated 65k ngsim_dense and factor `0.25` for one-shot 65k ngsim_dense; `user_choice_guidance` makes the asymmetry explicit. |
| 4135 advisory enforcement | All advisory flags intact; no dispatch surface added; `__post_init__` guard enforces all nine prohibited flags; `validate_current_benchmark_route_decisions()` returns `accept`, `errors == ()`. |
| `plan_rt_dbscan_execution` separation | Confirmed unchanged; structurally separate from the advisor; Goal2425 evidence only. |
| Claim boundaries | All prohibited flags are `False` across JSON pod, advisor packet, and registry. |

**Verdict: `accept-with-boundary`**

Goals 4134–4135 form a clean, correctly scoped extension of the Goal4117/Goal4122/Goal4126/Goal4130 evidence chain. The probe is commit-pinned to `93c52cb1` with a clean worktree, restricted to a single factor (`0.25`), and all six reported speedup values are exactly supported by the JSON artifact. The advisor correctly exposes the 524k evidence and correctly distinguishes repeated replay ranking from one-shot total ranking, keeping the 65k `ngsim_dense` factor asymmetry visible rather than flattening it. The route registry explicitly rejects a universal factor sweep claim and lists the extension as factor-0.25-only. All claim boundaries are intact across the JSON pod, advisor packet, and registry, with structural enforcement via `__post_init__` and the validator returning `accept` with zero errors.

This review does not authorize release, public speedup wording, broad RT-core wording, whole-app benchmark claims, paper-reproduction claims, hidden dispatch, automatic partner selection, automatic factor selection, native ABI additions, AMD performance claims, or true-zero-copy claims.
