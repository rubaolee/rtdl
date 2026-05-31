# Goal2779 Consensus - v2.5 Edge-List Components

Date: 2026-05-31

## Decision

Goal2779 is accepted for the internal v2.5 preview lane with boundary.

It adds `edge_list_components_i64`, a generic edge-list component-labeling
primitive. The operation is not a DBSCAN primitive and does not add cluster
policy or app semantics to the engine or partner surface.

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
  - `tests.goal2779_v2_5_triton_edge_list_components_preview_test`
  - Result: 74 tests passed locally, 8 skipped because local Windows had no
    executable Torch CUDA/Triton path.
- Pod CUDA validation on `69.30.85.171:22167`:
  - RTX A5000, driver `570.211.01`, Torch `2.8.0+cu128`, Triton `3.4.0`.
  - Goal2779 direct CUDA test: 6 tests passed, 0 skipped.
  - v2.5 preview/protocol/support-matrix slice: 73 tests passed, 0 skipped.
  - Artifact:
    `docs/reports/goal2779_pod_artifacts/goal2779_triton_edge_list_components_pod_69_30_85_171_2026-05-31.json`.
- Independent Gemini review:
  `docs/reviews/goal2779_gemini_review_edge_list_components_2026-05-31.md`.
  Verdict: `accept-with-boundary`.
- Independent Claude review:
  `docs/reviews/goal2779_claude_review_edge_list_components_2026-05-31.md`.
  Verdict: `accept-with-boundary`.

## Boundary

The consensus authorizes only the internal v2.5 preview contract and CUDA smoke
evidence for `edge_list_components_i64`.

It does not authorize:

- public speedup claims
- v2.5 release claims
- true-zero-copy claims
- RT traversal replacement claims
- DBSCAN cluster-quality claims
- app-level benchmark claims

Triton remains `preview_not_promoted`; Python remains the reference contract;
Numba fails closed for this operation; CuPy is descriptor-only.

Before DBSCAN-style app adapters consume this as benchmark evidence, the project
still needs a canonical adapter, convergence policy, and large-scale pod
evidence.
