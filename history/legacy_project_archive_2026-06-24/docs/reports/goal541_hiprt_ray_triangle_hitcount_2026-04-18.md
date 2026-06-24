# Goal 541: First HIPRT Workload, 3D Ray-Triangle Hit Count

Date: 2026-04-18

Repository: `/Users/rl2025/rtdl_python_only`

Linux validation checkout: `/tmp/rtdl_goal541_hiprt_rayhit`

HIPRT SDK: `/home/lestat/vendor/hiprt-official/hiprtSdk-2.2.0e68f54`

## Goal

Implement the first bounded RTDL workload using HIPRT traversal, with CPU/oracle correctness before any broader backend integration.

The selected first workload is `ray_triangle_hit_count` for 3D rays and 3D triangles because it maps directly onto HIPRT triangle mesh geometry and `hiprtGeomTraversalAnyHit`.

## Implementation

Files changed:

- `/Users/rl2025/rtdl_python_only/src/native/rtdl_hiprt.cpp`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/hiprt_runtime.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py`
- `/Users/rl2025/rtdl_python_only/tests/goal541_hiprt_ray_hitcount_test.py`
- `/Users/rl2025/rtdl_python_only/Makefile`

Public API:

```python
import rtdsl as rt

rows = rt.ray_triangle_hit_count_hiprt(rays3d, triangles3d)
```

Scope:

- Supports `Ray3D` and `Triangle3D`.
- Rejects `Ray2D` and `Triangle` inputs explicitly.
- Uses HIPRT context creation through Orochi CUDA path.
- Builds a HIPRT triangle mesh from RTDL `Triangle3D` inputs.
- Compiles a HIPRT device kernel through Orochi/NVRTC.
- Runs `hiprtGeomTraversalAnyHit` per ray and emits `{ray_id, hit_count}` rows.

## Why 3D Only

RTDL's existing 2D `ray_triangle_hit_count` semantics are not a literal ray-vs-triangle-surface test. They treat the finite 2D ray as a segment and check intersection with a 2D triangle area or its edges.

HIPRT triangle geometry is naturally 3D ray-vs-triangle traversal. Forcing the 2D semantics into HIPRT triangle traversal would be misleading. Therefore, this first HIPRT workload is 3D-only.

## Linux Build

Command:

```bash
cd /tmp/rtdl_goal541_hiprt_rayhit
make build-hiprt HIPRT_PREFIX=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54
```

Result: `PASS`

The only diagnostic was the same vendor Orochi `fread` ignored-return warning seen in Goal 540. RTDL code compiled successfully.

## Linux Correctness Tests

Command:

```bash
cd /tmp/rtdl_goal541_hiprt_rayhit
export RTDL_HIPRT_LIB=$PWD/build/librtdl_hiprt.so
export LD_LIBRARY_PATH=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54/hiprt/linux64:${LD_LIBRARY_PATH:-}
PYTHONPATH=src:. python3 -m unittest tests.goal540_hiprt_probe_test tests.goal541_hiprt_ray_hitcount_test
```

Result:

```text
Ran 4 tests in 0.729s
OK
```

Coverage:

- HIPRT version probe.
- HIPRT context creation/destroy probe.
- 3D ray-triangle hit-count parity against `rt.ray_triangle_hit_count_cpu`.
- Explicit rejection of 2D inputs.

## Linux Randomized Smoke

Command shape:

```bash
cd /tmp/rtdl_goal541_hiprt_rayhit
export RTDL_HIPRT_LIB=$PWD/build/librtdl_hiprt.so
export LD_LIBRARY_PATH=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54/hiprt/linux64:${LD_LIBRARY_PATH:-}
PYTHONPATH=src:. python3 <randomized parity script>
```

Observed result:

```json
{
  "ray_count": 128,
  "triangle_count": 256,
  "parity": true,
  "total_hits_cpu": 155,
  "total_hits_hiprt": 155,
  "cpu_seconds": 0.019992178999928,
  "hiprt_seconds_including_compile_build_launch": 0.622283716000311
}
```

## Performance Interpretation

This is a correctness-first HIPRT workload. The measured HIPRT time includes:

- HIPRT context setup.
- Triangle mesh upload.
- HIPRT geometry build.
- runtime kernel compilation through Orochi/NVRTC.
- HIPRT traversal launch.
- result copy-back.

Therefore, this goal makes no performance-win claim. The current result is expected to be slower than the CPU oracle on small cases because kernel compilation and acceleration-structure build are paid inside the one-shot call.

## Explicit Non-Claims

- No AMD GPU validation.
- No HIPRT CPU fallback validation.
- No 2D HIPRT ray-triangle support.
- No general `rt.run_hiprt(...)` lowering integration yet.
- No performance claim beyond the measured one-shot timing above.
- No replacement of existing CPU, Embree, OptiX, or Vulkan behavior.

## Verdict

Implementation status: `PASS`

Goal 541 establishes the first genuine HIPRT workload path in RTDL: 3D ray-triangle hit-count through HIPRT triangle traversal, validated against the existing CPU oracle on Linux NVIDIA/CUDA.

Recommended next step: add a prepared/cached HIPRT execution object or integrate the workload into a `run_hiprt` dispatch path, so compile/build overhead can be separated from query timing.
