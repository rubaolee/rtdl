# Goal1318: Jaccard Native Bounded Collection Routing

Date: 2026-05-05

## Scope

`polygon_set_jaccard` now routes Embree and OptiX summary mode through the
native bounded polygon-pair collection wrappers when the current native symbols
are available:

- `collect_polygon_pair_candidates_bounded_embree()`
- `collect_polygon_pair_candidates_bounded_optix()`

If a stale native library does not export the symbol, the app falls back to the
existing Python LSI/PIP candidate-discovery path and records
`native_collection=false`.

## Behavior

- Default collection capacity is `left_polygon_count * right_polygon_count`.
- Explicit `--collection-capacity` is still honored.
- Native overflow raises before exact Jaccard scoring.
- Generic Jaccard summary now accepts already-collected native
  `COLLECT_K_BOUNDED` metadata and marks `collection.native_collection=true`.

## Local Evidence

Focused tests passed:

- Native collection metadata accepted by generic Jaccard summary.
- OptiX app route calls the native bounded collector.
- Stale-library fallback remains available.
- Native overflow stops before score reduction.
- Existing fail-closed collection tests still pass.

Local Embree real-library app run:

```text
RTDL_FORCE_EMBREE_REBUILD=1 PYTHONPATH=src:. python3 examples/rtdl_polygon_set_jaccard.py --backend embree --copies 2 --output-mode summary --collection-capacity 16
```

Result:

- `candidate_row_count=6`
- `collection.native_collection=true`
- `collection.backend=embree`
- summary `intersection_area=10`, `left_area=26`, `right_area=22`,
  `union_area=38`, `jaccard_similarity=0.2631578947368421`

## Boundary

This routes native bounded collection into the app, but does not promote
`polygon_set_jaccard` yet. Remaining work:

- Pod OptiX app-route validation from git state.
- Native score reduction after complete candidate coverage.
- Updated diagnostic wording/inventory once score reduction is implemented.
