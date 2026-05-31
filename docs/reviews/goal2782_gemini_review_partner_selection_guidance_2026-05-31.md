# Goal2782 - v2.5 Partner-Selection Guidance Review

**Review Date:** 2026-05-31

## Purpose of Review

This review assesses Goal2782, which aims to establish machine-readable guidance for partner selection based on lessons learned from Goal2780 and Goal2781. The primary objective is to ensure that the introduction of new preview kernels (specifically Triton) does not automatically imply their selection as the default or preferred partner, especially when existing evidence demonstrates them to be slower for certain workloads.

## Artifacts Reviewed

*   `src/rtdsl/v2_5_partner_selection_guidance.py`: Core implementation of the partner selection guidance logic and data structures.
*   `tests/goal2782_v2_5_partner_selection_guidance_test.py`: Unit tests verifying the functionality and adherence to claim boundaries.
*   `docs/reports/goal2782_v2_5_partner_selection_guidance_2026-05-31.md`: The official report detailing the purpose, changes, boundary, and validation for Goal2782.
*   `docs/reports/goal2780_pod_artifacts/goal2780_topk_adapter_triton_pod_69_30_85_171_2026-05-31.json`: Evidence artifact from Goal2780 for `grouped_topk_f64`.
*   `docs/reports/goal2781_pod_artifacts/goal2781_grouped_vector_sum_adapter_pod_69_30_85_171_2026-05-31.json`: Evidence artifact from Goal2781 for `grouped_vector_sum_f64x2`.

## Review Findings

### 1. Distinction between Preview Availability and Partner Selection

**Requirement:** "Check preview availability != partner selection."

*   **Finding:** The distinction is explicitly and robustly enforced.
    *   The `src/rtdsl/v2_5_partner_selection_guidance.py` code includes `preview_kernel_available_does_not_imply_auto_select = True` and uses `V2_5_PARTNER_SELECTION_GUIDANCE_CLAIM_BOUNDARY` to define what is not authorized.
    *   The `validate_v2_5_partner_selection_guidance` function includes specific checks to ensure this distinction is maintained.
    *   The test suite includes assertions (`self.assertTrue(guidance["preview_kernel_available_does_not_imply_auto_select"])`) confirming this behavior.
    *   The Goal2782 report clearly states: "**preview kernel available is not the same as selected partner.**"

### 2. Faithfulness of Ratios

**Requirement:** "Verify ratios faithful."

*   **Finding:** The performance ratios recorded in `v2_5_partner_selection_guidance.py` are faithful to the evidence presented in the Goal2780 and Goal2781 JSON artifacts.
    *   For `grouped_topk_f64` (Goal2780), the guidance min/max ratios (`47.28` and `150.90`) accurately reflect the range of `triton_vs_torch_ratio` values observed in `goal2780_pod_artifacts.json`.
    *   For `grouped_vector_sum_f64x2` (Goal2781), the guidance min/max ratios (`4.09` and `16.59`) accurately reflect the range of `triton_over_torch_ratio` values observed in `goal2781_pod_artifacts.json`.
    *   The test `test_topk_and_vector_sum_negative_guidance_is_machine_readable` includes assertions to verify these ratios.

### 3. Blocked Claims

**Requirement:** "Ensure claims blocked."

*   **Finding:** All specified claims are appropriately blocked throughout the implementation, testing, and documentation.
    *   `V2_5_PARTNER_SELECTION_GUIDANCE_CLAIM_BOUNDARY` in the source code explicitly lists unauthorized claims.
    *   The `V25PartnerSelectionGuidanceRow` dataclass raises `ValueError` if flags like `public_speedup_claim_authorized` are set to `True`, enforcing a "negative guidance" policy.
    *   The `validate_v2_5_partner_selection_guidance` function verifies that these flags remain `False`.
    *   The unit tests (`test_guidance_validates_and_keeps_claims_blocked`) confirm that these claims (`promoted_performance_path`, `public_speedup_claim_authorized`, `true_zero_copy_claim_authorized`, `release_readiness_authorized`) are all `False`.
    *   The Goal2782 report explicitly lists claims that "This goal does not authorize."

### 4. No New Pod Needed

**Requirement:** "Check no new pod needed."

*   **Finding:** It is confirmed that no new pod is needed for this goal. The Goal2782 report explicitly states that "No pod is required for this goal because it consumes the already-recorded Goal2780 and Goal2781 pod artifacts instead of producing new timing evidence." The artifact paths in the `src` file point directly to these existing JSON files, and the validation steps in the report demonstrate successful testing without new pod generation.

## Conclusion

Goal2782 successfully implements a critical guidance mechanism that prevents the automatic selection of preview partners solely based on their availability, especially when performance evidence indicates otherwise. The solution is well-designed, thoroughly tested, and clearly documented. The explicit claim boundaries and validation checks provide strong safeguards against premature or inaccurate claims.

## Verdict

**accept**