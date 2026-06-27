# RTDL V4.0.0 Engineering Summary

This file is a compact maintainer note for the current V4.0.0 release shape.
New users should start with [README.md](README.md).

## Architecture

```text
Python application
  -> V4 planner and API surface
  -> generic RT-shaped operator
  -> explicit partner or RTDL native prepared runner
  -> application code consumes the result
```

The engine exposes generic continuation operators such as count threshold,
argmin, grouped reduction, component union, aggregate-frontier columns, and
pure predicate early-exit. The public programming model avoids app-identity
kernels such as "DBSCAN kernel" or "Barnes-Hut kernel"; apps compose generic
operators instead.

## Current Release Checks

The current release shape has:

- clean public docs and examples;
- runnable tutorial snippets;
- a complete 10-app NVIDIA RT-core table;
- named denominators for operator and app rows;
- wheel build and installed-wheel smoke coverage;
- a release tag that matches the committed source tree.

## Matrix Facts

| Fact | Value |
| --- | --- |
| Apps | `10` |
| V2.14/V3.0.2/V4.0 rows | `30` |
| Primary hardware path | NVIDIA OptiX / RT cores |
| Hot-path regressions in the current table | `0` |
| Material V4/V2.14 hot-path rows | Triangle counting, Barnes-Hut |

Use [app_level_benchmark_summary.md](app_level_benchmark_summary.md) for the
reader-facing table.

## Partner Policy

- Torch CUDA is the measured partner for most device-array operator examples.
- CuPy is supported where a surface explicitly names it, especially grouped
  continuation work.
- Numba is supported where a surface explicitly names it, including component
  union and constrained predicate early-exit.
- RTDL native prepared runners own index/frontier routes.

Each performance statement needs its own denominator, scale, and partner scope.
