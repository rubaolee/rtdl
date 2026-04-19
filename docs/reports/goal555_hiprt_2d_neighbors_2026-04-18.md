# Goal 555: HIPRT 2D Fixed-Radius and KNN

## Scope

Goal 555 adds native HIPRT support for:

- `fixed_radius_neighbors` on `Point2DLayout`
- `knn_rows` on `Point2DLayout`
- `bounded_knn_rows` on `Point2DLayout` through the same bounded-radius helper path

This closes two more v0.9 correctness-matrix rows: `fixed_radius_neighbors_2d` and `knn_rows_2d`.

## Implementation

Changed files:

- `/Users/rl2025/rtdl_python_only/src/native/rtdl_hiprt.cpp`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/hiprt_runtime.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py`
- `/Users/rl2025/rtdl_python_only/tests/goal555_hiprt_2d_neighbors_test.py`

Lowering strategy:

- Build-side 2D search points are encoded as HIPRT AABB-list custom primitives expanded by the query radius.
- Probe-side 2D query points are encoded as zero-length rays at `(x, y, 0)`.
- HIPRT custom intersection `intersectRtdlPointRadius2D` computes exact 2D Euclidean distance on device and rejects candidates outside radius.
- The kernel keeps the nearest `k_max <= 64` candidates per query with deterministic distance/id ordering, matching the existing 3D implementation.
- `knn_rows_2d_hiprt` uses a conservative global radius to include all search points, then reuses the bounded-radius top-k kernel.

Honesty boundary:

- This is real HIPRT traversal/refinement; no CPU fallback is used.
- Current validation is HIPRT/Orochi CUDA mode on NVIDIA GTX 1070, not AMD GPU.
- GTX 1070 has no RT cores, so this goal claims correctness coverage and backend parity, not RT-core speedup.

## Validation

Local macOS syntax/API validation:

```text
python3 -m py_compile src/rtdsl/__init__.py src/rtdsl/hiprt_runtime.py
PYTHONPATH=src:. python3 -m unittest tests.goal555_hiprt_2d_neighbors_test tests.goal554_hiprt_segment_polygon_test tests.goal547_hiprt_correctness_matrix_test
Ran 12 tests in 0.008s
OK (skipped=10)
```

Linux HIPRT build:

```text
make build-hiprt HIPRT_PREFIX=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54
```

Linux native HIPRT focused validation:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal555_hiprt_2d_neighbors_test
Ran 5 tests in 2.463s
OK
```

Expanded HIPRT correctness matrix:

- JSON: `/Users/rl2025/rtdl_python_only/docs/reports/goal555_hiprt_correctness_matrix_linux_2026-04-18.json`
- Summary: `pass=12`, `not_implemented=6`, `hiprt_unavailable=0`, `fail=0`
- Newly passing workloads:
  - `fixed_radius_neighbors_2d`
  - `knn_rows_2d`

## Status

Codex verdict: ACCEPT.

External AI review:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal555_external_review_2026-04-18.md`
- Verdict: ACCEPT, no blockers.

Final status: 2-AI consensus ACCEPT.
