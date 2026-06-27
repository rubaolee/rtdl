# Review for Goal2083: Streaming Witness Page Pod Evidence

**Date:** 2026-05-15
**Reviewer:** Gemini

**1. Do the pod artifacts support the report table values for 4096, 8192, and 16384?**

Yes, the pod artifacts fully support the report table values.
I compared the `median_s` values from the `v1_8_native_optix_rows`, `v2_0_partner_columns_full_python_rows`, and `v2_0_streaming_exact_witness_page_columns` sections in each of the three JSON artifact files (`goal2081_streaming_witness_page_perf_pod_4096_cupy_capacity.json`, `goal2081_streaming_witness_page_perf_pod_8192_cupy_capacity.json`, and `goal2081_streaming_witness_page_perf_pod_16384_cupy_capacity.json`) with the "v1.8 native OptiX rows sec", "old v2 full Python rows sec", and "new v2 streaming witness columns sec" columns in the markdown report's "Results" table. All raw median values align with the reported table values after rounding. The calculated ratios (`old v2 / v1.8`, `new v2 / v1.8`, `new v2 / old v2`) derived from the JSON artifacts also precisely match those presented in the report table for all `count` values.

**2. Is it correct to say the old weak row was an output-contract problem rather than a native traversal problem?**

Yes, it is correct. The `docs/reports/goal2083_streaming_witness_page_pod_evidence_2026-05-15.md` explicitly states, "The weak row was not fundamentally an RT traversal problem. It was an output-contract problem." It further clarifies that "The old v2 full-row path had to convert exact witnesses into Python dictionaries." This is consistent with the `docs/reviews/goal2082_gemini_review_goal2081_streaming_witness_page_adapter_2026-05-15.md`, which noted that the problem was "avoiding full Python witness-row materialization."

**3. Is it correct to distinguish the new streaming witness-column contract from the old full Python row contract?**

Yes, this distinction is correct and crucial to the reported improvements. The report clearly differentiates between the "old v2 full Python rows sec" and "new v2 streaming witness columns sec" in its results table and interpretation. It explains that the "old v2 full-row path had to convert exact witnesses into Python dictionaries," while "the new path keeps exact witness IDs in CuPy columns, pages them, and avoids Python row-table materialization." This is further supported by `docs/reviews/goal2082_gemini_review_goal2081_streaming_witness_page_adapter_2026-05-15.md` and the `tests/goal2083_streaming_witness_page_pod_evidence_test.py` which verifies that `full_python_row_table_materialization_avoided` is true for the new path.

**4. Are claim boundaries preserved: no v2.0 release authorization, no broad whole-app speedup claim, and external review required before final table update?**

Yes, the claim boundaries are consistently and explicitly preserved across all reviewed documents.
*   The "Boundary" section in `docs/reports/goal2083_streaming_witness_page_pod_evidence_2026-05-15.md` clearly sets `v2_0_release_authorized: false` and `whole_app_speedup_claim_authorized: false`, and states that "external review is required before using this as final release evidence."
*   The JSON artifacts also contain `v2_0_release_authorized: false`, `whole_app_speedup_claim_authorized: false`, and `requires_pod_review_before_table_update: true` within their `claim_boundary` and `metadata` sections.
*   `docs/reviews/goal2082_gemini_review_goal2081_streaming_witness_page_adapter_2026-05-15.md` also confirmed these same boundaries.
*   The test `tests/goal2083_streaming_witness_page_pod_evidence_test.py` asserts `self.assertFalse(metadata["v2_0_release_authorized"])` and `self.assertIn("external review is required", report)`.

**5. Flag any wording or evidence risk.**

No significant wording or evidence risks were identified. The report is clear, concise, and precise in its language. The evidence presented in the pod artifacts directly supports the numerical claims in the report table, and the consistency across all documents (report, JSON artifacts, previous review, and tests) is high. The careful delineation of the problem as an "output-contract" issue rather than a "native traversal" problem, and the explicit distinction between the old and new witness contracts, demonstrate strong attention to detail and avoid ambiguity.

**Verdict:** `accept-with-boundary`
