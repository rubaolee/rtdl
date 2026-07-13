# Goal5401 - Generic Status-State Machine Spike Contract Result

Date: 2026-07-10

## Goal

Goal5401 turns the Goal5399/Goal5400 decision into a tested RTDL core contract
for the next native implementation spike.

The problem to solve is not row remapping:

```text
Goal5387 author trace rows = 27133990
Goal5398 RTDL v7 rows = 2600727
Goal5400 existing knobs = under-count badly or over-count by orders of magnitude
```

Therefore Goal5401 defines the generic native status-state-machine semantics
that any Goal5402 implementation must satisfy before it may be compared to the
author explicit `-lb` trace.

## Implemented System Additions

New RTDL public constant:

```text
ACTIVE_QUERY_STATUS_STATE_MACHINE_NATIVE_SPIKE_CONTRACT
```

New RTDL public functions:

```text
active_query_status_state_machine_native_spike_contract()
validate_active_query_status_state_machine_native_spike_contract()
```

Files changed:

```text
src/rtdsl/active_query_status.py
src/rtdsl/__init__.py
tests/goal5401_status_state_machine_spike_contract_test.py
```

## Contract Requirements

The new contract requires two semantic emission points:

```text
raw_offload_before_continuation_reduce
post_continuation_feedback
```

The first point must happen before:

```text
row collapse
sort or unique
continuation feedback
light-row exact continuation
```

This directly addresses the Goal5398/5400 gap: current RTDL v7 rows are emitted
at an existing frontier row point, while the author trace records raw offload
append rows before load-balance reduce.

Required telemetry includes:

```text
active_query_count
raw_offload_row_count
raw_offload_row_hash_or_deterministic_samples
status_count_offloading
status_count_aborted
status_count_miss
status_count_completed
feedback_update_count
row_capacity
overflowed
```

Required gates:

```text
synthetic_non_app_raw_offload_rows
bounded_app_oracle_row_count_and_hash
full_external_oracle_row_count_hash_status_and_feedback
```

Required fail-closed rules:

```text
overflow_returns_no_partial_success_claim
row_count_mismatch_keeps_external_option_unsupported
hash_or_sample_mismatch_keeps_external_option_unsupported
feedback_mismatch_keeps_external_option_unsupported
```

Forbidden backend behavior:

```text
hard_coded_row_fanout_per_active_query
app_option_names_in_native_symbols
app_dataset_names_in_core_or_native
external_result_claim_without_row_hash_feedback_gate
```

## Validation

Focused local tests:

```text
$env:PYTHONPATH='src'; py -m unittest \
  tests.goal5401_status_state_machine_spike_contract_test \
  tests.goal5395_native_status_stream_abi_gate_test \
  tests.goal5379_active_query_status_machine_reference_test \
  tests.goal5380_active_query_frontier_bridge_test \
  tests.goal5382_status_machine_stream_design_test

Ran 24 tests in 2.802s
OK
```

Test coverage:

- public export of the new contract and validator;
- valid default contract;
- raw-offload-before-continuation emission point;
- post-feedback emission point;
- feedback telemetry;
- synthetic non-app gate;
- full external oracle gate;
- rejection when raw-offload point is missing;
- rejection when feedback telemetry is missing;
- app-neutral source and payload scan;
- rejection when an app identity token leaks into the contract.

## Claim Boundary

What Goal5401 proves:

```text
RTDL now has a tested generic design contract for the next status-state-machine
implementation spike.
```

What Goal5401 does not prove:

```text
native backend implementation exists;
author row-count parity;
author row-hash parity;
explicit X-HD -lb support;
Figure 7 reproduction;
Figure 11 reproduction;
performance parity;
full X-HD paper reproduction.
```

## Next Goal

Goal5402 should implement the smallest native synthetic status-state smoke that
satisfies this contract:

```text
emit raw offload rows before continuation/reduce;
report post-feedback telemetry or explicit not-applicable telemetry;
run a synthetic non-app fixture first;
then run bounded X-HD app gate;
then, only if bounded passes, run the full Goal5387 oracle gate.
```

## Status

```text
completed_generic_status_state_machine_spike_contract__backend_not_implemented
```
