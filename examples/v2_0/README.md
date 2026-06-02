# RTDL v2.x Examples

This is the current learner-facing example tree for the RTDL v2.x
Python+partner+RTDL source-tree surface. v2.3 is the latest released evidence
package; v2.6 partner-choice guidance is active pre-release work in this same
tree.

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
