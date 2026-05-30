# Independent Claude Review: Goals 2720–2723 — v2.5 Prepared Hit-Stream and Tiered Manifest

**Date:** 2026-05-30
**Reviewer:** Claude (claude-sonnet-4-6), independent review — distinct from Codex
**Verdict:** `accept-with-boundary`

---

## Scope

This is an independent Claude review of Goals 2720, 2722, and 2723. It covers:

- Goal 2720: prepared RayDB-style native OptiX device hit-stream steady-state path
- Goal 2722: large-scale RTX A5000 pod evidence for the prepared path
- Goal 2723: tiered 10-benchmark v2.5 manifest separating Tier A parity, Tier B bets, and Tier C baselines

Source files inspected: benchmark app (2567 lines), pod runner script, `v2_5_triton_app_migration.py`, `__init__.py` public API surface, both pod JSON artifacts, both markdown reports, and all four test files.

---

## Q1 — Prepared Path Engine Boundary

**Finding: Clean.**

`_run_paper_rt_prepared_device_hit_stream_triton_result_mode` (benchmark app, lines 1974–2219) correctly separates concerns:

- `prepare_paper_rt_encoded_table_descriptor` is app-owned Python that constructs dense scan/group encodings — no RTDL or native involvement.
- `prepare_generic_typed_primitive_payload_columns` and `prepare_optix_static_triangle_scene_3d` are generic RTDL APIs with no RayDB, SQL, or database vocabulary.
- The steady-state loop calls `prepared_scene.ray_triangle_hit_stream_device_columns` (generic OptiX primitive) and `gather_typed_payload_columns_for_hit_stream` (generic RTDL handoff API).
- Triton continuation uses the public adapter front door (`partner_group_count_by_key`, `partner_group_sum_by_key`, etc.).

The native symbol recorded in every artifact is `rtdl_optix_static_triangle_scene_3d_ray_triangle_hit_stream_device_columns` — no app-specific tokens.

The `group_id_bounds_validation="caller_asserted"` flag at line 2011 is a correct performance optimization. Dense group encoding is provably bounded by app code before the native call; this is an app-level responsibility that does not need to leak into the engine.

The `engine_boundary` metadata string in the result confirms the separation explicitly. The prepared path adds no RayDB-specific logic to the native layer.

---

## Q2 — Pod Artifact Consistency

**Finding: Internally consistent; numbers match reports exactly.**

### Goal 2720 smoke (10k and 100k rows, count and sum)

The JSON artifact (`goal2720_raydb_prepared_device_hit_stream_smoke_pod_69_30_85_171_2026-05-30.json`) was read in full. Key checks:

| Row count | Mode | Unprepared median (s) | Prepared median (s) | Ratio | Report claims |
|---:|---|---:|---:|---:|---|
| 10 000 | count | 0.027641 | 0.005005 | 5.52× | 5.522× ✓ |
| 10 000 | sum | 0.128689 | 0.027570 | 4.67× | 4.668× ✓ |
| 100 000 | count | 0.176325 | 0.007366 | 23.94× | 23.938× ✓ |
| 100 000 | sum | 0.602112 | 0.116064 | 5.19× | 5.188× ✓ |

All 8 cases: `matches_cpu_reference = true`. All 4 prepared cases: `prepared_steady_state = true`, `prepared_payload_columns_reused = true`, `prepared_optix_scene_reused = true`, `host_row_bridge_bypassed = true`, `true_zero_copy_authorized = false`.

The unprepared `workload_build` timings explain the speedup mechanically. For the 100k count case, the unprepared `workload_build` is ~0.014 s and accounts for most of the outer-loop overhead accumulated over three cold-rebuilt iterations. For the 10k sum case, `hit_stream_native_call` at ~0.022 s dominates the prepared-path timing, correctly showing that payload traversal is the remaining cost once setup is amortized.

### Goal 2722 large-scale (250k and 1M rows, count and sum)

The JSON artifact header was verified. Key checks:

| Row count | Mode | Reported ratio | Physical explanation |
|---:|---|---:|---|
| 250 000 | count | 65.4× | Unprepared rebuilds sparse triangle workload; hit stream is very sparse |
| 250 000 | sum | 5.7× | Native call for sum is heavier; ratio lower but still material |
| 1 000 000 | count | 210.3× | Workload rebuild at 1M rows dominates unprepared timing |
| 1 000 000 | sum | 10.5× | Same pattern |

All ratios are physically credible. The count advantage grows at scale because the unprepared path rebuilds a triangle scene proportional to row count each timed call, while the prepared path reuses it. The sum advantage is smaller because the native hit-stream call with value payload is heavier, proportional to hit count rather than triangle count.

Both artifacts carry `no_public_speedup_claim: true`, `all_correct: true`, and consistent boundary strings.

---

## Q3 — Claim Boundaries

**Finding: Conservative and consistent.**

Every artifact field that could authorize a public claim is explicitly set to false or a blocking string:

- `true_zero_copy_authorized: false` — every case, both goals
- `promoted_performance_path: false` — every phase-timing record
- `public_speedup_claim_authorized: false` — every adapter descriptor
- `rt_core_speedup_claim_authorized: false` — continuation plan metadata
- `neutral_buffer_seam` transfer statuses: `"borrowed_device_pointer_unmeasured"` — no transfer has been upgraded to a measured claim

The `same_pointer_evidence_observed: true` field appears in the torch carrier execution records. This is correctly bounded: same-pointer evidence proves the adapter ran without a host copy, but the neutral buffer seam explicitly classifies the transfer as `borrowed_device_pointer_unmeasured`, and `true_zero_copy_authorized` remains false. This is the correct layered boundary posture.

