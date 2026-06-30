# Goal3543 Claude Review — Goal3542 v2.9 Repeat/Resident Hook Coverage

**Verdict: accept-with-boundary**

Reviewed by: Claude Sonnet 4.6
Date: 2026-06-06
Scope: Goal3542 measurement-readiness implementation, not a pod-timing run

---

## Summary

Goal3542 adds repeat/resident hooks to the five rows that Goal3536 could not plan as `internal_repeat_knob`, and removes the artificial `high_setup_extreme_repeat` shortcut that previously allowed robot collision to bypass the wall-time guard without actually holding a hot-query repeat loop. All five rows now carry `--repeat`/`--warmup` flags; the planner dry-run confirms `internal_repeat_knob` for all ten plan slots (five rows × two lanes). No native engine logic was added. The report's claim boundary is clean.

---

## Per-Check Findings

### 1. Do the new repeat hooks measure hot prepared query phases rather than rebuilding scenes?

**Hausdorff** (`_run_prepared_directed_threshold`, lines 232–291)
`rt.prepare_generic_fixed_radius_count_threshold_2d` is called once as the `with` context manager. The loop (lines 242–253) calls only `prepared.count_threshold_reached(...)` per iteration. `scene_prepare_sec` is read from `prepared.scene_prepare_sec` *after* the loop exits. The primary metric is the median of `query_fixed_radius_threshold_reached_count_sec` across measured (non-warmup) iterations. Setup is cleanly excluded. **Pass.**

**Barnes-Hut** (`_run_prepared_node_coverage`, lines 374–445)
Identical structure to Hausdorff: one-time `with rt.prepare_generic_fixed_radius_count_threshold_2d(...)` before the loop; loop calls `prepared.count_threshold_reached(_body_points(bodies), ...)` per iteration; `prepare_sec` captured post-loop. Stability check (`len(covered_counts) != 1`) raises `RuntimeError` if the covered-body count varies across repeats. **Pass.**

**RayJoin** (`run_rayjoin_prepared_optix_workload` + `_phase_repeat_time`, lines 487–942 and 254–286)
`_phase_repeat_time` wraps the hot function call with warmup/measured split and records `statistics.median(elapsed)` into `phases["prepared_query_sec"]`. For count mode, the lambda calls `prepared.count(...)` or `prepared.count_active(...)` — scalars only, no view lifetime involved. For the `prepared_optix` benchmark case the registry supplies `--result-mode count`, so the raw-view path is not exercised. **Pass for deployed benchmark case.** See minor concern in §2.

**LibRTS** (`run_optix_aabb_counts`, lines 415–542)
Scene prepared once (`rt.prepare_optix_aabb_index_2d`); with `prepared_queries=True` (the default, used by the registry), query buffers are prepared once per operation type into `prepared_query_cache`. The hot loop calls `prepared.count_prepared_queries(prepared_query_cache[query_kind], operation=name)` per iteration. Count stability check (`len(count_values) != 1`) raises on drift. **Pass.**

**Robot Collision**
Pre-existing `--repeats` hook; now correctly routed through `internal_repeat_knob` after the `high_setup_extreme_repeat` shortcut is removed. No new code reviewed; behavioral change verified through planner test. **Pass.**

---

### 2. Are repeated raw-view paths safe?

For the RayJoin raw-view path (used when `result_mode="rows"`), each `run_raw_once()` invocation creates a view, reads `view.row_count`, optionally materialises `view.to_dict_rows()`, then calls `view.close()` in a `finally` block. View lifetime is correct.

**Minor concern**: The raw-view repeat path in `_phase_repeat_time` does not assert count stability across iterations (unlike Hausdorff, Barnes-Hut, and LibRTS which all raise `RuntimeError` on count drift). This is not a blocker because:
- The Goal2626 registry uses `--result-mode count` for `spatial_rayjoin_optix_prepared_full_route`, so the raw-view code path is not exercised by this benchmark case.
- The primary metric `prepared_query_total_sec` is derived from `phases["prepared_query_sec"]` (the median), which is only populated via `_phase_repeat_time` in the count branch.

**Recommendation for Goal3543 or a follow-up**: Add count-stability assertion to the raw-view repeat path to match the guard discipline of the other apps, even though it is not currently hit in the benchmark.

---

### 3. Does the Goal3536 planner retain the wall-time guard while removing only the artificial shortcut?

`_planned_case` in `goal3536_v2_8_vs_v2_3_10s_steady_state.py` (lines 127–240) is reviewed:

- `high_setup_extreme_repeat` is absent (verified by `test_artificial_high_setup_shortcut_is_removed`).
- When a repeat knob exists and the estimated wall time would exceed `max_estimated_wall_sec`, the planner returns `method="partial_base_repeat_wall_guard"` (lines 169–185), not `internal_repeat_knob`. The wall-time guard is intact.
- `partial_base_repeat_wall_guard` was present before Goal3542; it is unchanged by this goal. Only the path through `high_setup_extreme_repeat` was removed.

