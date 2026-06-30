# Goal 543: HIPRT Backend-Style Dispatch

Date: 2026-04-18

Repository: `/Users/rl2025/rtdl_python_only`

Linux validation checkout: `/tmp/rtdl_goal543_hiprt_dispatch`

HIPRT SDK: `/home/lestat/vendor/hiprt-official/hiprtSdk-2.2.0e68f54`

## Goal

Expose the existing HIPRT 3D ray-triangle hit-count workload through normal RTDL backend-style dispatch.

Before this goal, users had to call workload-specific helpers:

```python
rt.ray_triangle_hit_count_hiprt(rays3d, triangles3d)
rt.prepare_hiprt_ray_triangle_hit_count(triangles3d)
```

This goal adds:

```python
rt.run_hiprt(kernel, rays=rays3d, triangles=triangles3d)

with rt.prepare_hiprt(kernel, triangles=triangles3d) as prepared:
    rows = prepared.run(rays=rays3d)
```

## Supported Kernel Shape

Current HIPRT dispatch intentionally supports only this RTDL shape:

```python
@rt.kernel(backend="rtdl", precision="float_approx")
def kernel():
    rays = rt.input("rays", rt.Rays3D, layout=rt.Ray3DLayout, role="probe")
    triangles = rt.input("triangles", rt.Triangles3D, layout=rt.Triangle3DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_hit_count(exact=False))
    return rt.emit(hits, fields=["ray_id", "hit_count"])
```

Unsupported kernels fail clearly before backend loading when possible. The current rejection boundary includes 2D ray/triangle kernels, wrong layouts, wrong roles, wrong predicates, and unsupported result modes.

## Implementation

Files changed:

- `/Users/rl2025/rtdl_python_only/src/rtdsl/hiprt_runtime.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py`
- `/Users/rl2025/rtdl_python_only/tests/goal543_hiprt_dispatch_test.py`

Public API:

- `run_hiprt(kernel_fn_or_compiled, *, result_mode="dict", **inputs)`
- `prepare_hiprt(kernel_fn_or_compiled, **build_inputs)`
- `PreparedHiprtKernel`

Lower-level APIs remain available:

- `ray_triangle_hit_count_hiprt`
- `prepare_hiprt_ray_triangle_hit_count`
- `PreparedHiprtRayTriangleHitCount3D`

## Correctness Tests

Local macOS command:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest tests.goal543_hiprt_dispatch_test
```

Result:

```text
Ran 4 tests in 0.000s
OK (skipped=2)
```

Local coverage:

- Unsupported 2D dispatch is rejected before requiring a HIPRT backend library.
- `prepare_hiprt` rejects query rays at prepare time and tells users to pass rays later to `prepared.run(...)`.

Linux command:

```bash
cd /tmp/rtdl_goal543_hiprt_dispatch
export RTDL_HIPRT_LIB=$PWD/build/librtdl_hiprt.so
export LD_LIBRARY_PATH=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54/hiprt/linux64:${LD_LIBRARY_PATH:-}
PYTHONPATH=src:. python3 -m unittest \
  tests.goal540_hiprt_probe_test \
  tests.goal541_hiprt_ray_hitcount_test \
  tests.goal543_hiprt_dispatch_test
```

Result:

```text
Ran 9 tests in 2.333s
OK
```

Linux coverage:

- HIPRT version/context probe.
- Direct one-shot HIPRT workload.
- Direct prepared HIPRT workload.
- `run_hiprt` dispatch parity against `run_cpu_python_reference`.
- `prepare_hiprt` dispatch parity across multiple ray batches.
- Unsupported 2D shape rejection.

## Dispatch Performance Smoke

Linux workload:

- Rays: `1024`
- Triangles: `2048`
- Total CPU-reference hits: `1952`

Observed timings:

```json
{
  "cpu_reference_seconds": 1.2628278399997726,
  "run_hiprt_seconds": 0.627141049999409,
  "prepare_hiprt_seconds": 0.533080856000197,
  "prepared_query_seconds": [
    0.0023732619993097614,
    0.0022078160000091884,
    0.0022754709998480394,
    0.0023774569999659434,
    0.00232004000008601
  ],
  "run_hiprt_parity": true,
  "prepare_hiprt_parity_all": true
}
```

## Interpretation

`run_hiprt` is now a normal RTDL backend entry point for the first supported HIPRT workload. `prepare_hiprt` exposes the performance-relevant path by separating build/compile preparation from repeated ray-query batches.

This is still a narrow dispatch surface. It is intentionally not a broad HIPRT backend claim.

## Explicit Non-Claims

- No AMD GPU validation.
- No HIPRT CPU fallback validation.
- No 2D HIPRT ray-triangle support.
- No non-hit-count HIPRT workloads.
- No automatic fallback to CPU, Embree, OptiX, or Vulkan.
- No large-scale release-grade performance suite.

## Verdict

Implementation status: `PASS`

Goal 543 establishes HIPRT as a backend-style RTDL execution target for the first supported workload while preserving strict capability boundaries.

Recommended next step: add public documentation/examples for HIPRT dispatch, then choose whether to expand HIPRT to a second workload or run a larger HIPRT performance/correctness suite.
