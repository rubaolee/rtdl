# Goal5404 - X-HD Bounded Status-State Oracle Gate Result

Date: 2026-07-10

## Goal

Goal5404 implements the bounded status-state oracle gate authorized by
Goal5403.

The goal is narrower than full explicit `-lb` support:

```text
prove row/hash/status/feedback mechanics on a deterministic app-shaped bounded
fixture before attempting the full Goal5387 author trace.
```

It does not compare against the full Goal5387 trace and does not claim Figure
7/11 reproduction.

## Result

POD artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5404_bounded_status_state_oracle_gate_pod.json
```

Status:

```text
matched = true
status = bounded_status_state_oracle_passed
```

All bounded oracle checks passed:

```text
row_count_matched = true
raw_hash_matched = true
sample_matched = true
status_count_offloading_matched = true
feedback_update_count_matched = true
feedback_row_count_matched = true
current_best_before_matched = true
current_best_after_matched = true
overflow_fail_closed_matched = true
```

## Fixture

Fixture name:

```text
bounded_app_shaped_four_active_queries_four_offload_rows_two_feedback_updates
```

Shape:

```text
active queries = 4
candidate rows = 6
heavy threshold = 16
expected raw offload rows = 4
feedback rows = 4
expected feedback updates = 2
```

Expected offload columns:

```text
active_queue_indices = [0, 2, 4, 2]
query_row_ids        = [1010, 1011, 1012, 1011]
source_ids           = [11168, 210712, 437119, 210712]
cell_ids             = [2924, 17, 18, 99]
status_codes         = [2, 2, 2, 2]
transition_phases    = [1, 1, 1, 1]
current_best_before  = [25.0, 16.0, 9.0, 16.0]
current_best_after   = [20.0, 16.0, 9.0, 16.0]
```

Expected trace summary:

```text
row_count = 4
status_count_offloading = 4
raw_offload_row_hash = 18407930560672925736
sample_indices = [0, 2, 3]
sample source_ids = [11168, 437119, 210712]
sample cell_ids = [2924, 18, 99]
```

## System Change

Goal5404 includes a generic correctness fix to the native smoke:

```text
current_best_after_sq_out now uses updated_best[offset]
```

Before this fix, the native implementation computed feedback-updated best state
but wrote the original current best into the `current_best_after_sq` output
column. Goal5404 needs a bounded oracle that can prove feedback changes the
after-state, so the native generic smoke now exposes that already-computed
updated value.

This does not change the Goal5402 artifact because Goal5402's feedback update
targets a query that is not emitted as an offload row.

Changed generic native line:

```text
src/native/optix/rtdl_optix_api.cpp
```

## Implemented Files

```text
src/native/optix/rtdl_optix_api.cpp
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5404_bounded_status_state_oracle_gate.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5404_bounded_status_state_oracle_gate_pod.json
tests/goal5404_bounded_status_state_oracle_gate_test.py
```

## Validation

Local focused tests before POD artifact:

```text
$env:PYTHONPATH='src'; py -m unittest \
  tests.goal5404_bounded_status_state_oracle_gate_test \
  tests.goal5403_status_state_next_gate_decision_test \
  tests.goal5402_status_state_machine_native_smoke_test

Ran 13 tests
OK (skipped=1)
```

Local compile check:

```text
$env:PYTHONPATH='src'; py -m py_compile \
  Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5404_bounded_status_state_oracle_gate.py \
  tests/goal5404_bounded_status_state_oracle_gate_test.py \
  src/rtdsl/optix_runtime.py

no compile failure
```

POD preflight:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 preflight

POD_OK
45c502cfccb5
NVIDIA RTX 4000 Ada Generation, 550.127.05
```

POD focused tests before native build:

```text
cd /root/rtdl_goal5093
export PYTHONPATH=src
python3 -m unittest \
  tests.goal5404_bounded_status_state_oracle_gate_test \
  tests.goal5403_status_state_next_gate_decision_test \
  tests.goal5402_status_state_machine_native_smoke_test

Ran 13 tests
OK (skipped=1)
```

POD native build and gate:

```text
cd /root/rtdl_goal5093
make build-optix
export PYTHONPATH=src
export RTDL_OPTIX_LIB=/root/rtdl_goal5093/build/librtdl_optix.so
python3 Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5404_bounded_status_state_oracle_gate.py

matched = true
```

POD artifact regression:

```text
cd /root/rtdl_goal5093
export PYTHONPATH=src
python3 -m unittest \
  tests.goal5404_bounded_status_state_oracle_gate_test \
  tests.goal5403_status_state_next_gate_decision_test \
  tests.goal5402_status_state_machine_native_smoke_test

Ran 13 tests
OK
```

Local artifact regression after download:

```text
$env:PYTHONPATH='src'; py -m unittest \
  tests.goal5404_bounded_status_state_oracle_gate_test \
  tests.goal5403_status_state_next_gate_decision_test \
  tests.goal5402_status_state_machine_native_smoke_test \
  tests.goal5401_status_state_machine_spike_contract_test

Ran 18 tests
OK
```

## What This Proves

Goal5404 proves that the generic native status-state smoke can support a bounded
app-shaped status oracle with:

```text
raw offload row count;
deterministic raw row hash;
deterministic row samples;
status_count_offloading;
feedback_update_count;
feedback-updated current_best_after_sq output;
overflow fail-closed behavior.
```

This is a real step beyond Goal5402's purely synthetic native smoke.

## What This Does Not Prove

Goal5404 does not prove:

```text
explicit X-HD -lb support;
Goal5387 full author trace row-count parity;
Goal5387 raw row hash/sample parity;
Goal5387 feedback parity;
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
bounded status-state oracle passed on POD;
row/hash/status/feedback mechanics work on a deterministic app-shaped fixture;
the next gate may move toward real-stream bridge / full-gate readiness.
```

Not allowed:

```text
full explicit -lb support;
full Goal5387 parity;
paper figure reproduction;
performance parity.
```

## Recommended Next Step

Goal5405 should decide and/or implement the real-stream bridge:

```text
Goal5405_status_state_real_stream_bridge_or_full_gate_readiness
```

It must answer whether the bounded oracle mechanics can be connected to the
actual Goal5387-style candidate/frontier stream without X-HD-specific native
semantics.

If yes, the next gate can attempt full author trace row/hash/status/feedback
parity. If no, explicit `-lb` remains fail-closed for this reproduction line.
