# Goal607: v0.9.3 Apple RT Native Point-In-Polygon Positive Hits

Date: 2026-04-19

Status: accepted with 2-AI consensus

## Scope

Goal607 adds Apple Metal/MPS RT-backed candidate discovery for
`point_in_polygon(result_mode="positive_hits")` on `Point2D/Polygon2D` inputs.

`point_in_polygon` full-matrix mode remains compatibility-only because it must
emit every point/polygon pair, including negative rows. Treating full-matrix
negative materialization as hardware-backed candidate discovery would overclaim
the current implementation.

## Implementation

Changed files:

- `/Users/rl2025/rtdl_python_only/src/native/rtdl_apple_rt.mm`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/apple_rt_runtime.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py`
- `/Users/rl2025/rtdl_python_only/tests/goal603_apple_rt_native_contract_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal607_apple_rt_point_in_polygon_positive_native_test.py`

Native lowering:

- Each polygon is represented by a 2D bounding-box prism in Apple MPS.
- Each point casts a short z-ray through polygon bounding boxes.
- MPS masked traversal discovers candidate point/polygon pairs.
- CPU exact refinement runs RTDL's point-in-polygon predicate only on MPS
  candidates.
- Only exact positive rows are emitted with `contains=1`.

This is conservative: bounding boxes can over-admit candidates, but cannot miss
a true positive point-in-polygon hit.

## Contract Update

`rt.apple_rt_support_matrix()` now reports:

| Predicate | Native candidate discovery | Native shapes |
| --- | --- | --- |
| `point_in_polygon` | `shape_dependent` | `Point2D/Polygon2D positive_hits` |

`run_apple_rt(..., native_only=True)` accepts the positive-hit shape and rejects
full-matrix point-in-polygon mode.

## Validation

Build:

```bash
make build-apple-rt
```

Focused test command:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal578_apple_rt_backend_test tests.goal607_apple_rt_point_in_polygon_positive_native_test tests.goal606_apple_rt_point_neighbor_3d_native_test tests.goal605_apple_rt_point_neighbor_2d_native_test tests.goal604_apple_rt_ray_hitcount_2d_native_test tests.goal603_apple_rt_native_contract_test tests.goal582_apple_rt_full_surface_dispatch_test -v
```

Actual result:

```text
Ran 28 tests in 0.057s
OK
```

Additional checks:

```bash
PYTHONPATH=src:. python3 -m py_compile src/rtdsl/apple_rt_runtime.py src/rtdsl/__init__.py tests/goal607_apple_rt_point_in_polygon_positive_native_test.py tests/goal603_apple_rt_native_contract_test.py
git diff --check
```

Both completed with no output.

## Honesty Boundary

This goal does not claim full `point_in_polygon` coverage. It claims only
positive-hit semantics, where MPS can be used as a conservative candidate
discovery stage. Full-matrix semantics remain non-native until a later design
decides whether CPU negative-row materialization is acceptable.

## Verdict

Codex verdict: ACCEPT with external consensus.

Goal607 correctly adds Apple MPS RT-backed candidate discovery for
point-in-polygon positive hits without overclaiming full-matrix, polygon overlay,
graph, or DB coverage.

External consensus:

- Gemini review: `/Users/rl2025/rtdl_python_only/docs/reports/goal607_gemini_review_2026-04-19.md` verdict ACCEPT.
- Claude review was attempted, but Claude CLI was rate-limited until 12pm America/New_York.
