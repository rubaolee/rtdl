# RTDL V4.0.0 Release Notes

V4.0.0 is the current Python eDSL/operator-pushdown release for RT-shaped GPU
work on NVIDIA RT cores.

Use V4 as the single current entrypoint:

```python
import rtdsl.v4 as rtdl_v4
```

## What Changed

V4 keeps the mature V2.14 and V3 routes available through the current system
and adds a cleaner operator front door:

- one V4 import for app authors;
- generic operator planning for fixed-radius, nearest-witness, ray/triangle,
  AABB, aggregate-frontier, grouped-reduction, and constrained predicate
  workflows;
- explicit partner selection for Torch CUDA, CuPy, Numba, and RTDL native
  routes where each is named;
- a complete NVIDIA RT-core 10-app matrix for V2.14, V3.0.2, and V4.0;
- a bounded custom predicate early-exit workflow for pure Numba boolean
  predicates.

## Performance Reading

The 10 promoted benchmark apps all have V2.14, V3.0.2, and V4.0 rows on the
current NVIDIA RT-core matrix.

V4.0 has two material hot-path rows over V2.14:

- Triangle counting;
- Barnes-Hut aggregate frontier.

Most other app rows are similar-speed control rows. Use the distribution in
[app_level_benchmark_summary.md](app_level_benchmark_summary.md) when discussing
whole-app results instead of reducing the release to one blanket phrase.

Operator-surface results live in
[learn/operator_catalog.md](learn/operator_catalog.md). Each operator row names
its denominator, partner scope, and boundary.

## User-Facing Boundaries

V4.0.0 supports:

- the current V4 Python front door;
- inherited V2/V3 routes when they are the right implementation;
- measured generic operator/workflow surfaces;
- bounded Torch, CuPy, Numba, and RTDL native partner scopes;
- constrained custom predicate early-exit planning.

Keep these phrases out of broad public claims:

- every benchmark app is faster;
- broad V4-over-V2.14 or V4-over-V3 speedup;
- whole-application speedup for every app;
- public true-zero-copy support;
- raw OptiX callback support;
- arbitrary Tier-3 callback/PTX support;
- C ABI, embedding, or non-Python host binding support.

## Learning Path

Start with:

1. [Current V4 Status](current_v4_status.md)
2. [Operator Catalog](learn/operator_catalog.md)
3. [Partner Choice](learn/partner_choice.md)
4. [Tutorials](../tutorials/current/README.md)
5. [App-Level Benchmark Summary](app_level_benchmark_summary.md)
