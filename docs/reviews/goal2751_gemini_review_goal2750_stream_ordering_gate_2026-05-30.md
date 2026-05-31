# Independent Gemini Review for Goal2750 Stream-Ordering Gate

**Reviewer:** Gemini Agent
**Date:** 2026-05-30

## Context

RTDL v2.5 is hardening generic device-resident hit-stream handoff and partner continuation. Goals2738/2746 established stream-ordering metadata, and Goal2740 planned cross-partner hit-stream transfer. Goal2750 fixes a planner-safety risk: before this change, a device-resident hit stream with `producer_consumer_stream_ordering="not_proven"` could still receive a transfer plan that looked executable for a device partner.

## Files Inspected

- `src/rtdsl/hit_stream_handoff.py`
- `tests/goal2750_hit_stream_transfer_stream_ordering_gate_test.py`
- `tests/goal2740_hit_stream_cross_partner_transfer_plan_test.py`
- `docs/reports/goal2750_hit_stream_transfer_stream_ordering_gate_2026-05-30.md`
- `docs/research/future_version_to_do_list.md`

## Expected Contract

- Device partners (`triton`, `cupy_conformance`, `numba`) require proven producer/consumer stream ordering before the planner allows device execution.
- If the columns are device-ready but ordering is `not_proven`, the planner returns `status="stream_ordering_proof_required"`.
- Event-ordered and host-synchronized handoffs may remain executable preview paths, but still do not authorize true zero-copy or public speedup claims.
- This is only a planner safety gate. It does not implement native OptiX event output and does not change the native ABI.

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

## Review Questions and Answers

1.  **Does the new `stream_ordering_proof_required` status correctly prevent unsynchronized device-column handoffs from being treated as executable?**
    *   **Answer:** Yes, the `plan_v2_5_hit_stream_partner_transfer` function in `src/rtdsl/hit_stream_handoff.py` correctly sets the status to "stream_ordering_proof_required" and `execution_allowed_without_copy` to `False` when `producer_consumer_stream_ordering` is "not_proven" for device partners (`triton`, `cupy_conformance`, `numba`). This is verified by `tests/goal2750_hit_stream_transfer_stream_ordering_gate_test.py` and `tests/goal2740_hit_stream_cross_partner_transfer_plan_test.py`, and explicitly stated in `docs/reports/goal2750_hit_stream_transfer_stream_ordering_gate_2026-05-30.md`.

2.  **Are event-ordered and host-synchronized paths still allowed only as preview, with `true_zero_copy_authorized=False`?**
    *   **Answer:** Yes, for `producer_event_waited_by_consumer` and `host_synchronized_before_consumer` orderings, the status is "torch_carrier_preview" or "cuda_descriptor_preview", and `execution_allowed_without_copy` is `True`. However, `true_zero_copy_authorized` and `public_speedup_claim_authorized` remain `False`, as confirmed by the test cases and the `docs/reports/goal2750_hit_stream_transfer_stream_ordering_gate_2026-05-30.md` report.

3.  **Are the claim boundaries conservative and clear?**
    *   **Answer:** Yes, the claim boundaries are conservative and clear. `src/rtdsl/hit_stream_handoff.py` explicitly sets `true_zero_copy_authorized` and `public_speedup_claim_authorized` to `False` in relevant metadata. The `docs/reports/goal2750_hit_stream_transfer_stream_ordering_gate_2026-05-30.md` report clearly defines Goal2750 as a "planner safety gate, not a performance promotion" and explicitly states it "does not claim true zero-copy."

4.  **Is the future work correctly narrowed to native event/stream ordering rather than pretending Goal2750 already solved that?**
    *   **Answer:** Yes, the future work is correctly narrowed. `docs/reports/goal2750_hit_stream_transfer_stream_ordering_gate_2026-05-30.md` clarifies that "The actual future promotion target remains a native event/stream contract..." and `docs/research/future_version_to_do_list.md` outlines "Add stream/event evidence that proves the OptiX producer and Triton consumer are ordered on real hardware without relying on device-wide synchronization." This confirms that Goal2750 is not overstating its accomplishments and future work is clearly defined.

## Overall Verdict

accept
