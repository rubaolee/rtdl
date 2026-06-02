# External Review Handoff: Goals3045-3046 Hausdorff Active-Frontier Evidence

Date: 2026-06-02

Please perform an independent read-only review of the RTDL v2.6 Hausdorff
active-frontier evidence chain after Goal3042.

## Expected Output

Write exactly one review file:

- Claude: `docs/reviews/goal3047_claude_review_goal3045_3046_hausdorff_active_frontier_evidence_2026-06-02.md`
- Gemini: `docs/reviews/goal3047_gemini_review_goal3045_3046_hausdorff_active_frontier_evidence_2026-06-02.md`

Use one of these verdict values: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

## Files To Inspect

- `docs/reports/goal3042_point_group_active_frontier_witness_selection_2026-06-02.md`
- `docs/reports/goal3042_active_frontier_perf_a4000_2026-06-02.json`
- `docs/reports/goal3045_hausdorff_active_frontier_multitrial_harness_2026-06-02.md`
- `docs/reports/goal3045_hausdorff_active_frontier_multitrial_a4000_2026-06-02.json`
- `docs/reports/goal3046_hausdorff_active_frontier_dataset_diversity_2026-06-02.md`
- `docs/reports/goal3046_hausdorff_active_frontier_dataset_diversity_a4000_2026-06-02.json`
- `scripts/goal3045_hausdorff_active_frontier_multitrial.py`
- `scripts/goal3046_hausdorff_active_frontier_dataset_diversity.py`
- `examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_v2_function.py`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_core.cpp`
- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/v2_6_roadmap.py`
- `tests/goal3042_point_group_active_frontier_witness_selection_test.py`
- `tests/goal3045_hausdorff_active_frontier_multitrial_harness_test.py`
- `tests/goal3046_hausdorff_active_frontier_dataset_diversity_test.py`

## Review Questions

1. Does the active-frontier native primitive remain generic/app-agnostic?
2. Do Goals3045 and 3046 correctly preserve exact Hausdorff distance parity
   against the CuPy grouped-grid reference?
3. Are the reported A4000 speedups arithmetically consistent with the artifacts?
4. Does Goal3046 materially reduce the dataset-diversity and seed-miss concern
   raised after Goal3042/3045?
5. Are the claim boundaries strict enough? In particular, do not authorize
   public speedup, broad RT-core speedup, release, true-zero-copy, or whole-app
   wording from these artifacts alone.
6. What concrete follow-up remains before this evidence can support a public
   v2.6 Hausdorff RT-core performance claim?

## Required Boundary

This review must not treat Goal3045/3046 as release authorization. The evidence
is one A4000 pod, synthetic dataset diversity, one CuPy reference method, and no
second-GPU confirmation yet.
