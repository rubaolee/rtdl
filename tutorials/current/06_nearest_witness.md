# Nearest Witness

Nearest witness is the next common RTDL shape:

```text
query points + search candidates
-> candidate distance rows
-> argmin or top-k continuation
-> nearest witness row per query
```

This is not "call a nearest-neighbor app." The key idea is that RTDL produces
candidate facts, then a continuation keeps the best witness for each query.

## The Question

Ask:

```text
For each query, which candidate is the nearest witness?
```

Visual sketch:

```text
candidate 100      query 2      candidate 102
     *---------------*-------------*
       farther             nearest

The output keeps the winning witness, not every nearby candidate.
```

The output row is the winning candidate:

```python
nearest_row = {
    "query_id": 2,
    "neighbor_id": 102,
    "distance": 0.1414,
    "rank": 1,
}
```

## Kernel Mode

The RTDL kernel uses `knn_rows(k=1)` for a nearest-witness row:

```python
import rtdsl as rt

@rt.kernel(backend="rtdl", precision="float_approx")
def nearest_witness_kernel():
    query_points = rt.input("query_points", rt.Points, role="probe")
    search_points = rt.input("search_points", rt.Points, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.knn_rows(k=1))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance", "neighbor_rank"])
```

Read it as:

| RTDL piece | Meaning |
| --- | --- |
| `query_points` | Probe side. Each query wants a best witness. |
| `search_points` | Build side. Candidate witnesses live here. |
| `rt.traverse(...)` | Produces candidate pairs. |
| `rt.knn_rows(k=1)` | Keeps the nearest candidate per query. |
| `rt.emit(...)` | Returns nearest-witness rows. |

Run:

```bash
PYTHONPATH=src:. python examples/tutorial_programs/nearest_neighbor.py --mode kernel
```

PowerShell:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\tutorial_programs\nearest_neighbor.py --mode kernel
```

## Visible Flow

The visible flow shows the continuation explicitly:

```bash
PYTHONPATH=src:. python examples/tutorial_programs/nearest_neighbor.py --mode visible
```

It expands to:

```text
query_points + search_points
-> candidate witness rows
-> per-query argmin continuation
```

That argmin is the important concept. Many larger apps are built by changing
what happens after candidate rows are emitted.

Tie case:

| candidate_id | distance | tie-break |
| ---: | ---: | --- |
| 101 | 0.25 | lower candidate id wins |
| 102 | 0.25 | loses tie |

When distances tie, keep a deterministic rule such as lower candidate id or an
explicit app-provided rank. The rule belongs in the continuation contract; do
not leave ties to accidental traversal order.

## V4 Mode

After the kernel relation is clear, inspect the V4 execution target:

```bash
PYTHONPATH=src:. python examples/tutorial_programs/nearest_neighbor.py --mode v4
```

The V4 planner call is:

```python
import rtdsl.v4 as rtdl_v4

plan = rtdl_v4.plan_operator_request_v4("point_group_nearest", partner="torch")
```

This names the device-array operator surface for a recognized nearest-witness
relation. It is useful for partner choice and route control, not for first
learning RTDL.

## Fixed Radius Versus Nearest Witness

| Need | Use |
| --- | --- |
| "All candidates within radius r" | fixed-radius neighbor rows |
| "The closest candidate per query" | nearest-witness rows |
| "Only candidates passing a threshold" | fixed-radius rows plus threshold continuation |
| "Top-k or ranked output" | candidate rows plus ranked-summary continuation |

Hausdorff-style programs use nearest witnesses. RTNN-style programs often
combine fixed-radius filtering with ranked summaries. Contact programs reuse
the same witness idea with geometry-specific candidates.

Next: [AABB Predicates](07_aabb_predicates.md)
