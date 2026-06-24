# Phoenix V3 LibRTS AABB Count-Cache Focused Evidence

Date: 2026-06-22
Status: `focused_generic_runtime_fix_validated_not_release`

## Summary

This packet records a focused Phoenix V3 runtime fix for the remaining
post-Barnes-Hut app-geomean regression in the serious V2.14 vs V3 evidence:
`librts_spatial_index`.

The fix is generic runtime work:

- `src/rtdsl/aabb_index.py`
  - `EmbreeAabbIndex2D.count()` now reuses packed query records for repeated
    prepared count queries.
  - `operation="all"` reuses one packed point-query object and one packed
    box-query object across the native point/range count calls.
  - cache stats expose count-query hits/misses beside the existing range-row
    query cache.
- `src/rtdsl/embree_runtime.py`
  - `pack_aabb_point_queries_2d()` accepts already packed 2-D point queries.
  - `PreparedEmbreeAabbIndex2D` caches optional native symbols and declares
    `supports_packed_aabb_queries = True`.
- `tests/v3_phoenix_aabb_prepared_query_cache_test.py`
  - Adds a regression test proving repeated Embree native count calls reuse the
    same packed query records.

This is not a LibRTS-specific engine and does not authorize V3 release or broad
V3-over-V2 speedup wording.

## Evidence

Remote patch validation:

```text
pod: root@213.173.108.14 -p 11592
hardware: NVIDIA RTX 4000 Ada Generation
patched current hashes:
  src/rtdsl/aabb_index.py 7538ab41145a234cc5b49b56cf1346a7b6bcd0f1efc5fd6534e4c76ba4e25261
  src/rtdsl/embree_runtime.py e3a7da88c30d7d88f9278cb3bd0dc8acfbf5007575a909b7f21c66809e1a0051
  tests/v3_phoenix_aabb_prepared_query_cache_test.py 131fee2171d9933d830384cd70144940b3562c2cf84ee0ed8dd194c1cb1ab735
```

Remote targeted tests:

```text
PYTHONPATH=src python3 -m unittest \
  tests.v3_phoenix_aabb_prepared_query_cache_test.V3PhoenixAabbPreparedQueryCacheTest.test_embree_native_count_reuses_packed_query_records \
  tests.v3_phoenix_aabb_prepared_query_cache_test.V3PhoenixAabbPreparedQueryCacheTest.test_embree_native_reuses_range_query_records_without_caching_results \
  tests.goal4340_embree_native_aabb_index_route_test.Goal4340EmbreeNativeAabbIndexRouteTest.test_high_level_embree_aabb_uses_native_batch_when_available \
  tests.goal4348_embree_aabb_rows_test

Ran 5 tests in 0.003s
OK
```

Focused run artifacts:

```text
docs/rebuild/v3/evidence/phoenix_v3_librts_aabb_count_cache_focused_20260622_140223/
docs/rebuild/v3/evidence/phoenix_v3_librts_aabb_count_cache_repeat9_20260622_140402/
```

Both runs use the serious `goal2626_large` LibRTS row on the same pod, not toy
data.

## Focused Results

Metric:
`run_phases.query_median_sec`

Original serious run:

| backend | V2.14 sec | old V3 sec | old V3 vs V2.14 |
| --- | ---: | ---: | ---: |
| Embree | 0.024497 | 0.028180 | 0.869x |
| OptiX | 0.222862 | 0.220582 | 1.010x |

Focused repeat=3 after patch:

| backend | V2.14 sec | patched V3 sec | patched V3 vs V2.14 |
| --- | ---: | ---: | ---: |
| Embree | 0.033503 | 0.019655 | 1.705x |
| OptiX | 0.218444 | 0.210282 | 1.039x |

Focused repeat=9 after patch:

| backend | V2.14 sec | patched V3 sec | patched V3 vs V2.14 |
| --- | ---: | ---: | ---: |
| Embree | 0.041349 | 0.021499 | 1.923x |
| OptiX | 0.225418 | 0.246957 | 0.913x |

Interpretation:

- The Embree AABB count-only regression is fixed by a generic prepared-query
  packing/symbol-cache improvement.
- The OptiX AABB index row is not explained by this fix. It was near parity in
  the original serious run, slightly positive in focused repeat=3, and negative
  in repeat=9. Treat it as unstable/inconclusive until separately profiled.
- Therefore this packet supersedes the old LibRTS Embree regression diagnosis,
  but it does not close OptiX AABB route analysis.

## Release Impact

This improves Phoenix V3's generic runtime story, but it does not authorize
release:

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
```

Remaining row-level losses after the Barnes-Hut and LibRTS Embree fixes still
include Spatial RayJoin LSI OptiX and RTNN clustered Embree rows, and the
full all-app release gate must be rerun after enough generic fixes accumulate.

## Decision Audit

Decision: accept the Embree AABB count-cache patch as a valid focused generic
runtime fix, but do not claim the LibRTS OptiX row is solved.

1. Was I foolish? No for this decision.
2. If yes, what actions made the decision foolish? None. The foolish action
   would have been reporting the repeat=3 1.705x/1.039x result as complete
   LibRTS victory without the repeat=9 stability check.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes: skip LibRTS after Barnes-Hut and chase Spatial RayJoin. That would
   leave the only remaining sub-0.95 app geomean unexplained.
4. Can I now try a different path that actually solves the problem? Yes. Move
   next to Spatial RayJoin LSI OptiX or RTNN clustered Embree, while keeping
   OptiX AABB index instability as a separate open route-analysis item.

