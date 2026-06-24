# Claude Review — Goals 4107–4110: Prepared Direct Status Chain

**Date:** 2026-06-09
**Reviewer:** Claude Sonnet 4.6 (external read-only review)
**Verdict:** `accept-with-boundary`

---

## Scope

- Goal4107: `V28PreparedFixedRadiusPartitionConvergenceDirectStatusUnionCupyPreview3D` handle and public surface
- Goal4108: prepared direct-status reuse timing script, POD artifact, and report
- Goal4109: explicit `partner_cupy_prepared_direct_status_union_component_signature_3d` app mode and smoke PODs
- Goal4110: `current_benchmark_route_decisions.py` refresh and route report

No source files were edited. No tests were run. All findings are based on reading source, test, and artifact files.

---

## Question 1 — Goal4107: Does the handle genuinely prepare reusable point/partition columns without materializing near-pair columns or app-specific native ABI?

**Yes, with one minor resource note.**

The `_prepare_direct_status_union_runtime_columns_cupy_3d` function (line 1748) allocates and retains these device columns:

| Column | Role |
|---|---|
| `x`, `y`, `z` | point coordinates (float64) |
| `unique_cells` | encoded partition keys |
| `point_partition_ids` | per-point partition assignment |
| `partition_offsets`, `partition_counts`, `partition_point_ordinals` | partition layout |
| `partition_aabb_min/max_x/y/z64` | AABB per partition (float64) |

The near-pair status is **not** prepared. It is computed on-demand each call in `_run_direct_status_union_signature_from_prepared_columns_cupy_3d` (line 1864) by calling `_cupy_direct_partition_status_union_component_roots` with the retained columns. No `near_pair_*` arrays are stored in `runtime_columns`.

The `to_metadata()` method reports `near_pair_columns_materialized: False`, `partition_pair_rows_materialized: False`, and `pair_materialization_avoided: True` at the handle level. These are also propagated to the run metadata (lines 1929–1934). The test scans the source section between `_prepare_direct_status_union_runtime_columns_cupy_3d` and `build_v2_8_fixed_radius_partition_convergence_summary_numba_preview_3d` for the strings `"dbscan"` and `"cluster"` and asserts they are absent — a correct structural guard.

The `V28PreparedFixedRadiusPartitionConvergenceDirectStatusUnionCupyPreview3D` dataclass stores `point_rows` (a Python tuple) in addition to the device columns. This is required for `validate_against_materialized_signature` to work, but it means the raw Python row tuples live for the lifetime of the handle. This is expected and consistent with the `V28PreparedFixedRadiusPartitionConvergenceSummaryCupyPreview3D` precedent.

**Minor resource note:** `close()` sets `closed = True` but does not explicitly delete or clear `runtime_columns`. GPU memory is therefore not freed until the Python object is garbage-collected. This matches the pattern in the CuPy summary preview handle and is not a correctness bug, but callers using the context manager (`__exit__` → `close()`) should be aware that GPU reclamation is deferred to GC. This is non-blocking but worth documenting in any future resource-management pass.

---

## Question 2 — Goal4108: Does the timing script fairly distinguish prepared replay evidence from one-shot/default-route evidence?

**Yes, cleanly.**

The `_run_profile` function (line 73 of the timing script) runs all three comparators within the same profile loop iteration, with a single point-generation step at the top:

- **Prepared replay**: calls `run_v2_8_fixed_radius_partition_convergence_component_signature_cupy_prepared_direct_status_union_preview_3d` on the same `prepared` handle.
- **One-shot direct status**: calls `build_v2_8_fixed_radius_partition_convergence_component_signature_cupy_direct_status_union_preview_3d` fresh each iteration (re-prepares everything).
- **Current route**: calls `run_rt_dbscan_benchmark` with `mode="optix_rt_core_grouped_stream_numba_column_signature_3d"`.

