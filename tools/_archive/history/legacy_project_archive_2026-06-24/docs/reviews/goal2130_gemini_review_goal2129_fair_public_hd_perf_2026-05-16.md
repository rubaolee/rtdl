# Goal2130 Gemini Review of Goal2129 Fair Public Hausdorff A5000 Perf

**Date:** 2026-05-16

**Review of Report:** `docs/reports/goal2129_fair_public_hausdorff_a5000_perf_2026-05-16.md`
**Associated Files:**
- `examples/rtdl_hausdorff_v2_user_benchmark.py`
- `scripts/goal2126_public_hausdorff_dataset_perf.py`
- `docs/reports/goal2129_public_pod_a5000_steady/*.json`
- `docs/reports/goal2129_public_pod_a5000_group_sweep/*.json`
- `tests/goal2129_fair_public_hausdorff_a5000_perf_test.py`

---

## Review Questions and Verdicts:

### 1. Does the new `cupy_grouped_grid_rawkernel` baseline fairly give CuPy the same broad uniform group/lower-bound pruning idea, while avoiding OptiX/RT traversal?

**Verdict:** `accept`

**Evidence:** The report explicitly states that `cupy_grouped_grid_rawkernel` uses the "same uniform target grouping and group-AABB lower-bound pruning idea, but no OptiX and no RT cores." Inspection of `examples/rtdl_hausdorff_v2_user_benchmark.py` confirms the implementation of a `CUPY_GROUPED_GRID_KERNEL` and `build_cupy_grouped_grid_target_columns` function, which pre-processes data into a grid and computes group-wise Axis-Aligned Bounding Boxes (AABBs) used for lower-bound pruning within the CUDA RawKernel. This approach mimics the spatial partitioning and pruning concept without leveraging hardware RT cores or OptiX's specific traversal mechanisms, thus providing a fair, optimized CUDA baseline. The artifact tests also confirm the presence of this baseline.

### 2. Is the warmup correction handled correctly in `scripts/goal2126_public_hausdorff_dataset_perf.py`, so the reported fields are steady-state timings rather than warmup-included timings?

**Verdict:** `accept`

**Evidence:** The performance script `scripts/goal2126_public_hausdorff_dataset_perf.py` correctly implements warmup. Functions like `_run_cupy`, `_run_cupy_grouped_grid`, and `_run_rtdl_grouped_reduced` all include a `for _ in range(max(0, int(warmup))):` loop that executes the relevant computation path before starting the `time.perf_counter()` for the actual measurement. This ensures that any initial overheads (e.g., JIT compilation, kernel launch setup) are absorbed during the warmup phase, and the reported `elapsed_sec` reflects steady-state performance.

### 3. Do the JSON artifacts support the report conclusion: RTDL/OptiX beats dense CuPy at large public sizes, but the optimized/fair grouped CuPy baseline remains faster than current RTDL/OptiX on the best full-Dragon comparison?

**Verdict:** `accept`

**Evidence:**
*   **RTDL/OptiX beats dense CuPy at large public sizes:** The "A5000 Steady-State Results" table in the report clearly shows `RTDL / dense CuPy` ratios less than 1.0x for `actual n = 437,645` (e.g., `0.480x`, `0.416x`), indicating RTDL/OptiX is faster than dense CuPy at these larger problem sizes. The `public_hd_*.json` artifacts for steady-state results also contain `rtdl_vs_cupy_ratio` values that confirm this for large `sample_count`.
*   **Optimized/fair grouped CuPy baseline remains faster than current RTDL/OptiX on the best full-Dragon comparison:** The "Full-Dragon Group-Size Sweep" table and its summary in the report show that the best elapsed times for `grouped CuPy` (e.g., `3.252s` for Dragon shifted at group `256`) are lower than the best elapsed times for `RTDL` (e.g., `5.014s` for Dragon shifted at group `512`). The `public_hd_524288_group_*.json` artifacts confirm these timings and `rtdl_vs_cupy_grouped_grid_ratio` values greater than 1.0x for grouped CuPy's optimal group sizes. Furthermore, `tests/goal2129_fair_public_hausdorff_a5000_perf_test.py` includes specific assertions (`self.assertLess(best["case"]["grouped"], best["case"]["rtdl"])`) that directly validate this conclusion programmatically from the artifacts.

### 4. Are the claim boundaries sufficiently narrow: exact 2D projected point-set HD only, no exact X-HD dataset claim, no 3D surface HD claim, no release-wide speedup claim, and no claim that RTDL beats optimized CUDA?

**Verdict:** `accept`

**Evidence:** The "Boundary" section of the report explicitly lists all these limitations, ensuring narrow claims. The `scripts/goal2126_public_hausdorff_dataset_perf.py` sets corresponding `claim_boundary` flags (`xhd_paper_exact_dataset_evidence: False`, `three_dimensional_surface_hausdorff_claim: False`, `release_speedup_claim_authorized: False`, `xy_projection_only: True`) within the generated JSON artifacts. The test script `tests/goal2129_fair_public_hausdorff_a5000_perf_test.py` rigorously verifies that these `claim_boundary` flags are correctly set to restrict the scope of the claims.

### 5. What design debt should be highlighted for v2.0/v2.x based on this result?

**Verdict:** `accept`

**Evidence:** The "Design Consequence" section of the report directly and clearly articulates several key design debts and future directions for v2.0/v2.x. These include:
- Adding a more efficient generic nearest-reduction primitive.
- Supporting device-resident grouped payloads.
- Implementing multi-level or best-first generic group hierarchies.
- Testing 3D point groups and surface/triangle geometry where RT traversal is more likely to provide greater benefit.
- Emphasizing the importance of strong partner baselines for credible performance claims.
This section effectively highlights the areas for future improvement based on the current benchmark results.