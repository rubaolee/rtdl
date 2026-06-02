# RTDL v2.x Examples

This is the current learner-facing example tree for the RTDL v2.6
release-candidate Python+partner+RTDL source-tree surface. The directory name
`v2_0/` is retained as a stable v2.x compatibility path; the docs in this tree
describe the current v2.6 behavior.

| Directory | Purpose |
| --- | --- |
| `getting_started/` | smallest programs and the feature cookbook |
| `features/` | examples grouped by primitive or workload feature |
| `apps/` | complete application-level examples |
| `partners/` | examples that continue RTDL outputs with NumPy, CuPy, Numba, or user-owned native code |
| `learner_apps/` | app-scale learner and design-pressure cases that are not promoted benchmarks |
| `research_benchmarks/` | serious performance studies such as Hausdorff/X-HD and spatial/RayJoin |

Use source-tree execution from the repository root:

```bash
PYTHONPATH=src:. python examples/v2_0/getting_started/rtdl_hello_world.py
```
