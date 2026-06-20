# RTDL Tutorials

Tutorials are for teaching. They are not the reference manual, and they are not
the example inventory.

Use this directory when you want an ordered learning path for the current RTDL
source-tree surface.

## Start Here

| Path | Purpose |
| --- | --- |
| [V4.0 Tutorial Track](v4_0/README.md) | Learn the current V4.0 Python GPU device-array operator route. |
| [V3 Tutorial Track](current/README.md) | Learn the broader V3 Python+RTDL+partner programming surface. |

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

## V4.0 Current Track

| Step | Tutorial |
| --- | --- |
| 1 | [Source-Tree GPU Setup](v4_0/01_source_tree_gpu_setup.md) |
| 2 | [CuPy Fixed-Radius Route](v4_0/02_fixed_radius_cupy.md) |
| 3 | [Numba DeviceArray Route](v4_0/03_numba_device_array_route.md) |
| 4 | [PyTorch CUDA Tensor Route](v4_0/04_pytorch_cuda_tensor_route.md) |
| 5 | [Boundaries And Troubleshooting](v4_0/05_boundaries_and_troubleshooting.md) |

## What Belongs Where

| Area | Purpose | Use it when you ask... |
| --- | --- | --- |
| `tutorials/` | Teaching path | "How do I learn RTDL in order?" |
| `docs/` | Reference docs | "What does this API, primitive, architecture, or boundary mean?" |
| `examples/` | Runnable code | "Can I run or adapt a working program?" |
| `history/` | Archive | "What happened in older releases or audits?" |

## Current Claim Boundary

The V4.0 tutorial track teaches the current source-tree release: one
fixed-radius Python GPU device-array route with CuPy, Numba, and PyTorch
evidence. The V3 tutorial track remains the broader Python+RTDL, explicit
partner, and generic app-agnostic primitive path.

These tutorials are not package-install promises, automatic partner-selection
promises, universal speedup claims, or paper-reproduction claims.

## Related Doors

- [Project Front Page](../README.md)
- [Docs Index](../docs/README.md)
- [Examples Index](../examples/README.md)
- [App And Example Quickstart](../docs/app_example_quickstart.md)
- [Application Catalog](../docs/application_catalog.md)
- [Partner Acceleration Boundaries](../docs/partner_acceleration_boundaries.md)
- [Tutorial Archive](../history/tutorial_archive/README.md)