All three paths use the same `profile`, `point_count`, `seed`, and `radius`. Signature equality is asserted before the sample is recorded (line 146–150). GPU sync (`cupy.cuda.Stream.null.synchronize()`) is used before/after each timed segment.

The report correctly interprets the `ngsim_dense` three-run amortized result as "close enough that this should remain a preview." The test threshold for that profile is `(1.4, 1.1)` — the replay-vs-one-shot threshold is 1.4× and replay-vs-current is 1.1×, which are conservative lower bounds consistent with the artifact values (1.488× and 1.207×).

One honest limitation: wall-clock timing at this granularity on a shared GPU captures async effects. The report notes this. The three-repeat plus one-warmup design is appropriate for preview-quality evidence.

---

## Question 3 — Goal4109: Does the app expose a clear user-facing mode while preserving graph-component-only and non-default-route boundaries?

**Yes, on all required dimensions.**

The new mode `partner_cupy_prepared_direct_status_union_component_signature_3d` in `run_rt_dbscan_benchmark` (line 1353 of the app):

- Guards `include_rows=True` by raising `ValueError("signature mode does not materialize Python rows")` at line 969–979, **before** any CuPy import or GPU work. This is the correct pattern.
- Records `current_default_route: False`, `full_dbscan_semantics: False`, `graph_component_contract_only: True`, `partition_convergence_hybrid_promoted: False`.
- Records `materializes_partition_pair_rows: False`, `materializes_near_pair_columns: False`, `pair_materialization_avoided: True` — the non-materialization boundary propagates from the handle into the app metadata dictionary at line 1397–1401.
- The `partition_pair_enumeration` override is noted as `partition_pair_enumeration_ignored_by_direct_status_union` when overridden, which is correct — the direct-status path does not use the pair enumeration parameter.

The tiny POD confirms `matches_reference: true` with identical component signatures `[1, 4, 4]`. The clustered65536 POD confirms the mode runs at benchmark scale with `matches_reference: null` (validate=False), consistent with production smoke behaviour.

The `validate` path at line 1414–1423 builds the component labels reference and compares component sizes — this is a component-label reference comparison, not a DBSCAN reference. The contract is correctly `fixed_radius_graph_component_size_signature_3d`.

---

## Question 4 — Goal4110: Does the route guidance correctly keep one-shot conservative while allowing explicit prepared-direct-status use?

**Yes, with an appropriately scoped next action.**

The `rt_dbscan` decision (line 169–259 of `current_benchmark_route_decisions.py`):

- Keeps `primary_route` as the grouped-stream Numba continuation.
- Documents the prepared direct-status path in `user_choice_guidance` with an explicit condition: "only when the workload reuses the same point/partition columns for repeated component-signature queries."
- Adds `"partition_convergence_hybrid universal default promotion after Goal4108 prepared replay and Goal4109 app smoke"` to `rejected_or_unpromoted_candidates`.
- Identifies the specific `next_runtime_action`: "measure a route-level repeated prepared direct-status app packet and define an explicit reuse threshold."

The guidance correctly distinguishes:
- The one-shot smoke is prepare-dominated (0.560s total, 0.503s prepare, 0.056s signature at 65k).
- The prepared replay wins are clear but bounded to the `resident-reuse` operating condition.
- The `ngsim_dense` 1.207× replay-over-current margin is explicitly noted as a narrow case requiring further evidence before widening the recommendation.

The `__post_init__` on `CurrentBenchmarkRouteDecision` enforces all nine prohibited flags remain `False` at object-construction time. `validate_current_benchmark_route_decisions()` re-checks these at runtime. The test confirms validation returns `status="accept"` with zero errors for all 10 apps.

---

## Question 5 — Claim boundaries

The following claims are reviewed across all four goals:

