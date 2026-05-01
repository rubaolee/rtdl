# Goal663: Apple RT Performance Consensus and Next Steps

Date: 2026-04-20

Status: Codex and Claude consensus recorded; low-risk follow-up implemented

## Inputs

Codex performance report:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal662_apple_rt_anyhit_performance_optimization_2026-04-20.md`

Claude review:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal663_claude_apple_rt_perf_ideas_2026-04-20.md`

Benchmark artifacts:

- `/Users/rl2025/rtdl_python_only/build/goal662_final_1s.md`
- `/Users/rl2025/rtdl_python_only/build/goal663_distance_only_1s.md`
- `/Users/rl2025/rtdl_python_only/build/goal663_pooled_work_1s.md`

## Consensus

Codex and Claude agree on these points:

1. The current Apple RT any-hit path is genuinely Metal/MPS RT-backed.

   The backend builds `MPSTriangleAccelerationStructure` objects and dispatches `MPSRayIntersector` work through Metal command buffers. It is not a hidden CPU-only compatibility path.

2. The current performance claim must remain bounded.

   Apple RT prepared any-hit is faster than Shapely/GEOS STRtree on the measured Mac visibility/collision workload, but it still does not beat Embree on this Mac.

3. The first safe optimization was correct.

   Switching Apple RT any-hit to `MPSIntersectionTypeAny`, removing artificial 32-triangle chunking for prepared 2D any-hit, and reusing prepared Metal buffers produced a large improvement over the prior Apple RT path.

4. Further micro-optimizations are unlikely to close the full Embree gap alone.

   The remaining gap is likely dominated by MPS command-buffer scheduling, synchronization, MPS traversal overhead, Python/ctypes input conversion, and/or the 2D-to-3D prism representation. Blindly changing more local fields is not enough.

## Implemented After Claude Review

Claude recommended the following low-risk first step:

- Use `MPSIntersectionDataTypeDistance` instead of `MPSIntersectionDataTypeDistancePrimitiveIndex` for any-hit, because primitive identity is unused under `MPSIntersectionTypeAny`.

Codex implemented that recommendation for Apple RT any-hit paths and verified correctness.

Codex also implemented the next low-risk host-side cleanup:

- Reused the prepared `any_hits` and `valid_rays` working arrays.
- Filled the prepared Metal ray buffer directly instead of allocating a temporary `std::vector<MPSRayOriginMaskDirectionMaxDistance>` and copying it.
- Removed the redundant per-query `valid_ray_2d(...)` recheck inside the prepared dispatch loop.

## Correctness Verification

Command:

```bash
make build-apple-rt && PYTHONPATH=src:. python3 -m unittest -v tests.goal578_apple_rt_backend_test tests.goal651_apple_rt_3d_anyhit_native_test tests.goal652_apple_rt_2d_anyhit_native_test tests.goal659_mac_visibility_collision_perf_test && git diff --check
```

Result:

```text
Ran 14 tests in 0.043s
OK
git diff --check: clean
```

## Performance Results

Baseline after Goal662:

| Backend | Per-query median | Ratio vs Apple RT |
| --- | ---: | ---: |
| Apple RT prepared-query | 0.006613661 s | 1.000x |
| Embree | 0.003396472 s | Apple RT 1.947x slower |
| Shapely/GEOS STRtree | 0.072708116 s | Apple RT 11.0x faster |

After Claude A1 distance-only output:

| Backend | Per-query median | Ratio |
| --- | ---: | ---: |
| Apple RT prepared-query | 0.006655087 s | Apple RT 1.965x slower than Embree |
| Embree | 0.003386247 s | fastest |
| Shapely/GEOS STRtree | 0.071598804 s | Apple RT about 10.8x faster |

After distance-only plus pooled working arrays/direct ray-buffer fill:

| Backend | Per-query median | Ratio |
| --- | ---: | ---: |
| Apple RT prepared-query | 0.006540905 s | Apple RT 1.925x slower than Embree |
| Embree | 0.003397733 s | fastest |
| Shapely/GEOS STRtree | 0.072004080 s | Apple RT about 11.0x faster |

## Interpretation

The second optimization round is correct but only marginally faster.

The honest performance statement after Goal663 is:

> Apple RT prepared any-hit is about `5.7x` faster than the pre-Goal662 Apple RT prepared path and about `11x` faster than Shapely/GEOS STRtree on the measured Mac visibility/collision workload, but Embree remains about `1.9x` faster on the same Mac.

## Next Serious Performance Options

Codex and Claude agree that the next useful work should not be another blind micro-optimization.

Recommended next steps:

1. Profile with Metal System Trace or an equivalent timing split.

   Measure CPU ray packing, command buffer creation, GPU traversal, `waitUntilCompleted`, and result materialization separately. This identifies whether the remaining cost is GPU traversal or host/driver synchronization.

2. Add a benchmark mode that avoids hidden full CPU-oracle scaling costs.

   The current benchmark is good for correctness and small/medium comparisons, but large runs become dominated by oracle/Shapely work before engine results are useful. Add a precomputed-oracle or sampled-oracle mode with explicit honesty labeling.

3. Consider a batched prepared API.

   If profiling shows command-buffer scheduling dominates, a batched API that encodes multiple ray sets into one command buffer is likely the next practical speed lever.

4. Treat Metal 3 `MTLAccelerationStructure` as the research path.

   If the project goal is to beat Embree on Apple hardware, MPS may not be the final API. A Metal 3 acceleration-structure backend could better target Apple RT hardware, but it is a larger backend rewrite with higher correctness and compatibility risk.

## Release Boundary

No release or documentation should claim Apple RT beats Embree yet.

Allowed claim:

- Apple RT any-hit is now substantially faster than the earlier Apple RT path.
- Apple RT beats Shapely/GEOS on the measured Mac visibility/collision benchmark.
- Embree is still the fastest measured backend on this Mac.
