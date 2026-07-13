# Goal5385 X-HD Author Trace V2 Spec Result

Date: 2026-07-10

Status:

```text
implemented_review_pending
```

Exit label:

```text
author_trace_v2_spec_ready__next_patch_author_or_native_stream
```

## Purpose

Goal5384 added a generic multi-round active-query status reference, but the
current author oracle from Goal5374 is still count-only.  It proves the author
denominator:

```text
ActiveInQueueSize              = 437645
RawOffloadRowsBeforeSortReduce = 27133990
RawOffloadRowsAuthorWidthBytes = 217071920
```

but it does not expose enough state to compare a multi-round RTDL stream:

```text
raw offload row identity
per-round cmin2 / current-best vectors
miss / completed status counts
loadBalanceProcessing feedback
cmax2 state before / after ray and load-balance
```

Goal5385 defines the stronger author trace v2 oracle needed before the next
native parity attempt.

## Files Added

Builder:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5385_author_trace_v2_spec.py
```

Artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5385_author_trace_v2_spec.json
```

Tests:

```text
tests/goal5385_author_trace_v2_spec_test.py
```

## Artifact Summary

Artifact schema:

```text
rtdl.paper_reproduction.xhd.goal5385.author_trace_v2_spec.v1
```

Proposed author trace v2 schema:

```text
rtdl.goal5385.author.lb_status_trace.v2
```

Required per-batch fields include:

```text
batch_index
iteration_index
radius
active_in_queue_size
cmax2_before_ray
cmax2_after_ray
cmax2_after_load_balance
cmin2_initial_hash
cmin2_after_ray_hash
cmin2_after_load_balance_hash
cmin2_sample_indices
cmin2_initial_samples
cmin2_after_ray_samples
cmin2_after_load_balance_samples
raw_offload_rows_before_sort_reduce
raw_offload_row_hash
raw_offload_row_sample_point_ids
raw_offload_row_sample_cell_ids
status_count_init
status_count_offloading
status_count_aborted
status_count_miss
status_count_completed
cmax2_mbr_abort_count
point_loop_early_break_count
load_balance_input_row_count
load_balance_group_count
load_balance_feedback_update_count
```

Optional large fields:

```text
raw_offload_point_ids_full
raw_offload_cell_ids_full
cmin2_initial_full
cmin2_after_ray_full
cmin2_after_load_balance_full
```

Dump policy:

```text
full raw rows are not required for the default gate;
hash + samples are required;
full raw rows are allowed only under an explicit flag.
```

Reason:

```text
Dragon->Asian lb256 has 27133990 raw offload rows.
A full uint32 pair dump is about 217071920 bytes before container overhead.
```

## Patch Scope

The artifact identifies author-only patch targets:

```text
src/rt/launch_parameters.h
src/rt/shaders/shaders_nn_uniform_grid.cu
src/hd_impl/hausdorff_distance_rt.h
```

Marker:

```text
RTDL_GOAL5385_LB_STATUS_TRACE_V2
```

Expected hook points:

```text
before ray launch: hash/sample initial cmin2 and record cmax2;
inside shader offload append: preserve raw point_id/cell_id stream for hash/sample;
after ray launch before loadBalanceProcessing: hash/sample cmin2 and queue rows;
inside/after loadBalanceProcessing: record group count and feedback update count;
after loadBalanceProcessing: hash/sample cmin2 and cmax2.
```

No RTDL core patch is authorized by this goal.

## Validation

Command:

```text
py -m unittest \
  tests.goal5385_author_trace_v2_spec_test \
  tests.goal5384_multiround_status_requirements_test \
  tests.goal5384_multiround_active_query_status_test \
  tests.goal5374_author_lb_status_trace_oracle_test
```

Observed:

```text
Ran 15 tests in 2.771s
OK
```

The known local Python warning appeared:

```text
Could not find platform independent libraries <prefix>
```

Tests still passed.

## Claim Boundary

Allowed:

```text
Goal5385 defines the author trace v2 schema required for the next parity gate.
The current Goal5374 oracle is count-only and insufficient for row/state parity.
The next author patch or native stream must report cmin2 hashes/samples,
offload row hashes/samples, status counts, and load-balance feedback counts.
```

Not allowed:

```text
author v2 trace implemented;
author v2 trace executed on POD;
explicit -lb support;
row-count parity;
Figure 7 reproduction;
Figure 11 reproduction;
author RT-core algorithm parity;
RTDL/author performance ratio;
exact paper dataset reproduction;
full X-HD paper reproduction.
```

## Interpretation

Goal5385 is an oracle-strengthening step.  It prevents the next implementation
from guessing which author state matters and prevents the project from using a
count-only oracle to support a broad `-lb` claim.

The next concrete goal should be one of:

```text
1. Implement the Goal5385 v2 patch in the external author tree and run it on
   the Dragon -> AsianDragon lb256 diagnostic.

2. Implement a native generic multi-round status stream in RTDL and compare it
   against the v2 fields if the author v2 oracle exists.

3. If neither is feasible, write a fail-closed explicit -lb closeout rather
   than continuing local prune-mode probes.
```
