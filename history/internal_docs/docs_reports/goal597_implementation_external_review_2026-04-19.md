# Goal597: Implementation External Review

Date: 2026-04-19

Verdict: **ACCEPT**

## Review Notes

The implementation fulfills the requirements set forth in the design document:

1. **Correctness & Strategy**: The implementation in `src/native/rtdl_apple_rt.mm` accurately utilizes the chunked masked nearest-hit strategy. It partitions triangles into batches of at most 32 primitives and appropriately assigns a unique bit per primitive. The use of `MPSRayMaskOptionPrimitive` and `MPSRayMaskOperatorAnd` guarantees that only unvisited geometry in the chunk is intersected, resolving the epsilon correctness issue.
2. **Testing**: The new test file `tests/goal597_apple_rt_masked_hitcount_test.py` explicitly tests edge cases including exactly stacked primitives and inputs requiring multiple mask chunks (>32 primitives), proving the correctness of the pagination logic. All correctness checks pass and maintain parity with `ray_triangle_hit_count_cpu`.
3. **Performance**: As per the performance artifact (`docs/reports/goal597_post_masked_hitcount_perf_macos_2026-04-19.md`), the change yields an observable median speedup (from `0.417s` to `0.329s`) for the dense 128-ray / 512-triangle fixture. While still an order of magnitude slower than Embree on all-hit dense workloads, the new strategy honors the design's goal to eliminate the AS-rebuild per triangle penalty.

The code style aligns with the repository guidelines and properly leverages the expected Metal Performance Shaders features.
