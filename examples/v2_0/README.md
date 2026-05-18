# RTDL v2.0 Examples

This is the current learner-facing example tree for the RTDL v2.0
Python+partner+RTDL release.

Internal v2.1 keeps using this tree. It adds reviewed RayJoin/Hausdorff
benchmark evidence and readiness checks, but it is not a separate public
example version.

| Directory | Purpose |
| --- | --- |
| `getting_started/` | smallest programs and the feature cookbook |
| `features/` | examples grouped by primitive or workload feature |
| `apps/` | complete application-level examples |
| `partners/` | examples that continue RTDL outputs with NumPy, CuPy, or user-owned native code |
| `research_benchmarks/` | serious performance studies such as Hausdorff/X-HD and spatial/RayJoin |

Use source-tree execution from the repository root:

```bash
PYTHONPATH=src:. python examples/v2_0/getting_started/rtdl_hello_world.py
```
