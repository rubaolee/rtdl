# Call For Review: Goal5413 Generic Native Payload-Transition Trace Contract

Date: 2026-07-10

Please strictly review Goal5413:

```text
Goal5413 Generic Native Payload-Transition Trace Contract
```

Files under review:

```text
src/rtdsl/active_query_status.py
src/rtdsl/__init__.py
tests/goal5413_native_payload_transition_trace_contract_test.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5413_native_payload_transition_trace_contract.json
history/internal_docs/goal5413_xhd_generic_native_payload_transition_trace_contract_result_2026-07-10.md
```

Context:

```text
Goal5412 fail-closed explicit -lb under the current RTDL frontier-to-status
bridge and allowed only a design-only generic trace contract as a narrow
exception.
```

Goal5413 adds a public RTDL contract:

```text
native_payload_transition_trace_stream
```

It is intentionally design/schema only. It does not implement a backend and
does not support explicit `-lb`.

Requested review questions:

1. Is the new contract app-neutral in naming, schema, and metadata?
2. Does it avoid X-HD / paper / author / figure identity leakage in RTDL core?
3. Does it correctly remain design-only (`executable=false`) with no backend
   implementation claim?
4. Does the row schema include the fields needed for native traversal /
   payload transition traces: primitive/cell id, namespace code, status code,
   transition phase, current-best before/after, bounds, work count, event
   ordinal?
5. Does the telemetry schema include row count, hash/sample, status counts,
   feedback count, capacity, and overflow?
6. Does the validator fail closed for backend execution claims, app identity
   leakage, missing bounded sample gate, schema drift, and missing telemetry?
7. Is the evidence ladder correct: synthetic non-app behavior fixture first,
   bounded external sample-row recovery second, full row/hash/status/feedback
   only after bounded recovery?
8. Does this contract satisfy the latest review condition that any continuation
   beyond fail-closing `-lb` must first name a generic status transition and
   provide a non-X-HD path before returning to X-HD?
9. Does the report preserve all broad claim boundaries: no explicit `-lb`, no
   Figure 7/11, no performance ratio, no exact dataset, no full paper
   reproduction?
10. Should the next goal be `Goal5414_synthetic_non_app_payload_transition_trace_fixture`,
    or should the design line stop here?

Expected answer shape:

```text
Verdict:
  approve_goal5413_generic_native_payload_transition_trace_contract
  OR approve_contract_but_stop_before_goal5414
  OR revise_goal5413

Blocking findings:
  ...

Required amendments:
  ...

Non-blocking notes:
  ...

Answers to 10 questions:
  ...
```

Important: do not treat this as X-HD `-lb` support. It is a generic contract
review only.
