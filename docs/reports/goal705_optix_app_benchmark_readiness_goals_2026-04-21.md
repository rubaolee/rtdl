# Goal705: OptiX App Benchmark Readiness Goals

Date: 2026-04-21

Status: implementation and local verification pending external AI review

## Purpose

Goal705 converts the current performance discussion into a conservative gate:
RTDL should not spend more RTX cloud time on broad app benchmarking until the
apps are tuned enough that the results will be meaningful.

The key rule is simple: `--backend optix` is not a performance claim. A public
app becomes benchmark-ready only when the measured path isolates the relevant
native OptiX traversal or native summary work from Python packing, row
materialization, validation, and post-processing.

## Added Source Of Truth

Machine-readable API:

- `rtdsl.optix_app_benchmark_readiness_matrix()`
- `rtdsl.optix_app_benchmark_readiness(app)`
- `rtdsl.OPTIX_APP_BENCHMARK_READINESS_STATUSES`

Public documentation:

- `/Users/rl2025/rtdl_python_only/docs/app_engine_support_matrix.md`

## Current Readiness Summary

No app is marked `ready_for_rtx_claim_review` yet.

Closest candidates:

- `robot_collision_screening`: best OptiX traversal flagship candidate, but
  needs a phase-clean RTX rerun after compact-output/profiler polish.
- `outlier_detection`: RunPod RTX A5000 evidence is promising for
  `rt_count_threshold`, but the profiler still mixes validation and postprocess
  costs.
- `dbscan_clustering`: native core-flag summary exists, but full DBSCAN still
  includes Python cluster expansion; the core-flag sub-result must be timed
  separately.

Explicitly not RTX RT-core app-claim candidates today:

- CUDA-through-OptiX apps: Hausdorff, ANN candidate search, Barnes-Hut.
- Host-indexed fallback apps: graph analytics and default segment/polygon
  paths until native GPU/OptiX modes are promoted by tests.
- Apps without public OptiX exposure: Apple RT demo, HIPRT demo, CPU-only
  polygon overlap/Jaccard, and Embree/SciPy-only spatial examples.

## Follow-Up Goals

Goal706: DB analytics interface tuning.

Required result: prepared dataset timing splits packing, BVH/build,
launch/traversal, copy-back, exact filtering, grouping, and Python
materialization. The app may only make a performance claim if native/backend
work is no longer hidden by Python rows or host reduction.

Goal707: graph analytics native-kernel decision.

Required result: BFS and triangle-count either move to native GPU/OptiX
execution for the measured path or remain explicitly excluded from RTX RT-core
app claims.

Goal708: segment/polygon native/compact-path tuning.

Required result: hit-count and any-hit examples must benchmark native OptiX
mode and compact segment-level outputs separately from host fallback and
pair-row materialization.

Goal709: CUDA-through-OptiX app classification closure.

Required result: Hausdorff, ANN, and Barnes-Hut must either be benchmarked as
GPU-compute apps against appropriate GPU/CPU baselines or get a new valid
RT-core traversal design. They must not enter RT-core claim benchmarking as-is.

Goal710: outlier fixed-radius summary timing cleanup.

Required result: validation-free RTX timing for rows versus
`rt_count_threshold`, with backend/materialization, postprocess, oracle
validation, and total phases separated.

Goal711: DBSCAN core-flag timing cleanup.

Required result: core-flag summary timing separated from Python cluster
expansion and validation. Any claim must say core flags only, not full DBSCAN
acceleration.

Goal712: robot collision flagship timing cleanup.

Required result: RTX timing splits prepared-scene build/reuse, ray-buffer
packing, OptiX traversal, compact output, and oracle validation.

## Cloud Policy

Do not rent or keep a paid RTX cloud instance for broad app benchmarking until
Goal706 through Goal712 either close or explicitly exclude their app from RTX
RT-core claims.

Allowed exception: a narrow confirmation run for one app whose phase contract
has already been fixed locally.

## Verification Plan

- Focused unit tests must confirm that every public app has a benchmark
  readiness row.
- Tests must confirm that no app is currently marked
  `ready_for_rtx_claim_review`.
- Tests must confirm that high-risk apps are blocked or excluded, not silently
  promoted.
- Public docs must state the cloud benchmark policy and the
  `optix_app_benchmark_readiness_matrix()` API.

## Consensus Plan

Goal705 requires external review by Claude and Gemini Flash before follow-up
implementation starts. Reviewers should specifically check whether the gate is
too permissive. If they disagree, the default action is to make the matrix more
conservative, not less.

## Review Resolution

Gemini Flash returned ACCEPT with no blockers. Claude returned ACCEPT with
tightening findings. Goal705 resolved the actionable findings before closure:

- `segment_polygon_anyhit_rows` now uses `needs_native_kernel_tuning`, matching
  its `host_indexed_fallback` performance class until Goal708 promotes a native
  OptiX any-hit path.
- The Goal705 public API symbols are included in `rtdsl.__all__`.
- Focused tests now pin OptiX performance classes alongside readiness statuses,
  including the explicit `cuda_through_optix` exceptions for outlier and DBSCAN
  summary sub-paths.
