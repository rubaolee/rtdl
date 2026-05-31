# Gemini Review for Goal2797

Date: 2026-05-31

## Verdict

`accept-with-boundary`

## Review Questions

1.  **Does the new harness genuinely make Triangle Counting rerunnable as a v2.5 canonical harness for both RT-2A1 and RT-1A2 generic lowerings?**
    Yes, the `scripts/goal2797_triangle_counting_v25_canonical_harness.py` script and its associated tests confirm that Triangle Counting is rerunnable for both `rt_graph_2a1_generic_rt` and `rt_graph_1a2_generic_rt` lowerings. The pod evidence in `docs/reports/goal2797_pod_artifacts/triangle_counting_v25_canonical_harness_5000_optix.json` demonstrates successful execution and oracle matching for both methods on OptiX.

2.  **Does the harness preserve the primitive-first design instead of forcing or relabeling a Triton continuation?**
    Yes, the primitive-first design is preserved. The `docs/reports/goal2797_triangle_counting_v2_5_canonical_harness_2026-05-31.md` report explicitly states, "The benchmark remains primitive-first: RT-Graph-style triangle counting lowers to generic RTDL ray/triangle scalar-summary primitives. This goal does not force a Triton continuation when the scalar summary is already the right generic RTDL primitive." The manifest entry in `src/rtdsl/v2_5_triton_app_migration.py` also categorizes Triangle Counting under `primitive_first_rt_summary` and clarifies that Triton should only be added for row-stream or compact-mask modes if scalar summary is insufficient.

3.  **Does the pod artifact support the narrow claim that the OptiX rows match the oracle on the measured disjoint-triangle scales?**
    Yes. The `docs/reports/goal2797_pod_artifacts/triangle_counting_v25_canonical_harness_5000_optix.json` clearly shows `status: "pass"` and `triangle_count_matches_oracle: true` for all tested triangle counts (16, 1024, 5000) for both `rt_graph_2a1_generic_rt` and `rt_graph_1a2_generic_rt` methods when run with the OptiX backend. The report also visually confirms this with "Match: yes" in its results table.

4.  **Does the manifest update close the previous `needs_single_rerunnable_harness` gap without overclaiming release readiness or paper reproduction?**
    Yes. The `src/rtdsl/v2_5_triton_app_migration.py` manifest update correctly sets `canonical_harness_status="ready_with_goal2797_canonical_harness"` for Triangle Counting, effectively closing the gap. Overclaiming is prevented by the explicit `CLAIM_BOUNDARY` defined in the harness script, reflected in the pod artifact, and detailed in the `docs/reports/goal2797_triangle_counting_v2_5_canonical_harness_2026-05-31.md` report, which states that public speedup, Triton speedup, true zero-copy, and paper reproduction claims are blocked.

5.  **Do the tests guard the generator, local CPU path, manifest status, pod artifact, and claim boundary?**
    Yes, comprehensive tests are in place:
    *   **Generator**: `test_disjoint_triangle_generator_has_expected_oracle_shape`
    *   **Local CPU path**: `test_cpu_harness_matches_oracle_for_both_lowerings`
    *   **Manifest status**: `test_manifest_records_goal2797_canonical_harness_status`
    *   **Pod artifact**: `test_pod_artifact_records_optix_same_contract_rows`
    *   **Claim boundary**: `test_cpu_harness_matches_oracle_for_both_lowerings` (checks `public_speedup_claim_authorized` in harness output), `test_pod_artifact_records_optix_same_contract_rows` (checks `public_speedup_claim_authorized` in pod JSON), and `test_report_and_consensus_record_boundary` (checks boundary wording in report/consensus files).

## Claim Boundary

Goal2797 is harness/correctness evidence only. It must not authorize public speedup, whole-app speedup, Triton speedup, true zero-copy, paper reproduction, or v2.5 release claims.
