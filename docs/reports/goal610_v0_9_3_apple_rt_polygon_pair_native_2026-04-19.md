# Goal610: v0.9.3 Apple RT Polygon-Pair Overlap and Jaccard Native Candidate Discovery

Date: 2026-04-19

Status: accepted with 2-AI consensus (Codex + Gemini 2.5 Flash).

## Scope

Goal610 extends the Apple Metal/MPS RT backend to cover bounded 2D polygon-pair analytical workloads:

- `polygon_pair_overlap_area_rows`
- `polygon_set_jaccard`

This is native candidate-discovery coverage. Exact unit-cell area and Jaccard aggregation remain CPU-refined, matching the existing bounded reference semantics.

## Implementation

Files changed:

- `/Users/rl2025/rtdl_python_only/src/rtdsl/apple_rt_runtime.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py`
- `/Users/rl2025/rtdl_python_only/tests/goal603_apple_rt_native_contract_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal610_apple_rt_polygon_pair_native_test.py`

Lowering:

- Polygon-pair candidates are decomposed into existing Apple RT native candidate paths:
  - left polygon edges against right polygons through segment-polygon MPS traversal;
  - right polygon edges against left polygons through segment-polygon MPS traversal;
  - left vertices inside right polygons through point-polygon MPS traversal;
  - right vertices inside left polygons through point-polygon MPS traversal.
- Candidate pairs are deduplicated and then exact CPU unit-cell area/Jaccard refinement computes the final rows.
- The implementation preserves the existing integer-grid polygon-area contract enforced by the CPU reference.

Contract updates:

- `apple_rt_support_matrix()` marks `polygon_pair_overlap_area_rows` and `polygon_set_jaccard` as Apple RT native candidate-discovery rows for `Polygon2D/Polygon2D`.
- `run_apple_rt(..., native_only=True)` dispatches these predicates for 2D polygon inputs.
- `polygon_pair_overlap_area_rows_apple_rt` and `polygon_set_jaccard_apple_rt` are exported from `rtdsl`.

## Validation

Focused tests:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal610_apple_rt_polygon_pair_native_test tests.goal603_apple_rt_native_contract_test -v
```

Result:

```text
Ran 7 tests in 0.055s
OK
```

Broader Apple-focused suite:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal578_apple_rt_backend_test tests.goal610_apple_rt_polygon_pair_native_test tests.goal609_apple_rt_point_nearest_segment_native_test tests.goal608_apple_rt_segment_polygon_native_test tests.goal607_apple_rt_point_in_polygon_positive_native_test tests.goal606_apple_rt_point_neighbor_3d_native_test tests.goal605_apple_rt_point_neighbor_2d_native_test tests.goal604_apple_rt_ray_hitcount_2d_native_test tests.goal603_apple_rt_native_contract_test tests.goal582_apple_rt_full_surface_dispatch_test -v
```

Result:

```text
Ran 37 tests in 0.139s
OK
```

Mechanical checks:

```text
PYTHONPATH=src:. python3 -m py_compile src/rtdsl/apple_rt_runtime.py src/rtdsl/__init__.py tests/goal608_apple_rt_segment_polygon_native_test.py tests/goal609_apple_rt_point_nearest_segment_native_test.py tests/goal610_apple_rt_polygon_pair_native_test.py tests/goal603_apple_rt_native_contract_test.py
git diff --check
```

Result: both passed with no output.

## Honesty Boundary

- Apple MPS RT performs candidate discovery through point-polygon and segment-polygon traversal.
- Exact unit-cell area and Jaccard aggregation remain CPU-refined.
- The workload remains bounded to the existing integer-grid polygon-area semantics.
- This is not a broad Apple performance claim.
- Full `overlay_compose` remains compatibility-only after this goal because it intentionally emits all polygon-pair rows, including non-overlap rows, and needs a separate native flag-materialization design.

## External Review

Gemini 2.5 Flash reviewed Goals 608-612 in `/Users/rl2025/rtdl_python_only/docs/reports/goal608_612_gemini_quick_review_2026-04-19.md` and returned ACCEPT with no technical blockers. Goal610 is closed under the 2-AI rule.
