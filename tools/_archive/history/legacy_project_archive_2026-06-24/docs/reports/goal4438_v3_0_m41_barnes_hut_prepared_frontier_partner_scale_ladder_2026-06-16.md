# Goal4438 / V3.0 M41 - Barnes-Hut Prepared Frontier Partner Scale Ladder

## Result

M41 reruns the Barnes-Hut prepared aggregate-frontier device-column path at
three point scales and compares the two explicit Python-accessible partners on
the same RTDL/OptiX frontier contract:

- CuPy prepared weighted-vector continuation from M38
- Numba prepared weighted-vector continuation from M39

The result changes the current partner guidance for this contract. For the
prepared aggregate-frontier device-column weighted-vector route, Numba is the
current fastest measured partner and also the no-C++ Python-source route. CuPy
remains the same-contract comparison partner and remains valid evidence for
older exact-force rows that used a different contract.

## Timing Matrix

Measured configuration:

- RTX 4000 Ada pod
- bucket size 64
- theta 0.5
- softening 0.01
- 5 hot repeats per row after warmup
- source, target, and node lookup columns resident in the partner object
- no host materialization of frontier rows or contribution rows

| Points | Frontier rows | CuPy partner median | Numba partner median | Numba partner speedup | CuPy native+partner hot | Numba native+partner hot | Numba hot speedup |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 8,192 | 3,440,003 | 0.008451 s | 0.001252 s | 6.75x | 0.022707 s | 0.014712 s | 1.54x |
| 16,384 | 12,581,598 | 0.035038 s | 0.004939 s | 7.09x | 0.060444 s | 0.030269 s | 2.00x |
| 32,768 | 15,385,218 | 0.041524 s | 0.005028 s | 8.26x | 0.118851 s | 0.082540 s | 1.44x |

Correctness passed for every scale against the CuPy prepared output from the
same frontier contract:

| Points | max abs diff x | max abs diff y | tolerance |
| ---: | ---: | ---: | ---: |
| 8,192 | 3.33e-14 | 3.38e-14 | 1e-7 |
| 16,384 | 3.73e-14 | 5.08e-14 | 1e-7 |
| 32,768 | 3.95e-14 | 5.24e-14 | 1e-7 |

The raw evidence is recorded in:

- `docs/reports/goal4438_v3_0_m41_barnes_hut_prepared_frontier_partner_scale_ladder_2026-06-16.json`

## Interpretation

The speedup is explainable. Both partners consume the same RTDL/OptiX frontier
columns, so the measured difference is not a different tree, different opening
rule, or different frontier contract. The difference is in the continuation:

- Numba fuses contribution math and grouped accumulation into one CUDA JIT
  kernel using device atomics.
- CuPy expresses the continuation as an array-operation chain plus grouped
  `bincount` reductions.
- The Numba route therefore reduces intermediate work and launch/materialization
  pressure inside the partner continuation.

This is exactly the kind of partner evidence V3 needs: RTDL emits an
app-agnostic frontier primitive, while the application supplies a clearly named
force-law continuation. The partner is explicit; there is no hidden
auto-selection.

## Claim Boundary

M41 does not authorize public RT-core or whole-application speedup wording.

Conservative flags stay false:

- `rt_core_speedup_claim_authorized = False`
- `whole_app_speedup_claim_authorized = False`
- `public_speedup_claim_authorized = False`
- `true_zero_copy_claim_authorized = False`

What M41 can say:

- For the prepared aggregate-frontier device-column weighted-vector contract,
  Numba is currently faster than CuPy on the RTX 4000 Ada pod at 8k, 16k, and
  32k points.
- RTDL avoids unnecessary host materialization in this route: frontier rows and
  contribution rows remain device-side.
- The route remains app-agnostic at the RTDL primitive layer: the native engine
  emits frontier columns; the Barnes-Hut force law remains app partner logic.

What M41 cannot say:

- It is not a whole Barnes-Hut N-body speedup claim.
- It is not an OptiX-vs-Embree or GPU-vs-CPU claim.
- It is not proof that Numba always beats CuPy.
- It is not proof that RT cores accelerate the force accumulation itself.

## Route Guidance Update

The current Barnes-Hut route registry is updated to:

- prefer the prepared Numba continuation for the Goal4436/Goal4438
  aggregate-frontier device-column weighted-vector route
- keep CuPy as the required same-contract comparison partner
- preserve older CuPy-favored exact-force rows only under their older contract
- keep public speedup, RT-core speedup, and whole-app speedup flags false

Next runtime action: integrate this prepared aggregate-frontier Numba route into
the benchmark app as an explicit mode, then build same-contract Embree/CPU
evidence before any public backend-comparison wording.
