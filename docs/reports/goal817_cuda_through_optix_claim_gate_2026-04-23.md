# Goal 817: CUDA-Through-OptiX Claim Gate

Date: 2026-04-23

Status: complete

## Problem

Three apps expose `--backend optix`, but their current OptiX paths are not
NVIDIA RT-core traversal claims:

- `examples/rtdl_hausdorff_distance_app.py`
- `examples/rtdl_ann_candidate_app.py`
- `examples/rtdl_barnes_hut_force_app.py`

They are useful GPU-compute paths through the OptiX backend library, but they
are classified as `cuda_through_optix`. That means they must not be included in
RT-core cloud claim batches until redesigned around real traversal primitives.

## Change

Added `--require-rt-core` to all three apps.

With `--backend optix`, the flag fails before backend dispatch:

- Hausdorff: CUDA-through-OptiX KNN rows, not RT-core traversal.
- ANN: CUDA-through-OptiX KNN rows, not RT-core traversal.
- Barnes-Hut: CUDA-through-OptiX radius candidate generation, not RT-core
  traversal.

With non-OptiX backends, the flag fails because it is specific to NVIDIA
RT-core claim-sensitive runs.

Payloads now include `rt_core_accelerated: false` for these apps.

## Current Status

| App | Current OptiX class | RT-core claim status |
| --- | --- | --- |
| Hausdorff distance | `cuda_through_optix` | no claim |
| ANN candidate search | `cuda_through_optix` | no claim |
| Barnes-Hut force app | `cuda_through_optix` | no claim |

## Required Future Work

Promotion requires a true traversal-friendly design for each app:

- Hausdorff: traversal-backed candidate/summary design, not plain KNN rows.
- ANN: traversal-backed candidate generation or explicit non-RT GPU-compute
  classification.
- Barnes-Hut: hierarchical node candidate traversal plus split force/opening
  reduction timing.

Each promoted path needs local correctness, phase-clean profiling, and RTX
review before cloud claims.

## Verification

Run:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal817_cuda_through_optix_claim_gate_test tests.goal705_optix_app_benchmark_readiness_test tests.goal803_rt_core_app_maturity_contract_test
python3 -m py_compile examples/rtdl_hausdorff_distance_app.py examples/rtdl_ann_candidate_app.py examples/rtdl_barnes_hut_force_app.py tests/goal817_cuda_through_optix_claim_gate_test.py
git diff --check
```

Expected result: all tests pass and no whitespace errors.

## Release Boundary

This goal adds claim-safety gates. It does not convert these apps to RT-core
traversal and does not authorize RTX speedup claims.
