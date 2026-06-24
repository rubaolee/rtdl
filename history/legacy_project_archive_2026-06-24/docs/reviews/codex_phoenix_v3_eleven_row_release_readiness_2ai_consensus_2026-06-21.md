# Codex Consensus: Phoenix V3 Eleven-Row Release Readiness

Date: 2026-06-21

Consensus parties:

- Claude external review:
  `docs/reviews/claude_phoenix_v3_eleven_row_release_readiness_review_2026-06-21.md`
- Codex current-state intake:
  this file

Consensus status:
`claude_codex_consensus_current_eleven_row_not_release_ready_fix_p0`

Verdict:
`not-release-ready-fix-p0`

## Decision

Codex accepts Claude's eleven-row release-readiness review.

The current Phoenix V3 state supersedes the old six-row facts: V3 now has
eleven exact row-scoped M7-qualified rows, the active generic-engine queue is
closed, and Spatial RayJoin is future research rather than a current P0.

This does not authorize release. The superseding current-state consensus is itself a blocking consensus.
Phoenix V3 remains `blocked_not_release` until the
remaining release blockers are closed or explicitly scoped/waived through
reviewed release wording.

## What Is Now Settled

- The generic-engine active queue is closed.
- Existing evidence is not promotable into additional M7 rows without new
  evidence.
- Engine work is no longer the critical path for a scoped V3 release review.
- The current M7 release surface is eleven exact row-scoped rows.
- Broad V3-over-V2 speedup remains unauthorized.
- Whole-app, paper-reproduction, RTDL-beats-RayJoin, package-install, and
  general release claims remain unauthorized.

## Current P0 Blockers

The current consensus keeps these P0 blockers active:

1. `general_release_installer_not_ready`
   - The current `scripts/v3_install_gpu_pod_env.sh` path is a staged pod gate
     requiring `--accept-experimental-pod-gate`.
   - It is not a general release installer.
   - It does not authorize package-install wording.
2. `secondary_rt_performance_confirmation_not_closed`
   - The local `lx1` / `192.168.1.20` evidence is compatibility-only because it
     is GTX 1070-class hardware with no RT cores.
   - The eleven M7 rows are still single-RTX-4000-Ada-pod evidence.
3. `current_eleven_row_release_readiness_consensus_blocks_release`
   - Claude's current eleven-row review verdict is
     `not-release-ready-fix-p0`.
   - Codex agrees.
   - This current consensus blocks release until installer, secondary RT
     evidence or waiver, and scoped release wording are closed.
4. `eleven_row_surface_still_too_narrow_for_major_release`
   - Eleven rows are real progress, not a full broad major-release surface.
   - This can only be resolved by promoting more reusable rows or by explicitly
     positioning V3 as a narrow source-tree/pod-gated row-scoped release with
     external review.
5. `broad_v3_faster_than_v2_claim_not_authorized`
   - The same-RT-hardware V2.14-vs-current-V3 paired geomean remains `1.012x`.
   - Any broad performance-first V3-over-V2 claim remains false.
6. `release_authorization_false`
   - No release decision is authorized by this consensus.

## Required Next Sequence

1. Close installer/reproducibility either by a reviewed general installer path
   or by explicit source-tree/pod-gated release wording.
2. Close secondary RT performance either by a second RTX/RT-core run or by an
   explicit 2-AI-reviewed hardware-scoped waiver.
3. Upgrade final release wording/docs review so the release surface is not
   merely first-pass scanned.
4. Record the product scope machine-readably:
   `full_major_release` or `source_tree_pod_gated_eleven_row`.
5. Only then rerun the aggregate release-readiness gate and request final
   external release approval.

## Claim Boundary

Allowed current wording:

- "Phoenix V3 currently has eleven exact row-scoped M7-qualified rows."
- "The generic-engine active queue is closed."
- "Release remains blocked."
- "Broad V3-over-V2 speedup is not authorized."
- "The evidence is single RTX 4000 Ada pod performance evidence unless a later
  second-RTX packet or reviewed waiver says otherwise."

Forbidden current wording:

- "V3 is release-ready."
- "V3 broadly beats V2."
- "V3 has a general release installer."
- "V3 performance is confirmed across RT-core hardware."
- "RTDL beats RayJoin."
- "Spatial RayJoin is an M7 release row."

## Goal-Level Decision Self-Audit

Decision: Accept Claude's eleven-row release-readiness review as a current
blocking consensus, not as release approval.

1. Was I foolish?
   No. This replaces stale six-row factual framing with current eleven-row,
   queue-closed evidence while preserving the release block.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish action would be to quote Claude's praise for row
   quality and ignore its `not-release-ready-fix-p0` verdict.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes. I could keep tuning old app rows, but Claude now says no engine work is
   on the critical path; that would avoid the harder release blockers.
4. Can I now try a different path that actually solves the problem?
   Yes. The next work should target installer/reproducibility, secondary RT
   evidence or waiver, and final scoped release wording instead of more
   generic-engine mining.
