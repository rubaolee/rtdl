# Goal5279 - Generic Heavy-Offload Worklist Reference Result

Date: 2026-07-09

## Verdict

```text
implemented_review_pending
```

Goal5279 implements the first concrete system step after the Goal5278 design:
a generic heavy/offload worklist row schema plus a NumPy/CPU reference builder.
This is an RTDL system primitive, not an X-HD app primitive.

## Why This Goal Exists

Goal5277 showed that X-HD Figure 11 memory cannot be fairly reproduced under the
current route:

```text
Author WL             = in_queue + miss_queue
Author WL Heavy Peak  = peak heavy-cell offload queue
RTDL current WL       = generic frontier row-table capacity
RTDL current route    = no author-like heavy offload peak
```

Therefore the next useful step is not another X-HD JSON reshaping goal.  RTDL
needs a generic worklist/queue abstraction with peak telemetry that future native
backends can populate.

## Implemented Core API

Files changed:

```text
src/rtdsl/partner_continuations.py
src/rtdsl/__init__.py
```

New public constants:

```text
HEAVY_OFFLOAD_WORKLIST_CONTRACT = "generic_heavy_offload_worklist_v1"
HEAVY_OFFLOAD_WORKLIST_KIND_CODES = {"active": 1, "miss": 2, "deferred": 3}
HEAVY_OFFLOAD_WORKLIST_ROW_SCHEMA = (
  "work_source_id",
  "work_primitive_id",
  "work_begin_offset",
  "work_count",
  "work_kind_code",
  "work_cost_estimate",
  "lower_bound",
  "upper_bound",
)
```

New public reference helper:

```text
heavy_offload_worklist_numpy_columns(...)
```

The helper accepts app-neutral source / primitive / work-span columns and emits
selected heavy, miss, and deferred work rows.  It records telemetry for queue
capacity, queue bytes, offload row counts, peak rows, and offload queue bytes.

## Fail-Closed Behavior

If the selected row count exceeds `row_capacity`, the helper returns:

```text
overflowed = true
row_count = 0
heavy_offload_attempted_rows = attempted_count
all output columns empty
```

It does not emit partial rows.

## Evidence Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5279_generic_heavy_offload_worklist_reference_2026-07-09.json
```

Main fixture result:

```text
source ids:      [100, 101, 102, 103]
primitive ids:   [10, 11, 12, 13]
work counts:     [2, 9, 1, 7]
miss mask:       [false, false, true, false]
heavy_threshold: 5

emitted source ids:    [101, 102, 103]
emitted primitive ids: [11, 12, 13]
work kind codes:       [1, 2, 1]
row_count:             3
in_queue_capacity:     4
miss_queue_capacity:   1
heavy_offload_peak_rows: 3
heavy_offload_queue_peak_bytes: 48
```

## Genericity Proof

New tests include a non-X-HD "facility backlog" consumer.  It uses the same
worklist helper to select overloaded service-region work rows:

```text
service station ids -> demand region ids -> backlog work counts
```

This consumer does not call any X-HD wrapper and does not encode any Hausdorff
semantics.

## Validation

```text
py -m unittest \
  tests.goal5279_generic_heavy_offload_worklist_test \
  tests.goal5139_generic_nearest_state_frontier_api_test \
  tests.goal5140_generic_cell_mbr_traversal_abi_test

Ran 12 tests in 4.007s
OK
```

Note: the local Python launcher prints the known noisy line:

```text
Could not find platform independent libraries <prefix>
```

The tests still passed.

## What This Does Not Prove

This goal does not prove:

- X-HD Figure 11 reproduction;
- author memory parity;
- native backend completion;
- real POD queue peak telemetry;
- a performance improvement;
- exact paper dataset reproduction.

## Next Step

The next step is Goal5280:

```text
non-X-HD consumer + stronger genericity gate
```

Then Goal5281 should add the native/POD telemetry ABI spike so the generic
worklist can start producing real device-side peak evidence.
