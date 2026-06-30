# Goal2275: Prepared Segment-Pair Cached Right Lookup

Status: implemented locally; pod timing must be recorded separately.

## Purpose

Goal2273 showed that the new scalar count path does not materially improve the
sparse RayJoin-exported LSI stream. A code audit found one generic prepared-path
overhead: every prepared segment-pair run rebuilt a right-side `id -> segment`
lookup table even though the right-side scene is fixed by the prepared handle.

Goal2275 caches that right-side lookup inside
`PreparedSegmentPairIntersectionBuild` and reuses it in both:

- `run_prepared_segment_pair_intersection_optix`, and
- `count_prepared_segment_pair_intersection_optix`.

## Boundary

This is an app-agnostic prepared-scene optimization. It is not an LSI-specific
or RayJoin-specific engine path. The optimization preserves the same candidate
collection, exact segment-intersection refinement, and duplicate-pair
suppression.

## Expected Measurement

This implementation report does not claim a speedup by itself. Pod timing should
compare the RayJoin-exported 100k LSI stream before/after the cached right
lookup. A useful result may be small because the remaining runtime also includes
OptiX traversal, candidate copyback, left-side lookup construction, and exact
refinement.

