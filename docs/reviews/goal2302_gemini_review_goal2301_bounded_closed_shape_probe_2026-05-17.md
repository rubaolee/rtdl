# Goal2302 Gemini Review: Goal2301 Bounded Closed-Shape Point Probe

**Verdict:** `accept-with-boundary`

## Review Questions & Answers:

1.  **Confirm the source change stays app-agnostic: it changes the generic point/closed-shape membership probe geometry and does not add RayJoin, PIP, polygon, map, county, or join-specific native ABI names.**
    *   **Confirmation:** Yes. The report (`docs/reports/goal2301_bounded_closed_shape_point_probe_2026-05-17.md`) explicitly states: "The primitive remains app-agnostic. It still uses point, closed-shape, membership, and positive-row vocabulary; it does not add RayJoin, PIP, polygon, map, county, or join-specific logic to the native API." Examination of `src/native/optix/rtdl_optix_core.cpp` confirms that the modification is within the `__raygen__pip_probe` function, a generic PIP probe, and does not introduce application-specific naming.

2.  **Confirm the evidence supports the narrow claim: on the measured 100,000-query RayJoin-exported PIP stream, the bounded probe preserves the exact expected count `8686` and improves positive rows and scalar count over the current baseline.**
    *   **Confirmation:** Yes.
        *   **Exact count preservation:** Both baseline (`goal2301_bounded_point_probe_baseline_current_pod_2026-05-17.json`) and candidate (`goal2301_bounded_point_probe_candidate_pod_2026-05-17.json`) JSON artifacts consistently show `pip.expected_rows_from_prior_cpu_verified_artifacts: 8686` and `pip.positive_rows.values` and `pip.scalar_count.values` arrays containing `8686` for all repeats. The `matches_prior_expected_count` field is `true` in both.
        *   **Performance improvement:**
            *   **Positive rows median:** Baseline: `0.051157122 s`, Candidate: `0.018218992 s`. This represents a speedup of approximately `2.808x`.
            *   **Scalar count median:** Baseline: `0.037854942 s`, Candidate: `0.007748827 s`. This represents a speedup of approximately `4.885x`.
            These figures align with the "Result" table in the main report. The `goal2301_bounded_point_probe_candidate_pip_count_phase_pod_2026-05-17.json` artifact further illustrates the reduction in `candidate_write_pass` times (around `0.0031s`) compared to the baseline, supporting the performance gains.

3.  **Confirm the two tiny-probe variants are correctly rejected because they returned zero positives.**
    *   **Confirmation:** Yes. The "Rejected Variants" section in the report explains that both tiny-probe variants returned zero PIP positives. This is confirmed by the JSON artifacts:
        *   `goal2301_short_origin_inside_negative_pod_2026-05-17.json` shows `pip.scalar_count.values` as `[0, ..., 0]`.
        *   `goal2301_tiny_crossing_negative_pod_2026-05-17.json` shows `values` as `[0, ..., 0]`.

4.  **Confirm the report does not overclaim RayJoin reproduction, RTDL beating RayJoin, whole-app speedup, true zero-copy, or v2.0 release readiness.**
    *   **Confirmation:** Yes. The "Boundary" section of the report explicitly disclaims: "No RayJoin paper reproduction.", "No claim that RTDL beats RayJoin.", "No broad whole-app acceleration claim.", "No true zero-copy claim.", and "No v2.0 release authorization."

5.  **Note any risks: fixed `0.5` half-length generality, other coordinate scales, possible future need for a configurable/proven query extent, or missing additional datasets.**
    *   **Risks noted:**
        *   **Fixed `0.5` half-length generality and coordinate scales:** The use of a hardcoded `0.5f` for the probe segment's half-length (i.e., `py - 0.5f` to `py + 0.5f`) in `src/native/optix/rtdl_optix_core.cpp` introduces a dependency on the coordinate scale of the input data. While effective for the specific RayJoin-exported dataset used, this fixed length may not be appropriate for all potential datasets. Datasets with vastly different spatial extents (e.g., very large or very small coordinates) might see issues with missed intersections (probe too short) or reduced performance benefits (probe still too long).
        *   **Future need for configurable/proven query extent:** For broader applicability and robustness, the fixed `0.5` half-length may need to be made configurable, dynamically adjusted based on dataset characteristics, or empirically proven to be suitable across a wider range of common use cases.
        *   **Missing additional datasets:** The performance and correctness claims are strictly limited to "the measured 100,000-query RayJoin-exported PIP stream." The absence of evaluation on diverse datasets means the generalizability of the observed speedups and the appropriateness of the `0.5` probe length are currently unverified for other scenarios.

**Summary:**
The Goal2301 bounded closed-shape point probe provides a significant and verified performance improvement for the specified point-in-polygon workload while preserving exact count parity. The change is appropriately scoped as app-agnostic. The report clearly outlines its claims and boundaries, and the rejection of less robust probe variants is well-supported by evidence. The primary risk identified is the hardcoded `0.5` half-length of the probe, which, while effective for the tested data, may require further investigation for general applicability across varying coordinate scales and datasets. Given the explicit boundary conditions and the solid evidence for the narrow claim, the change is accepted with the understanding that its generalizability remains an area for future consideration.
