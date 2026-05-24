# Goal2576 LibRTS Generic AABB Index Primitive Boundary

## Scope

LibRTS exposes a useful RTDL language/runtime pressure point: prepared
axis-aligned spatial indexing over boxes with point and box query predicates.
The benchmark must not inject a `LibRTS` native engine path. The app now lowers
its local grid/reference mode through an app-name-free primitive:

- `AABB_INDEX_QUERY_2D`
- `prepare_aabb_index_2d`
- `query_aabb_index_2d`

## Behavior

The primitive indexes 2-D AABBs and supports exact predicate refinement for:

- `point_contains`: indexed box contains query point.
- `range_contains`: indexed box contains query box.
- `range_intersects`: indexed box intersects query box.

The current implementation is a CPU reference uniform-grid broadphase with
exact predicate refinement. It records candidate checks, occupied cells,
candidate entries, query counts, and timing for the query phase.

## App Boundary

The LibRTS benchmark calls this primitive from `partner_grid_reference`; it no
longer owns a benchmark-local `PreparedGridIndex2D` implementation. That keeps
the reusable behavior in `src/rtdsl/aabb_index.py`, while the benchmark keeps
only paper semantics, fixture generation, mutation scenario, WKT interchange,
and authors-code comparison tooling.

This is intentionally not a native engine customization:

- no `LibRTS` native symbol;
- no paper-specific ABI;
- no OptiX or Embree implementation yet;
- no public speedup wording.

## Next Promotion Step

If the LibRTS benchmark continues to justify native work, promote
`AABB_INDEX_QUERY_2D` as a prepared Embree/OptiX primitive with the same
behavior contract:

- prepared indexed AABB state;
- point and box query streams;
- count-first result mode before row collection;
- optional mutation batches only after the static query path is stable;
- app-agnostic names and metadata.

## Verification

Focused tests:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal2574_librts_spatial_index_benchmark_app_test \
  tests.goal2575_librts_rtspatial_pod_evidence_test \
  tests.goal2576_generic_aabb_index_primitive_test
```

Result: 14 tests passed locally.
