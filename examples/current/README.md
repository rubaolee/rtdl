# RTDL Current Examples

This is the current learner-facing example tree for the RTDL v2.14
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

V4 has two closed public GPU protocol families:

- `v4_public_bounded_relation.py` for custom-AABB canonical relation rows;
- `v4_public_triangle_reduction.py` for checked built-in-triangle reduction.

`v4_public_stable_sort.py` is an application example built entirely on the
first family.  It maps stable ordering to a predecessor relation, derives rank
from RT output, and linearly scatters records.  It is a correctness demo for
whole-callback identity/capacity contracts, not a new protocol family or a
high-performance alternative to CUB/Thrust sorting.

All three import RTDL exclusively through `rtdsl.v4` and require explicit native,
OptiX/CUDA include, compute-capability, and external proof-file arguments.  They
are functional examples, not performance or ease-of-use evidence.
