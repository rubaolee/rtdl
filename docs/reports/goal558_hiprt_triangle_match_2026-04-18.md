# Goal 558: HIPRT Triangle Match Backend

Date: 2026-04-18

## Scope

Goal 558 implements HIPRT support for the graph `triangle_match` workload.

This is a bounded correctness-first implementation. It does not use CPU fallback. It lowers CSR graph edges to source-keyed HIPRT AABB-list custom primitives, traverses one side of each seed edge through HIPRT AABB hits, filters the source match in the device kernel, refines the second adjacency on device against CSR arrays, then host-sorts candidate rows by seed order and `w` to match the CPU reference contract.

## Implementation

Changed files:

- `/Users/rl2025/rtdl_python_only/src/native/rtdl_hiprt.cpp`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/hiprt_runtime.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py`
- `/Users/rl2025/rtdl_python_only/tests/goal558_hiprt_triangle_match_test.py`

Native HIPRT path:

- `rtdl_hiprt_run_triangle_probe`
- `RtdlTriangleProbeKernel`
- `intersectRtdlTriangleGraphEdgeBySource` as the trivially accepting HIPRT custom intersector; source filtering happens in `RtdlTriangleProbeKernel`
- graph edge AABBs encoded as source-keyed AABB-list primitives
- device-side refinement checks whether `v -> w` exists in CSR
- host-side deterministic ordering and `unique` enforcement

Python path:

- `triangle_match_hiprt(graph, seeds, order="id_ascending", unique=True)`
- `rt.run_hiprt(...)` dispatch for `triangle_match`
- public export through `rtdsl.__init__`

## Correctness Semantics

The HIPRT output matches `rt.triangle_probe_cpu` for the supported contract:

- `order="id_ascending"`
- `unique=True` and `unique=False`
- skips `u == v`
- enforces `u < v < w` when `order="id_ascending"`
- preserves CPU reference ordering by seed order and ascending `w`
- emits rows with `u`, `v`, and `w`

## Validation Evidence

Local macOS Python-side validation:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal558_hiprt_triangle_match_test \
  tests.goal557_hiprt_bfs_test \
  tests.goal546_hiprt_api_parity_skeleton_test \
  tests.goal547_hiprt_correctness_matrix_test

Ran 16 tests in 0.010s
OK (skipped=8)
```

Linux HIPRT build:

```text
ssh lestat-lx1 'cd /tmp/rtdl_goal558_hiprt_triangle &&
  make build-hiprt HIPRT_PREFIX=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54'

build/librtdl_hiprt.so built successfully
```

Linux HIPRT focused validation:

```text
ssh lestat-lx1 'cd /tmp/rtdl_goal558_hiprt_triangle &&
  export RTDL_HIPRT_LIB=$PWD/build/librtdl_hiprt.so &&
  export LD_LIBRARY_PATH=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54/hiprt/linux64:${LD_LIBRARY_PATH:-} &&
  PYTHONPATH=src:. python3 -m unittest \
    tests.goal558_hiprt_triangle_match_test \
    tests.goal557_hiprt_bfs_test \
    tests.goal546_hiprt_api_parity_skeleton_test \
    tests.goal547_hiprt_correctness_matrix_test'

Ran 16 tests in 19.885s
OK
```

Linux v0.9 HIPRT matrix:

- Raw JSON: `/Users/rl2025/rtdl_python_only/docs/reports/goal558_hiprt_correctness_matrix_linux_2026-04-18.json`
- Summary: `pass=15`, `not_implemented=3`, `fail=0`, `hiprt_unavailable=0`
- Newly passing workload: `triangle_match`
- Remaining unimplemented workloads: `conjunctive_scan`, `grouped_count`, `grouped_sum`

## Honesty Boundary

This is a real HIPRT graph traversal path, but not yet a performance-forward triangle-counting system. The traversal discovers `u -> w` candidates via HIPRT custom primitives; the `v -> w` check is a bounded device-side CSR refinement. The implementation uses one device thread for deterministic bounded semantics and host-side final ordering. Current evidence proves correctness on the Linux NVIDIA CUDA-mode HIPRT path, not AMD GPU portability or RT-core acceleration.

## Codex Verdict

ACCEPT. Goal 558 is complete as a bounded correctness-first HIPRT `triangle_match` backend. It advances the HIPRT v0.9 matrix from 14 to 15 passing workloads without CPU fallback.
