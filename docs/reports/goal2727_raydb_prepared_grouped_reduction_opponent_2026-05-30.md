# Goal2727: RayDB Prepared Grouped-Reduction Opponent

Date: 2026-05-30
Status: accepted as corrective v2.5 design evidence

## Purpose

Goal2726 compared the prepared v2.5 hit-stream path against the older `paper_rt_optix` whole-call path. That was useful diagnostic evidence, but Claude's review correctly asked for a fairer same-contract opponent.

Goal2727 adds that opponent:

- backend label: `paper_rt_optix_prepared_grouped_reduction`;
- app-owned workload and query encoding are built once;
- generic OptiX scene is prepared once;
- generic primitive grouped payload is prepared once;
- ray batch is prepared once;
- measured iterations call the prepared generic grouped-reduction primitive directly.

This is still app-agnostic native execution: the native symbol is `rtdl_optix_static_triangle_scene_3d_ray_batch_prepared_primitive_grouped_i64_reduction`, and the app semantics remain in Python.

## Artifact

`docs/reports/goal2727_pod_artifacts/goal2727_raydb_prepared_grouped_vs_hit_stream_large_pod_69_30_85_171_2026-05-30.json`

Pod:

- host: `69.30.85.171`
- port: `22167`
- GPU: `NVIDIA RTX A5000, 570.211.01, 24564 MiB`
- commit: `861ae819bd02dddbc64a787044b6147bcbe7f3ae`
- repeats: `3`
- warmup: `1`
- group count: `256`

## Results

| Rows | Mode | Prepared grouped-reduction sec | Prepared v2.5 hit-stream+Triton sec | Hit-stream relative to fused primitive |
| ---: | --- | ---: | ---: | ---: |
| 250000 | count | 0.000421 | 0.011566 | 27.5x slower |
| 250000 | sum | 0.001846 | 0.259406 | 140.5x slower |
| 1000000 | count | 0.000360 | 0.008254 | 23.0x slower |
| 1000000 | sum | 0.002174 | 0.268089 | 123.3x slower |

All cases reported `matches_cpu_reference = true`.

## Interpretation

This is a good negative result. It prevents a wrong v2.5 design conclusion.

For RayDB-style `count` and `sum`, the continuation is already one of RTDL's generic fused reductions. In that case, a device hit-stream is the wrong fast path: it emits and hands off intermediate hit rows so a partner can perform a continuation that the native generic primitive can already perform more cheaply. The prepared grouped-reduction path keeps the continuation fused inside an app-agnostic native primitive and avoids the hit-stream materialization cost.

The v2.5 hit-stream path remains important, but its proper role is narrower:

- expose device-resident RT hit columns when the user continuation is not expressible as an existing fused generic primitive;
- provide typed payload columns to Torch/Triton/CuPy adapters for richer tensor continuations;
- serve as the bridge toward future user-defined continuation systems.

It should not replace an existing faster fused RTDL primitive for `count`, `sum`, `min`, `max`, or `sum_count` when those operations exactly match the user's program.

## Design Correction

The v2.5 planner should be primitive-first rather than hit-stream-first:

1. If the user continuation matches a fused app-agnostic RTDL primitive, route to the fused prepared primitive.
2. If the continuation needs generic tensor work that the fused primitive set cannot express, route to typed device hit-stream handoff plus partner continuation.
3. If the continuation requires user-authored device code or custom shader logic, leave it in the future v3.0 extension lane.

This preserves the v2.5 goal while avoiding a performance trap. The language/runtime should offer hit streams as a capability, not force hit streams as the universal lowering.

## Boundary

This goal does not authorize:

- true-zero-copy wording;
- broad RT-core speedup wording;
- public v2.5 release parity claims;
- RayDB paper reproduction claims;
- replacing all partner work with native fused reductions.

It does authorize an internal design statement: for RayDB-style grouped scalar reductions, the current prepared fused RTDL primitive is the correct v2.x fast path, while the v2.5 typed hit-stream path is reserved for continuations not covered by fused generic primitives.

