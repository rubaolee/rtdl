# Goal4448 / V3.0 M52 - Barnes-Hut Numba CUDA Fused Subtree Prototype

## Result

M52 adds a no-C++, Python-source Numba CUDA fused-subtree prototype:

```text
scripts/v3_0_m52_barnes_hut_numba_cuda_fused_subtree.py
```

It traverses the bucketized aggregate tree directly on the GPU and accumulates
force vectors in one fused CUDA kernel. It does not emit aggregate-frontier rows
and does not materialize contribution rows. This is partner/prototype evidence,
not an RT-core primitive.

The important result is clear:

- M52 beats the current prepared RTDL/OptiX+Numba aggregate-frontier route by
  `3.38x` to `7.82x` on the 8192/16384/32768-body scale ladder.
- M52 is still slower than the M45 fused CPU/Numba route at 8192 and 16384
  bodies, but faster at 32768 bodies.
- Therefore, the Barnes-Hut bottleneck is not Numba itself. The bottleneck was
  the unfused frontier-emission contract. A fused device route is the right V3
  direction.

## Same-Contract Scale Matrix

All rows use bucket size `64`, max depth `32`, theta `0.5`, softening `0.05`,
11 measured repeats after 2 warmups, and CUDA event medians for the M52 hot
kernel.

| Bodies | Contribution rows | M52 Numba CUDA fused hot | M45 CPU/Numba fused hot | M52 / M45 | M41 prepared OptiX+Numba hot | M41 / M52 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 8192 | 3,406,489 | 0.003207 s | 0.001304 s | 2.46x slower | 0.014712 s | 4.59x faster |
| 16384 | 12,727,680 | 0.008945 s | 0.004122 s | 2.17x slower | 0.030269 s | 3.38x faster |
| 32768 | 15,514,679 | 0.010552 s | 0.015161 s | 1.44x faster | 0.082540 s | 7.82x faster |

The 8192 row also has an M42 app-mode OptiX+Numba baseline: M42 hot median was
`0.016139 s`, so M52 is `5.03x` faster than that same app-mode prepared route.

## Correctness

The 128-body smoke uses the same M45 smoke settings: bucket size `16`, max depth
`32`, theta `0.5`, and softening `0.05`.

| Bodies | Contribution rows | Max abs diff x | Max abs diff y | Result |
| ---: | ---: | ---: | ---: | --- |
| 128 | 8,766 | 1.42e-14 | 1.60e-14 | pass |

M52 also records an 8192-body full CPU-reference validation:

| Bodies | Contribution rows | Max abs diff x | Max abs diff y | Result |
| ---: | ---: | ---: | ---: | --- |
| 8192 | 3,406,489 | 3.64e-12 | 4.09e-12 | pass |

The 8192 checksum matches the M42/M45 contract:

| Route | checksum force x | checksum force y |
| --- | ---: | ---: |
| M42 RTDL/OptiX + Numba app mode | -1836.5717739965667 | 4948.320604887265 |
| M45 fused CPU/Numba | -1836.571773996123 | 4948.320604887711 |
| M52 fused Numba CUDA | -1836.5717739960237 | 4948.32060488686 |

## Interpretation

M42 proved RTDL/OptiX could produce aggregate-frontier device columns and pass
them to a Numba/CuPy continuation. M45 proved that if the traversal and force
sum are fused, CPU/Numba can beat that prepared RT route at the tested scales.

M52 answers the next question: can a no-C++ Python-source GPU partner also fuse
the traversal and force accumulation? Yes. It removes the frontier row contract
from the hot path and beats the prepared RTDL/OptiX+Numba route decisively.

This does not mean RT cores accelerate Barnes-Hut today. It means the current
RTDL/OptiX aggregate-frontier primitive is the wrong final contract for this
app if the goal is peak performance. The right V3 shape is a fused hierarchical
vector primitive or a same-stream device continuation that preserves the RTDL
app-agnostic boundary while avoiding frontier materialization.

## Boundary

What M52 can say:

- RTDL now has a no-C++, Python-source CUDA fused-subtree Barnes-Hut prototype.
- The prototype avoids frontier and contribution row materialization.
- For this contract it is faster than the current prepared RTDL/OptiX+Numba
  aggregate-frontier route on the measured scale ladder.
- At 32768 bodies it is also faster than the current fused CPU/Numba route.

What M52 cannot say:

- It is not an RT-core primitive.
- It is not an OptiX-vs-Embree comparison.
- It is not a public GPU-vs-CPU speedup claim.
- It does not authorize automatic partner selection.
- It does not prove full Barnes-Hut paper reproduction or broad N-body
  acceleration.

## Raw Evidence

- `docs/reports/goal4448_v3_0_m52_barnes_hut_numba_cuda_fused_subtree_128_smoke_2026-06-16.json`
- `docs/reports/goal4448_v3_0_m52_barnes_hut_numba_cuda_fused_subtree_8192_validation_2026-06-16.json`
- `docs/reports/goal4448_v3_0_m52_barnes_hut_numba_cuda_fused_subtree_scale_r11_2026-06-16.json`
- `docs/reports/goal4442_v3_0_m45_barnes_hut_fused_numba_cpu_frontier_2026-06-16.md`
- `docs/reports/goal4439_v3_0_m42_barnes_hut_prepared_frontier_app_mode_2026-06-16.md`
- `docs/reports/goal4438_v3_0_m41_barnes_hut_prepared_frontier_partner_scale_ladder_2026-06-16.md`

## Next

Barnes-Hut is no longer blocked on obvious Python/host-row cleanup. The remaining
V3 work is architectural:

- promote the fused traversal-plus-vector-sum shape into an app-agnostic RTDL
  primitive contract;
- investigate whether OptiX/RT-native traversal can own that fused contract
  without exposing app-specific callbacks in the native engine;
- keep the Numba CUDA route as the no-C++ partner/reference lane for users who
  need fused custom logic today.
