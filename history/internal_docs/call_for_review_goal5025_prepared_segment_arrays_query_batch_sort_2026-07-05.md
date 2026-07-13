# Call For Review - Goal5025 Prepared Segment Arrays and Query-Batch Sort Probe

Please review:

- `history/internal_docs/goal5025_prepared_segment_arrays_and_query_batch_sort_result_2026-07-05.md`
- `history/internal_docs/rtdl_goal5025_query6_prepared_right_points_segments_warmfix_top4.json`
- `history/internal_docs/rtdl_goal5025_query6_prepared_right_points_segments_bitonic_rerun_top4.json`
- `history/internal_docs/rtdl_goal5025_query6_prepared_right_points_segments_native_lexsort_top4.json`

Baseline comparison artifacts:

- `history/internal_docs/rtdl_goal5024_query6_baseline_top4.json`
- `history/internal_docs/rtdl_goal5024_query6_prepared_right_points_top4.json`

## Requested Verdict

`approve_goal5025_query_batch_segment_array_reuse_win__native_lexsort_modest`

## Review Questions

1. Is `--prepared-query-batch-segment-arrays` correctly scoped to the app-layer prepared query-batch route, without RTDL core/native changes?
2. Does the Numba warmup signature fix correctly address a real first-batch carrier JIT mismatch (`uint32` faces in the real route versus prior `int64` warmup)?
3. Do the POD artifacts support the claim that reprojection moved from about `0.16-0.17s` per batch to about `0.0015-0.0034s` per batch?
4. Do the six-batch body sums support a real query-batch win even after charging the added query-batch session preparation cost?
5. Are descriptor pair counts and LSI row counts stable enough to treat the optimization as structurally safe for this writer-free binary route?
6. Is the native lexsort result correctly framed as a modest opt-in win, not the main source of improvement?
7. Does the report preserve all regime boundaries: not cold CLI one-shot, not paper text, not author parity, not 10x, not full device-resident?
8. Should Goal5025 close with `completed_query_batch_segment_array_reuse_win__native_lexsort_modest_win`?
