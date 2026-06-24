# Goal 748: OptiX Robot Any-Hit Correctness And Scaled Performance

## Verdict

ACCEPT for Linux OptiX correctness and app-performance harness readiness. The robot-collision OptiX any-hit path had a real correctness bug for short rays; it is fixed and validated on Linux. Performance evidence is useful for whole-call shape, but it is not RTX RT-core speedup evidence because the Linux GPU is a GTX 1070 with no RT cores.

## Scope

This goal starts the post-Embree NVIDIA/OptiX app-performance phase. The first target is the robot-collision / visibility / ray-triangle any-hit flagship path because it is already the cleanest RTDL operation-to-ray-tracing mapping:

- build: obstacle triangles;
- probe: robot link edge rays;
- traverse: OptiX BVH/custom primitive traversal;
- refine: 2D ray/triangle any-hit;
- emit: either per-ray rows or a prepared scalar hit-edge count.

## Correctness Bug Found

The initial Goal748 Linux run exposed a blocker:

| Backend | Hit-edge count |
|---|---:|
| CPU oracle | 5,742 |
| Embree rows | 5,742 |
| OptiX rows | 3,828 |
| OptiX prepared count | 3,828 |

The mismatch reproduced at smaller scales and was not random. The old OptiX 2D any-hit custom intersection used:

```cpp
optixReportIntersection(0.5f, 0u);
```

That is invalid for short rays whose traced world-space interval is below `0.5`. The robot fixture emits rectangle edges with short vertical rays, commonly length `0.25`, so valid intersections were silently dropped. This explained the consistent two-horizontal-edges-only pattern.

## Fix

`src/native/optix/rtdl_optix_core.cpp` now reports an interval-local `t` for 2D ray/triangle any-hit:

```cpp
float hit_t = optixGetRayTmin() + 1.0e-6f;
if (hit_t > optixGetRayTmax()) hit_t = optixGetRayTmax();
optixReportIntersection(hit_t, 0u);
```

For any-hit semantics, the exact intersection distance is not used by the payload. The reported `t` only needs to be valid within the current ray interval so OptiX accepts the intersection and invokes the any-hit program.

## Regression Tests

Added short-ray native regression coverage:

- `tests/goal637_optix_native_any_hit_test.py::test_optix_native_any_hit_2d_matches_cpu_for_short_rays`
- `tests/goal671_optix_prepared_anyhit_count_test.py::test_prepared_anyhit_count_matches_cpu_for_short_rays`

These tests use a `0.25`-length 2D ray that should hit a triangle. They would fail with the old fixed `0.5f` report distance on a native OptiX machine.

## New Harness

Added:

- `scripts/goal748_optix_robot_scaled_perf.py`
- `tests/goal748_optix_robot_scaled_perf_test.py`

The harness separates:

- case construction;
- optional CPU oracle validation;
- Embree row execution;
- OptiX row execution;
- OptiX prepared scalar hit-count execution;
- preparation costs for OptiX scene/rays;
- Python dict row materialization versus scalar output.

This matters because whole-app demos intentionally validate against CPU oracles, but performance conclusions must not mix CPU oracle time into native backend execution time.

## Linux Native Validation

Host:

- `lestat-lx1`
- GPU: NVIDIA GeForce GTX 1070, 8GB
- Driver: `580.126.09`
- CUDA: `12.0`
- OptiX SDK header: `$HOME/vendor/optix-dev/include/optix.h`
- Build command:

```bash
make build-optix OPTIX_PREFIX=$HOME/vendor/optix-dev CUDA_PREFIX=/usr NVCC=/usr/bin/nvcc
```

Native focused tests passed after the fix:

```text
tests.goal637_optix_native_any_hit_test
tests.goal671_optix_prepared_anyhit_count_test
11 tests OK
```

Scaled parity sweep after the fix:

