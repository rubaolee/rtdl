# Handoff For Claude - Goal2779 Edge-List Components

Please perform an independent read-only review of Goal2779 and write the result
to:

`docs/reviews/goal2779_claude_review_edge_list_components_2026-05-31.md`

Do not write a skeleton or placeholder. If you cannot complete the review, do
not create the review file. The review must contain evidence-backed answers and
one explicit verdict.

## Files To Inspect

- `src/rtdsl/partner_continuation_protocol.py`
- `src/rtdsl/triton_partner_continuation.py`
- `src/rtdsl/v2_5_partner_support_matrix.py`
- `src/rtdsl/__init__.py`
- `tests/goal2662_v2_5_partner_continuation_contract_test.py`
- `tests/goal2671_v2_5_preview_gate_test.py`
- `tests/goal2676_v2_5_triton_partner_pivot_test.py`
- `tests/goal2677_v2_5_triton_segmented_minmax_preview_test.py`
- `tests/goal2779_v2_5_triton_edge_list_components_preview_test.py`
- `docs/reports/goal2779_v2_5_edge_list_components_2026-05-31.md`

## Review Questions

1. Confirm `edge_list_components_i64` is generic and not DBSCAN/app-specific.
2. Confirm reference semantics label components by smallest node id.
3. Confirm the Triton preview mirrors the reference shape with min-label
   propagation kernels and no RawKernel.
4. Confirm the support matrix is honest: reference contract exists, Triton is
   preview-not-promoted, Numba fails closed, CuPy is descriptor-only.
5. Confirm no public speedup, release, true-zero-copy, RT traversal replacement,
   or DBSCAN cluster-quality claim is introduced.
6. List blockers or follow-ups before DBSCAN-style app adapters consume this
   operation, especially convergence and benchmark-promotion risks.

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`.
