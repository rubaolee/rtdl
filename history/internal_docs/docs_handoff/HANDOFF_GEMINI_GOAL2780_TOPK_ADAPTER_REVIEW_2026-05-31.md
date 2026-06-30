# Gemini Review Request - Goal2780 Top-K Adapter over Triton Grouped Top-K

Please perform an independent read-only review of Goal2780 and write the review
to:

`docs/reviews/goal2780_gemini_review_topk_adapter_triton_grouped_topk_2026-05-31.md`

Review these files:

- `src/rtdsl/partner_adapters.py`
- `tests/goal2780_topk_adapter_triton_grouped_topk_test.py`
- `docs/reports/goal2780_topk_adapter_triton_grouped_topk_2026-05-31.md`
- `docs/reports/goal2780_pod_artifacts/goal2780_topk_adapter_triton_pod_69_30_85_171_2026-05-31.json`

Questions to answer:

1. Confirm that `top_k_nearest_points_2d_partner_columns(..., partner="triton")`
   routes through the generic `grouped_topk_f64` continuation rather than adding
   app-specific native engine logic.
2. Confirm same-contract correctness against the Torch branch, including the
   deterministic distance-then-candidate-id tie break.
3. Confirm the CUDA `uint32` indexing repair is appropriate and does not change
   app semantics.
4. Confirm the report is honest that Triton is much slower than Torch for this
   dense exact top-k adapter and therefore is not promoted as a performance path.
5. Confirm no public speedup, RT-core speedup, true-zero-copy, release, or
   whole-app claim is authorized.

Use one of these verdicts exactly: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.
