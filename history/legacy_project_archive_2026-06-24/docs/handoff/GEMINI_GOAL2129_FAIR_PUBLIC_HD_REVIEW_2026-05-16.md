# Gemini Task: Review Goal2129 Fair Public Hausdorff A5000 Perf

Please perform a read-only independent review of the Goal2129 fair public Hausdorff performance report and artifacts.

Relevant files:

- `examples/rtdl_hausdorff_v2_user_benchmark.py`
- `scripts/goal2126_public_hausdorff_dataset_perf.py`
- `docs/reports/goal2129_fair_public_hausdorff_a5000_perf_2026-05-16.md`
- `docs/reports/goal2129_public_pod_a5000_steady/*.json`
- `docs/reports/goal2129_public_pod_a5000_group_sweep/*.json`
- `tests/goal2129_fair_public_hausdorff_a5000_perf_test.py`

Review questions:

1. Does the new `cupy_grouped_grid_rawkernel` baseline fairly give CuPy the same broad uniform group/lower-bound pruning idea, while avoiding OptiX/RT traversal?
2. Is the warmup correction handled correctly in `scripts/goal2126_public_hausdorff_dataset_perf.py`, so the reported fields are steady-state timings rather than warmup-included timings?
3. Do the JSON artifacts support the report conclusion: RTDL/OptiX beats dense CuPy at large public sizes, but the optimized/fair grouped CuPy baseline remains faster than current RTDL/OptiX on the best full-Dragon comparison?
4. Are the claim boundaries sufficiently narrow: exact 2D projected point-set HD only, no exact X-HD dataset claim, no 3D surface HD claim, no release-wide speedup claim, and no claim that RTDL beats optimized CUDA?
5. What design debt should be highlighted for v2.0/v2.x based on this result?

Please write your review to:

- `docs/reviews/goal2130_gemini_review_goal2129_fair_public_hd_perf_2026-05-16.md`

Use verdict terms:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Do not edit source code. If you find issues, describe them in the review file.
