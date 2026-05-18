# Gemini Review: Goal2340 Hausdorff v2.1 Benchmark Refresh

**Date:** 2026-05-18

**Reviewer:** Gemini Agent

## Purpose of the Review

To perform a read-only independent review of Goal2340, which refreshes the Hausdorff/X-HD benchmark app on the current v2.1 branch, focusing on app usability, grouped RT path improvements, and preparation for a clean current-main pod rerun.

## Files Inspected

*   `examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_v2_function.py`
*   `examples/v2_0/research_benchmarks/hausdorff_xhd/README.md`
*   `scripts/goal2126_public_hausdorff_dataset_perf.py`
*   `docs/reports/goal2340_hausdorff_v2_1_benchmark_refresh_2026-05-18.md`
*   `tests/goal2340_hausdorff_v2_1_benchmark_refresh_test.py`
*   `tests/goal2110_hausdorff_exact_rt_nearest_witness_test.py`
*   `tests/goal2112_hausdorff_v2_language_lab_test.py`
*   `tests/goal2121_xhd_point_group_hausdorff_optix_enhancement_test.py`
*   `tests/goal2123_xhd_point_group_nearest_reduction_test.py`
*   `tests/goal2131_xhd_seeded_pruned_hausdorff_test.py`

## Review Questions and Answers

### 1. Does the scale-aware `default_target_points_per_group()` default look technically reasonable for current X-HD-style point-set rows, while keeping explicit override knobs for reproducibility?

Yes, the `default_target_points_per_group()` function in `rtdl_hausdorff_v2_function.py` implements a scale-aware default for grouping points. It uses a base of 64 points, scales up based on `point_count // 128`, and rounds to the nearest power of two, capping at 8192. This approach balances performance and group size across different scales, which is technically reasonable for X-HD-style point-set rows. The `--target-points-per-group` CLI argument and direct function parameters allow explicit overrides, ensuring full reproducibility for specific benchmark sweeps. This is confirmed by tests in `tests/goal2340_hausdorff_v2_1_benchmark_refresh_test.py`.

### 2. Does the change preserve the app-agnostic native-engine boundary?

Yes, the changes meticulously preserve the app-agnostic native-engine boundary. All Hausdorff or X-HD specific logic, such as grouping, seeding, pruning, and adaptive worklist management, is implemented in Python at the application level within `rtdl_hausdorff_v2_function.py`. The underlying RTDL native engine (`src/native/optix/`) continues to exclusively utilize generic primitives (point groups, threshold flags, nearest witnesses, and max-distance reduction), without introducing any Hausdorff-specific ABI names or reducers. This separation is thoroughly verified by the various `goal21xx` tests.

### 3. Do the docs clearly present v2.1-compatible usage without claiming full X-HD reproduction, 3D surface Hausdorff, universal CUDA-vs-RT speedup, or a fresh current-main performance claim?

Yes, the documentation consistently and clearly presents v2.1-compatible usage while adhering to strict claim boundaries. The `README.md` explicitly states that the path is "informed by X-HD-style ideas" but does not claim full reproduction or universal speedup. The report (`docs/reports/goal2340_hausdorff_v2_1_benchmark_refresh_2026-05-18.md`) explicitly reiterates that "Full X-HD reproduction, full 3D surface Hausdorff, MRI/BraTS reproduction, original X-HD WKT-file reproduction, universal CUDA-vs-RT speedup, and release authorization remain `not-claimed`." It also specifies that a "fresh pod timing from current `main` is still required before replacing the May 16 numbers." The `scripts/goal2126_public_hausdorff_dataset_perf.py` also contains a `claim_boundary` field that programmatically enforces these limitations.

### 4. Are the stale test path repairs appropriate after the examples directory reorganization?

Yes, the stale test paths have been appropriately repaired. The relevant tests (`tests/goal2110_hausdorff_exact_rt_nearest_witness_test.py`, `tests/goal2112_hausdorff_v2_language_lab_test.py`, `tests/goal2121_xhd_point_group_hausdorff_optix_enhancement_test.py`, `tests/goal2123_xhd_point_group_nearest_reduction_test.py`, and `tests/goal2131_xhd_seeded_pruned_hausdorff_test.py`) now correctly reference files within the `examples/v2_0/research_benchmarks/hausdorff_xhd/` directory. The report's "Local Validation" section confirms that these tests passed, indicating successful adaptation to the examples directory reorganization.

### 5. Is the pod rerun plan sufficient to produce a future current-main RTX performance artifact?

Yes, the pod rerun plan detailed in `docs/reports/goal2340_hausdorff_v2_1_benchmark_refresh_2026-05-18.md` appears sufficient. It prescribes a thorough process including: fetching and hard resetting to `origin/main`, setting up the OptiX SDK, building the RTDL OptiX library, correctly exporting environment variables (`RTDL_OPTIX_LIBRARY`, `PYTHONPATH`), and executing the `scripts/goal2126_public_hausdorff_dataset_perf.py` benchmark for specified case suites and sample counts. The plan also mandates recording critical system information (pod SSH target, GPU, driver, commit, OptiX SDK tag, CUDA prefix), which is essential for a reproducible and verifiable performance artifact.

## Verdict

**`accept-with-boundary`**

The local implementation of Goal2340 is sound, adhering to technical requirements, architectural boundaries, and clear documentation practices. However, a fresh pod timing from current `main` is pending to produce a new performance claim. All performance claims remain within the boundaries defined in the documentation.
