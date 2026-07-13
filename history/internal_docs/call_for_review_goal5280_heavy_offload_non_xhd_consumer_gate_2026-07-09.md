# Call For Review - Goal5280 Heavy-Offload Non-XHD Consumer Gate

Please strictly review Goal5280.

## Files To Review

Tests:

```text
tests/goal5280_heavy_offload_non_xhd_consumer_gate_test.py
tests/goal5279_generic_heavy_offload_worklist_test.py
```

Implementation under test:

```text
src/rtdsl/partner_continuations.py
src/rtdsl/__init__.py
```

Result / artifact:

```text
history/internal_docs/goal5280_heavy_offload_non_xhd_consumer_gate_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5280_heavy_offload_non_xhd_consumer_gate_2026-07-09.json
```

Context:

```text
history/internal_docs/goal5279_generic_heavy_offload_worklist_reference_result_2026-07-09.md
history/internal_docs/goal5278_generic_heavy_offload_worklist_api_design_2026-07-09.md
```

## Review Questions

1. Is the retry/backlog scheduler consumer genuinely non-X-HD and non-Hausdorff?
2. Does it exercise active, miss, and deferred worklist rows behaviorally rather
   than only checking metadata?
3. Does the overflow control prove fail-closed behavior with no partial rows?
4. Is this enough genericity evidence for the reference helper to remain public,
   or should the helper be marked provisional until native telemetry exists?
5. Does the consumer avoid app identity leakage in RTDL core and in the
   consumer source?
6. Does the result avoid claiming X-HD Figure 11 reproduction, author memory
   parity, native backend completion, or performance?
7. Is Goal5281 correctly identified as the next substantive step?

## Requested Verdict Labels

Preferred approval label:

```text
approve_goal5280_heavy_offload_non_xhd_consumer_gate
```

If the non-X-HD consumer is not strong enough:

```text
revise_goal5280_non_xhd_consumer_too_weak
```

If the API should be provisional until native telemetry:

```text
approve_with_required_amendment_mark_heavy_worklist_api_provisional
```
