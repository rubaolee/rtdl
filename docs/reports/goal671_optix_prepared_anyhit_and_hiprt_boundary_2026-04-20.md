# Goal 671: OptiX Prepared Any-Hit Count and HIPRT Boundary Guard

Date: 2026-04-20

## Scope

This goal implements the first concrete follow-up from the Goal 670 engine optimization roadmap.

Implemented:

- HIPRT regression tests that prove oversized `k_max` / `k` requests are rejected before backend execution.
- OptiX prepared 2-D ray-triangle any-hit scalar count API:
  - C ABI:
    - `/Users/rl2025/rtdl_python_only/src/native/optix/rtdl_optix_prelude.h`
    - `/Users/rl2025/rtdl_python_only/src/native/optix/rtdl_optix_api.cpp`
    - `/Users/rl2025/rtdl_python_only/src/native/optix/rtdl_optix_workloads.cpp`
    - `/Users/rl2025/rtdl_python_only/src/native/optix/rtdl_optix_core.cpp`
  - Python API:
    - `/Users/rl2025/rtdl_python_only/src/rtdsl/optix_runtime.py`
    - `/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py`
  - Test:
    - `/Users/rl2025/rtdl_python_only/tests/goal671_optix_prepared_anyhit_count_test.py`
- Additional HIPRT boundary tests:
  - `/Users/rl2025/rtdl_python_only/tests/goal549_hiprt_3d_knn_test.py`
  - `/Users/rl2025/rtdl_python_only/tests/goal555_hiprt_2d_neighbors_test.py`

## OptiX API Added

Python:

```python
prepared = rt.prepare_optix_ray_triangle_any_hit_2d(triangles)
blocked_count = prepared.count(rays)
prepared.close()
```

Native:

```c
int rtdl_optix_prepare_ray_anyhit_2d(
    const RtdlTriangle* triangles,
    size_t triangle_count,
    void** prepared_out,
    char* error_out,
    size_t error_size);

int rtdl_optix_count_prepared_ray_anyhit_2d(
    void* prepared,
    const RtdlRay2D* rays,
    size_t ray_count,
    size_t* hit_count_out,
    char* error_out,
    size_t error_size);

void rtdl_optix_destroy_prepared_ray_anyhit_2d(void* prepared);
```

The prepared handle owns the triangle upload and OptiX BVH. The count call uploads each ray batch and returns a scalar count of rays with at least one accepted hit.

## Correctness Evidence

Local macOS:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal671_optix_prepared_anyhit_count_test \
  tests.goal548_hiprt_fixed_radius_3d_test \
  tests.goal549_hiprt_3d_knn_test \
  tests.goal555_hiprt_2d_neighbors_test -v

Ran 20 tests in 0.001s
OK (skipped=12)
```

Local compile checks:

```text
python3 -m py_compile \
  src/rtdsl/optix_runtime.py \
  src/rtdsl/hiprt_runtime.py \
  src/rtdsl/__init__.py \
  tests/goal671_optix_prepared_anyhit_count_test.py \
  tests/goal549_hiprt_3d_knn_test.py \
  tests/goal555_hiprt_2d_neighbors_test.py

OK
```

Linux native OptiX:

```text
Host path: /tmp/rtdl_goal671
Command: make build-optix
Result: build/librtdl_optix.so built successfully with nvcc.
```

```text
RTDL_OPTIX_LIB=/tmp/rtdl_goal671/build/librtdl_optix.so \
PYTHONPATH=src:. python3 -m unittest \
  tests.goal632_ray_triangle_any_hit_test \
  tests.goal671_optix_prepared_anyhit_count_test -v

Ran 8 tests in 0.406s
OK
```

Repository hygiene:

```text
git diff --check
OK
```

## Performance Observation

A quick Linux repeat-query probe used 8192 rays and 2048 triangles. Both paths returned the same blocked count.

```text
unprepared_anyhit_row_seconds:
  [0.005294168, 0.005016175, 0.005023658, 0.004979235, 0.004987958]

prepared_anyhit_count_seconds:
  [0.014995440, 0.008409884, 0.008202387, 0.008060210, 0.008133568]

blocked_count: 8192
```

Conclusion: this API is correctness-ready, but it is not yet a performance win on this dense sample. The scalar-count path avoids host row materialization, but the current OptiX kernel uses one global atomic increment per hit ray; dense all-hit workloads create atomic contention. Do not claim a speedup from this Goal 671 implementation.

## Honest Status

Accepted as implementation progress:

- HIPRT guard coverage is improved.
- OptiX now has a prepared scalar any-hit count surface.
- Linux native OptiX build and correctness tests pass.

Not accepted as a performance closure:

- The new OptiX prepared count API does not yet beat the existing unprepared row path on the dense probe.
- Further OptiX optimization should replace global per-hit atomics with lower-contention aggregation or a packed bitset/popcount strategy before making any performance claim.

