# Phoenix V3 Phase H/G Final Status Pending Release Owner

Date: 2026-06-24
Status: `capability_quality_candidate_complete_pending_release_owner`

## Decision

Phoenix V3 is no longer a high-performance release candidate. Phase A failed to
prove a broad, runtime-sourced performance source, so the A-H roadmap forked to
Phase H. The current V3 candidate is an honest capability/quality branch: it
keeps the usable V3 surfaces, public docs, tutorials, claim boundaries, source
tree doctor, and validation gates while explicitly blocking broad V3-over-V2
speed claims.

This document records the final local Phase H/G status. It does not authorize a
public release by itself.

## What Is Complete

- Phase A is closed as `no_go_enter_phase_h`.
- Phase H capability/quality candidate docs are written.
- Phase G source-tree/version truth work is in place for the capability branch:
  `VERSION` is `v3-capability-branch-2026-06-24` and `pyproject.toml` is
  `3.0.0.dev20260624`.
- Public front doors now point users to the current capability branch instead of
  old V3/V4 release claims.
- The high-performance branch remains blocked and cannot be described as a V3
  win over V2.x.
- V4, embedding, C ABI, and external zero-copy claims remain outside V3.

## Local Validation

The current Phase H/G local validation results are:

- `py -3 scripts\v3_release_wording_gate.py --pretty`
  - `status: pass`
  - `final_public_surface_gate: true`
  - `violations: []`
  - `release_authorized: false`
  - `broad_v3_faster_than_v2_claim_authorized: false`
- `py -3 scripts\rtdl_source_tree_doctor.py --json --run-smoke`
  - `ok: true`
  - `status: v3_capability_branch_ready`
  - `required_failures: []`
- `py -3 -m unittest tests.v3_release_wording_gate_test tests.v3_public_docs_rebuild_surface_test tests.v3_rebuild_tutorial_surface_test tests.v3_phoenix_release_readiness_gate_test tests.v3_phoenix_major_performance_mandate_gate_test tests.v3_rebuild_reset_test tests.goal4278_source_tree_doctor_test`
  - `Ran 39 tests`
  - `OK`
- `py -3 scripts\run_test_matrix.py --group v3_rebuild`
  - `module_count: 148`
  - `Ran 754 tests`
  - `OK`

Warnings from the source-tree doctor are optional local environment warnings:
`cupy`, `numba`, and the optional OptiX shared library are not present in this
Windows tree. They are not required failures for the capability branch.

## External Review

Claude reviewed the amended Phase H/G packet and returned:

`accept_phase_h_g_capability_release_ready`

Recorded at:

`docs/reviews/claude_phoenix_v3_phase_h_g_capability_completion_candidate_amendment_review_2026-06-24.md`

Claude explicitly did not authorize public speedup wording, all-app victory, V4,
embedding, C ABI, zero-copy, or release-owner approval.

Antigravity CLI stdout remained blocked by tooling behavior, not by a technical
review rejection. The CLI authenticated, selected `Gemini 3.5 Flash (Medium)`,
made streaming backend calls, and exited with code `0`, but returned empty
output even for a trivial health-check prompt and even when all PowerShell
streams were redirected to a file.

The substantive Antigravity model review was recovered from Antigravity's local
transcript store and returned:

`accept_phase_h_g_capability_release_ready`

Recorded review:

`docs/reviews/antigravity_phoenix_v3_phase_h_g_capability_completion_candidate_review_2026-06-24.md`

CLI stdout defect evidence:

`docs/reviews/antigravity_blocked_phoenix_v3_phase_h_g_capability_completion_candidate_2026-06-24.md`

The stdout defect is tooling evidence, not release authorization. The recovered
review is the Antigravity reviewer verdict for this Phase H/G candidate.

## Release Owner Requirements

Before a public V3 capability/quality release can be announced, the release
owner must explicitly decide whether this Phase H/G branch is acceptable as a
capability/quality release. That authorization must not be inferred from green
tests or from Claude's review.

Required before public release wording:

1. Release-owner authorization of the capability/quality scope.
2. No broad V3-over-V2 speed claim.
3. No public all-app victory claim.
4. No V4, embedding, C ABI, external zero-copy, or package-install claim.

## Goal-Level Decision Audit

Question 1: Was I being foolish?

Answer: The foolish path would be to call this a performance release or treat
empty Antigravity CLI output as consensus. I am not doing that here.

Question 2: If yes, what actions would make the decision foolish?

Answer: The decision would become foolish if I reopened performance-candidate
work after Phase A No-Go, hid the Antigravity review gap, ignored the
release-owner gate, or claimed V3 is broadly faster than V2.x.

Question 3: Is there another possible path that avoids being stuck on the wrong
idea?

Answer: Yes. The honest path is the Phase H capability/quality branch: finish
the usable docs, gates, tutorials, and source-tree truth, while preserving the
failed high-performance branch as evidence and blocking inflated claims.

Question 4: Can I start a different path that truly solves the problem?

Answer: Yes. The current path solves the user-facing truth problem now. Any
future high-performance V3 work must restart from a new falsifiable performance
source, not from this release candidate.

## Non-Authorization

This status file authorizes no public release by itself, no broad V3-over-V2
performance claim, no public speedup wording, no all-app victory, no V4,
no embedding, no C ABI, no external zero-copy claim, and no package-install
claim.
