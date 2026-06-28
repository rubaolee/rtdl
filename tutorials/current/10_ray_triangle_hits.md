# Ray/Triangle Hit Rows

Ray/triangle queries are the most direct RTDL shape:

```text
rays probe a triangle scene
-> traversal finds candidate ray/triangle pairs
-> refinement decides hit or miss
-> emitted rows become hit flags, counts, closest witnesses, or payload rows
```

This lesson teaches the relation first. V4 operator surfaces appear only after
the kernel shape is clear.

## Kernel Shape

This kernel emits one any-hit row per ray:

```python
import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def ray_triangle_any_hit_kernel():
    rays = rt.input("rays", rt.Rays, layout=rt.Ray2DLayout, role="probe")
    triangles = rt.input("triangles", rt.Triangles, layout=rt.Triangle2DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_any_hit(exact=False))
    return rt.emit(hits, fields=["ray_id", "any_hit"])


compiled = rt.compile_kernel(ray_triangle_any_hit_kernel)
print(compiled.name)
```

Read it as:

| Kernel part | Meaning |
| --- | --- |
| `rays` with `role="probe"` | The query rays. |
| `triangles` with `role="build"` | The searched triangle scene. |
| `rt.traverse(...)` | Produce possible ray/triangle pairs. |
| `rt.ray_triangle_any_hit(...)` | Accept the first meaningful hit per ray. |
| `rt.emit(...)` | Return compact per-ray hit flags. |

## Run It

PowerShell:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\tutorial_programs\ray_triangle_hits.py --mode kernel
py -3 examples\tutorial_programs\ray_triangle_hits.py --mode visible
py -3 examples\tutorial_programs\ray_triangle_hits.py --mode v4
```

Linux or macOS:

```bash
PYTHONPATH=src:. python examples/tutorial_programs/ray_triangle_hits.py --mode kernel
PYTHONPATH=src:. python examples/tutorial_programs/ray_triangle_hits.py --mode visible
PYTHONPATH=src:. python examples/tutorial_programs/ray_triangle_hits.py --mode v4
```

The default `--mode both` prints the kernel result, visible relation rows, and
V4 runtime mapping together.

## Rows

An any-hit row is compact:

```python
row = {"ray_id": 1, "any_hit": 1}
print(row["ray_id"], row["any_hit"])
```

Other ray/triangle programs use the same relation but emit different summaries:

| Output | Meaning |
| --- | --- |
| any-hit flag | one boolean-like row per ray |
| hit count | one count per ray |
| closest hit | nearest witness per ray |
| hit stream | one row per accepted ray/primitive pair |

The kernel chooses the output shape that the next continuation needs.

## Visible Python Mirror

The visible mode expands the relation:

```python
candidate = {"ray_id": 1, "triangle_id": 10, "hit": True}
any_hit = 1 if candidate["hit"] else 0
print(candidate["ray_id"], any_hit)
```

This mirror is intentionally small. The RTDL lesson is that every ray/triangle
decision can become a row, and later code chooses how to summarize those rows.

## V4 Runtime Mapping

After the kernel relation is clear, ask V4 for a measured execution surface:

```python
import rtdsl.v4 as rtdl_v4

plan = rtdl_v4.plan_operator_request_v4("any_hit", partner="torch")
print(plan.status)
print(plan.api_surface)
```

The V4 surface does not change the program meaning. It is the prepared
partner-backed route for a recognized ray/triangle any-hit relation.

## Where This Reappears

Ray/triangle hit rows are reused by triangle counting, robot collision,
RayDB-style query, contact manifolds, visibility queries, and custom predicate
planning.

Next: [Grouped Continuations](11_grouped_continuations.md)
