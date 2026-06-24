# Goal2779 - v2.5 Edge-List Components: Gemini Review

**Date:** 2026-05-31

**Reviewer:** Gemini

## Review Questions & Findings

1.  **Confirm `edge_list_components_i64` is generic and not DBSCAN/app-specific.**
    *   **Finding:** Confirmed. The `docs/reports/goal2779_v2_5_edge_list_components_2026-05-31.md` explicitly states: "This is not a DBSCAN primitive. It labels connected components over a caller supplied undirected edge list. App code owns the meaning of the edges and any cluster policy." The `tests/goal2662_v2_5_partner_continuation_contract_test.py` further reinforces this by asserting the operation set is generic and app-agnostic, checking for forbidden native app tokens.

2.  **Confirm reference semantics label components by smallest node id.**
    *   **Finding:** Confirmed. The `docs/reports/goal2779_v2_5_edge_list_components_2026-05-31.md` contract section specifies: "labels use the smallest node id in each component." This behavior is explicitly tested and verified in `tests/goal2779_v2_5_triton_edge_list_components_preview_test.py` (`test_reference_components_label_by_smallest_node_id`). The Triton implementation also utilizes `tl.atomic_min` as observed in `src/rtdsl/triton_partner_continuation.py` and confirmed by tests.

3.  **Confirm the Triton preview mirrors the reference shape with min-label propagation kernels and no RawKernel.**
    *   **Finding:** Confirmed. The `docs/reports/goal2779_v2_5_edge_list_components_2026-05-31.md` mentions the Triton preview uses "fixed-iteration min-label propagation" and "a relaxation kernel using `tl.atomic_min`" and a "compression kernel for iterative label propagation". The `tests/goal2779_v2_5_triton_edge_list_components_preview_test.py` (`test_triton_edge_list_components_descriptor_is_preview_not_promoted` and `test_source_uses_triton_component_kernels_and_no_rawkernel`) explicitly assert the algorithm is `fixed_iteration_min_label_propagation` and confirms the presence of `tl.atomic_min` usage and absence of `RawKernel` in the Triton source.

4.  **Confirm the support matrix is honest: reference contract exists, Triton is preview-not-promoted, Numba fails closed, CuPy is descriptor-only.**
    *   **Finding:** Confirmed. The "Partner status" table in `docs/reports/goal2779_v2_5_edge_list_components_2026-05-31.md` explicitly states these statuses for `python_reference`, `triton`, `numba`, and `cupy_conformance`. The `tests/goal2779_v2_5_triton_edge_list_components_preview_test.py` (`test_preview_kernel_set_and_support_matrix_include_edge_components`) explicitly verifies these statuses using `rt.plan_v2_5_partner_support`. The `src/rtdsl/v2_5_partner_support_matrix.py` also defines these statuses and enforces them via `ValueError` exceptions.

5.  **Confirm no public speedup, release, true-zero-copy, RT traversal replacement, or DBSCAN cluster-quality claim is introduced.**
    *   **Finding:** Confirmed. The "Boundary" section in `docs/reports/goal2779_v2_5_edge_list_components_2026-05-31.md` explicitly states: "This is not a public speedup claim, release claim, true-zero-copy claim, DBSCAN cluster-quality claim, or whole-app benchmark result." This is further enforced by checks in `src/rtdsl/v2_5_partner_support_matrix.py` and asserted in `tests/goal2662_v2_5_partner_continuation_contract_test.py` and `tests/goal2671_v2_5_preview_gate_test.py` for various contract and gate properties.

6.  **List blockers or follow-ups before DBSCAN-style app adapters consume this operation, especially convergence and benchmark-promotion risks.**
    *   **Blockers/Follow-ups:**
        *   **Benchmark Promotion:** The `docs/reports/goal2779_v2_5_edge_list_components_2026-05-31.md` explicitly states: "benchmark promotion requires a canonical app adapter, convergence policy, and large-scale pod evidence." This is the primary blocker for promoting the Triton preview to a generally usable state for app adapters.
        *   **Convergence Policy:** The `max_iterations` input parameter means that the caller (DBSCAN-style app adapter) is responsible for choosing a value that ensures convergence for its specific graph and use case. The primitive itself does not guarantee convergence or provide a convergence mechanism.
        *   **App Adapter Development:** A "canonical app adapter" is required to integrate this generic primitive into DBSCAN-style applications, defining how the operation is used and how its outputs are interpreted within the larger application context.
        *   **"Preview-Not-Promoted" Status:** The current status of the Triton implementation (`preview_not_promoted`) indicates that it is not yet considered production-ready or authorized for public claims.

## Verdict

**`accept-with-boundary`**

The implementation of `edge_list_components_i64` and its associated Triton preview align well with the stated goals and design principles. The component is generic, the reference semantics are accurately implemented, and the support matrix honestly reflects the current preview status. Crucially, the boundaries around what this goal *does not* claim (e.g., public speedup, DBSCAN cluster-quality claims) are clear and enforced through code and documentation.

The explicit need for "a canonical app adapter, convergence policy, and large-scale pod evidence" before benchmark promotion serves as a well-defined boundary for future work and prevents premature claims. The current implementation provides a solid foundation for subsequent integration efforts.
