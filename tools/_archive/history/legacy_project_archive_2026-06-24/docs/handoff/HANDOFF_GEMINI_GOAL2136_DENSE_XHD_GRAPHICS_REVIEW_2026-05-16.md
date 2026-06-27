# Gemini Task: Review Goal2136 Dense X-HD Graphics Stress Evidence

Please perform an independent read-only review and write the result to:

`docs/reviews/goal2137_gemini_review_goal2136_dense_xhd_graphics_stress_2026-05-16.md`

## Context

Goal2134 added RTDL/OptiX Hausdorff performance evidence on the graphics model names used by the X-HD scripts. Goal2136 adds a denser stress sweep:

- requested sample count: 1,048,576;
- group sizes: 4096 and 8192;
- same X-HD graphics model names;
- exact 2D projected-point Hausdorff only;
- grouped CuPy fairness baseline;
- RTDL/OptiX X-HD-style seeded-pruned nearest-witness path.

The engine must stay app-agnostic: the native primitives are generic point-group threshold traversal and nearest-witness reduction, with Hausdorff policy in Python.

## Files To Review

- `docs/reports/goal2136_xhd_graphics_dense_stress_perf_2026-05-16.md`
- `docs/reports/goal2136_xhd_graphics_dense_pod_a5000/*.json`
- `tests/goal2136_xhd_graphics_dense_stress_perf_test.py`
- context:
  - `docs/reports/goal2134_xhd_graphics_dataset_perf_2026-05-16.md`
  - `docs/reviews/goal2135_gemini_review_goal2134_xhd_graphics_hd_perf_2026-05-16.md`
  - `scripts/goal2126_public_hausdorff_dataset_perf.py`

## Review Questions

1. Do the Goal2136 artifacts support the stated million-requested-sample stress evidence?
2. Do all rows preserve correctness against grouped CuPy within the artifact/test boundary?
3. Is the performance conclusion accurate and bounded: RTDL/OptiX beats grouped CuPy on these measured A5000 projected-XY stress rows?
4. Are the boundaries conservative: no full 3D X-HD reproduction, no MRI/geo WKT reproduction, no universal CUDA-vs-RT speedup, no v2.0 release authorization from this evidence alone?
5. Does this evidence remain consistent with the app-agnostic engine rule?

## Required Verdict Format

Use only: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

Please include per-question verdicts, concrete issues if any, final overall verdict, and an explicit statement that this is an independent Gemini review distinct from Codex.
