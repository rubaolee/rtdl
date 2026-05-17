# Goal2279: Segment-Pair Direct-Index Refinement

Status: implemented locally; pod timing must be recorded separately.

## Purpose

Goals 2269-2278 established a prepared segment-pair intersection count path and
a cached prepared right-side lookup. Goal2276 showed a useful but modest gain on
the RayJoin-exported sparse LSI stream, leaving another generic overhead in the
exact-refinement stage: GPU candidate rows carried stable primitive IDs, so the
host refinement stage had to resolve both sides through hash maps before running
the exact segment predicate.

Goal2279 records direct primitive indices in each OptiX candidate row:

- `left_index`: the chunk-local probe index plus the launch `left_offset`;
- `right_index`: the hit primitive index reported by OptiX.

The row-producing and count-only exact-refinement paths now use those indices
directly when they are in bounds. The existing ID-based maps remain as defensive
fallbacks for invalid or future legacy candidate rows.

## Boundary

This is an app-agnostic internal optimization for the generic prepared
segment-pair intersection primitive. It is not an LSI-specific primitive, not a RayJoin-specific primitive, and not a new app continuation. It preserves:

- the same OptiX candidate traversal;
- the same exact CPU segment-intersection refinement;
- the same duplicate-pair suppression semantics, keyed by public segment IDs;
- the same row-producing and scalar-count public Python surfaces.

The direct index is stored as `uint32_t`, matching the existing launch and
primitive-index conventions. Extremely large left-side streams that would exceed
that index space fail closed instead of silently wrapping.

## Expected Measurement

This implementation report does not claim a speedup by itself. Pod timing should compare the RayJoin-exported 100k LSI stream against the Goal2276 cached-lookup baseline:

- Goal2276 raw-row median: `0.16502647660672665` seconds;
- Goal2276 scalar-count median: `0.15995669923722744` seconds.

Because the candidate row is wider after adding two indices, dense candidate
streams may see a copyback penalty. Sparse streams should be the best diagnostic
for whether the removed host hash lookups matter in practice.
