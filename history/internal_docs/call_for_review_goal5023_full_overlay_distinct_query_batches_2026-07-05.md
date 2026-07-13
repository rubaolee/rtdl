# Call For Review: Goal5023 Full Overlay Distinct Query Batches

Date: 2026-07-05

Please review:

- `history/internal_docs/goal5023_full_overlay_distinct_query_batches_result_2026-07-05.md`
- `history/internal_docs/rtdl_goal5023_full_overlay_distinct_chain_batches_top4.json`

## Requested Verdict

```text
approve_goal5023_full_overlay_query_batches_prepared_base_route__later_batches_under_0_8s__first_batch_visible
```

## Review Questions

1. Does Goal5023 actually run full overlay query batches, not LSI-only batches?
2. Does the chain batch builder preserve complete `DatasetArrays` structure
   rather than slicing only LSI segments?
3. Is it correct to classify this as a prepared-base same-domain query-batch
   route, not same-query replay?
4. Are the structural anchors and batch metadata sufficient for this bounded
   representative result?
5. Is the performance framing honest: first batch `3.835s`, later batches
   `~0.77-0.78s`, all-batch average `~1.795s`, not a single cherry-picked
   headline?
6. Does the report avoid cold CLI, paper-text, author parity, and broad 10x
   claims?
7. Does the route preserve RTDL as a generic system and RayJoin as an app?
8. Should the next work attack downstream PIP/reprojection/sort and the
   first-batch workspace cost, rather than more CPU hash/sort micro-work?
9. Should Goal5023 close with:

```text
completed_full_overlay_distinct_query_batches__prepared_base_later_batches_under_0_8s__first_batch_cost_still_visible
```
