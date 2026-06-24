# Goal1458 Public Docs Link Review Request

## Request

Review whether the v1.5.2 candidate documentation package may be linked from
the public documentation spine. Do not publish a release, do not create or move
tags, and do not authorize any stronger claim than the proposed wording.

## Files To Review

- Proposal:
  `docs/reports/goal1458_v1_5_2_public_docs_link_proposal_2026-05-07.md`
- Reviewed candidate package:
  `docs/release_reports/v1_5_2/README.md`
  `docs/release_reports/v1_5_2/prepared_host_output_buffers.md`
  `docs/release_reports/v1_5_2/release_surface_gate.md`
- Gate implementation:
  `src/rtdsl/v1_5_2_collect_buffers.py`
- Tests:
  `tests/goal1457_v1_5_2_release_surface_external_review_gate_test.py`
  `tests/goal1456_v1_5_2_release_surface_candidate_docs_test.py`
- Prior consensus and RTX validation:
  `docs/reports/three_ai_goal1457_v1_5_2_release_surface_candidate_docs_consensus_2026-05-07.md`
  `docs/reports/goal1457_rtx2000ada_release_surface_review_validation_2026-05-07.md`

## Current Boundary

The candidate docs are externally reviewed but still unlinked. The public docs
link proposal must preserve:

- No release action.
- No prepared-buffer reuse claim.
- No public speedup wording.
- No zero-copy wording.
- No whole-app claims.
- No stable primitive promotion.
- No release tag action.

## Review Question

Answer with `ACCEPT`, `ACCEPT_WITH_NOTES`, or `REJECT`.

If accepting, confirm that the exact proposed link label and status wording are
safe for the public docs spine. If rejecting, identify the precise blocker.
