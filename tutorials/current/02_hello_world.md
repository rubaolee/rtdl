# Hello RTDL

Every V4 program starts with one import:

```python
import rtdsl.v4 as rtdl_v4
```

The smallest useful program asks the planner for one RT-shaped relation. A
fixed-radius query means: for each query point, find or count reference points
inside a radius.

```python
import rtdsl.v4 as rtdl_v4

plan = rtdl_v4.plan_operator_request_v4("fixed_radius", partner="torch")
print(plan.status)
print(plan.api_surface)
print(plan.generic_primitive)
```

You have not run a GPU kernel yet. You have asked RTDL: "Is this a current V4
operator, and which API surface should I use?"

List the current operator surfaces:

```python
import rtdsl.v4 as rtdl_v4

for row in rtdl_v4.measured_operator_catalog_v4():
    partners = ",".join(row["measured_partners"])
    print(row["operator"], row["api_surface"], partners)
```

Run the quickstart script:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\simple\v4_frontdoor_quickstart.py
```

Next: [Sorting Rows](03_sorting_rows.md)