| Poses | Obstacles | Edge rays | Triangles | CPU | Embree | OptiX rows | OptiX prepared | Result |
|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 2 | 1 | 8 | 2 | 3 | 3 | 3 | 3 | ok |
| 4 | 2 | 16 | 4 | 3 | 3 | 3 | 3 | ok |
| 8 | 4 | 32 | 8 | 12 | 12 | 12 | 12 | ok |
| 16 | 8 | 64 | 16 | 39 | 39 | 39 | 39 | ok |
| 32 | 16 | 128 | 32 | 72 | 72 | 72 | 72 | ok |
| 64 | 32 | 256 | 64 | 150 | 150 | 150 | 150 | ok |
| 128 | 64 | 512 | 128 | 336 | 336 | 336 | 336 | ok |
| 256 | 128 | 1,024 | 256 | 660 | 660 | 660 | 660 | ok |
| 512 | 256 | 2,048 | 512 | 1,440 | 1,440 | 1,440 | 1,440 | ok |
| 1,024 | 512 | 4,096 | 1,024 | 2,955 | 2,955 | 2,955 | 2,955 | ok |
| 2,000 | 1,000 | 8,000 | 2,000 | 5,742 | 5,742 | 5,742 | 5,742 | ok |

## Correctness-Gated Timing

Raw JSON:

`/Users/rl2025/rtdl_python_only/docs/reports/goal748_optix_robot_scaled_perf_linux_gtx1070_2026-04-21.json`

Fixture:

- 2,000 poses;
- 1,000 obstacles;
- 8,000 edge rays;
- 2,000 obstacle triangles;
- CPU oracle validation enabled;
- all backends matched `5,742` hit edges.

| Backend | Output shape | Median execute sec | Hit edges | Parity |
|---|---|---:|---:|---|
| Embree rows | per-ray dict rows | 0.006293 | 5,742 | true |
| OptiX rows | per-ray dict rows | 0.004940 | 5,742 | true |
| OptiX prepared count | native scalar count | 0.0000659 | 5,742 | true |

Derived reading:

- OptiX rows were about `1.27x` faster than Embree rows on this GTX 1070 run.
- OptiX prepared scalar execute was about `95x` faster than Embree row execution, but this excludes OptiX scene/ray preparation and returns only a scalar count.
- Preparation costs were `0.133984s` for the scene and `0.007816s` for rays, so this path is strongest for repeated queries or when scalar output is sufficient.

## Larger No-Oracle Timing

Raw JSON:

`/Users/rl2025/rtdl_python_only/docs/reports/goal748_optix_robot_scaled_perf_linux_gtx1070_large_no_oracle_2026-04-21.json`

Fixture:

- 20,000 poses;
- 10,000 obstacles;
- 80,000 edge rays;
- 20,000 obstacle triangles;
- CPU oracle validation disabled for runtime practicality;
- all measured backends agreed on `59,400` hit edges.

| Backend | Output shape | Median execute sec | Hit edges |
|---|---|---:|---:|
| Embree rows | per-ray dict rows | 0.066656 | 59,400 |
| OptiX rows | per-ray dict rows | 0.050448 | 59,400 |
| OptiX prepared count | native scalar count | 0.000234 | 59,400 |

Derived reading:

- OptiX rows were about `1.32x` faster than Embree rows.
- OptiX prepared scalar execute was about `285x` faster than Embree row execution, excluding preparation.
- Preparation costs were `0.149585s` for the scene and `0.112473s` for rays.

## Boundaries

- GTX 1070 has no RT cores. These results validate OptiX traversal correctness and whole-call behavior, not RTX RT-core acceleration.
- Prior robot OptiX performance evidence before this fix is suspect for short-ray workloads and should not be used for release claims without rerun.
- Prepared scalar count is not a replacement for full pose-level witness rows. It is a different output contract for hit-edge count summaries.
- RTX-class cloud validation remains required before claiming NVIDIA RT-core speedup.

## Next Steps

- Read Windows Codex's Goal749 independent review when it appears in the bridge.
- Audit other hardcoded `optixReportIntersection(0.5f, ...)` sites and decide which are safe, risky, or need interval-local fixes.
- Run the same Goal748 harness on an RTX-class GPU before making RT-core performance claims.
