# Sorting Rows

RTDL traversal produces relation rows: a query, a candidate, and facts such as
distance, hit state, or weight. Many apps then sort those rows before taking a
nearest witness, a top-k list, or a grouped summary.

This is the small shape:

```python
hit_rows = [
    {"query": 0, "candidate": 8, "distance": 0.42, "weight": 2.0},
    {"query": 0, "candidate": 3, "distance": 0.18, "weight": 1.5},
    {"query": 1, "candidate": 2, "distance": 0.31, "weight": 0.5},
    {"query": 1, "candidate": 7, "distance": 0.11, "weight": 3.0},
]

sorted_rows = sorted(
    hit_rows,
    key=lambda row: (row["query"], row["distance"], row["candidate"]),
)

nearest_by_query = {}
for row in sorted_rows:
    nearest_by_query.setdefault(row["query"], row)

print(nearest_by_query[0]["candidate"])
print(nearest_by_query[1]["candidate"])
```

The important point is not that RTDL has a primitive named "sort". The point is
that V4 gives names to common continuation patterns so you can ask for the
right operator instead of hand-assembling every step.

Ask the planner for nearest-witness and grouped-summary surfaces:

```python
import rtdsl.v4 as rtdl_v4

nearest = rtdl_v4.plan_operator_request_v4(
    "point_group_nearest",
    partner="torch",
)
grouped = rtdl_v4.plan_operator_request_v4(
    "grouped_sum",
    partner="cupy",
)

print(nearest.status, nearest.api_surface)
print(grouped.status, grouped.api_surface)
```

Run the complete sorting example:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\simple\sorting_rows.py
```

Linux or macOS:

```bash
PYTHONPATH=src:. python examples/simple/sorting_rows.py
```

You will see sorted rows, the nearest candidate for each query, and a grouped
weight sum. The same pattern appears in RTNN, Hausdorff-style nearest witness,
triangle counting, and grouped reductions.

Next: [Relations and Operators](04_relations_and_operators.md)
