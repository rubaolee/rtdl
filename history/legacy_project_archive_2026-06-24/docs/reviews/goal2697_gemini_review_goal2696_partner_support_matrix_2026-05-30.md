# Goal2697: Independent Gemini Review of Goal2696 Partner Support Matrix

Reviewer: Gemini
Date: 2026-05-30
Responds to: `docs/reports/goal2696_v2_5_partner_support_matrix_2026-05-30.md`

## Verdict

**accept-with-boundary.**

## Review Answers

### 1. Does Goal2696 correctly make the `(partner x operation)` support envelope explicit without forcing a partner or overclaiming performance?

Yes, Goal2696 correctly makes the `(partner x operation)` support envelope explicit. The `V25PartnerSupportCell` class in `src/rtdsl/v2_5_partner_support_matrix.py` rigorously enforces that `promoted_performance_path`, `rt_traversal_replacement_allowed`, `public_speedup_claim_authorized`, and `true_zero_copy_claim_authorized` are all `False`, preventing overclaiming. The `v2_5_partner_support_matrix()` function explicitly sets `no_partner_forced=True` and `unsupported_cells_fail_closed=True`, ensuring no partner is implicitly forced. The accompanying report and code clearly define the status for each partner and operation, making the support envelope transparent and machine-readable.

### 2. Is the policy correct: universal Python reference, Triton preview for all current preview operations, Numba preview only for count/sum, CuPy descriptor conformance only?

Yes, the policy is correctly implemented as described. The `Matrix Policy` section in the report `docs/reports/goal2696_v2_5_partner_support_matrix_2026-05-30.md` accurately outlines these rules. This is reflected in `src/rtdsl/v2_5_partner_support_matrix.py` where:
- `python_reference` is universally set to `V2_5_SUPPORT_STATUS_REFERENCE`.
- `triton` is universally set to `V2_5_SUPPORT_STATUS_PREVIEW`.
- `numba` is set to `V2_5_SUPPORT_STATUS_PREVIEW` only for `segmented_count_i64` and `segmented_sum_f64`, failing closed as `V2_5_SUPPORT_STATUS_UNSUPPORTED` for all other operations.
- `cupy_conformance` is universally set to `V2_5_SUPPORT_STATUS_DESCRIPTOR`.
These policies are actively validated during cell creation and matrix validation.

### 3. Does the matrix fail closed for unsupported cells and keep RT traversal replacement, public speedup, and zero-copy claims false?

Yes, the matrix fails closed for unsupported cells and strictly keeps RT traversal replacement, public speedup, and zero-copy claims false. The `V25PartnerSupportCell` class contains checks that raise `ValueError` if `promoted_performance_path`, `rt_traversal_replacement_allowed`, `public_speedup_claim_authorized`, or `true_zero_copy_claim_authorized` are set to `True`. The `v2_5_partner_support_cells()` function explicitly initializes these flags to `False` for all cells. Unsupported Numba operations are marked with `status=V2_5_SUPPORT_STATUS_UNSUPPORTED` and provide explanatory notes. The `validate_v2_5_partner_support_matrix` function confirms that these claims remain `False` across the entire matrix.

### 4. Is this useful enough for app-boundary planning before pod execution?

Yes, this matrix is highly useful for app-boundary planning before pod execution. Goal2696 is explicitly framed as a "no-pod contract and planning milestone" aimed at making the partner-choice envelope explicit. The `plan_v2_5_partner_support(operation, partner)` function provides a clear, programmatic interface to query support status. This enables downstream code, such as benchmark planning or application logic, to check chosen `(partner x operation)` combinations against a defined, honest envelope, preventing undefined behavior and aligning with the principles of "partner selection is the app's choice" and "no partner is ever forced," as articulated in `docs/reports/v2_5_partner_choice_and_multi_partner_composition_design_2026-05-29.md`.

### 5. Are the tests and Windows/Linux validations sufficient for a no-pod contract milestone?

Yes, the tests and Windows/Linux validations are sufficient for this "no-pod" contract milestone. The `docs/reports/goal2696_v2_5_partner_support_matrix_2026-05-30.md` details successful `unittest` runs on both platforms for `tests.goal2696_v2_5_partner_support_matrix_test.py` and related contract tests. The tests cover:
- Verification of full `(partner x operation)` coverage.
- Validation of claim boundedness for reference and Triton cells.
- Confirmation of the intentionally narrow Numba preview.
- Assurance that CuPy conformance cells are descriptor-only.
- Checks that support-matrix symbols are experimental and not exported.
These validations adequately confirm the logical correctness and adherence to policy for a metadata-focused milestone that does not involve performance measurement on a pod.

### 6. What blockers remain before native OptiX CUDA-resident hit-column output?

The successful review of Goal2696 addresses the "Establishing a v2.5 Support Matrix" blocker. However, several other significant blockers, primarily identified in `docs/reports/v2_5_partner_choice_and_multi_partner_composition_design_2026-05-29.md` and detailed in `docs/reviews/goal2695_gemini_review_goal2694_hit_stream_neutral_seam_metadata_2026-05-30.md`, remain before native OptiX CUDA-resident hit-column output can commence:

1.  **Refactoring Torch-centric `hit_stream_handoff.py`:** The current implementation contains Torch-specific coercion logic that must be refactored to use a genuinely neutral buffer seam (DLPack / `__cuda_array_interface__`). This is critical for realizing "X's choice" and multi-partner composition without hidden copies.
2.  **Full Native Ownership/Lifetime Model Implementation:** The `neutral_buffer_seam` currently uses `"native_owned_pending_state_machine"`. The actual state machine for CUDA allocation, retention, release, and failure cleanup across partners needs to be fully designed and implemented.
3.  **Addressing Broader System Deficiencies in `hit_stream_handoff.py`:** Remaining issues and unproven claims in `hit_stream_handoff.py` (e.g., related to `caller_asserted` validation and `removes_host_materialization_bottleneck`) must be resolved for complete honesty and consistency.
4.  **Implementation of Native OptiX CUDA Output:** The core engineering task of producing bounded `ray_ids:int64`/`primitive_ids:int64` in CUDA-resident buffers directly from OptiX remains.
5.  **Performance Measurement and Pod Validation:** Gathering `sm_70+` pod evidence, measuring same-pointer/no-host-stage evidence, and accurately separating phase timings are necessary to authorize any zero-copy or public speedup claims.
6.  **Reduction Tolerance Policy:** A robust float tolerance policy is required for validating device/Triton float results against CPU references, which is a prerequisite for correctly gating future partner performance.

## Conclusion

Goal2696 successfully establishes a clear, explicit, and conservative `(partner x operation)` support matrix for v2.5. It correctly implements the policy of universal Python reference, narrow Numba preview, broad Triton preview, and CuPy conformance, while rigorously rejecting overclaims of performance, zero-copy, or RT traversal replacement. The provided tests and validations are sufficient for this metadata-focused milestone. While this goal marks a significant step in defining the partner-choice envelope, the listed blockers, particularly regarding the neutral buffer seam's complete neutrality and the cross-partner ownership model, must be addressed to fully enable honest native OptiX CUDA-resident hit-column output and multi-partner composition.
