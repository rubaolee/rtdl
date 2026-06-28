# Relations and Operators

RTDL programs are built from relations. A relation is a table of facts produced
by traversal:

- point `i` has at least one neighbor inside radius `r`;
- ray `j` hits triangle `k`;
- query point `q` has nearest witness `w`;
- box `a` overlaps box `b`;
- body `p` should use aggregate cell `c`.

An operator is the generic RTDL surface that creates or summarizes one of those
relations. The app name is not the operator. RTDBSCAN, RTNN, triangle counting,
robot collision, and Barnes-Hut all reuse a smaller set of generic operators.

Ask for the operator you need:

```python
import rtdsl.v4 as rtdl_v4

requests = [
    ("fixed_radius", "torch"),
    ("any_hit", "torch"),
    ("point_group_nearest", "torch"),
    ("aabb_index_query", "rtdl_native"),
    ("grouped_sum", "cupy"),
]

for operator, partner in requests:
    plan = rtdl_v4.plan_operator_request_v4(operator, partner=partner)
    print(operator, partner, plan.status, plan.api_surface)
```

This planner step is valuable even before you have real data. It tells you
whether your idea maps to a current V4 operator, which partner it uses, and
which prepare function to open next.

## Single-Skill Programs

Before opening full benchmark apps, run the small programs that teach one
concept at a time. Read the JSON fields named `candidate_rows`,
`neighbor_rows`, `nearest_rows`, `hit_rows`, or `manual_data_flow`; those are
the programming idea.

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\tutorial_programs\operator_primitives.py
py -3 examples\tutorial_programs\partner_choices.py
py -3 examples\tutorial_programs\fixed_radius_neighbors.py
py -3 examples\tutorial_programs\nearest_neighbor.py
py -3 examples\tutorial_programs\ray_triangle_hits.py
py -3 examples\tutorial_programs\continuation_grouped_sum.py
py -3 examples\tutorial_programs\point_in_polygon.py
py -3 examples\tutorial_programs\spatial_join_lsi.py
```

Linux or macOS:

```bash
PYTHONPATH=src:. python examples/tutorial_programs/operator_primitives.py
PYTHONPATH=src:. python examples/tutorial_programs/partner_choices.py
PYTHONPATH=src:. python examples/tutorial_programs/fixed_radius_neighbors.py
PYTHONPATH=src:. python examples/tutorial_programs/nearest_neighbor.py
PYTHONPATH=src:. python examples/tutorial_programs/ray_triangle_hits.py
PYTHONPATH=src:. python examples/tutorial_programs/continuation_grouped_sum.py
PYTHONPATH=src:. python examples/tutorial_programs/point_in_polygon.py
PYTHONPATH=src:. python examples/tutorial_programs/spatial_join_lsi.py
```

The point is not that every app calls a different primitive. The point is that
many apps are built from the same few relation-producing operators plus
different continuation and app code. The V4 planner tells you which accelerated
surface matches that relation after you understand the relation itself.

RTDL also has a recognizer for small declarative descriptions:

```python
import rtdsl.v4 as rtdl_v4

expr = {
    "relation": "any_hit",
    "input": "rays_and_triangles",
    "continuation": "flags",
}

recognized = rtdl_v4.recognize_pushdown_request_v4(expr, partner="torch")
print(recognized.status)
print(recognized.plan.api_surface)
```

Next: [Prepare, Run, Continue](05_prepare_run_continue.md)
