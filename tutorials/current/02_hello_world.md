# Front-Door Quickstart

V4 starts with one import:

```python
import rtdsl.v4 as rtdl_v4
```

List measured operators:

```python
for row in rtdl_v4.measured_operator_catalog_v4():
    print(row["operator"], row["api_surface"], row["measured_partners"])
```

Run the example:

```powershell
py -3 examples\v4\v4_frontdoor_quickstart.py
```

Expected shape:

```json
{
  "status": "ok",
  "measured_surface_count": 8,
  "candidate_surface_count": 0
}
```

Next: [Operator Choice](03_backend_choice.md)
