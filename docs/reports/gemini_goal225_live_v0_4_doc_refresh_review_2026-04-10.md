# Goal 225 Live v0.4 Doc Refresh Review (2026-04-10)

## Verdict

There are blocking issues regarding internal consistency across the reviewed documentation, specifically concerning the status of accelerated backend support for `knn_rows` and a misleading statement about "multiple backends" as a non-goal. Therefore, there are blocking issues.

## Findings

1.  **Contradiction in `docs/rtdl/dsl_reference.md` regarding `knn_rows` accelerated backend status.**
    *   **Location:** `/Users/rl2025/rtdl_python_only/docs/rtdl/dsl_reference.md`
    *   **Detail:** The "Predicates" section (lines 201-207) for `rt.knn_rows(k=...)` states: "accelerated backend support exists (Embree, OptiX, Vulkan)". However, the "Workload Contracts" section (lines 400-403) for `knn_rows` explicitly says: "Current closure is Python truth path plus native CPU/oracle. Accelerated backend closure is still pending." These two statements are directly contradictory within the same document.

2.  **Contradiction between `docs/rtdl/dsl_reference.md` and `docs/workloads_and_research_foundations.md` regarding `knn_rows` accelerated backend status.**
    *   **Locations:**
        *   `/Users/rl2025/rtdl_python_only/docs/rtdl/dsl_reference.md` (lines 400-403)
        *   `/Users/rl2025/rtdl_python_only/docs/workloads_and_research_foundations.md` (lines 35-37)
    *   **Detail:** `docs/workloads_and_research_foundations.md` states for `v0.4` workloads (`fixed_radius_neighbors`, `knn_rows`): "These are implemented in the active nearest-neighbor preview line (currently running across CPU/Oracle, Embree, OptiX, and Vulkan backends)". This directly contradicts the statement in `docs/rtdl/dsl_reference.md`'s "Workload Contracts" for `knn_rows` which claims "Accelerated backend closure is still pending."

3.  **Misleading statement in `docs/rtdl/dsl_reference.md` about "multiple backends" as a non-goal.**
    *   **Location:** `/Users/rl2025/rtdl_python_only/docs/rtdl/dsl_reference.md` (lines 463-475)
    *   **Detail:** The "Non-Goals Of The Current Language" section includes "multiple backends" as a non-goal. This is broadly misleading, as a core value proposition and demonstrated functionality of RTDL is to support workloads across multiple backends (Embree, OptiX, Vulkan, CPU Python reference). This statement should be clarified to specify what aspect of "multiple backends" is a non-goal (e.g., dynamic switching within a single kernel, or something similar), rather than implying that RTDL does not support multiple backends at all.

## Residual Risks

-   **User Confusion:** The identified contradictions and misleading statements will cause significant confusion for users attempting to understand the capabilities and limitations of RTDL, especially concerning `v0.4` features and GPU acceleration.
-   **Misaligned Expectations:** Users may have incorrect expectations about which backends are fully supported and stable for new `v0.4` features, potentially leading to frustration and wasted effort.
-   **Reduced Trust:** Inconsistent documentation erodes trust in the project's clarity and accuracy.

## Final Recommendation

The identified inconsistencies are blocking issues and must be resolved to ensure the `v0.4`-facing documentation accurately reflects the project's status and capabilities. Specifically:

1.  Clarify the exact status of accelerated backend support for `knn_rows` in `docs/rtdl/dsl_reference.md`, ensuring consistency between the "Predicates" and "Workload Contracts" sections.
2.  Ensure consistency in the accelerated backend status for `knn_rows` between `docs/rtdl/dsl_reference.md` and `docs/workloads_and_research_foundations.md`.
3.  Rewrite the "multiple backends" non-goal statement in `docs/rtdl/dsl_reference.md` to accurately convey its specific meaning without broadly contradicting RTDL's core functionality.

After these corrections are made, another review should be conducted to verify their successful implementation and overall consistency.