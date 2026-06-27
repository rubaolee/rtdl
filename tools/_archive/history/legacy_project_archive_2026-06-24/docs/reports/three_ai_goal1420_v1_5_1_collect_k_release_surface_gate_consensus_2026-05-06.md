# Three-AI Consensus: Goal1420 v1.5.1 COLLECT_K_BOUNDED Release-Surface Gate

## Verdict

ACCEPTED as the v1.5.1 `COLLECT_K_BOUNDED` release-surface gate package for the measured documented experimental public-candidate scope.

This consensus does not authorize public docs changes, stable primitive promotion, speedup wording, zero-copy wording, whole-app claims, or release-tag action.

## Reviewed Evidence

- Gate implementation: `src/rtdsl/v1_5_1_collect_k_bounded.py`
- Public exports: `src/rtdsl/__init__.py`
- Gate tests: `tests/goal1420_v1_5_1_collect_k_release_surface_gate_test.py`
- Candidate docs: `docs/release_reports/v1_5_1/README.md`
- Candidate docs: `docs/release_reports/v1_5_1/collect_k_bounded.md`
- Candidate docs: `docs/release_reports/v1_5_1/release_surface_gate.md`
- Gate report: `docs/reports/goal1420_v1_5_1_collect_k_release_surface_gate_2026-05-06.md`
- Proposal consensus: `docs/reports/three_ai_goal1419_v1_5_1_collect_k_release_surface_proposal_consensus_2026-05-06.md`
- External Claude review: `docs/reports/claude_goal1420_v1_5_1_collect_k_release_surface_gate_review_2026-05-06.md`
- External Gemini review: `docs/reports/gemini_goal1420_v1_5_1_collect_k_release_surface_gate_review_2026-05-06.md`

## Consensus

- Codex accepts the gate because it validates the candidate docs, required caution phrases, forbidden phrase absence, false authorization flags, and narrow allowed next actions.
- Claude returned `ACCEPT` with no blockers, confirming the gate and candidate docs are suitable for the measured documented experimental public-candidate scope.
- Gemini returned `ACCEPT` with no blockers, confirming the gate rejects forbidden overclaims and keeps all public authorization flags false.
- All reviewers agree the next allowed actions are limited to external review follow-up, a public-doc link patch after acceptance, or an explicit release decision if the user requests one.

## Notes

- Claude noted a non-blocking evidence-registry hardening opportunity: `V1_5_1_COLLECT_K_BOUNDED_READINESS_EVIDENCE` has three file pointers while the readiness gate has six logical gates. The current gate is accepted because the consensus files cover those logical gates and the validators enforce the pass state.
- Claude noted a non-blocking validator hardening opportunity: `validate_collect_k_bounded_result` defaults missing capacity/valid-count metadata to `0`, which is fail-closed for non-empty rows but could be made more explicit later.

## Remaining Boundary

- This gate does not publish the candidate docs through top-level public navigation.
- This gate does not authorize stable promotion, speedup wording, zero-copy wording, whole-app claims, release-tag action, or a release.
- The next implementation step may prepare a public-doc link patch, but that patch still must keep release/tag actions explicit and separate.
