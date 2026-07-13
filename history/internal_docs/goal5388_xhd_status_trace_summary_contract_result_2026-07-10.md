# Goal5388 X-HD Status Trace Summary Contract Result

Date: 2026-07-10

## Verdict

```text
implemented_review_pending
```

## Summary

Goal5388 adds a generic RTDL status-trace summary API and connects it to the
Goal5387 author trace v2 oracle.

New system API:

```text
active_query_status_trace_summary_numpy_columns
ACTIVE_QUERY_STATUS_TRACE_SUMMARY_CONTRACT
```

Contract:

```text
generic_active_query_status_trace_summary_v1
```

Purpose:

```text
summarize generic active-query offload row tables with:
  row_count;
  status_count_offloading;
  active_query_count;
  deterministic raw_offload_row_hash;
  deterministic sample indices;
  selected sample columns.
```

This is intentionally app-neutral.  It does not encode X-HD, paper figures,
`hd_exec`, author option names, or author-specific status enums.

## Why This Was Needed

Goal5387 strengthened the author `-lb` oracle from count-only evidence to state
evidence:

```text
active_in_queue_size = 437645
raw_offload_rows_before_sort_reduce = 27133990
raw_offload_row_hash = 4333109858711462591
raw_offload_row_sample_point_ids = [11168, 210712, 437119]
raw_offload_row_sample_cell_ids = [2924, 17, 17]
cmin2 hashes / samples are present
loadBalanceProcessing feedback count = 294
```

Before Goal5388, current RTDL probes could mostly report row counts.  That is no
longer strong enough.  A future RTDL counterpart must be able to emit comparable
row-count plus hash/sample evidence from its actual raw status rows.

## Artifacts

Primary artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5388_status_trace_summary_contract.json
```

Implementation:

```text
src/rtdsl/active_query_status.py
src/rtdsl/__init__.py
```

Tests:

```text
tests/goal5388_active_query_trace_summary_test.py
tests/goal5388_status_trace_summary_contract_test.py
```

Builder:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5388_status_trace_summary_contract.py
```

## System API Behavior

The helper accepts a generic offload row table, selected hash columns, selected
sample columns, and optional active-query indices.  It produces:

```text
schema = rtdl.generic.active_query_status_trace_summary.v1
contract = generic_active_query_status_trace_summary_v1
app_semantics = none
row_count
status_count_offloading
active_query_count
raw_offload_row_hash
hash_columns
sample_indices
sample_columns
samples
```

The hash contract is:

```text
fnv1a_u64_over_selected_int64_columns
```

The default empty hash is:

```text
1469598103934665603
```

The helper fails closed on:

```text
missing hash/sample columns;
mismatched column shapes;
out-of-range sample indices;
empty hash column list.
```

## Connection To Goal5387

The Goal5388 artifact carries forward the Goal5387 target:

```text
schema = rtdl.goal5385.author.lb_status_trace.v2
active_in_queue_size = 437645
raw_offload_rows_before_sort_reduce = 27133990
status_count_offloading_append = 27133990
raw_offload_row_hash = 4333109858711462591
raw_offload_row_sample_point_ids = [11168, 210712, 437119]
raw_offload_row_sample_cell_ids = [2924, 17, 17]
cmin2_initial_hash = 5369460447013261471
cmin2_after_ray_hash = 10400538358226239013
cmin2_after_load_balance_hash = 10400538358226239013
load_balance_input_row_count = 27133990
load_balance_group_count = 437645
load_balance_feedback_update_count = 294
```

Current RTDL full probes are still insufficient:

```text
Goal5381 full bridge offload rows = 2188225
Goal5383 active-initial-best full bridge offload rows = 2188225
author v2 raw offload rows = 27133990
row_count_parity = false
hash/sample comparable = false
```

Therefore Goal5388 does not claim parity.  It creates the generic summary
surface the next native stream must use.

## Verification

Focused tests:

```text
py -m unittest \
  tests.goal5388_active_query_trace_summary_test \
  tests.goal5388_status_trace_summary_contract_test \
  tests.goal5384_multiround_active_query_status_test \
  tests.goal5387_author_trace_v2_execution_test
```

Result:

```text
Ran 15 tests in 2.895s
OK
```

Earlier expanded focused suite after adding the API:

```text
py -m unittest \
  tests.goal5388_active_query_trace_summary_test \
  tests.goal5384_multiround_active_query_status_test \
  tests.goal5387_author_trace_v2_execution_test \
  tests.goal5387_author_trace_v2_instrumentation_test

Ran 15 tests in 1.507s
OK
```

The local Python warning:

```text
Could not find platform independent libraries <prefix>
```

is noisy environment output.  Tests passed.

## Claim Boundary

Allowed:

```text
RTDL now has a generic status-trace summary helper for active-query offload rows.
Goal5388 connects that helper to the Goal5387 author trace v2 target.
The next native stream must emit row-count plus hash/sample comparable evidence.
```

Forbidden:

```text
explicit -lb support is not claimed;
RTDL row-count parity is not claimed;
RTDL hash/sample parity is not claimed;
Figure 7 reproduction is not claimed;
Figure 11 reproduction is not claimed;
same-denominator memory parity is not claimed;
author RT-core algorithm parity is not claimed;
author-vs-RTDL performance ratio is not claimed;
exact paper dataset reproduction is not claimed;
full X-HD paper reproduction is not claimed.
```

## Next Work

The next goal should run or implement a generic native/raw status stream that
emits the Goal5388 summary from actual RTDL status rows, then compares against
Goal5387:

```text
row_count;
status_count_offloading;
active_query_count;
raw_offload_row_hash or row samples;
miss/completed/aborted counts;
feedback update count.
```

If row-count parity remains false, `-lb` must remain fail-closed.
