# Goal4951 Compiled Path-Split Synthetic Gate

Date: 2026-07-04

Status: completed_pending_review

## Purpose

Goal4951 tests the Layer 3 route approved in
`goal4951_compiled_generic_path_split_materializer_goal_2026-07-04.md`:

> compile the generic path-split / grouped-record materializer itself, while
> keeping RayJoin text formatting app-owned.

This report covers only Gate A and Gate B:

- Gate A: source genericity.
- Gate B: non-RayJoin synthetic correctness.

It does not claim RayJoin public-sample correctness or performance. Those are
Gate C and Gate D, and remain unopened until this report passes review.

## Files Added

- `history/internal_docs/goal4951_compiled_path_split_spike.py`
- `tests/goal4951_compiled_path_split_spike_test.py`

No public API file was changed. No `src/rtdsl/**` runtime file was changed.
The implementation is an internal spike under `history/internal_docs`.

## Implementation Summary

The spike adds `assemble_compiled_path_split_records(...)`, an internal Numba
compiled implementation of the same neutral contract as
`rtdsl.output_assembly.assemble_grouped_path_split_records(...)`.

The contract accepts only generic path-split inputs:

- independent chain ids;
- point offsets/counts;
- x/y point columns;
- ordered split events;
- optional descriptor columns;
- optional validity mask;
- optional output group ids.

It emits a neutral `GroupedOutputRowBuffer` with:

- `group_id`;
- `item_order`;
- `x`;
- `y`;
- descriptor columns indexed by interval.

The implementation does not know about RayJoin, polygon overlay, map0/map1,
author output files, or Section 5.7. It also validates split events before the
compiled core runs:

- unknown chain ids are rejected;
- split events on single-point chains are rejected;
- split edge orders outside the target chain are rejected;
- scratch capacity is derived from the input rather than hard-coded.

## Gate A: Source Genericity

The test suite includes a source scan against the internal spike source for:

- `rayjoin`
- `overlay`
- `section57`
- `author`
- `map0`
- `map1`

This source scan runs even on hosts without Numba.

Manual local scan:

```text
rg -n "rayjoin|overlay|section57|author|map0|map1" history/internal_docs/goal4951_compiled_path_split_spike.py
```

Result: no matches.

## Gate B: Non-RayJoin Synthetic Correctness

The synthetic test compares the compiled materializer against the existing
Python generic reference:

```python
materialize_grouped_output_row_buffer(
    assemble_grouped_path_split_records(...)
)
```

against:

```python
materialize_grouped_output_row_buffer(
    assemble_compiled_path_split_records(...)
)
```

Coverage:

- one chain with multiple split events;
- multiple chains;
- more than two independent chains;
- validity mask skipping an interval;
- descriptor preservation;
- consecutive point dedupe;
- invalid split event rejection.

The fixture is deliberately non-RayJoin and does not encode a binary map
assumption.

## Local Evidence

Local host does not have Numba installed, so compiled behavior tests are skipped
locally. The source genericity test and existing Python reference tests still run.

Command:

```text
$env:PYTHONPATH='src'; py -m unittest tests.goal4951_compiled_path_split_spike_test tests.goal4939_grouped_path_split_records_test
```

Output:

```text
.ssss.......
----------------------------------------------------------------------
Ran 12 tests in 0.111s

OK (skipped=4)
```

## POD Evidence

To avoid the earlier archive-tree evidence weakness, the POD run used a real Git
checkout cloned from a local bundle of HEAD.

POD path:

```text
/root/rtdl_goal4951_git
```

Environment:

```text
python3
PYTHONPATH=src:.
numba 0.66.0
numpy 2.1.2
```

Git/source state before the test:

```text
HEAD=7d30acd19ab253116fe210949918ec2bb5b987a8
STATUS_START
?? history/internal_docs/goal4951_compiled_path_split_spike.py
?? tests/goal4951_compiled_path_split_spike_test.py
STATUS_END
```

This means the POD checkout matched the reviewed repository HEAD and contained
only the two Goal4951 synthetic-gate files as untracked additions.

Command:

```text
cd /root/rtdl_goal4951_git
export PYTHONPATH=src:.
python3 -m unittest tests.goal4951_compiled_path_split_spike_test tests.goal4939_grouped_path_split_records_test
```

Output:

```text
............
----------------------------------------------------------------------
Ran 12 tests in 1.927s

OK
```

## What This Proves

This proves:

- a compiled generic path-split materializer can reproduce the existing Python
  generic path-split materializer on non-RayJoin fixtures;
- the spike does not contain app-identity vocabulary;
- the implementation handles more than two independent chains;
- the implementation can run on the POD with Numba;
- the implementation is not yet public API and does not change RTDL runtime
  source.

## What This Does Not Prove

This does not prove:

- RayJoin public-sample byte equality;
- writer speedup;
- author-output formatting acceleration;
- public API readiness;
- a release claim;
- that Layer 3 will win.

## Proposed Next Step

If review passes, open Goal4951 Gate C:

1. wire this compiled materializer into the RayJoin paper reproduction app as an
   app adapter only;
2. keep final author text formatting in the app;
3. require byte-for-byte equality before any performance claim;
4. then run the same-run writer performance gate:
   - minimum useful gate: writer speedup >= 1.10x;
   - strong gate: writer speedup >= 1.25x;
   - if byte-equal but slower, kill the route as default.

Exit label requested for this report:

`completed_gate_a_b_authorize_gate_c`
