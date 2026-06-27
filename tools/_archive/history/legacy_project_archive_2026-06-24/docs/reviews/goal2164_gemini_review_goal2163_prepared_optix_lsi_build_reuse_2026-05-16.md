This is an independent Gemini review of Goal2163, distinct from Codex authoring. This review does not by itself authorize v2.0 release.

## Review Questions

1.  **Does the prepared OptiX surface stay generic and app-agnostic?**
    Yes, the prepared OptiX surface remains generic and app-agnostic. The native C++ API (`rtdl_optix_prepare_segment_pair_intersection`, `rtdl_optix_run_prepared_segment_pair_intersection`, `rtdl_optix_destroy_prepared_segment_pair_intersection`) operates on generic geometric primitives (`RtdlSegment`) and does not contain any application-specific logic (e.g., "RayJoin"). The Python wrapper in `optix_runtime.py` mirrors this generic interface. The `goal2159_rayjoin_public_cdb_runner.py` script merely utilizes this generic primitive in the context of RayJoin. The report explicitly states this intent, reinforcing the design.

2.  **Do the pod artifacts support the report's exact claims?**
    Yes, the JSON pod artifacts (`goal2163_rayjoin_prepared_optix_lsi_count192_pod_2026-05-16.json`, `goal2163_rayjoin_prepared_optix_lsi_count256_pod_2026-05-16.json`, `goal2163_rayjoin_prepared_optix_lsi_count384_pod_2026-05-16.json`) fully support the numerical and qualitative claims made in the `docs/reports/goal2163_prepared_optix_lsi_build_reuse_2026-05-16.md` report's results table. All metrics, including candidate pair counts, row counts, and median elapsed times for one-shot OptiX, prepared OptiX (prepare and repeat), and CuPy brute-force, match precisely. Parity checks are consistently reported as `true`.

3.  **Is the comparison against CuPy correctly bounded as a same-runner non-RT CUDA-core baseline?**
    Yes, the comparison against CuPy is correctly bounded. The `_CUPY_LSI_KERNEL_SOURCE` in `goal2159_rayjoin_public_cdb_runner.py` confirms the use of a raw CUDA kernel for brute-force intersection detection, which is a non-RT CUDA-core approach. Both OptiX and CuPy backends are executed within the same runner script, ensuring consistent measurement conditions. The report accurately characterizes this as a "CuPy CUDA-core brute-force baseline" and acknowledges the need for future comparisons against more advanced CuPy baselines (e.g., spatial-prefilter variants).

4.  **Are the claim boundaries conservative enough, especially around broad RT speedup and v2.0 release readiness?**
    Yes, the claim boundaries are appropriately conservative. The "Claim Boundary" section in the report explicitly details what is and is not authorized, focusing on narrow statements about specific performance improvements for LSI on bounded CDB slices, and explicitly disclaiming broader assertions about overall RT speedup or v2.0 release authorization. This conservative approach is programmatically enforced in the `goal2159_rayjoin_public_cdb_runner.py` script, which sets `false` flags for broad claims in the generated artifact JSON.

5.  **Are there implementation or evidence debts that should block using Goal2163 as a v2.0 performance-design improvement?**
    No, there are no blocking implementation or evidence debts for using Goal2163 as a v2.0 performance-design improvement within its stated narrow claims. The "Next Work" items identified in the report (e.g., larger slices, bounded output capacity, comparing against more advanced CuPy baselines, learner-facing examples) are valid future enhancements or research directions. They do not represent critical flaws that undermine the current design improvement or its accompanying evidence. The current implementation for output handling in the Python runner, while potentially memory-intensive for extremely dense results, does not impact the correctness of the OptiX primitive or the validity of the performance measurements for the given test cases.

## Verdict

`accept-with-boundary`
