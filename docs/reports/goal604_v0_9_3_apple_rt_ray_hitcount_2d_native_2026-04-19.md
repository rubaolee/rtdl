# Goal604: v0.9.3 Apple RT Native 2D Ray/Triangle Hit-Count

Date: 2026-04-19

Status: accepted with 3-AI consensus

## Scope

Goal604 expands Apple Metal/MPS RT native coverage for `ray_triangle_hit_count`
from 3D-only to both supported RTDL ray/triangle shapes:

- `Ray3D/Triangle3D`: existing Apple MPS triangle traversal path.
- `Ray2D/Triangle2D`: new Apple MPS candidate traversal path using a thin 3D
  prism lowering for each 2D triangle.

This goal does not mark any unrelated geometry, nearest-neighbor, graph, or DB
workload as native.

## Implementation

Changed files:

- `/Users/rl2025/rtdl_python_only/src/native/rtdl_apple_rt.mm`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/apple_rt_runtime.py`
- `/Users/rl2025/rtdl_python_only/tests/goal578_apple_rt_backend_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal582_apple_rt_full_surface_dispatch_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal603_apple_rt_native_contract_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal604_apple_rt_ray_hitcount_2d_native_test.py`

Native lowering:

- Each 2D triangle is lifted into a bounded 3D prism represented by MPS triangle
  primitives.
- Each 2D finite ray is mapped to a 3D swept ray whose MPS parameter covers the
  original finite 2D segment.
- MPS masked traversal discovers candidate triangle IDs.
- Exact 2D ray/triangle refinement is applied only to discovered candidates
  before incrementing hit counts.

This satisfies the Goal602/Goal603 hardware-backed definition: Apple MPS
performs candidate discovery; CPU work is bounded exact refinement, not full
CPU candidate search.

## Contract Update

`rt.apple_rt_support_matrix()` now reports:

| Predicate | Native candidate discovery | Native shapes |
| --- | --- | --- |
| `ray_triangle_hit_count` | `shape_dependent` | `Ray2D/Triangle2D`, `Ray3D/Triangle3D` |

`rt.apple_rt_predicate_mode("ray_triangle_hit_count")` now returns
`native_mps_rt_2d_3d`, replacing the old 3D-only compatibility wording.

The native-only guard now accepts 2D and 3D hit-count shapes. Unsupported
compatibility predicates still raise `NotImplementedError` with
`native_only=True`.

## Validation

Build:

```bash
make build-apple-rt
```

Focused test command:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal578_apple_rt_backend_test tests.goal604_apple_rt_ray_hitcount_2d_native_test tests.goal603_apple_rt_native_contract_test tests.goal582_apple_rt_full_surface_dispatch_test -v
```

Actual result:

```text
Ran 17 tests in 0.058s
OK
```

Additional focused checks already passed before the library version bump:

```text
Ran 10 tests in 0.028s
OK
```

## Honesty Boundary

This is a correctness-first native coverage step, not a speedup claim. The new
2D path uses Apple MPS ray traversal for candidate discovery, but the current
implementation is bounded and scalar around the MPS calls. Performance must be
remeasured in the later v0.9.3 full-surface performance goal.

## Verdict

Codex verdict: ACCEPT with external consensus.

Goal604 correctly moves 2D `ray_triangle_hit_count` from compatibility-only
execution to real Apple MPS RT-backed candidate discovery while preserving CPU
oracle parity in native-only execution.

External consensus:

- Claude review: `/Users/rl2025/rtdl_python_only/docs/reports/goal604_external_review_2026-04-19.md` verdict ACCEPT; noted the stale mode string before it was corrected.
- Gemini review: `/Users/rl2025/rtdl_python_only/docs/reports/goal604_gemini_review_2026-04-19.md` verdict ACCEPT.
