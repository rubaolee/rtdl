# Claude Task: Goal1737 v1.8 Python+RTDL Gap Audit Review

Please perform an independent review of:

- `docs/reports/goal1737_v1_8_python_rtdl_gap_audit_2026-05-12.md`
- `tests/goal1737_v1_8_python_rtdl_gap_audit_test.py`
- the supporting v1.6.11 final decision chain: Goals 1729, 1732, 1735, and 1736
- `docs/release_reports/v1_8_v2_0_python_partner_rtdl_gate.md`

Review scope:

1. Verify that Goal1737 accurately states v1.8 is close but not release-ready.
2. Verify that it does not authorize a version bump, tag, release, or broad public claim.
3. Verify that it correctly separates v1.8 Python+RTDL from v2.0 Python+partner+RTDL.
4. Verify that the packaging/install gap is real: no `pyproject.toml`, `setup.py`, or `setup.cfg`.
5. Verify that it does not overclaim performance, arbitrary RTX acceleration, universal partner zero-copy, or partner readiness.
6. Run the focused test if possible:
   `py -3 -m unittest tests.goal1737_v1_8_python_rtdl_gap_audit_test tests.goal1736_v1_6_11_commit_ready_inventory_test tests.goal1735_v1_6_11_final_release_consensus_test`

Write your review to:

`docs/reviews/goal1738_claude_review_goal1737_v1_8_gap_audit_2026-05-12.md`

Use one of the established verdicts:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Please make clear that this is an independent Claude review, distinct from Codex and Gemini. Do not edit source code or release docs beyond the review file.
