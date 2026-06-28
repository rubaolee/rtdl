# Grouped Continuations

Traversal rows are often too detailed to be the final app output. A
continuation consumes many RTDL rows and writes a compact summary:

```text
relation rows
-> group by app-owned key
-> count, sum, min, max, argmin, bounded witnesses, or vector output
```

This lesson teaches continuation as a step after a kernel relation, not as a
magic replacement for the relation.

## Kernel Plus Continuation Shape

Start with a kernel that emits hit-count rows:

```python
import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def ray_triangle_hit_count_kernel():
    rays = rt.input("rays", rt.Rays, layout=rt.Ray2DLayout, role="probe")
    triangles = rt.input("triangles", rt.Triangles, layout=rt.Triangle2DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_hit_count(exact=False))
    return rt.emit(hits, fields=["ray_id", "hit_count"])


compiled = rt.compile_kernel(ray_triangle_hit_count_kernel)
print(compiled.name)
```

Then a continuation groups those rows by an app-owned key:

```python
rows = (
    {"ray_id": 1, "group_id": 100, "hit_count": 2},
    {"ray_id": 2, "group_id": 100, "hit_count": 0},
    {"ray_id": 3, "group_id": 200, "hit_count": 2},
)

summary = {}
for row in rows:
    summary[row["group_id"]] = summary.get(row["group_id"], 0) + row["hit_count"]

print(summary[100], summary[200])
```

The group id is app-owned. RTDL does not need to know whether group `100` means
a graph vertex, robot pose, table group, aggregate cell, or particle id.

## Run It

PowerShell:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\tutorial_programs\continuation_grouped_sum.py --mode kernel
py -3 examples\tutorial_programs\continuation_grouped_sum.py --mode visible
py -3 examples\tutorial_programs\continuation_grouped_sum.py --mode v4
```

Linux or macOS:

```bash
PYTHONPATH=src:. python examples/tutorial_programs/continuation_grouped_sum.py --mode kernel
PYTHONPATH=src:. python examples/tutorial_programs/continuation_grouped_sum.py --mode visible
PYTHONPATH=src:. python examples/tutorial_programs/continuation_grouped_sum.py --mode v4
```

The default `--mode both` prints the kernel rows, continuation rows, visible
Python mirror, and V4 runtime mapping together.

## Continuation Outputs

Common continuation rows include:

| Continuation | Typical row |
| --- | --- |
| grouped count | `{group_id, count}` |
| grouped sum | `{group_id, sum}` |
| grouped min/max | `{group_id, min, max}` |
| grouped argmin | `{group_id, witness_id, distance}` |
| bounded witnesses | `{group_id, witness_id, overflow}` |
| weighted vector sum | `{group_id, fx, fy}` |

The key rule: application identity lives in the group/payload columns. The
generic RTDL continuation stays app-free.

## V4 Runtime Mapping

After the row/continuation shape is clear, ask V4 for measured continuation
surfaces:

```python
import rtdsl.v4 as rtdl_v4

grouped_sum = rtdl_v4.plan_operator_request_v4("grouped_sum", partner="cupy")
grouped_i64 = rtdl_v4.plan_operator_request_v4("grouped_i64", partner="torch")
print(grouped_sum.status)
print(grouped_i64.status)
```

The partner is explicit. CuPy or Torch being good at a continuation does not
turn that continuation into an app-specific RTDL kernel. It remains a generic
operator over relation rows.

## Where This Reappears

Grouped continuations are reused by triangle counting, RayDB-style query,
Barnes-Hut weighted forces, RTDBSCAN summaries, contact witnesses, and robot
collision pose flags.

Next: [Component Union From Radius Rows](12_component_union_from_radius.md)

Later lessons lower graph, robot, database, Hausdorff, and Barnes-Hut workloads
into the row and continuation shapes you have now seen.
