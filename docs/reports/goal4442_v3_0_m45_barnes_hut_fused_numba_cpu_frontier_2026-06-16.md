# Goal4442 / V3.0 M45 - Barnes-Hut Fused Numba CPU Frontier Baseline

## Result

M45 adds a fused no-C++ CPU route:

```text
fused_frontier_force_sum_bucketized_cpu_numba
```

This route does not collect frontier rows and does not materialize contribution
rows. It converts the bucketized aggregate tree to compact arrays, then uses a
Numba CPU `njit` partner to traverse the tree and accumulate force vectors
directly, parallelized by source.

This is the current fastest measured Barnes-Hut route in the source tree for
the tested 8192/16384/32768-body contract. It is faster than the current
RTDL/OptiX prepared aggregate-frontier device-column route at these scales.
It is faster than the current RTDL/OptiX prepared aggregate-frontier device-column route.

## 8192-Body Exact App-Mode Comparison

The 8192-body M45 route matches the M42 app-mode frontier/contribution count
and checksum, so this is the cleanest comparison row.

| Route | Frontier/contribution rows | Frontier rows materialized | Contribution rows materialized | Hot median |
| --- | ---: | --- | --- | ---: |
| RTDL/OptiX + Numba GPU vector, M42 app mode | 3,406,489 | no | no | 0.016139 s |
| CPU host + Numba CPU vector, M44 | 3,406,489 | yes | no | 6.916229 s |
| Fused CPU/Numba, M45 | 3,406,489 | no | no | 0.001304 s |

Diagnostic ratios:

| Comparison | Ratio | Meaning |
| --- | ---: | --- |
| M44 CPU host+Numba hot / M45 fused CPU+Numba hot | 5304.6x | Host frontier materialization was the dominant CPU-side debt. |
| M42 RTDL/OptiX+Numba hot / M45 fused CPU+Numba hot | 12.4x | Current fused CPU/Numba is faster for this Barnes-Hut contract. |

Checksums:

| Route | checksum force x | checksum force y |
| --- | ---: | ---: |
| RTDL/OptiX + Numba GPU vector, M42 | -1836.5717739965667 | 4948.320604887265 |
| Fused CPU/Numba, M45 | -1836.571773996123 | 4948.320604887711 |

## Scale Ladder

The 16384 and 32768 rows are scale-level comparisons against the M41 prepared
OptiX+Numba ladder. They use the same body count, bucket size, theta, and
logical contract family, but the row counts are not byte-identical to M45, so
read these as scale evidence rather than exact app-mode equality.

| Bodies | M45 fused CPU/Numba hot | M41 prepared OptiX+Numba hot | M41 / M45 diagnostic ratio |
| ---: | ---: | ---: | ---: |
| 8192 | 0.001304 s | 0.014712 s | 11.3x |
| 16384 | 0.004122 s | 0.030269 s | 7.3x |
| 32768 | 0.015161 s | 0.082540 s | 5.4x |

M45 repeat timing has visible OS scheduling outliers, especially at 32768
bodies. The report uses the median of 11 measured repeats after 2 warmups.
The raw repeat lists are preserved in the JSON evidence.

## Correctness

The 128-body correctness smoke compares directly against the CPU reference:

| Bodies | contribution rows | max abs diff x | max abs diff y | Result |
| ---: | ---: | ---: | ---: | --- |
| 128 | 8,766 | 0.0 | 0.0 | pass |

The 8192/16384/32768 timing rows skip full validation but preserve contribution
counts, checksums, repeat timings, and closed claim flags.

## Interpretation

M43 showed the host-materialized CPU/Embree baselines were dominated by frontier
row collection. M44 removed the Python force-vector accumulation debt with a
Numba CPU continuation, but the host frontier collection still dominated.

M45 removes that frontier-row materialization from the CPU route. The result is
the important lesson for V3:

- For this Barnes-Hut contract, the best current CPU/Numba fused partner route
  is faster than the current RTDL/OptiX device-column route.
- The current RTDL/OptiX route is still valuable evidence that RTDL can expose
  generic aggregate-frontier device columns and feed Numba/CuPy partners.
- It is not evidence that RT cores accelerate Barnes-Hut versus optimized CPU
  partner code.
- To make RT cores competitive here, V3 needs a deeper fused native/device
  route, not more host-row optimization.

## Boundary

What M45 can say:

- RTDL now has a serious no-C++ CPU/Numba fused Barnes-Hut baseline.
- The baseline avoids frontier and contribution row materialization.
- For the tested scales, this baseline is faster than the current
  RTDL/OptiX+Numba prepared device-column route.

What M45 cannot say:

- It is not an Embree implementation.
- It is not a GPU-vs-CPU public speedup claim.
- It is not a whole Barnes-Hut paper reproduction.
- It does not authorize automatic route or partner selection.

## Raw Evidence

- `docs/reports/goal4442_v3_0_m45_barnes_hut_fused_numba_cpu_128_smoke_2026-06-16.json`
- `docs/reports/goal4442_v3_0_m45_barnes_hut_fused_numba_cpu_8192_r11_2026-06-16.json`
- `docs/reports/goal4442_v3_0_m45_barnes_hut_fused_numba_cpu_16384_r11_2026-06-16.json`
- `docs/reports/goal4442_v3_0_m45_barnes_hut_fused_numba_cpu_32768_r11_2026-06-16.json`
- `docs/reports/goal4439_v3_0_m42_barnes_hut_app_mode_numba_8192_2026-06-16.json`
- `docs/reports/goal4438_v3_0_m41_barnes_hut_prepared_frontier_partner_scale_ladder_2026-06-16.json`
- `docs/reports/goal4441_v3_0_m44_barnes_hut_cpu_host_numba_8192_2026-06-16.json`

## Next

Update Barnes-Hut route guidance to mixed explicit choice:

- choose `fused_frontier_force_sum_bucketized_cpu_numba` for the current fastest
  measured no-C++ app route;
- choose `prepared_aggregate_frontier_weighted_vector_optix --partner numba`
  when the purpose is RTDL/OptiX device-column execution evidence;
- do not claim Barnes-Hut RT-core acceleration until a fused RT-native/device
  route beats the fused CPU/Numba baseline under the same contract.
