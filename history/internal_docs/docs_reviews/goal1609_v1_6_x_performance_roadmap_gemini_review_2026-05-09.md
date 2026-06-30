# Verdict: ACCEPT

The `docs/reports/goal1609_v1_6_x_performance_roadmap_2026-05-09.md` roadmap is clear, safely sequenced, claim-safe, and practical. It establishes a rigorous empirical foundation for performance tuning that avoids premature claims and manages hardware costs effectively.

### Analysis Summary

*   **Clarity:** The document provides a well-defined progression from `v1.6.1` to `v1.6.10`, with explicit goals, deliverables, and acceptance gates for each phase. The distinction between the "Starting Point" and "North Star" is sharp.
*   **Safety & Sequencing:** The roadmap correctly prioritizes "Measurement Before Optimization" (`v1.6.1`). By ensuring that phase-timing and copy-counting are standardized before attempting GPU-based tuning, it prevents the common pitfall of "vague exploration" on expensive hardware.
*   **Claim Integrity:** The strict blocking of "true zero-copy" and "broad RTX speedup" wording is a major strength. The allowed wording is appropriately narrow, focusing on measured subpaths rather than whole-app claims.
*   **Practicality:** The Pod Policy is an excellent practical constraint, ensuring that paid hardware resources are only utilized after local validation is successful and benchmark scripts are fully prepared.

### Special Attention Areas

*   **COLLECT_K_BOUNDED:** The plan to keep this experimental until `v1.6.4` (the fail-closed promotion attempt) is the correct approach. Requiring explicit capacity/overflow metadata for stability before claiming performance is a sound engineering decision.
*   **Reduced-Copy vs. True Zero-Copy:** The roadmap maintains a clear technical boundary here. It focuses on the achievable goal of reducing materialization overhead (`v1.6.3`) while explicitly prohibiting zero-copy claims until device-resident memory management is actually implemented and proven.
*   **OptiX/NVIDIA Pod Usage:** The "batch all ready workloads" and "validate from Git" policies ensure that pod time is treated as a precious resource.
*   **Public Speedup Wording:** The audit gate at `v1.6.9` ensures that marketing or public-facing documentation remains synchronized with engineering evidence.

### Non-Blocking Notes

1.  **Phase Granularity (Goal 1610):** When creating the measurement manifest, ensure that "scene preparation" and "ray packing" are distinct from "launch time." In `v1.6.5`, the bottleneck is often the host-to-device transfer of the scene graph or rays rather than the RT-core traversal itself.
2.  **Thin Result Views (v1.6.7):** While compatibility rows are preserved, consider providing a migration path or "best practice" guide for users to transition to thin views, as this is likely where the most significant Python-side performance gains will be realized.
3.  **App-Generic Session API (v1.6.6):** This is a critical deliverable. Ensuring that the session object handles "stale" or "wrong-shape" failures explicitly will prevent hard crashes in the native layer when users attempt to reuse buffers across different query shapes.
