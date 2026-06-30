# Goal1151 Gemini Review Request

Please review the bounded Goal1151 robot-boundary gate follow-up.

Read:

- `docs/reports/goal1151_robot_boundary_gate_followup_2026-04-29.md`
- `tests/goal847_active_rtx_claim_review_package_test.py`
- `tests/goal978_rtx_speedup_claim_candidate_audit_test.py`
- `src/rtdsl/app_support_matrix.py`
- `docs/reports/goal1150_two_ai_consensus_2026-04-29.md`

Questions:

1. Is it correct to update live Goal847 and Goal978 tests away from the older `100 ms` phrase and toward the current robot public-wording boundary?
2. Does the change keep `robot_collision_screening / prepared_pose_flags` blocked for public speedup wording?
3. Does it preserve the future-review boundary: only explicit normalized per-pose wording may enter review, and whole-app robot planning speedup remains outside any wording?
4. Is the 60-test expanded public RTX gate suite sufficient for this bounded follow-up?

Write the verdict report to:

`docs/reports/goal1151_gemini_robot_boundary_gate_review_2026-04-29.md`

Use `VERDICT: ACCEPT` or `VERDICT: BLOCK` and list required fixes if any.

