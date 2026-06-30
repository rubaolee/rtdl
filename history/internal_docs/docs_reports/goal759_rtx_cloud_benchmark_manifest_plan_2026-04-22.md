# Goal 759: RTX Cloud Benchmark Manifest Plan

Status: plan.

## Purpose

Before renting another RTX cloud GPU, RTDL needs a machine-readable manifest of
which app paths should be benchmarked and what each result is allowed to claim.
The recent app work added prepared OptiX traversal paths, but the public app
surface also contains CUDA-through-OptiX, host-indexed fallback, and
Python/postprocess-dominated paths. A manifest prevents accidental mixing of
these categories during paid cloud runs.

## Proposed Artifact

Add `scripts/goal759_rtx_cloud_benchmark_manifest.py`.

It should emit JSON with:

- repository path and goal metadata
- candidate app path entries
- exact commands to run on an RTX host
- required backend/build preconditions
- performance class from `rtdsl.optix_app_performance_matrix()`
- benchmark readiness from `rtdsl.optix_app_benchmark_readiness_matrix()`
- allowed claim and explicit non-claim
- recommended scale parameters

## Initial Manifest Entries

Include only app paths that are useful for the next NVIDIA cloud run:

- `database_analytics`: prepared DB session profiler, correctness-capable
  OptiX DB path, interface-tuning evidence only.
- `outlier_detection`: prepared fixed-radius threshold summary path,
  `optix_traversal_prepared_summary`, no whole-app speedup claim.
- `dbscan_clustering`: prepared core-flag summary path,
  `optix_traversal_prepared_summary`, no full DBSCAN speedup claim.
- `robot_collision_screening`: prepared OptiX any-hit pose/count summaries,
  current cleanest traversal flagship candidate, still phase-gated.

Exclude from the manifest:

- Hausdorff, ANN, Barnes-Hut: current paths are CUDA-through-OptiX or
  Python/app dominated and should not be RT-core app benchmark candidates.
- Graph and segment/polygon host-indexed paths: not ready for RTX claims.
- Apple/HIPRT-specific apps: not OptiX cloud benchmark targets.

## Verification

- Add a focused test that checks:
  - manifest emits valid JSON;
  - every manifest app exists in `rtdsl.public_apps()`;
  - manifest performance/readiness values match the machine-readable matrices;
  - outlier and DBSCAN entries use `optix_traversal_prepared_summary`;
  - no excluded `cuda_through_optix` app enters the RTX claim candidate set.
- Run the script locally in dry-manifest mode.
- Run focused test plus `py_compile` and `git diff --check`.

## Consensus Request

Reviewer should confirm the manifest is a useful next gate and that it does not
promote any app into a broader RTX speedup claim before cloud evidence exists.
