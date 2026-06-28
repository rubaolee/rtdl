# Aggregate Frontier Rows

Aggregate frontier is a row relation used by hierarchical approximation:

```text
source objects + aggregate cells
-> choose aggregate-cell rows or exact-object rows
-> compute contribution rows
-> grouped weighted vector output
```

This lesson is relation-first. The current public tutorial API does not expose
aggregate frontier as an `@rt.kernel` predicate, so the runnable program names
the rows directly and then shows the V4 prepared operator surface.

## Relation Shape

The important row is the frontier row:

```python
row = {
    "body_id": 3,
    "frontier_id": 100,
    "kind": "aggregate_cell",
    "opening_ratio": 0.2069,
}
print(row["body_id"], row["frontier_id"], row["kind"])
```

The row says: for this body, use either an aggregate cell or an exact body as a
source of contribution. Later continuation rows turn those frontier choices
into vector output.

## Run It

PowerShell:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\tutorial_programs\aggregate_frontier_rows.py --mode relation
py -3 examples\tutorial_programs\aggregate_frontier_rows.py --mode visible
py -3 examples\tutorial_programs\aggregate_frontier_rows.py --mode v4
```

Linux or macOS:

```bash
PYTHONPATH=src:. python examples/tutorial_programs/aggregate_frontier_rows.py --mode relation
PYTHONPATH=src:. python examples/tutorial_programs/aggregate_frontier_rows.py --mode visible
PYTHONPATH=src:. python examples/tutorial_programs/aggregate_frontier_rows.py --mode v4
```

The default `--mode both` prints relation rows, visible contribution rows, and
V4 runtime mapping together.

## Contribution Rows

Frontier rows become contribution rows:

```python
contribution = {"body_id": 3, "source_id": 100, "fx": -0.237283, "fy": 0.004091}
print(contribution["body_id"], contribution["fx"], contribution["fy"])
```

Then a grouped vector continuation sums contributions by `body_id`.

## V4 Runtime Mapping

After the relation shape is clear, V4 exposes the measured prepared surfaces:

```python
import rtdsl.v4 as rtdl_v4

frontier = rtdl_v4.plan_operator_request_v4("aggregate_frontier", partner="rtdl_native")
continuation = rtdl_v4.plan_operator_request_v4("grouped_sum", partner="cupy")
print(frontier.status)
print(continuation.status)
```

The frontier route is RTDL native. The grouped vector continuation uses an
explicit CuPy partner when the user chooses it. This is still app-free: the
engine knows frontier rows and grouped vectors, not a Barnes-Hut application.

## Where This Reappears

Aggregate frontier rows and grouped weighted vector continuations are used by
Barnes-Hut-style workloads and other hierarchical approximation pipelines.

Next: [Ranked Summary Neighbors](15_ranked_summary_neighbors.md)

Later lessons lower graph, robot, database, Hausdorff, and benchmark-app bridge
programs using the row/continuation ideas already covered.
