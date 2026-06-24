# Call For Review: Phoenix V3 Core Gaps, Current Status, And Next Work

Date: 2026-06-22
Status: `review_request_not_release_authorization`
Scope: Phoenix V3 only. V4, C ABI, embedding, SDK, and multi-language host work are out of scope.

## Executive Summary For External Reviewer

Phoenix V3 is not release-ready. The current recovery work has useful generic
runtime fixes, but the serious same-hardware V2.14-vs-current-V3 paired run
does not prove a major-version performance release:

```text
overall same-metric geomean: 1.012x V3 vs V2.14
apps with geomean >1.05x: 1 / 10
apps with geomean <0.95x: 2 / 10
release_consideration_eligible: false
```

The four blockers to review are:

1. The execution graph exists as design/skeleton work, but it is not yet the
   productized default execution path.
2. Device-resident/no-hidden-copy behavior exists as evidence windows and
   metadata, but it is not yet a stable V3 capability.
3. Fused/partner continuation work exists, but too much of it is route-shaped
   instead of a coherent generic continuation layer.
4. Performance evidence is not yet broad or material enough for a V3 major
   release over V2.x.

The requested review is therefore not "is the prose good?" and not "can one
row be made faster?" The requested review is: is the proposed Phoenix path the
right way to rebuild V3 as a serious RTRDL language/runtime performance release?

## Post-Review Update

Claude's recorded external review has now been ingested under the bounded
protocol:

```text
review: docs/reviews/claude_phoenix_v3_external_review_2026-06-22.md
intake: docs/rebuild/v3/phoenix_v3_core_gaps_external_verdict_intake_2026-06-22.json
status_line: external_verdict_obtained_claude_approve_blocked_not_release
verdict: approve_blocked_not_release
release_authorized: false
direction: continue with redirect to Gap 1
```

Actions taken after that review:

- M1: added a minimal generic prepared execution/session runner.
- M1.1: bound the runner to the generic fixed-radius self-query primitive.
- M1.2: wired the runner-backed fixed-radius self-query route into the real
  CuPy grouped-stream probe route.
- M1.2 pod A/B: same RTX 4000 Ada evidence preserved signatures and confirmed
  runner metadata, but measured `0.9979x` geomean before/after speedup. This is
  neutral route evidence, not performance progress.

Current interpretation:

```text
Gap 1 route visibility: improved
material speedup: not proven
release_authorized: false
full_all_app_rerun_authorized: false
next: route a second Set-A family or remove reusable runner overhead
```

## Reviewer Task

Please perform a critical external review of the current Phoenix V3 recovery
direction. The core question is not whether a few benchmark rows can be made
faster. The core question is whether the current work is rebuilding V3 as a
serious RTRDL language/runtime performance release rather than as benchmark-app
tuning.

Please return:

1. A verdict: continue this V3 recovery path, redirect it, or stop and redesign.
2. The highest-severity technical gaps.
3. The next 3-5 engineering actions that are genuinely language/runtime work.
4. Any actions that look like app-specific tuning and should be rejected.
5. Whether the proposed next performance evidence would be enough to justify
   another all-app V2.14 vs V3 run.

Treat a positive review as authorization to continue the recovery direction,
not as release authorization. Treat a negative review as a design correction
input before more pod time is spent.

Do not approve release wording. Do not approve broad V3-over-V2.x speedup
wording. Treat V3 as blocked unless material, same-hardware, all-app evidence
proves otherwise.

## Current V3 Decision State

Phoenix V3 is still blocked:

```text
status: redo_required
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
```

The controlling reason is simple:

```text
V3 major release requires broad, material V2.x performance superiority.
The benchmark apps are not the product; they are stress tests for reusable
RTRDL runtime/language capabilities.
```

The latest serious same-RT-hardware V2.14 vs current Phoenix V3 run failed the
major-version performance bar:

