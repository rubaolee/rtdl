# Particle `110dee7aa` descriptive peak-memory diagnostic

Date: 2026-09-09

## Scope

This is a post-formal diagnostic at exact measured source
`110dee7aa11e57e984cc2509163e021d787c692a`, not a formal latency or memory
endpoint. It uses the same 160,000,000-query natural transition-stage workload
and complete U32x3 output contract as the formal transaction. No sample from
this diagnostic is pooled with formal performance evidence.

The schedule is balanced `RTDL, PyOptiX, PyOptiX, RTDL`, with one fresh worker
per position. The monitor requested 10 ms sampling of direct-worker RSS and
whole-device NVIDIA memory use. All four workers returned exact output digest
`6c4ec71524be3d7b241c3d66c4cd06a5aa7089b3948bf1d8dd8aab550f0dec89`.

## Result

The identical pre-worker whole-device baseline was 345,571,328 bytes
(0.322 GiB).

| Position | Arm | Samples | Whole-device peak GiB | Baseline-subtracted GiB | Direct-worker RSS GiB |
| ---: | --- | ---: | ---: | ---: | ---: |
| 0 | RTDL | 2,094 | 9.153 | 8.831 | 14.536 |
| 1 | PyOptiX | 2,087 | 6.831 | 6.509 | 18.604 |
| 2 | PyOptiX | 2,206 | 6.831 | 6.509 | 18.603 |
| 3 | RTDL | 2,084 | 9.153 | 8.831 | 14.537 |

Across the two repeats, RTDL's sampled whole-device peak is 2.322 GiB higher
(`1.339972x` total-device ratio), while its median direct-worker RSS is 4.066
GiB lower (`0.781415x` ratio). The mechanism therefore trades host memory for
temporary device staging rather than reducing all memory dimensions.

## Interpretation and limits

The packed path owns one immutable host snapshot instead of separately
materializing seven immutable host columns. Native preparation performs one
packed H2D transfer and then transposes into seven device-resident columns.
Until packed staging is released, both device layouts coexist; the higher GPU
peak is consistent with that implementation.

NVML per-process memory accounting was unavailable, so the GPU metric is the
whole device rather than an allocation-attributed worker value. The one-GPU
schedule and identical idle baseline reduce ambiguity but do not remove it.
Ten-millisecond sampling may miss shorter peaks. Direct-worker RSS excludes
compiler child processes. Monitoring perturbs execution, so recorded worker
latencies are not performance evidence.

Formal peak memory remains unmeasured. This diagnostic authorizes neither a
general memory advantage nor a formal memory regression claim. It records an
implementation trade-off that must accompany any discussion of the packed
device-transpose setup improvement.

## Custody

- Raw result: `PEAK_MEMORY_DIAGNOSTIC.json`, 21,750 bytes, SHA-256
  `0c3ee2df8d9411f3a6ef4e6e344cc802abe4b97bbba3d94b5e8eba20099ce49e`.
- Exact tool is retained as `PEAK_MEMORY_DIAGNOSTIC_TOOL.py` and on the RunPod
  network volume as `tools/particle_peak_memory_diagnostic_110dee7aa.py`, SHA-256
  `192b12ce24db902c0f164670ca0addc93f825e281955df6e49872f3c13f8f446`.
- The durable handoff verifier passed all 47 registered payload files after
  adding the tool and raw result.
