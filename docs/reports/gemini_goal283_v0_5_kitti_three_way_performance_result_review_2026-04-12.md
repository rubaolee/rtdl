# Gemini Goal 283 Review: KITTI Three-Way Performance Result

Date: 2026-04-12
Reviewer: Gemini CLI

## Verdict

**PASS**

The KITTI three-way performance result for Goal 283 is an honest and bounded comparison. It correctly separates one-time setup costs (compilation and database preparation) from repeated execution costs, providing a clear picture of the steady-state performance of each system.

## Findings

- **Honest Cost Separation:**
  - **cuNSearch:** Compilation of the specialized CUDA driver is measured separately (`2.268842 s`) from the execution of the resulting binary (`0.108413 s`). This reveals that for small, single-shot workloads, compilation is the dominant cost.
  - **PostGIS:** Table creation, data loading, and index building (using `gist_geometry_ops_nd` for true 3D indexing) are measured as a separate "prep" phase (`0.076574 s`), distinct from the query execution (`0.010436 s`).
  - **RTDL Reference:** Measured as pure Python truth-path execution (`0.056507 s`), serving as the baseline.
- **Methodological Integrity:**
  - The `goal283_kitti_three_way_performance.py` script uses consistent KITTI data packages (512 points) across all three backends.
  - Parity checks are performed and confirmed (`parity_ok: true`), ensuring the comparisons are valid and backends are producing equivalent results.
  - Median values over multiple repeats are used to mitigate noise.
- **Evidence-Bounded Conclusions:**
  - The report's "Honest Read" section avoids claiming general superiority. It correctly identifies that PostGIS is the fastest for *repeated query execution* on this specific bounded workload, while noting the overheads of other systems.

## Risks

- **Scale Sensitivity:** The current results are for a very small bounded set (512 points). The relative performance of PostGIS (highly optimized C/C++) vs. cuNSearch (GPU-accelerated) vs. RTDL (Python truth path) may shift significantly as the point cloud size grows. cuNSearch, in particular, is likely to show better amortized performance on larger datasets where the GPU parallelism can be fully leveraged and the compilation cost is a smaller fraction of the total lifecycle.
- **Environment Specifics:** Performance is highly dependent on the specific hardware (CPU/GPU) and software (PostgreSQL/PostGIS version, CUDA version) on the `lestat-lx1` host.

## Conclusion

Goal 283 successfully delivers the project's first high-integrity three-way benchmark. The separation of setup and execution costs provides the transparency necessary for architectural decision-making. The implementation is robust, the measurement is fair, and the reporting is disciplined.
