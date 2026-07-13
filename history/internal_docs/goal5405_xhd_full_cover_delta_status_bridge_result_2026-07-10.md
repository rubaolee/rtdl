# Goal5405 - X-HD Full-Cover Delta Status Bridge Result

Date: 2026-07-10

## Goal

Goal5405 advances the explicit `-lb` status-state line from Goal5404's bounded
app-shaped oracle to the specific 56+6 rows/active full-cover-delta shape
identified by Goals5393-5394.

It is still bounded:

```text
2 active queries;
56 base rows per active query;
6 delta rows per active query;
62 total rows per active query;
124 total raw offload rows.
```

It does not generate the full Goal5387 author stream:

```text
437,645 active queries;
27,133,990 raw offload rows.
```

## Result

POD artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5405_full_cover_delta_status_bridge_pod.json
```

Status:

```text
matched = true
status = bounded_full_cover_delta_status_bridge_passed
```

Passed checks:

```text
goal5394_shape_matches_target = true
native_row_count_matched_expected = true
native_hash_matched_expected = true
native_sample_matched_expected = true
native_status_count_matched_expected = true
native_feedback_count_zero_matched = true
native_current_best_after_matched = true
multiround_reference_total_rows_matched = true
overflow_fail_closed_matched = true
```

## Why 56+6 Matters

Goal5393 selected this target shape:

```text
author rows per active = 62
closest known generic RTDL surface rows per active = 56
missing rows per active = 6
```

Goal5394 converted that into a generic full-cover-delta probe:

```text
base rows per active = 56
delta rows per active = 6
target rows per active = 62
```

Goal5405 now proves that the native status-state smoke can emit the bounded
56+6 shape and match a deterministic generic trace summary.

## Bounded Fixture

Fixture:

```text
bounded_two_active_queries_56_base_plus_6_delta_rows_per_active
```

Expected rows:

```text
active_count = 2
base_rows_per_active = 56
delta_rows_per_active = 6
total_rows_per_active = 62
expected_total_rows = 124
```

Expected trace:

```text
row_count = 124
status_count_offloading = 124
raw_offload_row_hash = 3623014471670323363
sample_indices = [0, 62, 123]
sample source_ids = [11168, 210712, 210712]
sample cell_ids = [100000, 101006, 901005]
```

Multiround reference shape:

```text
contract = generic_active_query_multiround_status_reference_v1
round 0 offload rows = 112
round 1 offload rows = 12
raw_offload_rows_before_sort_reduce = 124
total_feedback_updates = 0
```

## Implemented Files

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5405_full_cover_delta_status_bridge.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5405_full_cover_delta_status_bridge_pod.json
tests/goal5405_full_cover_delta_status_bridge_test.py
```

No RTDL core/native code changed in Goal5405.

## Validation

Local focused tests before POD artifact:

```text
$env:PYTHONPATH='src'; py -m unittest \
  tests.goal5405_full_cover_delta_status_bridge_test \
  tests.goal5404_bounded_status_state_oracle_gate_test \
  tests.goal5403_status_state_next_gate_decision_test

Ran 13 tests
OK (skipped=1)
```

POD focused tests before runner:

```text
cd /root/rtdl_goal5093
export PYTHONPATH=src
python3 -m unittest \
  tests.goal5405_full_cover_delta_status_bridge_test \
  tests.goal5404_bounded_status_state_oracle_gate_test \
  tests.goal5403_status_state_next_gate_decision_test

Ran 13 tests
OK (skipped=1)
```

POD runner:

```text
cd /root/rtdl_goal5093
export PYTHONPATH=src
export RTDL_OPTIX_LIB=/root/rtdl_goal5093/build/librtdl_optix.so
python3 Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5405_full_cover_delta_status_bridge.py

matched = true
```

POD artifact regression:

```text
cd /root/rtdl_goal5093
export PYTHONPATH=src
python3 -m unittest tests.goal5405_full_cover_delta_status_bridge_test

Ran 5 tests
OK
```

Local artifact regression after download:

```text
$env:PYTHONPATH='src'; py -m unittest \
  tests.goal5405_full_cover_delta_status_bridge_test \
  tests.goal5404_bounded_status_state_oracle_gate_test \
  tests.goal5403_status_state_next_gate_decision_test \
  tests.goal5394_full_cover_delta_status_probe_test

Ran 17 tests
OK
```

## What This Proves

Goal5405 proves:

```text
the Goal5393/5394 56+6 rows/active target shape is correctly carried into a
bounded native status-state bridge;
the native bridge emits the expected 124 raw offload rows;
the generic trace hash and deterministic samples match;
status_count_offloading matches;
overflow still fails closed;
the bounded shape is consistent with the generic multiround reference.
```

This is stronger than Goal5404 because the shape is now tied to the explicit
`-lb` denominator analysis:

```text
56 base rows + 6 delta rows = 62 author rows per active query
```

## What This Does Not Prove

Goal5405 does not prove:

```text
explicit X-HD -lb support;
full Goal5387 row-count parity;
full Goal5387 row hash/sample parity;
full Goal5387 feedback parity;
generation of 27,133,990 real full-public rows;
Figure 7 reproduction;
Figure 11 reproduction;
author RT-core algorithm parity;
same-denominator memory claim;
author-vs-RTDL performance ratio;
exact paper dataset reproduction;
full X-HD paper reproduction.
```

## Claim Boundary

Allowed:

```text
bounded full-cover-delta status bridge passed on POD;
56+6 rows/active target shape works in the native status-state bridge;
next gate can target the real full-cover surface or full Goal5387 stream.
```

Not allowed:

```text
full explicit -lb support;
full Goal5387 parity;
paper figure reproduction;
performance parity.
```

## Recommended Next Step

Goal5406 should move from bounded shape to real stream:

```text
Goal5406_real_full_cover_surface_or_full_goal5387_stream_gate
```

It should choose one of:

```text
1. generate the real full-cover surface with 24,508,120 rows and compare its
   row count/hash/sample/status shape;
2. if available, generate the full 27,133,990-row Goal5387 target stream and
   compare row count/hash/sample/status/feedback;
3. fail close explicit -lb if producing that real stream requires X-HD-specific
   native semantics rather than generic RTDL active-query state.
```

The bounded shape is now validated. The remaining hard step is real full-public
row-stream generation.
