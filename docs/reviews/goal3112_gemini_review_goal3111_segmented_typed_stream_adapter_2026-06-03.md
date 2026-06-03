# Goal3112: Gemini Review of Goal3111 Segmented Typed-Stream Adapter

Date: 2026-06-03

## Verdict

**Accept**

## Summary of Findings

The `v2_8_segmented_typed_stream_adapter.py` module successfully bridges the `SegmentedRowStream` to the `V28TypedResultStreamContract` and, optionally, a `V28GroupedContinuationPlan`. The design adheres to the specified non-authorization of advanced claims (device-residency, zero-copy, etc.) and explicitly enforces fail-closed behavior for overflow, status values, and partner choice. The `host_reference_contract_adapter` materialization token clearly defines its role as a local reference target, making it safe for pre-native producer/partner consumer work.

### Files Inspected

*   `src/rtdsl/v2_8_segmented_typed_stream_adapter.py`
*   `tests/goal3111_v2_8_segmented_typed_stream_adapter_test.py`

### Review Questions & Answers

1.  **Does the adapter bridge SegmentedRowStream to typed result-stream contract?**
    *   **Finding:** Yes. The `build_segmented_typed_stream_adapter` function takes `rows` (which are processed into a `SegmentedRowStream`) and constructs a `V28TypedResultStreamContract` using `make_typed_result_stream_contract`. It maps row-schema fields to typed result-stream column roles and builds required status columns.
    *   **Severity:** N/A (Core functionality)

2.  **Does it preserve fail_closed_overflow/status values/explicit partner choice/grouped validation?**
    *   **Finding:** Yes.
        *   **`fail_closed_overflow`**: The `test_adapter_preserves_segmented_overflow_fail_closed` test case explicitly verifies that `SegmentedRowStreamOverflowError` is raised when `total_row_capacity` is exceeded. The `V28SegmentedTypedStreamAdapterResult` also records `overflow` status.
        *   **`status values`**: The `to_metadata` method and validation logic correctly capture and check `row_count`, `capacity`, `overflow`, and `complete_candidate_coverage`.
        *   **`explicit partner choice`**: The `build_segmented_typed_stream_adapter` function explicitly checks for `user_selected_partner` and raises a `ValueError` if "auto" is used, as demonstrated by `test_adapter_rejects_missing_role_and_auto_partner`.
        *   **`grouped validation`**: If an `operation` is provided, a `V28GroupedContinuationPlan` is created, and its validation is performed within `V28SegmentedTypedStreamAdapterResult.__post_init__` and `validate_segmented_typed_stream_adapter`.
    *   **Severity:** N/A (Core functionality)

3.  **Does it keep device-residency/zero-copy/release/speedup/RT-core/hidden-dispatch/app-specific-engine claims false?**
    *   **Finding:** Yes. The `V28SegmentedTypedStreamAdapterResult` dataclass initializes `native_producer_promoted`, `partner_consumer_promoted`, `device_resident_result_stream_proven`, `true_zero_copy_claim_authorized`, `release_authorized`, `public_speedup_claim_authorized`, `rt_core_speedup_claim_authorized`, `hidden_dispatch_allowed`, `automatic_partner_selection_allowed`, and `app_specific_engine_logic_allowed` to `False`. A `ValueError` is raised in `__post_init__` if any of these fields are set to `True` during instantiation. The `validate_segmented_typed_stream_adapter` function also explicitly asserts that these fields remain `False`. The `V2_8_SEGMENTED_TYPED_STREAM_ADAPTER_CLAIM_BOUNDARY` constant clearly defines these limitations.
    *   **Severity:** N/A (Core functionality/Safety)

4.  **Is host_reference_contract_adapter safe as a local reference target before native producer/partner consumer work?**
    *   **Finding:** Yes. The `V2_8_SEGMENTED_TYPED_STREAM_ADAPTER_MATERIALIZATION` is set to "host_reference_contract_adapter," and the code explicitly prevents any "promotion" claims. This clearly signals that the adapter is for local contract testing and does not imply performance or native integration. The dedicated claim boundary string reinforces this safety.
    *   **Severity:** N/A (Architectural safety)

### Claim Boundary

The claim boundary is clearly and correctly defined by `V2_8_SEGMENTED_TYPED_STREAM_ADAPTER_CLAIM_BOUNDARY`, which states that this adapter:

"bridges an existing segmented row stream into the typed result-stream contract for local contract testing. It does not prove device residency, true zero-copy, release readiness, public speedup, broad RT-core acceleration, hidden dispatch, hidden partner selection, app-specific native-engine behavior, or user-defined shader injection."

This boundary is consistently enforced in the code and tests.

### Next Step

The module is well-designed and tested for its stated purpose. The next logical step, as also outlined in the `goal3111_v2_8_segmented_typed_stream_adapter_2026-06-03.md` report, is to replace the host-reference producer in a narrow benchmark subpath with a real typed-stream producer or consumer. This will allow for performance comparison against this stable reference contract without modifying the established claim boundary. Ranked-summary or bounded-witness paths are good candidates.