# Call For Review: Goal5021 Prepared LSI Base Session Result

Date: 2026-07-05

Please review:

- `history/internal_docs/goal5021_prepared_lsi_base_session_result_2026-07-05.md`
- `history/internal_docs/rtdl_goal5021_prepared_lsi_base_session_top4.json`

## Requested Verdict

```text
approve_goal5021_prepared_lsi_base_session_moves_lsi_cost__true_query_many_still_unproven
```

## Review Questions

1. Does Goal5021 correctly distinguish prepared LSI base-session measurement
   from full prepared operator replay?
2. Does the implementation build a fresh LSI query object for each measured
   route rather than reusing the same prepared query output?
3. Is it valid to say the route amortizes `grouped_range_ensure`, based on the
   measured rows where grouped range drops from about `1.048s` in warmup to
   about `0.0000005s` in measured rows?
4. Is the `1.031s` median writer-free result a valid prepared-base-session
   route number for top4 County x Zipcode?
5. Does the report avoid claiming cold CLI one-shot speedup, true query-many,
   author parity, or 10x?
6. Does the route preserve the generic-system boundary by using the public
   generic LSI prepared session rather than adding a RayJoin-specific core
   primitive?
7. Are the structural anchors (`lsi_row_count = 428322`,
   `descriptor_pair_count = 15014`) sufficient to proceed to the next
   query-many validation step?
8. Should the next goal be a true distinct-query-batch query-many test, rather
   than more sort/hash micro-work?
9. Should Goal5021 close with:

```text
completed_prepared_lsi_base_session_route__grouped_range_amortized__true_query_many_still_unproven
```
