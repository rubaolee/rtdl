# Goal2269: Prepared Segment-Pair Intersection Count Mode

Status: implemented locally; pod timing must be recorded separately.

## Purpose

The RayJoin LSI-facing workload still needed a count-only path analogous to the
prepared closed-shape count work from Goals2258/2262. The existing prepared
segment-pair intersection surface returned witness rows
`(left_id, right_id, intersection_point_x, intersection_point_y)` and forced
Python to materialize those rows even when the caller only needed the exact
intersection cardinality.

Goal2269 adds a generic count-only surface:

- native ABI: `rtdl_optix_count_prepared_segment_pair_intersection`,
- Python API: `PreparedOptixSegmentPairIntersection.count(left_segments)`,
- native implementation: collect the same OptiX candidate pairs, preserve the
  same exact host refinement and duplicate-pair suppression, and return only a
  scalar count.

## Boundary

This is a generic segment-pair primitive, not an LSI-specific primitive and
not a RayJoin-specific primitive. It does not add app-specific logic to the engine.
The exact count remains bounded by the current candidate download plus host
refinement design. It avoids final `RtdlSegmentPairIntersectionRow` allocation
and Python row conversion, but it is not a pure device-resident continuation
yet.

## Expected Measurement

This report records the implementation contract. Pushed-commit pod timing must
be recorded separately before making a measured performance claim. The useful
comparison is:

- `prepared.run(left_segments)` row-return witness path,
- `prepared.count(left_segments)` exact scalar-count path,
- same prepared right-side scene,
- same input stream,
- parity: `prepared.count(...) == len(prepared.run(...))`.
