# Hausdorff / X-HD-Style Benchmark

This directory contains the current RTDL v2.14 benchmark app for **Hausdorff / X-HD-Style**.

## Start

From the repository root:

```bash
PYTHONPATH=src:. python examples/current/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py --help
```

When the app exposes `--backend cpu_python_reference`, use that first for a portable smoke run. Use Embree or OptiX only when the native backend is configured on your machine.

## What RTDL Owns

RTDL owns the RT-shaped kernel contract for this benchmark: prepared nearest/fixed-radius style distance decision.

## What The Python App Owns

The Python app owns data setup, benchmark fixtures, policy decisions, labels, final interpretation, and any domain-specific continuation not expressed by a generic RTDL primitive.

## Boundary

This benchmark is not exact Hausdorff proof or universal CUDA speedup. Treat timing as exact-contract evidence only. For public wording, use the v2.14 release package and support matrices rather than this README alone.

## Related Current Docs

- [Application Catalog](../../../../docs/application_catalog.md)
- [App Engine Support Matrix](../../../../docs/app_engine_support_matrix.md)
- [Performance Model](../../../../docs/performance_model.md)
