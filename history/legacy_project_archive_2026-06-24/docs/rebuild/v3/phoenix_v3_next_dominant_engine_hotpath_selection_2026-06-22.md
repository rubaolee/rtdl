# Phoenix V3 Next Dominant Engine Hotpath Selection

Date: 2026-06-22
Status: `active_p0_prepared_execution_session_runner_not_release`
Scope: Phoenix V3 only. V4, C ABI, embedding, SDK, and multi-language host
work are out of scope.

This is not a release report. It selects the next Phoenix V3 engineering
target after the serious same-RT-hardware V2.14 vs current V3 paired run failed
the major-version bar.

## Current Hard Facts

Phoenix V3 remains `redo_required`:

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
full_all_app_rerun_authorized_now: false
```

The serious paired run is the controlling evidence:

```text
evidence: docs/rebuild/v3/evidence/phoenix_v3_serious_v2x_paired_20260622_074100/summary.json
same_metric_comparison_count: 52
overall_geomean_v3_speedup_vs_v2_14: 1.0117790403434224
apps_with_geomean_gt_1_05: 1
apps_with_geomean_lt_0_95: 2
release_consideration_eligible: false
```

The old `phoenix_v3_next_generic_engine_work_queue_2026-06-21.json` says the
old row-promotion queue is closed. That is historical truth for the scoped
13-row surface. It does not answer the Phoenix redo question after the
all-app V2.14 paired run failed.

## External Review Alignment

Claude's recorded external review is now machine-ingested:

```text
review: docs/reviews/claude_phoenix_v3_external_review_2026-06-22.md
intake: docs/rebuild/v3/phoenix_v3_core_gaps_external_verdict_intake_2026-06-22.json
status_line: external_verdict_obtained_claude_approve_blocked_not_release
verdict: approve_blocked_not_release
direction_decision: continue_with_redirect
release_authorized: false
major_version_mandate_overridden: false
```

Accepted interpretation: Gap 1 is the critical path. Gaps 2-4 are downstream
symptoms. Continue non-release engineering, but redirect effort away from cache
hygiene and into a productized execution path that actually executes.

Claude also proposed a Set A / Set B replacement scorecard:

```text
proposal: docs/reviews/phoenix_v3_set_a_set_b_release_bar_proposal_2026-06-22.md
status: proposal_only_not_authorization
release_gate_changed_by_this_file: false
```

Use the proposal as the next measurement design unless the release owner
rejects it: freeze Set A residency/multi-phase probes and Set B
ceiling/materializing controls before the run; Set A wins must come from the
productized execution path, not from caches; Set B targets parity with
explanation.

## Selected P0

Select:

```text
id: prepared_execution_session_runner
generic_capability: productized_prepared_execution_session
priority: P0
```

Decision:

Build a small productized prepared execution/session runner that actually
routes selected existing generic primitives through one reusable runtime path
with explicit backend, explicit partner, phase accounting, residency metadata,
and no release claims.

Why this first:

- It is the most reusable V3-shaped fix: the same layer can serve
  fixed-radius threshold/self-query, AABB native query handles, grouped
  reduction, topology streams, and prepared graph/chunk rows.
- It addresses Gap 1 directly: execution graph and prepared graph code still
  mostly plan or validate, while the user-visible fast routes live in scattered
  benchmark/app surfaces.
- It gives V3 a language/runtime surface instead of another benchmark-row
  patch.
- It creates a single place to enforce explicit backend/partner selection,
  cold/hot phase accounting, no-hidden-copy metadata, and claim boundaries.

## Current Code Evidence

- `src/rtdsl/v3_0_execution_graph.py`: `V3_EXECUTION_GRAPH_STATUS` is
  `m2_no_execution_skeleton`; prepared graph metadata reports `executes:
  false`.
- `src/rtdsl/v3_0_prepared_graph_chunk_executor.py`: the chunk executor is a
  contract/adoption-gate surface; several readiness paths explicitly report
  `runtime_executed: false`.
- `src/rtdsl/prepared_execution.py`: prepared execution reporting and phase
  contracts exist, but they are reporting surfaces rather than the default
  runtime runner.
- `src/rtdsl/prepared_session_residency.py`: explicit prepared-session
  cache/residency contracts exist and forbid automatic partner/backend
  selection, but they are not yet the unified execution path for V3
  primitives.

## First Primitive Families To Route

### fixed_radius_count_threshold_self_query

Evidence apps:

- `hausdorff_xhd`
- `rt_dbscan`
- `barnes_hut`

Reason: common fixed-radius runtime code already has focused symbol-cache and
self-query contract evidence. The self-query refresh proved metadata
correctness but no material speedup, so the next step must target runner-level
reuse rather than more count-refresh polishing.

Evidence:

- `docs/reports/phoenix_v3_fixed_radius_symbol_cache_focused_evidence_2026-06-22.md`
- `docs/reports/phoenix_v3_fixed_radius_graph_self_query_refresh_focused_evidence_2026-06-22.md`

### aabb_index_query_2d_native_query_handle

Evidence apps:

- `librts_spatial_index`
- `contact_manifold`

Reason: AABB native query-handle work is a proven generic prepared-session
primitive with material row-scoped evidence, but OptiX prepare and route-fit
disclosures must remain explicit.

Evidence:

- `docs/rebuild/v3/phoenix_v3_aabb_native_query_handle_review_gate_2026-06-21.md`
- `docs/reports/phoenix_v3_librts_aabb_count_cache_focused_evidence_2026-06-22.md`

### grouped_reduction_and_component_union_continuation

Evidence apps:

- `raydb_style`
- `rt_dbscan`
- `triangle_counting`

Reason: the old M0-M149 work contains real grouped and chunked continuation
pieces. V3 needs a small generic continuation runner before any app-shaped
union or reduction row can count as language/runtime progress. RayDB
grouped_reduction and RTDBSCAN component_union are now redo-closed as retained
reusable evidence, so new app-specific variants do not count unless they land
in a shared runner or continuation primitive.

Evidence:

- `docs/rebuild/v3/phoenix_v3_raydb_grouped_reduction_redo_alignment_2026-06-22.md`
- `docs/rebuild/v3/phoenix_v3_rtdbscan_component_union_redo_alignment_2026-06-22.md`
- `docs/rebuild/v3/phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_2026-06-21.md`
- `docs/rebuild/v3/phoenix_v3_rtdbscan_component_signature_optimized_rtx_evidence_2026-06-21.md`
- `docs/rebuild/v3/phoenix_v3_triangle_prepared_graph_80000_m7_final_review_packet_2026-06-21.md`

### point_location_topology_stream

Evidence apps:

- `spatial_rayjoin`

Reason: Spatial topology_stream is now redo-closed as exactly one internal
`point_location_topology_stream` row. It can count as future Set-A work only if
the productized topology/point-location execution path is the measured source
of the win. Public RayJoin author comparisons require separate result-count and
paper-scope proof.

Evidence:

- `docs/rebuild/v3/phoenix_v3_spatial_topology_stream_redo_alignment_2026-06-22.md`
- `docs/rebuild/v3/phoenix_v3_spatial_relation_status_squared_boundary_candidate_2026-06-21.json`
- `docs/rebuild/v3/phoenix_v3_spatial_rayjoin_hotpath_probe_no_go_2026-06-21.json`

## Deliverables

M1:

A minimal runner contract and implementation for one selected primitive family
that records explicit backend, explicit partner, prepared-session key,
cold/hot phases, residency, materialization flags, correctness status, and
release/public-claim flags all false.

Current M1 status:

```text
report: docs/reports/phoenix_v3_prepared_execution_session_runner_m1_smoke_2026-06-22.md
status: m1_generic_runner_smoke_validated_not_release
code: src/rtdsl/prepared_execution.py
test: tests/v3_phoenix_prepared_execution_session_runner_test.py
boundary: generic runner exists; no pod performance evidence
```

Current M1.1 status:

```text
report: docs/reports/phoenix_v3_fixed_radius_self_query_runner_binding_m1_1_2026-06-22.md
status: m1_1_fixed_radius_self_query_runner_binding_validated_not_release
code: src/rtdsl/prepared_execution.py
test: tests/v3_phoenix_prepared_execution_session_runner_test.py
primitive_family: fixed_radius_count_threshold_self_query
adapter: fixed_radius_count_threshold_3d_optix_prepared_self_partner_device_columns
runtime_executed: true in local contract test
boundary: not wired into a real benchmark route yet; no pod performance evidence
```

Current M1.2 status:

```text
report: docs/reports/phoenix_v3_grouped_stream_runner_route_m1_2_2026-06-22.md
status: m1_2_runner_backed_fixed_radius_probe_route_validated_not_release
probe_route: PreparedOptixCupyRadiusGraphGroupedStreamContinuation3D.run
primitive_family: fixed_radius_count_threshold_self_query
productized_execution_path_visible_in_route: true
runner_metadata_expected:
  - prepared_execution_session_runner_used
  - prepared_execution_session_runner_metadata
  - productized_execution_path
  - core_flag_refresh_runtime_executed
