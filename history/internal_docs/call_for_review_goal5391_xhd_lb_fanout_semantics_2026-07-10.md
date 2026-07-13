# Call For Review: Goal5391 X-HD `-lb` Fanout Semantics Diagnostic

Date: 2026-07-10

Please strictly review Goal5391.

## Review Scope

Goal5391 is a diagnostic / requirements goal. It does not implement `-lb`.

It uses:

```text
Goal5387 author trace v2
Goal5390 full-source RTDL trace summary gate
```

to classify the remaining mismatch as a status-stream fanout / transition
semantics problem.

## Files To Review

```text
history/internal_docs/goal5391_xhd_lb_fanout_semantics_result_2026-07-10.md
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5391_lb_fanout_semantics.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5391_lb_fanout_semantics.json
tests/goal5391_lb_fanout_semantics_test.py
```

Prior artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5387_author_trace_v2_execution.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5390_full_trace_summary_gate.json
history/internal_docs/goal5390_xhd_full_trace_summary_gate_result_2026-07-10.md
history/internal_docs/call_for_review_goals5386_5390_xhd_lb_trace_packet_2026-07-10.md
```

## Critical Facts To Verify

1. Goal5391 correctly derives:

   ```text
   author rows = 27133990
   RTDL rows   = 2188225
   active count = 437645
   author aggregate rows per active = 62
   RTDL aggregate rows per active = 5
   ```

2. Goal5391 does **not** overclaim per-query uniform fanout distribution. It
   only claims aggregate denominator mismatch.

3. Goal5391 correctly rejects bridge runtime optimization as the next main
   path while row/hash parity is false.

4. Goal5391 keeps explicit `-lb` unsupported and keeps Figure 7 / Figure 11 /
   full-paper / performance claims closed.

5. Goal5391's next-native-stream requirements are generic and forbid:

   ```text
   hard-code 62 rows per active query;
   X-HD-specific native primitive names or paper semantics in RTDL core;
   source-limited smoke as full-source parity;
   bridge vectorization as the main fix while row/hash parity is false.
   ```

## Review Questions

1. Is the 62-vs-5 aggregate fanout derivation correct?
2. Is the "aggregate only, not per-query distribution" caveat sufficient?
3. Does this diagnostic correctly follow from Goal5387 and Goal5390?
4. Is it correct to reject bridge runtime optimization as the next main path?
5. Are the next-native-stream requirements generic enough?
6. Does the claim boundary avoid `-lb`, Figure 7/11, memory, performance, exact
   dataset, and full-paper overclaims?
7. Should the next implementation be a generic native multi-round status stream
   or a fail-closed `-lb` closeout?

## Expected Answer Shape

Please answer in this form:

```text
Verdict: approve / approve_with_required_amendments / block

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Answers to questions:
1. ...
2. ...
...
7. ...
```

Requested verdict label if approved:

```text
approve_goal5391_xhd_lb_fanout_semantics__native_multiround_or_fail_closed_next
```