```text
run_id: phoenix_v3_serious_v2x_paired_20260622_074100
hardware: NVIDIA RTX 4000 Ada Generation, driver 550.127.05, 20475 MiB
same_metric_comparison_count: 52
V3 faster by >5%: 12
Within +/-5%: 35
V3 slower by >5%: 5
Geomean V3 speedup vs V2.14: 1.012x
actual_app_geomean_wins_gt_1_05x: 1
actual_app_geomean_regressions_lt_0_95x: 2
release_consideration_eligible: false
```

This is not a responsible major-version performance result. A 1.01x-style
aggregate cannot define V3.

## The Four Core Gaps

### Gap 1: Execution graph is not yet the productized execution path

The original V3 plan defined an app-agnostic execution graph, prepared graph
plans, residency, streams, phase accounting, and partner nodes as the V3
architecture. The current source tree contains this design language, but it is
not yet the default runtime performance path.

Evidence:

- `src/rtdsl/v3_0_execution_graph.py` still declares
  `V3_EXECUTION_GRAPH_STATUS = "m2_no_execution_skeleton"`.
- `src/rtdsl/v3_0_prepared_graph_chunk_executor.py` contains planning and
  adoption-gate contracts, but its plans explicitly report
  `runtime_executed: False`.
- Existing high-performance pieces are spread across older surfaces such as
  `v2_8_fixed_radius_graph_component_front_door.py`,
  `partner_adapters.py`, `prepared_session_residency.py`, and app modes.

Reviewer question: Is the right next V3 engineering target a small productized
prepared execution layer that routes existing generic primitives through a
single reusable graph/session path?

### Gap 2: Device-resident and no-hidden-copy evidence is not yet a stable V3 capability

There are same-stream/no-hidden-copy evidence scripts and metadata, but this is
not yet a reliable user-facing runtime rule. The code can prove some windows,
but V3 does not yet make "avoid host materialization in the hot path" a default
execution discipline.

Evidence:

- Same-stream and no-hidden-copy work exists in M10-M17 lineage and in
  `PreparedOptixCupyRadiusGraphGroupedStreamContinuation3D.run_same_stream_evidence`.
- Metadata often correctly blocks `true_zero_copy_authorized`, even when device
  columns are used.
- Some benchmark rows still use host row materialization or host scalar
  materialization in their primary route.

Reviewer question: What minimal runtime contract would make device residency
real enough for V3 without drifting into V4 zero-copy/embed scope?

### Gap 3: Fused continuation exists, but too much of it is route-shaped

The project has real continuation work: grouped reductions, component union,
ranked summary, frontier/vector accumulation, topology streams, AABB candidate
streams, and partner continuations. But too much of it remains exposed as
route-specific or app-mode-specific code rather than as a coherent V3
continuation layer.

Evidence:

- Strong row-scoped evidence exists for grouped reduction, AABB candidate
  stream, RTDBSCAN component union, Triangle prepared graph chunk, RTNN ranked
  summary, Barnes-Hut fused vector accumulation, Hausdorff threshold summary,
  Robot collision flag stream, and Spatial topology-stream rows.
- Those rows are internal evidence, not a major release.
- Several routes work because a benchmark mode chooses a specific pipeline,
  not because V3 provides a general continuation planner/executor.

Reviewer question: Which continuation families should be promoted into a small
V3 generic runtime core first, and which should remain internal evidence?

### Gap 4: The performance evidence is not yet broad or material

The 13-row Phoenix surface shows that RTDL has valuable primitives. It does not
prove that V3 broadly improves over V2.14. The serious same-hardware paired run
settled that: current V3 is mostly parity with selected wins and some
regressions.

Evidence:

- Overall V3 vs V2.14 geomean: `1.012x`.
- Only 1 of 10 app geomeans cleared `>1.05x`.
- Several worst rows were caused by generic runtime overheads, repeated symbol
  lookup, repeated prepare/packing, row materialization, or mismatched
  evaluation emphasis.

Reviewer question: What performance bar should be required before a new
all-app paired run is worth the pod time?

