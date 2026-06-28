# Bounded Witness Collection

Some workloads need witnesses, but cannot let one query produce unbounded
output:

```text
candidate witness rows
-> rank or score within each pair/group
-> keep K witnesses
-> report overflow
```

This lesson teaches bounded collection as a continuation over emitted rows. It
does not teach a contact or collision app directly.

## Kernel Plus Continuation Shape

Use a kernel that emits witness rows. Here, segment intersections stand in for
candidate witnesses:

```python
import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def segment_witness_rows_kernel():
    left_segments = rt.input("left_segments", rt.Segments, layout=rt.Segment2DLayout, role="probe")
    right_segments = rt.input("right_segments", rt.Segments, layout=rt.Segment2DLayout, role="build")
    candidates = rt.traverse(left_segments, right_segments, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
    return rt.emit(hits, fields=["left_id", "right_id", "intersection_point_x", "intersection_point_y"])


compiled = rt.compile_kernel(segment_witness_rows_kernel)
print(compiled.name)
```

Then bounded collection keeps at most `K` rows per app-owned pair.

## Run It

PowerShell:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\tutorial_programs\bounded_witness_collection.py --mode kernel
py -3 examples\tutorial_programs\bounded_witness_collection.py --mode visible
py -3 examples\tutorial_programs\bounded_witness_collection.py --mode v4
```

Linux or macOS:

```bash
PYTHONPATH=src:. python examples/tutorial_programs/bounded_witness_collection.py --mode kernel
PYTHONPATH=src:. python examples/tutorial_programs/bounded_witness_collection.py --mode visible
PYTHONPATH=src:. python examples/tutorial_programs/bounded_witness_collection.py --mode v4
```

The default `--mode both` prints the kernel witness rows, bounded collection
rows, overflow validation, and V4 runtime mapping together.

## Rows

A witness row can look like this:

```python
row = {"pair_id": 1, "witness_id": 102, "depth": 0.03}
print(row["pair_id"], row["witness_id"], row["depth"])
```

A bounded output row adds a slot:

```python
kept = {"pair_id": 1, "witness_id": 102, "slot": 0, "depth": 0.03}
print(kept["pair_id"], kept["slot"])
```

Overflow is not an error to hide. It is a validation row the user can inspect.

## V4 Runtime Mapping

After the row shape is clear, ask V4 for the closest-witness grouped argmin
surface:

```python
import rtdsl.v4 as rtdl_v4

plan = rtdl_v4.plan_operator_request_v4("closest_hit_argmin", partner="torch")
print(plan.status)
print(plan.api_surface)
```

The V4 surface is a measured grouped-witness route. The language idea remains:
produce witness rows, then bound or reduce them.

## Where This Reappears

Bounded witnesses are reused by contact manifolds, robot collision, closest-hit
queries, and any workload where output must stay bounded per query.

Next: [Aggregate Frontier Rows](14_aggregate_frontier_rows.md)
