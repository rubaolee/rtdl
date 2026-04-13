# Gemini Review: Goal 318 - v0.5 Preview Support Matrix

**Date:** 2026-04-12

## 1. Introduction

This review assesses the `RTDL v0.5 Preview Support Matrix` (`docs/release_reports/v0_5_preview/support_matrix.md`) against the objectives outlined in `docs/goal_318_v0_5_preview_support_matrix.md` and the verification details in `docs/reports/goal318_v0_5_preview_support_matrix_2026-04-12.md`. The primary goal of Goal 318 is to convert the current `v0.5` backend/platform state into a clear, release-facing preview support matrix, explicitly stating the Linux 3D nearest-neighbor closure while maintaining honest boundaries for Windows, macOS, and PostGIS.

## 2. Technical Honesty of the Support Matrix

The `RTDL v0.5 Preview Support Matrix` (hereinafter referred to as "the support matrix") appears to provide a technically honest summary of the current `v0.5` backend/platform state.

-   **Current-state preview**: The support matrix explicitly states its status as "current development-state preview, not final release sign-off," aligning with the goal of creating a *preview* support matrix.
-   **Backend Roles**: It clearly describes the roles of Python reference, native CPU/oracle, PostGIS, Embree, OptiX, Vulkan, and cuNSearch. The inclusion of `cuNSearch` as an "external research comparison path" with "explicit duplicate/large-set boundaries" is a good example of honest boundary setting.
-   **Platform Roles**: The roles for Linux, local macOS, and Windows are well-defined, with appropriate qualifications (e.g., "accepted, bounded" for macOS and Windows).
-   **Workload Surface**: The support matrix details the `fixed_radius_neighbors`, `knn_rows`, and `bounded_knn_rows` in both 2D and 3D, noting their closure status and validation platforms.

The verification notes in `docs/reports/goal318_v0_5_preview_support_matrix_2026-04-12.md` provide concrete evidence for the bounded macOS and Windows Embree 3D correctness runs, supporting the claims made in the support matrix regarding these platforms.

## 3. Linux Ordering and Backend Roles

The support matrix explicitly details the "Current Linux Backend Ordering" for `fixed_radius_neighbors`, `bounded_knn_rows`, and `knn_rows` at a large scale (`32768 x 32768`), listing `OptiX < Vulkan < Embree < PostGIS`. This ordering is consistent across all three 3D nearest-neighbor workloads.

The `docs/reports/goal318_v0_5_preview_support_matrix_2026-04-12.md` document confirms that this Linux ordering and the backend roles are supported by already closed reports, specifically referencing:
-   `docs/reports/goal315_v0_5_vulkan_3d_nn_closure_2026-04-12.md`
-   `docs/reports/goal316_v0_5_linux_large_scale_embree_optix_vulkan_perf_2026-04-12.md`
-   `docs/reports/goal317_v0_5_current_linux_4backend_nn_perf_report_2026-04-12.md`
-   earlier closed CPU/oracle, Embree, OptiX, and PostGIS `v0.5` NN slices.

This indicates that the claims made in the support matrix regarding Linux backend performance and ordering are well-substantiated by preceding validation efforts.

## 4. Explicit Windows/macOS/PostGIS Boundaries

The support matrix maintains clear and explicit boundaries for Windows, macOS, and PostGIS:

-   **local macOS**: Described as for "development, focused regression, bounded local checks," with explicit statements that "Vulkan and OptiX are not being claimed as validated macOS `v0.5` runtime lines" and "no large-scale macOS NN performance claim." Bounded Embree 3D nearest-neighbor correctness is verified.
-   **Windows**: Positioned as a "secondary portability/bring-up host; no current large-scale `v0.5` NN performance claim." It also explicitly states that "no current `v0.5` large-scale nearest-neighbor performance claim is being made for Windows" and "Windows is not required for the current Linux performance story." Bounded Embree 3D nearest-neighbor correctness is verified.
-   **PostGIS**: Identified as an "external correctness and timing anchor" and a "supporting baseline," with the "Honest Summary" clarifying that "PostGIS remains the external correctness/timing anchor, not the target production runtime."

These explicit statements align perfectly with the "Important honesty boundary" section of `docs/reports/goal318_v0_5_preview_support_matrix_2026-04-12.md`, which emphasizes that the document "does not claim final cross-platform backend maturity" and "does not upgrade Windows or macOS into large-scale performance platforms" or "turn PostGIS into a target production backend."

## 5. Conclusion

The `RTDL v0.5 Preview Support Matrix` (`docs/release_reports/v0_5_preview/support_matrix.md`) successfully meets the objectives of Goal 318. It provides a technically honest, clear, and well-structured overview of the current `v0.5` backend/platform state. The document explicitly details Linux backend ordering and roles, supported by referenced closed reports, and clearly delineates the bounded roles of Windows, macOS, and PostGIS. The review confirms that the support matrix is an accurate and honest reflection of the current development status.
