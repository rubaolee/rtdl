# Line-Segment Intersection And Spatial Join

Spatial join asks one RTDL question:

```text
which left geometry rows interact with which right geometry rows?
```

For line segments, the core relation is segment-pair intersection. RTDL writes
that relation as probe segments, build segments, traversal, refinement, and
emitted witness rows. V4 can then map the broadphase part to a prepared AABB
operator surface.

## Kernel Shape

This is the language model:

```python
import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def line_segment_intersection_kernel():
    left_segments = rt.input("left_segments", rt.Segments, layout=rt.Segment2DLayout, role="probe")
    right_segments = rt.input("right_segments", rt.Segments, layout=rt.Segment2DLayout, role="build")
    candidates = rt.traverse(left_segments, right_segments, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
    return rt.emit(hits, fields=["left_id", "right_id", "intersection_point_x", "intersection_point_y"])


compiled = rt.compile_kernel(line_segment_intersection_kernel)
print(compiled.name)
```

Read it as:

| Kernel part | Meaning |
| --- | --- |
| `left_segments` with `role="probe"` | The segment set asking for matches. |
| `right_segments` with `role="build"` | The searched segment set. |
| `rt.traverse(...)` | Produce possible left/right segment pairs. |
| `rt.segment_intersection(...)` | Refine candidates into true intersections. |
| `rt.emit(...)` | Return witness rows, including intersection coordinates. |

## Run It

PowerShell:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\tutorial_programs\spatial_join_lsi.py --mode kernel
py -3 examples\tutorial_programs\spatial_join_lsi.py --mode visible
py -3 examples\tutorial_programs\spatial_join_lsi.py --mode v4
```

Linux or macOS:

```bash
PYTHONPATH=src:. python examples/tutorial_programs/spatial_join_lsi.py --mode kernel
PYTHONPATH=src:. python examples/tutorial_programs/spatial_join_lsi.py --mode visible
PYTHONPATH=src:. python examples/tutorial_programs/spatial_join_lsi.py --mode v4
```

The default `--mode both` prints the kernel result, the visible Python mirror,
and the V4 mapping in one payload.

## Rows

A line-segment intersection row is a normal relation row:

```python
row = {
    "left_id": 100,
    "right_id": 200,
    "intersection_point_x": 2.0,
    "intersection_point_y": 2.0,
}
print(row["left_id"], row["right_id"], row["intersection_point_x"])
```

For count-only work, later code can count rows per left segment. For join work,
later code keeps the row table and attaches topology or payload data.

## Visible Python Mirror

The visible mode expands the broadphase part:

```python
left = {"min_x": 0.0, "min_y": 0.0, "max_x": 4.0, "max_y": 4.0}
right = {"min_x": 2.0, "min_y": 0.0, "max_x": 2.0, "max_y": 4.0}

overlaps = not (
    left["max_x"] < right["min_x"]
    or right["max_x"] < left["min_x"]
    or left["max_y"] < right["min_y"]
    or right["max_y"] < left["min_y"]
)
print(overlaps)
```

AABB overlap gives possible pairs. `rt.segment_intersection(...)` decides which
pairs are real and emits witness rows.

## V4 Runtime Mapping

Once the relation shape is clear, V4 can expose the prepared broadphase surface:

```python
import rtdsl.v4 as rtdl_v4

plan = rtdl_v4.plan_operator_request_v4("aabb_index_query", partner="rtdl_native")
print(plan.status)
print(plan.api_surface)
```

The V4 surface does not replace the kernel idea. It is where a recognized
candidate-generation pattern lands when the runtime uses a prepared AABB route.

## Count Output Versus Row Output

Both output styles are useful:

| Style | Meaning |
| --- | --- |
| count output | one compact count per probe geometry |
| row output | one row per true `(left, right)` pair |

Count output is compact. Row output is better when the user needs a join table
for later continuation.

Next: [Ray/Triangle Hit Rows](10_ray_triangle_hits.md)

Later, RayJoin topology uses the same candidate-row idea with boundary policy
and output topology.
