# Fixed-Radius Neighbors

Fixed-radius is one of the most common RTDL kernel shapes:

```text
query points + search points + radius
-> candidate pairs from traversal
-> neighbor rows after radius refinement
-> count, threshold, graph, or component continuation
```

This is not a clustering app. It is the language feature that produces
radius-neighbor rows. RTDBSCAN, RTNN, and Hausdorff-style programs can reuse
this feature later.

## The Question

Ask:

```text
For each query point, which search points are within radius r?
```

Visual sketch:

```text
search 10       search 11
   *              *
    \            /
     \ r=0.5    /
      \        /
       q1 ----* search 12 is outside q1 radius

q1 emits rows for search points inside the circle only.
```

The output row is small:

```python
neighbor_row = {
    "query_id": 1,
    "neighbor_id": 10,
    "distance": 0.1414,
}
```

The row says only that query `1` has neighbor `10` inside the radius. The app
decides what that fact means.

## Kernel Mode

This is the RTDL language shape users should learn first:

```python
import rtdsl as rt

@rt.kernel(backend="rtdl", precision="float_approx")
def fixed_radius_neighbors_kernel():
    query_points = rt.input("query_points", rt.Points, role="probe")
    search_points = rt.input("search_points", rt.Points, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.fixed_radius_neighbors(radius=0.5, k_max=3))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance"])
```

Read it as:

| RTDL piece | Meaning |
| --- | --- |
| `query_points` | Probe side. One query emits zero or more neighbor rows. |
| `search_points` | Build side. RTDL can index or traverse these rows. |
| `rt.traverse(...)` | Produces candidate `(query, search)` pairs. |
| `rt.fixed_radius_neighbors(...)` | Keeps candidates inside the radius. |
| `rt.emit(...)` | Returns neighbor rows to the application. |

Run:

```bash
PYTHONPATH=src:. python examples/tutorial_programs/fixed_radius_neighbors.py --mode kernel
```

PowerShell:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\tutorial_programs\fixed_radius_neighbors.py --mode kernel
```

The output includes `neighbor_rows` and a `kernel_summary` that shows
`input -> traverse -> refine -> emit`.

## Visible Flow

The tutorial program can also print a plain Python mirror:

```bash
PYTHONPATH=src:. python examples/tutorial_programs/fixed_radius_neighbors.py --mode visible
```

That mode expands the same relation into candidate checks:

```text
query_points
-> candidate checks
-> neighbor relation rows
-> count-threshold continuation
```

The visible flow is for learning only. The kernel above is the RTDL program.

## V4 Mode

Only after the kernel shape is clear, inspect the V4 execution surface:

```bash
PYTHONPATH=src:. python examples/tutorial_programs/fixed_radius_neighbors.py --mode v4
```

The V4 planner maps the recognized fixed-radius relation to a current operator
surface:

```python
import rtdsl.v4 as rtdl_v4

plan = rtdl_v4.plan_operator_request_v4("fixed_radius", partner="torch")
```

This is useful for route selection and performance control. It is not a
replacement for the RTDL kernel model.

## Both Modes

Run both:

```bash
PYTHONPATH=src:. python examples/tutorial_programs/fixed_radius_neighbors.py --mode both
```

The important relationship is:

```text
RTDL kernel emits fixed-radius neighbor rows
-> V4 maps that relation to a fixed-radius operator surface
```

## What The User Owns

RTDL owns the generic radius-neighbor relation. Your application owns the
meaning of the rows:

- local density;
- threshold flags;
- graph edges;
- cluster components;
- nearest-candidate prefiltering.

Next: [Nearest Witness](06_nearest_witness.md)
