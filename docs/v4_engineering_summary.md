# RTDL V4.0.0 Engineering Summary

This page gives maintainers a compact technical view of the V4.0.0 release
shape while keeping the first-time user path focused on current docs and
examples.

## Architecture

V4 is a Python eDSL/operator-pushdown layer:

```text
Python application
  -> V4 planner and API surface
  -> generic RT-shaped operator
  -> explicit partner or RTDL native prepared runner
  -> app code consumes the result
```

The engine may expose generic continuation operators, such as count threshold,
argmin, grouped reduction, component union, aggregate-frontier columns, and
pure predicate early-exit. It must not expose app-identity kernels such as
"DBSCAN kernel" or "Barnes-Hut kernel" as the public programming model.

## Release Checks Used For V4.0.0

The V4.0.0 release path used these checks:

- clean public docs and examples;
- copy-paste runnable tutorial snippets;
- 10-app matrix facts are present and denominator wording is exact;
- wheel build and installed-wheel smoke pass;
- required evidence files are tracked by Git, including log files that would
  otherwise be ignored by normal ignore rules;
- the tag target matches the intended release commit.

## Evidence Policy

The public path stays short and current. Public pages should link to the current
docs and examples. Compact release evidence stays available for maintainers who
need to reproduce the checks.

## Current Matrix Facts

| Fact | Value |
| --- | --- |
| Apps | `10` |
| V2.14/V3.0.2/V4.0 rows | `30` |
| Primary denominator | NVIDIA RT-core/OptiX rows |
| Hot-path regressions in the current table | `0` |
| Material V4/V2.14 hot-path rows | `triangle_counting`, `barnes_hut` |
| Broad all-app speedup wording | not supported |

Use [app_level_benchmark_summary.md](app_level_benchmark_summary.md) for the
reader-facing table.

## Partner Policy

Partners are explicit:

- Torch CUDA is the measured partner for most device-array operator examples.
- CuPy is supported where a surface explicitly names it, especially grouped
  continuation work.
- Numba is supported where a surface explicitly names it, including component
  union and constrained predicate early-exit.
- RTDL native prepared runners own index/frontier routes.

Do not turn partner availability into broad partner performance wording. Each
claim needs its own denominator and scale.
