# Independent Gemini Review: Goal3693 RayJoin LSI Mismatch Localizer

**Date:** 2026-06-07

**Reviewer:** Gemini CLI

**Verdict:** accept-with-boundary

## Summary of Findings

Goal3693 successfully localized the one-row LSI mismatch identified in Goal3691 between RTDL and the original RayJoin implementation. The evidence unequivocally points to a single missing segment-pair in RTDL, with no extraneous pairs, after normalizing RTDL's one-based edge IDs. This missing pair `(230119, 226567)` is a near-endpoint intersection, where exact arithmetic correctly identifies a hit (`t ~= 7.57e-5`), but a simulated float32 device-style predicate rounds the coordinates sufficiently to cause `t` to become negative, leading to the candidate being dropped.

The report adheres to the principle of keeping the solution generic and app-agnostic, explicitly rejecting RayJoin-specific native engine logic. It proposes robust solutions for generic segment-pair candidate emission, such as emitting ambiguous near-boundary candidates or adopting a high-precision/scaled predicate mode, potentially complemented by typed status columns.

Crucially, the report maintains strict claim boundaries, disclaiming any authorization for release, public speedup claims, RTDL-beats-RayJoin assertions, RayJoin paper reproduction, broad RT-core claims, or true zero-copy claims. The findings are presented as an internal engineering conclusion, which is appropriate.

## Key Facts Verification

All key facts provided in the prompt were verified against the `docs/reports/goal3693_rayjoin_lsi_mismatch_localizer_2026-06-07.md` report and its accompanying artifacts, specifically `lsi_pair_set_diff_summary.json`, `missing_pair_geometry.json`, and `missing_pair_precision_probe.json`.

*   **LSI Count Mismatch:** Confirmed RayJoin reported `20860` and RTDL `20859`, with `1` missing from RTDL and `0` extra.
*   **Missing Pair:** Identified as `(230119, 226567)`.
*   **Endpoint-near Diagnosis:** Supported by the tiny `left_a_vs_right` orientation signal (`-4.1465700000E-8`) and the small positive `t` parameter for the intersection.
*   **Precision Probe:** Demonstrates how float32 rounding leads to `t` becoming negative, causing the pair to be dropped, while exact arithmetic maintains `t > 0`.
*   **Generic Solution Focus:** The report consistently emphasizes generic approaches and explicitly avoids RayJoin-specific native engine logic.
*   **Claim Boundaries:** The report's "Boundary" section is comprehensive and strict, disallowing any claims beyond internal engineering conclusions.

## Questions Answered

1.  **Does the evidence really localize the LSI mismatch to one normalized pair, with no RTDL extras?**
    *   **Answer:** Yes. The `lsi_pair_set_diff_summary.json` clearly shows a single missing pair (`230119, 226567`) in RTDL and zero extras, confirming precise localization.

2.  **Does the missing-pair geometry support the endpoint-near / precision-policy diagnosis?**
    *   **Answer:** Yes. The `missing_pair_geometry.json` and report details (tiny orientation signal, small `t` value) strongly support the endpoint-near diagnosis, indicating it's a candidate for precision-sensitive predicate behavior.

3.  **Does the precision probe reasonably explain how exact arithmetic includes the pair while a float32 candidate predicate can drop it?**
    *   **Answer:** Yes. The `missing_pair_precision_probe.json` demonstrates that exact arithmetic yields a positive `t`, while simulated float32 rounding results in a negative `t`, causing the pair to be dropped. This directly explains the discrepancy.

4.  **Does the report keep the solution generic and app-agnostic, without proposing RayJoin-specific native engine logic?**
    *   **Answer:** Yes. The report consistently advocates for generic segment-pair contract improvements and explicitly states that RayJoin-specific exceptions are a "Bad direction."

5.  **Are the claim boundaries strict enough: no release, public speedup, RTDL-beats-RayJoin, RayJoin reproduction, broad RT-core, or zero-copy claims?**
    *   **Answer:** Yes. The "Boundary" section is exceptionally strict and comprehensive, explicitly prohibiting all specified claims. This is further supported by the `segment_pair_contracts.py` file's claim boundaries.

6.  **What should the next generic segment-pair primitive/policy be: ambiguous candidate emission, high-precision/scaled candidate emission, typed status columns, or a different approach?**
    *   **Answer:** The report suggests multiple "Good directions," favoring either ambiguous candidate emission or a high-precision/scaled candidate emission path, potentially complemented by typed status columns. The "Next Work" section reinforces these as recommended steps.

## Conclusion

The Goal3693 RayJoin LSI Mismatch Localizer is a well-executed and insightful engineering effort. The precise localization and clear diagnosis of the LSI mismatch are highly valuable. The commitment to generic, app-agnostic solutions and strict claim boundaries aligns with best practices. The proposed next steps are logical and necessary to address this identified correctness gap. The verdict `accept-with-boundary` is given to reflect the comprehensive nature of the report's findings while emphasizing adherence to its carefully defined limitations.
