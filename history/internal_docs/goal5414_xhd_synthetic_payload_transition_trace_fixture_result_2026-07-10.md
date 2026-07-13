# Goal5414 — Synthetic Non-App Payload-Transition Trace Fixture Result

## Verdict

```text
completed_synthetic_non_app_payload_transition_trace_fixture
```

Goal5414 implements the first behavior-level proof for the generic
`ACTIVE_QUERY_PAYLOAD_TRANSITION_TRACE_CONTRACT` introduced in Goal5413.  It
does **not** implement a native backend, does **not** support X-HD `-lb`, and
does **not** reopen Figure 7 / Figure 11.  It only proves that the new generic
trace shape can be consumed by a non-X-HD synthetic workload and summarized
with fail-closed behavior.

## Why This Goal Exists

The Goal5408 review and Goal5412 decision corrected the project direction:

- the current X-HD `-lb` bridge is fail-closed;
- direct native fixes toward Goal5387 row identity are not authorized;
- any continuation must first become a generic RTDL status/trace abstraction,
  not another X-HD implementation-level reverse engineering loop.

Goal5413 therefore created a **design-only** generic payload-transition trace
contract.  Goal5414 is the first evidence gate on that ladder:

```text
synthetic non-app behavior -> bounded external sample-row gate -> full external row/hash/status/feedback gate
```

This goal completes only the first step.

## Implementation

### System API Added

The following generic summary helper was added to `src/rtdsl/active_query_status.py`:

```text
payload_transition_trace_summary_numpy_columns(...)
```

It summarizes rows matching the generic payload-transition schema:

```text
active_queue_indices
query_row_ids
source_ids
primitive_or_cell_ids
cell_namespace_codes
status_codes
transition_phase_codes
current_best_before_sq
current_best_after_sq
lower_bounds_sq
upper_bounds_sq
work_counts
payload_event_ordinals
```

The helper reports:

- row count;
- active query count;
- status counts for offload/completed/miss/aborted;
- deterministic FNV-1a hash over selected integer columns;
- deterministic samples;
- fail-closed rejection for overflow, bad capacity, unknown status codes,
  negative namespace codes, negative event ordinals, and shape mismatch.

It is intentionally a CPU reference / summary helper:

```text
native_engine_row_contract = not_called_cpu_reference_only
external_option_support_claimed = false
rt_core_speedup_claim_authorized = false
whole_app_speedup_claim_authorized = false
```

### Synthetic Fixture

The app-side runner is:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5414_synthetic_payload_transition_trace_fixture.py
```

The fixture models three generic spatial requests over numbered bins.  It uses
only generic statuses:

```text
offload, completed, miss, offload, aborted
```

It intentionally avoids X-HD, author logs, paper inputs, Figure labels, and
external option semantics.

### Artifact

Result artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5414_synthetic_payload_transition_trace_fixture.json
```

Key fields:

```json
{
  "matched": true,
  "status": "synthetic_non_app_payload_transition_trace_fixture_passed",
  "expected_counts": {
    "raw_transition_row_count": 5,
    "status_count_offloading": 2,
    "status_count_completed": 1,
    "status_count_miss": 1,
    "status_count_aborted": 1
  },
  "summary": {
    "status": "accept",
    "active_query_count": 3,
    "raw_transition_row_count": 5,
    "status_count_offloading": 2,
    "status_count_completed": 1,
    "status_count_miss": 1,
    "status_count_aborted": 1
  },
  "overflow_reject": {
    "status": "reject"
  }
}
```

## Validation

Focused commands:

```text
$env:PYTHONPATH='src'; py -m py_compile src\rtdsl\active_query_status.py src\rtdsl\__init__.py Paper-reproduction-apps\x-hd-paper\scripts\run_xhd_goal5414_synthetic_payload_transition_trace_fixture.py
$env:PYTHONPATH='src'; py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_goal5414_synthetic_payload_transition_trace_fixture.json > $null
$env:PYTHONPATH='src'; py -m unittest tests.goal5414_synthetic_payload_transition_trace_fixture_test tests.goal5413_native_payload_transition_trace_contract_test tests.goal5412_fail_close_or_native_trace_semantics_decision_test tests.goal5411_bounded_statused_deferral_sample_row_gate_test tests.goal5410_statused_large_cell_deferral_stream_probe_test
```

Result:

```text
Ran 27 tests in 0.077s
OK
```

Extended nearby regression:

```text
$env:PYTHONPATH='src'; py -m unittest tests.goal5414_synthetic_payload_transition_trace_fixture_test tests.goal5413_native_payload_transition_trace_contract_test tests.goal5412_fail_close_or_native_trace_semantics_decision_test tests.goal5411_bounded_statused_deferral_sample_row_gate_test tests.goal5410_statused_large_cell_deferral_stream_probe_test tests.goal5409_status_machine_semantics_decision_test tests.goal5408_cell_namespace_reconciliation_test tests.goal5407_full_cover_delta_membership_probe_test
```

Result:

```text
Ran 44 tests in 0.089s
OK
```

The local Python launcher printed the known environment warning:

```text
Could not find platform independent libraries <prefix>
```

The tests still passed.

## Claim Boundary

Authorized:

- a synthetic non-app payload-transition trace fixture passed;
- the generic trace summary helper is behaviorally exercised;
- overflow / invalid rows fail closed;
- Goal5413's design-only contract now has one non-X-HD behavior proof.

Not authorized:

- X-HD `-lb` support;
- Goal5387 full row identity;
- native payload-transition backend completion;
- Figure 7 reproduction;
- Figure 11 reproduction;
- author parity;
- performance ratio;
- exact paper dataset reproduction;
- full X-HD paper reproduction.

## Current Strategic Meaning

Goal5414 is deliberately small.  It answers only one question:

```text
Can the proposed payload-transition trace shape support a non-X-HD consumer?
```

Answer:

```text
Yes, at CPU-reference / synthetic-fixture level.
```

It does **not** prove that continuing toward X-HD `-lb` is worthwhile.  The
default project recommendation from Goal5412 remains:

```text
fail-close the current explicit -lb line
```

The only reason to continue is a narrow, separately reviewed generic trace line.

## Recommended Next Goal

```text
Goal5415_decide_stop_or_bounded_xhd_payload_transition_sample_gate
```

Goal5415 should not implement a backend by default.  It should decide whether
the project stops here or attempts one bounded X-HD sample-row recovery gate
using the new generic trace contract.

If attempted, that gate must remain bounded and must not reopen Figure 7,
Figure 11, or full `-lb` parity.
