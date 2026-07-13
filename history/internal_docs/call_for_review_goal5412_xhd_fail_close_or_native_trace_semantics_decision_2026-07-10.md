# Call For Review: Goal5412 X-HD Fail-Close Or Native Trace Semantics Decision

Date: 2026-07-10

Please strictly review Goal5412:

```text
Goal5412 X-HD Fail-Close Or Native Trace Semantics Decision
```

Files under review:

```text
history/internal_docs/goal5412_xhd_fail_close_or_native_trace_semantics_decision_2026-07-10.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5412_fail_close_or_native_trace_semantics_decision.json
tests/goal5412_fail_close_or_native_trace_semantics_decision_test.py
```

Context:

```text
Goal5410 passed a synthetic app-neutral statused deferral stream.
Goal5411 applied the current RTDL native frontier -> generic status bridge to
real Goal5387 author sample source ids and failed to recover author sample
source/cell rows.
```

Goal5412 decides:

```text
The current bridge is fail-closed for explicit -lb.
Full Goal5387 row identity parity is not authorized under the current model.
Only a design-only, generic native payload transition trace semantic is
authorized as a possible next step.
```

Requested review questions:

1. Does Goal5412 correctly interpret Goal5411 as a no-go for the current
   statused bridge, rather than as a partial `-lb` success?
2. Is it correct to fail-close explicit `-lb` under the current RTDL execution
   model?
3. Is it correct to forbid a full Goal5387 row/hash/status/feedback gate until
   a bounded sample-row gate passes?
4. Is the proposed `native_payload_transition_trace_stream` generic in name,
   schema, and semantics, or does it smuggle X-HD / paper / author-specific
   logic into RTDL core/native?
5. Is the proposed trace stream properly limited to **design only**, with no
   backend implementation or explicit `-lb` support claim?
6. Are the required schema fields sufficient to express traversal payload-state
   transition rows without hard-coding the author row fanout?
7. Are the forbidden shortcuts complete enough: no hard-coded 6/62 rows,
   no hard-coded sample rows, no X-HD option names, no full parity run before
   bounded recovery?
8. Does the evidence ladder make sense: synthetic non-X-HD fixture -> bounded
   X-HD sample-row gate -> full Goal5387 row-count/hash/sample/status/feedback?
9. Does the report preserve all claim boundaries: no Figure 7/11 reproduction,
   no performance ratio, no exact dataset reproduction, no full X-HD paper
   reproduction?
10. Should the next goal be `Goal5413_generic_native_payload_transition_trace_contract`,
    or should the line stop entirely after fail-closing current explicit `-lb`?

Expected answer shape:

```text
Verdict:
  approve_goal5412_fail_close_current_bridge_and_authorize_design_only_trace
  OR approve_fail_close_only_stop_trace_line
  OR revise_goal5412

Blocking findings:
  ...

Required amendments:
  ...

Non-blocking notes:
  ...

Answers to 10 questions:
  ...
```

Important: this review should not evaluate whether X-HD full paper reproduction
is complete. It is not. This review should judge whether Goal5412 makes the
right local decision after Goal5411's no-go.
