# Point In Polygon

Point-in-polygon asks one RTDL question:

```text
for each point, which polygon contains it?
```

The RT way to think about it is not "call a GIS function." It is a relation:
points probe a polygon set, traversal produces point/polygon candidates, and a
predicate keeps the containment rows. V4 can then map the candidate-generation
part to a prepared operator surface.

## Kernel Shape

This is the language model:

```python
import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def point_in_polygon_kernel():
    points = rt.input("points", rt.Points, role="probe")
    polygons = rt.input("polygons", rt.Polygons, role="build")
    candidates = rt.traverse(points, polygons, accel="bvh")
    hits = rt.refine(
        candidates,
        predicate=rt.point_in_polygon(exact=False, result_mode="positive_hits"),
    )
    return rt.emit(hits, fields=["point_id", "polygon_id", "contains"])


compiled = rt.compile_kernel(point_in_polygon_kernel)
print(compiled.name)
```

Read it as:

| Kernel part | Meaning |
| --- | --- |
| `points` with `role="probe"` | The things asking containment questions. |
| `polygons` with `role="build"` | The searched geometry set. |
| `rt.traverse(...)` | Produce possible point/polygon pairs. |
| `rt.point_in_polygon(...)` | Refine candidates into true containment rows. |
| `rt.emit(...)` | Return rows that later code can count, group, join, or filter. |

## Run It

PowerShell:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\tutorial_programs\point_in_polygon.py --mode kernel
py -3 examples\tutorial_programs\point_in_polygon.py --mode visible
py -3 examples\tutorial_programs\point_in_polygon.py --mode v4
```

Linux or macOS:

```bash
PYTHONPATH=src:. python examples/tutorial_programs/point_in_polygon.py --mode kernel
PYTHONPATH=src:. python examples/tutorial_programs/point_in_polygon.py --mode visible
PYTHONPATH=src:. python examples/tutorial_programs/point_in_polygon.py --mode v4
```

The default `--mode both` prints the kernel result, the visible Python mirror,
and the V4 mapping in one payload.

## Rows

A point-in-polygon hit is a normal relation row:

```python
row = {"point_id": 1, "polygon_id": 10, "contains": 1}
print(row["point_id"], row["polygon_id"], row["contains"])
```

The important part is not the small example data. The important part is the
shape: every true containment is a row, and rows compose with later RTDL
continuations.

## Visible Python Mirror

The visible mode expands the same idea:

```python
point = {"x": 0.25, "y": 0.25}
bounds = {"min_x": 0.0, "min_y": 0.0, "max_x": 1.0, "max_y": 1.0}

candidate = (
    bounds["min_x"] <= point["x"] <= bounds["max_x"]
    and bounds["min_y"] <= point["y"] <= bounds["max_y"]
)
print(candidate)
```

That broadphase candidate is not the final answer. The exact containment
predicate decides whether the row survives.

## V4 Runtime Mapping

Once the relation shape is clear, V4 can expose the prepared broadphase surface:

```python
import rtdsl.v4 as rtdl_v4

plan = rtdl_v4.plan_operator_request_v4("aabb_index_query", partner="rtdl_native")
print(plan.status)
print(plan.api_surface)
```

This is not the beginner programming model. It is the V4 runtime surface for a
recognized candidate-generation pattern. The RTDL kernel remains the clearest
way to explain what the program means.

## Where This Reappears

Point-in-polygon appears in polygon overlay and RayJoin-style workloads. The
RTDL lesson stays the same: express geometry as candidate rows, refine rows with
a predicate, and then let later application code decide what those rows mean.

Next: [Line-Segment Intersection And Spatial Join](09_line_segment_intersection_spatial_join.md)
