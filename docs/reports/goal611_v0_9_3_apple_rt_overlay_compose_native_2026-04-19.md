# Goal611: v0.9.3 Apple RT Overlay Compose Native Flag Discovery

Date: 2026-04-19

Status: accepted with 2-AI consensus (Codex + Gemini 2.5 Flash).

## Scope

Goal611 extends the Apple Metal/MPS RT backend to support `overlay_compose` through native flag discovery.

Unlike sparse overlap workloads, `overlay_compose` intentionally emits every left/right polygon pair. Therefore the honest Apple RT contract is native discovery of the `requires_lsi` and `requires_pip` flags, with CPU materialization of the complete pair matrix.

## Implementation

Files changed:

- `/Users/rl2025/rtdl_python_only/src/rtdsl/apple_rt_runtime.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py`
- `/Users/rl2025/rtdl_python_only/tests/goal603_apple_rt_native_contract_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal611_apple_rt_overlay_compose_native_test.py`

Lowering:

- Polygon edges are lowered to segment sets.
- Apple RT segment-intersection traversal discovers polygon pairs requiring line-segment intersection work.
- Apple RT point-in-polygon traversal discovers polygon pairs requiring containment work.
- CPU materializes every left/right pair and assigns `requires_lsi` / `requires_pip` flags from the native-discovered sets.

Contract updates:

- `apple_rt_support_matrix()` marks `overlay_compose` as Apple RT native flag/candidate discovery for `Polygon2D/Polygon2D`.
- `run_apple_rt(..., native_only=True)` dispatches `overlay_compose` for 2D polygon inputs.
- `overlay_compose_apple_rt` is exported from `rtdsl`.

## Validation

Focused tests:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal611_apple_rt_overlay_compose_native_test tests.goal603_apple_rt_native_contract_test -v
```

Result:

```text
Ran 6 tests in 0.039s
OK
```

Broader Apple-focused suite:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal578_apple_rt_backend_test tests.goal611_apple_rt_overlay_compose_native_test tests.goal610_apple_rt_polygon_pair_native_test tests.goal609_apple_rt_point_nearest_segment_native_test tests.goal608_apple_rt_segment_polygon_native_test tests.goal607_apple_rt_point_in_polygon_positive_native_test tests.goal606_apple_rt_point_neighbor_3d_native_test tests.goal605_apple_rt_point_neighbor_2d_native_test tests.goal604_apple_rt_ray_hitcount_2d_native_test tests.goal603_apple_rt_native_contract_test tests.goal582_apple_rt_full_surface_dispatch_test -v
```

Result:

```text
Ran 39 tests in 0.216s
OK
```

Mechanical checks:

```text
PYTHONPATH=src:. python3 -m py_compile src/rtdsl/apple_rt_runtime.py src/rtdsl/__init__.py tests/goal608_apple_rt_segment_polygon_native_test.py tests/goal609_apple_rt_point_nearest_segment_native_test.py tests/goal610_apple_rt_polygon_pair_native_test.py tests/goal611_apple_rt_overlay_compose_native_test.py tests/goal603_apple_rt_native_contract_test.py
git diff --check
```

Result: both passed with no output.

## Honesty Boundary

- Apple MPS RT discovers overlay flags through segment-intersection and point-in-polygon traversal.
- CPU still materializes the all-pairs overlay rows.
- This goal is correctness/coverage work, not an Apple performance claim.

## Remaining Apple RT Native Coverage After Goal611

Native candidate/flag discovery rows: 13.

Compatibility-only rows: 5.

- `bfs_discover`
- `conjunctive_scan`
- `grouped_count`
- `grouped_sum`
- `triangle_match`

## External Review

Gemini 2.5 Flash reviewed Goals 608-612 in `/Users/rl2025/rtdl_python_only/docs/reports/goal608_612_gemini_quick_review_2026-04-19.md` and returned ACCEPT with no technical blockers. Goal611 is closed under the 2-AI rule.
