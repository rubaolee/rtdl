# Independent Gemini Review for Goal2752 Zero-Copy Ordering Metadata

**Review Date:** 2026-05-30

## Review Questions and Answers

### 1. Does Goal2752 correctly distinguish host-synchronized safety from event/same-stream zero-copy-compatible ordering?

Yes, Goal2752 correctly distinguishes these concepts.

*   **Evidence from `src/rtdsl/hit_stream_handoff.py`:** The code defines `GENERIC_HIT_STREAM_STREAM_ORDERING_STATES` to include `host_synchronized_before_consumer`, while `GENERIC_HIT_STREAM_ZERO_COPY_COMPATIBLE_STREAM_ORDERING_STATES` explicitly excludes it, only including `same_stream` and `producer_event_waited_by_consumer` (lines 57-63). The `RtdlHitStreamColumnHandoff.to_metadata()` method then sets `"host_synchronization_used"` to `True` only for `host_synchronized_before_consumer` and `"zero_copy_compatible_stream_ordering"` (and `"event_or_same_stream_ordering_proven"`) to `True` only for the states within `GENERIC_HIT_STREAM_ZERO_COPY_COMPATIBLE_STREAM_ORDERING_STATES` (lines 129-137).
*   **Evidence from `docs/reports/goal2752_hit_stream_zero_copy_ordering_metadata_2026-05-30.md`:** The "Purpose" section states, "a handoff can be safe to consume because the host synchronized before returning, but that is not the same as event/same-stream ordering for future no-sync zero-copy promotion." The "Classification" table further reinforces this by marking `host_synchronized_before_consumer` as "Host sync used: true" but "Future zero-copy-compatible ordering: false". In contrast, `same_stream` and `producer_event_waited_by_consumer` are marked "Host sync used: false" and "Future zero-copy-compatible ordering: true".
*   **Evidence from `tests/goal2752_hit_stream_zero_copy_ordering_metadata_test.py`:** The unit test `test_host_synchronized_is_safe_but_not_zero_copy_compatible_ordering` (lines 67-74) asserts that for `host_synchronized_before_consumer`, `metadata["host_synchronization_used"]` is `True` and `metadata["event_or_same_stream_ordering_proven"]` is `False`, directly validating the distinction in the metadata.

### 2. Does it preserve `true_zero_copy_authorized=False` everywhere?

Yes, the `true_zero_copy_authorized` flag remains `False` across all relevant contracts and metadata.

*   **Evidence from `src/rtdsl/hit_stream_handoff.py`:** The `to_metadata()` methods for `RtdlHitStreamColumnHandoff` (line 140) and `RtdlNativeDeviceHitStreamOutput` (line 231) explicitly set `"true_zero_copy_authorized": False`. Similarly, functions describing contracts like `describe_generic_device_resident_hit_stream_handoff_3d()` (line 431), `describe_v2_5_native_hit_stream_output_abi()` (line 478), `describe_v2_5_hit_stream_torch_carrier_adapter()` (line 630), `gather_typed_payload_columns_for_hit_stream()` (line 799), `_gather_payload_torch_carrier()`'s execution metadata (line 977), `plan_v2_5_hit_stream_partner_transfer()` (line 1172), and `plan_v2_5_hit_stream_partner_continuation()` (line 1277) all explicitly set their respective `true_zero_copy_authorized` or `true_zero_copy_claim_authorized` flags to `False`.
*   **Evidence from `docs/reports/goal2752_hit_stream_zero_copy_ordering_metadata_2026-05-30.md`:** The "Classification" table consistently shows "Current zero-copy authorized: false" for all defined ordering states. The "Boundary" section also explicitly states, "It does not add native OptiX event handles, does not remove `cuStreamSynchronize`, and does not authorize true zero-copy."
*   **Evidence from `tests/goal2752_hit_stream_zero_copy_ordering_metadata_test.py`:** The tests confirm this behavior, with assertions like `self.assertFalse(plan["true_zero_copy_authorized"])` in both `test_host_synchronized_is_safe_but_not_zero_copy_compatible_ordering` (line 74) and `test_event_and_same_stream_ordering_are_future_zero_copy_compatible_but_not_authorized` (line 90), and `self.assertFalse(metadata["true_zero_copy_authorized"])` in `test_native_output_metadata_uses_same_ordering_classification` (line 103).

### 3. Does it avoid claiming that the native OptiX event ABI is implemented?

Yes, Goal2752 carefully avoids claiming that a native OptiX event ABI is implemented; it focuses on metadata and planning.

*   **Evidence from `docs/reports/goal2752_hit_stream_zero_copy_ordering_metadata_2026-05-30.md`:** The "Boundary" section clearly states that Goal2752 is "metadata and planner claim hardening," and explicitly notes, "It does not add native OptiX event handles." The "Classification" table implies the continued use of host synchronization (`cuStreamSynchronize`) rather than a native event ABI by marking `host_synchronized_before_consumer` as `host_synchronization_used: true`.
*   **Evidence from `docs/research/future_version_to_do_list.md`:** Under the "v2.5+ Optimization Lane" for "Hit-Stream Continuation Promotion Gates After Goal2744", future work items explicitly include: "Add stream/event evidence that proves the OptiX producer and Triton consumer are ordered on real hardware without relying on device-wide synchronization." This indicates that such event-based ordering proof is a *future* goal, not a current implementation. The boundary for this section also states, "This is v2.x runtime hardening, not v3.0 shader injection," and "None of these items authorizes public speedup, true zero-copy, or release promotion without the normal report/review/consensus process," reinforcing that no such advanced ABI claim is being made.
*   **Evidence from `src/rtdsl/hit_stream_handoff.py`:** The `claim_boundary` in `RtdlNativeDeviceHitStreamOutput.to_metadata()` (lines 233-236) states: "This metadata describes native CUDA hit-stream column output. It does not authorize true zero-copy or performance claims without pod evidence proving same-pointer/no-host-stage behavior and lifetime cleanup." This wording indicates that the current capabilities are about describing CUDA output and not about a fully validated, native OptiX event ABI for zero-copy.

## Verdict

**Accept.** Goal2752 successfully clarifies and hardens the metadata contracts related to hit-stream ordering. It correctly distinguishes host-synchronized safety from zero-copy-compatible stream ordering, consistently maintains `true_zero_copy_authorized=False` across all relevant contracts, and explicitly avoids claiming the implementation of a native OptiX event ABI. This aligns with the goal's stated purpose of metadata and planner claim hardening, paving the way for future, more advanced zero-copy developments without premature claims.
