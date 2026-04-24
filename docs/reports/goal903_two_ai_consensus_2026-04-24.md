# Goal903 Two-AI Consensus

Date: 2026-04-24

## Scope

Goal903 converts the Embree graph BFS and triangle-count candidate-generation
paths from `rtcPointQuery` to `rtcIntersect1` ray traversal over graph-edge
user-geometry primitives.

## Review Inputs

- Primary implementation report:
  `docs/reports/goal903_embree_graph_ray_traversal_2026-04-24.md`
- Claude review:
  `docs/reports/goal903_claude_review_2026-04-24.md`
- Gemini review:
  `docs/reports/goal903_gemini_review_2026-04-24.md`

## Consensus

Verdict: ACCEPT.

Both reviewers accept the implementation and honesty boundary.

Agreed facts:

- Embree BFS now uses `rtcSetGeometryIntersectFunction` and `rtcIntersect1`,
  not `rtcPointQuery`.
- Embree triangle-count now uses `rtcSetGeometryIntersectFunction` and
  `rtcIntersect1`, not `rtcPointQuery`.
- Each CSR edge is represented as a user-geometry primitive at
  `(src_vertex, 0)`, with `dst_vertex` stored as payload.
- The source-column ray formulation is a valid Embree CPU ray-tracing
  candidate-generation path.
- The implementation does not create a NVIDIA RT-core claim for BFS or
  triangle-count.
- OptiX BFS and triangle-count remain host-indexed fallback until a separate
  native graph-ray lowering is implemented and validated on RTX hardware.

## Non-Blocking Notes

Claude noted two non-blockers:

- The callback source-vertex guard is redundant but harmless.
- Triangle-count uniqueness still uses a linear scan in the accumulated rows;
  this is correct and pre-existing, but it may need optimization for larger
  graph workloads.

## Release Boundary

Goal903 is accepted for the local Embree graph-ray prototype. It is not a
release authorization for NVIDIA graph RT-core acceleration. The next goal must
implement the matching OptiX graph-ray lowering or keep BFS/triangle-count out
of NVIDIA RT-core claim tables.
