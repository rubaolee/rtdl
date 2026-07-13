# Goal5369 - X-HD lb Queue-State Requirements Gate

Date: 2026-07-09

Status: `implemented_review_pending`

## Verdict Label

```text
lb_queue_state_requirements_ready__implementation_requires_queue_state_reconstruction_or_author_instrumentation
```

Exit label:

```text
lb_queue_state_requirements_ready__no_explicit_lb_support_yet
```

## Purpose

Goal5368 proved that RTDL's raw no-inline `kind2` frontier count under the
author scalar radius is not the author `OffloadingSize` denominator:

```text
author OffloadingSize       = 27,133,990
RTDL raw same-radius kind2  = 304,981,889
RTDL / author               = 11.239846738352892
```

Goal5369 turns that evidence into an executable requirements gate for the next
`-lb` implementation step.  It does not add explicit `-lb` support and does not
claim row-count parity.  Its job is to prevent another denominator-mismatched
implementation by naming the runtime state that must be aligned first.

## Files

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5369_lb_queue_state_requirements.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5369_lb_queue_state_requirements.json
tests/goal5369_lb_queue_state_requirements_test.py
```

## Input Evidence

Goal5369 consumes the current `-lb` evidence packet:

```text
xhd_goal5361_res4full_nonterminal_author_queue_gate.json
xhd_goal5364_lb_trace_gate_author_pair_contract.json
xhd_goal5365_rtdl_lb_counterpart_gate.json
xhd_goal5366_lb_denominator_reconciliation.json
xhd_goal5367_lb_author_radius_probe.json
xhd_goal5368_cell_mbr_raw_kind_count_telemetry.json
```

The scope remains Level-B temporary public input:

```text
input1 = /tmp/xhd_goal5234/data/dragon.ply
input2 = /tmp/xhd_goal5234/data/asian_dragon.ply
exact_paper_dataset_identity_proven = false
```

## What Is Already Known

### Author-like Queue Rows

Goal5361 proves RTDL can reproduce a bounded nonterminal radius queue trace for
the fields:

```text
Iteration
NumInputPoints
NumOutputPoints
Radius
CMax2
```

That is real progress, but it does not cover:

```text
OffloadingSize
raw offloading queue rows
per-source current-best / cmin2 vector
```

### Author `lb256`

Author reference for Dragon -> AsianDragon:

```text
HDResult       = 52.453487396240234
lb             = 256
Radius         = 79.2156982421875
OffloadingSize = 27,133,990
WL Heavy Peak  = 217,071,920 bytes
NumInputPoints = 437,645
```

### RTDL Behavior So Far

Goal5365 passes only a behavior-level gate:

```text
lb0 offload rows = 0
lb256 offload rows > 0
HDResult matches within tolerance
```

It does not prove row-count or byte parity.

Goal5367 aligns the scalar radius but still produces:

```text
author-radius materialized rows = 21,006,960
author-radius / author          = 0.7741935483870968
```

Goal5368 disables inline/materialization and counts raw kind2 rows:

```text
raw kind2 rows = 304,981,889
raw kind2 / author = 11.239846738352892
```

## Rejected Hypotheses

Goal5369 records four hypotheses that are now rejected:

```text
1. The memory gap is a byte formula mismatch.
   Rejected by Goal5366: author-width formula shape is aligned.

2. Scalar radius mismatch alone explains OffloadingSize.
   Rejected by Goal5367: author radius gives 21,006,960 rows, not 27,133,990.

3. Author OffloadingSize equals all materialized RTDL heavy/offload rows.
   Rejected by Goal5365/5367: 24,508,120 / 21,006,960 are both different.

4. Author OffloadingSize equals all raw same-radius kind2 rows.
   Rejected by Goal5368: raw kind2 is 304,981,889, about 11.24x author.
```

## Required Runtime State For The Next Gate

The next implementation cannot be "set lb=256 and count kind2 rows."  It must
align the author queue state:

```text
active_in_queue_indices
per_source_current_best_or_cmin2
per_iteration_radius_schedule
raw_offload_row_shape
author_width_memory_view
```

Current status:

```text
active_in_queue_indices          = missing_for_lb_trace
per_source_current_best_or_cmin2 = missing_for_lb_trace
per_iteration_radius_schedule    = partially_available
raw_offload_row_shape            = source semantics available, runtime rows missing
author_width_memory_view         = formula available
```

The locally missing author runtime state is:

```text
per-source cmin2/current-best vector for iteration 3
active in_queue_idx vector for iteration 3
raw author offloading rows before sort/reduce
per-batch offloading_size contributions inside iteration 3
```

## Next Gate Contract

Next gate name:

```text
author_queue_aligned_lb_trace
```

Allowed implementation options:

```text
1. Reconstruct the RTDL queue/current-best state through prior iterations, then
   run count-only raw offload telemetry under that state.

2. Instrument/regenerate author to expose the missing runtime queue/current-best
   arrays and raw offload rows, then compare RTDL against them.
```

Minimum acceptance criteria:

```text
same input pair
same preprocessing
same lb threshold = 256
same iteration radius = 79.2156982421875
active queue size = author NumInputPoints = 437,645
author OffloadingSize = 27,133,990
must report:
  active_in_queue_size
  current_best_state_source
  raw_offload_rows_before_sort_reduce
  author_width_bytes
  row_count_parity
```

Success exit:

```text
author_queue_aligned_lb_trace_denominator_compared
```

Failure exit:

```text
lb_trace_blocked_until_queue_state_or_author_instrumentation_available
```

## Validation

Commands:

```text
py Paper-reproduction-apps\x-hd-paper\scripts\build_xhd_goal5369_lb_queue_state_requirements.py
py -m py_compile Paper-reproduction-apps\x-hd-paper\scripts\build_xhd_goal5369_lb_queue_state_requirements.py
py -m unittest tests.goal5369_lb_queue_state_requirements_test
```

Result:

```text
Ran 3 tests OK
```

The local Python runtime printed the known environment warning:

```text
Could not find platform independent libraries <prefix>
```

Tests still passed.

## Claim Boundary

Allowed:

```text
Goal5369 defines the runtime state required before RTDL can make an author
queue-aligned explicit -lb denominator comparison.

The current evidence rejects scalar-radius-only and raw-kind2-only explanations
for author OffloadingSize.
```

Not authorized:

```text
explicit -lb support
row-count parity
same-denominator Figure 11 memory parity
Figure 7 reproduction
Figure 11 reproduction
author RT-core algorithm parity
RTDL/author performance ratio
exact paper dataset reproduction
full X-HD paper reproduction
```

## Next Work

The next implementation goal should choose one of two routes:

```text
Route A: reconstruct RTDL queue/current-best state through prior iterations and
run count-only raw offload telemetry under that state.

Route B: instrument/regenerate author to expose the missing per-source queue
state and raw offload rows, then compare RTDL against that stronger oracle.
```

No further `-lb` performance or memory claim should be made until that gate
reports a denominator comparison against author `OffloadingSize`.
