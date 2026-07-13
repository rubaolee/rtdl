# Call For Review - Goal5024 Prepared Right-Vertex Query Points for Query Batches

Please review:

- `history/internal_docs/goal5024_prepared_right_vertex_points_query_batches_result_2026-07-05.md`
- `history/internal_docs/rtdl_goal5024_prepared_right_vertex_points_top4.json`
- `history/internal_docs/rtdl_goal5024_query6_baseline_top4.json`
- `history/internal_docs/rtdl_goal5024_query6_prepared_right_points_top4.json`
- `history/internal_docs/rtdl_goal5024_bbox_filter_vertex_pip_top4.json`

## Requested Verdict

`approve_goal5024_prepared_right_vertex_query_batch_win__bbox_filter_no_go`

## Review Questions

1. Did Goal5024 correctly reject bbox filtering after finding that bbox-excluded points can still have nonzero face ids and that descriptor pair counts changed?
2. Is the implemented `--prepared-query-batch-right-vertex-points` route a RayJoin app-layer query-batch optimization, not an RTDL core or native RayJoin-specific primitive?
3. Does the compatibility diagnostic justify reusing the prepared right vertex query-point buffer across distinct left chain batches under the same global scale bounds?
4. Do the 3-batch numbers show a body-time improvement but only near break-even after charging the added one-time session preparation?
5. Do the 6-batch numbers support a real query-many win after charging the added session preparation cost?
6. Are the descriptor pair counts stable between baseline and prepared-right-vertex runs for the 6-batch comparison?
7. Does the report keep the regime boundary clear: not cold CLI, not paper text, not author parity, not same-query replay?
8. Should Goal5024 close with `completed_prepared_right_vertex_points_query_batch_win__bbox_filter_no_go`?
