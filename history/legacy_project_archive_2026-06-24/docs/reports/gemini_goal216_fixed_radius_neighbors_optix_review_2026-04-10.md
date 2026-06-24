# Goal 216 Fixed Radius Neighbors OptiX Review (2026-04-10)

## Verdict

There are no blocking findings. The slice adds OptiX support for the `fixed_radius_neighbors` workload via a brute-force CUDA kernel, which is correct and matches the CPU reference implementation on all provided tests. The critical bug fix to ensure the CUDA context is initialized before module loading for helper kernels is also correctly implemented for both `point_nearest_segment` and the new `fixed_radius_neighbors` workload.

## Findings

1.  **Stale Documentation (Minor):** The header comments in `rtdl_optix_prelude.h` and the module docstring in `rtdsl/optix_runtime.py` are out of date and do not list `fixed_radius_neighbors` as a supported workload.
2.  **Stale Documentation (Minor):** The comment for the `point_nearest_segment` CUDA kernel in `rtdl_optix_core.cpp` incorrectly describes the parallelization strategy as one warp per point; the implementation uses one thread per point.
3.  **Inefficient Kernel Logic (Minor):** The CUDA kernel for `fixed_radius_neighbors` uses a linear scan to insert new neighbors into the sorted results list for each query point. This has O(k) complexity. While correct, this could be more efficient, for instance by using a heap for larger `k` or more optimized sorting network for smaller, fixed `k`. Given the brute-force nature of the overall kernel, this is a minor point.

## Suggested Fixes

1.  Update the file-level comment in `src/native/optix/rtdl_optix_prelude.h` to include `fixed_radius_neighbors` and its implementation strategy (CUDA-parallel brute-force).
2.  Update the module docstring in `src/rtdsl/optix_runtime.py` to include `fixed_radius_neighbors` in the list of supported native workloads.
3.  Correct the comment for `kPointNearestKernelSrc` in `src/native/optix/rtdl_optix_core.cpp` to accurately reflect its one-thread-per-point parallelization strategy.

## Residual Risks

- **Scalability:** The `fixed_radius_neighbors` implementation is a brute-force `O(num_queries * num_search_points)` CUDA kernel. This is consistent with the approach for `point_nearest_segment` and acceptable for the goal, but it will not scale to production use cases with large numbers of search points. A BVH-based or grid-based acceleration structure would be required for better performance.
