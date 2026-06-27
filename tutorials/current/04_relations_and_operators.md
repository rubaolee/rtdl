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
