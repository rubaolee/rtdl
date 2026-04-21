# Goal699 RTX Fixed-Radius Profile Report

Profile JSON: `docs/reports/goal698_rtx_cloud_fixed_radius_phase_profile_2026-04-21.json`
Environment file: `docs/reports/goal698_rtx_cloud_environment_2026-04-21.txt`

## Verdict Inputs

- mode: `optix`
- backend: `optix`
- copies: `128`
- iterations: `5`
- classification_change: `false`
- rtx_speedup_claim_in_input: `false`
- oracle_parity: `true`
- eligible_for_rtx_claim_review: `true`

## Comparison

| app | row path total median (s) | summary path total median (s) | total ratio row/summary | row backend median (s) | summary backend median (s) | backend ratio row/summary |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| outlier_detection | 0.225426 | 0.174460 | 1.292 | 0.004152 | 0.003364 | 1.234 |
| dbscan_clustering | 0.183948 | 0.334450 | 0.550 | 0.003634 | 0.003466 | 1.049 |

## Interpretation Boundary

This report is a structured interpretation of Goal697 profiler JSON. It does not by itself upgrade RTDL's public OptiX app classification.

A speedup statement is review-eligible only when `mode=optix`, `backend=optix`, every case preserves oracle parity, and the environment file records RTX-class hardware. Dry-run or GTX 1070 data must remain correctness/instrumentation evidence, not RT-core performance evidence.

The current native fixed-radius ABI reports whole-call timing. Packing, BVH build, OptiX launch, and copy-back are still not separately attributed.

## Environment Excerpt

```text
Goal698 RTDL RTX cloud validation environment
date_utc=2026-04-21T13:06:35Z
host=a4f981cabfae
repo=/root/rtdl_runpod_validation
commit=09147a6
python=Python 3.11.10
optix_prefix=/root/vendor/optix-dev
cuda_prefix=/usr/local/cuda
nvcc=/usr/local/cuda/bin/nvcc

nvidia-smi:
Tue Apr 21 13:06:35 2026       
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 580.126.09             Driver Version: 580.126.09     CUDA Version: 13.0     |
+-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  NVIDIA RTX A5000               On  |   00000000:57:00.0 Off |                  Off |
| 30%   21C    P5             24W /  230W |       1MiB /  24564MiB |      0%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+

+-----------------------------------------------------------------------------------------+
| Processes:                                                                              |
|  GPU   GI   CI              PID   Type   Process name                        GPU Memory |
|        ID   ID                                                               Usage      |
|=========================================================================================|
|  No running processes found                                                             |
+-----------------------------------------------------------------------------------------+

nvcc version:
nvcc: NVIDIA (R) Cuda compiler driver
Copyright (c) 2005-2024 NVIDIA Corporation
Built on Thu_Mar_28_02:18:24_PDT_2024
Cuda compilation tools, release 12.4, V12.4.131
Build cuda_12.4.r12.4/compiler.34097967_0
```
