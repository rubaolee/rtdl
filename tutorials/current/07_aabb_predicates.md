# AABB Predicates

An axis-aligned bounding box is the simplest spatial broadphase filter in RTDL.
It answers cheap spatial questions before more expensive geometry refinement:

```text
boxes + point or range queries
-> broadphase candidate rows
-> count rows or exact-refinement inputs
```

This is not a full spatial-index application. It teaches the rows that later
appear in LibRTS spatial index, contact manifold, robot collision, and spatial
joins.

## The Rows

A point-containment row can look like this:

```python
row = {
    "query_id": 10,
    "box_id": 1,
    "predicate": "point_contains",
}
```

The same box data can also answer range containment and range intersection.

Visual sketch:

```text
+-------------------+    indexed box A
|       *           |    point query is contained
|   +-------+       |    query box B is contained
|   |   B   |---+   |    query box C intersects but is not contained
|   +-------+  C|   |
+--------------+----+
```

Broadphase rows are candidates. A range-intersection candidate can still need
later exact refinement if the app cares about a more precise geometry predicate.

## Kernel Mode

The current public kernel API does not expose a direct
`rt.aabb_index_query(...)` predicate. Do not pretend it does.

For teaching the RTDL relation shape, this lesson uses rectangle containment as
a kernel-shaped broadphase:

```python
import rtdsl as rt

@rt.kernel(backend="rtdl", precision="float_approx")
def rectangle_containment_kernel():
    points = rt.input("points", rt.Points, role="probe")
    rectangles = rt.input("rectangles", rt.Polygons, role="build")
    candidates = rt.traverse(points, rectangles, accel="bvh")
    hits = rt.refine(
        candidates,
        predicate=rt.point_in_polygon(exact=False, result_mode="positive_hits"),
    )
    return rt.emit(hits, fields=["point_id", "polygon_id", "contains"])
```

Read it as:

| RTDL piece | Meaning |
| --- | --- |
| `points` | Probe side. |
| `rectangles` | Build side represented as four-vertex polygons. |
| `rt.traverse(...)` | Produces point/rectangle candidates. |
| `rt.point_in_polygon(...)` | Keeps containment hits. |
| `rt.emit(...)` | Returns containment rows. |

Run:

```bash
PYTHONPATH=src:. python examples/tutorial_programs/aabb_spatial_index_predicates.py --mode kernel
```

PowerShell:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\tutorial_programs\aabb_spatial_index_predicates.py --mode kernel
```

This teaches broadphase relation thinking. It is not the full V4 AABB prepared
runner.

## Visible Flow

The visible flow prints the full AABB predicate family by hand:

```bash
PYTHONPATH=src:. python examples/tutorial_programs/aabb_spatial_index_predicates.py --mode visible
```

It includes:

| Field | Meaning |
| --- | --- |
| `point_contains_rows` | Point is inside box. |
| `range_contains_rows` | Box contains query range. |
| `range_intersects_rows` | Box intersects query range. |

## V4 Mode

The V4 operator/runtime API is the current prepared AABB execution surface:

```bash
PYTHONPATH=src:. python examples/tutorial_programs/aabb_spatial_index_predicates.py --mode v4
```

The planner call is:

```python
import rtdsl.v4 as rtdl_v4

plan = rtdl_v4.plan_operator_request_v4("aabb_index_query", partner="rtdl_native")
```

This maps to the prepared AABB operator that can cover point, range-containment,
and range-intersection operations. It is the V4 execution target, not the first
thing a learner should see.

## What The User Owns

RTDL owns candidate rows. Your program decides what candidates mean:

- range query count;
- broadphase collision pair;
- spatial join candidate;
- contact candidate;
- later exact geometry refinement.

Next: [Point In Polygon](08_point_in_polygon.md)
