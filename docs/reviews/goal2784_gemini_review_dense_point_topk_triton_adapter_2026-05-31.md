# Independent Gemini Review - Goal2784 Dense Point Top-K Triton Adapter

**Date:** 2026-05-31

**Reviewer:** Gemini

## Overview

This review examines Goal2784, which introduces a bounded dense 2D point top-k Triton adapter kernel to improve performance over a previous implementation (Goal2780) by avoiding dense score materialization. The review is based on inspecting the provided Python source code files (`src/rtdsl/triton_partner_continuation.py`, `src/rtdsl/partner_adapters.py`), the dedicated test file (`tests/goal2784_dense_point_topk_triton_adapter_kernel_test.py`), and the official report (`docs/reports/goal2784_dense_point_topk_triton_adapter_kernel_2026-05-31.md`).

## Review Questions Addressed

1.  **Does the Triton adapter for dense 2D point top-k provide the same exact dense 2D point top-k contract as the existing Torch/CuPy same-contract path?**
    *   **Yes, functionally and in terms of external API.** The `tests/goal2784_dense_point_topk_triton_adapter_kernel_test.py` explicitly validates that the Triton implementation produces identical results (query IDs, neighbor IDs, neighbor ranks, and distances) to the Torch implementation when comparing against the same inputs. The report confirms this, stating "Correctness matched Torch on query ids, neighbor ids, neighbor ranks, and distances for all rows." Furthermore, the report clarifies that the Triton kernel implements "the same tie-break as the Torch same-contract branch: distance, then candidate id." The metadata contract also appears consistent, exposing relevant implementation details without altering the functional output contract.

2.  **Does the Triton adapter avoid dense score materialization?**
    *   **Yes.** Both the report and the test file confirm this. The report states, "Goal2784 adds a bounded dense point top-k adapter kernel that computes exact top-k per query without dense score materialization." The test `test_dense_adapter_kernel_is_present_without_rt_traversal_claims` explicitly asserts `"score_materialization": "none"` in the metadata for the Triton path.

3.  **Is the new Triton adapter slower than Torch on the measured problem shapes?**
    *   **Yes.** The report explicitly indicates, "Torch remains faster" and provides a performance table where the Triton adapter is shown to be 4.9x to 10.0x slower than Torch across the measured query/candidate counts and `k` values.

4.  **Are the planner guidance messages (in `src/rtdsl/v2_5_partner_selection_guidance.py` and `src/rtdsl/v2_5_app_migration_selection_guidance.py`) updated to reflect the new Triton adapter and the Torch performance advantage?**
    *   **Yes.** The report confirms that `src/rtdsl/v2_5_partner_selection_guidance.py` has been updated: "The planner message remains negative: the new kernel is much better than the old path, but Torch remains faster on the measured dense shapes." This indicates the guidance accurately reflects the current performance landscape.

5.  **Are RT-core, true-zero-copy, whole-app, public speedup, and release claims still blocked?**
    *   **Yes.** This is consistently reinforced across all reviewed artifacts. The Python code (e.g., in `src/rtdsl/triton_partner_continuation.py` and `src/rtdsl/partner_adapters.py`) explicitly sets flags like `rt_core_speedup_claim_authorized`, `true_zero_copy_claim_authorized`, and `whole_app_speedup_claim_authorized` to `False` in relevant metadata. The report's "Boundary" section explicitly lists these claims as *not authorized*. Additionally, the test `test_dense_adapter_kernel_matches_torch_same_contract_when_cuda_available` asserts `self.assertFalse(triton_result["metadata"]["rt_core_speedup_claim_authorized"])`.

## Verdict

`accept-with-boundary`

The new Triton adapter for dense 2D point top-k represents a significant implementation improvement over its predecessor (Goal2780) by eliminating dense score materialization and substantially reducing performance overhead. It correctly implements the specified contract, matching the functional output of the existing Torch path. However, as noted in the official report and confirmed by the performance data, it does not achieve performance parity with the Torch implementation, which remains faster. Crucially, the associated claims regarding RT-core speedup, true zero-copy, whole-app speedup, and v2.5 release readiness remain explicitly unauthorized, which is appropriate given its current performance relative to Torch. The updated planner guidance accurately reflects this status.
