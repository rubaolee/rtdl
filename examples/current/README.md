# RTDL Current Examples

This is the current learner-facing example tree for the RTDL v2.10
released Python+partner+RTDL source-tree surface. This tree is intentionally
named `current/` so learner-facing examples are not frozen under an old release
number.

| Directory | Purpose |
| --- | --- |
| `getting_started/` | smallest programs, primitive discovery, and the feature cookbook |
| `features/` | examples grouped by primitive or workload feature |
| `apps/` | complete application-level examples |
| `partners/` | examples that continue RTDL outputs with NumPy, CuPy, Numba, or user-owned native code |
| `learner_apps/` | app-scale learner and design-pressure cases that are not promoted benchmarks |
| `research_benchmarks/` | serious performance studies such as Hausdorff/X-HD and spatial/RayJoin |

Use source-tree execution from the repository root:

```bash
PYTHONPATH=src:. python examples/current/getting_started/rtdl_hello_world.py
PYTHONPATH=src:. python examples/current/getting_started/rtdl_primitive_discovery_workflow.py
```
