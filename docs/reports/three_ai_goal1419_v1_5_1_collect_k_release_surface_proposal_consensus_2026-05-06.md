# Three-AI Consensus: Goal1419 v1.5.1 COLLECT_K_BOUNDED Release-Surface Proposal

## Verdict

ACCEPTED as the proposal package for the next v1.5.1 `COLLECT_K_BOUNDED` release-surface gate.

This consensus does not authorize public docs changes, stable primitive promotion, speedup wording, zero-copy wording, release-tag action, or whole-app claims.

## Reviewed Evidence

- Proposal implementation: `src/rtdsl/v1_5_1_collect_k_bounded.py`
- Public exports: `src/rtdsl/__init__.py`
- Proposal tests: `tests/goal1419_v1_5_1_collect_k_release_surface_proposal_test.py`
- Proposal report: `docs/reports/goal1419_v1_5_1_collect_k_release_surface_proposal_2026-05-06.md`
- Readiness consensus: `docs/reports/three_ai_goal1418_v1_5_1_collect_k_readiness_gate_consensus_2026-05-06.md`
- Parity consensus: `docs/reports/three_ai_goal1416_v1_5_1_collect_k_native_parity_consensus_2026-05-06.md`
- Benchmark consensus: `docs/reports/three_ai_goal1417_v1_5_1_collect_k_benchmark_consensus_2026-05-06.md`
- External Claude review: `docs/reports/claude_goal1419_v1_5_1_collect_k_release_surface_proposal_review_2026-05-06.md`
- External Gemini review: `docs/reports/gemini_goal1419_v1_5_1_collect_k_release_surface_proposal_review_2026-05-06.md`

## Consensus

- Codex accepts the proposal because it recommends only `documented_experimental_public_candidate` status and explicitly does not authorize public docs changes or claims.
- Claude returned `ACCEPT` with no blockers, confirming the classification is appropriately cautious and the proposal is suitable for the next v1.5.1 release-surface gate.
- Gemini returned `ACCEPT` with no blockers, confirming the proposal avoids stable promotion, speedup claims, and release actions.
- All reviewers agree the evidence basis is the accepted Goal1416 parity consensus, Goal1417 benchmark consensus, and Goal1418 readiness consensus.
- All reviewers agree the allowed next actions remain limited to requesting external release-surface review, drafting user docs only after review accepts, and keeping current public docs unchanged until authorization.

## Notes

- Claude noted a non-blocking hardening opportunity: mirror the readiness gate's `whole_app_speedup_claim_authorized=False` as an explicit proposal field. The reviewed package already blocks whole-app speedup through `not_proposed`, `forbidden_wording`, and the claim boundary.
- Claude also noted that the proposal report says required reviewers are Codex, Claude, and Gemini while the code lists external review partners as Claude and Gemini. This is acceptable because Codex is the internal author/reviewer and Claude/Gemini are the external partners.

## Remaining Boundary

- This is a proposal package only.
- The next step is a release-surface gate/review package.
- No public docs, stable promotion, speedup wording, zero-copy wording, release-tag action, or whole-app claim is authorized by this consensus.
