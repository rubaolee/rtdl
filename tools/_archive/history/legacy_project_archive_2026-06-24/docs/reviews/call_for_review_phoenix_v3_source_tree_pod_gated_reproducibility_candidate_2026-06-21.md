# Call For Review: Phoenix V3 Source-Tree / Pod-Gated Reproducibility Candidate

Date: 2026-06-21

Reviewer: Claude external review requested from local Windows Claude Code.

Status: external review request, not release approval.

## Review Task

Please critically review whether the current Phoenix V3 source-tree /
pod-gated reproducibility candidate is acceptable as a reviewed, narrow
reproducibility path for the current V3 evidence surface.

This is not a request to approve a V3 release, not a request to approve a
general package installer, and not a request to authorize broad V3-over-V2
speedup wording. The question is narrower: can this candidate honestly support
wording that Phoenix V3 evidence is reproducible from the source tree on the
documented RTX pod environment?

Use one verdict:

- `approve-candidate-not-release`
- `approve-with-amendments-not-release`
- `not-enough-fix-p0`
- `reject-candidate`

## Questions To Answer

1. Is the candidate concrete enough to mark
   `source_tree_pod_gated_candidate_reviewed: true`, assuming Codex reaches the
   same consensus?
2. Does the candidate close the installer/reproducibility blocker for a narrow
   source-tree/pod-gated V3 scope, or must
   `installer_closes_release_blocker` remain `false`?
3. If it does not close the blocker, what exact missing work is required:
   general package installer, scoped release wording, second hardware evidence,
   runbook fixes, or something else?
4. Are the required commands, package pins, native backend build steps, runtime
   library exports, and GPU environment gate sufficient for a serious user to
   rerun the evidence on the documented pod class?
5. Does the candidate preserve the correct negative boundaries: not a general
   release installer, not package-install wording, not release authorization,
   not second-RTX confirmation, and not broad V3-over-V2 speedup?
6. What exact amendments, if any, must Codex make before the install gate can
   record this candidate as reviewed?

## Current State Claims To Audit

- V3 only. V4, C ABI, embedding, and external zero-copy interop are out.
- Release authorized: `false`.
- Broad V3-over-V2 speedup claim authorized: `false`.
- Current M7-qualified row-scoped count: `11`.
- Active generic-engine queue: empty.
- Current release readiness status: `blocked_not_release`.
- Current install gate status:
  `staged_pod_gate_present_general_release_installer_not_ready`.
- Current candidate status:
  `source_tree_pod_gated_candidate_not_reviewed_not_release`.
- Current candidate gate fields:
  - `source_tree_pod_gated_candidate_present: true`
  - `source_tree_pod_gated_candidate_reviewed: false`
  - `general_release_installer_ready: false`
  - `package_install_claim_authorized: false`
  - `installer_closes_release_blocker: false`

## Files To Read

Please read these files before writing the review:

- `docs/rebuild/v3/v3_source_tree_pod_gated_reproducibility_candidate_2026-06-21.md`
- `docs/rebuild/v3/v3_install_reproducibility_strategy_2026-06-21.md`
- `scripts/v3_phoenix_install_reproducibility_gate.py`
- `scripts/v3_install_gpu_pod_env.sh`
- `docs/rebuild/v3/v3_setup_and_rerun_runbook_2026-06-20.md`
- `docs/rebuild/v3/v3_release_authorization_blockers_2026-06-20.md`
- `docs/reviews/claude_phoenix_v3_eleven_row_release_readiness_review_2026-06-21.md`
- `docs/reviews/codex_phoenix_v3_eleven_row_release_readiness_2ai_consensus_2026-06-21.md`
- `docs/handoff/REFRESH_LOCAL_2026-04-13.md`

## Output File

Write your review to:

`docs/reviews/claude_phoenix_v3_source_tree_pod_gated_reproducibility_candidate_review_2026-06-21.md`

## Required Review Structure

Use this structure:

```text
# Claude Review: Phoenix V3 Source-Tree / Pod-Gated Reproducibility Candidate

Verdict: <one verdict>

## Bottom Line

## Findings

## Answers To The Six Questions

## Required Amendments

## Install Gate Recommendation

## Claim Boundary Check

## Evidence Gaps Or Weak Sources

## Suggested Next Sequence
```

Please be strict. Do not approve release just because this candidate is clearer
than having no reproducibility path. Do not penalize the candidate merely
because it is intentionally source-tree/pod-gated, but do require that the gate
and docs make that scope unmistakable.

## Goal-Level Decision Audit

Decision: request external review for the source-tree/pod-gated
reproducibility candidate before changing any install gate status.

1. Was I foolish?
   No. The candidate is currently not reviewed, and changing machine-readable
   gate fields without external review would repeat the same release-discipline
   failure Phoenix is meant to fix.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish action would be to mark the candidate reviewed,
   or close the installer blocker, before Claude and Codex both agree on the
   exact scope.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes. Build a general package installer first. That may still be necessary,
   but it is a larger task and should not block reviewing the current source
   tree path as a candidate.
4. Can I now try a different path that actually solves the problem?
   Yes. If Claude rejects this candidate, build the general installer/runbook
   path. If Claude accepts it with amendments, patch the candidate and gate
   without pretending release is authorized.
