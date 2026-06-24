# Goal2167 RayJoin Count512 Count-First LSI Evidence

Date: 2026-05-16

Status: larger bounded slice added and pod-validated.

## Purpose

Goal2165 showed that count-first prepared OptiX LSI beats the same-runner CuPy brute-force baseline on `count192`, `count256`, and `count384` public CDB slices.

Goal2167 adds one larger bounded public CDB LSI slice, `lsi_county256_soil256_count512`, to test whether the same design keeps improving at higher candidate-pair counts.

## What Changed

`scripts/goal2159_rayjoin_public_cdb_runner.py` now defines:

- `lsi_county256_soil256_count512`
- county slice: `br_county_start256_count512.cdb`
- soil slice: `br_soil_start256_count512.cdb`

No native engine logic was changed in this goal.

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
- RTDL runner commit: `366b5e962a17761091edbcc6a326377ccea714cc`
- CuPy package: `cupy-cuda12x 14.0.1`

Collected artifact:

- `docs/reports/goal2167_rayjoin_count_first_optix_lsi_count512_pod_2026-05-16.json`

## Result

The run used one warmup and five measured repeats.

| Case | Candidate pairs | Rows | Prepared OptiX sec | CuPy brute-force sec | Prepared OptiX vs CuPy | Parity |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `lsi_county256_soil256_count512` | 136,411,275 | 269 | 0.021676 | 0.041058 | 1.894x | all pass |

## Interpretation

The count512 result strengthens the Goal2165 trend. As the bounded public CDB slice grows from 83.3M candidate pairs to 136.4M candidate pairs, prepared OptiX moves from a `1.57x` win over CuPy brute force to a `1.89x` win.

The result supports a narrow design conclusion:

- prepared build-side reuse matters
- count-first compact candidate output matters
- sparse segment-pair workloads are a good fit for RTDL/OptiX once output allocation stops scaling with the full Cartesian product

## Claim Boundary

This goal authorizes:

- adding `lsi_county256_soil256_count512` to the bounded public CDB runner
- a narrow statement that prepared OptiX beat the measured same-runner CuPy brute-force baseline by `1.894x` on this count512 slice
- using count512 as additional evidence for the Goal2165 count-first output design

This goal does not authorize:

- full RayJoin paper reproduction
- broad RT-core speedup claims
- v2.0 release authorization
- claims against stronger CuPy spatial-prefilter baselines that have not been implemented and measured yet

## Verdict

Goal2167 is accepted as a larger-slice validation step for the count-first prepared OptiX LSI design. It does not change the release boundary, but it gives a stronger performance signal for the RayJoin LSI lane.
