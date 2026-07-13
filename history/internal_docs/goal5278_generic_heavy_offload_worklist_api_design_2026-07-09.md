# Goal5278 - Generic Heavy-Offload Worklist API Design For X-HD Figure 11 Gap

Status:

```text
design_ready_review_pending
```

## Purpose

Goal5277 established that X-HD Figure 11 cannot be reproduced from the current
RTDL route because the memory denominators are not aligned:

```text
Author WL            = in_queue + miss_queue
Author WL Heavy Peak = peak heavy-cell offload queue
RTDL current WL      = generic frontier row-table capacity
RTDL Heavy Peak      = unavailable
```

Goal5278 defines the **generic system API direction** required to close that
gap without turning RTDL core into an X-HD app implementation.

This is a design goal only.  It does not implement the backend.

## Existing Generic Assets

RTDL already has several pieces near the needed shape:

```text
cell-MBR nearest frontier rows
  generic row schema for inline/offload/pruned nearest-state frontiers

aggregate-frontier rows
  generic source-offset + row-major frontier collection ABI

fixed-radius ranked summary partial rows
  device-resident partial rows plus bounded partner continuation proof

hd_exec-compatible memory accounting
  status-bearing app-owned bridge into author-shaped Running JSON
```

But none of these is yet an author-like heavy-cell offload queue:

```text
no generic queue API for heavy source x cell pairs
no peak queue telemetry for offloaded pairs
no in/miss queue denominator for X-HD Figure 11 WL
no backend contract tying offload rows to a continuation kernel
```

## Required System Primitive

The next system primitive should be generic:

```text
generic_heavy_offload_worklist
```

It should represent "frontier work that is too large / too expensive to finish
inside traversal and must be continued by a downstream executor."

It must not mention:

```text
xhd
hausdorff
paper
hd_exec
dragon
buddha
```

## Proposed Contract

### Inputs

```text
source ids / query ids
frontier primitive ids
frontier work-size estimates
frontier lower/upper distance bounds or user-defined cost fields
threshold policy
optional current-best state
```

### Output Columns

Minimum generic columns:

```text
work_source_id          int64
work_primitive_id       int64
work_begin_offset       int64
work_count              int64
work_kind_code          int64
work_cost_estimate      float64
lower_bound             float64
upper_bound             float64
```

For X-HD, the app can map these to author-like concepts:

```text
work_source_id    -> offloading_point_ids_
work_primitive_id -> offloading_cell_ids_
```

But the RTDL API remains generic.

### Queue Semantics

The primitive should expose two related but distinct concepts:

```text
active queue:
  rows that must be processed by a continuation executor.

miss / deferred queue:
  rows not resolved in the current traversal pass and carried to a later pass
  or a host/partner continuation.
```

For Figure 11 alignment, the memory telemetry must separately report:

```text
in_queue_bytes
miss_queue_bytes
heavy_offload_queue_current_bytes
heavy_offload_queue_peak_bytes
```

Only after these are implemented can RTDL claim same-denominator coverage for
author:

```text
WL
WL Heavy Peak
```

## Proposed Public API Shape

Python-facing sketch:

```python
worklist = rtdsl.build_heavy_offload_worklist_columns(
    source_ids=...,
    primitive_ids=...,
    work_counts=...,
    lower_bounds=...,
    upper_bounds=...,
    threshold_policy=...,
    current_best=...,
)

continued = rtdsl.run_offload_worklist_continuation(
    worklist,
    executor="numba" | "cupy" | "native",
    reducer=...,
)

telemetry = worklist.memory_telemetry()
```

Native-facing ABI sketch:

```text
rtdl_optix_collect_heavy_offload_worklist_3d(
    prepared_scene,
    query_points,
    current_best,
    threshold_policy,
    row_capacity,
    rows_out,
    row_count_out,
    overflow_out,
    telemetry_out
)
```

The exact symbol name can change, but it must stay app-neutral.

## Telemetry Contract

Telemetry schema:

```text
rtdl.generic.heavy_offload_worklist.memory_telemetry.v1
```

Required fields:

```text
in_queue_capacity
miss_queue_capacity
in_queue_bytes
miss_queue_bytes
heavy_offload_row_capacity
heavy_offload_current_rows
heavy_offload_peak_rows
heavy_offload_queue_current_bytes
heavy_offload_queue_peak_bytes
device_buffer_bytes_excluding_accel
native_accel_bytes_if_applicable
```

For X-HD Figure 11, `WL` can only be mapped after:

```text
WL = in_queue_bytes + miss_queue_bytes
```

and `WL Heavy Peak` can only be mapped after:

```text
WL Heavy Peak = heavy_offload_queue_peak_bytes
```

## Correctness Gates

### Gate 1 - Synthetic Generic Queue

Use a small synthetic workload that is not Hausdorff:

```text
source tasks
cell-like primitives
known cost thresholds
known active/deferred/offload rows
```

Verify:

```text
row schema
source offsets
overflow fail-closed behavior
peak telemetry
no app vocabulary in core
```

### Gate 2 - Non-X-HD Consumer

Use a facility/service-radius or batched nearest-neighbor continuation consumer
to prove the queue is not only X-HD-shaped.

### Gate 3 - X-HD Bounded Mapping

Only after Gates 1-2:

```text
map work_source_id / work_primitive_id to author-like offloading ids
compare queue counts to author OffloadingSize on a bounded same-input case
attach telemetry into RTDL.memory_accounting
```

### Gate 4 - Figure 11 Candidate

Only after Gate 3:

```text
try a Figure 11 row with same-source or exact inputs
report RTDL WL / WL Heavy Peak under same denominator
still avoid memory ratio unless all other fields and inputs align
```

## Claim Boundary

Allowed after this design:

```text
We have identified the generic system API needed to close the Figure 11 memory
denominator gap.
```

Not allowed:

```text
Figure 11 reproduced
author memory parity
memory ratio
X-HD-specific core primitive
heavy offload peak measured
native backend complete
```

## Implementation Sequence

Recommended goals:

```text
Goal5279: generic heavy-offload worklist schema + CPU/NumPy reference
Goal5280: non-X-HD consumer and fail-closed tests
Goal5281: native/POD telemetry ABI spike
Goal5282: X-HD bounded mapping to author OffloadingSize / Memory fields
Goal5283: Figure 11 same-denominator candidate row, if inputs permit
```

Each implementation goal must keep:

```text
app-neutral core naming
status-bearing memory fields
same-denominator flags
no ratio unless denominator and input identity align
```

## Decision

The path to Figure 11 reproduction is not another JSON formatting goal.  It is
a system API gap:

```text
generic heavy/offload worklist + peak telemetry
```

This is the next coherent RTDL system investment if the owner wants to keep
pursuing Figure 11.  Otherwise Figure 11 should remain explicitly closed as
not reproduced / denominator not aligned under the current route.
