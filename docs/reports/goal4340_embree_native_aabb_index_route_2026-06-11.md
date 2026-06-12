# Goal4340: Native Embree AABB Index Route For LibRTS-Style CPU Rows

Date: 2026-06-11

Status: implemented locally; validated on local Linux.

## Purpose

Goal4339 proved that `--skip-counts` now avoids the expensive Python CPU
oracle, but it also exposed the real Embree bottleneck: the LibRTS-style
`embree_aabb_index` path was still using the generic columnar conjunctive-scan
fallback. That fallback is app-agnostic and correct, but it is the wrong
primitive shape for serious spatial-index evidence.

Goal4340 adds an app-agnostic native Embree `AABB_INDEX_QUERY_2D` count route:

- prepare indexed 2D AABBs as an Embree user-geometry scene;
- prepare query points/boxes as a second scene for the count call;
- use Embree 4 `rtcCollide(...)` for broadphase traversal;
- apply exact operation predicates in the callback:
  `point_contains`, `range_contains`, and `range_intersects`;
- keep the old columnar route as the fallback when an older Embree library does
  not export the new native symbols.

This is a generic primitive route, not a LibRTS-specific native engine path.

## Files Changed

- `src/native/embree/rtdl_embree_prelude.h`
- `src/native/embree/rtdl_embree_scene.cpp`
- `src/native/embree/rtdl_embree_api.cpp`
- `src/rtdsl/embree_runtime.py`
- `src/rtdsl/aabb_index.py`
- `examples/current/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py`

New exported native symbols:

- `rtdl_embree_prepare_aabb_index_2d`
- `rtdl_embree_count_prepared_aabb_index_2d`
- `rtdl_embree_destroy_prepared_aabb_index_2d`

Post-review availability guard:

- `embree_aabb_index_2d_available()` now requires Embree major version `>= 4`
  as well as the native symbols, because the route depends on Embree 4
  `rtcCollide(...)`.
- Direct `PreparedEmbreeAabbIndex2D(...)` construction also fails early with a
  clear Embree-4 requirement on older libraries.
- Older libraries therefore use the existing columnar fallback instead of
  advertising native AABB availability and failing later at count time.

## Correctness Guard

The first native count implementation used a plain `size_t` in the Embree
collision callback. The small repeated correctness row caught nondeterministic
count changes, which indicated parallel callback execution. The callback count
is now `std::atomic<size_t>` with relaxed increments.

## Local Linux Evidence

Artifact directory:

`docs/reports/goal4340_embree_native_aabb_index_local_linux/`

Environment:

- Host: local Linux `192.168.1.20`
- Embree: 4.3.0
- Backend library: `build/librtdl_embree.so`
- Threads: `OMP_NUM_THREADS=8`, `TBB_NUM_THREADS=8`,
  `RTDL_EMBREE_THREADS=8`

| Row | Box Count | Query Count | Validation | Native Index | Query Median Sec |
| --- | ---: | ---: | --- | --- | ---: |
| small validated | 64 | 64 | `matches_cpu_reference=true` | `embree_native_aabb_collision_index` | 0.000924686 |
| large skip-count | 1024 | 1024 | CPU oracle intentionally skipped | `embree_native_aabb_collision_index` | 0.011698941 |

The comparable pre-Goal4340 large skip-count row from Goal4339 had
`query_median_sec=43.764849884002615`, still inside the native query path.
The new native AABB collision route therefore improves the measured query
median by about `3740.9x` on this 1024x1024 LibRTS-style row.

## Same-Scale OptiX Check

Artifact:

`docs/reports/goal4340_embree_optix_same_scale_comparison_2026-06-11.json`

Same app runner and fixture shape:

- `box_count=1024`
- `query_count=1024`
- `operation=all`
- `repeat=2`
- `warmup=1`
- `--skip-counts`

| Backend | Host | Query Median Sec | Elapsed Sec | RT-Core Accelerated |
| --- | --- | ---: | ---: | --- |
| Embree CPU | local Linux `192.168.1.20` | 0.011698941 | 0.033405830 | false |
| OptiX RT | RTX 4000 Ada pod `157.157.221.29` | 0.000622335 | 0.265061430 | true |

The OptiX RT-core query median is about `18.8x` faster than the optimized
Embree CPU query median on this row. The elapsed totals are not a clean
cross-hardware conclusion because the OptiX row includes about `0.262s` of scene
preparation at this small scale, while the query-median comparison isolates the
prepared-query phase.

## Boundary

This report does not authorize public release, public speedup wording, paper
reproduction wording, broad CPU-vs-GPU claims, NVIDIA RT-core claims, automatic
partner selection, or app-specific native-engine logic.

The result is specifically:

- an app-agnostic Embree CPU `AABB_INDEX_QUERY_2D` primitive improvement;
- validated for count-only LibRTS-style rows on local Linux;
- not a claim that Embree CPU should beat NVIDIA RT cores generally;
- a prerequisite for a fair later Embree-vs-OptiX comparison.
