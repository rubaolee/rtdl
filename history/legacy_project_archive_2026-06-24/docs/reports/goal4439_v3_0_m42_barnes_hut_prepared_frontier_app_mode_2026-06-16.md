# Goal4439 / V3.0 M42 - Barnes-Hut Prepared Frontier App Mode

## Result

M42 turns the M39/M41 prepared aggregate-frontier route into a named Barnes-Hut
benchmark app mode:

```text
prepared_aggregate_frontier_weighted_vector_optix
```

The mode runs RTDL/OptiX aggregate-frontier device columns and then hands those
columns to an explicit app-selected partner:

- `--partner numba`
- `--partner cupy`

This closes an important usability gap. M41 proved the route in a scale-ladder
script; M42 makes it a normal benchmark-app entrypoint with CLI flags, JSON
output, capacity probing, repeat/warmup timing, validation for small cases, and
clear claim flags.

## API And CLI

Example:

```text
PYTHONPATH=src:. python examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py --mode prepared_aggregate_frontier_weighted_vector_optix --partner numba --body-count 8192 --bucket-size 64 --theta 0.5 --repeat 5 --warmup 1 --skip-validation --force-output-mode force_summary
```

New route controls:

- `--frontier-row-capacity`: optional explicit row capacity
- `--frontier-capacity-multiplier`: default initial capacity multiplier, `700`
- `--partner`: explicit; only `numba` and `cupy` are accepted for this mode

The default capacity probe starts from `body_count * 700`, reads the native
`attempted_count` if overflow occurs, and reruns with `attempted_count + 1024`.

## 8192-Body App-Mode Evidence

Measured configuration:

- RTX 4000 Ada pod
- 8192 bodies
- bucket size 64
- theta 0.5
- app softening 0.05
- 1 warmup, 5 measured repeats
- validation skipped for the 8192-body timing rows
- force rows suppressed with `--force-output-mode force_summary`

| Partner | Frontier rows | Frontier median | Partner median | Native+partner hot median | Wall median |
| --- | ---: | ---: | ---: | ---: | ---: |
| Numba | 3,406,489 | 0.014865 s | 0.001296 s | 0.016139 s | 0.022338 s |
| CuPy | 3,406,489 | 0.014948 s | 0.008339 s | 0.023295 s | 0.029347 s |

Same app mode, same frontier contract:

- Numba partner continuation is 6.43x faster than CuPy.
- Numba native+partner hot window is 1.44x faster than CuPy.
- Numba wall median around the app-mode calls is 1.31x faster than CuPy.

Raw evidence:

- `docs/reports/goal4439_v3_0_m42_barnes_hut_app_mode_numba_8192_2026-06-16.json`
- `docs/reports/goal4439_v3_0_m42_barnes_hut_app_mode_cupy_8192_2026-06-16.json`

## 128-Body Correctness Smoke

The pod also ran the Numba app mode at 128 bodies with CPU validation enabled.

| Bodies | Frontier rows | max abs diff x | max abs diff y | tolerance | Result |
| ---: | ---: | ---: | ---: | ---: | --- |
| 128 | 8,766 | 7.19e-14 | 4.26e-14 | 1e-7 | pass |

Raw evidence:

- `docs/reports/goal4439_v3_0_m42_barnes_hut_app_mode_numba_128_smoke_2026-06-16.json`

## Boundary

M42 is an app-mode integration, not a new native engine primitive. The native
engine still sees only the app-agnostic RTDL/OptiX aggregate-frontier
device-column contract. Barnes-Hut force math remains partner code.

Claim flags stay conservative:

- `automatic_partner_selection_allowed = False`
- `native_engine_app_specific = False`
- `frontier_columns_materialized_on_host = False`
- `contribution_rows_materialized_on_host = False`
- `rt_core_speedup_claim_authorized = False`
- `whole_app_speedup_claim_authorized = False`
- `public_speedup_claim_authorized = False`
- `true_zero_copy_claim_authorized = False`

What M42 can say:

- The prepared aggregate-frontier route is now usable from the Barnes-Hut
  benchmark app.
- Users can run both the best measured partner, Numba, and the same-contract
  CuPy comparison without writing C++ or CUDA files.
- RTDL avoids unnecessary frontier-row and contribution-row host
  materialization on this route.

What M42 cannot say:

- It is not a whole Barnes-Hut N-body speedup claim.
- It is not an OptiX-vs-Embree or GPU-vs-CPU comparison.
- It is not a public RT-core acceleration claim.
- It is not proof that Numba always beats CuPy.

## Next

The next clean target is same-contract CPU/Embree evidence for this exact
prepared aggregate-frontier app route. That comparison must hold app semantics,
tree policy, theta, softening, partner work, output contract, and timing window
fixed before any backend wording is considered.
