# Goal5378 X-HD `-lb` Status-Machine Direction Decision

Date: 2026-07-10

Status:

```text
implemented_review_pending
```

Verdict label:

```text
authorize_generic_active_query_status_machine_design__explicit_lb_still_fail_closed
```

## Purpose

Goal5378 decides what to do after Goal5377 rejected the simple
`heavy-before-inline-prune` probe.

This is deliberately a decision/design goal, not another kernel tweak.  The
goal is to prevent the X-HD `-lb` work from drifting through small probes after
the evidence has already shown that the remaining gap is a state-machine
problem.

## Evidence Considered

### Goal5372 - Author Status-Machine Requirements

Goal5372 pins the author shader/status-machine semantics behind
`OffloadingSize`:

```text
payload in_q_idx;
dynamic cmin2/current-best;
kInit / kOffloading / kAborted status;
cmax2 MBR abort;
heavy-cell offload append;
miss queue;
loadBalanceProcessing sort/reduce feedback.
```

It records six required semantics for a valid next gate:

```text
active in_queue index namespace
dynamic per-source cmin2/current-best
cmax2 abort status
heavy-cell offload append
loadBalanceProcessing grouping
miss queue
```

### Goal5374 - Author Oracle

Goal5374 instruments the author implementation and produces a concrete
same-input oracle for Dragon -> AsianDragon with `lb=256`:

```text
ActiveInQueueSize               = 437645
StatusInitCount                 = 437645
OffloadingSize                  = 27133990
RawOffloadRowsBeforeSortReduce  = 27133990
StatusOffloadingAppendCount     = 27133990
RawOffloadRowsAuthorWidthBytes  = 217071920
StatusCmax2MbrAbortCount        = 0
StatusPointLoopEarlyBreakCount  = 0
```

This is the denominator RTDL must match before explicit author-compatible
`-lb` can be considered.

### Goal5375 - Current RTDL Surfaces Fail The Oracle

Goal5375 compares the existing RTDL candidates:

| Candidate | RTDL rows | Ratio vs author | Row parity |
|---|---:|---:|---|
| author-radius inline kind2 | 21,006,960 | 0.7741935484 | false |
| author-radius inline + global-bound kind2 | 21,006,960 | 0.7741935484 | false |
| author-radius no-inline raw kind2 | 304,981,889 | 11.2398467384 | false |
| old full-cover lb256 behavior gate | 24,508,120 | 0.9032258065 | false |

No current surface has row-count parity.

### Goal5376 - Telemetry Contract Is Useful But Not Support

Goal5376 adds a generic status-shaped telemetry contract.  It makes the current
RTDL surface observable and comparable, but it does not implement author-like
state restoration, miss queues, or load-balance feedback.

Key flags remain:

```text
status_candidate_contract_ready = true
author_lb_row_parity_established = false
explicit_lb_support_authorized = false
```

### Goal5377 - Heavy-Before-Inline-Prune Is A No-Go

Goal5377 adds a generic diagnostic `frontier_status_probe_mode` and tests
`heavy-before-inline-prune`:

| Route | RTDL kind2 rows | Ratio vs author | Row parity |
|---|---:|---:|---|
| default inline-current-best prune | 21,006,960 | 0.7741935484 | false |
| heavy-before-inline-prune | 304,981,889 | 11.2398467384 | false |

The probe jumps from the known under-counting surface to the known no-inline
over-counting surface.  It is not close to the author denominator.

## Decision

Continue toward full X-HD reproduction only through a **generic active-query /
status-machine design**, not through more local branch-order probes.

Selected direction:

```text
authorize_generic_active_query_status_machine_design
```

Explicit `-lb` remains fail-closed:

```text
explicit_lb_support_claimed = false
row_count_parity_claimed = false
same_denominator_memory_claimed = false
```

## Why This Is The Right Direction

The evidence has ruled out several smaller explanations:

```text
scalar radius alignment;
host materialization / sorting artifact;
raw kind2 counting;
existing RTDL global-bound early break;
classifying heavy/offload before inline-current-best prune.
```

