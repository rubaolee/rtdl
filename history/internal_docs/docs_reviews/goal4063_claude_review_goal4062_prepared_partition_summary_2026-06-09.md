# Goal4063 — Claude Independent Review of Goal4062 Prepared Partition-Convergence Summary Preview

**Reviewer:** Claude (claude-sonnet-4-6)
**Date:** 2026-06-09
**Verdict:** `accept-with-boundary`

This review is independent from Codex authoring. Codex+Codex is not valid
consensus; this review was conducted by reading the production source, tests,
report, and timing artifact fresh, without relying on any prior review or
summary.

---

## Files Inspected

- `src/rtdsl/v2_8_fixed_radius_graph_component_front_door.py` (full)
- `src/rtdsl/__init__.py` (exports section)
- `tests/goal4062_prepared_partition_convergence_summary_preview_test.py`
- `tests/goal4044_partition_candidate_runtime_status_metadata_test.py`
- `docs/reports/goal4062_prepared_partition_convergence_summary_preview_2026-06-09.md`
- `docs/reports/goal4062_prepared_partition_summary_timing_pod.json`

---

## Q1 — Is the prepared-summary handle app-agnostic?

**Yes.**

The `V28PreparedFixedRadiusPartitionConvergenceSummaryCupyPreview3D` class
(lines 1434–1545) and its two consumer wrappers
(`run_v2_8_fixed_radius_partition_convergence_component_labels_cupy_prepared_preview_3d`,
`run_v2_8_fixed_radius_partition_convergence_component_signature_cupy_prepared_preview_3d`)
operate on the generic `fixed_radius_partition_convergence_summary_3d` stream.
No DBSCAN primitives, clustering terminology, or app-specific engine logic
appears in the prepared-handle section. The source test
`test_source_and_report_keep_app_agnostic_non_promotion_boundary` enforces this
mechanically by scanning the section from class declaration to the Numba preview
function and asserting that neither "dbscan" nor "cluster" appears. That test
boundary check is present and covers the right slice of source.

The handle stores `point_rows`, `radius`, `cell_factor`, `pair_capacity`, and
`pair_enumeration`. These are all generic partition-summary parameters. The two
consumers forward to the established generic CuPy preview functions
(`build_v2_8_fixed_radius_partition_convergence_component_labels_cupy_preview_3d`
and
`build_v2_8_fixed_radius_partition_convergence_component_signature_cupy_preview_3d`)
with `partition_summary=self.partition_summary` to trigger the existing
partition-reuse path. No new primitive is introduced.

---

## Q2 — Are the candidate-route boundaries honest?

**Yes, with disciplined multi-layer enforcement.**

The boundary flags are set to `False` at every level independently:

1. **`V28FixedRadiusGraphComponentPlan.__post_init__`** raises `ValueError` for
   any of the nine claim/authorization booleans set to `True`. The plan
   dataclass makes it impossible to construct a valid plan with any claim
   leaked in.

2. **`V28PreparedFixedRadiusPartitionConvergenceSummaryCupyPreview3D.to_metadata()`**
   stamps all nine flags `False` on the handle-level metadata:
   `native_abi_added`, `default_route_promoted`,
   `partition_convergence_hybrid_promoted`, `release_authorized`,
   `public_speedup_claim_authorized`, `rt_core_speedup_claim_authorized`,
   `whole_app_speedup_claim_authorized`, `true_zero_copy_claim_authorized`,
   `app_specific_engine_logic_allowed`, `automatic_partner_selection_allowed`,
   `hidden_dispatch_allowed`.

3. **`_decorate_prepared_partition_summary_result`** re-stamps the same set on
   every per-run result, so no downstream result can inherit a leaked flag from
   an intermediate layer.

4. **`_hybrid_runtime_status_metadata()`** keeps `default_route_promoted: False`
   and `partition_convergence_hybrid_promoted: False` in the planner-level
   description, visible in both `describe_v2_8_fixed_radius_graph_component_front_door()`
   and `plan_v2_8_fixed_radius_graph_component_continuation()` with
   `strategy="partition_convergence_hybrid"`.

5. The `__init__.py` exports confirm the four new symbols are published to the
   public surface (`V28PreparedFixedRadiusPartitionConvergenceSummaryCupyPreview3D`,
   `prepare_…`, `run_…_component_labels_…`, `run_…_component_signature_…`) and
   no undocumented dispatch entry-points are visible.

No default promotion, no native ABI addition, no hidden dispatch, no automatic
partner choice, no release/speedup/RT-core/whole-app/true-zero-copy claim is
present anywhere in the diff.

---

## Q3 — Is the timing artifact interpreted correctly?

**Yes, with one minor data anomaly worth flagging.**

The pod `goal4062_prepared_partition_summary_timing_pod.json` correctly frames
results as prepared-replay evidence:

- `claim_boundary` in the root object states explicitly that the artifact does
  not promote `partition_convergence_hybrid`, authorize release, public speedup,
  broad RT-core, whole-app, hidden-dispatch, automatic partner selection,
  app-specific engine logic, native ABI addition, or true-zero-copy claims.
- All top-level claim booleans are `false`.
- `source_commit: ddcc0680` correctly pins the hardware run.
- The `prepared_signature_metadata` on each row records
  `prepared_partition_summary_reused: true` and
  `prepared_partition_summary_handle_status: explicit_cupy_preview_not_promoted`,
  confirming the timing measures replay of a prepared summary, not a
  one-shot call.
