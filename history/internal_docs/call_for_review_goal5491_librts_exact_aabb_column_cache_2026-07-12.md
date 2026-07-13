# Call For Review: Goal5491 LibRTS Exact AABB Column Cache

Please review the app-owned exact-input cache and POD reuse evidence. This goal
does not modify RTDL core; it tests whether the generic `Aabb2DColumns` API can
be used across repeated LibRTS runs without reparsing the 6.7GB WKT source.

## Files

- cache implementation:
  `Paper-reproduction-apps/librts-paper/build_exact_aabb_column_cache.py`
- repeat runner:
  `Paper-reproduction-apps/librts-paper/run_exact_point_contains_prepared_phase_columns_repeat.py`
- test: `tests/goal5489_librts_prepared_phase_repeat_test.py`
- cache build result:
  `Paper-reproduction-apps/librts-paper/results/librts_goal5491_lakes_cache_build.json`
- reuse result:
  `Paper-reproduction-apps/librts-paper/results/librts_goal5491_lakes_bz2_cache_repeat.json`
- report:
  `history/internal_docs/goal5491_librts_exact_aabb_column_cache_result_2026-07-12.md`

## Review questions

1. Does the cache preserve source SHA-256, row count, dtype, and schema, and
   reject stale source files?
2. Is cache publication atomic and is incomplete cache state rejected?
3. Does the POD result use the same exact input files and revalidate hashes
   before reusing author evidence?
4. Do all three cached queries match the author count `103189`?
5. Are cache load, one-time build, index prepare, query wall, and primitive
   phases kept separate?
6. Does the implementation remain app-owned while consuming a generic RTDL
   `Aabb2DColumns` contract?
7. Are end-to-end speedup, author ratio/parity, pointwise relation, Figure 6,
   full paper, device zero-copy, and Embree claims all closed?

## Expected answer shape

```text
Verdict: approve | revise
Blocking findings: ...
Required amendments: ...
Non-blocking notes: ...
```
