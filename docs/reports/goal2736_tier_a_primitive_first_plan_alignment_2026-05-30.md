# Goal2736: Tier A Primitive-First Plan Alignment

Date: 2026-05-30
Status: accepted as v2.5 planner alignment

## Purpose

Goal2727-2732 corrected the RayDB v2.5 story: if an existing fused app-agnostic RTDL primitive exactly matches the computation, the planner should choose that primitive first and reserve typed hit-stream / partner continuation for unfused continuations.

Goal2730 applied the same rule to triangle counting. Goal2736 extends the explicit planner metadata to the other Tier A rows:

- Spatial RayJoin
- LibRTS-style AABB index query

## What Changed

Spatial RayJoin now exposes `v2_5_plan_payload()` with:

- selected path: `prepared_generic_rtdl_count_or_parity`
- selected primitive family: prepared point/shape, segment-pair, and shape-pair count/parity contracts
- typed hit-stream forced: false
- partner continuation required: false
- Triton reserved for optional compact-mask or grouped-count post-processing only if that continuation enters benchmark timing

LibRTS now exposes `v2_5_plan_payload()` with:

- selected path: `prepared_generic_aabb_index_query_2d`
- selected primitive: `AABB_INDEX_QUERY_2D`
- typed hit-stream forced: false
- partner continuation required: false
- Triton reserved for optional grouped summaries outside the prepared AABB query path

The v2.5 migration manifest now labels both rows as `primitive_first_rt_count_or_parity`.

## Boundary

This is not pod evidence and not a speedup claim. It is a planner consistency guard: the v2.5 roadmap must not accidentally route an already-fused native RTDL count/parity path through Triton just because Triton is the headline partner for v2.5.

Partner continuation remains important for unfused continuations, row streams, compact masks, top-k/ranking, witness-preserving reductions, and app-owned follow-up math. The rule is simply: fused generic primitive first when it exactly matches.
