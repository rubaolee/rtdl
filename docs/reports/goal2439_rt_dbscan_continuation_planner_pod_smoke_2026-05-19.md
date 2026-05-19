# Goal2439 RT-DBSCAN Continuation Planner Pod Smoke

Date: 2026-05-19

Status: pod-smoked, with boundary.

## Purpose

Goal2437 added `planned_rt_dbscan_continuation`, an explicit app-level planner
that chooses between:

- full OptiX-written directed fixed-radius adjacency;
- chunked OptiX-written directed fixed-radius adjacency.

Goal2439 verifies that the planner executes both branches on the current
hardware checkout and records its decision metadata. This is a smoke test of
the plan/explain surface, not a new performance claim.

## Pod

```text
ssh root@69.30.85.177 -p 22055 -i C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod
```

The pod checkout was reset to:

```text
1aa52fad5746899c768fa8e4473bca59344569e7
```

OptiX runtime:

```text
RTDL_OPTIX_LIBRARY=/root/rtdl_goal2415/build/librtdl_optix.so
CUDA_HOME=/usr/local/cuda-12
RTDL_OPTIX_PTX_ARCH=compute_86
```

Artifacts:

- `docs/reports/goal2439_rt_dbscan_continuation_planner_pod_smoke/tiny_validated.json`
- `docs/reports/goal2439_rt_dbscan_continuation_planner_pod_smoke/clustered4096_full_adjacency_validated.json`
- `docs/reports/goal2439_rt_dbscan_continuation_planner_pod_smoke/clustered32768_chunked_adjacency_no_validation.json`
- `docs/reports/goal2439_rt_dbscan_continuation_planner_pod_smoke/summary.json`

## Results

| Row | Points | Selected mode | Estimated directed edges | Budget | Fits budget | App elapsed (s) | Outer elapsed (s) | Matches reference |
| --- | ---: | --- | ---: | ---: | --- | ---: | ---: | --- |
| `tiny_validated` | 9 | `cpu_reference` | 33 | 64,000,000 | yes | 0.000110 | 0.416245 | yes |
| `clustered4096_full_adjacency_validated` | 4,096 | `optix_rt_core_adjacency_cupy_components_3d` | 2,113,929 | 64,000,000 | yes | 1.389266 | 3.534881 | yes |
| `clustered32768_chunked_adjacency_no_validation` | 32,768 | `optix_rt_core_chunked_adjacency_cupy_components_3d` | 135,291,470 | 64,000,000 | no | 1.727496 | 2.593822 | not run |

The large chunked row intentionally used `--no-validation` to avoid turning the
smoke test into a slow CPU-oracle run. Correctness for the underlying chunked
mode is covered by Goal2433/Goal2435 pod artifacts; this goal verifies that the
planner selects and executes that branch.

## What This Confirms

- The `tiny` fixture remains a CPU correctness fixture.
- A small clustered row whose estimated full adjacency stream fits the explicit
  budget selects the full OptiX adjacency contract and validates against the CPU
  reference.
- A dense clustered row whose estimated stream exceeds the explicit budget
  selects the chunked OptiX adjacency contract.
- Every planner result records `not_hidden_dispatcher: true`.
- Every planner result keeps release and paper-reproduction claims disabled.

## Boundary

This goal does not add native DBSCAN ABI. It does not change the RTDL engine. It
does not authorize a broad RT-core speedup, DBSCAN paper reproduction, or release
claim.

The only conclusion is that the Goal2437 explicit continuation planner executes
on hardware and records the intended full-vs-chunked branch decisions.

## Verdict

`accept-with-boundary`.
