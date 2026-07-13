# Call For Review - Goal5398 X-HD Native v7 Status-Stream Parity Gate

Please strictly review Goal5398.

## Files To Review

Result report:

```text
history/internal_docs/goal5398_xhd_native_v7_status_stream_parity_gate_result_2026-07-10.md
```

POD artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5398_native_v7_status_stream_parity_gate_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5398_native_v7_status_stream_parity_gate_bounded_pod.json
```

Implementation and tests:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5398_native_v7_status_stream_parity_gate.py
tests/goal5398_native_v7_status_stream_parity_gate_test.py
```

Prior oracle and related status-stream work:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5387_author_trace_v2_execution.json
history/internal_docs/goal5397_xhd_native_v7_status_stream_smoke_result_2026-07-10.md
history/internal_docs/goal5396_xhd_v6_status_stream_remap_no_go_result_2026-07-10.md
history/internal_docs/goal5395_xhd_native_status_stream_abi_gate_result_2026-07-10.md
```

## Review Questions

1. Does Goal5398 correctly compare the generic native v7 status stream against
   the Goal5387 author trace v2 oracle instead of against a self-generated
   RTDL expectation?
2. Does the full-public POD artifact support the conclusion that active query
   count matches but row-count parity fails?
3. Does the full-public POD artifact support the conclusion that raw hash/sample
   parity fails?
4. Is it correct to keep explicit X-HD `-lb` support fail-closed after this
   result?
5. Does the result avoid claiming Figure 7, Figure 11, performance parity,
   exact paper dataset reproduction, or full X-HD paper reproduction?
6. Is the bounded `source_limit=64` smoke correctly treated as a script/native
   path smoke rather than as an author parity result?
7. Does the implementation keep the status-stream path generic and avoid
   putting X-HD option names or figure semantics into RTDL core/native APIs?
8. Is the next recommended gate correctly framed as a semantic status-machine
   redesign or stop decision, rather than another row-count remap?

## Expected Answer Shape

Please respond with:

```text
Verdict:
  approve_goal5398_native_v7_status_stream_parity_gate_fail_closed
  OR approve_with_required_amendments
  OR revise_goal5398

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
approve_goal5398_native_v7_status_stream_parity_gate_fail_closed
```