boundary: pod A/B exists but is neutral; no release/public/all-app authorization
```

Current M1.2 pod A/B status:

```text
report: docs/reports/phoenix_v3_grouped_stream_runner_route_pod_ab_2026-06-22.md
status: m1_2_runner_route_pod_ab_neutral_not_release
geomean_before_over_after_speedup: 0.9978812011247638
material_speedup_observed: false
interpretation: runner-backed route executes and preserves signatures, but is not faster
```

Current M2 contract status:

```text
report: docs/reports/phoenix_v3_aabb_native_query_handle_runner_route_m2_2026-06-22.md
status: m2_aabb_native_query_handle_runner_contract_validated_not_release
primitive_family: aabb_index_query_2d_native_query_handle
helper: run_aabb_index_query_2d_range_intersection_prepared_session
runtime_executed: true in local contract test
set_a_probe_candidate: true
productized_execution_path_visible_in_helper: true
pod_performance_evidence: true through M2.1 route rerun below
material_speedup_observed: true in focused M2.1 pod A/B
boundary: second Set-A family routed through runner at contract level; M2.1
  below records route wiring and focused pod evidence. This still does not
  authorize release, public speedup, broad V3-over-V2, or all-app rerun claims.
```

Current M2.1 route status:

```text
status: m2_1_aabb_runner_backed_contact_route_validated_not_release
route: examples/current/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py::aabb_broadphase_witness_rows
route_test: tests/v3_phoenix_aabb_prepare_reuse_pod_runner_test.py::test_contact_aabb_route_uses_productized_prepared_session_runner
productized_execution_path_visible_in_route: true
runtime_executed_count_in_route_test: 3
cache_hit_count_in_route_test: 2
boundary: route wiring is validated; existing 2026-06-21 AABB pod rows predate
  this route binding and must not be reinterpreted as runner-backed evidence
  without a focused rerun
