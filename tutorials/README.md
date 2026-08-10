# RTDL Tutorials

Tutorials are for teaching. They are not the reference manual, and they are not
the example inventory.

Use this directory when you want an ordered learning path for the current RTDL
source-tree surface.

## Start Here

| Path | Purpose |
| --- | --- |
| [V3 Canonical Lowering Tutorial](v3_canonical_lowering.md) | Start with the V3 statement-to-provider contract, then follow the target validation path. |
| [Foundational RTDL Tutorial Track](current/README.md) | Learn the retained Python, primitive, prepared, and partner foundations step by step. |

## Current Track

| Step | Tutorial |
| --- | --- |
| 1 | [Run From The Source Tree](current/01_source_tree_first_run.md) |
| 2 | [Kernel Shape And Backends](current/02_kernel_shape_and_backends.md) |
| 3 | [Primitive Discovery](current/03_primitives_and_discovery.md) |
| 4 | [Python App Structure](current/04_python_app_structure.md) |
| 5 | [Partner Columns With CuPy Or Numba](current/05_partner_columns_cupy_numba.md) |
| 6 | [Prepared Execution And Measurement](current/06_prepared_execution_measurement.md) |
| 7 | [Benchmark App Walkthrough](current/07_benchmark_app_python_rtdl_partner.md) |
| 8 | [Spatial Join Benchmark Reference](current/08_spatial_join_rayjoin_reference.md) |

## What Belongs Where

| Area | Purpose | Use it when you ask... |
| --- | --- | --- |
| `tutorials/` | Teaching path | "How do I learn RTDL in order?" |
| `docs/` | Reference docs | "What does this API, primitive, architecture, or boundary mean?" |
| `examples/` | Runnable code | "Can I run or adapt a working program?" |
| `history/` | Archive | "What happened in older releases or audits?" |

## Current Claim Boundary

The active release is V3.0. The canonical-lowering tutorial teaches its
compiler-owned statement-to-provider contract. The longer foundational track
retains the Python, prepared-execution, and partner concepts inherited from the
v2 line.

These tutorials do not claim automatic algorithm invention, universal speedup,
or unrestricted callback support.

## Related Doors

- [Project Front Page](../README.md)
- [Docs Index](../docs/README.md)
- [Examples Index](../examples/README.md)
- [App And Example Quickstart](../docs/app_example_quickstart.md)
- [Application Catalog](../docs/application_catalog.md)
- [Partner Acceleration Boundaries](../docs/partner_acceleration_boundaries.md)
- [Tutorial Archive](../history/tutorial_archive/README.md)
