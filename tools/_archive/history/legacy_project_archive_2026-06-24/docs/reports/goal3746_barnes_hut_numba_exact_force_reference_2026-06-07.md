# Goal3746 Barnes-Hut Numba Exact-Force Reference

## Purpose

Goal3746 closes the Barnes-Hut partner-reference gap found by Goal3740:
users should be able to run the app's custom force-vector continuation with
Numba CUDA JIT instead of writing CuPy RawKernel code.

This is intentionally app/partner-layer work. The native RTDL engine remains
app-agnostic and does not embed Barnes-Hut force math.

## Implementation

- `weighted_point_rows_to_partner_columns(..., partner="numba")` now creates
  Numba-owned weighted point columns.
- `pairwise_inverse_square_force_2d_partner_columns(..., partner="numba")`
  adds an app-scoped Numba CUDA JIT implementation for the exact all-pairs
  softened inverse-square vector sum.
- The simulation app and research benchmark wrapper now accept
  `--partner numba` for `partner_exact_force`.
- The Barnes-Hut README documents the Numba path as a no-RawKernel reference.

## Boundary

This path is an exact all-pairs force-vector reference. It is not hierarchical Barnes-Hut acceleration, not a full RT-BarnesHut paper reproduction, and not an RT-core claim. It exists to show how a user can write custom CUDA-side app logic through the supported Numba partner lane while preserving the generic engine boundary.

## Validation

Local validation:

```text
PYTHONPATH=src;. py -3 -m unittest tests.goal3746_barnes_hut_numba_exact_force_reference_test
```

A5000 pod evidence is recorded in:

- `docs/reports/goal3746_barnes_hut_numba_exact_force_a5000/summary.json`

Correctness spot check:

| Body count | Partner | Result |
| ---: | --- | --- |
| 256 | Numba CUDA JIT | matches CPU oracle, max relative error `5.489235176361001e-15` |

Same-contract exact all-pairs force timing after warmup/JIT compilation:

| Body count | CuPy RawKernel median sec | Numba CUDA JIT median sec | Numba / CuPy |
| ---: | ---: | ---: | ---: |
| 1024 | 0.004504 | 0.005971 | 0.754x |
| 2048 | 0.008528 | 0.010573 | 0.807x |
| 4096 | 0.016904 | 0.019944 | 0.848x |
| 8192 | 0.034285 | 0.038382 | 0.893x |

The tuned Numba path uses `cuda.jit(fastmath=True)`. It is slower than the
hand-written CuPy RawKernel path on this A5000 run, but it is close enough to
serve as a real high-performance no-RawKernel reference for users who prefer
Numba. The result does not authorize a public speedup claim.
