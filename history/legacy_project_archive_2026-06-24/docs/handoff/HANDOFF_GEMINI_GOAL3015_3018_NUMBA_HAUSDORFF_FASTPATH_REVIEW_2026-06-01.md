# Handoff: Gemini Review for Goal3015-Goal3018

Please perform an independent read-only review of the current RTDL main branch
for the Goal3015-Goal3018 Hausdorff Numba fast-path work.

## Files to inspect

- `src/rtdsl/numba_partner_continuation.py`
- `src/rtdsl/partner_adapters.py`
- `src/rtdsl/v2_6_roadmap.py`
- `examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py`
- `docs/reports/goal3015_numba_block_nearest_rows_for_hausdorff_2026-06-01.md`
- `docs/reports/goal3016_hausdorff_numba_dense_vs_block_l4_pod_2026-06-01.md`
- `docs/reports/goal3016_hausdorff_numba_dense_vs_block_l4_pod_2026-06-01.json`
- `docs/reports/goal3017_numba_grouped_witness_no_host_sync_fast_path_2026-06-01.md`
- `docs/reports/goal3018_hausdorff_numba_no_host_sync_comparison_l4_pod_2026-06-01.md`
- `docs/reports/goal3018_hausdorff_numba_no_host_sync_comparison_l4_pod_2026-06-01.json`
- `tests/goal3015_numba_block_nearest_rows_for_hausdorff_test.py`
- `tests/goal3017_numba_grouped_witness_no_host_sync_fast_path_test.py`
- `tests/goal3018_hausdorff_numba_no_host_sync_comparison_l4_pod_test.py`

## Questions to answer

1. Is `pairwise_l2_sq_block_nearest_rows_2d` generic and app-agnostic enough
   for the Numba partner layer?
2. Is the explicit no-host-sync fast path safe as implemented: conservative by
   default, only enabled by app code for generated dense score rows, and clearly
   marked as unsafe for arbitrary user score rows unless the caller can prove
   the invariants?
3. Do the Goal3016 and Goal3018 L4 artifacts credibly show the timing shift:
   before no-host-sync, dense 1.349s vs block 1.416s; after no-host-sync, dense
   0.774s vs block 1.077s, with oracle parity and all claim flags false?
4. Does any code/report/artifact overclaim v2.6 release readiness, Numba
   speedup, RT-core speedup, whole-app speedup, true zero-copy, automatic
   partner selection, or app-specific native-engine logic?
5. What should be the next engineering step before calling this a recommended
   Hausdorff benchmark path?

## Output

Write the review to:

`docs/reviews/goal3019_gemini_review_goal3015_3018_numba_hausdorff_fastpath_2026-06-01.md`

Use one of these verdict values only:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Do not edit source files. If you run tests, record the exact command and result.
