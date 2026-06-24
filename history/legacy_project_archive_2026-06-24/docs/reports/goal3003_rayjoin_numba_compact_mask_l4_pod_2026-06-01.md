# Goal3003: RayJoin Numba Compact Mask L4 Pod Evidence

## Result

Goal3003 passed on an NVIDIA L4 pod for all three RayJoin-style workloads:

| Workload | Selected Rows | CPU Candidate Parity | CPU Index Parity | Neutral Handoff |
| --- | ---: | --- | --- | --- |
| `pip` | `122,257` | true | true | accept |
| `lsi` | `106,700` | true | true | accept |
| `overlay_seed` | `106,596` | true | true | accept |

Run metadata:

- source commit: `6e02f4c743bcd7e863f850bc79260fe515076329`
- source dirty status: empty
- GPU: `NVIDIA L4, 565.57.01`
- rows per workload: `1,000,000`
- operation: `compact_mask_i64`
- app mode: `v2_6_numba_compact_mask_preview`
- all workloads match CPU oracle: true

Artifact:

`docs/reports/goal3003_rayjoin_numba_compact_mask_l4_pod_2026-06-01.json`

## Boundary

Goal3003 proves app-level v2.6 Numba compact-mask wiring for RayJoin-style row streams. It does not prove RayJoin paper reproduction, RayJoin-scale performance, a Numba speedup, a whole-app speedup, an RT-core speedup, true zero-copy, or v2.6 release readiness.

Prepared generic RTDL count/parity primitives remain the recommended fast path when scalar counts are enough.
