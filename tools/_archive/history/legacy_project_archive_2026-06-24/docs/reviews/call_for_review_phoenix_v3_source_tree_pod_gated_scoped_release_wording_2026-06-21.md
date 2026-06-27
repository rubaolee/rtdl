# Call For Review: Phoenix V3 Source-Tree / Pod-Gated Scoped Release Wording

Date: 2026-06-21

Reviewer: Claude external review requested from local Windows Claude Code.

Status: external release-scope review request, not release approval.

## Review Task

Please critically review whether Phoenix V3 can close the
installer/reproducibility blocker under an explicitly narrow
`source_tree_pod_gated_eleven_row` scope.

This is not a request to approve the V3 release. It is not a request to approve
a general installer. It is not a request to authorize `pip install`, broad
V3-over-V2 speedup, secondary RT-core hardware confirmation, whole-app speedup,
or paper-reproduction wording.

The question is narrower: if V3 is explicitly scoped as source-tree/pod-gated
and limited to the current eleven exact row-scoped M7-qualified evidence rows,
is that enough to change only this field?

```text
installer_closes_release_blocker: false -> true
```

All other release-blocking fields would remain false until separately reviewed.

Use one verdict:

- `accept-scoped-installer-closure-not-release`
- `accept-with-amendments-not-release`
- `reject-scope-build-general-installer`
- `reject-scope-insufficient-release-discipline`

## Questions To Answer

1. Is `source_tree_pod_gated_eleven_row` a precise enough product scope to close
   the installer/reproducibility blocker without claiming a general installer?
2. If accepted, what exact machine fields may change, and which must remain
   false?
3. If rejected, is the required next step a general installer, stronger scoped
   wording, more hardware evidence, or more M7 rows?
4. Does the candidate protect users from confusing a source-tree/pod-gated
   evidence path with `pip install` release readiness?
5. Does the candidate preserve broad V3-over-V2 speedup, secondary RT-core
   confirmation, whole-app speedup, paper reproduction, and release
   authorization as blocked?
6. What exact amendments, if any, must Codex apply before updating any gate?

## Current State Claims To Audit

- V3 only. V4, C ABI, embedding, and external zero-copy interop are out.
- Release authorized: `false`.
- Broad V3-over-V2 speedup claim authorized: `false`.
- Current M7-qualified row-scoped count: `11`.
- Active generic-engine queue: empty.
- Current release readiness status: `blocked_not_release`.
- Current install gate status:
  `staged_pod_gate_present_general_release_installer_not_ready`.
- Current install candidate status:
  `source_tree_pod_gated_candidate_reviewed: true`.
- Current install blocker status:
  `installer_closes_release_blocker: false`.
- Current secondary RT status:
  `secondary_rt_performance_confirmation_authorized: false`.

## Files To Read

Please read these files before writing the review:

- `docs/rebuild/v3/v3_source_tree_pod_gated_scoped_release_wording_candidate_2026-06-21.md`
- `docs/rebuild/v3/v3_source_tree_pod_gated_reproducibility_candidate_2026-06-21.md`
- `docs/reviews/claude_phoenix_v3_source_tree_pod_gated_reproducibility_candidate_review_2026-06-21.md`
- `docs/reviews/codex_phoenix_v3_source_tree_pod_gated_reproducibility_candidate_2ai_consensus_2026-06-21.md`
- `docs/rebuild/v3/v3_install_reproducibility_strategy_2026-06-21.md`
- `scripts/v3_phoenix_install_reproducibility_gate.py`
- `docs/rebuild/v3/v3_setup_and_rerun_runbook_2026-06-20.md`
- `docs/rebuild/v3/v3_release_authorization_blockers_2026-06-20.md`
- `docs/reviews/claude_phoenix_v3_eleven_row_release_readiness_review_2026-06-21.md`
- `docs/reviews/codex_phoenix_v3_eleven_row_release_readiness_2ai_consensus_2026-06-21.md`
- `docs/learn/current_claim_boundaries.md`
- `docs/handoff/REFRESH_LOCAL_2026-04-13.md`

## Output File

Write your review to:

`docs/reviews/claude_phoenix_v3_source_tree_pod_gated_scoped_release_wording_review_2026-06-21.md`

## Required Review Structure

Use this structure:

```text
# Claude Review: Phoenix V3 Source-Tree / Pod-Gated Scoped Release Wording

Verdict: <one verdict>

## Bottom Line

## Findings

## Answers To The Six Questions

## Required Amendments

## Gate Recommendation

## Claim Boundary Check

## Evidence Gaps Or Weak Sources

## Suggested Next Sequence
```

Please be strict. The intended failure mode to prevent is a user mistaking
source-tree/pod-gated evidence reproducibility for a finished package release.
Do not approve release. Do not approve broad performance claims.

## Goal-Level Decision Audit

Decision: request external release-scope review before considering any change
to `installer_closes_release_blocker`.

1. Was I foolish?
   No. The current install gate says a scoped 2-AI release wording decision is
   one legitimate path, but the field must not change without external review.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish action would be to treat reviewed candidate
   reproducibility as release-scope acceptance.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes. Build a general package installer first. That remains the fallback if
   the scoped wording is rejected.
4. Can I now try a different path that actually solves the problem?
   Yes. Ask Claude to accept, amend, or reject the scoped wording, then intake
   the result conservatively.
