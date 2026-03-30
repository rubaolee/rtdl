1. Is this the right remaining implementation slice for the Embree baseline?

Yes. This slice (Steps 3-9) correctly shifts the focus from backend implementation to system-wide integration and usability. It groups the shared ABI, automated benchmarking, and cross-backend validation into a single logical push. Since the individual backends (CPU/Embree) and the contracts are already stable, this is the right time to wrap them in a unified harness before moving to the OptiX/GPU phase.

2. What specific acceptance checks should be used for this slice?

- ABI Parity: A single test suite must confirm that run_cpu and run_embree accept the same logical records and produce matching outputs (via compare_baseline_rows) for all 4 baseline workloads.
- Harness Output: The benchmark script must generate a structured JSON artifact in build/ containing backend, workload, dataset, and timing metadata for multiple iterations.
- CLI Entry Points: A contributor should be able to execute a workload via a simple command like `python -m rtdsl.baseline_runner lsi` without manual setup.
- Dataset Validation: The RayJoin subset datasets (br_county_subset, etc.) must be successfully loaded and processed by both backends in a reproducible "baseline run."
- Authored Code Sign-off: The provided examples (e.g., rtdl_ray_tri_hitcount.py) must pass the `validate_compiled_kernel_against_baseline` check and execute successfully on the Embree backend.

3. Are any pieces missing or misordered?

- Missing: The benchmark harness should explicitly account for a "warmup" iteration or distinguish between BVH construction time and traversal time to ensure timing data is not skewed by initialization.
- Missing: A "baseline summary" report generator that consumes the benchmark JSON and prints a human-readable comparison of CPU vs Embree performance.
- Ordering: The current order is logical, as the shared ABI (Step 3) is a prerequisite for the generic runners and harness (Steps 6-7).

4. If acceptable, what conditions would constitute consensus to begin implementing this slice?

- The `src/rtdsl/baseline_contracts.py` remains the immutable source of truth for all 4 workloads.
- The `tests/fixtures/rayjoin/` datasets are confirmed as the fixed scale for "representative" baseline runs.
- The benchmark harness is agreed to be a local-only tool for the Embree phase, with results stored in `build/` and ignored by git.
- Implementation can begin immediately as the underlying `run_cpu` and `run_embree` functions are already functionally complete and awaiting this integration layer.
