# Gemini Independent Review - Goal2776 Grouped Argmax Witness Reduction

**Verdict: accept**

## Review of Required Checks

### 1. Confirm the new operation name, fields, and semantics are generic.

**Findings:**
The new operation `grouped_argmax_f64` is defined in `src/rtdsl/partner_continuation_protocol.py` within the `V2_5_PARTNER_CONTINUATION_OPERATIONS` tuple. Its fields are `group_ids`, `item_ids`, `scores`, and `group_count` for inputs, and `group_ids`, `item_ids`, `scores`, and `missing_group_ids` for outputs. The `behavior` string for `grouped_argmax_f64` explicitly states: "select the highest-score item per group with deterministic item-id tie-break; group ids must be in [0, group_count)".

This phrasing is generic and does not contain any app-specific tokens or semantics, aligning with the `V2_4_FORBIDDEN_NATIVE_APP_TOKENS` checks confirmed in `tests/goal2662_v2_5_partner_continuation_contract_test.py`. The operation is categorized as "ranked_summary", further reinforcing its generic nature.

### 2. Confirm Python reference semantics implement highest-score selection with deterministic lowest-item-id tie-breaks and explicit missing groups.

**Findings:**
The `_grouped_argmax` function in `src/rtdsl/partner_continuation_protocol.py` implements the Python reference semantics.
-   **Highest-score selection:** It initializes `best` with `None` for each group and updates it if a `candidate` score is greater than the `current` best score.
-   **Deterministic lowest-item-id tie-breaks:** When creating the `candidate` tuple, it uses `(float(score), -int(item))`. This means that for equal scores, the tuple with the numerically larger negative item ID (i.e., the smaller positive item ID) will be considered "greater", thus selecting the lowest item ID in case of a tie. When extracting the `item_id` for output, it is converted back with `-negative_item`.
-   **Explicit missing groups:** The function iterates through the `best` list. If a group's `best` entry is `None`, its `group` ID is added to the `missing_group_ids` list.

`tests/goal2776_v2_5_triton_grouped_argmax_preview_test.py`'s `test_reference_grouped_argmax_has_deterministic_tie_break` successfully validates this behavior with specific test cases.

### 3. Confirm the Triton preview mirrors the reference shape: `tl.atomic_max` best-score pass, `tl.atomic_min` equal-best item-id pass, no RawKernel.

**Findings:**
In `src/rtdsl/triton_partner_continuation.py`:
-   **`tl.atomic_max` best-score pass:** The `_triton_grouped_argmax_score_f64_kernel` uses `tl.atomic_max(dense_scores + groups, vals, sem="relaxed", mask=valid)` to find the highest score per group.
-   **`tl.atomic_min` equal-best item-id pass:** The `_triton_grouped_argmax_item_i64_kernel` loads the `best_scores` found in the previous pass. For rows where `vals == best_scores`, it then uses `tl.atomic_min(dense_item_ids + groups, items, sem="relaxed", mask=is_best)` to select the lowest `item_id` among those with the highest score.
-   **No RawKernel:** The inspected `triton_partner_continuation.py` file and `test_source_uses_triton_argmax_kernels_and_no_rawkernel` in the test confirm that Triton's native kernel capabilities (`tl.atomic_max`, `tl.atomic_min`) are used directly, and there is no reliance on `RawKernel` implementations.

### 4. Confirm the support matrix is honest: reference contract exists, Triton is preview-not-promoted, Numba fails closed, CuPy is descriptor-only.

