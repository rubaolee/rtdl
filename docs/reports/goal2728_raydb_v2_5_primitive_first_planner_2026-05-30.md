# Goal2728: RayDB v2.5 Primitive-First Planner

Date: 2026-05-30
Status: accepted as planner correction with pod evidence

## Purpose

Goal2727 showed that the prepared fused generic grouped-reduction primitive is the correct RayDB fast path for grouped scalar reductions. Goal2728 turns that lesson into an explicit v2.5 planner backend:

`paper_rt_optix_v2_5_primitive_first`

The planner is intentionally simple and explainable:

1. If the user continuation matches an existing fused app-agnostic RTDL primitive, select that primitive.
2. If the continuation cannot be expressed by the fused primitive set, keep the typed hit-stream plus partner-continuation path available.
3. Do not claim public speedup or true zero-copy from this routing decision.

## Artifact

`docs/reports/goal2728_pod_artifacts/goal2728_raydb_v25_primitive_first_planner_pod_69_30_85_171_2026-05-30.json`

Pod:

- host: `69.30.85.171`
- port: `22167`
- GPU: `NVIDIA RTX A5000, 570.211.01, 24564 MiB`
- commit: `782dcc17cac7ad5cee82e89a6a94ae4ce4ca3128`
- repeats: `3`
- warmup: `1`
- group count: `256`

## Results

| Rows | Mode | Primitive-first median sec | Selected path | Selected reduction |
| ---: | --- | ---: | --- | --- |
| 250000 | count | 0.000432 | prepared fused generic grouped reduction | count |
| 250000 | sum | 0.001787 | prepared fused generic grouped reduction | sum |
| 1000000 | count | 0.000371 | prepared fused generic grouped reduction | count |
| 1000000 | sum | 0.002094 | prepared fused generic grouped reduction | sum |

All cases reported:

- `matches_cpu_reference = true`
- `prepared_steady_state = true`
- `prepared_optix_scene_reused = true`
- `prepared_primitive_payload_reused = true`
- `prepared_ray_batch_reused = true`
- `v2_5_selected_path = prepared_fused_generic_grouped_reduction`
- `v2_5_alternative_backend = paper_rt_optix_device_hit_stream_triton_prepared`
- `v2_5_alternative_reserved_for = continuations_not_expressible_as_fused_generic_rtdl_reductions`
- `typed_hit_stream_forced = false`
- `partner_continuation_required = false`
- `true_zero_copy_authorized = false`

## Interpretation

This closes the immediate RayDB planning mistake. v2.5 should not be "partner first" or "hit-stream first." It should be primitive-first:

- use fused RTDL primitives when they exactly match the computation;
- use partner continuations when a tensor continuation is needed;
- keep custom shader/user-defined continuation work out of v2.5 and in the future v3.0 lane.

For RayDB-style grouped count and sum, this means the planner selects the prepared fused RTDL primitive. The typed hit-stream path remains a real v2.5 capability, but it is not the fastest route for these scalar grouped reductions.

## Boundary

This goal does not authorize:

- true-zero-copy wording;
- broad RT-core speedup wording;
- whole-app RayDB reproduction claims;
- claims that partner continuations are unnecessary in v2.5;
- claims about apps whose continuation is not a fused grouped scalar reduction.

It does authorize this internal design rule: v2.5 planners must record selected backend, selected primitive/path, skipped alternative, fallback reason, and claim boundary.

