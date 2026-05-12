# Gemini Task: Goal1742 v1.8 Release-Candidate Evidence Packet Review

Please perform an independent read-only review of:

- `docs/reports/goal1742_v1_8_release_candidate_evidence_packet_2026-05-12.md`
- `tests/goal1742_v1_8_release_candidate_evidence_packet_test.py`
- supporting Goals 1737, 1740, and 1741
- supporting v1.6.11 final evidence Goals 1729, 1732, 1735, and 1736
- `docs/release_reports/v1_8_v2_0_python_partner_rtdl_gate.md`

Review scope:

1. Confirm whether Goal1742 is suitable as a v1.8 Python+RTDL release-candidate evidence packet for external review.
2. Confirm it does not authorize a tag, version bump, package upload, or public release.
3. Confirm it correctly keeps v1.8 as source-tree Python+RTDL and keeps Python+partner+RTDL in v2.0.
4. Confirm the source-tree boundary and packaging metadata gap are accurately described.
5. Confirm the allowed and blocked wording is conservative and does not overclaim speedups, arbitrary RTX, universal partner zero-copy, PyTorch/CuPy readiness, or package-install support.
6. Run the focused test if available:
   `py -3 -m unittest tests.goal1742_v1_8_release_candidate_evidence_packet_test tests.goal1741_v1_8_source_tree_install_boundary_test tests.goal1740_v1_8_public_docs_boundary_alignment_test tests.goal1737_v1_8_python_rtdl_gap_audit_test`

Write your review to:

`docs/reviews/goal1743_gemini_review_goal1742_v1_8_release_candidate_packet_2026-05-12.md`

Use one of the established verdicts:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Please make clear that this is an independent Gemini review, distinct from Codex and Claude. Do not edit source code or release docs beyond the review file.
