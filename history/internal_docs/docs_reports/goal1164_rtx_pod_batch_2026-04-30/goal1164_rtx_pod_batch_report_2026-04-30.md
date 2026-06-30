# Goal1164 RTX Pod Batch Report - 2026-04-30

## Scope

This report records the first consolidated RTX A5000 pod validation batch for the current v1.0 RT-core app work. It validates that the prepared/native OptiX paths can load and run on real NVIDIA RTX hardware after local pre-cloud preparation. It does not authorize broad public speedup wording by itself; each public claim still needs same-contract baseline comparison and external review.

## Pod Environment

```text
Thu Apr 30 13:39:47 UTC 2026
ed2fb89e0cc0
NVIDIA RTX A5000, 550.127.05, 24564 MiB
Python 3.12.3
Build cuda_13.0.r13.0/compiler.36424714_0
v8.0.0
include/optix.h:37:#define OPTIX_VERSION 80000
include/optix_function_table.h:29:#define OPTIX_ABI_VERSION 87
```

Operational constraints discovered during bootstrap:

- The pod driver accepts OptiX 8.0 headers (`OPTIX_ABI_VERSION 87`) but rejects OptiX 8.1/9.1 with `Unsupported ABI version`.
- CUDA 13 headers redirect `cuCtxCreate` to a driver symbol unavailable on driver 550; using the CUDA primary context (`cuDevicePrimaryCtxRetain` + `cuCtxSetCurrent`) fixes library loading.
- CUDA 13 NVRTC needs host glibc arch predefines on this pod, but forcing `--device-as-default-execution-space` breaks OptiX launch-parameter recognition. The working path for this pod is `RTDL_OPTIX_PTX_COMPILER=nvcc` with `/usr/local/cuda/bin/nvcc`.

## Compact Smoke Results

| App/gate | rc | elapsed_s | RT/native evidence |
|---|---|---|---|
| outlier_detection | 0 | 0.570 | native_continuation_backend=optix_threshold_count; native_continuation_active=True |
| facility_knn_assignment | 0 | 1.191 | native_continuation_backend=optix_threshold_count; rt_core_accelerated=True; native_continuation_active=True |
| ann_candidate | 0 | 1.229 | rt_core_accelerated=True |
| service_coverage_gaps | 0 | 1.163 | native_continuation_backend=optix_threshold_count; rt_core_accelerated=True; native_continuation_active=True |
| event_hotspot_screening | 0 | 1.151 | native_continuation_backend=optix_threshold_count; rt_core_accelerated=True; native_continuation_active=True |
| robot_collision_screening | 0 | 1.721 | native_continuation_backend=optix_prepared_pose_flags; native_continuation_active=True |
| barnes_hut_force | 0 | 1.179 | rt_core_accelerated=True |
| hausdorff_app | 0 | 1.059 | native_continuation_backend=optix_threshold_count; rt_core_accelerated=True; native_continuation_active=True |
| hausdorff_contract | 0 | 2.176 |  |
| road_hazard_gate | 0 | 1.377 | status=pass; strict_pass=True |
| graph_visibility_gate | 0 | 7.098 | status=pass; strict_pass=True |
| polygon_pair_gate | 0 | 1.653 | status=pass |
| polygon_jaccard_gate | 0 | 1.486 | status=pass |

Result: all smoke entries are green after rerunning outlier detection without an unsupported CLI `--require-rt-core` flag. The outlier JSON still records `native_continuation_backend=optix_threshold_count` and `native_continuation_active=true`.

## Medium Timed Batch

| Workload | rc | timeout | elapsed_s | status/app |
|---|---|---|---|---|
| facility_knn_assignment_copies_65536 | 0 | False | 3.830 | facility_knn_assignment |
| service_coverage_gaps_copies_65536 | 0 | False | 2.879 | service_coverage_gaps |
| event_hotspot_screening_copies_65536 | 0 | False | 3.018 | event_hotspot_screening |
| ann_candidate_copies_65536 | 124 | True | 600.117 |  |
| hausdorff_app_copies_65536 | 0 | False | 4.437 | hausdorff_distance |
| barnes_hut_body_65536 | 0 | False | 1.555 | barnes_hut_force_app |
| robot_pose_262144_obstacle_64 | 124 | True | 600.129 |  |
| road_hazard_copies_8192 | 0 | False | 2.324 | pass |
| graph_visibility_copies_4096 | 0 | False | 2.196 | pass |
| polygon_pair_copies_8192 | 0 | False | 4.073 | pass |
| polygon_jaccard_copies_8192 | 1 | False | 4.752 | fail |
| hausdorff_contract_points_65536 | 0 | False | 2.113 |  |

