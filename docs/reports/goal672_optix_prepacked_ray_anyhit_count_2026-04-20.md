# Goal 672: OptiX Prepacked Ray Any-Hit Count

Date: 2026-04-20

## Scope

Goal 672 follows Goal 671's non-winning prepared-count result. Goal 671 prepared the triangle scene but still packed and uploaded rays on every `count()` call. Goal 672 adds a prepacked 2-D ray buffer for repeated-query app cases where both the blocker scene and the ray batch are reused.

Implemented:

- Native OptiX C ABI:
  - `rtdl_optix_prepare_rays_2d`
  - `rtdl_optix_count_prepared_ray_anyhit_2d_packed`
  - `rtdl_optix_destroy_prepared_rays_2d`
- Python API:
  - `rt.prepare_optix_rays_2d(rays)`
  - `PreparedOptixRayTriangleAnyHit2D.count_packed(packed_rays)`
  - `PreparedOptixRayTriangleAnyHit2D.count(packed_rays)` dispatches to the packed path.
- Tests:
  - `/Users/rl2025/rtdl_python_only/tests/goal671_optix_prepared_anyhit_count_test.py`

## User-Facing Shape

```python
with rt.prepare_optix_ray_triangle_any_hit_2d(triangles) as scene:
    with rt.prepare_optix_rays_2d(rays) as packed_rays:
        blocked_count = scene.count_packed(packed_rays)
```

This is intentionally an app-level repeated-query API. It is useful for visibility/collision, robot planning, repeated LOS checks, and benchmark loops where the ray set is stable across multiple evaluations.

## Correctness Evidence

Local macOS:

```text
python3 -m py_compile src/rtdsl/optix_runtime.py src/rtdsl/__init__.py tests/goal671_optix_prepared_anyhit_count_test.py
OK
```

```text
PYTHONPATH=src:. python3 -m unittest tests.goal671_optix_prepared_anyhit_count_test -v

Ran 6 tests in 0.000s
OK (skipped=2)
```

Linux native OptiX:

```text
Host path: /tmp/rtdl_goal672
Command: make build-optix
Result: build/librtdl_optix.so built successfully with nvcc.
```

```text
RTDL_OPTIX_LIB=/tmp/rtdl_goal672/build/librtdl_optix.so \
PYTHONPATH=src:. python3 -m unittest tests.goal671_optix_prepared_anyhit_count_test -v

Ran 6 tests in 0.303s
OK
```

Repository hygiene:

```text
git diff --check
OK
```

## Linux Performance Probe

Hardware context: Linux host `lx1`, NVIDIA GTX 1070, OptiX backend built from current source under `/tmp/rtdl_goal672`.

Workload:

- 8192 2-D rays
- 2048 2-D triangles
- Dense all-hit case
- Correctness checked by comparing all three paths to the same blocked count: `8192`
- 10 repeated timed iterations after warmup

Results:

| Path | Median seconds |
|---|---:|
| Existing unprepared OptiX any-hit row output | `0.005031049` |
| Goal 671 prepared scene, unpacked rays each call | `0.008270310` |
| Goal 672 prepared scene plus prepacked rays | `0.000075006` |

Raw timings:

```text
unprepared_anyhit_row_seconds:
  [0.011186969, 0.005020787, 0.005033994, 0.005001013, 0.005002009,
   0.005028104, 0.010889434, 0.005085481, 0.005037353, 0.004993976]

prepared_unpacked_count_seconds:
  [0.008425663, 0.008398420, 0.008247180, 0.008106539, 0.008207024,
   0.008293440, 0.008412511, 0.008398539, 0.008107839, 0.008245650]

prepared_packed_count_seconds:
  [0.000079721, 0.000075094, 0.000073432, 0.000074543, 0.000076505,
   0.000074382, 0.000076142, 0.000074587, 0.000074917, 0.000131525]
```

## Honest Claim Boundary

This is a real speedup for a narrow repeated-query contract:

- Prepared triangle BVH is reused.
- The ray batch is prepacked/uploaded once and reused.
- Output is a scalar count, not emitted rows.

This must not be generalized to:

- one-shot queries,
- changing ray batches,
- full row-output workloads,
- all OptiX workloads,
- or non-OptiX engines.

Goal 672 does not remove Goal 671's finding that the unpacked prepared-count path is slower than the existing row-output path. It adds a new lower-copy path that is fast when the app can use the stricter prepared+packed contract.

## Next Optimization Candidates

- Replace global hit-count atomics with lower-contention per-block aggregation or bitset/popcount.
- Add a benchmark script with multiple densities and scales.
- Consider the same prepared+packed scalar contract for Vulkan and HIPRT if their APIs make persistent ray buffers practical.