The remaining mismatch is stateful:

```text
the author carries active in_queue indices;
the author updates/restores cmin2/current-best by queue row;
the author emits offload rows keyed by in_queue index;
the author has miss/completed/aborted status transitions;
the author feeds offload processing back into later queue state.
```

That shape is not X-HD-only if designed correctly.  It is a generic spatial
execution need:

```text
active queries;
per-query state;
frontier / offload rows;
miss rows;
completed rows;
continuation feedback.
```

Therefore the next useful work is a reusable RTDL execution contract, not a
paper-specific shortcut.

## Rejected Next Steps

Do not spend the next goal on:

```text
more scalar-radius tuning;
another raw-kind2 row-count probe;
treating existing global-bound as author cmax2 abort;
more heavy-before-inline-prune variants;
exposing explicit -lb from Goal5376/5377 telemetry;
mapping the 304,981,889 over-counting surface to author OffloadingSize.
```

## Planned Next Goals

### Goal5379 - Generic Active-Query Status-Machine CPU Reference

Purpose:

```text
Define a generic CPU/NumPy reference executor for active query state before
writing native code.
```

Minimum contract:

```text
query_row_id;
active_queue_index;
source_id;
current_best_sq;
status;
offload_cell_id;
miss_queue_row;
completed_nearest_row.
```

Required behavior:

```text
active-query state persists across continuation steps;
offload rows are keyed by active_queue_index;
miss rows remain explicit;
completed rows can update global max-nearest state;
row parity is reported only after comparison against an author oracle.
```

Important boundary:

```text
Goal5379 should be generic and local/CPU first.  It should not import author
X-HD code and should not claim explicit -lb support.
```

### Goal5380 - Native / OptiX Status-Machine Prototype

Only after Goal5379 pins the semantics.

Purpose:

```text
Implement/probe the generic active-query status-machine path in native/OptiX
and compare it directly to the Goal5374 author oracle.
```

Minimum comparison:

```text
raw_offload_rows_before_sort_reduce == 27133990;
raw_offload_rows_author_width_bytes == 217071920;
row_count_parity explicitly reported;
status/miss/abort counters reported.
```

### Goal5381 - Option Surface Or Fail-Closed Closeout

Only after Goal5380.

If row parity is achieved:

```text
consider a narrow app-owned explicit -lb compatibility surface and reopen
Figure 7 / Figure 11 only under same-denominator review.
```

If row parity is not achieved:

```text
keep -lb fail-closed and record full X-HD reproduction as blocked on author
status-machine semantics.
```

## POD Expectation

Goal5378 itself does not require POD.  It is a design/decision artifact.

Expected POD use:

```text
Goal5379:
  likely local only if it is a CPU/NumPy reference semantics goal.

Goal5380:
  requires POD for native / OptiX validation;
  must use scripts/current_pod_ssh.py;
  must sync changed files to /tmp/rtdl_goal5364;
  must rebuild OptiX before route probes;
  must compare to Goal5374.
```

Known POD:

```text
host = 213.173.108.24
port = 13502
gpu  = NVIDIA RTX 4000 Ada Generation
```

## Claim Boundary

Allowed:

```text
Goal5378 decides that the next valid implementation line is a generic
active-query/status-machine model.

Goal5378 records that explicit -lb remains fail-closed.

Goal5378 rejects further branch-order probes without a new execution model.
```

Not authorized:

```text
explicit -lb support;
row-count parity;
same-denominator memory parity;
Figure 7 reproduction;
Figure 11 reproduction;
author RT-core algorithm parity;
RTDL/author performance ratio;
exact paper dataset reproduction;
full X-HD paper reproduction.
```

## Validation

No runtime kernel validation is expected for this decision goal.  The artifact
is:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5378_lb_status_machine_direction_decision.json
```

This report is the human-readable decision record.

## Exit Label

```text
authorize_generic_active_query_status_machine_design__explicit_lb_still_fail_closed
```