**Findings:**
The `v2_5_partner_support_cells` function in `src/rtdsl/v2_5_partner_support_matrix.py` is the source of truth for the support matrix.
-   **Reference contract exists:** A `V25PartnerSupportCell` for `grouped_argmax_f64` with `partner=V2_5_REFERENCE_PARTNER` and `status=V2_5_SUPPORT_STATUS_REFERENCE` is generated.
-   **Triton is preview-not-promoted:** A cell for `grouped_argmax_f64` with `partner=V2_5_PRIMARY_PARTNER` (triton) is generated with `status=V2_5_SUPPORT_STATUS_PREVIEW` (which maps to `preview_not_promoted`).
-   **Numba fails closed:** A cell for `grouped_argmax_f64` with `partner=V2_5_FALLBACK_PARTNER` (numba) is generated with `status=V2_5_SUPPORT_STATUS_UNSUPPORTED`.
-   **CuPy is descriptor-only:** A cell for `grouped_argmax_f64` with `partner=V2_5_CONFORMANCE_PARTNER` (cupy) is generated with `status=V2_5_SUPPORT_STATUS_DESCRIPTOR`.

These findings are consistently validated by `test_preview_kernel_set_and_support_matrix_include_grouped_argmax` in `tests/goal2776_v2_5_triton_grouped_argmax_preview_test.py`.

### 5. Confirm no public speedup, release, true-zero-copy, or RT traversal replacement claim is introduced.

**Findings:**
-   `src/rtdsl/partner_continuation_protocol.py` explicitly sets `V2_5_PERFORMANCE_PATH_AUTHORIZED = False`, `V2_5_RT_TRAVERSAL_REPLACEMENT_ALLOWED = False`, `V2_5_PREVIEW_RELEASE_TAG_AUTHORIZED = False`, and `V2_5_PREVIEW_PUBLIC_SPEEDUP_CLAIM_AUTHORIZED = False`. The `RtdlPartnerContinuationSpec` and its validation also raise `ValueError` if `promoted_performance_path`, `replaces_rt_traversal`, or `app_specific_semantics_allowed` are set to `True`.
-   `src/rtdsl/triton_partner_continuation.py`'s `_base_triton_descriptor` and `_triton_run_result` consistently set `promoted_performance_path=False`, `replaces_rt_traversal=False`, and `rt_core_speedup_claim_authorized=False`. It also specifies `true_zero_copy_claim_authorized=False` for group ID bounds validation.
-   `src/rtdsl/v2_5_partner_support_matrix.py`'s `V25PartnerSupportCell` explicitly validates that `promoted_performance_path`, `rt_traversal_replacement_allowed`, `public_speedup_claim_authorized`, and `true_zero_copy_claim_authorized` must not be true. The `V2_5_PARTNER_SUPPORT_CLAIM_BOUNDARY` clearly states: "They do not authorize RT traversal replacement, public speedup claims, release claims, or true zero-copy claims."
-   The report `docs/reports/goal2776_v2_5_grouped_argmax_witness_reduction_2026-05-31.md` also explicitly states in its "Boundary" section: "This is not a public speedup claim, release claim, true-zero-copy claim, or whole-app benchmark result."

All inspected files and tests confirm that no such claims are introduced.

### 6. List blockers or follow-ups before app adapters consume this operation.

**Blockers/Follow-ups:**
1.  **"preview_not_promoted" Status:** The Triton implementation of `grouped_argmax_f64` is currently in `preview_not_promoted` status. This means it has not yet undergone the necessary performance benchmarking and validation to be considered a promoted, production-ready path. The handoff report also notes "Pod validation is still required before any performance wording."
2.  **Benchmark Integration and External Consensus:** The `v2_5_partner_preview_gate()` in `src/rtdsl/partner_continuation_protocol.py` (and confirmed in `tests/goal2671_v2_5_preview_gate_test.py`) indicates `benchmark_integration_validated: False` and `external_3ai_consensus_complete: False`. Full benchmark integration and external 3-AI consensus are still pending for all v2.5 preview kernels.
3.  **No Public Claims:** As confirmed in check #5, no public speedup or release claims are authorized. App adapters consuming this operation would need to be aware of its preview status and the lack of authorized public performance claims.
4.  **No RawKernel:** While this is a positive from a maintainability perspective, it means that any app adapters must rely on the existing Triton kernel and not attempt to implement custom `RawKernel` logic.

This operation is ready for internal validation and continued development, but not yet for broad external consumption via app adapters that would imply performance or stability guarantees beyond its preview status.
