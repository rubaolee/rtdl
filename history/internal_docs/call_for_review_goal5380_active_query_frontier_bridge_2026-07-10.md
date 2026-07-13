# Call For Review: Goal5380 Active-Query Frontier Bridge

Please strictly review Goal5380.

Files:

```text
history/internal_docs/goal5380_active_query_frontier_bridge_result_2026-07-10.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5380_active_query_frontier_bridge.json
src/rtdsl/active_query_status.py
src/rtdsl/__init__.py
tests/goal5380_active_query_frontier_bridge_test.py
```

Context:

```text
Goal5374 gives the author X-HD -lb oracle:
  ActiveInQueueSize              = 437645
  RawOffloadRowsBeforeSortReduce = 27133990
  RawOffloadRowsAuthorWidthBytes = 217071920

Goals5375-5377 prove existing RTDL row surfaces do not match that oracle.
Goal5378 selected the generic active-query/status-machine direction.
Goal5379 implemented the generic CPU/NumPy active-query status-machine
reference.

Goal5380 connects generic cell-MBR frontier row tables to that active-query
reference.
```

Expected verdict labels:

```text
approve_goal5380_active_query_frontier_bridge
revise_goal5380_active_query_frontier_bridge
block_goal5380_if_lb_support_is_overclaimed
```

Review questions:

1. Is `active_query_status_from_frontier_row_table_numpy_columns` genuinely
   app-neutral, or does it encode X-HD/Hausdorff/paper semantics?

2. Does the bridge correctly lower frontier row table columns into the
   Goal5379 active-query reference contract?

3. Do the tests prove real behavior, not just metadata?

4. Do the tests cover completed/offload/miss/aborted states and fail-closed
   invalid frontier inputs?

5. Are the public exports acceptable as RTDL generic system API surface?

6. Does the report correctly state that Goal5380 does not prove explicit
   author-compatible `-lb`, row-count parity, Figure 7/11, performance, or
   native backend completion?

7. Is the POD preflight evidence sufficient for the next native goal, without
   pretending that Goal5380 itself ran a native/POD row-parity probe?

8. Is the recommended next goal correct: native/OptiX active-query row-parity
   probe against the Goal5374 author oracle?

9. Are any claim boundaries missing?

10. Should Goal5380 be closed with:

```text
active_query_frontier_bridge_ready__native_author_oracle_probe_next
```

or should it be revised before proceeding?
