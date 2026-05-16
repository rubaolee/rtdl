# Gemini Task: Review Goal2134 X-HD Graphics Hausdorff Perf Evidence

Please perform an independent read-only review of the RTDL Goal2134 evidence and write your review to:

`docs/reviews/goal2135_gemini_review_goal2134_xhd_graphics_hd_perf_2026-05-16.md`

## Context

The project is testing RTDL v2.0 as Python+partner+RTDL, with the native RTDL engine required to remain absolutely app-agnostic. Recent Goals 2131-2133 added and reviewed an X-HD-style exact 2D projected-point Hausdorff path:

- generic OptiX point-group threshold flags;
- generic OptiX point-group nearest-witness reduction;
- Hausdorff policy in Python;
- vectorized NumPy owner-buffer point packing;
- grouped CuPy fairness baseline.

Goal2134 extends the public performance evidence from the earlier Stanford Dragon/Happy controls to the graphics model names used by the X-HD scripts:

- Dragon vs Asian Dragon;
- Thai Statuette vs Happy Buddha;
- Dragon vs Happy Buddha;
- Thai Statuette vs Asian Dragon.

The evidence is intentionally scoped to exact 2D projected-point Hausdorff after XY projection of public Stanford PLY vertices. It must not be reviewed as a full 3D surface Hausdorff reproduction of the X-HD paper.

## Files To Review

- `scripts/goal2126_public_hausdorff_dataset_perf.py`
- `docs/reports/goal2134_xhd_graphics_dataset_perf_2026-05-16.md`
- `docs/reports/goal2134_xhd_graphics_pod_a5000/*.json`
- `tests/goal2134_xhd_graphics_dataset_perf_test.py`
- optional context:
  - `docs/reports/goal2132_xhd_seeded_pruned_packfast_a5000_perf_2026-05-16.md`
  - `docs/reviews/goal2133_gemini_review_goal2131_2132_xhd_packfast_hd_2026-05-16.md`

## Review Questions

1. Do the artifacts support the report's stated X-HD graphics dataset-name coverage?
2. Do all rows preserve correctness against grouped CuPy within the artifact/test boundary?
3. Is the performance conclusion accurately stated: RTDL/OptiX seeded-pruned beats grouped CuPy on these measured RTX A5000 projected-XY rows?
4. Are the claim boundaries precise and conservative, especially:
   - not claiming full 3D surface Hausdorff;
   - not claiming MRI or geo WKT reproduction;
   - not claiming universal CUDA-vs-RT speedup;
   - not authorizing v2.0 release by this evidence alone?
5. Does the harness extension preserve the old default `stanford` suite and avoid app-specific native-engine changes?

## Required Verdict Format

Use only these verdict values: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

Please include:

- per-question verdicts;
- any concrete issues found, with file references;
- final overall verdict;
- explicit statement that this is an independent Gemini review, distinct from Codex.
