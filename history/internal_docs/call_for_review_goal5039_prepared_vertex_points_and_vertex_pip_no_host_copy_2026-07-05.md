# Call For Review - Goal5039 Prepared Vertex Points And Vertex PIP No-Host-Copy

Reviewer: Claude or external reviewer

Please review:

- `history/internal_docs/goal5039_prepared_vertex_points_and_vertex_pip_no_host_copy_result_2026-07-05.md`
- implementation in `Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py`
- tests in `tests/goal5036_prepared_lsi_query_workspace_test.py`
- artifacts:
  - `history/internal_docs/rtdl_goal5039_left_vertex_points_1_top4.json`
  - `history/internal_docs/rtdl_goal5039_left_vertex_points_2_top4.json`
  - `history/internal_docs/rtdl_goal5039_left_vertex_points_3_top4.json`
  - `history/internal_docs/rtdl_goal5039_left_vertex_points_4_top4.json`
  - `history/internal_docs/rtdl_goal5039_left_vertex_points_5_top4.json`
  - `history/internal_docs/rtdl_goal5039_vertex_nohost_1_top4.json`
  - `history/internal_docs/rtdl_goal5039_vertex_nohost_2_top4.json`
  - `history/internal_docs/rtdl_goal5039_vertex_nohost_3_top4.json`
  - `history/internal_docs/rtdl_goal5039_vertex_nohost_4_top4.json`
  - `history/internal_docs/rtdl_goal5039_vertex_nohost_5_top4.json`

Requested verdict label:

```text
approve_goal5039_prepared_query_batch_per_batch_hot_body_47ms__six_batch_sum_329ms__vertex_pip_no_host_copy_win
```

## Review Questions

1. Is `--prepared-query-batch-left-vertex-points` correctly scoped to prepared LSI base sessions with explicit query batches and point-location device face columns?

2. Does the implementation avoid adding RTDL core/native RayJoin-specific overlay semantics?

3. Is it valid for the prepared query-batch route to prepare left vertex point sets once per distinct batch and reuse them in the measured hot body?

4. Is it valid for vertex PIP to use `copy_host=not device_resident_carrier_enabled` when the device-resident binary carrier consumes device face-id columns?

5. Do the tests guard the two intended implementation properties: left vertex point preparation exists, and vertex PIP does not force `copy_host=True` in the device-resident carrier path?

6. Do the artifacts support the claimed per-query-batch hot-body improvement from about `0.062045s` to about `0.046956s`?

7. Do the artifacts support the vertex PIP improvements:

```text
map0: 0.004890s -> 0.001095s
map1: 0.012757s -> 0.003932s
```

8. Are the structural anchors stable across Goal5038 and Goal5039 routes?

9. Does the report preserve the regime boundary: prepared query-batch writer-free binary route only; no cold CLI, no paper-text, no author-parity claim?

10. Is the report correct to state that `0.046956s` is a per-query-batch median, not the whole top4 six-batch runtime?

11. Do the artifacts support the corrected whole-top4 prepared binary six-batch sum of about `0.328842s`?

12. Should Goal5039 close with `completed_prepared_query_batch_per_batch_hot_body_47ms__six_batch_sum_329ms__vertex_pip_no_host_copy_win`?

13. What should be the next target: remaining carrier construction, descriptor consumer, sort/reprojection, or stop and stabilize this prepared query-batch result?
