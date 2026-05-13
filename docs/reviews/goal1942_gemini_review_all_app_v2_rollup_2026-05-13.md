# Independent Gemini Review of Goal1942: All-App v2 Rollup

Date: 2026-05-13

This is an independent Gemini review, distinct from Codex, of the refreshed all-app v2 performance rollup as presented in `docs/handoff/GOAL1942_EXTERNAL_REVIEW_ALL_APP_V2_ROLLUP.md`.

## Review Scope

The review focused on the committed state at `96d882ff` and inspected the following documents and artifacts:
- `docs/reports/goal1931_current_all_app_v18_v2_perf_analysis_2026-05-13.md`
- `docs/reports/goal1931_current_all_app_v18_v2_perf_analysis_2026-05-13.json`
- `scripts/goal1931_current_all_app_v18_v2_perf_analysis.py`
- `tests/goal1931_current_all_app_v18_v2_perf_analysis_test.py`
- `docs/reports/goal1937_fixed_radius_repeat3_pod/fixed_radius_524288_repeat3.json`
- `docs/reports/goal1940_robot_segment_scaleup_pod_perf_2026-05-13.md`
- `docs/reviews/goal1941_gemini_review_goal1940_robot_segment_scaleup_2026-05-13.md`
- `docs/reports/goal1899_v2_strict_birth_gate_current_board_2026-05-13.md`

## Answers to Questions

1.  **Is the refreshed classification accurate: 11 `positive`, 1 `positive-subsecond`, and 4 `control` rows?**
    Yes, the refreshed classification is accurate. The `goal1931_current_all_app_v18_v2_perf_analysis_2026-05-13.json` explicitly reports `{"control": 4, "positive": 11, "positive-subsecond": 1}`. This is further validated by the unit test `tests/goal1931_current_all_app_v18_v2_perf_analysis_test.py`, which asserts these exact counts and classifications for individual applications.

2.  **Does Goal1931 correctly integrate the repeat-3 fixed-radius pod evidence, the Goal1940 segment any-hit seconds-scale row, and the Goal1940 robot subsecond-but-positive row?**
    Yes, Goal1931 correctly integrates these pieces of evidence. The `scripts/goal1931_current_all_app_v18_v2_perf_analysis.py` script demonstrates that data from `goal1937_fixed_radius_repeat3_pod/fixed_radius_524288_repeat3.json` (for fixed-radius applications) and the relevant JSON artifacts from `goal1940_robot_segment_scaleup_pod/` (for segment any-hit and robot collision) are all consumed to produce the `goal1931_current_all_app_v18_v2_perf_analysis` reports. The insights provided in the `goal1931_current_all_app_v18_v2_perf_analysis_2026-05-13.md` document for these rows accurately reflect the summarized findings from their respective pod evidence.

3.  **Are the four control rows correctly kept out of v2 partner speedup claims?**
    Yes, the four control rows (`database_analytics`, `graph_analytics`, `polygon_pair_overlap_area_rows`, `polygon_set_jaccard`) are correctly identified and explicitly excluded from v2 partner speedup claims. The `goal1931_current_all_app_v18_v2_perf_analysis_2026-05-13.md` report clearly states that these are "important evidence rows, but they are not v2 partner speedup rows until their app continuations move into reviewed partner tensor contracts." The corresponding JSON artifact also sets `"control_rows_are_speedup_evidence": false` within its `claim_boundary`.

4.  **Is the claim boundary still intact: no v2.0 release authorization, no whole-app/broad RT-core/package-install/arbitrary-partner acceleration claim?**
    Yes, the claim boundary remains intact. The `goal1931_current_all_app_v18_v2_perf_analysis_2026-05-13.json` explicitly marks `v2_0_release_authorized`, `whole_app_speedup_claim_authorized`, and `control_rows_are_speedup_evidence` as `false`. The `goal1931_current_all_app_v18_v2_perf_analysis_2026-05-13.md` report also reiterates this in its "Release Boundary" section. Furthermore, `docs/reports/goal1899_v2_strict_birth_gate_current_board_2026-05-13.md` confirms that broad RT-core speedup, whole-application acceleration, and package-install support are still blocked or not ready, and the arbitrary PyTorch/CuPy acceleration claim is bounded.

5.  **What, if anything, remains before a release decision besides source-tree vs package policy, final multi-AI release consensus, and explicit user release action?**
    Based on `docs/reports/goal1899_v2_strict_birth_gate_current_board_2026-05-13.md`, the following also remain before a full release decision:
    *   **True zero-copy**: Public wording decision pending further app rows and pod evidence.
    *   **Direct device-pointer handoff**: Wording needs to remain narrow, not generalized.
    *   **Broad RT-core speedup / Whole-application acceleration**: Completion of the road-hazard pod row is needed, followed by a decision on which app claims are allowed. A fresh Claude or Pro-class review would also be required if a new key performance conclusion is drawn from the all-app matrix.

## Verdict

`accept-with-boundary`

The Goal1942 external review confirms that the refreshed all-app v2 performance rollup is accurate in its classifications and correctly integrates evidence from various pods. Crucially, the explicit claim boundaries regarding v2.0 release authorization, whole-app speedup, broad RT-core acceleration, and package-install claims are consistently and correctly maintained across all reviewed documentation and artifacts. While significant progress is evident, several explicit blockers and wording refinements, as outlined in Goal1899, remain before a final release decision. The current status warrants an `accept-with-boundary` verdict, acknowledging the solid evidence within the stated constraints while highlighting the remaining work required for a full release.
