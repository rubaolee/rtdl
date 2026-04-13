# Review of Goal 323: v0.5 Call For Test Publish Readiness (2026-04-12)

## Objective

This review re-evaluates Goal 323 against the current repository state, specifically examining the contents of `README.md` and `docs/release_reports/v0_5_preview/support_matrix.md` to ensure proper linkage and consistent messaging regarding the `v0.5` preview and its associated call-for-test documentation.

## Analysis of `README.md`

The `README.md` (front page) currently presents the following relevant information for the `v0.5` preview:

- **Version Status At A Glance**: Clearly states "current active development line in this repo: `v0.5 preview`".
- **`v0.5` Preview Additions**: Lists `bounded_knn_rows`, 3D point nearest-neighbor support, and Linux backend closure across CPU/oracle, Embree, OptiX, and Vulkan.
- **Linkage to `v0.5` Preview Support Matrix**: The README provides a direct link to `[RTDL v0.5 Preview Support Matrix](docs/release_reports/v0_5_preview/support_matrix.md)` for exact status.
- **OS Support At A Glance**: Mentions "bounded support in the current `v0.5` preview line" for Windows and `local macOS`. It reiterates the link to the `v0.5` Preview Support Matrix for precise boundaries.
- **Current Release State**: Reinforces that "Current development preview in this repo: `v0.5 preview`".

Crucially, `README.md` *does not directly link* to the `call_for_test.md` document. It adheres to the instruction that the front page should not be treated as linking the call-for-test doc, instead directing users to the `support_matrix.md` for detailed information.

## Analysis of `docs/release_reports/v0_5_preview/support_matrix.md`

The `support_matrix.md` for `v0.5` preview provides comprehensive details:

- **Date and Status**: Clearly dated 2026-04-12 and marked as "current development-state preview, not final release sign-off."
- **Link to Call For Test**: It explicitly links to the `v0.5` Preview Call For Test: `[RTDL v0.5 Preview Call For Test](/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_5_preview/call_for_test.md)`. This is the intended location for this link.
- **Reading Guide**: Defines status wording used throughout the document (e.g., `accepted`, `accepted, bounded`, `supporting baseline`, `not yet closed`).
- **Platform Roles**: Details roles and status for Linux (primary validation), local macOS (development, bounded regression), and Windows (secondary portability/bring-up).
- **Backend Roles**: Outlines the status of various backends (Python reference, native CPU/oracle, PostGIS, Embree, OptiX, Vulkan, cuNSearch) within the `v0.5` preview.
- **Current Workload Surface**: Lists the status of 2D and 3D `fixed_radius_neighbors`, `knn_rows`, and `bounded_knn_rows`. Confirms that 3D NN for these is "closed on CPU/oracle, Embree, OptiX, Vulkan; Linux-validated".
- **Platform/Backend Boundary Summary**: Provides detailed honest states for Linux, local macOS, and Windows regarding 3D NN lines and performance claims.
- **Current Linux Backend Ordering**: Presents performance ordering for `fixed_radius_neighbors`, `bounded_knn_rows`, and `knn_rows` on Linux at `32768 x 32768` scale.
- **Honest Summary**: A concise summary of the `v0.5` preview's progress, highlighting the real 3D NN backend line on Linux, the inclusion of Vulkan, and the bounded nature of Windows/macOS support for large-scale performance claims.

## Conclusion

The repository is in a consistent state regarding "Goal 323" and the `v0.5` call for test.

- The `README.md` correctly serves as a high-level overview and directs users to the `support_matrix.md` for detailed `v0.5` preview status, without directly linking to the call-for-test document. This aligns with the specified instruction.
- The `docs/release_reports/v0_5_preview/support_matrix.md` properly acts as the detailed technical document for the `v0.5` preview, including the explicit link to the `call_for_test.md`. This ensures that the call-for-test is accessible and discoverable from the appropriate context.

The information presented across both documents is consistent and provides a clear picture of the `v0.5` preview's status, supported platforms, backends, and workloads, while also guiding users to further details, including the call for test.

This structure appropriately manages the visibility and accessibility of the `v0.5` call for test, ensuring it is discoverable for interested parties while not being prominently linked from the main project overview (`README.md`).