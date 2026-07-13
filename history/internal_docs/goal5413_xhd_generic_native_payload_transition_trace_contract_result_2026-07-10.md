# Goal5413 Generic Native Payload-Transition Trace Contract Result

Date: 2026-07-10

Status:

```text
generic_native_payload_transition_trace_contract_specified__no_backend_implementation
```

## Purpose

Goal5412 fail-closed explicit X-HD `-lb` under the current RTDL
frontier-to-status bridge. It authorized only a narrow design-only exception:
a generic native trace semantic emitted at traversal / payload transition time.

Goal5413 turns that exception into an RTDL public contract:

```text
native_payload_transition_trace_stream
```

This is a system contract. It is not an X-HD primitive, not a backend, and not
explicit `-lb` support.

## Implemented System Surface

Added to `src/rtdsl/active_query_status.py` and exported from `rtdsl`:

```text
ACTIVE_QUERY_PAYLOAD_TRANSITION_TRACE_CONTRACT
ACTIVE_QUERY_PAYLOAD_TRANSITION_TRACE_ROW_SCHEMA
ACTIVE_QUERY_PAYLOAD_TRANSITION_TRACE_TELEMETRY_SCHEMA
native_payload_transition_trace_stream_contract
validate_native_payload_transition_trace_stream_contract
```

Contract identifier:

```text
generic_native_payload_transition_trace_stream_contract_v1
```

Execution status:

```text
executable = false
backend_implemented = false
design/schema only
```

## Required Row Schema

```text
active_queue_index
query_row_id
source_id
primitive_or_cell_id
cell_namespace_code
status_code
transition_phase_code
current_best_before_sq
current_best_after_sq
lower_bound_sq
upper_bound_sq
work_count
payload_event_ordinal
```

The schema is app-neutral. The important difference from the earlier
frontier/status bridge is that it requires a row emitted at native traversal or
payload transition time, before downstream frontier lowering, row collapse,
sort/unique, grouped reduction, or continuation feedback.

## Required Telemetry

```text
active_query_count
raw_transition_row_count
raw_transition_row_hash_or_deterministic_samples
status_count_offloading
status_count_completed
status_count_miss
status_count_aborted
feedback_update_count_or_not_applicable
row_capacity
overflowed
```

## Required Gates

The contract hard-codes the evidence ladder as generic gate names:

```text
synthetic_non_app_payload_transition_trace_behavior
bounded_external_oracle_sample_row_recovery
full_external_oracle_row_count_hash_status_feedback
```

This means future implementation must first pass a non-X-HD synthetic behavior
fixture. It may not jump directly to a full X-HD Goal5387 row-identity run.

## Validator Behavior

The validator accepts the default contract and rejects:

```text
backend execution claims;
app identity token leakage;
missing bounded sample-row recovery gate;
unexpected row or telemetry schema;
non-generic app flag;
overflow / hash / feedback gate omissions.
```

## Claim Boundary

Goal5413 proves:

```text
RTDL now has a public generic design contract for a native payload-transition
trace stream.
```

Goal5413 does not prove:

```text
native backend implementation;
explicit -lb support;
bounded X-HD sample-row recovery;
full Goal5387 row identity parity;
Figure 7 or Figure 11 reproduction;
performance ratio;
exact paper dataset reproduction;
full X-HD paper reproduction.
```

## Artifacts

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5413_native_payload_transition_trace_contract.json
tests/goal5413_native_payload_transition_trace_contract_test.py
```

## Validation

```text
$env:PYTHONPATH='src'; py -m py_compile src\rtdsl\active_query_status.py src\rtdsl\__init__.py

$env:PYTHONPATH='src'; py -m unittest `
  tests.goal5413_native_payload_transition_trace_contract_test `
  tests.goal5412_fail_close_or_native_trace_semantics_decision_test `
  tests.goal5411_bounded_statused_deferral_sample_row_gate_test `
  tests.goal5410_statused_large_cell_deferral_stream_probe_test `
  tests.goal5409_status_machine_semantics_decision_test `
  tests.goal5408_cell_namespace_reconciliation_test `
  tests.goal5407_full_cover_delta_membership_probe_test

Ran 39 tests OK
```

Narrow Goal5413 validation also passed:

```text
$env:PYTHONPATH='src'; py -m unittest `
  tests.goal5413_native_payload_transition_trace_contract_test `
  tests.goal5412_fail_close_or_native_trace_semantics_decision_test `
  tests.goal5411_bounded_statused_deferral_sample_row_gate_test `
  tests.goal5410_statused_large_cell_deferral_stream_probe_test

Ran 22 tests OK
```

## Recommended Next Goal

```text
Goal5414_synthetic_non_app_payload_transition_trace_fixture
```

Goal5414 should create a synthetic app-neutral behavior fixture for this
contract. It should not use X-HD author samples, X-HD option names, paper
figure labels, or author constants. Only after that synthetic fixture passes
should a bounded X-HD sample-row gate be reconsidered.
