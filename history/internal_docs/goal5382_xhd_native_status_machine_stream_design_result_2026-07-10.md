# Goal5382 X-HD Native Status-Machine Stream Design Result

Date: 2026-07-10

Status:

```text
implemented_review_pending
```

Exit label:

```text
native_status_machine_stream_design_ready__explicit_lb_still_fail_closed
```

## Purpose

Goal5381 proved that the current path:

```text
generic native cell-MBR frontier rows
-> active_query_status_from_frontier_row_table_numpy_columns
-> generic active-query status-machine reference
```

runs at full scale but does **not** match the Goal5374 author `-lb` offload
denominator.

Goal5382 converts that negative result into a concrete next-system contract:

```text
generic_active_query_status_stream_v1
```

This is a design / decision goal. It does not implement the native backend.

## Files Added

Builder:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5382_status_machine_stream_design.py
```

Artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5382_status_machine_stream_design.json
```

Tests:

```text
tests/goal5382_status_machine_stream_design_test.py
```

## Evidence Carried Forward

Author oracle from Goal5374:

```text
ActiveInQueueSize              = 437645
StatusInitCount                = 437645
OffloadingSize                 = 27133990
RawOffloadRowsBeforeSortReduce = 27133990
StatusOffloadingAppendCount    = 27133990
RawOffloadRowsAuthorWidthBytes = 217071920
StatusCmax2MbrAbortCount       = 0
StatusPointLoopEarlyBreakCount = 0
```

Goal5381 current bridge probe:

```text
active_query_count        = 437645
candidate_row_count       = 13129392
bridge_offload_row_count  = 2188225
author_offload_rows       = 27133990
row_count_parity          = false
row_ratio_rtdl_div_author = 0.08064516129032258
author_width_byte_parity  = false
```

Interpretation:

```text
The active-query count aligns, but the current native frontier stream plus
active-query bridge emits only about 8.06 percent of the author offload rows.
The current frontier stream is not the author-compatible raw status-machine
stream.
```

## Design Decision

Selected direction:

```text
define_generic_native_active_query_status_stream
```

Rejected directions:

```text
vectorize_cpu_active_query_bridge_first;
more_scalar_radius_or_branch_order_probes;
xhd_specific_native_lb_kernel.
```

Why:

```text
The bridge is slow, but the first failure is semantic row-denominator mismatch.
A faster bridge would still consume the wrong row stream.
```

## Required Native Stream Contract

Contract name:

```text
generic_active_query_status_stream_v1
```

Owner:

```text
rtdl_core_generic_contract
```

App semantics:

```text
none
```

Minimum columns:

```text
active_queue_index
query_row_id
query_point_id
cell_id
point_begin_offset
point_count
min_distance
max_distance
current_best_distance
status_code
```

Optional columns:

```text
nearest_item_id
current_best_item_id
iteration_index
continuation_round
```

Status codes:

```text
inline_resolved
offload
miss
completed
aborted
pruned
```

Required telemetry:

```text
active_query_count
raw_status_row_count
offload_row_count
miss_row_count
completed_row_count
aborted_row_count
peak_status_row_count
row_capacity
overflowed
```

Critical emission point:

```text
The native stream must emit raw active-query status transitions before the
current RTDL frontier output drops, collapses, sorts, uniques, or filters rows
in a way that loses offload-denominator information.
```

## X-HD App Mapping

The X-HD paper app may map:

```text
generic offload_row_count -> author OffloadingSize;
generic active_query_count -> author ActiveInQueueSize;
generic raw status rows -> author-width memory diagnostics;
```

But RTDL core must not own:

```text
author status enum names;
paper figure wording;
hd_exec JSON formatting;
dataset-specific tolerance decisions.
```

## Validation

Artifact generation:

```text
py Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5382_status_machine_stream_design.py
```

Observed:

```text
{"output": ".../xhd_goal5382_status_machine_stream_design.json", "status": "design_ready_review_pending"}
```

Focused regression:

```text
py -m unittest \
  tests.goal5382_status_machine_stream_design_test \
  tests.goal5381_active_query_frontier_bridge_probe_test \
  tests.goal5380_active_query_frontier_bridge_test \
  tests.goal5379_active_query_status_machine_reference_test \
  tests.goal5279_generic_heavy_offload_worklist_test \
  tests.goal5280_heavy_offload_non_xhd_consumer_gate_test
```

Observed:

```text
Ran 25 tests in 1.273s
OK
```

The local Python launcher also printed:

```text
Could not find platform independent libraries <prefix>
```

This is the known noisy Windows Python environment message and did not affect
the passing tests.

## What This Proves

Goal5382 proves that the project now has a concrete, app-neutral next contract
for closing the explicit `-lb` status-machine gap:

```text
generic_active_query_status_stream_v1
```

It also proves that the next native implementation must be evaluated against
the Goal5374 author oracle by row count, not by scalar HDResult alone.

## What This Does Not Prove

Goal5382 does not prove:

```text
explicit -lb support;
author OffloadingSize parity;
Figure 7 reproduction;
Figure 11 memory parity;
same-denominator performance ratio;
full X-HD paper reproduction;
native backend completion.
```

## Next Work

### Goal5383

Implement a generic native status-stream prototype or mode.

Required acceptance:

```text
focused synthetic non-X-HD status-stream test passes;
X-HD Dragon -> AsianDragon row-count probe reports active_query_count parity;
offload_row_count is compared to the Goal5374 author oracle;
no explicit -lb claim unless row_count_parity is true.
```

### Goal5384

Optimize bridge/runtime only after status-stream row-count semantics are
correct.

### Goal5385

Refresh the X-HD claim matrix and memory after the status-stream outcome.

## Claim Boundary

Allowed summary:

```text
Goal5382 defines the generic native active-query status-stream contract required
after Goal5381 showed the current frontier stream under-counts author offload
rows by about 12.4x. It authorizes a generic status-stream prototype next,
while keeping explicit -lb fail-closed until row-count parity is proven.
```

Forbidden summaries:

```text
Goal5382 implements explicit -lb.
Goal5382 matches author OffloadingSize.
Goal5382 reproduces Figure 7 or Figure 11.
Goal5382 completes X-HD paper reproduction.
Goal5382 adds an X-HD-specific native primitive.
```
