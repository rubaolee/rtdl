# Gemini Review Request - Goal2776 Grouped Argmax Witness Reduction

Please perform an independent read-only review of Goal2776.

## Context

Goal2776 adds the generic sibling to `grouped_argmin_f64`:

`grouped_argmax_f64`

It is intended to support witness-style reductions where a user needs the
highest-score item per group, with deterministic lowest-item-id tie-breaks. This
must remain app-agnostic and must not become a Hausdorff, nearest-neighbor,
RayJoin, or DBSCAN-specific primitive.

## Files To Inspect

- `src/rtdsl/partner_continuation_protocol.py`
- `src/rtdsl/triton_partner_continuation.py`
- `src/rtdsl/v2_5_partner_support_matrix.py`
- `src/rtdsl/__init__.py`
- `tests/goal2662_v2_5_partner_continuation_contract_test.py`
- `tests/goal2671_v2_5_preview_gate_test.py`
- `tests/goal2676_v2_5_triton_partner_pivot_test.py`
- `tests/goal2677_v2_5_triton_segmented_minmax_preview_test.py`
- `tests/goal2776_v2_5_triton_grouped_argmax_preview_test.py`
- `docs/reports/goal2776_v2_5_grouped_argmax_witness_reduction_2026-05-31.md`

## Required Checks

1. Confirm the new operation name, fields, and semantics are generic.
2. Confirm Python reference semantics implement highest-score selection with
   deterministic lowest-item-id tie-breaks and explicit missing groups.
3. Confirm the Triton preview mirrors the reference shape:
   - `tl.atomic_max` best-score pass
   - `tl.atomic_min` equal-best item-id pass
   - no RawKernel
4. Confirm the support matrix is honest:
   - reference contract exists
   - Triton is preview-not-promoted
   - Numba fails closed
   - CuPy is descriptor-only
5. Confirm no public speedup, release, true-zero-copy, or RT traversal
   replacement claim is introduced.
6. List blockers or follow-ups before app adapters consume this operation.

## Validation Commands

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal2662_v2_5_partner_continuation_contract_test tests.goal2671_v2_5_preview_gate_test tests.goal2676_v2_5_triton_partner_pivot_test tests.goal2677_v2_5_triton_segmented_minmax_preview_test tests.goal2678_v2_5_triton_compact_mask_preview_test tests.goal2679_v2_5_triton_grouped_argmin_preview_test tests.goal2680_v2_5_triton_bounded_collect_preview_test tests.goal2696_v2_5_partner_support_matrix_test tests.goal2776_v2_5_triton_grouped_argmax_preview_test
```

## Output

Write your review to:

`docs/reviews/goal2776_gemini_review_grouped_argmax_witness_reduction_2026-05-31.md`

Use verdict `accept`, `accept-with-boundary`, or `needs-more-evidence`.

Do not edit source code, tests, reports, or `MEMORY.md`.
