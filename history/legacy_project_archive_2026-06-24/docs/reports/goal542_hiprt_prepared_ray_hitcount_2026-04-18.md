# Goal 542: Prepared HIPRT 3D Ray-Triangle Hit Count

Date: 2026-04-18

Repository: `/Users/rl2025/rtdl_python_only`

Linux validation checkout: `/tmp/rtdl_goal542_hiprt_prepared`

HIPRT SDK: `/home/lestat/vendor/hiprt-official/hiprtSdk-2.2.0e68f54`

## Goal

Separate HIPRT preparation cost from repeated query execution for the first HIPRT workload.

Goal 541 proved that RTDL can run a genuine HIPRT 3D ray-triangle hit-count workload. Goal 542 adds a prepared execution path so triangle upload, HIPRT geometry build, and HIPRT trace-kernel compilation are not paid on every query.

## Public API

```python
import rtdsl as rt

with rt.prepare_hiprt_ray_triangle_hit_count(triangles3d) as prepared:
    rows_a = prepared.run(rays3d_a)
    rows_b = prepared.run(rays3d_b)
```

Related one-shot API remains available:

```python
rows = rt.ray_triangle_hit_count_hiprt(rays3d, triangles3d)
```

## Implementation

Files changed:

- `/Users/rl2025/rtdl_python_only/src/native/rtdl_hiprt.cpp`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/hiprt_runtime.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py`
- `/Users/rl2025/rtdl_python_only/tests/goal541_hiprt_ray_hitcount_test.py`

Native prepared ABI:

- `rtdl_hiprt_prepare_ray_hitcount_3d`
- `rtdl_hiprt_run_prepared_ray_hitcount_3d`
- `rtdl_hiprt_destroy_prepared_ray_hitcount_3d`

Python wrapper:

- `PreparedHiprtRayTriangleHitCount3D`
- `prepare_hiprt_ray_triangle_hit_count`

The prepared object owns:

- HIPRT/Orochi runtime context.
- Uploaded triangle vertices.
- Built HIPRT triangle geometry.
- HIPRT trace kernel function.

Each `prepared.run(rays)` call only uploads rays, launches the already-compiled traversal kernel, copies rows back, and returns `{ray_id, hit_count}` rows.

## Correctness Test

Linux command:

```bash
cd /tmp/rtdl_goal542_hiprt_prepared
export RTDL_HIPRT_LIB=$PWD/build/librtdl_hiprt.so
export LD_LIBRARY_PATH=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54/hiprt/linux64:${LD_LIBRARY_PATH:-}
PYTHONPATH=src:. python3 -m unittest tests.goal540_hiprt_probe_test tests.goal541_hiprt_ray_hitcount_test
```

Result:

```text
Ran 5 tests in 1.239s
OK
```

Coverage:

- HIPRT version/context probe.
- One-shot 3D hit-count parity against CPU oracle.
- Explicit 2D rejection.
- Prepared object reused across two different ray batches.
- Prepared outputs match `rt.ray_triangle_hit_count_cpu`.

## Performance Smoke

Linux workload:

- Rays: `1024`
- Triangles: `2048`
- Total CPU oracle hits: `1974`

Observed timings:

```json
{
  "cpu_seconds": 1.2611286510000355,
  "one_shot_hiprt_seconds": 0.6327427060004993,
  "prepare_seconds": 0.5334111880001728,
  "prepared_query_seconds": [
    0.0020764329992744024,
    0.0018609809994813986,
    0.0018791920001604012,
    0.001918089000355394,
    0.001972246000150335
  ],
  "prepared_query_best_seconds": 0.0018609809994813986,
  "one_shot_parity": true,
  "prepared_parity_all": true
}
```

## Interpretation

The prepared path makes HIPRT performance measurement more honest:

- `prepare_seconds` contains context setup, triangle upload, HIPRT geometry build, and runtime kernel compilation.
- `prepared_query_seconds` contains ray upload, HIPRT traversal launch, row copy-back, and Python/ctypes overhead.

The prepared query is much faster than the CPU oracle on this bounded smoke case, but this is not yet a full release performance claim. It is a first positive signal for the prepared HIPRT execution model.

## Explicit Non-Claims

- No AMD GPU validation.
- No HIPRT CPU fallback validation.
- No 2D HIPRT ray-triangle support.
- No general `rt.run_hiprt(...)` lowering integration yet.
- No large-scale performance suite.
- No replacement of OptiX, Vulkan, Embree, or CPU behavior.

## Verdict

Implementation status: `PASS`

Goal 542 establishes a prepared HIPRT execution path for the first workload and demonstrates that one-time build/compile cost can be separated from repeated query cost while preserving CPU-oracle parity.

Recommended next step: either add a `run_hiprt` dispatch surface for this workload or expand the HIPRT workload set to another direct 3D traversal primitive before broader language integration.
