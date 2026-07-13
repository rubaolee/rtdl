# Goal5403 - X-HD Status-State Next Gate Decision Result

Date: 2026-07-10

## Goal

Goal5403 reconciles the current explicit `-lb` evidence before authorizing the
next status-state step.

The goal is deliberately a decision / gate goal, not a new native algorithm:

```text
read Goal5387 author trace v2 oracle;
read Goal5398 RTDL native v7 mismatch;
read Goal5402 generic native status-state smoke;
decide whether direct full Goal5387 parity is ready or whether a bounded
status-state oracle gate must come first.
```

## Result

Artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5403_status_state_next_gate_decision.json
```

Exit label:

```text
authorize_goal5404_bounded_status_state_oracle_gate__direct_goal5387_gate_not_ready
```

Decision:

```text
direct_full_goal5387_gate_authorized = false
bounded_status_state_oracle_gate_authorized = true
explicit_lb_support_remains_unsupported = true
next_goal = Goal5404
```

## Evidence Reconciled

### Goal5387 Author Trace V2 Oracle

```text
active queries = 437,645
raw offload rows before sort/reduce = 27,133,990
status_count_offloading = 27,133,990
raw row hash = 4333109858711462591
feedback_update_count = 294
```

This is the current author-side oracle for explicit `-lb` status-stream
semantics.

### Goal5398 Current RTDL Native V7

```text
active_query_count_parity = true
RTDL v7 raw rows = 2,600,727
row_count_parity = false
hash_parity = false
status_count_offloading_parity = false
feedback_update_count_parity = null / unmeasured
row_ratio_rtdl_v7_div_author = 0.09584756978240207
```

This proves the active queue size aligns, but the raw row denominator and hash
surface do not.

### Goal5402 Native Synthetic Smoke

```text
matched = true
native symbol = rtdl_optix_active_query_status_state_machine_smoke_v1
contract = generic_active_query_status_state_machine_native_spike_v1
synthetic active queries = 3
synthetic raw offload rows = 2
synthetic feedback updates = 1
```

This proves the smallest generic native status-state-machine smoke can execute
on POD. It does not consume the real Goal5387 candidate/frontier stream and does
not establish row/hash parity against the author trace.

## Why Direct Full Goal5387 Gate Is Not Ready

The artifact records these blockers:

```text
current native v7 status stream has row_count_parity=false;
current native v7 status stream has hash_parity=false;
current native v7 feedback_update_count_parity is null/unmeasured;
Goal5402 is synthetic and does not consume the real Goal5387 candidate/frontier stream;
Goal5402 active/query/row scale is 3 active queries and 2 rows, not
437645 active queries and 27133990 rows.
```

The scale gap is decisive:

```text
Goal5387 author raw rows = 27,133,990
Goal5398 RTDL v7 rows    = 2,600,727
Goal5402 smoke rows      = 2
```

Therefore a direct "full explicit `-lb` support" claim would be false.

## Authorized Next Gate

Goal5403 authorizes Goal5404 as a bounded status-state oracle gate.

Required Goal5404 properties:

```text
deterministic small app-shaped fixture;
raw offload rows before continuation/reduce;
row_count and deterministic row hash or sample comparison;
status_count_offloading comparison;
feedback_update_count comparison;
overflow fail-closed behavior;
no X-HD-specific constants or option names in RTDL core/native.
```

Success label:

```text
bounded_status_state_oracle_matches_rows_status_feedback__full_gate_next
```

Failure label:

```text
bounded_status_state_oracle_no_go__explicit_lb_remains_fail_closed
```

## Implemented Files

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5403_status_state_next_gate_decision.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5403_status_state_next_gate_decision.json
tests/goal5403_status_state_next_gate_decision_test.py
```

No RTDL core/native code changed in Goal5403.

## Validation

Artifact generation:

```text
$env:PYTHONPATH='src'; py Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5403_status_state_next_gate_decision.py

Paper-reproduction-apps/x-hd-paper/results/xhd_goal5403_status_state_next_gate_decision.json
```

Focused Goal5403 test:

```text
$env:PYTHONPATH='src'; py -m unittest tests.goal5403_status_state_next_gate_decision_test

Ran 4 tests
OK
```

Neighbor status-state regression:

```text
$env:PYTHONPATH='src'; py -m unittest \
  tests.goal5403_status_state_next_gate_decision_test \
  tests.goal5402_status_state_machine_native_smoke_test \
  tests.goal5401_status_state_machine_spike_contract_test \
  tests.goal5398_native_v7_status_stream_parity_gate_test

Ran 19 tests
OK
```

The local Python warning:

```text
Could not find platform independent libraries <prefix>
```

is the known Windows environment noise and did not prevent test success.

## Claim Boundary

Allowed:

```text
Goal5403 authorizes a bounded status-state oracle gate as the next step.
Goal5403 records that direct full Goal5387 trace parity is not ready.
```

Not allowed:

```text
explicit X-HD -lb support;
Goal5387 row-count parity;
Goal5387 hash/sample parity;
Goal5387 feedback parity;
Figure 7 reproduction;
Figure 11 reproduction;
same-denominator memory claim;
author performance ratio;
author RT-core algorithm parity;
exact paper dataset reproduction;
full X-HD paper reproduction.
```

## Conclusion

Goal5403 prevents an invalid jump from Goal5402 synthetic smoke to full explicit
`-lb` support. The correct next move is a bounded app-shaped status-state oracle
gate that exercises row count, deterministic row hash/sample, status count,
feedback count, and overflow behavior before attempting the full Goal5387 author
trace.
