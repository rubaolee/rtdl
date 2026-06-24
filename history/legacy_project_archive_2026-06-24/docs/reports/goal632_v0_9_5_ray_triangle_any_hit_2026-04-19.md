# Goal632: v0.9.5 Ray/Triangle Any-Hit Predicate

Date: 2026-04-19

## Verdict

Implemented and locally verified.

## Scope

Goal632 adds the first implementable minimal ITRE extension selected for
`v0.9.5`: bounded any-hit / early-exit traversal.

## User-Facing Surface

- `rt.ray_triangle_any_hit(exact=False)`
- `rt.ray_triangle_any_hit_cpu(rays, triangles)`
- kernel output schema:
  - `ray_id`
  - `any_hit`

Example:

```python
@rt.kernel(backend="rtdl", precision="float_approx")
def ray_triangle_any_hit_demo():
    rays = rt.input("rays", rt.Rays, layout=rt.Ray2DLayout, role="probe")
    triangles = rt.input("triangles", rt.Triangles, layout=rt.Triangle2DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_any_hit(exact=False))
    return rt.emit(hits, fields=["ray_id", "any_hit"])
```

## Implementation

- `/Users/rl2025/rtdl_python_only/src/rtdsl/api.py`
  - adds the `ray_triangle_any_hit` predicate constructor
- `/Users/rl2025/rtdl_python_only/src/rtdsl/reference.py`
  - adds `ray_triangle_any_hit_cpu`
  - stops scanning triangles after the first accepted hit
- `/Users/rl2025/rtdl_python_only/src/rtdsl/runtime.py`
  - wires `run_cpu_python_reference`
  - allows 3D any-hit through the same Python reference fallback boundary used
    for 3D closest-hit
- `/Users/rl2025/rtdl_python_only/src/rtdsl/oracle_runtime.py`
  - wires `run_cpu` through the reference fallback
- `/Users/rl2025/rtdl_python_only/src/rtdsl/lowering.py`
  - adds `ray_tri_anyhit` lowering metadata, output record, payload registers,
    and early-exit host/device-plan text
- `/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py`
  - exports the public predicate and CPU helper
- `/Users/rl2025/rtdl_python_only/examples/rtdl_ray_triangle_any_hit.py`
  - runnable app-facing example

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

Focused Goal632 assertions:

- public predicate compiles and lowers to `ray_tri_anyhit`
- output schema is exactly `("ray_id", "any_hit")`
- CPU helper matches `hit_count > 0` on deterministic fixtures
- `run_cpu_python_reference` and `run_cpu` match
- 3D any-hit works through the documented reference fallback

Example command:

```bash
PYTHONPATH=src:. python3 examples/rtdl_ray_triangle_any_hit.py
```

Result summary:

- `cpu_python_reference` and `cpu_oracle` both return ray 1 as `any_hit=1`
  and ray 2 as `any_hit=0`
- `parity: true`

## Boundary

This is a language/reference/oracle contract slice. Native backend-specific
any-hit kernels are future backend work. No backend speedup claim is made.
