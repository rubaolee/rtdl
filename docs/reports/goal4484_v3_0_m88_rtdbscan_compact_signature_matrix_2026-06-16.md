# Goal4484 / V3.0 M88 RT-DBSCAN Compact-Signature Route Matrix

## Outcome

M88 refreshes the RT-DBSCAN compact-signature route decision with a full-contract
matrix on the RTX 4000 Ada pod.

Two things changed:

1. The predicate direct-status app path now records the OptiX count-threshold
   prepare cost separately as `prepared_optix_count_threshold_sec` and includes
   it in `prepare_plus_replay_median_sec`. The old fields could understate the
   one-shot boundary by timing direct-status prepare and replay while leaving the
   count-threshold prepare phase implicit.
2. The 524,288-point matrix compares the same compact DBSCAN signature contract
   across grouped-stream Numba, grouped-stream CuPy, and predicate direct-status
   CuPy on `clustered3d`, `road3d`, and `ngsim_dense`.

The measured route result is clear: for the tested 524k compact-signature
profiles, explicit predicate direct-status is the better RTDL route than grouped
stream, especially for resident/repeated replay. It remains an explicit route
choice, not a hidden default and not public RT-core speedup wording.

## Evidence

Raw packet:
`docs/reports/goal4484_v3_0_m88_rtdbscan_compact_signature_matrix_2026-06-16.json`

Line packet:
`docs/reports/goal4484_v3_0_m88_rtdbscan_compact_signature_matrix_2026-06-16.jsonl`

Hardware: NVIDIA RTX 4000 Ada Generation, driver 550.127.08.

CUDA/Numba environment used the project CUDA 12.4 NVVM/ptxas path:
`NUMBA_CUDA_PREFIX=/usr/local/lib/python3.12/dist-packages/nvidia/cuda_nvcc`.

The packet contains 29 successful rows and zero errors.

## Correctness Gates

Small CPU-oracle validation:

| Dataset | Grouped Numba | Grouped CuPy | Predicate Direct-Status |
| --- | ---: | ---: | ---: |
| `clustered3d`, 4,096 points | pass | pass | pass |
| `road3d`, 4,096 points | pass | pass | pass |
| `ngsim_dense`, 4,096 points | pass | pass | pass |

Large same-contract signature gate:

| Dataset | Points | Protocols | Result |
| --- | ---: | --- | --- |
| `clustered3d` | 524,288 | one-shot, warmed replay | grouped Numba, grouped CuPy, and predicate direct-status signatures match |
| `road3d` | 524,288 | one-shot, warmed replay | grouped Numba, grouped CuPy, and predicate direct-status signatures match |
| `ngsim_dense` | 524,288 | one-shot, warmed replay | grouped Numba, grouped CuPy, and predicate direct-status signatures match |

This is the right large-scale gate for this target: the full CPU oracle is useful
at small scale, while the 524k rows check that all same-contract RTDL routes
produce the same cluster/core/noise signature.

## Performance Matrix

One-shot table uses `prepare + measured replay` seconds. Predicate direct-status
includes both direct-status prepare and OptiX count-threshold prepare after the
M88 instrumentation fix.

| Dataset | Grouped Numba | Grouped CuPy | Predicate Direct-Status | Best | Speedup vs Grouped Numba |
| --- | ---: | ---: | ---: | --- | ---: |
| `clustered3d` | 7.616s | 8.010s | 4.321s | predicate direct-status | 1.76x |
| `road3d` | 4.442s | 4.727s | 3.882s | predicate direct-status | 1.14x |
| `ngsim_dense` | 3.137s | 3.399s | 3.119s | predicate direct-status | 1.006x |

Warmed replay table uses measured replay seconds after one warmup. This is the
resident prepared-route boundary.

| Dataset | Grouped Numba | Grouped CuPy | Predicate Direct-Status | Best | Speedup vs Grouped Numba |
| --- | ---: | ---: | ---: | --- | ---: |
| `clustered3d` | 5.055s | 5.347s | 1.553s | predicate direct-status | 3.26x |
| `road3d` | 1.847s | 2.111s | 1.326s | predicate direct-status | 1.39x |
| `ngsim_dense` | 0.598s | 0.867s | 0.337s | predicate direct-status | 1.78x |

## Interpretation

Predicate direct-status is now the measured explicit RT-DBSCAN compact-signature
route for the tested 524k profiles. It uses generic RTDL pieces:

- OptiX fixed-radius count-threshold device columns for core flags.
- CuPy predicate direct-status union for the compact component signature.
- No DBSCAN-specific native ABI.
- No hidden route, partner, factor, or border-policy selection.

The speedup mechanism matches the timings. Grouped-stream routes replay the
component work through the grouped union stream and then aggregate the signature.
Predicate direct-status consumes a more compact predicate/status representation
and avoids the heavier grouped-stream replay shape. The effect is largest on
clustered3d repeated replay, still useful on road3d, and almost neutral for
ngsim_dense one-shot because prepare cost dominates there.

## Boundary

The graph-only direct-status probe is not a DBSCAN route. It is faster on some
rows but carries `graph_component_contract_only=True` and
`dbscan_core_border_noise_semantics=False`; it must not be reported as a full
RT-DBSCAN compact signature path.

M88 authorizes internal route guidance only:

- Use predicate direct-status explicitly for the measured 524k compact
  cluster-size/noise/core signature profiles.
- Keep grouped-stream Numba as the conservative reference/fallback path.
- Keep full Python rows explicit.
- Keep automatic output-mode, partner, route, factor, and border-policy
  selection blocked.
- Do not turn this into a paper-reproduction, whole-app speedup, broad RT-core,
  or GPU-vs-CPU/Embree claim.
