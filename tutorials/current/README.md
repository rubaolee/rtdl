# RTDL V4 Tutorial

This path teaches RTDL as a programming model. It starts from the idea of ray
tracing and ends with recipes for the 10 benchmark apps.

Read the lessons in order:

1. [What RTDL Is](01_first_run.md)
2. [Hello RTDL](02_hello_world.md)
3. [Sorting Rows](03_sorting_rows.md)
4. [Relations and Operators](04_relations_and_operators.md)
5. [Prepare, Run, Continue](05_prepare_run_continue.md)
6. [Measure a Program](06_measure_a_program.md)
7. [Build the Benchmark Apps](07_benchmark_apps.md)
8. [Choose a Partner](08_choose_a_partner.md)

By the end you should understand how to:

- describe an RT-shaped relation such as radius-neighbor, any-hit,
  nearest-witness, AABB query, or aggregate-frontier;
- run tutorial programs for NN, radius neighbors, ray hits, PIP, spatial join,
  partner choice, primitives, and continuations;
- ask the V4 planner for the current operator surface;
- choose Torch, CuPy, Numba, or RTDL native explicitly;
- keep application meaning outside the generic operator;
- combine an RT relation with a continuation step;
- run small tutorial programs before opening the full benchmark apps;
- read the benchmark app recipes before opening the full app sources.
