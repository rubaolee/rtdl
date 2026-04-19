# Goal 554: HIPRT Segment/Polygon Workloads

## Scope

Goal 554 adds native HIPRT support for:

- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`

This closes the two segment/polygon entries from the v0.9 HIPRT correctness matrix without CPU fallback.

## Implementation

Changed files:

- `/Users/rl2025/rtdl_python_only/src/native/rtdl_hiprt.cpp`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/hiprt_runtime.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py`
- `/Users/rl2025/rtdl_python_only/tests/goal554_hiprt_segment_polygon_test.py`

Lowering strategy:

- Build-side polygons are encoded as HIPRT AABB-list custom primitives.
- Probe-side segments are encoded as finite rays from `(x0, y0, 0)` with direction `(x1 - x0, y1 - y0, 0)` and `maxT = 1`.
- HIPRT custom intersection `intersectRtdlSegmentPolygon2D` performs device-side exact refinement:
  - endpoint-in-polygon test
  - segment-vs-polygon-edge intersection test
  - inclusive boundary semantics
- `segment_polygon_hitcount` emits one row per input segment.
- `segment_polygon_anyhit_rows` emits positive `(segment_id, polygon_id)` rows, then host-compacts and sorts by input segment order and polygon order to match CPU reference ordering.

Honesty boundary:

- This is a real HIPRT traversal/refinement backend path.
- The validation host is NVIDIA GTX 1070 through HIPRT/Orochi CUDA mode, not AMD GPU.
- GTX 1070 has no RT cores; this goal claims correctness coverage, not RT-core performance speedup.

## Validation

Local macOS syntax/API validation:

```text
python3 -m py_compile src/rtdsl/hiprt_runtime.py tests/goal554_hiprt_segment_polygon_test.py scripts/goal547_hiprt_correctness_matrix.py
PYTHONPATH=src:. python3 -m unittest tests.goal554_hiprt_segment_polygon_test tests.goal546_hiprt_api_parity_skeleton_test tests.goal547_hiprt_correctness_matrix_test
Ran 13 tests in 0.007s
OK (skipped=5)
```

Linux HIPRT build:

```text
make build-hiprt HIPRT_PREFIX=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54
```

Linux native HIPRT focused validation:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal554_hiprt_segment_polygon_test
Ran 5 tests in 2.769s
OK
```

Linux native HIPRT post-sync validation:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal554_hiprt_segment_polygon_test tests.goal547_hiprt_correctness_matrix_test
Ran 7 tests in 12.559s
OK
```

Expanded HIPRT correctness matrix:

- JSON: `/Users/rl2025/rtdl_python_only/docs/reports/goal554_hiprt_correctness_matrix_linux_2026-04-18.json`
- Summary: `pass=10`, `not_implemented=8`, `hiprt_unavailable=0`, `fail=0`
- Newly passing workloads:
  - `segment_polygon_hitcount`
  - `segment_polygon_anyhit_rows`

## Status

Codex verdict: ACCEPT.

External AI review:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal554_external_review_2026-04-18.md`
- Verdict: ACCEPT, no blockers.

Post-review cleanup:

- Fixed two pre-existing indentation style issues in `src/rtdsl/hiprt_runtime.py` `finally` blocks noted by Claude.
- Re-ran local validation:

```text
python3 -m py_compile src/rtdsl/hiprt_runtime.py
PYTHONPATH=src:. python3 -m unittest tests.goal554_hiprt_segment_polygon_test tests.goal546_hiprt_api_parity_skeleton_test tests.goal547_hiprt_correctness_matrix_test
Ran 13 tests in 0.006s
OK (skipped=5)
```

Final status: 2-AI consensus ACCEPT.
