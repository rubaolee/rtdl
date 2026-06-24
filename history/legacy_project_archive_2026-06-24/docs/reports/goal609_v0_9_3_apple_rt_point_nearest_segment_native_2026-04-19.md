# Goal609: v0.9.3 Apple RT Point-Nearest-Segment Native Candidate Discovery

Date: 2026-04-19

Status: accepted with 2-AI consensus (Codex + Gemini 2.5 Flash).

## Scope

Goal609 extends the Apple Metal/MPS RT backend to cover the bounded 2D `point_nearest_segment` workload.

This is a native candidate-discovery implementation. It does not claim full GPU-resident ranking or broad performance improvement.

## Implementation

Files changed:

- `/Users/rl2025/rtdl_python_only/src/rtdsl/apple_rt_runtime.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py`
- `/Users/rl2025/rtdl_python_only/tests/goal603_apple_rt_native_contract_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal609_apple_rt_point_nearest_segment_native_test.py`

Lowering:

- Each build segment is converted to an expanded 2D bounding box.
- The existing Apple MPS point-to-box traversal path discovers point/segment candidate pairs.
- The expansion radius is conservatively derived from the combined point/segment coordinate span so correctness does not depend on an approximate nearest radius.
- Exact CPU point-segment distance ranking then selects one nearest segment per point, including the existing lower-segment-id tie rule.

Contract updates:

- `apple_rt_support_matrix()` marks `point_nearest_segment` as Apple RT native candidate discovery for `Point2D/Segment2D`.
- `run_apple_rt(..., native_only=True)` dispatches `point_nearest_segment` for 2D point/segment inputs.
- `point_nearest_segment_apple_rt` is exported from `rtdsl`.

## Validation

Focused tests:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal609_apple_rt_point_nearest_segment_native_test tests.goal603_apple_rt_native_contract_test -v
```

Result:

```text
Ran 7 tests in 0.012s
OK
```

Broader Apple-focused suite:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal578_apple_rt_backend_test tests.goal609_apple_rt_point_nearest_segment_native_test tests.goal608_apple_rt_segment_polygon_native_test tests.goal607_apple_rt_point_in_polygon_positive_native_test tests.goal606_apple_rt_point_neighbor_3d_native_test tests.goal605_apple_rt_point_neighbor_2d_native_test tests.goal604_apple_rt_ray_hitcount_2d_native_test tests.goal603_apple_rt_native_contract_test tests.goal582_apple_rt_full_surface_dispatch_test -v
```

Result:

```text
Ran 34 tests in 0.123s
OK
```

Mechanical checks:

```text
PYTHONPATH=src:. python3 -m py_compile src/rtdsl/apple_rt_runtime.py src/rtdsl/__init__.py tests/goal608_apple_rt_segment_polygon_native_test.py tests/goal609_apple_rt_point_nearest_segment_native_test.py tests/goal603_apple_rt_native_contract_test.py
git diff --check
```

Result: both passed with no output.

## Honesty Boundary

- Apple MPS RT performs candidate discovery.
- Exact nearest-distance ranking is still CPU reference logic.
- This goal is correctness/coverage work, not an Apple performance-win claim.
- The conservative candidate radius can overproduce candidates; this is acceptable for current correctness coverage but should not be marketed as optimized.

## External Review

Gemini 2.5 Flash reviewed Goals 608-612 in `/Users/rl2025/rtdl_python_only/docs/reports/goal608_612_gemini_quick_review_2026-04-19.md` and returned ACCEPT with no technical blockers. Goal609 is closed under the 2-AI rule.
