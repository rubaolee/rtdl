# Call For Review - Goal5038 Device Carrier Concurrent Side Append

Reviewer: Claude or external reviewer

Please review:

- `history/internal_docs/goal5038_device_carrier_concurrent_side_append_result_2026-07-05.md`
- implementation in `Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py`
- tests in `tests/goal5034_device_carrier_atomic_append_test.py`
- artifacts:
  - `history/internal_docs/rtdl_goal5038_baseline_1_top4.json`
  - `history/internal_docs/rtdl_goal5038_baseline_2_top4.json`
  - `history/internal_docs/rtdl_goal5038_baseline_3_top4.json`
  - `history/internal_docs/rtdl_goal5038_baseline_4_top4.json`
  - `history/internal_docs/rtdl_goal5038_baseline_5_top4.json`
  - `history/internal_docs/rtdl_goal5038_concurrent_1_top4.json`
  - `history/internal_docs/rtdl_goal5038_concurrent_2_top4.json`
  - `history/internal_docs/rtdl_goal5038_concurrent_3_top4.json`
  - `history/internal_docs/rtdl_goal5038_concurrent_4_top4.json`
  - `history/internal_docs/rtdl_goal5038_concurrent_5_top4.json`
  - `history/internal_docs/rtdl_goal5038_final_direct_concurrent_1_top4.json`
  - `history/internal_docs/rtdl_goal5038_final_direct_concurrent_2_top4.json`
  - `history/internal_docs/rtdl_goal5038_final_direct_concurrent_3_top4.json`
  - `history/internal_docs/rtdl_goal5038_final_direct_concurrent_4_top4.json`
  - `history/internal_docs/rtdl_goal5038_final_direct_concurrent_5_top4.json`

Requested verdict label:

```text
approve_goal5038_prepared_query_batch_hot_body_62ms__concurrent_side_append_win
```

## Review Questions

1. Is `--device-carrier-concurrent-sides` correctly scoped to the writer-free binary descriptor route, where carrier row order is not a paper-text ordering contract?

2. Does the implementation avoid adding RTDL core/native RayJoin-specific overlay semantics?

3. Is it valid to use CUDA atomic append into shared `counters` across two side append kernels launched on separate streams for this binary descriptor route?

4. Do the artifacts support the claimed prepared query-batch hot-body improvement from about `0.070311s` to about `0.062045s`?

5. Do the artifacts support the carrier construction improvement from about `0.024918s` to about `0.017564s`?

6. Are the structural anchors stable across baseline, concurrent, and final routes?

7. Is the report correct to treat direct carrier-prefix descriptor consumption as architecture cleanup, not a meaningful hot-body speedup?

8. Does the report preserve the regime boundary: prepared query-batch writer-free binary route only; no cold CLI, no paper-text, no author-parity claim?

9. Should Goal5038 close with `completed_prepared_query_batch_hot_body_62ms__concurrent_side_append_win`?

10. What should be the next target: remaining carrier construction, vertex PIP, descriptor consumer, or stop and stabilize?