| Claim | Status |
|---|---|
| Release authorized | `False` in all artifacts, metadata dicts, and dataclass fields ✓ |
| Public speedup claim | `False` everywhere ✓ |
| Broad RT-core claim | `False` everywhere ✓ |
| Whole-app benchmark claim | `False` everywhere ✓ |
| Paper reproduction claim | `False` everywhere ✓ |
| True zero-copy claim | `False` everywhere ✓ |
| Hidden dispatch | `False` everywhere ✓ |
| Automatic partner selection | `False` everywhere ✓ |
| Native ABI added | `False` everywhere ✓ |
| App-specific engine logic | `False` everywhere ✓ |
| `partition_convergence_hybrid` promoted | `False` everywhere ✓ |

The `V28FixedRadiusGraphComponentPlan.__post_init__` (line 186–198) raises `ValueError` at object construction if any of nine authorization flags is `True`, preventing silent claim creep. This guard is enforced in all four goals.

The Goal4108 script additionally records `partition_convergence_hybrid_promoted: False` at the per-profile row level and at the top-level payload level.

No issues found.

---

## Question 6 — Correctness, determinism, route-guidance, and performance-risk issues

### Correctness: no blocking issues found

The tiny-dataset test (`test_prepared_direct_status_reuses_columns_and_matches_materialized_signature`) verifies that the prepared direct-status signature equals the materialized reference signature for 6 points at radius 0.05. The tiny POD independently confirms this for 9 points at the app layer.

The signature comparison target in `run_component_signature` is `build_v2_8_fixed_radius_partition_convergence_component_signature_cupy_preview_3d` with `pair_enumeration="device_count_then_emit_non_skip_unordered"` — a previously validated path. The cross-check is therefore against a known-good reference, not a self-comparison.

### Determinism

The direct-status union iterates to convergence with `max_iterations=64`. The convergence loop is not analyzed in this chain for pathological cases (worst-case diameter inputs). The iteration count is bounded and the test confirms `union_iterations: 2` for the tiny case. For production inputs, convergence is empirically confirmed by signature-match checks in Goal4108. This is the same pattern used in earlier Goals (4104/4105) and is not a regression.

The `component_roots` step uses `cupy.unique(component_roots, return_counts=True)` which is deterministic in sorted output. The signature is sorted before comparison. No ordering-nondeterminism risk here.

### Route guidance

Goal4110's next action is specific and actionable: a route-level packet with same-contract correctness, no ngsim_dense regression, and production timing outside the prepared-reuse-only boundary. This is the correct blocker for one-shot default promotion and it is correctly left unmet.

### Performance risk

The ngsim_dense three-run amortized margin is thin (~4%, 0.099s vs 0.103s). This is accurately identified as the weakest profile. If future runs at different hardware or driver versions show this margin disappearing, the amortized claim would need to be qualified further. The report correctly stops short of calling this a universal win.

The clustered65536 one-shot app-mode smoke (0.560s) is prepare-dominated (0.503s prepare, 0.056s signature). This makes the mode unsuitable as a one-shot default — which is the correct conclusion in Goal4110.

---

## Summary

| Goal | Finding |
|---|---|
| 4107 | Correctly prepares point/partition columns without near-pair materialization or app-specific ABI. Minor: `close()` defers GPU reclamation to GC. |
| 4108 | Fair three-way comparison with signature verification. Conservative interpretation of `ngsim_dense` margin. |
| 4109 | Clean user-facing mode with proper boundary metadata and early `include_rows` guard. |
| 4110 | Conservative route guidance update. Promotion correctly blocked. Next action well-defined. |
| Claim boundaries | All prohibited flags are `False` across all artifacts. Structural enforcement via `__post_init__` is intact. |

**Verdict: `accept-with-boundary`**

The chain is internally consistent, claim boundaries are properly enforced and structurally guarded, correctness is verified against reference implementations, and the conservative route guidance correctly blocks one-shot default promotion. The chain is ready for the next engineering step (route-level repeated prepared direct-status app packet with explicit reuse threshold).

No issues were found that should block the next step. The one non-blocking note (deferred GPU memory reclamation in `close()`) is consistent with prior handles and does not affect correctness.
