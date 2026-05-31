# Gemini Review For Goal2803 Barnes-Hut v2.5 Consolidated Harness

Date: 2026-05-31

Verdict: accept-with-boundary

## Blocking Issues

None.

## Review Questions and Answers

1.  **Does Goal2803 provide a real current consolidated harness for `barnes_hut`, not only historical report links?**
    *   **Answer**: Yes. The `scripts/goal2803_barnes_hut_v25_consolidated_harness.py` script is an executable Python program that runs both the RT-assisted expanded-membership lowering (Embree vs. OptiX) and the partner grouped vector-sum continuation (Torch vs. Triton). It generates a JSON artifact with current performance and correctness results. The report (`docs/reports/goal2803_barnes_hut_v2_5_consolidated_harness_2026-05-31.md`) explicitly states its status as "implemented locally with first Embree/OptiX/Torch/Triton pod evidence" and directly references the harness script as a current component, not merely a historical link.

2.  **Does it cover both the RT-assisted expanded-membership lowering and the partner grouped vector-sum continuation clearly?**
    *   **Answer**: Yes.
        *   **RT-assisted expanded-membership lowering**: The harness script's `_run_membership_cases` function directly executes and compares Embree and OptiX for expanded-membership aggregate-frontier lowering. The generated artifact explicitly records `optix_rt_core_accelerated: true` and `rows_match_between_backends: true`. The report's purpose section clearly outlines this coverage.
        *   **Partner grouped vector-sum continuation**: The harness script's `_run_vector_sum_probe` function performs a comparison between Torch and Triton for grouped vector sums. The report details this comparison, validating its explicit coverage.

3.  **Does the artifact preserve same-contract membership parity and record OptiX RT-core use for the generic membership subpath?**
    *   **Answer**: Yes.
        *   **Same-contract membership parity**: The `membership_rows` in the `barnes_hut_v25_consolidated_harness.json` artifact consistently show `rows_match_between_backends: true`, confirming that the membership computation results are identical between Embree and OptiX, thus preserving same-contract parity.
        *   **OptiX RT-core use**: For all membership rows in the artifact, `optix_rt_core_accelerated: true` is explicitly recorded, indicating that the OptiX path utilized RT-cores for the generic membership subpath.

4.  **Does the vector-sum probe compare Torch and Triton honestly and keep Triton auto-selection blocked when appropriate?**
    *   **Answer**: Yes.
        *   **Honest comparison**: The `_run_vector_sum_probe` within the harness script measures and records performance for both Torch and Triton. The JSON artifact explicitly states `matches_torch: true` (for correctness), `torch_faster: true`, and provides a `triton_over_torch_ratio` of `6.844x slower`, demonstrating an honest and data-driven comparison where Triton is currently slower.
        *   **Triton auto-selection blocked**: The harness script explicitly sets `triton_vector_sum_auto_selection_allowed: False`, and this is reflected in the generated JSON artifact. The report, the test (`tests/goal2803_barnes_hut_v25_consolidated_harness_test.py`), and the `src/rtdsl/v2_5_triton_app_migration.py` manifest all contain specific checks and wording to ensure Triton auto-selection remains blocked due to its current performance characteristics.

5.  **Does the report avoid paper reproduction, authors-code comparison, public speedup, whole-app speedup, and native app-customization claims?**
    *   **Answer**: Yes. The "Boundary" section of `docs/reports/goal2803_barnes_hut_v2_5_consolidated_harness_2026-05-31.md` explicitly lists all these items as "Not claimed". This aligns with the `CLAIM_BOUNDARY` variable in the harness script and corresponding `false` flags in the JSON artifact. The associated test file also includes assertions to verify these boundary claims are maintained in the report and other relevant documents.

6.  **Is clean-from-Git validation correctly identified as pending if it has not yet been recorded?**
    *   **Answer**: Yes. The "Validation" section of the report clearly states: "Focused tests, external review, consensus, and clean-from-Git pod validation are still pending at the time this report was first written." Furthermore, the `source_dirty` field in the `barnes_hut_v25_consolidated_harness.json` artifact shows pending changes, correctly indicating that the initial run was not from a clean Git state, thus corroborating the "pending" status for clean-from-Git validation.
