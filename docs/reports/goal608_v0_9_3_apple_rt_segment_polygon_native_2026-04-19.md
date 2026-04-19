# Goal608: v0.9.3 Apple RT Segment-Polygon Native Candidate Discovery

Date: 2026-04-19

Status: accepted with 2-AI consensus (Codex + Gemini 2.5 Flash).

## Scope

Goal608 extends the Apple Metal/MPS RT backend to cover the bounded 2D segment-polygon workloads:

- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`

This is a native candidate-discovery implementation, not a performance claim. The Apple backend uses MPS ray traversal to discover conservative polygon candidates and keeps exact CPU refinement for final segment-polygon semantics.

## Implementation

Files changed:

- `/Users/rl2025/rtdl_python_only/src/native/rtdl_apple_rt.mm`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/apple_rt_runtime.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py`
- `/Users/rl2025/rtdl_python_only/tests/goal603_apple_rt_native_contract_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal608_apple_rt_segment_polygon_native_test.py`

Native lowering:

- Builds conservative polygon bounding-box prisms as MPS triangle acceleration geometry.
- Casts each 2D segment as a 3D MPS ray from `(x0, y0, -1)` toward `(x1, y1, +1)`.
- Uses primitive masks to enumerate candidate polygons per segment in bounded chunks.
- Expands xy box bounds by `1.0e-4` for candidate discovery robustness only.
- Keeps z slab inside the ray interval (`-0.9999` to `0.9999`) so MPS intersections remain within `maxDistance`.
- Uses endpoint point-in-polygon MPS candidate discovery to cover segments fully contained inside a polygon box, where a surface-only segment ray has no box-face crossing.
- Exact CPU refinement via the existing reference segment-polygon predicate removes false positives and produces final hit-count or any-hit rows.

Contract updates:

- `apple_rt_support_matrix()` now marks both segment-polygon predicates as Apple native candidate-discovery rows for `Segment2D/Polygon2D`.
- `run_apple_rt(..., native_only=True)` dispatches these two predicates through Apple RT for 2D segment/polygon inputs.
- Full CPU compatibility dispatch remains available for unsupported shapes or predicates.

## Validation

Commands run locally on macOS:

```text
make build-apple-rt
PYTHONPATH=src:. python3 -m unittest tests.goal607_apple_rt_point_in_polygon_positive_native_test tests.goal608_apple_rt_segment_polygon_native_test -v
```

Result:

```text
Ran 6 tests in 0.042s
OK
```

Broader Apple-focused suite:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal578_apple_rt_backend_test tests.goal608_apple_rt_segment_polygon_native_test tests.goal607_apple_rt_point_in_polygon_positive_native_test tests.goal606_apple_rt_point_neighbor_3d_native_test tests.goal605_apple_rt_point_neighbor_2d_native_test tests.goal604_apple_rt_ray_hitcount_2d_native_test tests.goal603_apple_rt_native_contract_test tests.goal582_apple_rt_full_surface_dispatch_test -v
```

Result:

```text
Ran 31 tests in 0.105s
OK
```

Mechanical checks:

```text
PYTHONPATH=src:. python3 -m py_compile src/rtdsl/apple_rt_runtime.py src/rtdsl/__init__.py tests/goal608_apple_rt_segment_polygon_native_test.py tests/goal603_apple_rt_native_contract_test.py
git diff --check
```

Result: both passed with no output.

## Honesty Boundary

- This goal proves bounded Apple Metal/MPS RT candidate discovery plus exact final CPU refinement for 2D segment-polygon workloads.
- It does not claim that aggregation/refinement is fully GPU-resident.
- It does not claim broad performance improvement over Embree.
- It does not make full polygon overlay or polygon-polygon workloads native.

## External Review

Gemini 2.5 Flash reviewed Goals 608-612 in `/Users/rl2025/rtdl_python_only/docs/reports/goal608_612_gemini_quick_review_2026-04-19.md` and returned ACCEPT with no technical blockers. Goal608 is closed under the 2-AI rule.
