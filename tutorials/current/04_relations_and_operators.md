# Relations And Operators

RTDL starts from relation rows, not from application names and not from a
runtime catalog call.

A relation row is a fact produced by traversal and refinement:

- query point `q` is near point `p`;
- ray `r` hits triangle `t`;
- point `q` has nearest witness `w`;
- box `a` overlaps box `b`;
- body `p` should use aggregate cell `c`.

The app name is not the operator. RTDBSCAN, RTNN, triangle counting, robot
collision, and Barnes-Hut reuse a smaller set of generic relation-producing
operators and continuations.

## Kernel First

The user-facing RTDL shape is:

```python
import rtdsl as rt

@rt.kernel(backend="rtdl", precision="float_approx")
def program():
    probe = rt.input("probe_rows", rt.Points, role="probe")
    build = rt.input("build_rows", rt.Points, role="build")
    candidates = rt.traverse(probe, build, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.fixed_radius_neighbors(radius=0.5, k_max=3))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance"])
```

This is the language model:

```text
input objects
-> candidate relation rows
-> refined relation rows
-> continuation rows
-> application output
```

The important questions are:

| Question | Example answer |
| --- | --- |
| What is the probe side? | Query points, rays, frontier rows. |
| What is the build side? | Search points, triangles, boxes, aggregate cells. |
| What does traversal generate? | Candidate pairs. |
| What does refinement keep? | Hits, neighbors, witnesses, overlaps. |
| What does emit return? | Rows the application can consume. |
| What continuation follows? | Count, sum, argmin, union, ranked summary. |

## V4 Second

After the relation is clear, V4 can expose the execution target:

```python
import rtdsl.v4 as rtdl_v4

plan = rtdl_v4.plan_operator_request_v4("fixed_radius", partner="torch")
print(plan.status)
print(plan.api_surface)
```

This call is not the programming model. It is a planning and execution-surface
check for a relation that RTDL already knows how to describe.

Use the V4 operator/runtime API when you need to:

- inspect which operator surface a relation maps to;
- choose a partner such as Torch, CuPy, Numba, or RTDL native;
- pin a route for benchmark or production reproducibility;
- pass caller-owned device arrays into a prepared route.

## Run The Concept Programs

PowerShell:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\tutorial_programs\operator_primitives.py
py -3 examples\tutorial_programs\fixed_radius_neighbors.py --mode both
py -3 examples\tutorial_programs\v4_frontdoor_quickstart.py
```

Linux or macOS:

```bash
PYTHONPATH=src:. python examples/tutorial_programs/operator_primitives.py
PYTHONPATH=src:. python examples/tutorial_programs/fixed_radius_neighbors.py --mode both
PYTHONPATH=src:. python examples/tutorial_programs/v4_frontdoor_quickstart.py
```

In `operator_primitives.py`, read the vocabulary. In
`fixed_radius_neighbors.py`, run the kernel/relation shape. Only then use
`v4_frontdoor_quickstart.py` to inspect the current V4 front door.

| Field | Meaning |
| --- | --- |
| `relation_row_examples` | Small examples of the row facts RTDL emits. |
| `operator_catalog_rows` | How V4 names current execution surfaces. |
| `continuation_classes` | What kind of continuation consumes relation rows. |

## Keep App Meaning Outside The Operator

The same neighbor rows can mean several different things:

| Same relation rows | Possible app meaning |
| --- | --- |
| `(query_id, neighbor_id, distance)` | local density |
| `(query_id, neighbor_id, distance)` | graph edges |
| `(query_id, neighbor_id, distance)` | candidate prefiltering |
| `(query_id, neighbor_id, distance)` | threshold flags |

RTDL should produce generic rows. Your application decides what those rows mean.

Next: [Fixed-Radius Neighbors](05_fixed_radius_neighbors.md)
