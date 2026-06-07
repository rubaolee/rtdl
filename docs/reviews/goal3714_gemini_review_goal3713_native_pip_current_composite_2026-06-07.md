# Gemini Review For Goal3713 Native-PIP Current Composite

## Review Questions & Answers:

1.  **Does Goal3713 correctly summarize the artifact numbers: all-CuPy `1.430714336s`, native-PIP mixed `0.005322640s`, `268.798x`, all counts matching?**
    *   **Answer:** Yes, the report and `summary.json` consistently show:
        *   All-CuPy Sum Median Sec: `1.430714336s`
        *   Native-PIP Mixed Sum Median Sec: `0.005322640s`
        *   Mixed Speedup Vs All-CuPy: `268.798x`
        *   Counts Match: `true`

2.  **Does it correctly identify the PIP improvement over Goal3711: PIP moves from CuPy parity to RTDL/OptiX native scalar count, with `2.590x` PIP-leg speedup and `1.099x` composite improvement?**
    *   **Answer:** Yes, the report clearly states that PIP moves to the "RTDL/OptiX native relation-status corrected scalar count" and provides the `2.590x` PIP-leg speedup and `1.099x` composite improvement. These numbers are consistent with the data provided.

3.  **Does it preserve the app-agnostic boundary: generic closed-shape membership scalar count, not RayJoin-specific native engine logic?**
    *   **Answer:** Yes, the report explicitly states under "Interpretation" that "The native engine remains generic: closed-shape membership scalar count, relation-status correction, prepared points, and prepared shapes." The `summary.json` also confirms the `output_contract` for PIP as "closed_shape_membership_scalar_count".

4.  **Is the claim boundary honest: internal same-contract evidence only, not public speedup, not release, not RTDL-beats-RayJoin, not RayJoin paper reproduction, not broad RT-core speedup, and not true zero-copy?**
    *   **Answer:** Yes, the report's "Status" and "Boundary" sections, along with the `claim_boundary` flags in `summary.json`, clearly and repeatedly define that this is "internal same-contract performance evidence" and does *not* authorize any public claims, releases, or broader statements about RTDL-beats-RayJoin, paper reproduction, RT-core speedup, or true zero-copy. The test `test_claim_boundary_flags_remain_false` also verifies these flags.

5.  **Are there any correctness, metadata, or route-naming issues that should block treating Goal3713 as the current internal recommended RayJoin mixed route pending broader tests?**
    *   **Answer:** No.
        *   **Correctness:** The report and `summary.json` confirm "all counts match," and the test suite verifies this.
        *   **Metadata:** The `summary.json` contains appropriate and consistent metadata (`git_commit`, `gpu`, `schema`).
        *   **Route-naming:** Route names are descriptive and align with the technical goals.
    *   No blocking issues were identified. The report appropriately acknowledges "Remaining Work" including external review and broader tests.

## Verdict:

`accept-with-boundary`

## Justification:

Goal3713 successfully demonstrates the integration of the native RTDL/OptiX scalar count executor for the PIP leg into the RayJoin mixed route, achieving significant speedup (`2.590x` for PIP, `1.099x` composite) while preserving correctness (all counts match). The report clearly and consistently adheres to the specified claim boundaries, explicitly stating its internal nature and refraining from broader authorizations. Metadata and route-naming are consistent and clear. The identified "Remaining Work" correctly scopes this internal recommendation, making `accept-with-boundary` the appropriate verdict.