Main findings:

- Facility KNN, service coverage, event hotspot, Hausdorff, Barnes-Hut, road hazard, graph visibility, polygon pair overlap, and the Hausdorff contract all ran successfully at the tested medium scales.
- ANN at 65,536 copies and robot collision at 262,144 poses timed out at the 600 s per-command cap. Recovery runs below show these paths are functional but scale poorly in the current whole-app command shape.
- Polygon Jaccard at 8,192 copies with `chunk_copies=256` failed parity because the candidate set was incomplete.

## Recovery Runs

| Workload | rc | timeout | elapsed_s | status/app |
|---|---|---|---|---|
| ann_candidate_copies_1024 | 0 | False | 2.066 | ann_candidate_search |
| ann_candidate_copies_8192 | 0 | False | 52.339 | ann_candidate_search |
| robot_pose_8192_obstacle_64 | 0 | False | 29.603 | robot_collision_screening |
| robot_pose_32768_obstacle_64 | 0 | False | 112.341 | robot_collision_screening |
| polygon_jaccard_copies_1 | 0 | False | 1.561 | pass |
| polygon_jaccard_copies_256 | 0 | False | 1.402 | pass |
| polygon_jaccard_copies_8192_chunk8192 | 0 | False | 1.692 | needs_optix_runtime |

Recovery interpretation:

- ANN is functional at 1,024 and 8,192 copies, but 8,192 copies already takes 52.339 s. The 65,536-copy timeout is therefore a scaling/performance bottleneck, not an OptiX availability failure.
- Robot collision is functional at 8,192 and 32,768 poses, taking 29.603 s and 112.341 s respectively. The 262,144-pose timeout is expected under the current app path and should not be used as a release-speed claim.
- Jaccard `chunk_copies=8192` returns `needs_optix_runtime` due to LSI output capacity overflow; this is a capacity boundary, not a crash.

## Jaccard Chunk Sweep

| chunk_copies | status | parity_vs_cpu | optix_candidate_rows | optix_candidate_sec |
|---|---|---|---|---|
| 1024 | pass | True | 16384 | 1.769 |
| 2048 | pass | True | 16384 | 2.413 |
| 4096 | pass | True | 16384 | 3.015 |
| 512 | pass | True | 16384 | 2.198 |

Jaccard conclusion: for 8,192 copies on this fixture, chunk sizes 512, 1024, 2048, and 4096 pass parity. Chunk size 256 misses candidates, while all-in-one 8192 overflows LSI output capacity. Current docs/scripts should avoid presenting arbitrary chunking as semantically neutral for Jaccard until candidate merging is made chunk-boundary safe.

## Current App Status From This Batch

- `really ran on RTX OptiX prepared/native path`: outlier detection, facility KNN assignment, service coverage gaps, event hotspot screening, ANN candidate search, Barnes-Hut node coverage, Hausdorff threshold, robot collision prepared pose flags, road hazard native gate, graph visibility/native graph gate, polygon pair candidate discovery, polygon Jaccard candidate discovery at safe chunk sizes.
- `needs performance work before public speed claim`: ANN candidate search and robot collision, because medium-large whole-app sizes are slow or timeout.
- `needs implementation-boundary fix`: polygon Jaccard chunking, because too-small chunks can miss candidates and too-large chunks can overflow output capacity.
- `needs public-claim review`: all speedup wording. This report is runtime evidence, not a final public wording authorization.

## Files

- Environment: `docs/reports/goal1164_rtx_pod_batch_2026-04-30/environment.txt`
- Smoke artifacts: `docs/reports/goal1164_rtx_pod_batch_2026-04-30/smoke/`
- Medium artifacts: `docs/reports/goal1164_rtx_pod_batch_2026-04-30/timed_medium/`
- Recovery artifacts: `docs/reports/goal1164_rtx_pod_batch_2026-04-30/recovery/`
- Jaccard sweep artifacts: `docs/reports/goal1164_rtx_pod_batch_2026-04-30/jaccard_sweep/`
