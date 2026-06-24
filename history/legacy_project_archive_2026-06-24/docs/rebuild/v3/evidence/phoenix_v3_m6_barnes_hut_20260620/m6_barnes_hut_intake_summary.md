# Phoenix V3 M6 Barnes-Hut Intake

Status: internal_m6_route_parity_evidence

M6 Barnes-Hut confirms the current fastest route is fused CPU/Numba or fused Numba CUDA, while prepared OptiX remains bounded device-column evidence.

```text
release_authorized: false
public_speedup_claim_authorized: false
rt_core_speedup_claim_authorized: false
Phoenix M7-qualified release rows: 0
```

## Route Matrix

| Bodies | Fastest route | Fastest | OptiX+Numba | OptiX+Numba / fastest | Contribution rows | Checksum parity |
|---:|---|---:|---:|---:|---:|---|
| 32,768 | `numba_cuda_fused` | 11.249 ms | 82.435 ms | 7.328x | 15,514,679 | pass |
| 65,536 | `numba_cuda_fused` | 34.738 ms | 177.858 ms | 5.120x | 55,935,606 | pass |
| 131,072 | `numba_cuda_fused` | 44.445 ms | 618.302 ms | 13.912x | 68,023,506 | pass |

Ratios in this table use mixed timing bases: fused Numba CUDA uses CUDA-event
kernel time when available, while CPU/Numba and prepared OptiX routes use
the runner's wall-clock hot median. These ratios are internal route guidance,
not kernel-to-kernel comparisons.

## Methodology

- Repeat: 11
- Warmup: 3
- Theta: 0.5
- Bucket size: 64
- Timing note: Fused Numba CUDA uses CUDA-event kernel timing when available; CPU/Numba and prepared OptiX routes use the runner's hot median. The route ratios therefore compare CUDA-event kernel time against wall-clock hot median; they are not kernel-to-kernel comparisons. Large rows are route-parity evidence, not full exact-force oracle rows.

## Failures

- none
