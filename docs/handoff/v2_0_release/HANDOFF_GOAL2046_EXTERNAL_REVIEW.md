# Handoff: Goal2046 CuPy Witness Continuation Surface Review

Please review Goal2046:

- `docs/reports/goal2046_cupy_witness_continuation_surface_2026-05-14.md`
- `src/rtdsl/partner_continuations.py`
- `tests/goal2046_cupy_witness_continuation_surface_test.py`

Context:

- Goal2044 added NumPy reference partner continuation primitives.
- Goal2046 adds the matching CuPy-facing witness-continuation surface: `cupy_group_topk`, `cupy_group_argmin_then_global_argmax_with_witness`, and `directed_hausdorff_2d_cupy_columns`.
- This is a contract/runtime surface for future pod validation, not release performance evidence.

Review questions:

1. Does this preserve app-agnostic partner-continuation design?
2. Is it reasonable to accept this as a bounded CuPy surface before pod runtime evidence?
3. Are the boundaries clear enough: no pod evidence, no OptiX zero-copy candidate-row handoff, no large-scale speed claim, no v2.0 release authorization?
4. What should be the next pod validation step?

Please write your review to:

`docs/reviews/goal2047_gemini_review_goal2046_cupy_witness_continuation_surface_2026-05-14.md`

Use one of these verdicts: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.
