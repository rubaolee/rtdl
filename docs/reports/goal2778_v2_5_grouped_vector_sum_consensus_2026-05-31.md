# Goal2778 Consensus - v2.5 Grouped Vector Sum

Date: 2026-05-31

## Decision

Goal2778 is accepted for the internal v2.5 preview lane with boundary.

It adds `grouped_vector_sum_f64x2`, a generic grouped two-component float64
vector-sum primitive. The operation is not a Barnes-Hut force primitive and
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
  - `tests.goal2778_v2_5_triton_grouped_vector_sum_preview_test`
  - Result: 66 tests passed locally, 7 skipped because local Windows had no
    executable Torch CUDA/Triton path.
- Pod CUDA validation on `69.30.85.171:22167`:
  - RTX A5000, driver `570.211.01`, Torch `2.8.0+cu128`, Triton `3.4.0`.
  - Goal2778 direct CUDA test: 6 tests passed, 0 skipped.
  - v2.5 preview/protocol/support-matrix slice: 66 tests passed, 0 skipped.
  - Artifact:
    `docs/reports/goal2778_pod_artifacts/goal2778_triton_grouped_vector_sum_pod_69_30_85_171_2026-05-31.json`.
- Independent Gemini review:
  `docs/reviews/goal2778_gemini_review_grouped_vector_sum_2026-05-31.md`.
  Verdict: `accept-with-boundary`.

## Boundary

The consensus authorizes only the internal v2.5 preview contract and CUDA smoke
evidence for `grouped_vector_sum_f64x2`.

It does not authorize:

- public speedup claims
- v2.5 release claims
- true-zero-copy claims
- RT traversal replacement claims
- Barnes-Hut force-accuracy claims
- app-level benchmark claims

Triton remains `preview_not_promoted`; Python remains the reference contract;
Numba fails closed for this operation; CuPy is descriptor-only.
