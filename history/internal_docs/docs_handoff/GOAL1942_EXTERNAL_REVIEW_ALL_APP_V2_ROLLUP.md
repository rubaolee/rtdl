# Goal1942 External Review Task

Please perform an independent review of the refreshed all-app v2 performance
rollup in `C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review`.

Review the committed state at `96d882ff` and inspect:

- `docs/reports/goal1931_current_all_app_v18_v2_perf_analysis_2026-05-13.md`
- `docs/reports/goal1931_current_all_app_v18_v2_perf_analysis_2026-05-13.json`
- `scripts/goal1931_current_all_app_v18_v2_perf_analysis.py`
- `tests/goal1931_current_all_app_v18_v2_perf_analysis_test.py`
- `docs/reports/goal1937_fixed_radius_repeat3_pod/fixed_radius_524288_repeat3.json`
- `docs/reports/goal1940_robot_segment_scaleup_pod_perf_2026-05-13.md`
- `docs/reviews/goal1941_gemini_review_goal1940_robot_segment_scaleup_2026-05-13.md`
- `docs/reports/goal1899_v2_strict_birth_gate_current_board_2026-05-13.md`

Questions to answer:

1. Is the refreshed classification accurate: 11 `positive`, 1
   `positive-subsecond`, and 4 `control` rows?
2. Does Goal1931 correctly integrate the repeat-3 fixed-radius pod evidence,
   the Goal1940 segment any-hit seconds-scale row, and the Goal1940 robot
   subsecond-but-positive row?
3. Are the four control rows correctly kept out of v2 partner speedup claims?
4. Is the claim boundary still intact: no v2.0 release authorization, no
   whole-app/broad RT-core/package-install/arbitrary-partner acceleration claim?
5. What, if anything, remains before a release decision besides source-tree vs
   package policy, final multi-AI release consensus, and explicit user release
   action?

Please save your review as:

`docs/reviews/goal1942_gemini_review_all_app_v2_rollup_2026-05-13.md`

Use one of these verdicts:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

State clearly that this is an independent Gemini review distinct from Codex.
