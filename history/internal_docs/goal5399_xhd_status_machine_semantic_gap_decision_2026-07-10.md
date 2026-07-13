# Goal5399 - X-HD Status-Machine Semantic Gap Decision

Date: 2026-07-10

## Goal

Goal5399 decides what to do after Goal5398 showed that RTDL's generic native v7
active-query status stream still does not match the X-HD author explicit `-lb`
trace.

This is a decision goal, not an implementation goal.

## Inputs

Author oracle:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5387_author_trace_v2_execution.json
```

RTDL native v7 result:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5398_native_v7_status_stream_parity_gate_pod.json
```

Relevant source surfaces:

```text
Paper-reproduction-apps/x-hd-paper/scripts/instrument_xhd_author_lb_status_trace_v2.py
src/native/optix/rtdl_optix_workloads.cpp
src/rtdsl/active_query_status.py
```

## Evidence Summary

Goal5398 full-public gate:

```text
active_query_count_parity = true
author active queries = 437645
RTDL v7 active queries = 437645

row_count_parity = false
author raw offload rows = 27133990
RTDL v7 status rows = 2600727
RTDL / author row ratio = 0.09584756978240207

hash_parity = false
author raw hash = 4333109858711462591
RTDL v7 raw hash = 12842101464127179321

explicit -lb support = fail-closed
```

Goal5387 author trace v2:

```text
status_count_init = 437645
status_count_offloading = 27133990
status_count_aborted = 0
status_count_miss = 0
status_count_completed = 0
cmax2_mbr_abort_count = 0
point_loop_early_break_count = 0
load_balance_feedback_update_count = 294

cmin2_initial_hash = 5369460447013261471
cmin2_after_ray_hash = 10400538358226239013
cmin2_after_load_balance_hash = 10400538358226239013
```

## Author Semantics

The author trace is an app-owned instrumentation of the external author source,
but it exposes the decisive status-machine shape:

```text
if np_in_cell > processing_threshold:
    append in_q_idx to offloading_point_ids
    append mbr_id to offloading_cell_ids
    update_status(kOffloading)
    return
```

The trace is captured before load-balance reduce:

```text
raw_offload_rows_before_sort_reduce = offloading_size
raw_offload_row_hash = hash(offloading_point_ids, offloading_cell_ids)
raw_offload_row_sample_point_ids = [...]
raw_offload_row_sample_cell_ids = [...]
```

Then author calls load-balance processing:

```text
loadBalanceProcessing(
  offloading_point_ids,
  offloading_cell_ids,
  cmin2,
  ...
)
```

and records:

```text
load_balance_input_row_count = offloading_size
load_balance_group_count = 437645
load_balance_feedback_update_count = 294
cmin2_after_load_balance_hash
cmax2_after_load_balance
```

Important observation:

```text
cmin2_after_ray_hash == cmin2_after_load_balance_hash
load_balance_feedback_update_count = 294
```

For this specific public Dragon -> AsianDragon run, the load-balance stage
updates the global feedback bound only 294 times and does not change the sampled
cmin2 hash relative to after-ray. The status-row denominator, however, is
already determined before that load-balance stage: it is the raw shader
offload append stream.

## Current RTDL v7 Semantics

The native v7 stream is attached to the existing RTDL cell-MBR frontier /
inline-nearest path:

```text
intersection:
  compute min_sq
  optionally prune with payload/current-best or initial-best
  report intersection

any-hit:
  classify cell as:
    kind=1 inline
    kind=2 offload
    kind=3 pruned
  optionally inline-nearest scan
  optionally drop pruned rows
  emit frontier row
  emit status row from the same emitted-row point
```

This means RTDL v7 status rows inherit the denominator of the current generic
frontier route. It does not emit the author raw shader offload append stream.

In the Goal5398 run:

```text
transition_phase_codes = {2: 2600727}
status_codes = {2: 2600727}
current_best_before_finite_count = 2600727
current_best_after_finite_count = 2600727
```

This is useful generic telemetry, but it is not author `-lb` parity.

## Root Cause

The mismatch is semantic, not merely mechanical.

The author explicit `-lb` stream is:

```text
raw shader offload append rows before load-balance reduce, generated from
author traversal state and threshold semantics.
```

The current RTDL v7 stream is:

```text
status rows emitted at RTDL's existing generic frontier row emission point,
after RTDL's current best / initial-best pruning and inline-nearest route shape.
```

Therefore:

```text
RTDL v7 row count = 2600727
author row count = 27133990
```

The factor is too large for a simple hash-order or column-name bug.

## Rejected Paths

### Rejected: Hard-code 62 rows per active query