## What Has Been Fixed Since The Failed Serious Run

These are focused generic runtime fixes. None authorizes release.

### 1. Barnes-Hut fixed-radius prepared OptiX symbol/library cache

Files:

- `src/rtdsl/optix_runtime.py`
- `tests/goal757_prepared_optix_fixed_radius_count_test.py`

Evidence:

- `docs/reports/phoenix_v3_barnes_hut_symbol_cache_focused_evidence_2026-06-22.md`

Result:

```text
Largest Barnes-Hut prepared OptiX regressions recovered from about 0.622x/0.591x
to about 0.999x/1.038x vs V2.14 on the same RTX 4000 Ada pod.
```

Interpretation: useful generic runtime regression repair, not V3 release.

### 2. LibRTS/AABB generic Embree prepared query count cache

Files:

- `src/rtdsl/embree_runtime.py`
- `src/rtdsl/aabb_index.py`
- `tests/v3_phoenix_aabb_prepared_query_cache_test.py`

Evidence:

- `docs/reports/phoenix_v3_librts_aabb_count_cache_focused_evidence_2026-06-22.md`

Result:

```text
Embree count-only focused rows recovered in repeat=3 and repeat=9 runs.
OptiX AABB remains unstable/inconclusive and needs separate route analysis.
```

Interpretation: generic prepared-handle/query-cache cleanup, not release.

### 3. RTNN prepared neighbor symbol cache

Files:

- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/embree_runtime.py`
- `tests/goal4351_embree_rtnn_ranked_summary_parity_test.py`

Evidence:

- `docs/reports/phoenix_v3_rtnn_neighbor_symbol_cache_focused_evidence_2026-06-22.md`

Result:

```text
12-row RTNN focused geomean patched V3 vs V2.14: 1.001x.
```

Interpretation: validated hygiene only. This direction is not a material V3
performance rescue.

### 4. Broader fixed-radius prepared count-threshold symbol cache

Files:

- `src/rtdsl/embree_runtime.py`
- `src/rtdsl/optix_runtime.py`
- `tests/v3_phoenix_prepared_fixed_radius_symbol_cache_test.py`

Local validation:

```text
py_compile optix_runtime.py and embree_runtime.py: OK
targeted prepared fixed-radius tests: 4 OK
combined targeted runtime tests: 33 OK, 2 skipped
release/readiness/wording gates: 11 OK
remote targeted tests: 27 OK
```

Latest focused pod evidence:

```text
run_id: phoenix_v3_fixed_radius_symbol_cache_focused_20260622_144922
remote_run_dir: /root/rtdl_v3_rebuild_20260620/phoenix_v3_fixed_radius_symbol_cache_focused_20260622_144922
local_artifact_dir: docs/rebuild/v3/evidence/phoenix_v3_fixed_radius_symbol_cache_focused_20260622_144922/
report: docs/reports/phoenix_v3_fixed_radius_symbol_cache_focused_evidence_2026-06-22.md
status at latest observation: completed, copied locally, and analyzed
result: 17 same-metric rows; geomean 1.062x; 4 >1.05x, 12 within +/-5%, 1 <0.95x
classification: useful generic runtime cleanup, not release proof
```

Important: this focused run does not include the later local self-query refresh
patch below. Do not mix the two evidence packets.

## Current Local Patch Now Pod-Validated As Contract Cleanup

### Generic fixed-radius graph self-query refresh

Files:

- `src/rtdsl/partner_adapters.py`
- `src/rtdsl/optix_runtime.py`
- `tests/goal4486_rt_dbscan_self_count_threshold_test.py`
- `tests/v3_phoenix_fixed_radius_graph_self_query_refresh_test.py`

Change:

`PreparedOptixCupyRadiusGraphGroupedStreamContinuation3D`,
`run_same_stream_evidence`, and
`PreparedOptixNumbaRadiusGraphGroupedStreamContinuation3D._refresh_core_flags`
now call:

```text
fixed_radius_count_threshold_3d_optix_prepared_self_partner_device_columns
```

instead of the host-query path:

```text
fixed_radius_count_threshold_3d_optix_prepared_partner_device_columns(..., point_rows, ...)
```

Why this is V3 runtime work:

- It applies to generic self-query fixed-radius graph/component continuation.
- It avoids reusing the same search points as host query input when the native
  prepared scene already has a device search buffer.
- It does not add DBSCAN-specific native ABI or app semantics.
- It connects an existing generic self-query primitive to an existing generic
  grouped-stream continuation handle.

Pod evidence:

```text
report: docs/reports/phoenix_v3_fixed_radius_graph_self_query_refresh_focused_evidence_2026-06-22.md
run_id: phoenix_v3_self_query_refresh_ab_20260622_153305
local_artifact_dir: docs/rebuild/v3/evidence/phoenix_v3_self_query_refresh_ab_20260622_153305/
classification: focused_generic_runtime_contract_fix_validated_no_material_speedup
CuPy A/B rows: 3
signature mismatches: 0
geomean after-vs-before speedup: 0.998x
metadata result:
  adapter changed to fixed_radius_count_threshold_3d_optix_prepared_self_partner_device_columns
  transfer_mode changed to prepared_device_search_points_self_count_threshold_columns
  host_query_point_repack_avoided: true
  host_query_point_upload_avoided: true
