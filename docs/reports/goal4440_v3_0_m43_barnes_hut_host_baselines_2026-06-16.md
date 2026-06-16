# Goal4440 / V3.0 M43 - Barnes-Hut Host Baselines For The Prepared App Route

## Result

M43 adds two explicit Barnes-Hut benchmark app modes:

```text
aggregate_frontier_weighted_vector_cpu_host
aggregate_frontier_weighted_vector_embree_host
```

They share the same logical aggregate-frontier weighted-vector output contract
as the M42 prepared OptiX app route, but they intentionally materialize
frontier rows on the host. Therefore they are diagnostic host baselines, not a
same device-resident backend comparison and not public RT-core speedup wording.
In short: these are host-materialized logical baselines.
They are not a same device-resident backend comparison.

## Why This Matters

M42 proved the usable app route:

```text
prepared_aggregate_frontier_weighted_vector_optix
```

That route keeps frontier columns resident on device and hands them to an
explicit `numba` or `cupy` partner. M43 answers the next question: what happens
if the CPU/Embree side uses the same logical frontier/vector semantics but pays
host row materialization?

The answer is clear: at 8192 bodies, all routes produce the same frontier row
count and matching force checksums, but the host baselines spend seconds in
frontier collection and host accumulation while the prepared OptiX route spends
milliseconds in the hot native+partner window.

## 8192-Body Matrix

Configuration:

- RTX 4000 Ada pod
- 8192 bodies
- bucket size 64
- theta 0.5
- app softening 0.05
- validation skipped for the 8192-body timing rows
- force rows suppressed with `--force-output-mode force_summary`

| Route | Frontier rows | Aggregate rows | Exact rows | Frontier phase | Vector/partner phase | Hot or total window | Contract note |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| RTDL/OptiX + Numba | 3,406,489 | 477,919 | 2,928,570 | 0.014865 s | 0.001296 s | 0.016139 s hot | device-resident prepared frontier columns |
| RTDL/OptiX + CuPy | 3,406,489 | 477,919 | 2,928,570 | 0.014948 s | 0.008339 s | 0.023295 s hot | device-resident prepared frontier columns |
| CPU host baseline | 3,406,489 | 477,919 | 2,928,570 | 6.938711 s | 3.146279 s | 10.231974 s total | host-materialized frontier rows |
| Embree host baseline | 3,406,489 | 477,919 | 2,928,570 | 8.064940 s | 3.269292 s | 11.480454 s total | host-materialized frontier rows |

Checksum agreement:

| Route | checksum force x | checksum force y |
| --- | ---: | ---: |
| RTDL/OptiX + Numba | -1836.5717739965667 | 4948.320604887265 |
| RTDL/OptiX + CuPy | -1836.571773996528 | 4948.320604887442 |
| CPU host baseline | -1836.5717739961324 | 4948.320604887712 |
| Embree host baseline | -1836.5717739961324 | 4948.320604887712 |

## Diagnostic Ratios

These are diagnostic ratios only. They are useful for engineering triage, but
they are not public speedup claims because the timing windows and residency
contracts differ.

| Comparison | Ratio | Interpretation |
| --- | ---: | --- |
| CPU host frontier phase / OptiX frontier median | 466.8x | Host row collection dominates the CPU logical baseline. |
| Embree host frontier phase / OptiX frontier median | 542.5x | The current Embree baseline pays native collect plus host row materialization. |
| CPU host vector phase / Numba partner median | 2428.0x | Python host accumulation is not a serious opponent for device-side fused accumulation. |
| Embree host vector phase / Numba partner median | 2522.9x | Same continuation bottleneck after Embree frontier collection. |
| CPU host total / OptiX+Numba hot | 634.0x | Diagnostic only; total host path versus hot device-resident path. |
| Embree host total / OptiX+Numba hot | 711.3x | Diagnostic only; total host path versus hot device-resident path. |

## 128-Body Correctness Smokes

Both host modes were also run at 128 bodies with CPU reference validation
enabled.

| Route | Frontier rows | max abs diff x | max abs diff y | Result |
| --- | ---: | ---: | ---: | --- |
| CPU host baseline | 8,766 | 1.78e-15 | 0.0 | pass |
| Embree host baseline | 8,766 | 1.78e-15 | 0.0 | pass |

## Boundary

What M43 can say:

- The CPU and Embree host baselines now run from the Barnes-Hut benchmark app.
- They match the logical frontier/vector semantics of the prepared OptiX app
  route at the tested scales.
- They expose the cost of host frontier materialization and host Python vector
  accumulation.
- The current Embree host baseline is slower than the current CPU host baseline
  on the 8192-body timing row, so it is not an optimized CPU RT opponent.

What M43 cannot say:

- It is not a same device-resident OptiX-vs-Embree comparison.
- It is not a public RT-core or GPU-vs-CPU speedup claim.
- It is not proof of whole Barnes-Hut N-body acceleration.
- It does not make automatic partner selection safe.

## Raw Evidence

- `docs/reports/goal4440_v3_0_m43_barnes_hut_cpu_host_128_smoke_2026-06-16.json`
- `docs/reports/goal4440_v3_0_m43_barnes_hut_embree_host_128_smoke_2026-06-16.json`
- `docs/reports/goal4440_v3_0_m43_barnes_hut_cpu_host_8192_2026-06-16.json`
- `docs/reports/goal4440_v3_0_m43_barnes_hut_embree_host_8192_2026-06-16.json`
- `docs/reports/goal4439_v3_0_m42_barnes_hut_app_mode_numba_8192_2026-06-16.json`
- `docs/reports/goal4439_v3_0_m42_barnes_hut_app_mode_cupy_8192_2026-06-16.json`

## Next

The next clean V3 target is not more host-row timing. It is a fused or
device/engine-resident CPU-side baseline, or an explicitly documented decision
that Barnes-Hut backend comparison remains diagnostic until such a baseline
exists. The user-facing route should keep Numba as the best measured partner
for the prepared OptiX route and keep CPU/Embree host baselines as correctness
and bottleneck evidence.
