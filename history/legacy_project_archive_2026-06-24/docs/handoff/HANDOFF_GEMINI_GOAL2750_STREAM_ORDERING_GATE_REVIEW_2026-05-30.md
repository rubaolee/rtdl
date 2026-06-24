# Handoff: Gemini Review For Goal2750 Stream-Ordering Gate

Please perform an independent read-only review of Goal2750 and write your
review to:

`docs/reviews/goal2751_gemini_review_goal2750_stream_ordering_gate_2026-05-30.md`

## Context

RTDL v2.5 is hardening generic device-resident hit-stream handoff and partner
continuation. Goals2738/2746 established stream-ordering metadata, and Goal2740
planned cross-partner hit-stream transfer.

Goal2750 fixes a planner-safety risk: before this change, a device-resident
hit stream with `producer_consumer_stream_ordering="not_proven"` could still
receive a transfer plan that looked executable for a device partner.

## Files To Inspect

- `src/rtdsl/hit_stream_handoff.py`
- `tests/goal2750_hit_stream_transfer_stream_ordering_gate_test.py`
- `tests/goal2740_hit_stream_cross_partner_transfer_plan_test.py`
- `docs/reports/goal2750_hit_stream_transfer_stream_ordering_gate_2026-05-30.md`
- `docs/research/future_version_to_do_list.md`

## Expected Contract

- Device partners (`triton`, `cupy_conformance`, `numba`) require proven
  producer/consumer stream ordering before the planner allows device execution.
- If the columns are device-ready but ordering is `not_proven`, the planner
  returns `status="stream_ordering_proof_required"`.
- Event-ordered and host-synchronized handoffs may remain executable preview
  paths, but still do not authorize true zero-copy or public speedup claims.
- This is only a planner safety gate. It does not implement native OptiX event
  output and does not change the native ABI.

## Validation Already Run By Codex

Local Windows:

```text
Ran 24 tests in 0.035s
OK (skipped=2)
```

Pod:

```text
Ran 24 tests in 0.610s
OK
```

## Review Questions

1. Does the new `stream_ordering_proof_required` status correctly prevent
   unsynchronized device-column handoffs from being treated as executable?
2. Are event-ordered and host-synchronized paths still allowed only as preview,
   with `true_zero_copy_authorized=False`?
3. Are the claim boundaries conservative and clear?
4. Is the future work correctly narrowed to native event/stream ordering rather
   than pretending Goal2750 already solved that?

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`.
