# Goal5379 Generic Active-Query Status-Machine Reference Result

Date: 2026-07-10

Status:

```text
implemented_review_pending
```

Exit label:

```text
generic_active_query_status_machine_reference_ready__native_author_oracle_probe_next
```

## Purpose

Goal5379 implements the CPU/NumPy reference layer authorized by Goal5378.  The
goal is to pin a **generic active-query/status-machine contract** before any
native/OptiX attempt to match the author X-HD `-lb` oracle.

This is a system step, not an X-HD shortcut.  It introduces app-neutral state
rows and transition rows that can represent:

```text
active queries;
per-query current-best state;
offload rows;
miss rows;
completed nearest rows;
aborted rows;
continuation feedback into current-best state.
```

## What Was Implemented

New module:

```text
src/rtdsl/active_query_status.py
```

New public exports:

```text
ACTIVE_QUERY_STATUS_MACHINE_CONTRACT
ACTIVE_QUERY_STATUS_KIND_CODES
ACTIVE_QUERY_ABORT_REASON_CODES
ACTIVE_QUERY_OFFLOAD_ROW_SCHEMA
ACTIVE_QUERY_TERMINAL_ROW_SCHEMA
active_query_status_machine_reference_numpy_columns
apply_active_query_feedback_numpy_columns
```

New focused test:

```text
tests/goal5379_active_query_status_machine_reference_test.py
```

New result artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5379_active_query_status_machine_reference.json
```

## Contract

Contract string:

```text
generic_active_query_status_machine_reference_v1
```

Primary function:

```text
active_query_status_machine_reference_numpy_columns(...)
```

It consumes:

```text
query_row_ids
active_queue_indices
source_ids
current_best_sq
current_best_item_ids
candidate_query_row_ids
candidate_cell_ids
candidate_min_sq
candidate_max_sq
candidate_work_counts
candidate_exact_best_sq
candidate_exact_item_ids
```

It emits:

```text
offload_rows
completed_rows
miss_rows
aborted_rows
updated_state
telemetry
metadata
```

The reference is intentionally CPU/NumPy.  It is the semantic baseline for a
future native path, not a performance backend.

## Continuation Feedback

Goal5379 also implements:

```text
apply_active_query_feedback_numpy_columns(...)
```

It applies continuation results back into active-query state by
`active_queue_index`:

```text
lower distance wins;
lower item id breaks equal-distance ties;
unknown queue ids fail closed.
```

This is important because the author X-HD `-lb` path is not a single-pass row
emitter.  It feeds load-balanced/offloaded work back into later current-best
state.  Goal5379 gives RTDL a generic reference shape for that feedback.

## Validation

Commands:

```text
py -m py_compile src/rtdsl/active_query_status.py src/rtdsl/__init__.py

py -m unittest \
  tests.goal5379_active_query_status_machine_reference_test \
  tests.goal5279_generic_heavy_offload_worklist_test \
  tests.goal5280_heavy_offload_non_xhd_consumer_gate_test
```

Observed:

```text
Ran 13 tests OK
```

The known local Windows Python warning appeared:

```text
Could not find platform independent libraries <prefix>
```

It did not affect test success.

## What The Tests Cover

The focused tests verify:

```text
completed row emission;
offload row emission keyed by active_queue_index;
miss row emission;
aborted row emission;
current-best feedback updates by active_queue_index;
lower-id tie-break for feedback;
overflow fail-closed with no partial output rows;
unknown feedback/candidate ids fail closed;
public surface exports;
source scan for app-neutrality.
```

The app-neutral scan checks that the new generic functions do not contain:

```text
xhd
x-hd
hausdorff
paper
hd_exec
figure
```

## Relationship To Existing Worklist Assets

Goal5279 and Goal5280 already introduced a generic heavy/offload worklist.
Goal5379 does not replace that.  It adds the missing **active-query state
transition layer** above the worklist shape:

```text
Goal5279/5280:
  generic active/miss/deferred work rows and queue telemetry.

Goal5379:
  active query state, transition rows, feedback into current-best state.
```

Together, these form the reference vocabulary needed before a native
author-oracle comparison.

## What This Does Not Prove

Goal5379 does not prove:

```text
explicit author-compatible -lb support;
row-count parity against author OffloadingSize;
same-denominator Figure 11 memory parity;
Figure 7 reproduction;
Figure 11 reproduction;
author RT-core algorithm parity;
performance improvement;
native backend completion;
exact paper dataset reproduction;
full X-HD paper reproduction.
```

## Why This Matters

Goal5377 showed that another local branch-order probe is not enough.  Goal5379
is the first implementation step toward the actual missing abstraction:

```text
generic active-query state carried across traversal / continuation boundaries.
```

This is the right direction because the author `-lb` denominator is controlled
by a state machine, not by a static row filter.

## Next Work

Recommended next goal:

```text
Goal5380 - native/OptiX active-query status-machine prototype against the
Goal5374 author oracle.
```

Goal5380 must compare directly against:

```text
author raw offload rows before sort/reduce = 27,133,990
author raw offload row bytes               = 217,071,920
author active in_queue size                = 437,645
```

Goal5380 must still keep:

```text
explicit_lb_support_claimed = false
row_count_parity_claimed = false
same_denominator_memory_claimed = false
```

until the native evidence proves otherwise and review approves the stronger
claim.