```

Current M2.1 pod A/B status:

```text
status: m2_1_aabb_runner_route_pod_ab_pending_2ai_not_m7
report: docs/reports/phoenix_v3_aabb_runner_route_m2_1_pod_ab_2026-06-22.md
call_for_review: docs/reviews/call_for_review_phoenix_v3_aabb_runner_route_m2_1_pod_ab_2026-06-22.md
evidence: docs/rebuild/v3/evidence/phoenix_v3_aabb_runner_m2_1_pod_ab_20260622_180241/summary.json
productized_runner_visible_for_prepared_backends: true
optix_over_embree_cold_plus_collect_wall_speedup: 1.34595769645315
optix_over_embree_query_total_speedup: 1.73787303873785
runtime_executed_count: embree=50 optix=50
cache_hit_count: embree=49 optix=49
m7_reopen_candidate_pending_2ai_review: true
boundary: positive focused Set-A evidence pending external review; no release,
  M7, public-speedup, broad V3-over-V2, or all-app authorization
```

Current RTDBSCAN/component-union runner-contract status:

```text
report: docs/reports/phoenix_v3_rtdbscan_component_signature_runner_route_m3_2026-06-22.md
route_report: docs/reports/phoenix_v3_rtdbscan_component_signature_runner_route_m3_1_2026-06-22.md
status: rtdbscan_component_signature_runner_route_wired_local_validated_not_release
helper: run_radius_graph_component_signature_3d_prepared_session
primitive_family: fixed_radius_graph_component_signature
continuation_contract: grouped_stream_component_size_signature_3d
productized_execution_path: prepared_execution_session_runner
runtime_executed: true in local contract test
set_a_probe_candidate: true
wired_into_real_benchmark_route: true
route: examples/current/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py::optix_rt_core_grouped_stream_numba_column_signature_3d
route_test: tests.v3_phoenix_rtdbscan_component_signature_optimization_test
pod_performance_evidence: false
material_speedup_observed: false
boundary: route wiring and fake-runner local contract only; not a second Set-A
  material win until focused pod A/B proves it
