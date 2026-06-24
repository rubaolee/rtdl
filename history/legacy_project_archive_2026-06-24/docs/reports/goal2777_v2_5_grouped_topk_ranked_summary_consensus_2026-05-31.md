# Goal2777 Consensus - v2.5 Grouped Top-K Ranked Summary

Date: 2026-05-31

## Decision

Goal2777 is accepted for the internal v2.5 preview lane with boundary.

It adds `grouped_topk_f64`, a generic grouped ranked-summary primitive that
selects up to `k` lowest-score distinct items per group with deterministic
score-then-item-id ordering. The operation is not an RTNN-specific primitive and
does not add app semantics to the engine or partner surface.

## Evidence

- Codex implementation and local validation:
  - `tests.goal2662_v2_5_partner_continuation_contract_test`
  - `tests.goal2671_v2_5_preview_gate_test`
  - `tests.goal2676_v2_5_triton_partner_pivot_test`
  - `tests.goal2677_v2_5_triton_segmented_minmax_preview_test`
  - `tests.goal2678_v2_5_triton_compact_mask_preview_test`
  - `tests.goal2679_v2_5_triton_grouped_argmin_preview_test`
  - `tests.goal2680_v2_5_triton_bounded_collect_preview_test`
  - `tests.goal2696_v2_5_partner_support_matrix_test`
  - `tests.goal2776_v2_5_triton_grouped_argmax_preview_test`
  - `tests.goal2777_v2_5_triton_grouped_topk_preview_test`
  - Result: 59 tests passed locally, 6 skipped because local Windows had no
    executable Torch CUDA/Triton path.
- Pod CUDA validation on `69.30.85.171:22167`:
  - RTX A5000, driver `570.211.01`, Torch `2.8.0+cu128`, Triton `3.4.0`.
  - Goal2777 direct CUDA test: 6 tests passed, 0 skipped.
  - v2.5 preview/protocol/support-matrix slice: 59 tests passed, 0 skipped.
  - Artifact:
    `docs/reports/goal2777_pod_artifacts/goal2777_triton_grouped_topk_pod_69_30_85_171_2026-05-31.json`.
- Independent Gemini review:
  `docs/reviews/goal2777_gemini_review_grouped_topk_ranked_summary_2026-05-31.md`.
  Verdict: `accept-with-boundary`.

## Boundary

The consensus authorizes only the internal v2.5 preview contract and CUDA smoke
evidence for `grouped_topk_f64`.

It does not authorize:

- public speedup claims
- v2.5 release claims
- true-zero-copy claims
- RT traversal replacement claims
- RTNN paper reproduction claims
- app-level benchmark claims

Triton remains `preview_not_promoted`; Python remains the reference contract;
Numba fails closed for this operation; CuPy is descriptor-only.
