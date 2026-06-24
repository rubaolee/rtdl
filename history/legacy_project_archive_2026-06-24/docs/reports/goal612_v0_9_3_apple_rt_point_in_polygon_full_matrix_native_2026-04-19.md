# Goal612: v0.9.3 Apple RT Point-In-Polygon Full-Matrix Native Support

Date: 2026-04-19

Status: accepted with 2-AI consensus (Codex + Gemini 2.5 Flash).

## Scope

Goal612 extends the existing Apple Metal/MPS RT point-in-polygon support from sparse `positive_hits` output to the default `full_matrix` output.

## Implementation

Files changed:

- `/Users/rl2025/rtdl_python_only/src/rtdsl/apple_rt_runtime.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py`
- `/Users/rl2025/rtdl_python_only/tests/goal607_apple_rt_point_in_polygon_positive_native_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal582_apple_rt_full_surface_dispatch_test.py`

Lowering:

- Apple MPS RT still discovers positive point/polygon hits through polygon bounding-box traversal.
- Exact point-in-polygon refinement decides the true positive set.
- CPU materializes the required full point/polygon matrix and fills false rows with `contains = 0`.

Contract updates:

- `apple_rt_support_matrix()` now reports `point_in_polygon` native-only support for both `positive_hits` and `full_matrix`.
- `run_apple_rt(..., native_only=True)` accepts default full-matrix point-in-polygon kernels for 2D point/polygon inputs.
- `point_in_polygon_full_matrix_apple_rt` is exported from `rtdsl`.

## Validation

Focused tests:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal607_apple_rt_point_in_polygon_positive_native_test tests.goal603_apple_rt_native_contract_test -v
```

Result:

```text
Ran 8 tests in 0.024s
OK
```

Broader Apple-focused suite:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal578_apple_rt_backend_test tests.goal611_apple_rt_overlay_compose_native_test tests.goal610_apple_rt_polygon_pair_native_test tests.goal609_apple_rt_point_nearest_segment_native_test tests.goal608_apple_rt_segment_polygon_native_test tests.goal607_apple_rt_point_in_polygon_positive_native_test tests.goal606_apple_rt_point_neighbor_3d_native_test tests.goal605_apple_rt_point_neighbor_2d_native_test tests.goal604_apple_rt_ray_hitcount_2d_native_test tests.goal603_apple_rt_native_contract_test tests.goal582_apple_rt_full_surface_dispatch_test -v
```

Result:

```text
Ran 40 tests in 0.186s
OK
```

Mechanical checks:

```text
PYTHONPATH=src:. python3 -m py_compile src/rtdsl/apple_rt_runtime.py src/rtdsl/__init__.py tests/goal607_apple_rt_point_in_polygon_positive_native_test.py tests/goal582_apple_rt_full_surface_dispatch_test.py tests/goal603_apple_rt_native_contract_test.py
git diff --check
```

Result: both passed with no output.

## Honesty Boundary

- Apple MPS RT discovers positive point/polygon hits.
- CPU materializes false full-matrix rows.
- This is native-assisted correctness coverage, not a broad Apple performance claim.

## External Review

Gemini 2.5 Flash reviewed Goals 608-612 in `/Users/rl2025/rtdl_python_only/docs/reports/goal608_612_gemini_quick_review_2026-04-19.md` and returned ACCEPT with no technical blockers. Goal612 is closed under the 2-AI rule.
