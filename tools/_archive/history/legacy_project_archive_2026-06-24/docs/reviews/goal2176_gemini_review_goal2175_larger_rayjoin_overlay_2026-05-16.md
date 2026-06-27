# Gemini Review: Goal2175 Larger RayJoin Overlay

**Date:** 2026-05-16

**Reviewer:** Gemini Agent

## Goal 2175: Larger RayJoin Overlay

### Review Questions and Answers:

1.  **Verify that the `overlay_compose_cpu` reference change is a correctness-harness optimization, not a semantic change:**
    *   **Finding:** Verified.
        The change to `overlay_compose_cpu` in `src/rtdsl/reference.py` is a correctness-harness optimization. The report `docs/reports/goal2175_larger_rayjoin_overlay_seed_reference_fix_and_pod_evidence_2026-05-16.md` states that the fix addresses the reference materialization cost by precomputing pair sets (`lsi_pairs` and `pip_pairs`), which "preserves the same row contract" and that the "public schema is unchanged: `left_polygon_id`, `right_polygon_id`, `requires_lsi`, `requires_pip`."
        The test `tests/goal2175_overlay_reference_pair_set_materialization_test.py` (`test_overlay_reference_preserves_lsi_and_pip_flags`) explicitly confirms semantic preservation by checking expected LSI and PIP flags for specific polygon pairs. The same test (`test_overlay_reference_uses_pair_sets_not_repeated_hit_scans`) verifies the implementation uses pair sets and avoids repeated hit scans, confirming the optimization.
    *   **Same output fields:** Verified. The report explicitly states the public schema remains unchanged (`left_polygon_id`, `right_polygon_id`, `requires_lsi`, `requires_pip`).
    *   **Same LSI and first-vertex PIP dependency flag semantics:** Verified. The test `test_overlay_reference_preserves_lsi_and_pip_flags` confirms this by asserting specific (LSI, PIP) flag values for known polygon pairs.
    *   **Pair-set materialization is reasonable for larger overlay rows:** Verified. The use of precomputed `lsi_pairs` and `pip_pairs` in `overlay_compose_cpu` (as seen in `src/rtdsl/reference.py`) to perform O(1) set lookups is a sound optimization for larger datasets, avoiding redundant computation for each polygon pair.

2.  **Verify the pod artifact numbers for `overlay_county256_soil256`:**
    *   **Finding:** Verified.
        All specified numbers from `docs/reports/goal2175_overlay_count256_shared_reference_pod_2026-05-16.json` and `docs/reports/goal2175_larger_rayjoin_overlay_seed_reference_fix_and_pod_evidence_2026-05-16.md` are consistent:
    *   **commit:** `9a4b8ae1ef054406eeda8475a51f24ed3f225459`
    *   **left polygons:** `241`
    *   **right polygons:** `236`
    *   **rows:** `56876` (both `candidate_pair_count` and `shared_reference.row_count`)
    *   **shared CPU Python reference rows:** `56876`
    *   **CPU/native-oracle median:** `2.1851774686947465`
    *   **Embree median:** `0.13478228449821472`
    *   **OptiX one-shot median:** `0.07310969196259975`
    *   **prepared OptiX median:** `0.07800947688519955`
    *   **all four backends parity-clean:** Verified, the `all_parity_vs_cpu_python_reference` flag is `true` for all listed backends in the JSON artifact.

3.  **Judge whether the narrow performance interpretation is valid:**
    *   **Finding:** Valid.
        The performance interpretations are consistent with the provided data:
    *   **one-shot OptiX beats Embree by `1.844x` on this exact same-contract row:** Verified. Calculated ratio: `0.13478228449821472 (Embree) / 0.07310969196259975 (OptiX one-shot) = 1.84358...`, which matches the `1.844x` claim.
    *   **prepared OptiX beats Embree by `1.728x` on this exact same-contract row:** Verified. Calculated ratio: `0.13478228449821472 (Embree) / 0.07800947688519955 (OptiX prepared) = 1.72776...`, which matches the `1.728x` claim.
    *   **prepared OptiX is not always faster than one-shot OptiX:** Verified. The OptiX one-shot median (`0.07310969196259975`) is indeed faster than the prepared OptiX median (`0.07800947688519955`) for this specific row. The report also explicitly states this in its "Interpretation" section: "Prepared state remains a valid design pattern, but this row shows that the current one-shot OptiX path can be faster at this scale."

4.  **Verify that the report does not overclaim:**
    *   **Finding:** Verified.
        The "Claim Boundary" section of `docs/reports/goal2175_larger_rayjoin_overlay_seed_reference_fix_and_pod_evidence_2026-05-16.md` explicitly lists and denies authorization for the following:
    *   **no full RayJoin paper reproduction:** Explicitly denied.
    *   **no broad RT-core speedup:** Explicitly denied.
    *   **no v2.0 release authorization:** Explicitly denied.
    *   **no whole-app RayJoin speedup:** Explicitly denied.
    *   **no claim against stronger CUDA/CuPy spatial-prefilter baselines:** Explicitly denied.
        The `claim_boundary` object in the `docs/reports/goal2175_overlay_count256_shared_reference_pod_2026-05-16.json` artifact also has all corresponding flags set to `false`, confirming these limitations.

## Verdict:

`accept`