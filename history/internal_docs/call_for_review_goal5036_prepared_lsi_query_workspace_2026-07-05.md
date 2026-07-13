# Call For Review: Goal5036 Prepared LSI Query-Batch Workspace Warmup

Date: 2026-07-05

Please review:

```text
history/internal_docs/goal5036_prepared_lsi_query_workspace_result_2026-07-05.md
```

Requested verdict label:

```text
approve_goal5036_prepared_query_batch_lsi_workspace_warmup
```

## Review Questions

1. Does Goal5036 keep the implementation in the RayJoin paper app layer, without adding a RayJoin-specific RTDL core/native primitive?
2. Is the new `--prepared-query-batch-lsi-query-workspaces` route correctly scoped to prepared-base/query-batch usage, rather than cold CLI one-shot?
3. Does the implementation still recompute LSI pair-id device columns in measured rows, rather than replaying cached LSI results?
4. Is the A/B fair despite the POD native-lexsort PTX issue, given that both baseline and warmed routes use the same Numba CUDA sort fallback?
5. Do the POD artifacts support the performance claim: hot body 0.131156s -> 0.089189s and LSI phase 0.044176s -> 0.002034s?
6. Is the ~0.323s session-prepare cost disclosed clearly enough to prevent a misleading cold/fresh claim?
7. Are structural anchors sufficient for this optimization gate (`lsi_row_counts` and `descriptor_pair_counts` identical)?
8. Should this close as `completed_prepared_query_batch_lsi_workspace_warmup__query_many_hot_body_improved`, with remaining work moved to downstream floor/native-sort/toolchain targets?

## Files To Inspect

Implementation:

```text
Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py
tests/goal5036_prepared_lsi_query_workspace_test.py
```

Artifacts:

```text
history/internal_docs/rtdl_goal5036_baseline_numba_sort_1_top4.json
history/internal_docs/rtdl_goal5036_baseline_numba_sort_2_top4.json
history/internal_docs/rtdl_goal5036_baseline_numba_sort_3_top4.json
history/internal_docs/rtdl_goal5036_warmed_numba_sort_1_top4.json
history/internal_docs/rtdl_goal5036_warmed_numba_sort_2_top4.json
history/internal_docs/rtdl_goal5036_warmed_numba_sort_3_top4.json
```
