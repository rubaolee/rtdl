# Goal 557: HIPRT BFS Discover Backend

Date: 2026-04-18

## Scope

Goal 557 implements the first HIPRT graph workload for v0.9: `bfs_discover`.

The implementation is correctness-first and bounded. It does not use a CPU fallback. It lowers CSR graph edges to HIPRT AABB-list custom primitives keyed by source vertex, probes each frontier vertex through HIPRT traversal, refines visited/dedupe semantics in the HIPRT device kernel, and sorts host-side output rows by the CPU reference order `(level, dst_vertex, src_vertex)`.

## Implementation

Changed files:

- `/Users/rl2025/rtdl_python_only/src/native/rtdl_hiprt.cpp`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/hiprt_runtime.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py`
- `/Users/rl2025/rtdl_python_only/tests/goal546_hiprt_api_parity_skeleton_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal557_hiprt_bfs_test.py`

Native HIPRT path:

- `rtdl_hiprt_run_bfs_expand`
- `RtdlBfsExpandKernel`
- `intersectRtdlGraphEdgeBySource`
- graph edge AABBs encoded as source-keyed AABB-list primitives
- no CPU fallback inside `run_hiprt`

Python path:

- `bfs_expand_hiprt(graph, frontier, visited, dedupe=True)`
- `rt.run_hiprt(...)` dispatch for `bfs_discover`
- public export through `rtdsl.__init__`

## Correctness Semantics

The HIPRT output matches `rt.bfs_expand_cpu`:

- validates CSR graph and frontier/visited vertex IDs
- skips already visited vertices
- respects `dedupe=True` global discovery within one BFS step
- supports `dedupe=False` duplicate discovery behavior
- emits rows with `src_vertex`, `dst_vertex`, and `level`
- sorts final rows by `(level, dst_vertex, src_vertex)` to match the CPU reference contract

## Validation Evidence

Local macOS Python-side validation:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal546_hiprt_api_parity_skeleton_test \
  tests.goal557_hiprt_bfs_test \
  tests.goal547_hiprt_correctness_matrix_test

Ran 12 tests in 0.009s
OK (skipped=4)
```

Linux HIPRT build:

```text
ssh lestat-lx1 'cd /tmp/rtdl_goal557_hiprt_bfs &&
  make build-hiprt HIPRT_PREFIX=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54'

build/librtdl_hiprt.so built successfully
```

Linux HIPRT focused validation:

```text
ssh lestat-lx1 'cd /tmp/rtdl_goal557_hiprt_bfs &&
  export RTDL_HIPRT_LIB=$PWD/build/librtdl_hiprt.so &&
  export LD_LIBRARY_PATH=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54/hiprt/linux64:${LD_LIBRARY_PATH:-} &&
  PYTHONPATH=src:. python3 -m unittest \
    tests.goal557_hiprt_bfs_test \
    tests.goal546_hiprt_api_parity_skeleton_test \
    tests.goal547_hiprt_correctness_matrix_test'

Ran 12 tests in 16.745s
OK
```

Linux v0.9 HIPRT matrix:

- Raw JSON: `/Users/rl2025/rtdl_python_only/docs/reports/goal557_hiprt_correctness_matrix_linux_2026-04-18.json`
- Summary: `pass=14`, `not_implemented=4`, `fail=0`, `hiprt_unavailable=0`
- Newly passing workload: `bfs_discover`
- Remaining unimplemented workloads: `triangle_match`, `conjunctive_scan`, `grouped_count`, `grouped_sum`

## Honesty Boundary

This is a real HIPRT traversal implementation, but it is not yet a performance-forward graph algorithm. It uses a single device thread for deterministic BFS-step semantics and host-side final sorting. Current evidence proves correctness and backend integration on the Linux NVIDIA CUDA-mode HIPRT path, not AMD GPU portability or RT-core acceleration.

## Codex Verdict

ACCEPT. Goal 557 is complete as a bounded correctness-first HIPRT `bfs_discover` backend. It advances the HIPRT v0.9 matrix from 13 to 14 passing workloads without CPU fallback.
