# Gemini Independent Review for Goal2136 Dense X-HD Graphics Stress Evidence

**Date:** 2026-05-16

**Reviewer:** Gemini CLI Agent

This is an independent Gemini review, distinct from any Codex review.

## Objective

This review assesses the public performance evidence from RTDL Goal2136, which extends the analysis of the RTDL/OptiX Hausdorff path to denser stress cases using X-HD graphics model names. The review focuses on verifying the claims and boundaries as presented in the provided artifacts.

## Scope (Files Reviewed)

*   `docs/reports/goal2136_xhd_graphics_dense_stress_perf_2026-05-16.md`
*   `docs/reports/goal2136_xhd_graphics_dense_pod_a5000/summary.json`
*   `docs/reports/goal2136_xhd_graphics_dense_pod_a5000/xhd_graphics_xy_1048576_group_4096.json`
*   `docs/reports/goal2136_xhd_graphics_dense_pod_a5000/xhd_graphics_xy_1048576_group_8192.json`
*   `tests/goal2136_xhd_graphics_dense_stress_perf_test.py`
*   `docs/reports/goal2134_xhd_graphics_dataset_perf_2026-05-16.md` (context)
*   `docs/reviews/goal2135_gemini_review_goal2134_xhd_graphics_hd_perf_2026-05-16.md` (context)
*   `scripts/goal2126_public_hausdorff_dataset_perf.py` (context)

## Review Questions and Verdicts

### 1. Do the Goal2136 artifacts support the stated million-requested-sample stress evidence?

**Verdict:** `accept`

**Analysis:** The `docs/reports/goal2136_xhd_graphics_dense_stress_perf_2026-05-16.md` report explicitly indicates a requested sample count of 1,048,576. The performance table in the report and the underlying JSON artifacts (`xhd_graphics_xy_1048576_group_4096.json`, `xhd_graphics_xy_1048576_group_8192.json`, and `summary.json`) confirm that cases like "Thai Statuette vs Happy Buddha" and "Thai Statuette vs Asian Dragon" were run with an `sample_count` of 1,048,576. The `tests/goal2136_xhd_graphics_dense_stress_perf_test.py` also programmatically verifies that all dense rows indeed correspond to this sample count.

### 2. Do all rows preserve correctness against grouped CuPy within the artifact/test boundary?

**Verdict:** `accept`

**Analysis:** The `docs/reports/goal2136_xhd_graphics_dense_stress_perf_2026-05-16.md` report explicitly states that "All rows matched grouped CuPy distance within the harness tolerance." This is consistently supported by the JSON artifacts, where each row includes `"match": true` and `"matches_cupy_grouped_grid_seeded_pruned": true`. The unit test `tests/goal2136_xhd_graphics_dense_stress_perf_test.py` further validates this by asserting `self.assertTrue(row["matches_cupy_grouped_grid_seeded_pruned"])` for all processed rows.

### 3. Is the performance conclusion accurate and bounded: RTDL/OptiX beats grouped CuPy on these measured A5000 projected-XY stress rows?

**Verdict:** `accept`

**Analysis:** The performance data presented in the `docs/reports/goal2136_xhd_graphics_dense_stress_perf_2026-05-16.md` report clearly demonstrates that RTDL/OptiX significantly outperforms grouped CuPy on the specified stress rows. Speedup factors range from 8.26x to 13.93x, indicating a substantial advantage. The report's "Interpretation" section accurately highlights that RTDL/OptiX maintains near-constant performance (around one second) for million-point dense rows, while grouped CuPy slows considerably. The conclusion is appropriately bounded, as reflected in the "Claim Boundary" section, which explicitly limits this performance advantage to "the measured RTX A5000 projected-XY stress rows." The unit test `tests/goal2136_xhd_graphics_dense_stress_perf_test.py` also programmatically confirms this significant performance ratio.

### 4. Are the boundaries conservative: no full 3D X-HD reproduction, no MRI/geo WKT reproduction, no universal CUDA-vs-RT speedup, no v2.0 release authorization from this evidence alone?

**Verdict:** `accept`

**Analysis:** The `docs/reports/goal2136_xhd_graphics_dense_stress_perf_2026-05-16.md` report's "Claim Boundary" section meticulously lists several disclaimers, marking them as `not-claimed` or `not-authorized-here`. Specifically, it clearly states: "Full 3D surface Hausdorff reproduction of X-HD | `not-claimed`", "MRI or geo WKT reproduction | `not-claimed`", "Universal CUDA-vs-RT speedup | `not-claimed`", and "v2.0 release authorization | `not-authorized-here`." These conservative boundaries are explicitly verified by the `tests/goal2136_xhd_graphics_dense_stress_perf_test.py`, ensuring that the claims are not overgeneralized.

### 5. Does this evidence remain consistent with the app-agnostic engine rule?

**Verdict:** `accept`

**Analysis:** The "Interpretation" section of the `docs/reports/goal2136_xhd_graphics_dense_stress_perf_2026-05-16.md` reaffirms that "The native work is generic point-group threshold traversal and nearest-witness reduction" and that "X-HD-style seed/prune policy lives in Python." It also states, "No Hausdorff-specific native entry point was added." This is consistent with the design observed in `scripts/goal2126_public_hausdorff_dataset_perf.py`, where the Hausdorff policy is implemented in Python using generic RTDL primitives. This evidence aligns with the app-agnostic engine rule previously affirmed in the `goal2135` review.

## Overall Verdict

**Overall Verdict:** `accept`

**Concrete Issues Found:** None.

The evidence presented in Goal2136 robustly supports the claims of million-point stress performance for RTDL/OptiX Hausdorff, demonstrating significant speedups over grouped CuPy while maintaining correctness. The artifacts and tests consistently uphold the explicitly stated conservative claim boundaries and remain consistent with the app-agnostic engine design.
