# v0.4 Goal Sequence

Date: 2026-04-16 (Backfilled)
Last Updated: 2026-04-16
Status: historical

## Purpose

Record the goal ladder for the `v0.4` development line, which introduced the core nearest-neighbor (KNN and Fixed-radius) workload family and unified the GPU backend architecture.

## Sequence

1. Goal 193
   - `v0.4` direction decision and workload family selection
2. Goal 196
   - `fixed_radius_neighbors` contract and DSL surface design
3. Goal 202
   - `knn_rows` contract and Python truth-path closure
4. Goal 215
   - GPU rework proposal for unified OptiX/Vulkan RT pipelines
5. Goal 222
   - Windows harness portability closure and automated testing
6. Goal 228
   - "Heavy" nearest-neighbor performance benchmarking and optimizations
7. Goal 236
   - final `v0.4` release gate and `v0.5` paper-consistency direction
8. Goal 241
   - repo-wide project system-level audit and database indexing
9. Goal 257
   - `v0.5` readiness current state review and transition audit

## Discipline

This version marked the transition of RTDL from a feature-rich research codebase into a high-performance system capable of beating established baselines for complex spatial-join and neighbor queries.
