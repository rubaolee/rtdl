# RTDL V4 Tutorial

This path teaches RTDL as a programming model. It starts from the idea of ray
tracing and ends with recipes for the 10 benchmark apps.

Read the lessons in order:

1. [What RTDL Is](01_first_run.md)
2. [Hello RTDL](02_hello_world.md)
3. [Relations and Operators](03_backend_choice.md)
4. [Prepare, Run, Continue](04_prepared_runtime.md)
5. [Measure a Program](05_measurement_boundaries.md)
6. [Build the Benchmark Apps](06_benchmark_apps.md)
7. [Choose a Partner](07_partner_choice.md)

By the end you should understand how to:

- describe an RT-shaped relation such as radius-neighbor, any-hit,
  nearest-witness, AABB query, or aggregate-frontier;
- ask the V4 planner for the current operator surface;
- choose Torch, CuPy, Numba, or RTDL native explicitly;
- keep application meaning outside the generic operator;
- combine an RT relation with a continuation step;
- read the benchmark app recipes before opening the full harnesses.
