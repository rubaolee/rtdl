# Call For Review - Goal5401 Generic Status-State Machine Spike Contract

Please strictly review Goal5401.

## Files To Review

Result report:

```text
history/internal_docs/goal5401_generic_status_state_machine_spike_contract_result_2026-07-10.md
```

Implementation and tests:

```text
src/rtdsl/active_query_status.py
src/rtdsl/__init__.py
tests/goal5401_status_state_machine_spike_contract_test.py
```

Prior decision/evidence:

```text
history/internal_docs/goal5399_xhd_status_machine_semantic_gap_decision_2026-07-10.md
history/internal_docs/goal5400_xhd_existing_status_stream_knob_matrix_result_2026-07-10.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5387_author_trace_v2_execution.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5398_native_v7_status_stream_parity_gate_pod.json
```

## Review Questions

1. Does Goal5401 correctly translate the Goal5399 semantic gap into a generic
   RTDL contract rather than an X-HD-specific shortcut?
2. Does the contract require raw offload rows before continuation/reduce?
3. Does the contract require feedback telemetry?
4. Are the success gates strong enough to prevent claiming external option
   support from a synthetic smoke alone?
5. Are the fail-closed rules strong enough for overflow, row mismatch, hash
   mismatch, and feedback mismatch?
6. Does the implementation keep app identity tokens out of RTDL core/source and
   contract payload?
7. Does the report correctly avoid claiming a native backend, explicit `-lb`,
   Figure 7/11, performance parity, or full X-HD reproduction?
8. Is Goal5402 the correct next implementation step?

## Expected Answer Shape

Please respond with:

```text
Verdict:
  approve_goal5401_generic_status_state_machine_spike_contract
  OR approve_with_required_amendments
  OR revise_goal5401

Blocking findings:
  ...

Required amendments:
  ...

Non-blocking notes:
  ...

Answers to the 8 review questions:
  ...
```

## Proposed Verdict

```text
approve_goal5401_generic_status_state_machine_spike_contract
```
