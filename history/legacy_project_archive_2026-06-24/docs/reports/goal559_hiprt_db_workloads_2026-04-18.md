# Goal 559: HIPRT DB Workload Backends

Date: 2026-04-18

## Scope

Goal 559 implements HIPRT support for the remaining v0.9 database-style workloads:

- `conjunctive_scan`
- `grouped_count`
- `grouped_sum`

This completes the v0.9 HIPRT workload matrix at the API/runtime correctness level.

## Implementation

Changed files:

- `/Users/rl2025/rtdl_python_only/src/native/rtdl_hiprt.cpp`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/hiprt_runtime.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py`
- `/Users/rl2025/rtdl_python_only/tests/goal546_hiprt_api_parity_skeleton_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal547_hiprt_correctness_matrix_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal559_hiprt_db_workloads_test.py`

Native HIPRT path:

- `rtdl_hiprt_run_conjunctive_scan`
- `rtdl_hiprt_run_grouped_count`
- `rtdl_hiprt_run_grouped_sum`
- `RtdlDbMatchKernel`
- `intersectRtdlDbRowAabb`
- one HIPRT AABB custom primitive per denormalized table row
- device-side predicate matching against encoded row values
- native C++ host-side row-id projection and grouped aggregation from matched row indices

Python path:

- `conjunctive_scan_hiprt(table_rows, predicates)`
- `grouped_count_hiprt(table_rows, query)`
- `grouped_sum_hiprt(table_rows, query)`
- `rt.run_hiprt(...)` dispatch for all three DB predicates
- public exports through `rtdsl.__init__`

## Correctness Semantics

The HIPRT DB outputs match the Python reference for the supported first-wave contract:

- denormalized rows with `row_id`
- predicate operators: `eq`, `lt`, `le`, `gt`, `ge`, `between`
- exact text support through the existing RTDL text-to-integer encoding path
- exactly one group key for grouped workloads
- numeric grouped sums
- empty table inputs return empty rows

## Validation Evidence

Local macOS Python-side validation:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal559_hiprt_db_workloads_test \
  tests.goal558_hiprt_triangle_match_test \
  tests.goal557_hiprt_bfs_test \
  tests.goal546_hiprt_api_parity_skeleton_test \
  tests.goal547_hiprt_correctness_matrix_test

Ran 23 tests in 0.011s
OK (skipped=15)
```

Linux HIPRT build:

```text
ssh lestat-lx1 'cd /tmp/rtdl_goal559_hiprt_db &&
  make build-hiprt HIPRT_PREFIX=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54'

build/librtdl_hiprt.so built successfully
```

Linux HIPRT focused validation:

```text
ssh lestat-lx1 'cd /tmp/rtdl_goal559_hiprt_db &&
  export RTDL_HIPRT_LIB=$PWD/build/librtdl_hiprt.so &&
  export LD_LIBRARY_PATH=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54/hiprt/linux64:${LD_LIBRARY_PATH:-} &&
  PYTHONPATH=src:. python3 -m unittest \
    tests.goal559_hiprt_db_workloads_test \
    tests.goal558_hiprt_triangle_match_test \
    tests.goal557_hiprt_bfs_test \
    tests.goal546_hiprt_api_parity_skeleton_test \
    tests.goal547_hiprt_correctness_matrix_test'

Ran 23 tests in 27.387s
OK
```

Linux v0.9 HIPRT matrix:

- Raw JSON: `/Users/rl2025/rtdl_python_only/docs/reports/goal559_hiprt_correctness_matrix_linux_2026-04-18.json`
- Summary: `pass=18`, `not_implemented=0`, `fail=0`, `hiprt_unavailable=0`
- Newly passing workloads: `conjunctive_scan`, `grouped_count`, `grouped_sum`

## Honesty Boundary

This is a real HIPRT traversal path, but it is correctness-first rather than performance-forward. The current DB lowering uses broad row AABBs so one probe ray visits all row primitives, then predicate refinement happens in the device kernel. Native C++ host code performs projection and grouped aggregation from the matched row indices. Python is used for input encoding and output decoding only; it is not used as a CPU fallback for the workload result.

Current evidence proves correctness on the Linux NVIDIA CUDA-mode HIPRT path. It does not prove AMD GPU portability, RT-core acceleration, or performance superiority over OptiX, Vulkan, Embree, PostgreSQL, or CPU baselines.

## Codex Verdict

ACCEPT. Goal 559 completes HIPRT support for the v0.9 target workload matrix at the bounded correctness/API level, advancing the matrix to 18 passing workloads with no unimplemented entries and no CPU fallback.
