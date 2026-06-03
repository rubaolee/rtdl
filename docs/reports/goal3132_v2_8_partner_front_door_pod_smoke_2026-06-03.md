# Goal3132: v2.8 Partner Front Door Pod Smoke

Date: 2026-06-03

Status: pod functional smoke passed; larger Numba timing is negative

## Purpose

Goals3120-3131 established local functional coverage for the v2.8 explicit
partner-consumer front door. The only local gap was Numba-specific grouped
argmin/argmax validation because the local GTX 1070 Numba stack destroyed its
CUDA context even for a trivial kernel.

Goal3132 uses a pod with RTX 4000 Ada hardware to validate the same front-door
surface on a healthy partner stack.

## Pod

SSH command supplied by the user:

```text
ssh root@157.157.221.29 -p 24317 -i ~/.ssh/id_ed25519
```

The default `~/.ssh/id_ed25519` was rejected by the pod. The working key for
this run was the RTDL Codex key:

```text
C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review\id_ed25519_rtdl_codex
```

Environment:

- host: `4463b4adb79b`
- GPU: `NVIDIA RTX 4000 Ada Generation`
- driver: `580.65.06`
- compute capability: `8.9`
- Python: `3.12.3`
- repo path: `/root/rtdl_v28_goal3132`
- commit: `2809a45b`
- venv: `/root/rtdl_v28_env`
- Numba: `0.65.1`
- CuPy: `14.1.1`
- Torch: `2.12.0+cu130`

Artifact:

`docs/reports/goal3132_pod_artifacts/v2_8_partner_front_door_pod_smoke_2026-06-03.json`

## Validation

Focused unit gate:

```text
Ran 27 tests in 0.006s
OK
```

Numba sanity:

```text
[pod3132] numba sanity passed [1, 2, 3, 4, 5, 6, 7, 8]
```

Small functional front-door cases:

| Operation | Partner | Status |
| --- | --- | --- |
| `segmented_count_i64` | CuPy | passed |
| `segmented_sum_f64` | CuPy | passed |
| `grouped_vector_sum_f64x2` | CuPy | passed |
| `grouped_argmin_f64` | Numba | passed |
| `grouped_argmax_f64` | Numba | passed |
| `grouped_topk_f64` | Torch | passed |
| `bounded_collect_finalize_i64` | Torch | passed |

Every small case matched the Goal3114 Python reference consumer. Every recorded
claim flag stayed false:

- `release_authorized: false`
- `true_zero_copy_claim_authorized: false`
- `public_speedup_claim_authorized: false`

## Larger Numba Timing Probe

The larger probe used:

- `row_count = 65536`
- `group_count = 1024`
- partner: `numba`
- operations: `grouped_argmin_f64`, `grouped_argmax_f64`
- warm-up separated from three steady-state repetitions

Observed timings:

| Operation | Warm Seconds | Steady Seconds | Python Reference Seconds |
| --- | ---: | --- | ---: |
| `grouped_argmin_f64` | 0.213202 | 0.312432, 0.216399, 0.216772 | 0.056126 |
| `grouped_argmax_f64` | 0.208432 | 0.210361, 0.211569, 0.212234 | 0.055611 |

This is negative performance evidence for the current v2.8 Numba grouped-arg
front-door path at this size. The Numba kernels emitted under-occupancy
warnings during the probe, and the end-to-end path still includes generic
front-door orchestration rather than a tuned device-resident primitive.

## Interpretation

Goal3132 closes the correctness gap for the current v2.8 front-door surface on
pod hardware:

- Numba grouped argmin/argmax works on a healthy RTX 4000 Ada stack.
- CuPy count/sum/vector-sum works.
- Torch top-k and bounded collect works.
- Claim flags remain blocked.

Goal3132 does **not** close performance readiness. The larger Numba timing is
slower than the Python reference for this probe. The next engineering task
should therefore treat v2.8 grouped-arg performance as an active problem, not a
claim.

## Claim Boundary

Goal3132 does not authorize:

- a v2.8 release,
- public speedup wording,
- broad RT-core wording,
- true-zero-copy wording,
- hidden dispatch,
- automatic partner selection,
- app-specific native-engine behavior,
- user-defined shader injection,
- benchmark-app performance claims.

## Next Engineering Target

The next target is a v2.8 grouped-arg performance hardening pass:

1. inspect the Numba grouped-arg path for under-occupied launches and host-side
   compacting overhead;
2. separate kernel-time, compaction-time, and front-door orchestration time;
3. test larger row/group regimes where the current block layout is not
   under-occupied;
4. decide whether grouped argmin/argmax should remain a partner continuation or
   become a stronger generic native primitive in the v2.x line;
5. keep all speedup and release claims blocked until the optimized path wins
   under reviewed same-contract evidence.
