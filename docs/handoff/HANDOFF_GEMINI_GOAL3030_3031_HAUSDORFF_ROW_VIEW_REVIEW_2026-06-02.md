# Handoff: Gemini Review For Goal3030/Goal3031 Hausdorff Row-View Work

Please perform an independent read-only review of the current repository after
Goal3030 and Goal3031.

## Files To Inspect

- `src/rtdsl/optix_runtime.py`
- `examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_v2_function.py`
- `scripts/goal3026_hausdorff_raw_row_view_probe.py`
- `examples/v2_0/research_benchmarks/hausdorff_xhd/README.md`
- `src/rtdsl/v2_6_roadmap.py`
- `docs/reports/goal3031_hausdorff_vectorized_row_view_l4_pod_2026-06-02.md`
- `docs/reports/goal3031_hausdorff_vectorized_row_view_l4_pod_2026-06-02.json`
- `tests/goal3030_optix_row_view_numpy_reducer_test.py`
- `tests/goal3031_hausdorff_vectorized_row_view_l4_pod_test.py`

## Review Questions

1. Does `OptixRowView.to_numpy()` correctly present a borrowed host row-buffer
   view without implying device zero-copy or partner handoff?
2. Does the Hausdorff raw-row method remain exact and app-layer only, with no
   Hausdorff-specific native ABI or engine customization?
3. Does Goal3031 honestly represent the L4 pod evidence: vectorized raw row-view
   is faster than the old adaptive RT row path, but still slower than the dense
   CuPy grouped-grid reference?
4. Are the claim boundaries intact: no v2.6 release, no public speedup wording,
   no broad RT-core speedup wording, no true zero-copy, no package-install, and
   no app-specific native-engine behavior?
5. Are the tests adequate for this internal performance-tuning goal, and what
   residual risks should be tracked?

## Required Output

Write the review to:

`docs/reviews/goal3032_gemini_review_goal3030_3031_hausdorff_vectorized_row_view_2026-06-02.md`

Use one of these verdicts exactly:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

This review is for internal v2.6 performance-tuning evidence only. Do not
authorize release or public claims.