**Pass.**

---

### 4. Does the Goal2626 registry use the right primary metric paths?

| Case | `primary_metric_path` | Correct path? |
|------|----------------------|---------------|
| `hausdorff_optix_threshold` | `("run_phases", "query_fixed_radius_threshold_reached_count_sec")` | Yes — median query time from `_run_prepared_directed_threshold` |
| `spatial_rayjoin_optix_prepared_full_route` | `("prepared_query_total_sec",)` | Yes — top-level field in `run_rayjoin_suite` output, sum of per-workload `phases["prepared_query_sec"]` medians |
| `barnes_hut_optix_node_coverage` | `("node_coverage", "run_phases", "query_fixed_radius_threshold_reached_count_sec")` | Yes — `_annotate` spreads the app payload so `node_coverage` is top-level; path resolves correctly |
| `librts_optix_aabb_index` | `("run_phases", "query_median_sec")` | Yes — new field, replaces total wall time. `query_median_sec = float(sum(query_sec.values()))` |
| `robot_collision_optix_prepared_device_buffers` | `("tail_medians", "total_run_seconds")` | Unchanged, pre-existing |

**LibRTS naming note**: `query_median_sec` is set to `sum(query_sec.values())` where each `query_sec[name]` is itself a median over repeats for one operation. The name is slightly misleading (it is a sum of per-operation medians, not a single median over all operations). This is internally consistent and documented, but consumers reading the field name should know it aggregates three operation medians. Not a correctness defect.

**Pass overall.**

---

### 5. Does the report avoid overclaiming?

The report (`goal3542_v2_9_repeat_resident_hook_coverage_2026-06-06.md`) is reviewed:

- Status is `internal engineering milestone, not release evidence` (line 3).
- Explicitly lists six unauthorised claims: v2.9 release, public speedup, broad RT-core, whole-app speedup, true zero-copy, paper reproduction.
- States "This is a measurement-readiness result only. It does not replace the required A5000/pod rerun."
- The design boundary section confirms no new native/RT engine logic was added.
- `rt_core_accelerated: backend == "optix"` is set to `True` in the app output for the prepared threshold path, which is accurate at the app level; the report does not use this to make a speedup claim.

**Pass.**

---

### 6. What must be fixed before Goal3543 pod timing evidence?

No hard blockers. The hooks are correct and the planner routes correctly. The following should be addressed before or alongside the Goal3543 run:

**Required for valid Goal3543 evidence:**
- Nothing. The five rows are now measurable as `internal_repeat_knob`. The planner dry-run confirms all ten plan slots resolve correctly with the seed artifact from Goal3536.

**Should be addressed (non-blocking):**
1. **RayJoin raw-view count stability** — Add an inter-iteration count-stability assertion to `_phase_repeat_time` or `run_raw_once` to match the guard discipline in Hausdorff, Barnes-Hut, and LibRTS. This does not affect the deployed benchmark measurement path today but is a defensive hygiene gap.
2. **LibRTS `query_median_sec` naming** — Consider renaming to `query_summed_median_sec` or adding a comment clarifying it is the sum of per-operation medians, to reduce reader confusion.

---

## Test Coverage Assessment

`goal3542_v2_9_repeat_resident_hook_coverage_test.py` covers:
- Report phrase checks (scope, claim boundary, required next step)
- Presence of `--repeat`, `--warmup`, and `query_repeat|repeat_protocol` in all five app sources
- Registry wiring of `--repeat`/`--warmup` for all four newly wired cases (Hausdorff, RayJoin, Barnes-Hut, LibRTS)
- `primary_metric_path=("run_phases", "query_median_sec")` presence for LibRTS
- Planner dry-run produces exactly 10 rows all with `method="internal_repeat_knob"` and `target_met_by_plan=True`
- Absence of `high_setup_extreme_repeat` and presence of `partial_base_repeat_wall_guard`

The `goal3536_v2_8_vs_v2_3_10s_steady_state_test.py` adds a companion test (`test_v2_9_repeat_hooks_plan_former_partial_rows_as_internal_repeats`) that independently verifies the same five rows plan correctly using the A5000 seed artifact.

Coverage is comprehensive for the stated goal.

---

## Verdict

**`accept-with-boundary`**

The hook additions are structurally correct, hot-phase separation is enforced, count stability is guarded for the three apps that return per-query counts, the wall-time guard is preserved in the planner, the LibRTS primary metric is now resident query time rather than total wall time, and the report does not overclaim.

The two non-blocking findings (RayJoin raw-view stability gap and LibRTS metric naming) should be tracked as v2.9 hygiene items but do not prevent proceeding to Goal3543 pod timing.

Goal3543 must produce actual A5000 timing artifacts for all five formerly partial rows before any performance positioning is accepted.
