# Goal 556: HIPRT Overlay Compose

## Scope

Goal 556 adds native HIPRT support for `overlay_compose` on `Polygon2DRef` inputs.

This closes the last 2D geometry-only v0.9 HIPRT correctness-matrix gap.

## Implementation

Changed files:

- `/Users/rl2025/rtdl_python_only/src/native/rtdl_hiprt.cpp`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/hiprt_runtime.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py`
- `/Users/rl2025/rtdl_python_only/tests/goal546_hiprt_api_parity_skeleton_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal556_hiprt_overlay_test.py`

Lowering strategy:

- Build-side right polygons are represented as HIPRT AABB-list custom primitives.
- This first implementation uses broad candidate AABBs that include every left polygon first vertex, so every left/right pair is visited by HIPRT traversal.
- Device-side refinement computes the CPU-compatible overlay seed flags:
  - `requires_lsi`: any left polygon edge intersects any right polygon edge.
  - `requires_pip`: the left first vertex is inside the right polygon, or the right first vertex is inside the left polygon.
- Output is the full `left_count * right_count` matrix in input order.

Honesty boundary:

- This is a real HIPRT traversal/refinement path and uses no CPU fallback.
- It is correctness-first and intentionally broad-candidate; it is not yet a performance-forward overlay index.
- Current validation is HIPRT/Orochi CUDA mode on NVIDIA GTX 1070, not AMD GPU.
- GTX 1070 has no RT cores, so this goal claims correctness coverage and backend parity, not RT-core speedup.

## Validation

Local macOS syntax/API validation:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal546_hiprt_api_parity_skeleton_test tests.goal556_hiprt_overlay_test tests.goal555_hiprt_2d_neighbors_test tests.goal547_hiprt_correctness_matrix_test
Ran 16 tests in 0.010s
OK (skipped=8)
```

Linux HIPRT build:

```text
make build-hiprt HIPRT_PREFIX=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54
```

Linux native HIPRT focused validation:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal556_hiprt_overlay_test
Ran 3 tests in 1.388s
OK
```

Expanded HIPRT correctness matrix:

- JSON: `/Users/rl2025/rtdl_python_only/docs/reports/goal556_hiprt_correctness_matrix_linux_2026-04-18.json`
- Summary: `pass=13`, `not_implemented=5`, `hiprt_unavailable=0`, `fail=0`
- Newly passing workload:
  - `overlay_compose`

## Status

Codex verdict: ACCEPT.

External AI review:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal556_external_review_2026-04-18.md`
- Verdict: ACCEPT, no blockers.
- Noted non-blocking caveats: broad-candidate `O(left * right)` design, float device precision consistent with other 2D HIPRT paths, AMD GPU untested.

Final status: 2-AI consensus ACCEPT.