Reason:

```text
62 is an observed denominator for this workload, not a generic invariant.
Hard-coding it would be app-specific and would not match row hash/samples.
```

### Rejected: Remap existing v7 rows

Reason:

```text
RTDL v7 has only 2600727 rows. The missing 24533263 rows cannot be recovered
by renaming or sorting existing rows.
```

### Rejected: Claim explicit `-lb` from scalar correctness

Reason:

```text
The directed-HD scalar route is strong, but explicit -lb is a distinct author
status-stream / load-balance option. Scalar match does not prove row-stream
parity.
```

### Rejected: Add an X-HD-only native primitive

Reason:

```text
RTDL is a general spatial language/system. Native/core code must expose generic
active-query traversal and continuation state, not paper option names or figure
semantics.
```

## Decision

Authorize one more implementation line, but only if it is framed as a generic
active-query status-state machine, not as an X-HD-specific shortcut.

Decision label:

```text
authorize_goal5400_generic_active_query_status_state_machine_spike
```

The reason to continue is that the missing capability is still plausibly a
generic RTDL feature:

```text
traversal emits active-query offload rows;
continuation/reducer processes offload rows;
continuation feeds back per-query/global current-best state;
the next traversal or summary can compare row streams and feedback counts.
```

This is exactly the kind of traversal/continuation boundary that RTDL as a
language needs to own generically.

However, the authorization is bounded:

- no X-HD option names in RTDL core/native symbols;
- no Figure 7/Figure 11 claims until row/hash parity passes;
- no performance claims until denominator and phase boundaries align;
- no hard-coded fanout;
- no full paper reproduction claim from the status-machine spike alone.

## Goal5400 Proposed Scope

Goal5400 should be a spike with a fail-closed exit.

### Minimum generic API shape

```text
collect_active_query_offload_status_stream_3d_optix(
  query points,
  target cell MBRs,
  point-count threshold,
  initial/current best state mode,
  row capacity,
  emit_offload_before_continuation=True,
)
```

The name above is descriptive. Final naming may differ, but must remain
app-neutral.

### Required outputs

At minimum:

```text
active_queue_index
query_row_id
source_id
cell_id
status_code
transition_phase_code
current_best_before_sq
current_best_after_sq
```

Telemetry:

```text
active_query_count
raw_offload_row_count
raw_offload_row_hash
status_count_offloading
status_count_aborted
status_count_miss
status_count_completed
feedback_update_count_or_not_applicable
overflowed
```

### Required gates

1. Synthetic non-X-HD test:

```text
small generic active-query fixture;
known offload rows;
known feedback behavior or explicit not-applicable;
no X-HD strings in core/native public symbols.
```

2. Bounded X-HD app gate:

```text
small source-limit;
compare denominator and hash/sample where possible;
do not claim full parity.
```

3. Full Dragon -> AsianDragon gate:

```text
compare against Goal5387:
  active_query_count = 437645
  author rows = 27133990
  author hash = 4333109858711462591
  feedback_update_count = 294
```

### Exit labels

Success:

```text
generic_status_state_machine_matches_author_lb_trace_v2
```

Partial / continue:

```text
generic_status_state_machine_reduces_gap_but_row_or_hash_mismatch_remains
```

No-go:

```text
generic_status_state_machine_no_go__explicit_lb_line_stop_recommended
```

## If Goal5400 Fails

If a generic status-state machine cannot close the denominator/hash gap without
embedding X-HD-specific semantics, then the project should stop the explicit
`-lb` trace line and close X-HD at:

```text
Level-B public directed-HD scalar correctness;
generic nearest/witness/reduction extraction;
documented algorithm gap for explicit author -lb.
```

That would be a scientifically honest endpoint, but it would not satisfy full
paper reproduction or Figure 7/11 reproduction.

## Claim Boundary

Allowed summary:

```text
Goal5399 decides that Goal5398 exposed a semantic status-machine gap rather
than an ABI or row-remap bug. It authorizes a bounded Goal5400 spike to build a
generic active-query status-state machine that can be tested against the
Goal5387 author trace v2 oracle, while keeping explicit -lb fail-closed until
row/hash parity is proven.
```

Forbidden summaries:

```text
RTDL supports X-HD -lb.
RTDL matches author OffloadingSize.
RTDL reproduces Figure 7 or Figure 11.
RTDL full X-HD paper reproduction is complete.
The missing rows are solved by v7.
The next implementation may hard-code 62 rows per active query.
```

## Status

```text
completed_status_machine_gap_decision__authorize_generic_goal5400_spike__explicit_lb_still_fail_closed
```
