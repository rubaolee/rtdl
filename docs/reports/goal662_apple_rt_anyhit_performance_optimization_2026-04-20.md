# Goal662: Apple RT Any-Hit Performance Optimization

Date: 2026-04-20

Status: implemented and measured; Embree not beaten yet

## Scope

This goal attempted to optimize the Apple Metal/MPS RT path for the Mac visibility/collision app benchmark, specifically the prepared 2D `ray_triangle_any_hit` workload used by line-of-sight and obstacle screening apps.

The target was aggressive: try to beat Embree on the same Apple M4 Mac. The optimization improved Apple RT substantially, but the measured result still does not beat Embree.

## Changes

1. Switched Apple RT any-hit paths from `MPSIntersectionTypeNearest` to `MPSIntersectionTypeAny`.

   This applies only to any-hit workloads. Closest-hit and count-style workloads still require ordered hit identity and remain nearest/count/refinement paths.

2. Removed artificial 32-triangle chunking from Apple RT 2D any-hit.

   The old path needed per-primitive masks because it used nearest-hit primitive identity plus CPU exact refinement. In `Any` mode, primitive identity is not part of the contract, so the prepared 2D any-hit backend can issue one MPS traversal over the whole prepared prism acceleration structure instead of many chunk passes.

3. Reused prepared Metal ray and intersection buffers.

   Prepared Apple RT 2D any-hit now keeps reusable `MTLBuffer` objects in the prepared handle and grows them only when needed, instead of allocating fresh ray/intersection buffers on every query call.

## Correctness Verification

Command:

```bash
PYTHONPATH=src:. python3 -m unittest -v tests.goal578_apple_rt_backend_test tests.goal651_apple_rt_3d_anyhit_native_test tests.goal652_apple_rt_2d_anyhit_native_test tests.goal659_mac_visibility_collision_perf_test
```

Result:

```text
Ran 14 tests in 0.041s
OK
```

Important correction during implementation:

- The first edit accidentally changed a closest-hit MPS encode site to `MPSIntersectionTypeAny`; closest-hit correctness failed because primitive identity changed.
- That change was reverted immediately.
- Final code keeps closest-hit on `MPSIntersectionTypeNearest` and limits `MPSIntersectionTypeAny` to any-hit semantics.

## Performance Evidence

Host:

```text
Apple M4
macOS 26.3 arm64
Python 3.14.0
Apple RT version tuple: (0, 9, 3)
Embree version tuple: (4, 4, 0)
```

Benchmark command:

```bash
PYTHONPATH=src:. build/goal659_shapely_venv/bin/python scripts/goal659_mac_visibility_collision_perf.py \
  --warmups 0 \
  --repeats 1 \
  --target-sample-seconds 1 \
  --scale dense_blocked:chunkless_buffer_reuse_1s,8192,1024 \
  --backend apple_rt_prepared_query \
  --backend embree \
  --backend shapely_strtree \
  --json-out build/goal662_final_1s.json \
  --md-out build/goal662_final_1s.md
```

Measured result:

| Case | Rays | Triangles | Backend | Per-query median | Sample median | Correct |
| --- | ---: | ---: | --- | ---: | ---: | --- |
| dense blocked | 8192 | 2048 | Apple RT prepared-query | 0.006613661 s | 0.965595 s | true |
| dense blocked | 8192 | 2048 | Embree | 0.003396472 s | 0.998563 s | true |
| dense blocked | 8192 | 2048 | Shapely/GEOS STRtree | 0.072708116 s | 1.017914 s | true |

Ratios:

- Apple RT prepared-query vs Embree: `1.947x` slower.
- Apple RT prepared-query vs Shapely/GEOS STRtree: `0.091x`, meaning Apple RT is about `11.0x` faster.

Improvement relative to the prior Apple RT long-run evidence:

- Prior prepared Apple RT dense 8192-ray/2048-triangle per-query median from Goal661: `0.037357453 s`.
- Current optimized prepared Apple RT per-query median: `0.006613661 s`.
- Improvement: about `5.65x` faster.

## Stopped Large-Scale Runs

Two larger exploratory runs were stopped manually because the benchmark's hidden correctness oracle and/or Shapely comparison dominated wall time before producing useful engine timing:

- `32768` rays with `4096` obstacle rectangles.
- `16384` rays with `2048` obstacle rectangles.

This is a benchmark harness scaling issue, not an Apple RT correctness failure. Future large-scale Apple RT vs Embree engine tests should either:

- use a precomputed oracle artifact,
- compare Apple RT and Embree result equality after one correctness-verified dataset family,
- or add a sampled-oracle mode with an explicit honesty note.

## Conclusion

Apple RT any-hit optimization is real and useful:

- It remains hardware-backed through Metal/MPS `MPSRayIntersector`.
- It is correctness-compatible with the existing RTDL any-hit tests.
- It substantially improves the prepared Apple RT visibility/collision workload.
- It beats Shapely/GEOS STRtree clearly on the measured app-style case.

However, Apple RT does not beat Embree yet on this Mac:

- Current measured Apple RT prepared-query: `0.006613661 s`.
- Current measured Embree: `0.003396472 s`.
- Remaining gap: Apple RT is about `1.95x` slower.

The honest release/documentation claim should be:

> Apple RT prepared any-hit is now much faster than the previous Apple RT path and faster than Shapely/GEOS on the measured Mac visibility/collision benchmark, but Embree remains the fastest measured backend on this Mac.
