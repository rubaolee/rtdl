# Component Union From Radius Rows

Component union is a continuation over neighbor rows:

```text
points
-> fixed-radius neighbor rows
-> core flags
-> density-reachable union edges
-> component labels
```

This is the RTDL part of clustering-style workloads. The tutorial is not a
DBSCAN course; it teaches how radius rows become graph labels.

## Kernel Plus Continuation Shape

Start with a normal fixed-radius kernel:

```python
import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def radius_edges_kernel():
    query_points = rt.input("query_points", rt.Points, role="probe")
    search_points = rt.input("search_points", rt.Points, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.fixed_radius_neighbors(radius=0.55, k_max=8))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance"])


compiled = rt.compile_kernel(radius_edges_kernel)
print(compiled.name)
```

Then component union consumes the emitted rows. The group labels are app-owned;
the RTDL relation is only the neighbor row table.

## Run It

PowerShell:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\tutorial_programs\component_union_from_radius.py --mode kernel
py -3 examples\tutorial_programs\component_union_from_radius.py --mode visible
py -3 examples\tutorial_programs\component_union_from_radius.py --mode v4
```

Linux or macOS:

```bash
PYTHONPATH=src:. python examples/tutorial_programs/component_union_from_radius.py --mode kernel
PYTHONPATH=src:. python examples/tutorial_programs/component_union_from_radius.py --mode visible
PYTHONPATH=src:. python examples/tutorial_programs/component_union_from_radius.py --mode v4
```

The default `--mode both` prints the kernel rows, visible continuation, and V4
runtime mapping together.

## Rows

The kernel emits radius rows:

```python
row = {"query_id": 1, "neighbor_id": 2, "distance": 0.2}
print(row["query_id"], row["neighbor_id"])
```

The continuation emits labels:

```python
label = {"point_id": 1, "component": 1}
print(label["point_id"], label["component"])
```

## V4 Runtime Mapping

After the row and continuation shape is clear, ask V4 for the measured
component-union surface:

```python
import rtdsl.v4 as rtdl_v4

plan = rtdl_v4.plan_operator_request_v4("component_union", partner="numba")
print(plan.status)
print(plan.api_surface)
```

Numba is an explicit continuation partner. That does not turn the continuation
into an app-specific kernel; it remains a generic row-graph operation.

## Where This Reappears

Component union is reused by RTDBSCAN-style density clustering and any workload
that turns radius-neighbor rows into connected labels.

Next: [Bounded Witness Collection](13_bounded_witness_collection.md)
