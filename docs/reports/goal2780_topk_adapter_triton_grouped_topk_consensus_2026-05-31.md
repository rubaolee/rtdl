# Goal2780 Consensus - Top-K Adapter over Triton Grouped Top-K

Date: 2026-05-31

## Decision

Goal2780 is accepted with boundary for the internal v2.5 preview lane.

It authorizes the code and documentation change that lets
`top_k_nearest_points_2d_partner_columns(..., partner="triton")` route through
the generic `grouped_topk_f64` continuation. It does not promote this path as
the RTNN/top-k performance path.

Verdict: `accept-with-boundary`.

## Evidence

- Codex implementation:
  - `src/rtdsl/partner_adapters.py`
  - `tests/goal2780_topk_adapter_triton_grouped_topk_test.py`
- Local validation:
  - source-route test passed
  - CUDA-gated adapter test skipped on Windows as expected
  - `py_compile` passed for touched Python files
  - `git diff --check` passed for touched files
- Pod validation on `69.30.85.171:22167`:
  - GPU: NVIDIA RTX A5000
  - Torch: `2.8.0+cu128`
  - Unit CUDA test passed: Triton adapter output matched Torch for query ids,
    neighbor ids, ranks, and distances.
  - Artifact:
    `docs/reports/goal2780_pod_artifacts/goal2780_topk_adapter_triton_pod_69_30_85_171_2026-05-31.json`.
- Independent Gemini review:
  `docs/reviews/goal2780_gemini_review_topk_adapter_triton_grouped_topk_2026-05-31.md`.
  Verdict: `accept-with-boundary`.

## Boundary

The accepted claim is narrow:

- the Triton adapter path is generic;
- it uses `grouped_topk_f64`;
- it preserves deterministic distance-then-candidate-id ranking;
- the CUDA `uint32` indexing repair is necessary and semantics-preserving.

The accepted evidence explicitly does not authorize:

- public speedup claims;
- RT-core speedup claims;
- true-zero-copy claims;
- v2.5 release claims;
- whole-app RTNN performance claims.

The pod timings are negative performance evidence for the current dense exact
top-k Triton preview: measured rows were about 47x-151x slower than the Torch
same-contract branch. Therefore the planner should keep Torch/CuPy as the
selected app partner for this dense ranking phase, or replace the current
iterative Triton preview with a stronger tiled/block-level top-k implementation
before any performance promotion.
