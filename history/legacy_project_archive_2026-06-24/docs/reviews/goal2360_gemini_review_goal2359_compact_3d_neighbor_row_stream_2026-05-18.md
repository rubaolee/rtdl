This is an independent Gemini review, distinct from Codex.

## Review for Goal2359 Compact 3D Neighbor Row Stream

**Verdict: `accept-with-boundary`**

This review examines the final Goal2357/Goal2359 RTNN-informed 3D neighbor work after the compact row-stream follow-up. The goal was to introduce a generic spatial preparation step for bounded neighbor collection within RTDL's OptiX backend, inspired by RTNN's performance, while maintaining app-agnosticism.

### Review Questions and Answers:

1.  **Does the implementation remain app-agnostic, with no RTNN-specific native ABI or benchmark-specific continuation?**
    *   **Answer:** Yes. The `docs/reports/goal2357_v2_2_rtnn_uniform_cell_neighbor_step_2026-05-18.md` report explicitly states that the implementation is app-agnostic and does not introduce RTNN-specific names, datasets, or native app continuations. Analysis of `scripts/goal2348_rtnn_v2_2_external_runner.py` and the C++ source files (`rtdl_optix_api.cpp`, `rtdl_optix_core.cpp`, `rtdl_optix_workloads.cpp`) confirms that the implementation provides generic 3D neighbor search primitives without tying into specific RTNN ABIs or continuations.

2.  **Does the final default path use generic uniform-cell bounded-neighbor traversal with compact populated-row output, while preserving explicit diagnostic fallbacks for old CUDA and simple RT traversal?**
    *   **Answer:** Yes. The report `docs/reports/goal2357_v2_2_rtnn_uniform_cell_neighbor_step_2026-05-18.md` confirms that the default path is a "Generic uniform-cell bounded-neighbor traversal" which "writes only compact populated bounded rows." It also details the explicit diagnostic fallbacks: `RTDL_OPTIX_FIXED_RADIUS_3D_FORCE_RT=1` for the "Simple custom-primitive OptiX traversal" and `RTDL_OPTIX_FIXED_RADIUS_3D_FORCE_CUDA=1` for the "Older all-pairs CUDA kernel." The `scripts/goal2348_rtnn_v2_2_external_runner.py` further demonstrates the activation and reporting of these distinct paths via environment variables.

3.  **Are the final pod artifacts and report claims consistent, especially:**
    *   **compact uniform-cell warm/raw beats old CUDA warm/raw at 65k and 262k;**
        *   **Answer:** Yes, consistent.
            *   **65k points:** New uniform-cell (0.691s) is faster than old CUDA (0.877s). The reported 1.269x speedup is confirmed by `0.877 / 0.691 ~= 1.269`.
            *   **262k points:** New uniform-cell (2.743s) is faster than old CUDA (3.444s). The reported 1.255x speedup is confirmed by `3.444 / 2.743 ~= 1.255`.
    *   **compact uniform-cell beats the collected RTNN warm row at 65k;**
        *   **Answer:** Yes, consistent. New uniform-cell at 65k (0.691s) is faster than the reported RTNN warm row at 65k (1.357s). The reported 1.964x speedup is confirmed by `1.357 / 0.691 ~= 1.964`.
    *   **compact uniform-cell still trails RTNN at 262k;**
        *   **Answer:** Yes, consistent. New uniform-cell at 262k (2.743s) is slower than the reported RTNN warm row at 262k (1.528s). The reported "0.557x" indicates that uniform-cell is approximately 55.7% the speed of RTNN, confirming it trails.
    *   **simple naked RT traversal is not accepted as default?**
        *   **Answer:** Yes, consistent. The simple RT traversal results at both 65k (2.694s) and 262k (10.608s) are significantly slower than both the new uniform-cell and old CUDA paths. The report explicitly states it is "not default" and "slower and not accepted as default."

4.  **Are the public claim boundaries strict enough, especially around RT-core acceleration, RTNN parity, and v2.2 release readiness?**
    *   **Answer:** Yes. The claim boundaries in the report (`docs/reports/goal2357_v2_2_rtnn_uniform_cell_neighbor_step_2026-05-18.md`) are appropriately strict. They explicitly disallow broad claims regarding RT-core acceleration, RTNN reproduction, beating RTNN at 262k points, and general v2.2 release claims. This conservative approach is well-justified by the performance data, particularly the continued trailing of RTNN at higher point counts. The `tests/goal2357_v2_2_rtnn_uniform_cell_neighbor_step_test.py` also validates these specific claim boundary statements.

5.  **Is the proposed next primitive `prepared_bounded_neighbor_search_3d` still the right v2.x direction after the compact row-stream evidence?**
    *   **Answer:** Yes. The evidence from the compact row-stream implementation, particularly its performance trailing RTNN at 262k points, reinforces the need for further optimization via a "prepared" primitive. The report clearly outlines that RTDL still "lacks RTNN's stronger partitioning/batching and prepared-neighbor runtime contract," making `prepared_bounded_neighbor_search_3d` a logical and necessary next step for v2.x improvements, encompassing reusable structures, batching policies, and device-resident continuation.

### Conclusion:

The Goal2357/Goal2359 work successfully introduces a generic uniform-cell bounded-neighbor traversal that significantly outperforms the older CUDA-based solution and even surpasses RTNN's performance at smaller scales (65k points). The implementation maintains app-agnosticism and provides useful diagnostic fallbacks. The report and supporting artifacts are clear and consistent, and the public claim boundaries are appropriately conservative, reflecting the nuanced performance profile and the remaining work towards full RTNN parity at all scales. The proposed next steps for a `prepared_bounded_neighbor_search_3d` primitive are well-justified by the current evidence.

