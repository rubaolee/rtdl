# RTDL Versioning

Status: no current public release marker on 2026-06-24.

`VERSION` is now `v3-capability-branch-2026-06-24`. That is a branch marker,
not a release tag and not a package/distribution promise.

## Current Rule

No V3 or later release is currently promoted from this branch. The high-
performance Phase A path is closed by external review, so a future V3 release
marker may replace the capability-branch marker only after the Phase H
capability/quality gate passes:

1. broad V3-over-V2 speed wording removed;
2. row-by-row evidence classified and scoped;
3. tutorials and examples rebuilt for the capability branch;
4. V4/embedding/C-ABI material fenced from the V3 front door;
5. external release-readiness authorization obtained.

## Tag Policy

- Do not create or advertise a release tag from a rebuild marker.
- A future release tag must point at a commit with matching release reports,
  docs, tests, and benchmark artifacts.
- Archived release packets remain historical evidence only.

## Claim Boundary

The capability-branch marker authorizes no performance claim. Read:

- [V3 Rebuild Control](rebuild/v3/README.md)
- [Phase A Performance-Source Consensus](reviews/codex_claude_antigravity_phoenix_v3_phase_a_performance_source_consensus_2026-06-24.md)
- [Current Claim Boundaries](learn/current_claim_boundaries.md)
