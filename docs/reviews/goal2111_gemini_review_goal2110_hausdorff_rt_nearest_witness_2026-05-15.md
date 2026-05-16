# Goal2110: Exact RT Hausdorff Nearest Witness Review

**Date:** 2026-05-15

**Reviewer:** Gemini Agent

## Review Verdict: `accept-with-boundary`

## Review Questions & Answers:

### 1. Does Goal2110 honestly answer that the previous exact v2 Hausdorff path did not use RT cores, while the new `rtdl_rt_nearest_witness` path does use RTDL/OptiX traversal?

Yes, the Goal2110 report (`docs/reports/goal2110_hausdorff_exact_rt_nearest_witness_2026-05-15.md`) explicitly clarifies this distinction. It states:
- "The earlier v2.0 Hausdorff user program had two separate paths: `rtdl_v2_user_cuda`: exact Hausdorff distance, but the exact nearest-neighbor work is a CuPy/CUDA continuation and does not use RT cores."
- "After this goal: `rtdl_rt_nearest_witness` is an exact Hausdorff path using RTDL/OptiX RT traversal to obtain nearest witnesses."

The `examples/rtdl_hausdorff_v2_function.py` code also correctly reflects this by setting `rt_core_accelerated=True` for the `rtdl_rt_nearest_witness` method.

### 2. Is the new primitive generic enough for RTDL's app-agnostic engine boundary, or does it smuggle Hausdorff-specific logic into the native engine?

The new primitive, `rtdl_optix_run_prepared_fixed_radius_nearest_witness_2d`, implemented in `src/native/optix/rtdl_optix_api.cpp` and `src/native/optix/rtdl_optix_core.cpp` (via `kFrnNearestKernelSrc`), appears generic and adheres to the app-agnostic engine boundary. Its core function is to identify the nearest neighbor within a fixed radius for each query point.

The Hausdorff-specific logic (i.e., reducing the set of nearest witnesses to a single directed Hausdorff distance, and then combining two directed distances to compute the undirected Hausdorff distance) remains in the higher-level Python code (`examples/rtdl_hausdorff_v2_function.py`). This separation ensures the native engine provides a fundamental building block without incorporating application-specific algorithms.

### 3. Does the report avoid overclaiming X-HD paper-level performance?

Yes, the report explicitly and thoroughly avoids overclaiming X-HD paper-level performance. The "Boundary" section of `docs/reports/goal2110_hausdorff_exact_rt_nearest_witness_2026-05-15.md` clearly lists the missing algorithmic layers and optimizations that would be required for such a claim, including:
- absence of multi-resolution grid-cell grouping.
- lack of an HD estimator/early-break pruning loop.
- no heavy-cell CUDA offload.
- no persistent two-direction prepared-scene cache in the public Python wrapper.
- no large-pod RTX performance claim.

It concludes by stating that the claim is narrow and applies only to the use of RTDL/OptiX traversal for nearest-witness discovery.

### 4. Do the validation artifacts support exact correctness versus OpenMP/CUDA/CuPy baselines on the tested cases?

Yes, the validation artifacts provided (`docs/reports/hausdorff_v2_rt_nearest_witness_local_optix_512.json` and `docs/reports/hausdorff_v2_rt_nearest_witness_local_optix_2048_warm.json`) demonstrate exact correctness. Both JSON reports show that the `rtdl_rt_nearest_witness` method's distance value `matches_primary: true` against all listed baselines (OpenMP, CUDA C++, CuPy, and v2 user-CUDA) for the tested cases (512x512 and 2048x2048 points). The `tests/goal2110_hausdorff_exact_rt_nearest_witness_test.py` also explicitly verifies this.

### 5. What risks remain, especially around float tie-breaking, setup overhead, and the missing X-HD algorithmic layers?

**Summary of Remaining Risks:**

1.  **Float Tie-breaking:** The native `kFrnNearestKernelSrc` uses single-precision floats (`floatf`) for distance calculations and applies a `1.0e-7f` epsilon for tie-breaking, prioritizing smaller `seg_id` values. The Python layer re-computes the final distance in double precision (`math.hypot`) and applies its own tie-breaking logic (prioritizing smaller `source_index`). While current validation shows consistency, slight numerical variations or edge cases with many equidistant points across different hardware/compiler versions could lead to different `neighbor_id` (and thus `target_index`) selections compared to baselines or future implementations. The Python re-computation of distance in double precision does mitigate this for the accuracy of the final distance value itself.

2.  **Setup Overhead:** The reported elapsed times for `rtdl_rt_nearest_witness` (e.g., ~1 second for both 512x512 and 2048x2048 datasets) are significantly higher than the baseline methods (~millisecond range). This indicates substantial overhead related to OptiX context initialization, module compilation (even with caching), and particularly the BVH build (`AccelHolder build_custom_accel`). Although `_prepared_optix_execution_cache` attempts to reuse prepared scenes, its limited size (`_PREPARED_CACHE_MAX_ENTRIES = 8`) means that frequently changing scene data or exceeding the cache capacity could lead to repeated, costly re-preparations. This overhead is a known characteristic of complex RT acceleration structures and implies that this solution might not be optimal for very small or highly dynamic datasets.

3.  **Missing X-HD Algorithmic Layers:** As acknowledged in the report's "Boundary" section, the absence of advanced X-HD algorithmic layers (e.g., multi-resolution grids, early-break pruning, heavy-cell offload) means the current solution, while functionally correct, might not deliver the performance benefits expected from a fully optimized RT-core-accelerated Hausdorff distance computation for large-scale, complex problems. The current implementation is a foundational step rather than a complete, high-performance X-HD solution.

## Conclusion:

Goal2110 successfully introduces an exact Hausdorff distance path leveraging RTDL/OptiX traversal for nearest-witness discovery, aligning with the stated goal. The implementation is honest about its use of RT cores and avoids overclaiming performance benefits beyond its current scope. Validation artifacts demonstrate exact correctness against existing baselines. However, users should be aware of the inherent setup overheads and the current absence of advanced X-HD algorithmic optimizations, which are critical for achieving state-of-the-art performance for all problem sizes.