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

## Pod OptiX Evidence

Pushed commit:

```text
1a41a80 Route Jaccard through native bounded collection
```

Pod checkout:

```text
root@213.173.99.11 -p 39006
/workspace/rtdl_goal1292
```

The pod reset from GitHub `origin/main`, rebuilt OptiX, and validated the
focused routing tests:

```text
RTDL_OPTIX_LIB=/workspace/rtdl_goal1292/build/librtdl_optix.so PYTHONPATH=src:. python3 -m unittest tests.goal1318_v1_5_jaccard_native_collection_routing_test tests.goal1311_v1_5_jaccard_generic_fail_closed_collection_test
```

Result:

```text
Ran 11 tests in 0.007s
OK
```

Real OptiX app-route run:

```text
RTDL_OPTIX_LIB=/workspace/rtdl_goal1292/build/librtdl_optix.so PYTHONPATH=src:. python3 examples/rtdl_polygon_set_jaccard.py --backend optix --copies 2 --output-mode summary --collection-capacity 16
```

Observed:

- `candidate_row_count=4`
- `collection.native_collection=true`
- `collection.backend=optix`
- `collection.capacity=16`
- `collection.emitted_count=4`
- `collection.overflowed=false`
- `collection.complete_candidate_coverage=true`
- summary `intersection_area=10`, `left_area=26`, `right_area=22`,
  `union_area=38`, `jaccard_similarity=0.2631578947368421`

Note: the OptiX native bounded collection returned fewer positive candidates
than the local Embree run for the same 2-copy sample (`4` vs `6`), but exact
Jaccard scoring produced the same final summary. This is acceptable for this
routing slice because both native collectors produce complete positive
candidate coverage for the exact score path; candidate-count parity is not a
promotion criterion here.

## Boundary

This routes native bounded collection into the app, but does not promote
`polygon_set_jaccard` yet. Remaining work:

- Native score reduction after complete candidate coverage.
- Updated diagnostic wording/inventory once score reduction is implemented.