```

M2:

Route a second Set-A family through the runner, preferably AABB native query
handle, grouped reduction/component continuation, or topology_stream, or remove
measurable runner-level overhead across multiple runner-backed routes. Repeat
on at least two Set-A probes before any all-app rerun.

Current selected next route:

```text
route_target: RTDBSCAN component-signature / component-union continuation
next_action: run a focused same-hardware pod A/B for the existing RTDBSCAN
  benchmark route now wired through the app-agnostic component-signature helper
  without adding RTDBSCAN-specific native engine logic
pod_trigger: focused same-hardware A/B only after route metadata proves
  productized_execution_path: prepared_execution_session_runner
```

M3:

Freeze the Set A / Set B classification and only then preregister the next
all-app V2.14 vs current V3 rerun if focused evidence is material.

## Rejected Paths

- More symbol-cache polishing: useful hygiene, but focused results were
  1.062x on 17 rows for broad fixed-radius and 1.001x for RTNN.
- Self-query count-refresh speed claim: reject as speed path because the A/B
  was 0.998x geomean after-vs-before.
- App-specific native engine shortcuts: reject because benchmark apps are
  probes, not the V3 product.
- RayDB-specific grouped_sum variants: reject unless the work lands in shared
  grouped_reduction, component continuation, or productized runner code.
- Spatial public RayJoin speedup wording: reject until author result-count and
  paper-scope proof exist. The redo alignment keeps one internal
  point_location_topology_stream row; it does not authorize public Spatial or
  `RTDL beats RayJoin` wording.
- Repeat full all-app now: reject for now because only one runner-backed Set-A
  route has material focused pod evidence; the protocol requires at least two
  Set-A probes before spending all-app pod time.

## Pod Trigger For Next Full Run

Before another full all-app V2.14 vs current V3 run:

- one selected P0 runner primitive must land as generic runtime code;
- `runtime_executed: True` must be shown on at least two Set-A probes;
- focused pod A/B must show material improvement or remove a dominant overhead
  class across more than one Set-A probe;
- Set A / Set B classification must be frozen before the run;
- correctness signatures or oracles must remain unchanged;
- claim-boundary tests must pass;
- external review packet must be prepared if the result is proposed for M7.

The release bar remains:

```text
overall_geomean_v3_speedup_vs_v2_14 >= 1.20x for release consideration
app_geomean_wins_gt_1_05 >= 8 of 10
app_geomean_regressions_lt_0_95 == 0 without accepted explanation
surprising rows must have user-readable explanations
```

## Non-Claims

This selection does not claim:

- V3 is done.
- V3 is release-ready.
- Public speedup wording is authorized.
- Broad V3-over-V2 wording is authorized.
- True zero-copy wording is authorized.
- V4, C ABI, embedding, SDK, or multi-language host scope belongs in Phoenix
  V3.
- App-specific native engine shortcuts count as Phoenix V3 core progress.

## Goal-Level Decision Audit

Decision: Select `prepared_execution_session_runner` as the next dominant
Phoenix V3 P0 hot path, and keep release blocked.

1. Was I foolish?
   No for this decision. It uses the serious paired failure and focused
   follow-up evidence to choose a reusable runtime layer instead of chasing
   another app row.
2. If yes, what actions made the decision foolish?
   The foolish action would be to treat the old closed 13-row queue as proof
   that V3 has no engine work left, or to keep polishing symbol lookup and
   self-query count refresh after evidence showed no major release-scale gain.
3. Was there another path that would have avoided getting stuck on that idea?
   Continue app-specific tuning, rerun the full benchmark immediately, or
   promote scoped rows. Those paths would repeat the earlier failure:
   impressive local facts without a user-responsible V3 runtime.
4. Can I now try a different path that actually solves the problem?
   Yes. Use the existing M0-M149 prepared/session/continuation work to build
   one small productized prepared execution/session runner, prove it with
   focused pod evidence, and only then consider a new all-app paired run.
