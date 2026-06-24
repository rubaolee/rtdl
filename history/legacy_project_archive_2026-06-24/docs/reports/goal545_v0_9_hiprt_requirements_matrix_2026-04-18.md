# Goal 545: v0.9 HIPRT Requirements And Feasibility Matrix

Date: 2026-04-18
Status: accepted with 3-AI consensus

## Purpose

Goal 545 defines the v0.9 HIPRT release line before implementation continues.

The user target is ambitious: HIPRT should deliver the same support shape as
OptiX, Embree, and Vulkan, and every workload should have correctness and
performance evidence compared with those backends.

The plan keeps that target, but adds the required honesty rule: no workload may
be counted as HIPRT-supported through silent CPU fallback or vague wording. Each
workload must either pass HIPRT correctness/performance gates or receive an
explicit 3-AI consensus reclassification.

## Primary Plan Artifact

- `/Users/rl2025/rtdl_python_only/docs/proposals/v0_9_hiprt_backend_full_support_plan_2026-04-18.md`

Machine-readable matrix:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal545_v0_9_hiprt_requirements_matrix_2026-04-18.json`

## Current HIPRT Baseline

HIPRT currently supports:

- version probe;
- context probe;
- direct Ray3D/Triangle3D hit count;
- prepared Ray3D/Triangle3D hit count;
- `run_hiprt(...)` / `prepare_hiprt(...)` dispatch for the same 3D hit-count
  shape.

It does not currently support:

- 2D geometry workloads;
- nearest-neighbor workloads;
- graph workloads;
- DB workloads;
- prepared DB dataset reuse.

## Required Peer Workload Surface

The peer backend workload set includes:

- `segment_intersection`
- `point_in_polygon`
- `overlay_compose`
- 2D `ray_triangle_hit_count`
- 3D `ray_triangle_hit_count`
- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`
- `point_nearest_segment`
- 2D `fixed_radius_neighbors`
- 3D `fixed_radius_neighbors`
- 2D `knn_rows`
- 3D `knn_rows`
- `bfs_discover`
- `triangle_match`
- `conjunctive_scan`
- `grouped_count`
- `grouped_sum`
- prepared DB dataset reuse for DB workloads

## Goal Ladder

- Goal 545: requirements, feasibility matrix, and 3-AI plan consensus.
- Goal 546: HIPRT API parity skeleton with precise `NotImplementedError`
  rejection for workloads not implemented yet.
- Goal 547: cross-workload HIPRT correctness harness.
- Goal 548: HIPRT 3D geometry and 3D nearest-neighbor expansion.
- Goal 549: HIPRT 2D geometry expansion.
- Goal 550: HIPRT graph expansion.
- Goal 551: HIPRT DB expansion and prepared dataset support.
- Goal 552: Linux cross-backend correctness/performance suite.
- Goal 553: v0.9 public docs, tutorials, examples, and support matrix.
- Goal 554: v0.9 pre-release test, doc, and flow audit.

## Main Risks

- 2D ray/triangle semantics may not map directly to HIPRT triangle traversal
  because a lifted 2D ray may be coplanar with a lifted triangle.
- Graph workloads may become ordinary GPU compute unless a real HIPRT traversal
  lowering is found.
- DB workloads require custom row/predicate spatial encoding and exact grouping
  semantics.
- The available Linux GPU is a GTX 1070; timing evidence is valid, but no
  RT-core speedup can be claimed on that host.
- No AMD GPU validation is possible with the current hardware.

## Codex Position

Codex accepts the plan as the right v0.9 starting point because it preserves the
user's target while preventing dishonest release claims. The implementation
should proceed goal-by-goal, with 3-AI review for plan scope and for any
workload rejection or reclassification.

## Consensus

- Codex: ACCEPT
- Claude: ACCEPT in `/Users/rl2025/rtdl_python_only/docs/reports/goal545_external_review_2026-04-18.md`
- Gemini Flash: ACCEPT in `/Users/rl2025/rtdl_python_only/docs/reports/goal545_gemini_flash_review_2026-04-18.md`

Goal 545 is accepted as the v0.9 planning baseline. Implementation can proceed
through the goal ladder, but any workload rejection or reclassification still
requires the 3-AI gate defined in the plan.
