# Gemini Independent Review: Goal3050 Partner Choice Docs

Date: 2026-06-02

This is an independent review of Goal3050, distinct from Codex authoring.

## Verdict: accept

## Review Questions Addressed:

1.  **Does the guide clearly answer when a user should choose CuPy vs Numba for custom logic, while keeping RTDL primitive-first as the default?**
    *   Yes. `docs/learn/partner_choice_for_custom_logic.md` explicitly states "Use the RTDL primitive first" and provides clear guidance, including a "Quick Choice" table and detailed sections on "CuPy Strengths" and "Numba Strengths," for selecting a partner when custom logic is needed. It strongly emphasizes that "RTDL does not accelerate arbitrary Numba or CuPy programs."

2.  **Does the benchmark matrix cover the promoted benchmark apps without overclaiming performance?**
    *   Yes. `docs/learn/benchmark_partner_reference_matrix.md` covers the ten promoted research apps. It includes "Evidence boundary" columns for each entry, which consistently qualify performance claims and refer to specific artifacts or conditions (e.g., "cite Goal3046/3048 artifacts before publishing"). The "Status" and "How To Use This Matrix" sections further reinforce cautious interpretation and evidence-based decision-making.

3.  **Does the wording preserve the rule that users choose partners explicitly and that RTDL does not accelerate arbitrary CuPy/Numba programs?**
    *   Yes. This rule is consistently and clearly articulated across all reviewed documents. `docs/learn/partner_choice_for_custom_logic.md` states "Choose the partner explicitly" and "RTDL does not accelerate arbitrary Numba or CuPy programs." Similar statements are found in `docs/learn/benchmark_partner_reference_matrix.md` and the `docs/reports/goal3050_partner_choice_for_custom_logic_docs_and_benchmark_matrix_2026-06-02.md` "Design Boundary" section.

4.  **Are the v2.6 Numba statements honest: first-class for selected generic continuation contracts, but not automatically faster than CuPy?**
    *   Yes. `docs/learn/partner_choice_for_custom_logic.md` explicitly states: "The current v2.6 lane makes Numba first-class for selected generic continuation contracts. Numba is not automatically faster than CuPy. It wins only when the contract, launch shape, and data residency are good for that workload." This honesty is further supported by the nuanced "Numba role" descriptions in the benchmark matrix, which often highlight its use for correctness and contract evidence rather than universal performance gains.

5.  **Are any benchmark rows misleading, missing, or inconsistent with current evidence?**
    *   Based on the provided documentation, the benchmark rows appear consistent with the stated philosophy of evidence-based claims and cautious language. All ten promoted research apps are covered. The "Evidence boundary" column in the matrix and the general guidance on publishing performance ensure that claims are qualified. Without direct access to the raw benchmark evidence, a definitive statement about "inconsistency with current evidence" cannot be made, but the documentation itself adheres to strict principles to prevent such inconsistencies from being published. No rows appear overtly misleading or missing.

## Final Note:
The documentation carefully avoids authorizing a v2.6 release, package install wording, broad RT-core speedup wording, broad CuPy/Numba acceleration wording, or hidden partner auto-selection, as instructed.
