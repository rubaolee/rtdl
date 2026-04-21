# Goal670: Codex OptiX Performance Optimization Review

Date: 2026-04-20

Reviewer: Codex

Input playbook:

`/Users/rl2025/rtdl_python_only/docs/reports/goal669_cross_engine_performance_optimization_lessons_2026-04-20.md`

Primary source reviewed:

- `/Users/rl2025/rtdl_python_only/src/native/optix/rtdl_optix_api.cpp`
- `/Users/rl2025/rtdl_python_only/src/native/optix/rtdl_optix_core.cpp`
- `/Users/rl2025/rtdl_python_only/src/native/optix/rtdl_optix_workloads.cpp`
- `/Users/rl2025/rtdl_python_only/src/native/optix/rtdl_optix_prelude.h`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/optix_runtime.py`

Prior evidence reviewed:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal637_v0_9_5_optix_native_early_exit_anyhit_2026-04-19.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal427_v0_7_rt_db_optix_backend_closure_2026-04-15.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal435_v0_7_optix_native_prepared_db_dataset_2026-04-16.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal441_v0_7_optix_columnar_prepared_db_dataset_transfer_2026-04-16.md`

## Verdict

ACCEPT WITH NOTES.

OptiX already has the strongest RTDL performance foundation among the GPU RT
engines: native any-hit early exit, prepared DB dataset reuse, and columnar DB
ingestion. The next optimization work should focus less on proving that OptiX
can run workloads, and more on removing repeated host/device setup and row
materialization from hot app contracts.

## Current OptiX Performance State

Implemented and credible:

- `ray_triangle_any_hit` has native OptiX early-exit traversal. Goal637 changed
  the any-hit program to set payload `any_hit=1` and call `optixTerminateRay()`.
- DB workloads have a real OptiX RT path over custom AABB row primitives.
- DB workloads also have a prepared dataset API that reuses the built
  GAS/traversable across repeated queries.
- DB ingestion has a columnar transfer path that reduced measured 200k-row
  prepare time by about `3.17x` to `3.38x` against row-struct transfer.
- Python prepared dispatch caches bound executions for ordinary prepared
  kernels and routes raw `ray_triangle_any_hit` to native OptiX symbols when
  available.

Measured evidence:

- Goal637 dense any-hit microcase on Linux: native any-hit median
  `0.0032699169969419017 s` versus hit-count median
  `0.02033192099770531 s`, about `6.22x` faster on that bounded dense-hit
  fixture.
- Goal435 DB repeated-query gate on Linux, 200k rows / 10 queries:
  - `conjunctive_scan`: OptiX prepare `2.693911 s`, median query `0.011617 s`
  - `grouped_count`: OptiX prepare `2.548569 s`, median query `0.004479 s`
  - `grouped_sum`: OptiX prepare `2.414290 s`, median query `0.010184 s`
- Goal441 columnar transfer gate on Linux:
  - prepare-time speedup: about `3.17x` to `3.38x`

## What Is Already Optimized

### Native Any-Hit Early Exit

The `ray_triangle_any_hit` implementation is correctly prioritized for OptiX.
The native implementation uses `optixTerminateRay()` rather than hit-count
projection. This is the right mechanism for dense visibility/collision cases
where the app only needs existence.

### Prepared DB Dataset Reuse

The prepared DB path avoids rebuilding the custom-primitive GAS for every DB
query. This directly follows the Goal669 lesson that stable build-side data
must become a prepared object.

### Columnar DB Transfer

The columnar transfer path directly addresses Python/ctypes row-ingestion
overhead for prepared DB creation. This is consistent with the Goal669 rule
that Python should orchestrate rather than repeatedly marshal heavy data.

### Kernel/Pipeline Caching

Several CUDA helper kernels use `std::call_once` to compile/load PTX and fetch
function handles once. Python also has a small prepared execution cache.

## Main Remaining Optimization Opportunities

### 1. Prepared Ray/Triangle Any-Hit And Scalar Count

Expected value: very high.

Implementation risk: medium.

Current `ray_triangle_any_hit` still returns one row per ray and does not expose
an app-level scalar count path analogous to the Apple RT packed-count path.
The next OptiX visibility/collision optimization should add:

- prepared triangle GAS handle;
- prepacked ray buffers;
- reusable output buffers;
- scalar `any` or `count` result path when the app does not need emitted rows;
- profile counters for pack, launch, wait, download, and materialization.

This is the direct OptiX version of the Apple RT lesson. OptiX should be the
highest-priority engine for this because it has true programmable any-hit and
RT-core-capable hardware on suitable GPUs.

Claim boundary:

- Do not compare scalar-count OptiX against full-row Embree/Vulkan/HIPRT
  without saying the output contract differs.
- Report first-query and repeated-query costs separately.
- GTX 1070 evidence remains non-RT-core evidence.

### 2. Native Reduced Outputs For Nearest Neighbor

Expected value: high for app workloads.

Implementation risk: medium to high.

