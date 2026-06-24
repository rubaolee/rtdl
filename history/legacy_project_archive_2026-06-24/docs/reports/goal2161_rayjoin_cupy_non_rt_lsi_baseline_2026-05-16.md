# Goal2161 RayJoin CuPy Non-RT LSI Baseline

Date: 2026-05-16

Status: runner implemented; pod evidence collected; external review pending.

## Purpose

Goal2161 adds a CUDA-core, non-RT baseline to the public RayJoin CDB runner. The purpose is to prevent us from comparing RTDL/OptiX only against CPU and Embree when a v2.0 user could also write ordinary partner code with CuPy.

The new backend is named `cupy_lsi_bruteforce`. It is deliberately scoped to line-segment intersection (LSI) and deliberately marked as not RT-core accelerated.

## What Changed

`scripts/goal2159_rayjoin_public_cdb_runner.py` now accepts `cupy_lsi_bruteforce` as a backend.

That backend:

- loads the same bounded CDB segment slices as the RTDL runner
- launches a CuPy `RawKernel` over every left/right segment pair
- computes the same non-colinear segment-intersection predicate as the RTDL reference contract
- returns the same row schema: `left_id`, `right_id`, `intersection_point_x`, `intersection_point_y`
- checks parity against the CPU Python reference
- records `rt_core_accelerated: false`, `partner_accelerated: true`, and `baseline_kind: cupy_rawkernel_cuda_core_bruteforce_lsi`

This is app/user partner code, not a native RTDL engine extension.

## Pod Evidence

Pod access:

- `root@157.157.221.29`
- SSH port: `24240`
- Accepted local key: `id_ed25519_rtdl_codex`

Runtime facts:

- GPU: NVIDIA RTX 4000 Ada Generation
- Driver: 580.65.06
- CUDA: 12.8
- OptiX SDK: v8.1.0
- RTDL runner commit: `28f5c69cf4e84da93c3c01f03c00566a3a516909`
- CuPy package installed on pod: `cupy-cuda12x 14.0.1`

Collected artifacts:

- `docs/reports/goal2161_rayjoin_public_cdb_cupy_baseline_count192_pod_2026-05-16.json`
- `docs/reports/goal2161_rayjoin_public_cdb_cupy_baseline_count128_192_pod_2026-05-16.json`

## Single-Case Count192 Result

Command shape:

```bash
python3 scripts/goal2159_rayjoin_public_cdb_runner.py \
  --data-dir /root/rtdl_rayjoin_pod/data/rayjoin \
  --output docs/reports/goal2161_rayjoin_public_cdb_cupy_baseline_count192_pod_2026-05-16.json \
  --cases lsi_county256_soil256_count192 \
  --backends cpu,embree,optix,cupy_lsi_bruteforce \
  --warmups 1 --repeats 5 --step-timeout 360
```

| Case | Rows | CPU sec | Embree sec | OptiX sec | CuPy sec | Fastest | Parity |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `lsi_county256_soil256_count192` | 85 | 0.016256 | 0.030044 | 0.015249 | 0.010819 | CuPy | all pass |

Ratios:

- OptiX vs CPU: `1.07x`
- OptiX vs Embree: `1.97x`
- CuPy vs CPU: `1.50x`
- CuPy vs OptiX: `1.41x`

## Two-Case Warmed Session Result

Command shape:

```bash
python3 scripts/goal2159_rayjoin_public_cdb_runner.py \
  --data-dir /root/rtdl_rayjoin_pod/data/rayjoin \
  --output docs/reports/goal2161_rayjoin_public_cdb_cupy_baseline_count128_192_pod_2026-05-16.json \
  --cases lsi_county256_soil256_count128,lsi_county256_soil256_count192 \
  --backends optix,cupy_lsi_bruteforce \
  --warmups 1 --repeats 5 --step-timeout 360
```

| Case | Rows | OptiX sec | CuPy sec | Fastest | Parity |
| --- | ---: | ---: | ---: | --- | --- |
| `lsi_county256_soil256_count128` | 56 | 0.010405 | 0.006232 | CuPy | all pass |
| `lsi_county256_soil256_count192` | 85 | 0.015294 | 0.010799 | CuPy | all pass |

The prior Goal2159 multi-case artifact showed a much faster OptiX warm-state result for `count192`. This rerun did not reproduce that median, even though all parity checks passed. The safest interpretation is that the very fast OptiX state is not yet stable enough for a public performance claim.

## Interpretation

This is a useful loss.

On these bounded public CDB LSI slices, a simple CuPy CUDA-core all-pairs kernel beats the current RTDL/OptiX median. That does not invalidate the RT path; it clarifies the design problem:

- the current slices have low hit counts and modest candidate-pair counts
- OptiX pays traversal/module/session overhead that is not yet amortized
- the current runner rebuilds and reruns at app-call granularity instead of holding a persistent batched RT session
- the CuPy baseline does a flat parallel all-pairs test that fits comfortably on the GPU for these slice sizes

Therefore, RayJoin LSI cannot yet be used as a strong RT-core speedup claim. It can be used as a correctness and integration example, and as a benchmark pressure test for future persistent-session RTDL design.

## Claim Boundary

This goal authorizes:

- a same-runner CUDA-core CuPy baseline for bounded RayJoin public-CDB LSI slices
- a narrow statement that CuPy is the fastest measured backend for these two bounded LSI protocols
- a design conclusion that RTDL/OptiX needs better persistent-session or batched-query amortization before claiming RayJoin LSI speedups

This goal does not authorize:

- a broad claim that CuPy will beat OptiX on RayJoin
- a broad claim that OptiX will beat CuPy on RayJoin
- full RayJoin paper reproduction
- paper-scale performance claims
- v2.0 release authorization

## Next Work

1. Add a persistent-session benchmark mode that separates acceleration-structure build, module warmup, and repeated query traversal.
2. Search larger bounded public CDB slices with more candidate pairs and nonzero intersections.
3. Add a CuPy grid or bounding-box prefilter variant so the non-RT baseline is not only brute force.
4. Only promote RayJoin RT speed claims if OptiX beats the best available same-contract partner baseline under a documented protocol.

## Verdict

Goal2161 is accepted as a benchmark-hardening and negative-result documentation step. It improves our evidence quality by showing that the current RTDL/OptiX RayJoin LSI path is correct but not yet the best-performing v2.0 user implementation on these bounded public slices.
