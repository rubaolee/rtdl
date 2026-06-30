# Goal2725: Triangle Counting v2.5 Plan Mode

Date: 2026-05-30
Status: accepted as executable planning guardrail

## Purpose

The v2.5 tiered manifest classifies `triangle_counting` as Tier A, meaning it should be realistic to compare against the current Triton grouped/scalar continuation surface. However, the current fast RT-Graph-style paths are not already Triton benchmark paths:

- `rt_graph_2a1_generic_rt` uses generic ray-triangle weighted any-hit summaries;
- `rt_graph_1a2_generic_rt` uses generic ray-triangle hit-count summaries;
- the optional `--partner cupy` path builds device geometry for the existing summary path, but it is not a v2.5 Triton continuation benchmark.

Goal2725 adds an executable app mode:

`--mode v2_5_plan`

The mode reports the precise v2.5 target and blocks a misleading shortcut: do not relabel the existing native scalar summary as Triton.

## Behavior

`v2_5_plan` returns:

- the Tier A manifest row;
- current fast paths;
- required generic partner operations;
- same-contract opponent;
- canonical harness status;
- next action;
- claim boundary flags that keep Triton integration and parity claims false.

## Boundary

This is not the triangle-counting v2.5 implementation. It is a guardrail before implementation.

The next implementation goal must choose a same-contract row or summary boundary that genuinely feeds generic Triton segmented count/sum or compact-mask continuation, then compare it against the existing CuPy/native same-contract path on an `sm_70+` pod.