The current kNN/fixed-radius paths use CUDA kernels, then download candidate
records and perform exact filtering, sorting, trimming, and row construction on
the host. This is correct and useful, but not yet the fastest app contract for
workloads that only need:

- neighbor count within radius;
- `any neighbor within radius`;
- min distance;
- max nearest-neighbor distance for Hausdorff;
- density flags for outlier/DBSCAN-style apps.

Recommended path:

- add prepared search-point buffers;
- add prepacked query-point buffers for repeated query sets;
- add device-side reduced output kernels for `count`, `any`, `min`, and `max`;
- keep row-output kNN/fixed-radius as the correctness source of truth.

This would remove host sorting/materialization when apps only need reductions.

### 3. DB Grouped Aggregation On Device

Expected value: medium to high.

Implementation risk: high.

The prepared DB path is strong, but grouped aggregation still collects
candidate row indices and performs grouped count/sum with host-side
`unordered_map` logic. This is honest first-wave behavior, but it leaves a
large future optimization target.

Recommended path:

- keep prepared columnar dataset as the default for performance gates;
- add backend profiles separating candidate discovery from grouping;
- for low-cardinality group keys, add device-side grouped count/sum;
- for high-cardinality group keys, keep bounded host aggregation until a robust
  GPU hash/reduction design exists.

The grouped-output ceiling (`65536` groups) should remain enforced.

### 4. Graph Workloads Need A Real GPU/Prepared Strategy

Expected value: high if graph apps become a release focus.

Implementation risk: high.

Current OptiX graph BFS and triangle probe paths are host-indexed native C++
implementations, not OptiX RT traversal or GPU kernels. They are correctness
credible but not a performance-optimized OptiX engine path.

Recommended path:

- do not claim OptiX graph acceleration until a GPU/prepared graph path exists;
- first add profiling for frontier packing, visited-set construction, output
  sorting, and materialization;
- consider CUDA compute kernels for BFS/triangle before forcing RT traversal;
- add reduced outputs only where the app truly needs counts/flags rather than
  exact vertex rows.

This is a mechanism-honesty boundary: public API support is not the same as
OptiX hardware acceleration.

### 5. Spatial Overlay And Polygon Workloads Need Candidate/Refine Split

Expected value: medium.

Implementation risk: high.

Spatial overlay and point-in-polygon paths mix GPU candidate logic with exact
CPU/GEOS refinement in places. That is a sensible correctness design, but it
means performance claims must split:

- candidate discovery time;
- exact refinement time;
- geometry repair/topology time;
- row materialization time.

Recommended path:

- add prepared polygon/segment geometry where repeated layers exist;
- expose reduced outputs for `any overlap`, `candidate count`, and flags;
- do not claim full exact-geometry acceleration unless exact geometry output
  and topology costs are measured.

## Workload-Specific Recommendations

| Workload family | Current OptiX state | Best next optimization |
| --- | --- | --- |
| Visibility/collision | Native any-hit exists; row output still common | Prepared GAS + prepacked rays + scalar count/any |
| Nearest neighbor | CUDA kernels plus host exact/filter/sort | Prepared search set + native reductions (`count`, `any`, `min`, `max`) |
| DB-style | Prepared RT dataset and columnar transfer exist | Device-side grouped reductions where bounded and low-cardinality |
| Graph | Host-indexed native C++ path | GPU/prepared graph strategy before performance claims |
| Spatial overlay | Candidate/refine hybrid | Prepared layers and explicit candidate/refine timing |

## Risk And Claim Boundaries

- OptiX is the top-priority performance backend, but not every RTDL workload is
  currently accelerated by OptiX RT traversal.
- CUDA compute under the OptiX backend is useful but should be labeled as CUDA
  compute, not OptiX RT-core traversal.
- Prepared-query speedups must include setup/break-even reporting.
- Reduced-output speedups must not be compared to full-row outputs without
  explicit output-contract disclosure.
- GPU results on non-RT-core hardware should not be described as RT-core
  speedups.

## Proposed Implementation Order

1. Add OptiX prepared ray/triangle any-hit with prepacked rays and scalar
   count/any profile output.
2. Add a reusable OptiX phase profiler for prepare, pack, launch, wait,
   download, reduction, and Python materialization.
3. Add OptiX reduced-output nearest-neighbor helpers for Hausdorff/outlier
   app contracts.
4. Add DB grouped aggregation profiling, then decide whether low-cardinality
   device-side grouping is worth implementing.
5. Re-audit graph workloads and classify them as CUDA compute, RT traversal, or
   host-indexed support before making performance claims.

## Final Position

OptiX has the clearest path to strong RTDL performance. The immediate
optimization target should be the same pattern that made Apple RT competitive
for the Mac visibility app: prepared build data, prepacked probes, and native
reduced-output contracts. For OptiX, the first candidate should be
ray/triangle visibility scalar count because the engine already has true
programmable any-hit and a measured dense-hit early-exit win.
