# Gemini Review: Goal2847 Current-Head Canonical Harness Refresh

Date: 2026-05-31

This is an independent Gemini review, distinct from Codex.

Verdict: **accept-with-boundary**

## Review Summary

Goal2847 successfully reran the seven canonical v2.5 RTX pod harnesses on current `main` (`23b047e5d44bfda7e535ca7ba78d94f195e2be86`). All artifacts (`goal2797_triangle_counting.json`, `goal2798_librts.json`, `goal2799_spatial_rayjoin.json`, `goal2800_rtnn.json`, `goal2801_hausdorff_xhd.json`, `goal2802_rt_dbscan.json`, `goal2803_barnes_hut.json`) report `status: pass`, `source_dirty: []`, and GPU `NVIDIA RTX A5000, 570.211.01`. The accompanying test `tests/goal2847_current_head_canonical_harness_refresh_test.py` validates these fundamental properties.

The report `docs/reports/goal2847_current_head_canonical_harness_refresh_2026-05-31.md` is well-structured and transparently addresses claim boundaries, explicitly stating that this is not a v2.5 release authorization nor a public speedup claim. It also correctly highlights known weak spots and areas for future improvement.

## Review Questions

### 1. Do the seven artifacts really establish a clean current-head pod pass for the canonical v2.5 harness packet?

Yes, the `goal2847_summary.json` explicitly states `"all_pass": true` and identifies the `source_commit` as `23b047e5d44bfda7e535ca7ba78d94f195e2be86`. Each individual artifact JSON (`goal2797_triangle_counting.json` through `goal2803_barnes_hut.json`) confirms `status: "pass"`, an empty `source_dirty` list (`[]`), and the expected GPU `NVIDIA RTX A5000, 570.211.01`. The test `test_all_expected_artifacts_are_present_and_pass` in `tests/goal2847_current_head_canonical_harness_refresh_test.py` rigorously verifies these conditions. This establishes a clean current-head pass for the canonical v2.5 harness packet.

### 2. Are the claim boundaries in the report accurate and sufficiently cautious?

Yes, the claim boundaries are accurate and sufficiently cautious. The report explicitly states, "This is **not a v2.5 release authorization** and not a public speedup claim." Furthermore, the "Claim Boundary" section details that no whole-app speedup, paper reproduction, or broad public speedup claims are authorized. Specific caveats are provided for Hausdorff (slower than optimized CuPy grid), RTNN (distribution-dependent performance), and Barnes-Hut (Triton vector sum not promoted). The `test_claim_boundaries_remain_fail_closed` in the test suite confirms that relevant `claim_boundary` flags in the artifacts are set to `false`, reinforcing these cautious statements.

### 3. Does the report correctly call out weak spots: RTNN distribution dependence, Hausdorff slower than optimized CuPy grid, Barnes-Hut Triton vector sum not promoted, Barnes-Hut large case progress logging debt?

Yes, the report correctly calls out all listed weak spots:
*   **RTNN distribution dependence:** The report notes, "RTNN remains distribution-dependent: clustered and shell favor the RTDL prepared aggregate path, while uniform is slightly slower than the CuPy grid opponent."
*   **Hausdorff slower than optimized CuPy grid:** It states, "Hausdorff remains slower than the optimized CuPy baseline," and provides a clear performance ratio.
*   **Barnes-Hut Triton vector sum not promoted:** The report explains, "Therefore Triton auto-selection remains disabled for this path" due to Triton being slower than Torch.
*   **Barnes-Hut large case progress logging debt:** The report identifies this, stating, "Barnes-Hut needs better progress logging: the 8,192-body case spent about 342 seconds inside a quiet CPU-heavy comparison window before printing its completion line."
The `test_report_records_current_head_verdict_and_debt` test verifies that these phrases are present in the report.

### 4. Does the test cover the important integrity properties without overstating release readiness?

Yes, the test `tests/goal2847_current_head_canonical_harness_refresh_test.py` comprehensively covers important integrity properties. It validates the presence and pass status of all artifacts, the correct source commit and GPU, and the absence of dirty sources. Crucially, `test_claim_boundaries_remain_fail_closed` and `test_report_records_current_head_verdict_and_debt` specifically ensure that the report and artifacts correctly disclaim unauthorized public speedup or release claims, thus preventing any overstatement of release readiness. The test confirms that specific performance metrics and their boundaries are as expected, maintaining integrity without implying broader claims.

### 5. Are there any stale public-speedup or release-authorization claims that should be removed or tightened?

No, there are no stale public-speedup or release-authorization claims. Both the report and the individual JSON artifacts consistently use "fail-closed" flags for all such claims (`public_speedup_claim_authorized: false`, `whole_app_speedup_claim_authorized: false`, `paper_reproduction_claim_authorized: false`, etc.). The review confirms that these claims are explicitly denied or appropriately qualified in both the human-readable report and the machine-readable artifacts, and this is enforced by the test suite.
