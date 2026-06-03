# Goal3115: Gemini Review of Goal3114 Hit-Stream Neutral-Seam Reconciliation

Date: 2026-06-03

## Verdict
**Accept.**

Goal3114 successfully implements a reference grouped-continuation consumer that reuses the existing v2.5 Python reference continuation executor, ensuring a consistent and established oracle for testing v2.8 typed stream contracts. The implementation correctly handles mapping for various grouped operations and rigorously maintains the "false" status for all advanced claims, aligning with its role as an internal reference.

## Findings by Severity

### Critical Findings
None.

### High-Severity Findings
None.

### Medium-Severity Findings
None.

### Low-Severity Findings
None.

## Review Questions Addressed

### 1. Does Goal3114 reuse existing v2.5 Python reference continuation executor instead of inventing a second oracle?
**Yes.** The `execute_segmented_typed_stream_reference_continuation` function in `src/rtdsl/v2_8_segmented_typed_stream_adapter.py` explicitly imports and utilizes `execute_v2_5_partner_continuation_reference` from `.partner_continuation_protocol`. This directly reuses the established v2.5 Python reference continuation executor, avoiding the creation of a new, potentially divergent oracle.

### 2. Does adapter-to-reference mapping correctly cover grouped argmax, segmented sum, top-k k handling, and listed operations at contract level?
**Yes.** The `_reference_inputs_for_plan` helper function in the adapter module correctly translates the `V28GroupedContinuationPlan` into the input format required by the v2.5 reference executor.
-   **Grouped Argmax:** The logic for `grouped_argmax_f64` properly extracts `item_ids` and `scores`. This is validated by `test_reference_consumer_executes_grouped_argmax_oracle` in the test suite.
-   **Segmented Sum:** The `segmented_sum_f64` case correctly processes the `values` column. This is validated by `test_reference_consumer_executes_segmented_sum_oracle`.
-   **Top-K k handling:** For `grouped_topk_f64`, the implementation includes a `ValueError` check if `k` is not provided, demonstrating fail-closed behavior. When `k` is supplied, it is correctly passed through. This behavior is covered by `test_reference_consumer_requires_k_for_topk`.
-   **Listed Operations:** The `_reference_inputs_for_plan` function shows explicit handling for all listed operations: `segmented_count_i64`, `segmented_sum_f64`, `segmented_min_f64`, `segmented_max_f64`, `grouped_vector_sum_f64x2`, `grouped_argmin_f64`, `grouped_argmax_f64`, `grouped_topk_f64`, `bounded_collect_finalize_i64`, and `compact_mask_i64`.

### 3. Does it keep all native producer/partner consumer/device residency/zero-copy/release/speedup/RT-core/hidden-dispatch/app-specific-engine/user-shader claims false?
**Yes.** All such advanced claims are explicitly and consistently set to `False` throughout the implementation:
-   The `V28SegmentedTypedStreamAdapterResult` dataclass initializes these boolean flags as `False`.
-   Its `__post_init__` method contains a safeguard that raises a `ValueError` if any of these flags are unexpectedly set to `True`.
-   The `validate_segmented_typed_stream_adapter` function includes checks to ensure these fields remain `False` in the adapter's metadata.
-   The output of `execute_segmented_typed_stream_reference_continuation` explicitly sets these fields to `False`.
-   The `V2_8_SEGMENTED_TYPED_STREAM_ADAPTER_CLAIM_BOUNDARY` string clearly defines the limited scope and non-authorizing nature of this adapter.
-   The `test_adapter_summary_is_internal_and_non_authorizing` test, along with specific assertions in other tests, confirms these claims remain `False`.

## Claim Boundary

Goal3114's claim boundary is well-defined and consistently enforced:
"v2.8 segmented typed stream adapter bridges an existing segmented row stream into the typed result-stream contract for local contract testing. It does not prove device residency, true zero-copy, release readiness, public speedup, broad RT-core acceleration, hidden dispatch, hidden partner selection, app-specific native-engine behavior, or user-defined shader injection."

This boundary is crucial for managing expectations and clearly delineating the capabilities of this reference implementation.

## Files Inspected

-   `src/rtdsl/v2_8_segmented_typed_stream_adapter.py`
-   `tests/goal3111_v2_8_segmented_typed_stream_adapter_test.py`
-   `docs/reports/goal3114_v2_8_reference_grouped_continuation_consumer_2026-06-03.md`

## Next Step

As outlined in the `docs/reports/goal3114_v2_8_reference_grouped_continuation_consumer_2026-06-03.md`, the next step for v2.8 should be to:
"select one benchmark subpath and replace either the reference producer or reference consumer with a real native/partner implementation that emits or consumes the same typed stream contract. That next step will need pod validation when it touches OptiX or partner GPU execution."
