# Goal 550: HIPRT 2D Geometry Lowering Plan

Date: 2026-04-18

## Purpose

Bring the remaining 2D geometry workloads onto HIPRT without using CPU fallback and without pretending ordinary GPU brute force is HIPRT support.

## Target Workloads

Goal 550 covers these v0.9 target predicates:

- `segment_intersection`
- `ray_triangle_hit_count` with `Ray2DLayout` / `Triangle2DLayout`
- `point_in_polygon`
- `overlay_compose`
- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`
- `point_nearest_segment`

## Lowering Design

### Shared HIPRT Representation

Use HIPRT AABB-list custom primitives for all 2D build-side objects. Coordinates remain in XY; Z is fixed at `0`.

- Build segments become segment AABBs.
- Build triangles become triangle AABBs.
- Build polygons become polygon bounding boxes plus packed vertex ranges.
- Build segments for nearest-segment become segment AABBs.

Probe objects cast HIPRT rays or zero-length probe rays:

- Query segment: ray from `(x0, y0, 0)` toward `(x1 - x0, y1 - y0, 0)` with `maxT = 1`.
- Query ray: ray from `(ox, oy, 0)` toward `(dx, dy, 0)` with `maxT = tmax`.
- Query point: zero-length or epsilon-length probe ray at `(x, y, 0)`.
- Query polygon: a small set of boundary segment probes plus representative vertex probes when overlay classification requires it.

Custom intersection functions do exact 2D refinement after HIPRT candidate discovery:

- Segment-vs-segment intersection for `segment_intersection`.
- Ray-vs-triangle edge crossing or point-in-triangle logic for `ray_triangle_hit_count`.
- Point-in-polygon for `point_in_polygon`.
- Segment-vs-polygon edge/boundary checks for segment/polygon workloads.
- Point-vs-segment distance and top-1 selection for `point_nearest_segment`.

## Execution Order

1. `segment_intersection`: first 2D custom-AABB traversal because it is the simplest and exercises multi-hit row emission.
2. `ray_triangle_hit_count` 2D: use the same query-ray pattern with triangle custom primitives.
3. `point_in_polygon`: polygon AABB candidate discovery plus custom vertex-range refinement.
4. `segment_polygon_hitcount` and `segment_polygon_anyhit_rows`: reuse segment probe and polygon build representation.
5. `overlay_compose`: compose LSI and PIP-style tests, but only count as HIPRT-supported if the heavy candidate/refinement work stays inside HIPRT-backed kernels.
6. `point_nearest_segment`: use segment AABB traversal and top-1 distance refinement; if exact nearest cannot be bounded without broad candidate expansion, document it as correctness-first and not performance-forward.

## Bounded v0.9 Constraints

- Initial row buffers may use conservative bounded capacities with explicit overflow errors rather than silent truncation.
- Geometry counts must fit `uint32_t`.
- Per-query local candidate/rank buffers must have explicit documented ceilings.
- No target workload may silently call `rt.run_cpu_python_reference`.
- If a workload uses HIPRT only for broad candidate discovery and then performs large CPU-side refinement, it is not accepted as HIPRT support.

## Performance Position

The first v0.9 requirement is correctness parity and honest HIPRT traversal. Performance comparisons are required later against Embree, OptiX, and Vulkan, but only after correctness passes. For the GTX 1070 Linux validation host, no RT-core speedup claim is allowed.

## Consensus Request

This plan should receive 3-AI consensus before implementation because it defines how the largest remaining HIPRT workload family will be counted as supported.

Codex plan verdict: ACCEPT.

Claude external verdict: ACCEPT in `/Users/rl2025/rtdl_python_only/docs/reports/goal550_hiprt_2d_geometry_plan_external_review_2026-04-18.md`.

Gemini Flash verdict: ACCEPT in `/Users/rl2025/rtdl_python_only/docs/reports/goal550_hiprt_2d_geometry_plan_gemini_flash_review_2026-04-18.md`.

Consensus: 3-AI ACCEPT. Goal 550 plan is approved for implementation.
