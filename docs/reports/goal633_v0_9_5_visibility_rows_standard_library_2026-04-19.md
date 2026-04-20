# Goal633: v0.9.5 Visibility Rows Standard-Library Workload

Date: 2026-04-19

## Verdict

Implemented and locally verified.

## Scope

Goal633 adds a line-of-sight / visibility-row standard-library helper built on
the Goal632 any-hit primitive.

## User-Facing Surface

- `rt.visibility_rows_cpu(observers, targets, blockers)`
- output schema:
  - `observer_id`
  - `target_id`
  - `visible`

Data transformation:

```text
observers + targets + blocker triangles -> {observer_id, target_id, visible}
```

`visible=1` means no blocker triangle intersects the finite observer-target
segment. `visible=0` means at least one blocker triangle intersects it.

## Implementation

- `/Users/rl2025/rtdl_python_only/src/rtdsl/reference.py`
  - adds finite observer-target ray construction
  - validates dimensional consistency
  - rejects zero-length observer-target pairs
  - calls `ray_triangle_any_hit_cpu` internally
- `/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py`
  - exports `visibility_rows_cpu`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_visibility_rows.py`
  - runnable app-facing example

## Important Correctness Fix

The implementation uses full observer-to-target direction vectors with
`tmax=1.0`, so intersection is bounded to the segment between the observer and
target. This prevents blockers behind the target from being reported as
occluders.

## Correctness Evidence

Command:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal632_ray_triangle_any_hit_test tests.goal633_visibility_rows_test tests.rtdsl_ray_query_test tests.rtdsl_simulator_test -v
```

Result:

```text
Ran 22 tests in 0.019s
OK
```

Focused Goal633 assertions:

- 2D blocker between observer and target produces `visible=0`
- 2D blocker behind target produces `visible=1`
- output cardinality is the observer-target matrix
- 3D blocker between observer and target produces `visible=0`
- 3D blocker behind target produces `visible=1`
- mixed dimensions and zero-length observer-target pairs are rejected

Example command:

```bash
PYTHONPATH=src:. python3 examples/rtdl_visibility_rows.py
```

Result summary:

- emits deterministic `{observer_id, target_id, visible}` rows
- demonstrates line-of-sight row generation through bounded any-hit

## Boundary

This is a CPU standard-library helper in `v0.9.5`. Native backend-specific
visibility helpers remain future backend work after the CPU/oracle contract is
stable. RTDL does not claim a renderer, path tracer, or dynamic scene system.
