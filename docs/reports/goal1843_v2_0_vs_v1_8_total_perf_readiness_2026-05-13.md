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
- Goal1848 extends that primitive surface from flags to bounded all-hit witness
  rows, preserving generic ray/primitive identity without app-shaped native ABI.
- Goal1850 lifts the witness contract to the first app-level adapter for
  `segment_polygon_anyhit_rows`.
- Goal1853 adds the stronger caller-supplied PyTorch/CuPy GPU-column version of
  that adapter, so the input tensors can be owned by the learner/user rather
  than packed internally by RTDL.
- Goal1856 adds the first same-contract v2.0-vs-v1.8 timing row for that app,
  at 512 and 2048 synthetic rows on the RTX A4500 pod.
- Goal1859 adds a second app-level OptiX partner adapter for
  `segment_polygon_hitcount`, but it is correctness evidence only: app counts
  are still materialized in Python from generic witness pairs, so it is not a
  whole-app zero-copy or timing row.
- Goal1861 upgrades that hit-count path to partner-owned device count columns,
  with app aggregation performed by PyTorch/CuPy tensor operations from generic
  witness pairs. It has pod correctness evidence but still no same-contract
  timing row.
- No all-app v2.0 partner timing harness exists yet.

## Current Evidence Inventory

| Evidence | Scope | Status | Release use |
| --- | --- | --- | --- |
| Goal1756 | v1.8/current vs v1.0 Embree, same app command wall-clock, 16 rows | complete internal evidence | not public speedup wording |
| Goal1750 | v1.8/current vs v1.0 OptiX, same-contract primary ratios, 17 rows | complete internal evidence | not public speedup wording |
| Goal1838 | v2.0 preview, OptiX prepared 2-D any-hit primitive, Torch/CuPy input-plus-output zero-copy | accepted by Gemini as `accept-with-boundary` | not v2.0 release |
| Goal1842 | learner docs for the Goal1838 preview path | complete local docs gate | not v2.0 release |
| Goal1848 | v2.0 preview, OptiX bounded all-hit witness rows into partner-owned CUDA outputs | pod validated on RTX A4500 for Torch/CuPy | not v2.0 release |
| Goal1850 | first app-level segment/polygon partner adapter over generic witness rows | pod validated on RTX A4500 for Torch/CuPy; Claude accepted with boundary | not v2.0 release |
| Goal1853 | caller-supplied PyTorch/CuPy GPU-column segment/polygon partner adapter | pod validated on RTX A4500 for Torch/CuPy; Claude accepted with boundary | not v2.0 release |
| Goal1856 | first same-contract v2.0-vs-v1.8 timing row for `segment_polygon_anyhit_rows` | pod validated on RTX A4500 at 512 and 2048 rows; Claude accepted with boundary | not v2.0 release |
| Goal1859 | second app-level adapter for `segment_polygon_hitcount` over generic witness rows | pod correctness-smoked on RTX A4500 for Torch/CuPy; host/Python count materialization remains explicit | not v2.0 release |
| Goal1861 | device-count-column adapter for `segment_polygon_hitcount` | pod correctness-smoked on RTX A4500 for Torch/CuPy; app count columns stay partner-owned | not v2.0 release |

## Engine Readiness

| Engine | v1.8 comparison baseline | v2.0 partner comparison readiness | What remains before total comparison |
| --- | --- | --- | --- |
| Embree | ready as CPU same-surface app-wall evidence | no GPU partner zero-copy claim is applicable; Embree can still be timed as the CPU RT fallback/control | define whether v2.0 Embree rows are unchanged control rows or partner-host rows, then rerun the same app-command harness on the v2.0 release candidate |
| OptiX | ready as same-contract primary/subpath evidence | one app-level row adapter is execution- and timing-proven for Torch/CuPy GPU columns: `segment_polygon_anyhit_rows`; one count-style app adapter now has partner-owned device count columns: `segment_polygon_hitcount` | add same-contract timing for the count-column path, expand to more app adapters, add a v2.0 app harness, then run pod timings with Torch and CuPy |

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
| `segment_polygon_hitcount` | available | CPU control rerun needed | available | Goal1861 device count columns exist over generic witness rows; no same-contract timing row yet |
| `segment_polygon_anyhit_rows` | available | CPU control rerun needed | available | first v2.0 OptiX app adapter and timing row exist: Goal1850 record adapter, Goal1853 caller-supplied PyTorch/CuPy GPU-column adapter, Goal1856 narrow 512/2048-row timing evidence |
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

2. Extend from the first timing row to broader benchmark coverage:
   `segment_polygon_anyhit_rows` now has a first same-contract timing row
   (Goal1856), but it still needs larger real-data rows, repeated environment
   checks, and external review before any public performance wording.

3. Extend the same pattern from rows to compact outputs:
   hit counts, selected rows, compact summaries, or domain-level metrics must be
   produced without quietly falling back to RTDL-owned staging buffers in the
   measured path. Goal1861 now satisfies this as correctness evidence for
   `segment_polygon_hitcount`, but it still needs same-contract timing before it
   can enter the performance table.

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

Goal1843 now says the comparison is beyond plan-only but still not all-app
execution-ready. The first app-level v2.0 OptiX adapter exists, has pod
correctness evidence, and has a first narrow same-contract timing row. A second
count-style adapter also exists with partner-owned device count columns, but it
is correctness-only until timed against the same v1.8 app contract. The next
implementation goal should scale the timed row to real datasets and add timing
for the count-column path before any total v2.0-vs-v1.8 table is attempted.
