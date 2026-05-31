# Goal2778 - v2.5 Grouped Vector Sum - Gemini Review

Date: 2026-05-31

## Purpose

Goal2778 adds the generic two-component vector reduction needed before
Barnes-Hut-style benchmark adapters can move from legacy CuPy/Torch continuation
paths toward the v2.5 Triton partner surface:

`grouped_vector_sum_f64x2`

This is not a Barnes-Hut force primitive. It sums paired float64 components per
integer group. App code owns the meaning of those components.

## Review Verdict

`accept-with-boundary`

## Review Questions & Answers

### 1. Confirm `grouped_vector_sum_f64x2` is generic and not Barnes-Hut/app-specific.

**Confirmed.** The `grouped_vector_sum_f64x2` operation is defined as generic within `src/rtdsl/partner_continuation_protocol.py`. The `app_specific_semantics_allowed` flag is explicitly `False` in its `RtdlPartnerContinuationOperation` definition, and its behavior description explicitly states that "App code owns the meaning of those components," indicating it is not Barnes-Hut or app-specific. This is further reinforced by the `RtdlPartnerContinuationSpec` validation that rejects app-specific semantics.

### 2. Confirm reference semantics are componentwise sums per group with zero for empty groups.

**Confirmed.** The Python reference implementation in `src/rtdsl/partner_continuation_protocol.py` (`_grouped_vector_sum_f64x2`) initializes sum arrays (`sum_x`, `sum_y`) with zeros for all groups. It then iterates through `group_ids`, `values_x`, and `values_y`, performing independent componentwise summations (`sum_x[group] += value_x`, `sum_y[group] += value_y`). This ensures that any group not present in `group_ids` correctly retains a sum of `0.0`. This behavior is explicitly documented in `docs/reports/goal2778_v2_5_grouped_vector_sum_2026-05-31.md` and verified by `tests/goal2778_v2_5_triton_grouped_vector_sum_preview_test.py`.

### 3. Confirm the Triton preview mirrors the reference shape with paired atomic-add component sums and no RawKernel.

**Confirmed.** The Triton preview implementation in `src/rtdsl/triton_partner_continuation.py` uses a dedicated JIT kernel (`_triton_grouped_vector_sum_f64x2_kernel`). This kernel initializes output tensors (`sum_x`, `sum_y`) with zeros using `torch.zeros`, thus mirroring the reference shape for empty groups. The kernel then performs paired `tl.atomic_add` operations for `output_x` and `output_y` independently, ensuring componentwise summation. The code explicitly avoids and guards against the use of RawKernel, with `raw_kernel_required=False` in its descriptors and test assertions confirming its absence. The `tests/goal2778_v2_5_triton_grouped_vector_sum_preview_test.py` also validates that the Triton results match the reference.

### 4. Confirm the support matrix is honest: reference contract exists, Triton is preview-not-promoted, Numba fails closed, CuPy is descriptor-only.

**Confirmed.** The support matrix generation logic in `src/rtdsl/v2_5_partner_support_matrix.py` and the verification in `tests/goal2778_v2_5_triton_grouped_vector_sum_preview_test.py` consistently show the following:
*   `python_reference`: `reference_contract`
*   `triton`: `preview_not_promoted` (with a note indicating "preview kernel exists; benchmark promotion still requires pod evidence")
*   `numba`: `unsupported_fail_closed` (as Numba does not implement grouped vector sum)
*   `cupy_conformance`: `descriptor_only` (with a note that "CuPy remains an app-chosen conformance/interoperability partner; generic v2.5 kernels are not promoted here")
This accurately reflects the current status of each partner's support for `grouped_vector_sum_f64x2`.

### 5. Confirm no public speedup, release, true-zero-copy, RT traversal replacement, or Barnes-Hut force-accuracy claim is introduced.

**Confirmed.** All listed claims are explicitly disclaimed or set to `False` across the codebase:
*   `V2_5_PERFORMANCE_PATH_AUTHORIZED`, `V2_5_RT_TRAVERSAL_REPLACEMENT_ALLOWED`, `V2_5_RAWKERNEL_REQUIRED_ALLOWED`, `V2_5_PREVIEW_RELEASE_TAG_AUTHORIZED`, and `V2_5_PREVIEW_PUBLIC_SPEEDUP_CLAIM_AUTHORIZED` are all `False` in `src/rtdsl/partner_continuation_protocol.py`.
*   Validation logic in `RtdlPartnerContinuationSpec` and `V25PartnerSupportCell` actively rejects any attempt to enable these claims prematurely.
*   `_base_triton_descriptor()` and `_triton_group_id_bounds_validation_metadata()` in `src/rtdsl/triton_partner_continuation.py` explicitly set `promoted_performance_path`, `rt_core_speedup_claim_authorized`, `replaces_rt_traversal`, and `true_zero_copy_claim_authorized` to `False`.
*   The **Boundary** section in `docs/reports/goal2778_v2_5_grouped_vector_sum_2026-05-31.md` clearly states, "This is not a public speedup claim, release claim, true-zero-copy claim, Barnes-Hut force-accuracy claim, or whole-app benchmark result."

### 6. List blockers or follow-ups before Barnes-Hut-style app adapters consume this operation.

Based on the `v2_5_partner_preview_gate()` in `src/rtdsl/partner_continuation_protocol.py`, the notes in `src/rtdsl/v2_5_partner_support_matrix.py`, and the report boundary, the following blockers and follow-ups must be addressed before Barnes-Hut-style app adapters can fully consume this operation:

1.  **Full RT hit-stream handoff:** The integration with the real-time ray tracing hit-stream is incomplete.
2.  **Benchmark integration:** The `grouped_vector_sum_f64x2` operation needs to be fully integrated into the project's benchmarking framework and thoroughly validated for performance characteristics.
3.  **Optimized performance path:** While a preview kernel exists, further work is needed to develop and validate an optimized performance path.
4.  **External 3-AI consensus:** Achieving consensus from relevant external AI teams or stakeholders is a pending requirement.
5.  **Public release tag authorization:** A formal authorization for a public release tag needs to be obtained.
6.  **Public speedup claim authorization:** Authorization for any public claims regarding performance speedup is not yet granted.
7.  **Benchmark promotion (requiring pod evidence):** The current Triton preview status requires additional "pod evidence" (e.g., performance validation on specific hardware configurations) before it can be promoted to a stable, generally consumable state for benchmark-focused applications.

## Conclusion

The implementation of `grouped_vector_sum_f64x2` adheres to the specified contract and design principles, particularly regarding genericity, reference semantics, and the cautious staging of its Triton preview. All claims are appropriately bounded, and necessary gates are in place. The identified blockers and follow-ups are consistent with the current preview status and provide a clear path forward for full consumption by app adapters.
