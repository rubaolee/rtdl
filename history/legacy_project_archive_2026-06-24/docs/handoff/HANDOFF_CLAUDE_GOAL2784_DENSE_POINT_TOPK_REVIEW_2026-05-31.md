# Handoff - Goal2784 Dense Point Top-K Triton Adapter Review

Please perform an independent read-only review of Goal2784 and write the result
to:

`docs/reviews/goal2784_claude_review_dense_point_topk_triton_adapter_2026-05-31.md`

## Files To Inspect

- `src/rtdsl/triton_partner_continuation.py`
- `src/rtdsl/partner_adapters.py`
- `src/rtdsl/v2_5_partner_selection_guidance.py`
- `src/rtdsl/v2_5_triton_app_migration.py`
- `tests/goal2784_dense_point_topk_triton_adapter_kernel_test.py`
- `tests/goal2782_v2_5_partner_selection_guidance_test.py`
- `tests/goal2783_v2_5_app_migration_selection_guidance_test.py`
- `docs/reports/goal2784_dense_point_topk_triton_adapter_kernel_2026-05-31.md`
- `docs/reports/goal2784_pod_artifacts/goal2784_dense_point_topk_triton_adapter_pod_69_30_85_171_2026-05-31.json`

## Review Questions

1. Does Goal2784 preserve the same exact dense 2D point top-k contract as the
   Torch branch?
2. Does the Triton adapter kernel actually avoid dense score materialization?
3. Is the performance evidence recorded honestly, including the fact that
   Triton improved substantially over Goal2780 but remains slower than Torch?
4. Does the refreshed Goal2782/Goal2783 planner guidance remain advisory only?
5. Are RT-core, true-zero-copy, whole-app, public speedup, and release claims
   still blocked?

Use one verdict: `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`.
