# Goal 673: OptiX Prepacked Ray Cleanup

Date: 2026-04-20

## Scope

Goal 673 addresses the non-blocking findings from the Goal 672 external review.

Implemented:

- `PreparedRays2D` no longer retains a host `std::vector<GpuRay>` for the lifetime of the prepared ray buffer.
- `PreparedRays2D` now keeps only `ray_count` plus the device ray buffer.
- The packed-count C ABI now has explicit boundary-level guards for:
  - null `prepared_rays`
  - null `hit_count_out`
- The unpacked prepared-count C ABI now explicitly guards null `hit_count_out`.
- Added a portable Python lifecycle test that closed `OptixRay2DBuffer` objects are rejected by `count_packed`.

Touched files:

- `/Users/rl2025/rtdl_python_only/src/native/optix/rtdl_optix_workloads.cpp`
- `/Users/rl2025/rtdl_python_only/src/native/optix/rtdl_optix_api.cpp`
- `/Users/rl2025/rtdl_python_only/tests/goal671_optix_prepared_anyhit_count_test.py`

## Correctness Evidence

Local macOS:

```text
python3 -m py_compile \
  src/rtdsl/optix_runtime.py \
  src/rtdsl/__init__.py \
  tests/goal671_optix_prepared_anyhit_count_test.py

OK
```

```text
PYTHONPATH=src:. python3 -m unittest tests.goal671_optix_prepared_anyhit_count_test -v

Ran 7 tests in 0.000s
OK (skipped=2)
```

Linux native OptiX:

```text
Host path: /tmp/rtdl_goal673
Command: make build-optix
Result: build/librtdl_optix.so built successfully with nvcc.
```

```text
RTDL_OPTIX_LIB=/tmp/rtdl_goal673/build/librtdl_optix.so \
PYTHONPATH=src:. python3 -m unittest tests.goal671_optix_prepared_anyhit_count_test -v

Ran 7 tests in 0.306s
OK
```

Focused local regression:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal671_optix_prepared_anyhit_count_test \
  tests.goal548_hiprt_fixed_radius_3d_test \
  tests.goal549_hiprt_3d_knn_test \
  tests.goal555_hiprt_2d_neighbors_test -v

Ran 22 tests in 0.001s
OK (skipped=13)
```

Repository hygiene:

```text
git diff --check
OK
```

## Performance Sanity Check

After dropping the retained host ray vector, the Linux packed-count path still matches expected output and remains in the same or slightly faster range than Goal 672.

Workload:

- 8192 rays
- 2048 triangles
- dense all-hit case
- expected blocked count: `8192`

Raw packed-count timings:

```text
[0.000075169, 0.000066900, 0.000063705, 0.000063467, 0.000062119,
 0.000061733, 0.000061940, 0.000062241, 0.000060540, 0.000061838]
```

Median:

```text
0.000062180 s
```

## Claim Boundary

This is a cleanup and memory-footprint improvement for the Goal 672 prepared+prepacked OptiX path. It does not expand the performance claim beyond Goal 672:

- repeated prepared-scene plus prepacked-ray scalar count only
- not one-shot queries
- not changing ray batches
- not full row-output workloads
- not all OptiX workloads
- not other engines