Numba status:
  blocked by CUDA_ERROR_UNSUPPORTED_PTX_VERSION on this pod
release_authorized: false
```

Validation:

```text
py -3 -m py_compile src/rtdsl/partner_adapters.py: OK
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_fixed_radius_graph_self_query_refresh_test \
  tests.goal4486_rt_dbscan_self_count_threshold_test \
  tests.v3_phoenix_prepared_fixed_radius_symbol_cache_test \
  tests.goal4347_rt_dbscan_embree_numba_fair_mode_test \
  tests.goal4351_embree_rtnn_ranked_summary_parity_test

17 tests OK

PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_major_performance_mandate_gate_test \
  tests.v3_phoenix_release_readiness_gate_test \
  tests.v3_phoenix_serious_v2x_paired_analysis_test \
  tests.v3_release_wording_gate_test

11 tests OK

remote targeted tests after sync:
  11 tests OK
```

Reviewer question: Should this be kept as a V3 device-residency/contract fix
even though it is performance-neutral, and should the next V3 work move to a
dominant reusable hot path instead of additional count-refresh cleanup?

## Current Interpretation Of The Main Problem

The main problem is not "RTDBSCAN is slow" or "Barnes-Hut needs tuning." The
main problem is:

```text
V3 has many generic high-performance ingredients, but it has not yet unified
them into a default, productized execution path that broadly beats V2.14.
```

Benchmark apps should be used only as probes. They must not become the
optimization target. If a change cannot be expressed as one of these reusable
runtime capabilities, it should not count as Phoenix V3 core work:

- prepared execution/session reuse;
- fixed-radius self-query device-column execution;
- typed stream/device-resident result values;
- grouped reduction or component-union continuation;
- partner continuation with explicit partner and phase accounting;
- no-hidden-copy/same-stream evidence windows;
- prepared graph/chunk execution where runtime actually executes, not just
  plans.

## Expected Next Work

### Step 1: Finish intake of the fixed-radius symbol-cache focused pod run

Completed:

1. Verify the local copied summaries and hashes.
2. Parse same-case V2.14 vs current rows.
3. Write:
   `docs/reports/phoenix_v3_fixed_radius_symbol_cache_focused_evidence_2026-06-22.md`
4. Classify honestly as useful focused generic runtime cleanup, not release
   proof.

Decision: stop spending V3 time on pure symbol-cache tweaks unless a new
serious row proves the same overhead class blocks a reusable runtime primitive.

### Step 2: Stop treating self-query refresh as a speed path

Completed A/B shows correct metadata and unchanged signatures, but no material
speedup. Keep it as contract cleanup only. The next work should target a
dominant reusable runtime hot path; do not keep polishing count-refresh overhead
unless a serious row proves it dominates.

### Step 3: Promote only a small set of reusable runtime capabilities

Do not create app-specific fast paths. The likely next generic candidates are:

1. Prepared execution/session runner that actually executes selected existing
   generic primitives, rather than only recording metadata.
2. Fixed-radius self-query device-column path as a first-class primitive.
3. Continuation planner for component union / grouped reductions over typed
   streams.
4. Device-resident row/status accounting that avoids mandatory host row
   materialization in primary metrics.

The expected P0 engineering direction is to pick one dominant reusable hot path,
land it as a runtime primitive, prove it with focused pod evidence, and only
then consider another all-app paired run. Current candidates are:

1. Prepared execution/session runner for existing generic primitives.
2. Dominant grouped/component-union continuation hot path shared by
   fixed-radius graph workloads.
3. Generic AABB/topology/query-handle overhead reduction where exactness and
   author-code comparisons remain honest.

### Step 4: Rerun all-app serious V2.14 vs V3 only after material generic fixes

Do not burn pod time repeating the full suite after tiny changes. A full rerun
is justified only after focused evidence shows at least one generic runtime fix
materially affects multiple benchmark probes or one major common primitive
family.

The existing major-version release bar remains:

```text
overall_geomean_v3_speedup_vs_v2 >= 1.20x for release consideration
at least 8 of 10 app geomeans > 1.05x
no app geomean < 0.95x without accepted explanation
every surprising row explained in user language
```

### Step 5: External review before any release claim

Closure requires Codex plus at least one external AI review, preferably Claude
or Gemini, following:

```text
docs/rebuild/v3/phoenix_v3_bounded_external_review_protocol_2026-06-22.md
```

External AI unavailability is not release approval. Record the failure and
continue non-release engineering work.

## Specific Review Questions

1. Are the four gaps above the correct blockers for V3 as an RTRDL
   language/runtime performance release?
2. Is the current local self-query refresh patch generic enough for V3, or is
   it still too route-specific?
3. Should the existing execution-graph layer be turned into an executing
   prepared-session runner now, or should V3 first harden one primitive family
   such as fixed-radius self-query typed streams?
4. Which benchmark rows should be treated as negative controls because they
   intentionally materialize rows, such as RTDBSCAN Embree neighbor rows?
5. What focused pod evidence would be sufficient before another all-app V2.14
   vs current run?
6. Are there any V3 actions in the current plan that smell like app development
   rather than language/runtime design?
7. Should any of the 13 old M7 rows be demoted further because they distract
   from the major-version performance mandate?

## Non-Claims

This packet does not claim:

- V3 is done.
- V3 is release-ready.
- V3 broadly beats V2.x.
- RTDL broadly beats Embree, OptiX author code, CUDA, CuPy, or Numba.
- V3 has true zero-copy.
- V3 has automatic optimal backend or partner selection.
- V4/C ABI/embedding belongs inside Phoenix V3.

## Goal-Level Decision Audit

Decision: ask for critical review of the V3 recovery direction before treating
the current fixes as V3 progress.

1. Was I foolish? The prior V3 process was foolish when it treated scoped row
   evidence and documentation cleanup as enough for a major language/runtime
   release.
2. What actions made it foolish? It mixed benchmark-row success with product
   readiness, accepted 1.01x-style aggregate performance as if it could be
   polished into a major release, and let route-specific evidence obscure the
   missing execution layer.
3. Was another path available? Yes. The correct path was to enforce broad
   V2.x performance superiority and require every optimization to land as a
   reusable runtime capability.
4. Can we now try a different path that solves the problem? Yes. The current
   path blocks release, uses benchmark apps only as probes, promotes only
   generic runtime capabilities, and requires focused pod evidence before any
   all-app rerun or public claim.