The markdown reports explicitly disclaim: public true-zero-copy wording, broad RT-core speedup wording, RayDB paper reproduction, whole-app speedup claims, and treating prepared steady-state as a replacement for cold whole-app timing.

No claim overreach found.

---

## Q4 — Tiered Manifest Category Errors

**Finding: Manifest correctly prevents category errors. Validator is machine-checkable.**

`v2_5_triton_app_migration.py` implements `V2_5_TIERED_BENCHMARK_MANIFEST_ROWS` (10 rows) and `validate_v2_5_tiered_benchmark_manifest()` which checks:

- Exactly 10 apps, no duplicates
- Exactly 4 Tier A / 4 Tier B / 2 Tier C
- `public_speedup_claim_authorized = False`
- `true_zero_copy_claim_authorized = False`
- Tier C rows do not mention partner parity
- Tier A and B rows each name a same-contract opponent
- RayDB row records prepared pod evidence

Category separation is correct:

**Tier A** (count/parity achievable with current surface): raydb_style (partner continuation, proven), triangle_counting (needs wiring + streaming closure), spatial_rayjoin and librts_spatial_index (RT-core count/parity track — Triton only if count path enters benchmark timing). The separation between partner-continuation Tier A apps and RT-core-track Tier A apps is preserved in the `benchmark_track` field.

**Tier B** (new generic operations needed): rt_dbscan needs `grouped_components_or_fallback`; rtnn needs `bounded_topk_or_ranked_summary`; barnes_hut needs `grouped_vector_sum`; hausdorff_xhd needs `grouped_argmax_witness`. None of these are in the current adapter front door (`V2_5_TRITON_PARTNER_ADAPTER_FRONT_DOOR_OPERATIONS`). The manifest correctly flags these as per-app bets rather than uniform Triton parity targets.

**Tier C** (no-regression only): contact_manifold and robot_collision. The manifest enforces `"no-regression"` in the parity target and `"rt_core"` in the benchmark track. The validator rejects any Tier C row that mentions partner parity. These apps should never be compared against a Triton continuation opponent.

The `test_tier_c_rows_are_not_partner_parity_requirements` test in `goal2723_v2_5_tiered_benchmark_manifest_test.py` correctly asserts these invariants.

---

## Q5 — Highest-Priority Next Risks

**Risk 1 — Missing v2.4 same-contract opponent for RayDB (highest priority)**

The current comparison is prepared v2.5 vs unprepared v2.5. This is a valid internal measurement, and the reports correctly scope it as such. However, the manifest's `next_action` for raydb_style is: "add v2.4 same-contract opponent before any public parity wording." Until the v2.4 prepared path (same fixture, same scene reuse, different continuation) is run on the same pod, the published speedups cannot be cited publicly. This gate must close before any parity wording moves beyond internal scope.

**Risk 2 — Transfer measurement gap**

All neutral buffer transfer statuses are `"borrowed_device_pointer_unmeasured"`. Same-pointer evidence at the torch carrier level is not equivalent to a measured transfer record in the neutral buffer seam. Any reduced-copy or zero-copy claim requires upgrading these to measured entries with explicit per-column copy accounting.

**Risk 3 — Tier B blocking operations**

`grouped_components_or_fallback`, `bounded_topk_or_ranked_summary`, `grouped_vector_sum`, and `grouped_argmax_witness` are absent from the Triton preview surface. Progress on rt_dbscan, rtnn, barnes_hut, and hausdorff_xhd is blocked until these operations are defined, previewed, and added to `V2_5_PARTNER_PREVIEW_KERNEL_OPERATIONS`. The migration plan validator (`validate_v2_5_triton_benchmark_app_migration_plan`) will correctly reject these apps if they are added with missing operations.

**Risk 4 — triangle_counting streaming and OOM gap**

triangle_counting is Tier A but its `canonical_harness_status` is `"needs_single_rerunnable_harness"` and the next action explicitly names a streaming/OOM gap at paper-size row counts. This app cannot advance to the same evidence level as raydb_style until both gaps close.

**Risk 5 — Harness consolidation for Tier A/B apps**

Several apps (rtnn, barnes_hut, rt_dbscan) have `canonical_harness_status` set to `"needs_live_harness_not_frozen_evidence_wrapper"` or similar. Any attempt to collect new pod evidence for these apps will fail without a canonical harness that can be re-run. This is a prerequisite blocker for all non-RayDB Tier A/B progress.

---

## Summary

| Question | Finding |
|---|---|
| Prepared path engine boundary | Clean — no RayDB logic in native code |
| Pod artifact consistency | Consistent — numbers match, physics coherent |
| Claim boundaries | Conservative throughout — no overreach found |
| Tiered manifest category errors | Prevented — validator is machine-checkable |
| Highest next risks | v2.4 opponent gap, transfer measurement, Tier B ops, triangle_counting OOM, harness gaps |

**Verdict: `accept-with-boundary`**

The implementation is correct and the boundary discipline is well-maintained. The `accept-with-boundary` qualifier records that the comparison evidence is currently prepared-v2.5 vs unprepared-v2.5 only. The boundary lifts to a full accept for public parity wording once the v2.4 same-contract opponent evidence is added on the same hardware and the transfer statuses are measured.

This review is independent of Codex. It was performed by Claude (claude-sonnet-4-6) on 2026-05-30 by direct inspection of source files and pod artifacts.
