# Handoff For Gemini - Goal2778 Grouped Vector Sum

Please perform an independent read-only review of Goal2778 and write the result
to:

`docs/reviews/goal2778_gemini_review_grouped_vector_sum_2026-05-31.md`

## Files To Inspect

- `src/rtdsl/partner_continuation_protocol.py`
- `src/rtdsl/triton_partner_continuation.py`
- `src/rtdsl/v2_5_partner_support_matrix.py`
- `src/rtdsl/__init__.py`
- `tests/goal2662_v2_5_partner_continuation_contract_test.py`
- `tests/goal2671_v2_5_preview_gate_test.py`
- `tests/goal2676_v2_5_triton_partner_pivot_test.py`
- `tests/goal2677_v2_5_triton_segmented_minmax_preview_test.py`
- `tests/goal2778_v2_5_triton_grouped_vector_sum_preview_test.py`
- `docs/reports/goal2778_v2_5_grouped_vector_sum_2026-05-31.md`

## Review Questions

1. Confirm `grouped_vector_sum_f64x2` is generic and not Barnes-Hut/app-specific.
2. Confirm reference semantics are componentwise sums per group with zero for
   empty groups.
3. Confirm the Triton preview mirrors the reference shape with paired atomic-add
   component sums and no RawKernel.
4. Confirm the support matrix is honest: reference contract exists, Triton is
   preview-not-promoted, Numba fails closed, CuPy is descriptor-only.
5. Confirm no public speedup, release, true-zero-copy, RT traversal replacement,
   or Barnes-Hut force-accuracy claim is introduced.
6. List blockers or follow-ups before Barnes-Hut-style app adapters consume this
   operation.

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`.
