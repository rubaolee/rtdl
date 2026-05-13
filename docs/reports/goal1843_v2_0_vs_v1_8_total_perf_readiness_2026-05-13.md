# Goal1843 v2.0 vs v1.8 Total Performance Readiness

Date: 2026-05-13
Status: `planning-evidence`

## Purpose

This report answers how far RTDL is from a full v2.0-vs-v1.8 performance
comparison across the public app surface for the two active engines, Embree and
OptiX.

It does not report new timings and does not authorize v2.0 release wording.

## Short Answer

RTDL is not yet ready for a total v2.0-vs-v1.8 performance table for all apps.

The v1.8 side is mostly ready:

- Embree has a complete same-surface app-wall column through Goal1756.
- OptiX has broad same-contract app/subpath ratios through Goal1750.

The v2.0 side is only partially born:

- Goal1838 proves one real OptiX partner zero-copy slice:
  Torch/CuPy CUDA input columns plus Torch/CuPy CUDA output flags for the
  prepared 2-D ray/triangle any-hit primitive.
- No public app has yet been rewritten end-to-end as a v2.0 partner app.
- No all-app v2.0 partner timing harness exists yet.

## Current Evidence Inventory

| Evidence | Scope | Status | Release use |
| --- | --- | --- | --- |
| Goal1756 | v1.8/current vs v1.0 Embree, same app command wall-clock, 16 rows | complete internal evidence | not public speedup wording |
| Goal1750 | v1.8/current vs v1.0 OptiX, same-contract primary ratios, 17 rows | complete internal evidence | not public speedup wording |
| Goal1838 | v2.0 preview, OptiX prepared 2-D any-hit primitive, Torch/CuPy input-plus-output zero-copy | accepted by Gemini as `accept-with-boundary` | not v2.0 release |
| Goal1842 | learner docs for the Goal1838 preview path | complete local docs gate | not v2.0 release |

## Engine Readiness

| Engine | v1.8 comparison baseline | v2.0 partner comparison readiness | What remains before total comparison |
| --- | --- | --- | --- |
| Embree | ready as CPU same-surface app-wall evidence | no GPU partner zero-copy claim is applicable; Embree can still be timed as the CPU RT fallback/control | define whether v2.0 Embree rows are unchanged control rows or partner-host rows, then rerun the same app-command harness on the v2.0 release candidate |
| OptiX | ready as same-contract primary/subpath evidence | one primitive is ready, but no app-level partner rewrites are complete | rewrite public apps that can use the partner any-hit/count/reduce surface, add a v2.0 app harness, then run pod timings with Torch and CuPy |

## Public App Matrix

| App | Embree v1.8 baseline | Embree v2.0 readiness | OptiX v1.8 baseline | OptiX v2.0 readiness |
| --- | --- | --- | --- | --- |
| `database_analytics` | available | CPU control rerun needed | available | not rewritten for partner tensors |
| `graph_analytics` | split app-wall rows available | CPU control rerun needed | split same-contract rows available | not rewritten for partner tensors |
| `apple_rt_demo` | not an Embree app | not in active v2.0 Embree scope | not an OptiX app | not in active v2.0 OptiX scope |
| `service_coverage_gaps` | available | CPU control rerun needed | available | candidate after any-hit/count partner app adapter |
| `event_hotspot_screening` | available | CPU control rerun needed | available | candidate after any-hit/count partner app adapter |
| `facility_knn_assignment` | available | CPU control rerun needed | available | not yet covered by Goal1838 any-hit slice |
| `road_hazard_screening` | available | CPU control rerun needed | available | candidate after any-hit/count partner app adapter |
| `segment_polygon_hitcount` | available | CPU control rerun needed | available | candidate after any-hit/count partner app adapter |
| `segment_polygon_anyhit_rows` | available | CPU control rerun needed | available | closest current app to Goal1838; still needs app-level partner rewrite |
| `polygon_pair_overlap_area_rows` | available | CPU control rerun needed | available | not yet covered beyond candidate discovery subphase |
| `polygon_set_jaccard` | available | CPU control rerun needed | available | not yet covered beyond candidate discovery subphase |
| `hausdorff_distance` | available | CPU control rerun needed | available | not yet covered by Goal1838 any-hit slice |
| `ann_candidate_search` | available | CPU control rerun needed | available | not yet covered by Goal1838 any-hit slice |
| `outlier_detection` | available | CPU control rerun needed | available | not yet covered by Goal1838 any-hit slice |
| `dbscan_clustering` | shared primitive alias | CPU control scope decision needed | shared primitive alias | not independently comparable until alias policy is fixed |
| `robot_collision_screening` | available | CPU control rerun needed | available | candidate after partner output flags are lifted to app-level pose flags |
| `barnes_hut_force_app` | available | CPU control rerun needed | available | not yet covered by Goal1838 any-hit slice |
| `hiprt_ray_triangle_hitcount` | not an Embree app | not in active v2.0 Embree scope | not an OptiX app | not in active v2.0 OptiX scope |

## Required Work Before The Total Table

1. Freeze the v2.0 comparison contract:
   `v1.8 source-tree Python+RTDL app` versus
   `v2.0 source-tree Python+partner+RTDL app`, with identical datasets,
   identical output semantics, and explicit warm/cold timing phases.

2. Build a v2.0 partner app adapter for at least one any-hit/count app:
   `segment_polygon_anyhit_rows` is the natural first app because Goal1838
   already proves the underlying OptiX primitive can consume partner-owned CUDA
   inputs and write partner-owned CUDA output flags.

3. Extend from primitive output flags to the app's real output contract:
   hit counts, selected rows, compact summaries, or domain-level metrics must be
   produced without quietly falling back to RTDL-owned staging buffers in the
   measured path.

4. Add a v2.0 app performance harness:
   it must print progress for long rows, record exact commands, hardware,
   partner framework, cold/warm timing, parity, and whether a row used true
   zero-copy or a fallback.

5. Run the harness on an NVIDIA pod for OptiX:
   the local Linux GTX 1070 can smoke-test builds, but it is not accepted as the
   release performance machine for broad OptiX/RT-core claims.

6. Rerun Embree as the CPU control column:
   Embree should be treated as the CPU RT fallback/control. It can be measured
   locally, but those rows do not prove CUDA zero-copy or RT-core speedup.

7. Get external review:
   any total v2.0-vs-v1.8 performance conclusion is a key public claim and needs
   3-AI consensus before release wording.

## Boundary

Goal1843 says the comparison is plan-ready, not execution-ready. The next
implementation goal should create the first app-level v2.0 partner adapter and
timing row, preferably for `segment_polygon_anyhit_rows` on OptiX, then expand
only after that row proves parity and useful timing telemetry.