- The report section "Pod evidence at source commit `ddcc0680`…" distinguishes
  replay-only speedup from three-run amortized speedup, correctly explaining
  that the amortized figure includes the prepare cost.

**Data anomaly (non-blocking):** In the `road3d_4096` row,
`prepared_replay_speedup_min` (6.275) exceeds `prepared_replay_speedup_median`
(6.130). A minimum statistic should not exceed the median over the same sample.
This is likely a recording artifact — the `_min` and `_median` fields may come
from different timing runs or the field semantics shifted during the script.
The test only asserts `> 3.0` on `prepared_replay_speedup_min`, which passes.
This does not invalidate the replay speedup claim but the pod should be treated
with caution for this row if the exact figures are cited.

The `prepare_validation` on all six rows has
`summary_same_contract_validation_skipped_for_prepared_timing: true`. This is
the intended design: validation is skipped in timing runs to measure pure
replay cost. The functional test `Goal4062PreparedPartitionSummaryRuntimeTest`
calls `validate_summary_same_contract=True` and `validate_against_all_pairs=True`
to confirm correctness separately. The distinction is honest and well-labelled.

---

## Q4 — Is the blocker rename accurate?

**Yes.**

Old blocker: `no_prepared_native_or_partner_partition_handle`
New blocker: `no_promoted_prepared_native_partition_handle`

Goal4062 adds an explicit CuPy (partner-side) prepared partition-summary
handle. The old blocker stated that no prepared native or partner handle
existed; that is now factually incorrect, because a CuPy partner preview handle
does exist. The rename to `no_promoted_prepared_native_partition_handle` is
accurate on both counts:

- "no promoted": the handle is marked `explicit_cupy_preview_not_promoted`
  throughout and `partition_convergence_hybrid_promoted: False` everywhere. A
  promoted native handle (one that replaces or promotes the grouped-stream route
  as the default) does not yet exist.
- "native": a CuPy preview is a partner-side Python/CuPy layer, not a native
  (OptiX-compiled) partition producer. The distinction is preserved; the
  remaining gap is at the native/OptiX level.

The rename does not overstate Goal4062's contribution and does not close the
blocker prematurely.

---

## Q5 — What must happen next before this becomes a promoted/default v2.x route?

Five blockers remain in
`V2_8_FIXED_RADIUS_GRAPH_COMPONENT_HYBRID_PROMOTION_BLOCKERS`:

1. **`Goal4041_mixed_timing_not_universal_speed_win`** — Goal4041 found that the
   partition-convergence approach does not universally beat the grouped-stream
   route across all tested profiles. A promoted route must be a universal speed
   win on representative workloads, or the tradeoff must be explicitly accepted
   with evidence.

2. **`prepared_front_door_still_grouped_stream_only`** — The promoted
   `prepare_v2_8_fixed_radius_graph_component_continuation_3d` front door still
   routes through grouped-stream OptiX+partner continuations. The
   partition-convergence path is not reachable through the promoted front door;
   it is only accessible via the explicit `prepare_v2_8_fixed_radius_partition_convergence_summary_cupy_preview_3d`
   preview path.

3. **`host_compact_label_materialization_breaks_resident_output`** — The CuPy
   component-label preview materializes labels as host Python tuples
   (`point_labels = tuple(partition_labels[…])`), breaking the device-resident
   output guarantee expected of a promoted route.

4. **`separate_ambiguous_classifier_kernel_not_fused`** — The ambiguous-pair
   classification runs as a separate CuPy RawKernel invocation, not fused with
   the primary partition-pair traversal. This is an efficiency and correctness
   isolation gap that must be resolved before the route can be promoted.

5. **`no_promoted_prepared_native_partition_handle`** — No native (OptiX-level)
   partition producer exists. The promoted route requires a native partition
   kernel, not a CuPy Python preview, to be the default path. The
   `next_engineering_target` in `_hybrid_runtime_status_metadata()` is stated as
   "fused resident component-label continuation or promoted native partition
   handle."

Until all five blockers are resolved, the partition-convergence candidate cannot
become a default or promoted v2.x route.

---

## Summary Assessment

Goal4062 is a well-scoped incremental step. It adds an explicit prepared preview
handle for the generic partition-convergence summary stream, enabling partition
columns to be built once and replayed across multiple component-label or
component-signature probes. The handle is app-agnostic, the claim boundaries are
mechanically enforced at plan, handle, and per-run result levels, and the timing
artifact is honestly scoped to replay speedup with all claim flags false. The
blocker rename from `no_prepared_native_or_partner_partition_handle` to
`no_promoted_prepared_native_partition_handle` is accurate. The five remaining
promotion blockers are intact and the candidate route is not promoted.

The one non-blocking data anomaly (min > median in the road3d_4096 timing row)
should be noted in any external citation of those specific figures, but does not
affect the claim scope.

**Verdict: `accept-with-boundary`**

The boundary is: this is a generic CuPy preview handle for prepared-replay
speedup evidence only. It does not add a native ABI, does not promote the
partition-convergence hybrid as a default route, does not authorize any release
or public speedup claim, and does not satisfy any of the five remaining
promotion blockers.
