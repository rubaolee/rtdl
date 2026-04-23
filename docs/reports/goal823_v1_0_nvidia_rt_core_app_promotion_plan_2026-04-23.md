# Goal823 v1.0 NVIDIA RT-Core App Promotion Plan

Date: 2026-04-23

## Verdict

ACCEPT. The v1.0 NVIDIA RT-core app work now has a concrete tiered plan and a
cloud-cost rule.

## Plan File

`/Users/rl2025/rtdl_python_only/docs/goal_823_v1_0_nvidia_rt_core_app_promotion_plan.md`

## Core Decision

RTDL will not equate `--backend optix` with NVIDIA RT-core acceleration. Apps
are promoted only when their dominant RTDL operation uses OptiX traversal over
an acceleration structure, with correctness evidence and phase-clean timing.

## Execution Order

1. Tier 1: robot collision, outlier, DBSCAN, and DB compact summaries.
2. Tier 2: service coverage and event hotspot after phase-profiler evidence.
3. Tier 3: segment/polygon, graph, Hausdorff, ANN, and Barnes-Hut after native
   OptiX redesign or strict validation.
4. Tier 4: facility KNN and polygon overlap/Jaccard after an OptiX app surface
   exists.

## Cloud Policy

Do not ask the user to restart or stop cloud pods per app. Local development
must produce a batched readiness gate first. The next paid RTX session should
run one consolidated batch and collect all artifacts before shutdown.

## Verification

This is a planning goal. It will be followed immediately by a local pre-cloud
readiness gate that mechanically checks the manifest, docs, dry-run runner, and
excluded/deferred app boundaries.
