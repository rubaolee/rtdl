# Current RTDL Tutorial Track

Status: current v2.10 source-tree learner path.

This track teaches RTDL from zero to a benchmark-style Python+RTDL+partner
program. It is intentionally short and ordered. Start here when you want to
learn the current programming model rather than browse project history.

## What RTDL Is

RTDL is a Python eDSL for writing traversal-shaped compute programs.

```text
Python owns the application.
RTDL expresses the primitive.
The backend executes the primitive.
CuPy or Numba can continue selected typed columns when custom logic is needed.
```

The engine is app-agnostic. Benchmark apps are examples of how to compose
generic primitives, not hidden custom engines.

## Tutorial Ladder

| Step | Tutorial | Outcome |
| --- | --- | --- |
| 1 | [Run From The Source Tree](01_source_tree_first_run.md) | Run the smallest RTDL examples and learn the source-tree setup. |
| 2 | [Kernel Shape And Backends](02_kernel_shape_and_backends.md) | Understand input, traversal, refine, emit, and backend choice. |
| 3 | [Primitive Discovery](03_primitives_and_discovery.md) | Find an existing primitive before creating a new app path. |
| 4 | [Python App Structure](04_python_app_structure.md) | Divide a program into Python app logic and RTDL primitive logic. |
| 5 | [Partner Columns With CuPy Or Numba](05_partner_columns_cupy_numba.md) | Learn when a partner is useful and how to keep the choice explicit. |
| 6 | [Prepared Execution And Measurement](06_prepared_execution_measurement.md) | Separate setup, warmup, validation, and steady-state timing. |
| 7 | [Benchmark App Walkthrough](07_benchmark_app_python_rtdl_partner.md) | Run an RT-DBSCAN-style benchmark app with CPU, RTDL, CuPy, and Numba routes. |

## Prerequisites

For the first four tutorials:

- a Python environment that can import this source tree;
- a shell at the repository root;
- `PYTHONPATH=src:.` on Linux/macOS or `$env:PYTHONPATH='src;.'` on Windows
  PowerShell.

For partner and OptiX tutorials:

- CuPy and/or Numba only for the partner routes you choose;
- `librtdl_optix.so` and `RTDL_OPTIX_LIBRARY` only for OptiX routes;
- a CUDA-capable machine only when running GPU partner or OptiX examples.

## Claim Boundary

These tutorials are current source-tree guidance. They are not package-install
promises, universal speedup claims, or automatic partner-selection rules.

Use the exact command, backend, partner, dataset, and hardware when reporting
performance. If a tutorial says a route is optional, CUDA-only, or OptiX-only,
treat that route as unavailable until your environment proves it.

## Where To Go Next

- [Tutorial Reference Pages](../README.md)
- [App And Example Quickstart](../../app_example_quickstart.md)
- [Primitive Catalog](../../rtdl_primitive_catalog.md)
- [Partner Choice For Custom Logic](../../learn/partner_choice_for_custom_logic.md)
- [Research Benchmark Apps](../../../examples/current/research_benchmarks/README.md)
