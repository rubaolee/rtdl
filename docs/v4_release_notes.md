# RTDL V4.0.0 Release Notes

V4.0.0 is the current Python eDSL release for RT-shaped GPU work on NVIDIA RT
cores.

Use V4 as the current entrypoint:

```python
import rtdsl.v4 as rtdl_v4
```

## Highlights

- A single V4 import for app authors.
- V2.14 and V3 routes remain available through the current system.
- Generic operator planning for fixed-radius, nearest-witness, ray/triangle,
  AABB, aggregate-frontier, grouped-reduction, and constrained predicate
  workflows.
- Explicit partner selection for Torch CUDA, CuPy, Numba, and RTDL native
  routes where each is supported.
- A complete NVIDIA RT-core table for the 10 promoted benchmark apps across
  V2.14, V3.0.2, and V4.0 rows.
- A bounded custom predicate early-exit workflow for pure Numba boolean
  predicates.

## Performance Reading

The 10-app table has two material hot-path rows over V2.14:

- Triangle counting;
- Barnes-Hut aggregate frontier.

Most other app rows are similar-speed or modest-gain rows on the current
NVIDIA RT-core table. The useful reading is the distribution in
[app_level_benchmark_summary.md](app_level_benchmark_summary.md), not a blanket
statement that every app became faster.

Operator-level results live in
[learn/operator_catalog.md](learn/operator_catalog.md). Each operator row names
its partner scope and representative denominator.

## Learning Path

1. [Current V4 Status](current_v4_status.md)
2. [Operator Catalog](learn/operator_catalog.md)
3. [Partner Choice](learn/partner_choice.md)
4. [Tutorials](../tutorials/current/README.md)
5. [Examples](../examples/README.md)
6. [App-Level Benchmark Summary](app_level_benchmark_summary.md)
