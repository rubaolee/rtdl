# Final v0.4 Re-Audit Report: Nearest-Neighbor Line

Date: 2026-04-10
Status: **PASSED**
Verdict: The `v0.4` line is ready for release-packaging and version tagging.

## Summary

This re-audit confirms that the RTDL `v0.4` nearest-neighbor workload family has successfully transitioned from its earlier CPU-only baseline to a fully closure-consistent state spanning CPU, Embree, OptiX, and Vulkan backends. The "reopened for GPU" bar established in Goal 215 has been fully met and honestly documented.

## Audit Findings

### 1. Technical Correctness & Parity
- **Consolidated Test Suite**: 204 tests run, **OK**. This covers the core quality, language safety, and workload-specific contracts for `fixed_radius_neighbors` and `knn_rows`.
- **GPU Backends**: Goals 216–219 have been closed with Linux-validated evidence. Both NN workloads now support OptiX (primary GPU path) and Vulkan (correctness-first portability path).
- **Application Validation**: Goal 214 application examples (`service_coverage_gaps`, `event_hotspot_screening`, `facility_knn_assignment`) are verified on the truth path and CPU/Embree backends.

### 2. Honest Boundary & Performance
- **Vulkan Policy**: The audit confirms that Vulkan is honestly described as "correctness-first and performance-bounded." It correctly materializes nearest-neighbor rows but is not yet tuned for peak throughput compared to OptiX.
- **Embree KNN Regression**: The earlier audit finding regarding Embree KNN performance (1.5–2.0x overhead vs CPU Oracle on small datasets) is noted and documented in the feature guide. This is accepted as a research-stage characteristic for the `v0.4` preview.
- **Distance Precision**: GPU distance results are correctly bounded to float32 precision and verified against the double-precision truth path using appropriate tolerances.

### 3. Documentation & Identity
- **Consolidated Identity**: The root `README.md` and `docs/README.md` correctly identify the repo as `v0.3.0` (stable) with a `v0.4` active preview.
- **Support Matrix**: The `docs/release_reports/v0_4/support_matrix.md` is technically accurate and synchronized with the backend implementation status.
- **Support for Python 3.9**: A minor compatibility fix (`from __future__ import annotations`) was applied to the `src/rtdsl/` package to allow verification on standard macOS Python 3.9 environments.

## Verdict

The `v0.4` nearest-neighbor workload line is **Technically Closed**. The "reopened" period initiated at Goal 215 is complete. 

### Recommendations
1. Proceed with the `v0.4.0` version increment in the `VERSION` file.
2. Create the `v0.4.0` git tag.
3. Archive the goal-ladder reports into `history/` before starting the next major research line.

**Audit Signed by:** Gemini
**Review Signed by:** Codex (via consensus closure)
